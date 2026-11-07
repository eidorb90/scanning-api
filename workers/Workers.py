import asyncio
import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
from scanning.DogColmap import DogColmap
from basics.Queue import ScanQueue
from .Jobs import ScanJob



class Worker:
    jobQueue = None

    def __init__(self, jobQueue) -> None:
        self.jobQueue = jobQueue


class ScanWorker(Worker):
    def __init__(self, jobQueue):
        super().__init__(jobQueue)
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def work(self):
        try:
            while True:
                job = None
                if self.jobQueue is None:
                    print("Job Queue is None")
                    return
                    
                if not self.jobQueue.is_empty():
                    job = self.jobQueue.dequeue()
                if job is not None:
                    print(f"Processing scan for {job.user_name}/{job.file_name}")
            
                    loop = asyncio.get_running_loop()
                    try:
                        await loop.run_in_executor(self.executor, self._run_job, job)

                    except Exception as e:
                        print(
                            f"Job failed for: {job.user_name}/{job.file_name} with exception: {e}"
                        )
                        traceback.print_exc()
                    finally:
                        self.jobQueue.set_active(None)
                else:
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("ScanWorker stopped")
            self.executor.shutdown(wait=False)
            raise
        except Exception as e:
            print(f"Worker crashed: {type(e).__name__}: {e}")

            traceback.print_exc()

    def _move_ply(self, job):
        try:
            if job.mesh:
                source_path = f"uploaded_videos/{job.user_name}/{job.file_name}/out/sparse/{job.out_name}.ply"
            else:
                source_path = f"uploaded_videos/{job.user_name}/{job.file_name}/out/sparse/{job.out_name}.ply" 

            destination_dir = f"uploaded_videos/{job.user_name}/ply"
            destination = os.path.join(destination_dir, f"{job.out_name}.ply")

            if os.path.exists(destination):
                os.remove(destination)
            shutil.move(source_path, destination_dir)
        except Exception as e:
            print(e)

    def _clean_up(self, job):
        try:
            job_out_dir = f"uploaded_videos/{job.user_name}/{job.file_name}/out"
            shutil.rmtree(job_out_dir)
        except Exception as e:
            print(e)

    def _run_job(self, job: ScanJob, mesh=False):
        """Synchronous work that runs in the thread pool."""
        os.makedirs(job.frames_path, exist_ok=True)
        os.makedirs(job.sparse_path, exist_ok=True)
        os.makedirs(job.mesh_path, exist_ok=True)
        dc = DogColmap(
            video_path=job.file_path, 
            user_name=job.user_name, 
            file_name=job.file_name, 
            file_path=job.file_path,
            out_name=job.out_name,
            depth = job.depth,
            pw = job.pw,
            trim = job.trim,
            frame_interval=job.frame_interval,
            max_distance=job.max_distance,
            mesh=job.mesh,
            frames_dir=job.frames_path,
            sparse_dir=job.sparse_path,
            mesh_dir=job.mesh_path,
        )
        dc.run()
        self._move_ply(job)
        self._clean_up(job)
