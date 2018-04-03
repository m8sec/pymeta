#!/usr/bin/env bash

# Author: m8r0wn
# Script: setup.sh

# Description:
# pymeta setup script to verify all required packages
# are installed on the system.

#Check if Script run as root
if [[ $(id -u) != 0 ]]; then
	echo -e "\n[!] Setup script needs to run as root\n\n"
	exit 0
fi

echo -e "\n[*] Starting pymeta setup script"
echo -e "[*] Checking for Python 3"
if [[ $(python3 -V 2>&1) == *"not found"* ]]
then
    echo -e "[*] Installing Python3"
    apt-get install python3 -y
else
    echo "[+] Python3 installed"
fi

echo -e "[*] Checking for Exiftool"
if [[ $(python3 -V 2>&1) == *"not found"* ]]
then
    echo -e "[*] Installing Exiftool"
    apt-get install exiftool -y
else
    echo "[+] Exiftool installed"
fi

echo -e "[*] Checking for required Python3 libraries"
if [[ $(python3 -c "import bs4" 2>&1) == *"No module"* ]]
then
    echo -e "[*] Installing BeautifulSoup"
    pip3 install bs4
else
    echo "[+] BeautifulSoup installed"
fi

echo -e "\n[*] pymeta setup complete\n\n"