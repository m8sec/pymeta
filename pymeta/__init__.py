#!/usr/bin/env python3

import re
import os
import argparse
import requests
from sys import exit
from time import sleep
from random import choice
from time import strftime
from bs4 import BeautifulSoup
from subprocess import getoutput
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)

class PyMeta():
    def __init__(self, jitter, debug=False):
        self.__real_path   = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        self.__exiftool    = '{}/resources/exiftool'.format(self.__real_path)
        self.__user_agents = [line.strip() for line in open('{}/resources/user_agents.txt'.format(self.__real_path))]
        self.__urls        = {'google'    : 'https://www.google.com/search?q=site:{}+filetype:{}&num=100&start={}',
                              'bing'      : 'http://www.bing.com/search?q=site:{}%20filetype:{}&first={}',
                              'duckduckgo': 'https://duckduckgo.com/?q=site%3A{}%20filetype%3A{}&ia=web'}

        self.file_types = ['pdf', 'xls', 'xlsx', 'csv', 'doc', 'docx', 'ppt', 'pptx']
        self.running    = True
        self.debug      = debug
        self.links      = []
        self.detection  = 0
        self.jitter     = jitter

    def web_search(self, search, domain, ext, search_cap):
        http        = re.compile("http([^\)]+){}([^\)]+)\.{}".format(domain, ext))
        https       = re.compile("https([^\)]+){}([^\)]+)\.{}".format(domain, ext))
        link_count  = -1  # Count used to increment results in search URL
        total_links = 0   # Ensure search doesnt exceed maximum

        while self.running:
            tmp        = len(self.links)
            search_url = self.__urls[search].format(domain, ext, str(link_count + 1))
            try:
                headers    = {'User-Agent' : choice(self.__user_agents)}
                resp       = requests.get(search_url, headers=headers, verify=False, timeout=5)
                soup       = BeautifulSoup(resp.content, 'html.parser')

                # Captcha check on first pass of every Google search
                if search =='google' and link_count <= -1:
                    if self.detection_check(resp):
                        sleep(self.jitter)
                        return

                for link in soup.findAll('a'):
                    if total_links >= search_cap:
                        print("[*] {:<4}:{:>3} {}".format(ext, (len(self.links) - tmp), search_url))
                        return
                    else:
                        try:
                            link = str(link.get('href')).strip()
                            if search not in link.lower():
                                link_count += 1
                                if http.match(link) or https.match(link):
                                    if link not in self.links:
                                        self.links.append(link)
                                        total_links += 1
                                        if self.debug: print("[++] Found: {}".format(link))
                        except Exception as e:
                            if self.debug: print("[**] Link Parser Error: {}".format(str(e)))

                print("[*] {:<4}:{:>3} {}".format(ext, (len(self.links)-tmp), search_url))
                if (len(self.links)-tmp) == 0:
                    return
                sleep(self.jitter)
            except KeyboardInterrupt:
                print("[!] Key event detected")
                exit(0)
            except Exception as e:
                if self.debug: print("[**] Web Search Error: {}".format(str(e)))

    def detection_check(self, resp):
        if "you may be asked to solve the CAPTCHA" in resp.text and self.detection <= 1:
            self.detection += 1
            self.jitter = self.jitter + 5
            print("[!] Captcha'ed: Increasing jitter to {}".format(self.jitter))
            return True
        elif "you may be asked to solve the CAPTCHA" in resp.text and self.detection >= 2:
            print("[!] Captcha'ed: Change source IP's or come back later...")
            if len(self.links) > 0:
                self.running = False
                return True
            else:
                exit(0)
        return False

    def download_files(self, links, write_dir):
        for link in links:
            try:
                requests.packages.urllib3.disable_warnings()
                response = requests.get(link, headers={'User-Agent': choice(self.__user_agents)}, verify=False, timeout=6)
                with open(write_dir + link.split("/")[-1], 'wb') as f:
                    f.write(response.content)
            except KeyboardInterrupt:
                print("\n[!] Keyboard Interrupt Caught...\n\n")
                exit(0)
            except:
                pass

    def create_csv(self, file_dir, output_file):
        cmd = "perl {} -csv {}* > {}".format(self.__exiftool,file_dir,  output_file)
        resp = getoutput(cmd)
        if self.links:
            print("[*] Adding source URL's to the report")
            self.insert_sourceUrl(output_file)

    def insert_sourceUrl(self, output_file):
        tmp = '.pymeta_tmp.csv'
        with open(output_file, 'r', encoding="ISO-8859-1") as in_csv, open(tmp, 'w') as out_csv:
            for row in in_csv:
                try:
                    filename = self.url_match(row.split(',')[0])
                    out_csv.write("{},{}".format(filename, row))
                except:
                    pass
        os.remove(output_file)
        os.rename(tmp, output_file)

    def url_match(self, filename):
        if filename == "SourceFile":
            return "SourceURL"
        for url in self.links:
            # Split to account for custom dir paths
            if filename.split("/")[-1] in url:
                return url
        return "n/a"

