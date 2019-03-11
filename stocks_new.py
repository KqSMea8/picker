#!/usr/bin/env python3
# Using https://github.com/alpacahq/pylivetrader/blob/master/examples/graham-fundamentals/GrahamFundamentals.py

import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
import time
import timeout_decorator
from iexfinance.base import _IEXBase
from iexfinance.stocks import Stock
import sqlite3
import os


sys.setrecursionlimit(50000)
@timeout_decorator.timeout(10, use_signals=False)

def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None


def get_soup(url):
    try:
        # print("Opening: %s" % url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        req = urllib.request.Request(url, data=None, headers=headers)
        response = urllib.request.urlopen(req)
        page = response.read()
        # print("Got: %s" % url)
        return BeautifulSoup(page, "lxml")
    except:
        return None

def get_stock_info(url):
    soup = get_soup(url)
    foundcode='N'
    foundex='N'
    stock_dict = {}
    for dl in soup.find_all('dl', attrs={'class': "spacer-top"}):
        for dtdd in dl.find_all(['dt', 'dd']):
            stockinfo = dtdd.text.lstrip().rstrip()
            if foundcode == 'Y':
                stock_dict['stockcode'] = stockinfo
                foundcode = 'N'
            if foundex == 'Y':
                stock_dict['exchange'] = stockinfo
                foundex = 'N'
            if stockinfo == 'EPIC:' or stockinfo == 'Short code:':
                foundcode = 'Y'
            if stockinfo == 'Exchange:':
                foundex = 'Y'
    return stock_dict


print(get_stock_info('https://www.hl.co.uk/shares/shares-search-results/s/sig-plc-ordinary-10p-shares/company-information'))
print(get_stock_info('https://www.hl.co.uk/shares/shares-search-results/s/sinopec-shanghai-petrochemical-adr-rep-100/company-information'))
