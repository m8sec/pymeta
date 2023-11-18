import logging
import os
import re
import sys
import threading
from datetime import datetime, timedelta
from random import choice
from time import sleep
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tldextract import extract
from urllib3 import disable_warnings, exceptions

from pymeta.logger import Log

disable_warnings(exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("tldextract").setLevel(logging.CRITICAL)
logging.getLogger("filelock").setLevel(logging.CRITICAL)


class Timer(threading.Thread):
    def __init__(self, timeout):
        threading.Thread.__init__(self)
        self.start_time = None
        self.running = None
        self.timeout = timeout

    def run(self):
        self.running = True
        self.start_time = datetime.now()
        logging.debug("Thread Timer: Started")

        while self.running:
            if (datetime.now() - self.start_time) > timedelta(seconds=self.timeout):
                self.stop()
            sleep(0.05)

    def stop(self):
        logging.debug("Thread Timer: Stopped")
        self.running = False


class PyMeta:
    def __init__(self, search_engine, target, file_type, timeout, conn_timeout=3, proxies=None, jitter=0,
                 max_results=50):
        if proxies is None:
            proxies = []
        self.search_engine = search_engine
        self.file_type = file_type.lower()
        self.conn_timeout = conn_timeout
        self.max_results = max_results
        self.timeout = timeout
        self.proxies = proxies
        self.target = target
        self.jitter = jitter

        self.results = []
        self.regex = re.compile(
            f"[https|https]([^\)]+){self.target}([^\)]+)\.{self.file_type}"
        )
        self.url = {'google': 'https://www.google.com/search?q=site:{}+filetype:{}&num=100&start={}',
                    'bing': 'http://www.bing.com/search?q=site:{}%20filetype:{}&first={}'}

    def search(self):
        search_timer = Timer(self.timeout)
        search_timer.start()

        while search_timer.running:
            try:
                last_result = len(self.results)

                url = self.url[self.search_engine].format(self.target, self.file_type, len(self.results))
                resp = web_request(url, self.conn_timeout, self.proxies)
                http_code = get_statuscode(resp)

                if http_code != 200:
                    Log.info("{:<3} | {:<4} - {} ({})".format(len(self.results), self.file_type, url, http_code))
                    Log.warn(f'None 200 response, exiting search ({http_code})')
                    break

                self.page_parser(resp)
                Log.info("{:<3} | {:<4} - {} ({})".format(len(self.results), self.file_type, url, http_code))

                if len(self.results) >= self.max_results:
                    Log.info(f'Max results hit, exiting search (max: {self.max_results})')
                    break

                if len(self.results) <= last_result:
                    logging.debug(
                        f"No new results, exiting search ({last_result}:{len(self.results)})"
                    )
                    break

                sleep(self.jitter)
            except KeyboardInterrupt:
                Log.warn("Key event detected, closing...")
                sys.exit(0)

        search_timer.stop()
        return self.results

    def page_parser(self, resp):
        for link in extract_links(resp):
            try:
                self.results_handler(link)
            except Exception as e:
                Log.warn(f"Failed Parsing: {link.get('href')}- {e}")

    def results_handler(self, link):
        url = str(link.get('href'))
        if self.regex.match(url):
            self.results.append(url)
            logging.debug(f'Added URL: {url}')


def get_statuscode(resp):
    try:
        return resp.status_code
    except Exception:
        return 0


def get_proxy(proxies):
    tmp = choice(proxies) if proxies else False
    return {"http": tmp, "https": tmp} if tmp else {}


def download_file(url, dwnld_dir, timeout=6):
    try:
        logging.debug(f'Downloading: {url}')
        response = requests.get(url, headers={'User-Agent': get_agent()}, verify=False, timeout=timeout)
        http_code = get_statuscode(response)

        if http_code != 200:
            Log.fail(f'Download Failed ({http_code}) - {url}')
            return

        with open(os.path.join(dwnld_dir, url.split("/")[-1]), 'wb') as f:
            f.write(response.content)
    except Exception as e:
        logging.debug(f"Download Error: {e}")


def web_request(url, timeout=3, proxies=[], **kwargs):
    try:
        s = requests.Session()
        r = requests.Request('GET', url, headers={'User-Agent': get_agent()}, **kwargs)
        p = r.prepare()
        return s.send(p, timeout=timeout, verify=False, proxies=get_proxy(proxies))
    except requests.exceptions.TooManyRedirects as e:
        Log.fail(f'Proxy Error: {e}')
    except Exception:
        pass
    return False


def extract_links(resp):
    soup = BeautifulSoup(resp.content, 'lxml')
    return list(soup.findAll('a'))


def extract_subdomain(url):
    return urlparse(url).netloc


def extract_webdomain(url):
    x = extract(url)  # extract base domain from URL
    return f'{x.domain}.{x.suffix}' if x.suffix else x.domain


def get_agent():
    return choice([
        '''Mozilla/5.0 (Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:57.0) Gecko/20100101 Firefox/57.0''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.55''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36''',
        '''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5''',
        '''Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/63.0''',
        '''Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.57''',
        '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063''',
        '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299''',
        ''''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0''',
        '''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0''',
        '''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0''',
        '''Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko''',
        '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36''',
        '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'''])
