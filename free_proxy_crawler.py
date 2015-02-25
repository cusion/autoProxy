'''This file defines proxy website crawler, which is used to crawl a website providing 
free proxy lists, we will use these free proxies to filter out those fit for our purpose.'''
import time
import urllib2
import threading
import traceback
from bs4 import BeautifulSoup

__author__ = "Kui Xiong"
__contact__ = "kuixoing at gmail"

class ProxyItem(object):
    '''This class indicate one particular proxy server.'''
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.request_time = -1

class ProxyCrawler(threading.Thread):
    
    def __init__(self, id,  spider, latch, crawled_file_prefix="proxies_"):
        threading.Thread.__init__(self)
        self.id = id
        self.spider = spider
        self.latch = latch
        self.crawled_file_prefix=crawled_file_prefix
        self.proxy_list = []
        
    def parse_result(self):
        for i in xrange(self.spider.npages):
            html = self.spider.crawl()
            self.proxy_list += self.spider.parse(html)
            self.spider.next_page()
        return self.proxy_list
    
    def run(self):
        try:
            self.parse_result()
            # write to file
            file = open(self.crawled_file_prefix+str(self.id)+".txt", "w")
            for item in self.proxy_list:
                file.write(item.ip+":"+item.port+"\n")
            file.close()
        except Exception, e:
            print(e)
            print(traceback.format_exc())
        finally:
            self.latch.count_down()
            
    
class nntimeSpider(object):
    '''This ad-hoc crawler is intended to crawl a website whose url is http://nntime.com/'''
    
    start_url = "http://nntime.com/"
    reconnect_times = 4
    def __init__(self, npages = 4, timeout = 30, pn = 1):
        self.npages = npages
        self.pn = pn
        self.timeout = timeout
        self.url = self.start_url
        
    def crawl(self):
        html = ""
        print("crawling " + self.url)
        reconnection = 0
        timeout = self.timeout
        while reconnection < self.reconnect_times:
            if reconnection > 0:
                print("reconnecting " + str(reconnection) + "time(s)")
            try:
                response = urllib2.urlopen(self.url, timeout=timeout)
                reconnection = self.reconnect_times+1
            except Exception:
                timeout += timeout
                reconnection += 1
                
        if not response:
            return ""
        
        for line in response.readlines():
            html += line
        return html
    
    def parse(self, html):
        proxy_list = []
        content = BeautifulSoup(html).select("table#proxylist")
        
        # for the odd <tr> elements
        odd = content[0].select("tr.odd")
        for item in odd:
            port_len = item.select("td:nth-of-type(2)")[0].text.count('+')
            port = item.select("td:nth-of-type(1)")[0].input["value"][-port_len:]
            ip = item.select("td:nth-of-type(2)")[0].next.strip()
            print("crawled " + ip + ":" + port)
            proxy_list.append(ProxyItem(ip, port))
        
        # for the even <tr> elements
        even = content[0].select("tr.even")
        for item in even:
            port_len = item.select("td:nth-of-type(2)")[0].text.count('+')
            port = item.select("td:nth-of-type(1)")[0].input["value"][-port_len:]
            ip = item.select("td:nth-of-type(2)")[0].next.strip()
            print("crawled " + ip + ":" + port)
            proxy_list.append(ProxyItem(ip, port))
            
        return proxy_list
        
    
    def next_page(self):
        self.pn += 1
        self.url = self.start_url + "proxy-list-" + "%02d" % self.pn + ".htm"
        