import os
from urllib.parse import urlparse

from urllib3 import disable_warnings, exceptions

from pymeta.logger import Log

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
    Log.warn(f"Input file not found: {filename}")
    exit(1)


def dir_exists(dir):
    if os.path.isdir(dir):
        return dir
    Log.warn(f'Input directory not found (\"{dir}\")\n')
    exit(1)


###############################
# Download / file Support func.
###############################
def create_out_dir(base_dir, domain, base="meta"):
    dir_name = f'{domain[:4]}_{base}'
    write_dir = check_rename_dir(base_dir, dir_name)
    os.mkdir(write_dir)
    return write_dir


def check_rename_dir(base_dir, dir_name):
    count = 0
    tmp_name = os.path.join(base_dir, dir_name)
    while os.path.isdir(tmp_name):
        count += 1
        tmp_name = f"{dir_name}_{count}"
    return tmp_name


def check_rename_file(filename, dwnld_dir):
    chk = filename.split('.')
    name = '.'.join(chk[:-1]) if len(chk) >= 2 else filename
    ext = chk[-1] if len(chk) >= 2 else ''

    count = 0
    tmp_name = os.path.join(dwnld_dir, f"{name}.{ext}")
    while os.path.exists(tmp_name):
        count += 1
        tmp_name = os.path.join(dwnld_dir, f"{name}_{count}.{ext}")
    return tmp_name


def get_url_filename(url):
    try:
        fname = urlparse(url).path.split('/')[-1]
    except Exception:
        fname = "not_found"
    return fname
