# pymeta
![](https://img.shields.io/badge/Python-3.6+-blue.svg)&nbsp;&nbsp;
![](https://img.shields.io/badge/License-GPL%203.0-green.svg)

Pymeta is a Python3 rewrite of the tool [PowerMeta](https://github.com/dafthack/PowerMeta), created by [dafthack](https://twitter.com/dafthack) in PowerShell. It uses specially crafted search queries to identify and download the following file types (pdf, xls, xlsx, doc, docx, ppt, pptx) from a given domain using Google and Bing. Once downloaded, metadata is extracted from these files using Phil Harvey's [exiftool](https://sno.phy.queensu.ca/~phil/exiftool/). This is a common place for penetration testers to find internal domain names, usernames, software/version numbers, and identify an organization's naming conventions.

Pymeta can also be pointed at a directory to extract metadata from files manually downloaded using the '-dir' command line argument. See the 'Usage', and 'All Options' sections for more information. 

During metadata extraction, unique 'Author', 'Creator', and 'Producer' fields will be written to the terminal. However, more verbose output can be accomplished by generating a csv report with the '-csv' command line argument. 

## Install
* PyPi (last release)
```
pip3 install pymetadata
```

* GitHub (latest code)
```
git clone https://github.com/m8r0wn/pymeta
cd pymeta
python3 setup.py install
```

## Usage
* Search Google and Bing for files within example.com and extract metadata to terminal:<br>
```pymeat -d example.com```

* Search Google only for files within example.com and extract metadata to a csv report:<br>
```pymeta -d example.com -s google -csv```

* Extract metadata from files within the given directory and create csv report:<br>
```pymeta -dir ../Downloads/ -csv```


## All Options
    -h, --help      show help message and exit
    -d DOMAIN       Target domain
    -dir FILE_DIR   Directory of files to extract Metadata
    -s ENGINE       Search engine to use: google, bing, all (Default: all)
    -m MAX_RESULTS  Max results to collect per file type (Default: 50)
    -csv            write all metadata to CSV (Default: display in terminal)
    
## Credit
- Beau Bullock [(@dafthack)](https://twitter.com/dafthack) - [https://github.com/dafthack/PowerMeta](https://github.com/dafthack/PowerMeta)
- Phil Harvey - [https://sno.phy.queensu.ca/~phil/exiftool/](https://sno.phy.queensu.ca/~phil/exiftool/)
