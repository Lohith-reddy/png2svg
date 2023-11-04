import importlib

import yaml
from multiprocessing import Queue


class PipelineBuild:
    def __init__(self, yaml_location):
        self.yaml = yaml_location

    def build(self):
        with open(self.yaml, 'r') as file:
            data = yaml.safe_load(file)
            file.close()

        for worker in data["WORKERS"]:
            for threads in worker["THREAD_COUNT"]:
                importlib.import_module(worker["CLASS"],)
                scheduler = ScrapeScheduler(scrape_q, pagecount=page, download_q=download_q)
                scraper_schedulers_list.append(scheduler)