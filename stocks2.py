#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import numpy as np


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None


def get_soup(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        req = urllib.request.Request(url, data=None, headers=headers)
        response = urllib.request.urlopen(req)
        page_letter = response.read()
        return BeautifulSoup(page, "lxml")
    except:
        return None

# stocksfile = open('stocks.md', 'w')
# stocksfile.write("# Stocks\n")
# stocksfile.write("| Stock |\n")
# stocksfile.write("| ----- |\n")

pool = mp.Pool(processes=4)
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']
results = [pool.apply(get_soup, args=('http://www.hl.co.uk/shares/shares-search-results/' + l)) for l in letters]
print(results)
    # url = 'http://www.hl.co.uk/shares/shares-search-results/' + l
    # print("Opening: %s" % url)
    # first_soup = get_soup(url)
