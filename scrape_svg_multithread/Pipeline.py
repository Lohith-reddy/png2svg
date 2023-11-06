import importlib

import yaml
from multiprocessing import Queue


class PipelineBuild:
    def __init__(self, yaml_name):
        self._one_thread_instance = None
        self.yaml = yaml_name
        self.data = None
        self._queues = {}
        self._scheduler_threads = []
        self.pagecount = 0

    def import_yaml_data(self):
        with open(self.yaml, 'r') as file:
            self.data = yaml.safe_load(file)
            file.close()

    def initialise_queue(self):
        # initialising queues for each of the schedulers
        for queue in self.data["QUEUES"].values():
            self._queues[queue] = Queue()

    def initialise_scraper(self):
        # The pipeline has nested structure,
        # the second thread (download_worker) instantiates inside the scraper_worker
        # Here for every web page, we initiate a queue and threads
        # which will execute the svg_scraper func in undraw.py
        # there is not much use of multi-threading here, async programming would be better
        # might add async programming in the future
        print("Initializing scraper threads")
        for page in range(self.data["ENVIRONMENT_VARIABLES"]["PAGE_COUNT"]):
            self.pagecount = page
            self.initialise_threads(self.data["WORKERS"]["SCRAPER_WORKER"])
            self._queues["scraper_q"].put(page)
            for i in range(self.data["WORKERS"]["SCRAPER_WORKER"]["THREAD_COUNT"]):
                self._queues["scraper_q"].put("DONE")

            for i in range(self.data["WORKERS"]["SCRAPER_WORKER"]["THREAD_COUNT"]):
                self._scheduler_threads[i].join()
                if i == 0:
                    print("joining the scraper threads")

    def initialise_threads(self, worker):
        thread_count = worker["THREAD_COUNT"]
        for threads in range(thread_count):
            self._scheduler_threads.append(self.initialise_schedulers(worker))

    def initialise_schedulers(self, worker):

        scheduler = getattr(importlib.import_module(worker["LOCATION"]), worker["CLASS"])

        input_queue = self._queues[worker["INPUT_QUEUE"]]
        output_queue = self._queues[worker["OUTPUT_QUEUE"]]

        # the download scheduler will be initialised inside the scraper scheduler
        # using the output queue of the scraper scheduler
        # check scheduler.py for more info
        print("inputing page number", self.pagecount, "to scraper queue")
        self._one_thread_instance = scheduler(input_queue=input_queue,
                                              output_queue=output_queue,
                                              pagecount=self.pagecount)
        return self._one_thread_instance

    def pipeline(self):
        self.import_yaml_data()
        print("Pipeline initialised")
        self.initialise_queue()
        print("Queues initialised")
        self.initialise_scraper()
        print("Scraper initialised")
        # scrapper will initialise the threads
        # which will initialise the scraperworker instances
        # which internally initialises queues, thread_instances
        # and the function of download_worker.
