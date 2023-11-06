import threading
import importlib
import yaml

from utils import download_img
from undraw import UnDraw

with open("config.yaml", 'r') as file:
    yaml_data = yaml.safe_load(file)
    file.close()


class DownloadScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(DownloadScheduler, self).__init__()
        self.queue = input_queue
        self.start()

    def run(self):
        print("Starting Download")
        while True:
            val = self.queue.get()
            if val == "DONE":
                break

            title = download_img(val)


class ScrapeScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(ScrapeScheduler, self).__init__()
        self.queue = input_queue
        self.pagecount = int(kwargs["pagecount"])
        self.download_q = kwargs["output_queue"]
        self.thread_count = int(yaml_data["WORKERS"]["DOWNLOAD_WORKER"]["THREAD_COUNT"])
        self.start()

    def run(self):
        print("received pagecount: ", self.pagecount, "\n")
        und = getattr(importlib.import_module(yaml_data["CLASSES"]["LOCATION"]),
                      yaml_data["CLASSES"]["NAME"])

        download_schedulers_list = []
        while True:
            val = self.queue.get()
            if val == "DONE":
                # when the scraper q gets empty it will send "DONE" signals to the download_q,
                # and we join all the download threads
                for i in range(len(download_schedulers_list)):
                    self.download_q.put("DONE")

                for i in range(len(download_schedulers_list)):
                    if i == 0:
                        print("Joining the download threads")
                    download_schedulers_list[i].join()
                # scheduler.download()
                break

            for i in range(self.thread_count):
                print("Initializing download thread: ", i, "\n")
                scheduler = DownloadScheduler(self.download_q)
                download_schedulers_list.append(scheduler)

            for i, j in und.get_svg(self.pagecount).items():
                self.download_q.put((i, j))
                print("Added to download queue: ", i, "\n")
