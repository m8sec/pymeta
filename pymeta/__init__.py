#!/usr/bin/env python3
# Author: @m8sec
# License: GPLv3

import os
import threading
import argparse
from sys import exit
from time import sleep
from pymeta import exif
from pymeta import utils
from pymeta.logger import *
from subprocess import getoutput
from pymeta.search import PyMeta, download_file


def status(args):

    VERSION = 'v1.2.0'

    print("\nPyMeta {} - {}\n".format(VERSION, highlight("by @m8sec", "bold", "gray")))

    if args.file_dir:
        return

    Log.info("Target Domain     : {}".format(highlight(args.domain if args.domain else args.file_dir, "bold", "gray"), ))
    Log.info("Search Engines(s) : {}".format(highlight(', '.join(args.engine), "bold", "gray")))
    Log.info("File Types(s)     : {}".format(highlight(', '.join(args.file_type), "bold", "gray"), ))
    Log.info("Max Downloads     : {}\n".format(highlight(args.max_results, "bold", "gray")))


def cli():
    args = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    args.add_argument('--debug', dest="debug", action='store_true', help=argparse.SUPPRESS)
    args.add_argument('-T', dest='max_threads', type=int, default=5, help='Max threads for file download (Default=5)')
    args.add_argument('-t', dest='timeout', type=float, default=8, help='Max timeout per search (Default=8)')
    args.add_argument('-j', dest='jitter', type=float, default=1, help='Jitter between requests (Default=1)')

    search = args.add_argument_group("Search Options")
    search.add_argument('-s', '--search', dest='engine', default='google,bing', type=lambda x: utils.delimiter2list(x), help='Search Engine (Default=\'google,bing\')')
    search.add_argument('--file-type', default='pdf,xls,xlsx,csv,doc,docx,ppt,pptx', type=lambda x: utils.delimiter2list(x), help='File types to search')
    search.add_argument('-m', dest='max_results', type=int, default=50, help='Max results per type search')

    p = args.add_argument_group("Proxy Options")
    pr = p.add_mutually_exclusive_group(required=False)
    pr.add_argument('--proxy', dest='proxy', action='append', default=[], help='Proxy requests (IP:Port)')
    pr.add_argument('--proxy-file', dest='proxy', default=False, type=lambda x: utils.file_exists(x), help='Load proxies from file for rotation')

    output = args.add_argument_group("Output Options")
    output.add_argument('-o', dest="dwnld_dir", type=lambda x: utils.dir_exists(x), default="./", help="Path to create downloads directory (Default: ./)")
    output.add_argument('-f', dest="report_file", type=str, default="pymeta_report.csv", help="Custom report name (\"pymeta_report.csv\")")

    target = args.add_argument_group("Target Options")
    action = target.add_mutually_exclusive_group(required=True)
    action.add_argument('-d', dest='domain', type=str, default=False, help='Target domain')
    action.add_argument('-dir', dest="file_dir", type=lambda x: utils.dir_exists(x), default=False, help="Pre-existing directory of files")
    return args.parse_args()
    

def start_scrape(args):
    tmp = []
    Log.info('Searching {} for {} file type(s) on "{}"'.format(', '.join(args.engine), len(args.file_type), args.domain))

    for file_type in args.file_type:
        for search_engine in args.engine:
            pym = PyMeta(search_engine, args.domain, file_type, args.timeout, 3, args.proxy, args.jitter, args.max_results)
            if search_engine in pym.url.keys():
                tmp += pym.search()
                tmp = list(set(tmp))

    dwnld_dir = download_results(args, tmp)
    extract_exif(dwnld_dir, args.report_file, tmp)
    return tmp


def download_results(args, urls):
    if len(urls) == 0:
        Log.warn('No results found, closing...')
        exit(0)

    dwnld_dir = utils.create_out_dir(args.dwnld_dir, args.domain)
    Log.info("Setting up downloads folder at {}".format(dwnld_dir))

    Log.info("Downloading ({}) unique files".format(len(urls)))
    if len(urls) > 9: Log.info('This may take a minute...')

    active_th = []
    for url in urls:
        th = threading.Thread(target=download_file, args=(url, dwnld_dir))
        th. daemon = True
        th.start()
        active_th.append(th)
        sleep(args.jitter)

        while threading.activeCount() > args.max_threads:
            sleep(0.05)

        for th in active_th:
            if not th.is_alive():
                active_th.remove(th)

    while len(active_th) > 0:
        for th in active_th:
            if not th.is_alive():
                active_th.remove(th)
        sleep(0.05)

    return dwnld_dir


def extract_exif(file_dir, output_file, urls=[]):
    if len(os.listdir(file_dir)) == 0:
        Log.warn('No files found at {}, closing...'.format(file_dir))
        os.rmdir(file_dir)
        exit(0)

    Log.info("Extracting metadata from {}".format(file_dir))
    report_file = utils.check_rename_file(output_file, file_dir)

    cmd = "exiftool -csv -r {} > {}".format(file_dir, report_file)
    logging.debug('Executing: "{}"'.format(cmd))
    getoutput(cmd)

    if len(urls) > 0:
        Log.info("Adding source URL's in report\n")
        exif.report_source_url(urls, report_file)

    Log.success("Report complete: {}".format(report_file))


def main():
    try:
        args = cli()
        status(args)
        exif.exif_check()

        if args.debug: setup_debug_logger(); debug_args(args)
        extract_exif(args.file_dir, args.report_file) if args.file_dir else start_scrape(args)
    except KeyboardInterrupt:
        Log.warn("Key event detected, closing...")
        exit(0)


if __name__ == '__main__':
    main()
