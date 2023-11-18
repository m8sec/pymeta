import os
import logging
from pymeta.logger import Log
from subprocess import getoutput
from shutil import move


def exif_check():
    # Check exiftool installed
    try:
        float(getoutput('exiftool -ver'))
        return True
    except Exception:
        Log.warn("ExifTool not installed, closing.")
        exit(0)


def report_source_url(urls, output_file):
    # Add source URLs to exif data
    with (open(output_file, 'r', encoding="ISO-8859-1") as in_csv, open('.pymeta_tmp.csv', 'w') as out_csv):
        for r in in_csv:
            try:
                url = url_match(urls, r.split(',')[0])
                out_csv.write(f"{url},{r}")
            except Exception as e:
                logging.debug(f'URL ReParsing Error: {r} = {e}')

    os.remove(output_file)
    move('.pymeta_tmp.csv', output_file)


def url_match(urls, filename):
    if filename == "SourceFile":
        return "SourceURL"

    return next((url for url in urls if filename.split("/")[-1] in url), "n/a")
