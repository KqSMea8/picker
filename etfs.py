#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
sys.setrecursionlimit(50000)


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
        print("Error getting: %s" % url)
        return None

def get_sector_urls(sector):
    urls = []
    soup = get_soup('http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?&etf_search_input=&companyid=&sectorid=' + sector['id'] + '&non_soph=1')

    for tables in soup.find_all('table', attrs={'summary': "ETF search results"}):
        for table in tables:
            for tr in table.find_all('tr'):
                td = tr.find_all('td')
                row = [i for i in td]
                if len(row) > 5:
                    etf_url = row[1].a.get('href')
                    etf_desc = row[4].text
                    urls.append({'sector_id': sector['id'], 'sector_desc': sector['desc'], 'etf_url': etf_url, 'etf_desc': etf_desc})
    return urls

def get_etf_details(etf):
    sector_id = etf['sector_id']
    sector_desc = etf['sector_desc']
    etf_url = etf['etf_url']
    etf_desc = etf['etf_desc']
    soup = get_soup(etf_url)
    if soup != None:
        for tables in soup.find_all('table', attrs={'class': "factsheet-table table-no-border"}):
            print("URL: %s tables: %s" % (etf_url, tables))
            for table in tables:
                for tr in table.find_all('tr'):
                    td = tr.find_all('td')
                    row = [i for i in td]
                    print(row)


etfsfile = open('etfs.md', 'w')
etfsfile.write("# ETFs\n")
etfsfile.write("| ETF |\n")

header_soup = get_soup('http://www.hl.co.uk/shares/exchange-traded-funds-etfs')
sectors = []
for sector_select in header_soup.find_all('select', attrs={'id': "sectorid"}):
    for sector_option in sector_select.find_all('option'):
        sector_id = sector_option.get('value')
        sector_desc = sector_option.text
        if sector_id != '':
            sectors.append({'id': sector_id, 'desc': sector_desc})

pool = mp.Pool(processes=10)
etf_list = pool.map(get_sector_urls, sectors)
for etfs in etf_list:
   etf_details = pool.map(get_etf_details, etfs)
