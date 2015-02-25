# encoding=utf-8

__author__ = "Kui Xiong"
__contact__ = "kuixiong at gmail"

import socks
import urllib2
import scrapy
import socket
import time

# url = "http://www.falundafa.org/"
# url = "http://www.google.com/"
# url = "http://www.baidu.com"
url = "http://www.yelp.com"
# url = "http://www.dropbox.com"
timeout = 10

#normal web request
try:
    start = time.time()
    response = urllib2.urlopen(url, timeout = timeout)
    end = time.time()
    print(url+ " : normal response is -- " + response.read(10) + "\t" + str(end-start))
except Exception:
    print(url + " : could not connect using normal http!")
    
print("=======================================================")

http_ips = [line.split()[0] for line in open("working_proxies.txt")]
count = 0
for http_ip in http_ips:
    http_server = "http://" + http_ip
    http_proxy = urllib2.ProxyHandler({"http":http_server})
    http_opener = urllib2.build_opener(http_proxy)
    try:
        start = time.time()
        response = http_opener.open(url, timeout=timeout)
        end = time.time()
        print(url + " : http proxy " + http_ip + " response is -- " + response.read(10) + "\t" + str(end-start))
    except Exception:
#         print(url + " : could not connect using http proxy " + http_ip)
        count += 1
print("fails " + str(count))
    
print("=======================================================")

socks_type = socks.PROXY_TYPE_SOCKS5
socks_server = "127.0.0.1"
socks_port = 7070
socks.setdefaultproxy(socks_type, socks_server, socks_port)
socket.socket = socks.socket
try:
    start - time.time()
    response = urllib2.urlopen(url, timeout = timeout)
    end = time.time()
    print(url + " : socks5 response is -- " + response.read(50) + "\t" + str(end-start))
except Exception:
    print(url + " : could not connect using socks5 proxy!")
    