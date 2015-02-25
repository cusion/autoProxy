import math
import os
import os.path
import urllib2
import threading
import sys

import re
import time

global good_list
good_list = []

# Check proxy method
# user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'
# ip_check_url = 'http://ip.42.pl/raw'  # http://www.icanhazip.com/  http://myip.dnsdynamic.org/
# 
# def get_real_pip():
#     req = urllib2.Request(ip_check_url)
#     req.add_header('User-agent', user_agent)
#     conn = urllib2.urlopen(req)
#     page = conn.read()
#     return page
# 
# def check_proxy(pip):
#     try:
#         # Build opener
#         proxy_handler = urllib2.ProxyHandler({'http':pip})
#         opener = urllib2.build_opener(proxy_handler)
#         opener.addheaders = [('User-agent', user_agent)]
#         urllib2.install_opener(opener)
#  
#         # Build, time, and execute request
#         req = urllib2.Request(ip_check_url)
#         time_start = time.time()
#         conn = urllib2.urlopen(req)
#         time_end = time.time()
#         detected_pip = conn.read()
#  
#         # Calculate request time
#         time_diff = time_end - time_start
#  
#         # Check if proxy is detected
#         if detected_pip == get_real_pip():
#             proxy_detected = True
#         else:
#             proxy_detected = False
#  
#     # Catch exceptions
#     except urllib2.HTTPError, e:
#         # print "ERROR: Code ", e.code
#         return (True, False, 999)
#     except Exception, detail:
#         # print "ERROR: ", detail
#         return (True, False, 999)
#  
#     # Return False if no exceptions, proxy_detected=True if proxy detected
#     return (False, proxy_detected, time_diff) 


class Proxish(threading.Thread):
    def __init__(self, proxy_list, threadnum, timeout=10):
        threading.Thread.__init__(self)
        self.good_list = []
        self.thread_number = threadnum
        self.timeout = timeout
        self.list = proxy_list

    def verify_list(self, proxy_list):
        working_list = []
        for prox in proxy_list:
            try:
                proxy = urllib2.ProxyHandler({'http':'http://'+prox+'/'})
                opener = urllib2.build_opener(proxy)
                start_time = time.time()
                ip = opener.open("http://ip.42.pl/raw", timeout=self.timeout).readlines()
                end_time = time.time()
                if ip:
                    print '[Thread:', self.thread_number, '] Current IP:', ip[0]
                    print '[Thread:', self.thread_number, '] Proxy works:', prox
                    print '[Thread:', self.thread_number, '] match:', True if ip[0].find(prox.split(':')[0]) >= 0 else False
                    working_list.append(prox + "\t" + str(end_time-start_time))
            except Exception, e:#urllib2.URLError:
                print '[Thread:', self.thread_number, '] Proxy failed', prox
                print '[Thread:', self.thread_number, '] Proxy failed', e
        print '[Thread:', self.thread_number, '] Working Proxies:', working_list
        return working_list

    def run(self):
        global good_list
        good_list += self.verify_list(self.list)
        print '[All       ] Working Proxies:', good_list
        f = open('working_proxies.txt', 'r+')
        to_write = ''
        for i in good_list:
            to_write+= i+'\n'
        f.write(to_write)
        f.close()


def get_proxy_list():
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
            if file[:8] == 'proxies_':
                if not file[len(file)-1]== '~': # Gedit kept making temp files and it would read those
                    proxy_list.append(directory+file)
    return proxy_list

def get_proxies(files):
    proxy_list = []
    for file in files:
        for prox in open(file, 'r+').readlines():
            proxy_list.append(prox.strip())
    return proxy_list

def setup(number_threads):
    thread_amount = float(number_threads) # how many threads do you want the program to have?
    proxy_list = get_proxies(get_proxy_list()) # load the lists
    # get the amount to div the list into
    amount = int(math.ceil(len(proxy_list)/thread_amount))
    # split the large list into multiple smaller lists
    proxy_lists = [proxy_list[x:x+amount] for x in xrange(0, len(proxy_list), amount)]
    # if there is one left over, add ito the end of the last list
    if len(proxy_list) % thread_amount > 0.0:
        proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
    return proxy_lists

def start(threads):
    lists = setup(threads)
    thread_list = []
    good_list = []
    count = 0
    for list in lists:
        thread_list.append(Proxish(list, count))
        thread_list[len(thread_list)-1].start() # the above creates, but this starts
        count+=1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start(sys.argv[1])
    else:
        start(raw_input('How many threads you would like to test proxies with: '))