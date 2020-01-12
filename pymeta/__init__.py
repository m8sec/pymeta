#!/usr/bin/env python3

# Author: m8r0wn
# License: GPL-3.0

import argparse
import requests
import re
import os
from subprocess import getoutput
from sys import exit
from time import sleep
from bs4 import BeautifulSoup
from random import choice
from time import strftime
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)


class PyMeta():
    def __init__(self):
        self.__real_path = os.path.dirname(os.path.realpath(__file__))

        self.UA   = [line.strip() for line in open(os.path.join(self.__real_path, 'resources/user_agents.txt'))]
        self.EXIF = os.path.join(self.__real_path, 'resources/exiftool')
        self.URL  = {'google1': 'https://www.google.com/search?q=site:{}+filetype:{}&num=100',
                    'google2': 'https://www.google.com/search?q=site:{}+filetype:{}&num=100&start={}',
                    'bing1': 'http://www.bing.com/search?q=site:{}%20filetype:{}',
                    'bing2': 'http://www.bing.com/search?q=site:{}%20filetype:{}&first={}'}

        self.total_links = 0
        self.links       = []
        self.output      = './'
        self.filename    = ''

    def setup_logging(self, domain):
        write_dir = os.path.join(self.output, '{}_meta/'.format(self.filename))
        # If dir already exists, add dir_count to name of new folder
        dir_count = 2
        while os.path.exists(write_dir):
            write_dir = os.path.join(self.output, '{}_meta{}/'.format(self.filename, dir_count))
            dir_count += 1
        os.mkdir(write_dir)
        return write_dir

    def web_search(self, engine, domain, ext, search_cap):
        # regex to search for only domain pages w/ extension
        http = re.compile("http([^\)]+){}([^\)]+)\.{}".format(domain, ext))
        https = re.compile("https([^\)]+){}([^\)]+)\.{}".format(domain, ext))
        found_links = 0
        while True:
            try:
                new_links = 0
                if found_links == 0:
                    # Pull URL from dictionary
                    search_query = self.URL[engine + str(1)].format(domain, ext)
                else:
                    # Multiple pages in results
                    search_query = self.URL[engine + str(2)].format(domain, ext, found_links + 1)
                response = requests.get(search_query, headers={'User-Agent': choice(self.UA)}, verify=False, timeout=4)
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.findAll('a'):
                    try:
                        # return if max results hit
                        if self.total_links >= search_cap:
                            print("[*] {:4}:{:3} ".format(ext, new_links), search_query)
                            return
                        link = str(link.get('href'))
                        if engine not in link.lower():
                            if http.match(link) or https.match(link):
                                found_links += 1
                                if link not in self.links:
                                    self.links.append(link)
                                    self.total_links += 1
                                    new_links += 1
                    except:
                        pass
                print("[*] {:4}:{:3} ".format(ext, new_links), search_query)
                # return when no new results are found
                if new_links == 0:
                    return
                sleep(.5)
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                # print(e) #Debug
                pass

    def download_files(self, links, write_dir):
        for x in links:
            try:
                requests.packages.urllib3.disable_warnings()
                response = requests.get(x, headers={'User-Agent': choice(self.UA)}, verify=False, timeout=6)
                with open(write_dir + x.split("/")[-1], 'wb') as f:
                    f.write(response.content)
            except KeyboardInterrupt:
                print("\n[!] Keyboard Interrupt Caught...\n\n")
                exit(0)
            except Exception as e:
                # print(e) #Debug
                pass

    def extract_csv(self, file_dir, outfile):
        meta_fields = ['File Name', 'File Size', 'Author', 'Creator', 'File Type', 'File Type Extension', 'MIME Type',
                       'Creator Tool', 'PDF Version', 'Title', 'Application', 'Producer', 'Company', 'Create Date',
                       'Modify Date',
                       'Last Modified By', 'File Modification Date/Time', 'File Access Date/Time',
                       'File Inode Change Date/Time']
        link_count = 0
        # write headers, include source link if available
        if self.links:
            write_file(outfile, "\"Source Link\",")
        for m in meta_fields:
            write_file(outfile, "\"{}\",".format(m))
        write_file(outfile, "\n")  # newline
        # Add metadata content
        for f in os.listdir(file_dir):
            tmp_head = []
            tmp_data = []
            # Extract metadata in tab-delimited list to split output
            try:
                meta = getoutput("{} -t '{}'".format(self.EXIF, file_dir + f)).splitlines()
                for m in meta:
                    s = m.split("\t")
                    tmp_head.append(s[0])
                    tmp_data.append(s[1])
                if self.links:
                    write_file(outfile, "\"{}\",".format(self.links[link_count]))
                    link_count += 1
                for x in meta_fields:
                    try:
                        write_file(outfile, "\"{}\",".format(tmp_data[tmp_head.index(x)]))
                    except Exception as e:
                        # print(e)
                        write_file(outfile, "\"n/a\",")
                write_file(outfile, "\n")  # newline
            except Exception as e:
                print("Error with processing file {}: {}".format(f, e))

    def extract_term(self, file_dir):
        # Extract metadata and write unique Author, Creator, & Producer fields to terminal
        print("[*] Displaying all unique metadata, use -csv for more")
        found = []
        for f in os.listdir(file_dir):
            try:
                meta = getoutput("exiftool '{}'".format(file_dir + f)).splitlines()
                for m in meta:
                    n = m.split(":")
                    if "Author" in n[0] or "Creator" == n[0].strip() or "Producer" == n[0].strip():
                        if n[1].strip() and n[1].strip() not in found:
                            found.append(n[1].strip())
                            print("    {:8} : ".format(n[0].strip()) + n[1].strip())
            except Exception as e:
                print("Error with processing file {}: {}".format(f, e))


