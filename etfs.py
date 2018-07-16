#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

etfsfile = open('stocks.md', 'w')
etfsfile.write("# Stocks\n")
etfsfile.write("| Stock |\n")
