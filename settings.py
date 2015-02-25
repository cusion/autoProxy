'''This file is used to setup resources needed during each process in the 
pipelines.'''

__author__ = "Kui Xiong"
__contact__ = "kuixiong at gmail"

PROXY_WEBSITES = [
                          {
                           "url" : "http://nntime.com/",
                           "used" : True,
                           "pages" : 6,
                           "spider" : "free_proxy_crawler.nntimeSpider"
                          },
                          {
                           "url" : "http://letushide.com/",
                           "used" : False
                          },
                          {
                           "url" : "http://www.xici.net.co/",
                           "used" : False
                          },
                          {
                           "url" : "http://www.proxy360.cn/default.aspx",
                           "used" : False
                          },
                         ]
CRAWLED_FILE_PREFIX = "proxies_"

IP_CHECK_WEBSITES = ["http://ip.42.pl/raw", "http://www.icanhazip.com/", "http://myip.dnsdynamic.org/",]
THREADS_NUMBER = 10
WORKING_RESULT_FILE = "working_proxies.txt"

TARGET_WEBSITES = ["http://www.yelp.com/",]
TARGET_RESULT_FILE = "target_proxies.txt"