def write_file(file, data):
    if os.path.exists(file):
        option = 'a'
    else:
        option = 'w'
    OpenFile = open(file, option)
    OpenFile.write('%s' % (data))
    OpenFile.close()


def timestamp():
    return strftime('%d-%m-%y_%H_%M')


def path_exists(parser, pathname):
    if not os.path.exists(pathname):
        parser.error("Input files not found: {}".format(pathname))
    else:
        return pathname


def launcher(args):
    # Start pymeta
    filetypes = ['pdf', 'xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx']

    pyme = PyMeta()
    pyme.output = args.output

    if args.domain:
        if args.filename == 'original':
            filename = args.domain[0:4]
        else:
            filename = args.domain

        pyme.filename = filename
        print("\n[*] Starting web search")
        print("[*] Extension  |  Number of New Links Found  |  Search URL")
        # Seach Google &/or Bing for all file extensions in domain
        for ext in filetypes:
            # total links found in search, reset at each extension
            pyme.total_links = 0
            if args.engine == 'google' or args.engine == 'all':
                pyme.web_search('google', args.domain, ext, args.max_results)
            if args.engine == 'bing' or args.engine == 'all':
                pyme.web_search('bing', args.domain, ext, args.max_results)
        # Quit if no links found in search
        if not pyme.links:
            print("[-] No Results found, check search engine for captcha and manually inspect links\n")
            exit(0)
        # Setup logging folder and download files
        print("[*] Setting up folder for downloads")
        args.file_dir = pyme.setup_logging(args.domain)
        print("[*] Downloading files from the internet")
        pyme.download_files(pyme.links, args.file_dir)
    # Extract metadata from dir
    if args.csv:
        # create output file name

        try:
            outfile = os.path.join(args.output, "pymeta_{}.csv".format(filename))
        except:
            outfile = os.path.join(args.output, 'pymeta_{}.csv'.format(timestamp()))
        # Write csv report
        print("[*] Extracting Metadata from folder: {}, to {}".format(args.file_dir, outfile))
        pyme.extract_csv(args.file_dir, outfile)
    else:
        # Write to terminal
        print("[*] Extracting Metadata from folder: {}".format(args.file_dir))
        pyme.extract_term(args.file_dir)


def main():
    try:
        version = '1.0.2'
        args = argparse.ArgumentParser(description="""
            PyMeta
   -----------------------------------
Search the web for files on the targeted domain
and extract metadata.

usage:
    pymeta -d example.com -s all -csv
    pymeta -d example.org -s bing
    pymeta -dir my_files/""".format(version), formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
        action = args.add_mutually_exclusive_group(required=True)
        action.add_argument('-d', dest='domain', type=str, default=False, help='Target domain')
        action.add_argument('-dir', dest="file_dir", type=lambda x: path_exists(args, x), default=False, help="Directory of files to extract Metadata")
        args.add_argument('-s', dest='engine', type=str, default='all', help='Search engine to use: google, bing, all (Default: all)')
        args.add_argument('-m', dest='max_results', type=int, default=50, help='Max results to collect per file type (Default: 50)')
        args.add_argument('-csv', dest="csv", action='store_true', help="write all metadata to CSV (Default: display in terminal)")
        args.add_argument('-o', dest="output", type=str, help="Path to store output (Default is PyMeta folder)", default="./")
        args.add_argument('-f', dest="filename", type=str, choices=['original', 'full'], help="File/folder naming scheme (original or full name)", default='original')
        args = args.parse_args()
        launcher(args)
    except KeyboardInterrupt:
        print("\n[!] Keyboard Interrupt Caught...\n\n")
        exit(0)