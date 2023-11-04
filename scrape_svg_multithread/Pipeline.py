import importlib
import os

import yaml
from multiprocessing import Queue


class PipelineBuild:
    def __init__(self, yaml_name):
        self._one_thread_instance = None
        self.yaml = yaml_name
        self.data = None
        self._queues = {}
        self._scheduler_threads = {}

    def initialise_pipeline(self):
        with open(self.yaml, 'r') as file:
            self.data = yaml.safe_load(file)
            file.close()

    def initialise_queue(self):
        for queue in self.data["QUEUES"]:
            self._queues[queue["NAME"]] = Queue()

    def initialise_schedulers(self, worker):

        scheduler = getattr(importlib.import_module(worker["LOCATION"],
                                                    worker["CLASS"]))

        input_queue = self._queues[worker["INPUT_QUEUE"]]
        output_queue = self._queues[worker["OUTPUT_QUEUE"]]
        pagecount = self.data["ENVIRONMENT_VARIABLES"]["PAGE_COUNT"]

        self._one_thread_instance = scheduler(input_queue=input_queue,
                                              output_queue=output_queue,
                                              pagecount=pagecount)
        return {worker: self._one_thread_instance}

    def initialise_threads(self, worker):
        thread_count = worker["THREAD_COUNT"]
        for threads in thread_count:
            self._scheduler_threads.update(self.initialise_schedulers(worker))

    def pipeline(self):
        self.initialise_pipeline()
        self.initialise_queue()

        # The pipeline has nested structure,
        # the second thread (download_worker) instantiates inside the scraper_worker

        for page in self.data["ENVIRONMENT_VARIABLES"]["PAGE_COUNT"]:
            self.initialise_threads(self.data["WORKERS"]["SCRAPER_WORKER"])
            self._queues["scraper_q"].put(page)

            for i in range(len(self._scheduler_threads["SCRAPER_WORKER"])):
                self._queues["scraper_q"].put("DONE")

            for i in range(len(self._scheduler_threads["SCRAPER_WORKER"])):
                self._scheduler_threads["SCRAPER_WORKER"][i].join()


if __name__ == "__main__":
    pipe = PipelineBuild("config.yaml")
    pipe.pipeline()
    print(len(os.listdir(PipelineBuild.data["ENVIRONMENT_VARIABLES"]["IMAGE_DIR"])))


