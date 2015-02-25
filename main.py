'''This main file contains the top-level operations of crawling free proxies ,and then checking 
whether they are alive or not, finally using those alive ones to reach out the target websits '''

from settings import *
import free_proxy_crawler
import proxy_filter
import urllib2
import threading
from thread_utils import CountDownLatch
from free_proxy_crawler import ProxyCrawler

        
def get_module_clazz(path):
    seg = path.rfind('.')
    return path[:seg], path[seg+1:]
    
def initiate(clazz_path, *args, **kwargs):
    module, clazz = get_module_clazz(clazz_path)
    mod = __import__(module)
    return getattr(mod, clazz)(*args, **kwargs)

if __name__ == "__main__":
    webs = []
    for item in PROXY_WEBSITES:
        if item["used"]:
             webs.append(item)
    cdl = CountDownLatch(len(webs))
      
    for id, site in enumerate(webs):
        workingSpider = initiate(site["spider"], site["pages"])
        ProxyCrawler(id+1, workingSpider, cdl, CRAWLED_FILE_PREFIX).start()
          
    cdl.await()  # wait for those crawlers to get proxy_list
    print("===========================================")
    print("INFO: Crawler done!")
    
    proxy_filter.start(THREADS_NUMBER, CRAWLED_FILE_PREFIX, TARGET_WEBSITES)
    print("INFO: Filter done!")
    
        

    
