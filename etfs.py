#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
sys.setrecursionlimit(50000)
import sqlite3
import os

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
                    urls.append({'sector_desc': sector['desc'], 'etf_url': etf_url, 'etf_desc': etf_desc})
    return urls

def get_etf_details(etf):
    charge = None
    top_sectors=[]
    soup = get_soup(etf['etf_url'])
    if soup != None:
        for div in soup.find_all('div', attrs={'class': "tab-content margin-top"}):
            for tables in div.find_all('table', attrs={'class': "factsheet-table table-no-border"}):
                tr = tables.find('tr')
                td = tr.find('td')
                charge = td.text.strip().replace('%', '').replace('n/a', '')
        if charge != None and charge != '':
            for div in soup.find_all('div', attrs={'id': "top_10_sectors_data"}):
                for tables in div.find_all('table', attrs={'class': "factsheet-table top-10-table"}):
                    for tr in tables.find_all('tr'):
                        td = tr.find_all('td')
                        row = [i for i in td]
                        if len(row) > 1:
                            top_sectors.append({'sector': row[0].text, 'perc': row[1].text.replace('%', '')})
        if charge != None and charge != '':
            for div in soup.find_all('div', attrs={'id': "top_10_countries_data"}):
                for tables in div.find_all('table', attrs={'class': "factsheet-table top-10-table"}):
                    for tr in tables.find_all('tr'):
                        td = tr.find_all('td')
                        row = [i for i in td]
                        if len(row) > 1:
                            top_sectors.append({'sector': row[0].text, 'perc': row[1].text.replace('%', '')})

    return {'url': etf['etf_url'], 'etf_desc': etf['etf_desc'], 'charge': charge, 'top_sectors': top_sectors}


etfsfile = open('etfs.md', 'w')
etfsfile.write("# ETFs\n")
etfsfile.write("| ETF | Charge |\n")
etfsfile.write("| --- | ------:|\n")

try:
    os.remove('etfs.db')
except OSError:
    pass

db = sqlite3.connect('etfs.db')
c = db.cursor()
pool = mp.Pool(processes=10)


# c.execute('''CREATE TABLE search_sectors (sector_id number, sector_desc text)''')
header_soup = get_soup('http://www.hl.co.uk/shares/exchange-traded-funds-etfs')
sectors = []
for sector_select in header_soup.find_all('select', attrs={'id': "sectorid"}):
    for sector_option in sector_select.find_all('option'):
        sector_id = sector_option.get('value')
        sector_desc = sector_option.text
        if sector_id != '':
            sectors.append({'id': sector_id, 'desc': sector_desc})
#             c.execute('''INSERT INTO search_sectors(sector_id, sector_desc)
#                   VALUES(?,?)''', (sector_id, sector_desc))
# db.commit()

etf_list = pool.map(get_sector_urls, sectors)
c.execute('''CREATE TABLE etf_search_sectors (etf_id text, sector_desc text)''')
etf_url_list = []
for etfs in etf_list:
    for etf in etfs:
        c.execute('''INSERT INTO etf_search_sectors(etf_id, sector_desc)
              VALUES(?,?)''', (etf['etf_url'].split('/')[5], etf['sector_desc']))
        if {'etf_url': etf['etf_url'], 'etf_desc': etf['etf_desc']} not in etf_url_list:
            etf_url_list.append({'etf_url': etf['etf_url'], 'etf_desc': etf['etf_desc']})
db.commit()

etf_details = pool.map(get_etf_details, etf_url_list)
c.execute('''CREATE TABLE etf_details (etf_id text, etf_url text, etf_desc text, charge real)''')
c.execute('''CREATE TABLE etf_top_sectors (etf_id text, sector_desc text, perc real)''')
for etf_detail in etf_details:
   if etf_detail['charge'] != '' and etf_detail['charge'] != None:
        c.execute('''INSERT INTO etf_details(etf_id, etf_url, etf_desc, charge)
              VALUES(?,?,?,?)''', (etf_detail['url'].split('/')[5], etf_detail['url'], etf_detail['etf_desc'], etf_detail['charge']))
        for etf_top_sector in etf_detail['top_sectors']:
            c.execute('''INSERT INTO etf_top_sectors(etf_id, sector_desc, perc)
                  VALUES(?,?,?)''', (etf_detail['url'].split('/')[5], etf_top_sector['sector'], etf_top_sector['perc']))
db.commit()

for row in c.execute('select * from etf_details where charge < 1 and etf_id in (select etf_id from etf_search_sectors where sector_desc in (SELECT sector_desc FROM etf_search_sectors group by sector_desc having count(*) < 5))'):
        etfsfile.write("|[%s](%s \"Link\")|%s|\n" % (row[2], row[1], row[3]))
