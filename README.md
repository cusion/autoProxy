# autoProxy
Automatically crawling free Proxy website to get working proxies and picking out those ones which could approach our target url

Steps:
1. set what is needed in settings.py
2. if you need to configure your own free proxy web site, you need to create another parser and pass it to the ProxyCrawler object. see what is configured like http://nntime.com/ in the settings.PROXY_WEBSITES
3. run main.py: python main.py
