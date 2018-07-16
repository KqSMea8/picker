#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

etfsfile = open('stocks.md', 'w')
etfsfile.write("# Stocks\n")
etfsfile.write("| Stock |\n")


req_etf_header = urllib.request.Request('http://www.hl.co.uk/shares/exchange-traded-funds-etfs', data=None, headers=headers)
with urllib.request.urlopen(req_etf_header) as response_etf_header:
    page_etf_header = response_etf_header.read()
    soup_etf_header = BeautifulSoup(page_etf_header, "lxml")
    # print(soup_etf_header.prettify())
    for sector_select in soup_etf_header.find_all('select', attrs={'id': "sectorid"}):
        for sector_option in sector_select.find_all('option'):
            sector_id = sector_option.get('value')
            sector_desc = sector_option.text
            if sector_id != '':
                req_etf_by_sect = urllib.request.Request('http://www.hl.co.uk/shares/exchange-traded-funds-etfs/list-of-etfs?&etf_search_input=&companyid=&sectorid=' + sector_id + '&non_soph=1', data=None, headers=headers)
                with urllib.request.urlopen(req_etf_by_sect) as response_etf_by_sect:
                    page_etf_by_sect = response_etf_by_sect.read()
                    soup_etf_by_sect = BeautifulSoup(page_etf_by_sect, "lxml")
                    for etf_link in soup_etf_header.find_all('a', attrs={'class': "link-headline"}):
                        etf_url = etf_link.get('href')
                        etf_desc = etf_link.get('title')
                        if etf_desc != None:
                            req_etf_detail = urllib.request.Request(etf_url, data=None, headers=headers)
                            with urllib.request.urlopen(req_etf_detail) as response_etf_detail:
                                page_etf_detail = response_etf_detail.read()
                                soup_etf_detail = BeautifulSoup(page_etf_detail, "lxml")
                                for tables in soup_etf_detail.find_all('table', attrs={'class': "factsheet-table top-10-table"}):
                                    for table in tables:
                                        for tr in table.find_all('tr'):
                                            td = tr.find_all('td')
                                            row = [i.text for i in td]
                                            print("1: %s 2: %s" % (row[0], row[1]))
                                # print("sector_id: %s sector desc: %s link: %s title %s" % (sector_id, sector_desc, etf_url, etf_desc))
