import asyncio
import os
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor
from scanning.DogColmap import DogColmap
from basics.Queue import ScanQueue
from .Jobs import ScanJob
import time
from scanning.utils import get_video_frames



class Worker:
    jobQueue = None
    _test = None

    def __init__(self, jobQueue) -> None:
        self.jobQueue = jobQueue
        self._test = False


class ScanWorker(Worker):
    _test_params = None

    def __init__(self, jobQueue):
        super().__init__(jobQueue)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._test_params = {
            "intervals": [8, 10, 12],
            "num_feats": [9000, 8000, 10000],
            "peak_thresh": [0.01, 0.001, 0.0001],
            "domain_pooling": False,
            "estimate_shape": True,
        }

    def _log_results(self, frames, feats, thresh, time, file_name):
        with open(f"uploaded_videos/{file_name}", "a") as file:
            file.write(f"{frames}, {feats}, {thresh}, {time}\n")

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
                    if self._test and self._test_params:
                        for feats in self._test_params["num_feats"]:
                            for peak_thresh in self._test_params["peak_thresh"]:
                                for interval in self._test_params["intervals"]:
                                    start_time = time.perf_counter()
                                    job.max_num_feats = feats
                                    job.peak_thresh = peak_thresh
                                    job.estimate_shape = self._test_params["estimate_shape"]
                                    job.domain_pooling = self._test_params["domain_pooling"]
                                    job.out_name = f"{job.file_name}_{job.max_num_feats}_{job.peak_thresh}_{interval}"
                                    job.frame_count = get_video_frames(job.file_path, interval)

                                    job.mesh = False

                                    await self._process(job)                        
                                    end_time = time.perf_counter()
                                    total_time = end_time - start_time
                                    self._log_results(frames=job.frame_count, feats=job.max_num_feats, thresh=peak_thresh, time=total_time, file_name="temp_log_file.csv")
                    else:
                        print(f"Processing scan for {job.user_name}/{job.file_name}")
                        await self._process(job)

                else:
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("ScanWorker stopped")
            self.executor.shutdown(wait=False)
            raise
        except Exception as e:
            print(f"Worker crashed: {type(e).__name__}: {e}")

            traceback.print_exc()

    async def _process(self, job):
        print(f"Starting scan for {job.file_name}, FEATS: {job.max_num_feats}, THRESH: {job.peak_thresh}")
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



    def _clean_up(self, job):
        try:
            job_out_dir = f"uploaded_videos/{job.user_name}/{job.file_name}/out"
            shutil.rmtree(job_out_dir)
        except Exception as e:
            print(e)

    def _run_job(self, job: ScanJob):
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
            max_num_feats=job.max_num_feats,
            peak_thresh=job.peak_thresh,
            estimate_shape=job.estimate_shape,
            domain_pooling=job.domain_pooling,
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
        # self._clean_up(job)
