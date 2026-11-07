
import os
from pathlib import Path

import numpy as np
import open3d as o3d
import pycolmap

from .Extract import extract


class DogColmap:
    def __init__(
        self,
        video_path,
        user_name,
        file_name,
        file_path,
        out_name,
        depth=9,
        pw=2.0,
        trim=7.0,
        frame_interval=8,
        max_distance=10,
        mesh=False,
        frames_dir="./vid/out",
        sparse_dir="./out_ply",
        mesh_dir="./out_mesh",
    ):
        self._video_path = video_path
        self._user_name = user_name
        self._file_name = file_name
        self._file_path = file_path
        self._out_name = out_name

        self._depth = depth
        self._pw = pw
        self._trim = trim
        self._frame_interval = frame_interval
        self._max_distance = max_distance
        self._mesh = mesh

        self._frames_dir = Path(frames_dir)
        self._sparse_dir = Path(sparse_dir)
        self._mesh_dir = Path(mesh_dir)

        # Output locations
        self._sparse_output_dir = self._sparse_dir / "sparse"
        print(self._sparse_output_dir)
        self._ply_path = self._sparse_output_dir / f"{self._out_name}.ply"
        self._mesh_path = self._mesh_dir / f"{self._out_name}.ply"

    def run(self):
        try:
            # 1. Extract video frames
            extract(self._video_path, self._frame_interval)

            # 2. Run COLMAP reconstruction
            self.reconstruct_dog()

            # 3. Filter and export sparse point cloud
            self.reconstruct_model()

            print(f"Sparse PLY saved: {self._ply_path}")

            # 4. Generate mesh if requested
            if self._mesh:
                self.mesh_poisson()
                return self._mesh_path


            return self._ply_path

        except Exception as e:
            print(f"Reconstruction failed: {e}")
            raise

        
        

    def reconstruct_dog(self):
        self._sparse_dir.mkdir(parents=True, exist_ok=True)
        self._sparse_output_dir.mkdir(parents=True, exist_ok=True)

        database_path = self._sparse_dir / "database.db"

        extraction_opts = pycolmap.FeatureExtractionOptions()
        extraction_opts.sift.max_num_features = 8192
        extraction_opts.sift.estimate_affine_shape = True

        pycolmap.extract_features(
            database_path,
            self._frames_dir,
            extraction_options=extraction_opts,
        )

        print("Running sequential matching...")

        pycolmap.match_sequential(
            database_path,
            pairing_options=pycolmap.SequentialPairingOptions(overlap=15),
        )

        with pycolmap.Database.open(database_path) as db:
            num_matches = db.num_matches()
            print(f"Number of matched pairs: {num_matches}")

            if num_matches == 0:
                print("Sequential produced 0 matches, trying exhaustive...")
                pycolmap.match_exhaustive(database_path)
                print(f"After exhaustive: {db.num_matches()} matched pairs")

        maps = pycolmap.incremental_mapping(
            database_path,
            self._frames_dir,
            self._sparse_output_dir,
            options={
                "min_num_matches": 15,
                "multiple_models": False,
            },
        )

        if not maps or 0 not in maps:
            raise RuntimeError("Sparse reconstruction failed")

        maps[0].write(self._sparse_output_dir)

        return maps[0]

    def reconstruct_model(self):
        rec = pycolmap.Reconstruction(
            self._sparse_output_dir / "0"
        )

        points_to_delete = []

        for point_id, point in rec.points3D.items():
            distance = np.linalg.norm(point.xyz)

            if distance > self._max_distance:
                points_to_delete.append(point_id)

        for point_id in points_to_delete:
            rec.delete_point3D(point_id)

        rec.export_PLY(str(self._ply_path))

        print(
            f"Filtered sparse points saved to: {self._ply_path}"
        )

        return self._ply_path

    def estimate_normals(self, ply_path):
        print("Estimating point normals using Open3D...")

        pcd = o3d.io.read_point_cloud(str(ply_path))

        if pcd.is_empty():
            raise RuntimeError(f"Point cloud is empty: {ply_path}")

        # Remove statistical outliers
        pcd, _ = pcd.remove_statistical_outlier(
            nb_neighbors=20,
            std_ratio=2.0,
        )

        if len(pcd.points) < 3:
            raise RuntimeError("Not enough points to estimate normals")

        pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=0.5,
                max_nn=50,
            )
        )

        pcd.orient_normals_consistent_tangent_plane(k=15)

        # Overwrite the original PLY, keeping its existing location
        success = o3d.io.write_point_cloud(
            str(ply_path),
            pcd,
        )

        if not success:
            raise RuntimeError("Failed to save point cloud normals")

        print("Point normals estimated successfully.")

        return ply_path

    def mesh_poisson(self):
        # Estimate normals on the original sparse PLY
        ready_ply = self.estimate_normals(self._ply_path)

        # Ensure mesh directory exists
        self._mesh_dir.mkdir(parents=True, exist_ok=True)

        poisson_options = pycolmap.PoissonMeshingOptions()
        poisson_options.depth = self._depth
        poisson_options.point_weight = self._pw
        poisson_options.trim = self._trim

        print(f"Running Poisson meshing on: {ready_ply}")

        pycolmap.poisson_meshing(
            str(ready_ply),
            str(self._mesh_path),
            options=poisson_options,
        )

        print(f"Final mesh saved to: {self._mesh_path}")

        return self._mesh_path
