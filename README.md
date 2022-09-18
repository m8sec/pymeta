# PyMeta
<p align="left">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg"/>&nbsp;
  <img src="https://img.shields.io/badge/License-GPL%203.0-green.svg"/>&nbsp;
  <a href="https://www.twitter.com/m8sec">
      <img src="https://img.shields.io/badge/Twitter-@m8sec-blue?style=plastic&logo=twitter"/>
  </a>&nbsp;
  <a href="https://github.com/sponsors/m8sec">
      <img src="https://img.shields.io/badge/Sponsor-GitHub-red?style=plastic&logo=github"/>
  </a>
</p>

PyMeta is a Python3 rewrite of the tool [PowerMeta](https://github.com/dafthack/PowerMeta), created by [dafthack](https://twitter.com/dafthack) in PowerShell. It uses specially crafted search queries to identify and download the following file types (**pdf, xls, xlsx, csv, doc, docx, ppt, pptx**) from a given domain using Google and Bing scraping.

Once downloaded, metadata is extracted from these files using Phil Harvey's [exiftool](https://sno.phy.queensu.ca/~phil/exiftool/) and added to a ```.csv``` report.  Alternatively, Pymeta can be pointed at a directory to extract metadata from files manually downloaded using the ```-dir``` command line argument. See the [Usage](#Usage), or [All Options](#All-Options) section for more information.

#### Why?
Metadata is a common place for penetration testers and red teamers to find: domains, user accounts, naming conventions, software/version numbers, and more!

*Still not convinced? Checkout -* **[Hacking Organizations One Document at a Time With Metadata](https://infosecwriteups.com/hacking-organizations-one-document-at-a-time-with-metadata-1af2eb10f254)**

# Getting Started
### Prerequisites
[Exiftool](https://sno.phy.queensu.ca/~phil/exiftool/) is required and can be installed with:

&nbsp;&nbsp;&nbsp;&nbsp;**Ubuntu/Kali** - ```apt-get install exiftool -y```

&nbsp;&nbsp;&nbsp;&nbsp;**Mac OS** - ```brew install exiftool```

### Install:
Install the last stable release from PyPi:
```commandline
pip3 install pymetasec
```

Or, install the most recent code from GitHub:
```
git clone https://github.com/m8sec/pymeta
cd pymeta
python3 setup.py install
```

## Usage
* Search Google and Bing for files within example.com and extract metadata to a csv report:<br>
```pymeta -d example.com```

* Extract metadata from files within the given directory and create csv report:<br>
```pymeta -dir Downloads/```


## All Options
```
options:
  -h, --help            show this help message and exit
  -T MAX_THREADS        Max threads for file download (Default=5)
  -t TIMEOUT            Max timeout per search (Default=8)
  -j JITTER             Jitter between requests (Default=1)

Search Options:
  -s ENGINE, --search ENGINE
                        Search Engine (Default='google,bing')
  --file-type FILE_TYPE
                        File types to search
  -m MAX_RESULTS        Max results per type search

Proxy Options:
  --proxy PROXY         Proxy requests (IP:Port)
  --proxy-file PROXY    Load proxies from file for rotation

Output Options:
  -o DWNLD_DIR          Path to create downloads directory (Default: ./)
  -f REPORT_FILE        Custom report name ("pymeta_report.csv")

Target Options:
  -d DOMAIN             Target domain
  -dir FILE_DIR         Pre-existing directory of file
```
    
## Credit
- Beau Bullock [(@dafthack)](https://twitter.com/dafthack) - [https://github.com/dafthack/PowerMeta](https://github.com/dafthack/PowerMeta)
- Phil Harvey - [https://exiftool.org/](https://exiftool.org/)