######################################
# Misc Functions
######################################
def timestamp():
    return strftime('%d-%m-%y_%H_%M')

######################################
# File Handling & Verification
######################################
def create_outDir(out_dir, domain, base="_meta"):
    # Create DIR to download office files to
    out_dir = validate_dir(out_dir)
    write_dir = os.path.join(out_dir, '{}{}'.format(domain[0:4], base))
    write_dir = dedup_fileName(write_dir, ext="/")
    os.mkdir(write_dir)
    return write_dir

def validate_dir(path):
    if path.endswith("/"):
        path = path[:-1]

    if not os.path.isdir(path):
        print("\n[-] Directory not found: {}\n".format(path))
        exit(1)
    else:
        return path

def create_reportFile(filename, domain):
    '''
    Take in -dir or -d value and return a valid report name
    that wont overwrite or append an existing file/report
    '''
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    if filename:
        report_name = filename
        report_name = dedup_fileName(report_name)
    else:
        tmp = ''
        for x in domain:
            if x in chars:
                tmp += x
            if len(tmp) >= 4:
                break

        if not tmp:
            tmp = timestamp()

        report_name = "{}_meta".format(tmp)
        report_name = dedup_fileName(report_name, ext='.csv')
    return report_name

def dedup_fileName(file, ext=''):
    count = 2
    tmp = file
    if os.path.exists(file+ext):
        while os.path.exists(file+ext):
            file = '{}{}'.format(tmp, str(count))
            count += 1
    return file+ext

######################################
# Primary Handlers
######################################
def domain_handler(pymeta, output_dir, filename, search, max_results, domain):
    print("\n[*] Starting PyMeta web scraper")
    print("[*] Extension  |  Number of New Files Found  |  Search URL")

    for ext in pymeta.file_types:
        if search in ['google', 'all']:
            pymeta.web_search('google', domain, ext, max_results)
        if search in ['bing', 'all']:
            pymeta.web_search('bing', domain, ext, max_results)
        if search in ['duckduckgo', 'all']:
            pymeta.web_search('duckduckgo', domain, ext, max_results)

    if len(pymeta.links) == 0:
        print("[-] No Results found, check search engine for captchas and manually inspect inputs\n")
        exit(0)

    # Dont create output dir & file until results found
    output_dir  = create_outDir(output_dir, domain)
    report_file = create_reportFile(filename, domain)

    print("[*] Downloading {} files to: {}".format(str(len(pymeta.links)), output_dir))
    pymeta.download_files(pymeta.links, output_dir)
    dir_handler(pymeta, output_dir, report_file)

def dir_handler(pymeta, input_dir, report_file):
    print("[*] Extracting Metadata...".format(input_dir))
    pymeta.create_csv(input_dir, report_file)
    print("[+] Report complete: {}".format(report_file))

######################################
# Main
######################################
def launcher(args):
    pymeta = PyMeta(args.jitter, args.debug)

    if args.domain:
        domain_handler(pymeta, args.output_dir, args.filename, args.search, args.max_results, args.domain)
    else:
        report_file = create_reportFile(args.filename, args.file_dir)
        dir_handler(pymeta, args.file_dir, report_file)

def main():
    try:
        version = '1.0.4'
        args = argparse.ArgumentParser(description="""
            PyMeta v.{}
   -----------------------------------
Search the web for files on the targeted domain
and extract metadata.

usage:
    pymeta -d example.com -s all -csv
    pymeta -d example.org -s bing
    pymeta -dir my_files/""".format(version), formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)

        target = args.add_argument_group("Target Options")
        action = target.add_mutually_exclusive_group(required=True)
        action.add_argument('-d', dest='domain', type=str, default=False, help='Target domain')
        action.add_argument('-dir', dest="file_dir", type=lambda x: validate_dir(x), default=False, help="Pre-existing directory of files")

        search = args.add_argument_group("Search Options")
        search.add_argument('-s', dest='search', choices=['google','bing','duckduckgo','all'], default='all', help='Search engine(s) to scrape')
        search.add_argument('-m', dest='max_results', type=int, default=50, help='Max results per file type, per search engine (Default: 50)')
        search.add_argument('-j', dest='jitter', type=int, default=2, help='Seconds between search requests (Default: 2)')

        output = args.add_argument_group("Output Options")
        output.add_argument('-o', dest="output_dir", type=str, help="Path to store PyMeta's download folder (Default: ./)", default="./")
        output.add_argument('-f', dest="filename", type=str, default='', help="Custom report path/name.csv")
        output.add_argument('--debug', dest='debug', action='store_true', help='Show links as they are collected during scraping')

        args = args.parse_args()
        launcher(args)
    except KeyboardInterrupt:
        print("\n[!] Keyboard Interrupt Caught...\n\n")
        exit(0)
