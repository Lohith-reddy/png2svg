# Downloading free svg from web using multithreading

In web_scraping_svg, i tried to download svgs by scraping a website
but it took too much time. So in this iteration of web-scarping 
I will use multithreading to download svgs.

There is one more reason to use multithreading.
I am concurrently (pun intended) learning spark which
processes big data using multiprocessing and multithreading while
distributing the data across multiple nodes. So, implementing multithreading and multiprocessing 
in python will help me understand the underlying concepts better.

Project Structure:

main: main.py
    
- This is the main file which will be executed.

- It will call the functions from other files.

pipeline: pipeline.py
    
- This file contains the pipeline class which will control the flow of processes.
   
Schedulers: schedulers.py

- This file contains the schedulers which will schedule the processes.

- It contains two schedulers: 
    - ScraperScheduler: This scheduler will schedule the website scraping.
    - DownloadScheduler: This scheduler will schedule the downloading.

undraw: undraw.py
    
- This file contains the undraw class which will scrape the undraw website.

Config.py

- This file contains the configuration for the project.
- Changes to thread-count for each scraper,
- Changes to the number of pages of be scraped,
- directory to store the svgs,
- and other configurations can be made here.

utils: utils.py

- This file contains the utility functions.

.env

- contains the environment variables.

