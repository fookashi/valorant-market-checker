import requests
from itertools import cycle

import proxy_check

URL_HTTP = 'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt'
URL_SOCKS5 = 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'


class ProxyParser:

    def __init__(self) -> None:
        self.proxies = None
        self.proxy_cycle = None

    def github_scrape(self, url):

        self.proxies = requests.get(url).text.splitlines()
        self.proxy_cycle = cycle(self.proxies)

        return self.proxies

    def get_proxy(self):
        if self.proxy_cycle is None:
            raise Exception('No proxies parsed!')
        
        proxy = next(self.proxy_cycle)

        return proxy


pp = ProxyParser()
proxies = pp.github_scrape(URL_SOCKS5)
get_proxy = pp.get_proxy


