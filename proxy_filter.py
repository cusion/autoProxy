'''proxy_filter is used to pick out working proxies crawled by free_proxy_crawler, this is only
a test for whether the proxies are alive or not, by using ip address checker, when it comes to 
the availability of our target website, we finally need to use those alive ones to crawl one 
test page of the target again.'''

import math
import os
import os.path
import urllib2
import threading
import sys
import settings
from thread_utils import CountDownLatch

import re
import time
import traceback

__author__ = "Kui Xiong"
__contact__ = "kuixiong at gmail"

WORKING_RESULT_FILE = settings.WORKING_RESULT_FILE
IP_CHECK_WEBSITES = settings.IP_CHECK_WEBSITES
TARGET_RESULT_FILE = settings.TARGET_RESULT_FILE

class Proxy_checker(threading.Thread):
    def __init__(self, proxy_list, threadnum, latch, lock, timeout=10):
        threading.Thread.__init__(self)
        self.thread_number = threadnum
        self.timeout = timeout
        self.list = proxy_list
        self.latch = latch
        self.lock = lock

    def verify_list(self, proxy_list):
        working_list = []
        for prox in proxy_list:
            proxy = urllib2.ProxyHandler({'http':'http://'+prox+'/'})
            opener = urllib2.build_opener(proxy)
            is_alive = False
            cnt = 0
            while not is_alive and cnt < len(IP_CHECK_WEBSITES):
                try:
                    start_time = time.time()
                    ip = opener.open(IP_CHECK_WEBSITES[cnt], timeout=self.timeout).readlines()
                    end_time = time.time()
                    is_alive = True
                except Exception, e:
                    print '[Thread:', self.thread_number, ']', e
#                     print(traceback.format_exc())
                    cnt += 1
            if is_alive and ip:
                print '[Thread:', self.thread_number, '] Current IP:', ip[0]
                print '[Thread:', self.thread_number, '] Proxy works:', prox
                print '[Thread:', self.thread_number, '] match:', True if ip[0].find(prox.split(':')[0]) >= 0 else False
                working_list.append(prox + "\t" + str(end_time-start_time))
            else:
                print '[Thread:', self.thread_number, '] Proxy failed', prox
#         print '[Thread:', self.thread_number, '] Working Proxies:', working_list
        return working_list

    def run(self):
        good_list = self.verify_list(self.list)
        print '[Thread:', self.thread_number, '] Working Proxies :', good_list
        try:
            to_write = ''
            for i in good_list:
                to_write+= i+'\n'
            with self.lock:
                f = open(WORKING_RESULT_FILE, 'a')
                f.write(to_write)
                f.close()
        except Exception, e:
            print(e)
            print(traceback.format_exc())
        finally:
            self.latch.count_down()

class GeneralProxyFilter(object):
    
    def __init__(self, thread_num, crawled_file_prefix, latch):
        self.latch = latch
        self.threads_num = thread_num
        self.crawled_file_prefix = crawled_file_prefix

    def get_proxy_list(self):
        #get the directory
        file = os.path.abspath(__file__)
        for i in sorted(range(len(file)), reverse=True):
            if '/' in file[i] or '\\' in file[i]:
                directory = file[:i+1]
                break
        file_list = os.listdir(directory)
        proxy_list = []
        for file in file_list:
            if len(file) > 12:
                if file[:8] == self.crawled_file_prefix:
                    if not file[len(file)-1]== '~': # Gedit kept making temp files and it would read those
                        proxy_list.append(directory+file)
        return proxy_list
    
    def get_proxies(self, files):
        proxy_list = []
        for file in files:
            for prox in open(file, 'r').readlines():
                proxy_list.append(prox.strip())
        return proxy_list
    
    def setup(self):
        thread_amount = float(self.threads_num) # how many threads do you want the program to have?
        proxy_list = self.get_proxies(self.get_proxy_list()) # load the lists
        # get the amount to div the list into
        amount = int(math.ceil(len(proxy_list)/thread_amount))
        # split the large list into multiple smaller lists
        proxy_lists = [proxy_list[x:x+amount] for x in xrange(0, len(proxy_list), amount)]
        # if there is one left over, add ito the end of the last list
        if len(proxy_list) % thread_amount > 0.0:
            proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
        return proxy_lists
    
    def start(self):
        lists = self.setup()
        count = 0
        lock = threading.Lock()
        print("====================== Working Filter ========================")
        for list in lists:
            Proxy_checker(list, count, self.latch, lock).start()
            count += 1
            
class TargetProxyFilter(object):
    
    def __init__(self, targets, latch, timeout = 20):
        self.targets = targets
        self.latch = latch
        self.timeout = timeout
        
    def start(self):
        self.latch.await()
        print("====================== Target Filter ========================")
        http_ips = [line.split()[0] for line in open(WORKING_RESULT_FILE, 'r')]
        count = 0
        file = open(TARGET_RESULT_FILE, "w")
        for http_ip in http_ips:
            http_server = "http://" + http_ip
            http_proxy = urllib2.ProxyHandler({"http":http_server})
            http_opener = urllib2.build_opener(http_proxy)
            try:
                for site in self.targets:
                        start = time.time()
                        response = http_opener.open(site, timeout=self.timeout)
                        end = time.time()
                        print(site + " : http proxy " + http_ip + " response is -- " + response.read(50))
                file.write(http_ip + "\t" + str(end-start) + "\n")
            except Exception, e:
        #         print(url + " : could not connect using http proxy " + http_ip)
                print(e)
                count += 1
        print("[IFNO]Failed " + str(count) + "/" + len(http_ips))
        file.close()
        
def start(threads, crawled_file_prefix, targets):
    latch = CountDownLatch(threads)
    p = GeneralProxyFilter(threads, crawled_file_prefix, latch)
    c = TargetProxyFilter(targets, latch)
    p.start()
    c.start()
        
