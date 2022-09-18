import os
from pymeta.logger import Log
from urllib.parse import urlparse
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)


def delimiter2list(value, delim=","):
    return value.split(delim) if value else []


def delimiter2dict(value, delim_one=";", delim_two=":"):
    x = {}
    for item in value.split(delim_one):
        if item:
            sp = item.split(delim_two)
            x[sp[0].strip()] = delim_two.join(sp[1:]).strip()
    return x


###############################
# Argparse support
###############################
def file_exists(filename, contents=True):
    if os.path.exists(filename):
        return [line.strip() for line in open('filename')] if contents else filename
    Log.warn("Input file not found: {}".format(filename))
    exit(1)

def dir_exists(dir):
    if os.path.isdir(dir):
        return dir
    Log.warn("Input directory not found (\"{}\")\n".format(dir))
    exit(1)


###############################
# Download / file Support func.
###############################
def create_out_dir(base_dir, domain, base="meta"):
    dir_name = '{}_{}'.format(domain[0:4], base)
    write_dir = check_rename_dir(base_dir, dir_name)
    os.mkdir(write_dir)
    return write_dir

def check_rename_dir(base_dir, dir_name):
    count = 0
    tmp_name = os.path.join(base_dir, dir_name)
    while os.path.isdir(tmp_name):
        count += 1
        tmp_name = "{}_{}".format(dir_name, count)
    return tmp_name


def check_rename_file(filename, dwnld_dir):
    chk = filename.split('.')
    name = '.'.join(chk[:-1]) if len(chk) >= 2 else filename
    ext = chk[-1] if len(chk) >= 2 else ''

    count = 0
    tmp_name = os.path.join(dwnld_dir, name + "." + ext)
    while os.path.exists(tmp_name):
        count += 1
        tmp_name = os.path.join(dwnld_dir, "{}_{}.{}".format(name, count, ext))
    return tmp_name


def get_url_filename(url):
    try:
        fname = urlparse(url).path.split('/')[-1]
    except:
        fname = "not_found"
    return fname

