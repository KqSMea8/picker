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

def get_invtrust_urls(sector):
    urls = []
    soup = get_soup('https://www.hl.co.uk/shares/investment-trusts/search-for-investment-trusts?it_search_input=&sectorid=' + sector['id'])

    for tables in soup.find_all('table', attrs={'summary': "Investment trust search results"}):
        for table in tables:
            for tr in table.find_all('tr'):
                td = tr.find_all('td')
                row = [i for i in td]
                if len(row) > 3:
                    inv_url = row[1].a.get('href')
                    inv_desc = row[1].text + ' ' + row[2].text
                    urls.append({'sector_desc': sector['desc'], 'inv_url': inv_url, 'inv_desc': inv_desc})
    return urls

def get_inv_details(inv):
    charge = None
    pd = None
    pd12 = None
    spread = None
    top_sectors=[]
    soup = get_soup(inv['inv_url'])
    if soup != None:
        trs = soup.find_all('tr')
        for tr in trs:
            if tr.th != None:
                if tr.th.text.strip() == 'Ongoing charge:':
                    charge = tr.td.text.strip().replace('%', '') if tr.td.text.strip().replace('%', '') != 'n/a' else None
                if tr.th.text.strip() == 'Premium/Discount:':
                    pd = tr.td.text.strip().replace('%', '') if tr.td.text.strip().replace('%', '') != 'n/a' else None
                if tr.th.text.strip() == '12m average Premium/Discount:':
                    pd12 = tr.td.text.strip().replace('%', '') if tr.td.text.strip().replace('%', '') != 'n/a' else None

        for price_span in soup.find_all('span', attrs={'class': "bid price-divide"}):
            sell = price_span.text.replace('£', '').replace('$', '').replace('€', '').replace(',', '').replace('p', '')

        for price_span in soup.find_all('span', attrs={'class': "ask price-divide"}):
            buy = price_span.text.replace('£', '').replace('$', '').replace('€', '').replace(',', '').replace('p', '')

        spread = round(((float(buy) - float(sell)) / float(buy))*100, 2)

        sector_table = soup.find('table', attrs={'summary': "Top 10 sectors"})
        if sector_table != None:
            table_rows = sector_table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                if len(row) > 1:
                    top_sectors.append({'sector': row[0], 'perc': row[1].replace('%', '')})

    return {'url': inv['inv_url'], 'inv_desc': inv['inv_desc'], 'charge': charge, 'pd': pd, 'pd12': pd12, 'spread': spread, 'top_sectors': top_sectors}

invsfile = open('invtrusts.md', 'w')

try:
    os.remove('invtrusts.db')
except OSError:
    pass

db = sqlite3.connect('invtrusts.db')
c_generic = db.cursor()
c_select = db.cursor()
c_unf_sector = db.cursor()
c_sectors = db.cursor()
c_inv_detail = db.cursor()

pool = mp.Pool(processes=10)

header_soup = get_soup('http://www.hl.co.uk/shares/investment-trusts')
sectors = []
for sector_select in header_soup.find_all('select', attrs={'id': "sectorid"}):
    for sector_option in sector_select.find_all('option'):
        sector_id = sector_option.get('value')
        sector_desc = sector_option.text
        if sector_id != '':
            sectors.append({'id': sector_id, 'desc': sector_desc})

inv_list = pool.map(get_invtrust_urls, sectors)
c_generic.execute('''CREATE TABLE inv_search_sectors (inv_id text, sector_desc text)''')
inv_url_list = []
for invs in inv_list:
    for inv in invs:
        c_generic.execute('''INSERT INTO inv_search_sectors(inv_id, sector_desc)
              VALUES(?,?)''', (inv['inv_url'].split('/')[5], inv['sector_desc']))
        if {'inv_url': inv['inv_url'], 'inv_desc': inv['inv_desc']} not in inv_url_list:
            inv_url_list.append({'inv_url': inv['inv_url'], 'inv_desc': inv['inv_desc']})
db.commit()

inv_details = pool.map(get_inv_details, inv_url_list)

c_generic.execute('''CREATE TABLE inv_details (inv_id text, inv_url text, inv_desc text, charge real, pd real, pd12 real, spread read)''')
c_generic.execute('''CREATE TABLE inv_top_sectors (inv_id text, sector_desc text, perc real)''')
for inv_detail in inv_details:
   if inv_detail['charge'] != '' and inv_detail['charge'] != None:
        c_generic.execute('''INSERT INTO inv_details(inv_id, inv_url, inv_desc, charge, pd, pd12, spread)
              VALUES(?,?,?,?,?,?,?)''', (inv_detail['url'].split('/')[5], inv_detail['url'], inv_detail['inv_desc'], inv_detail['charge'], inv_detail['pd'], inv_detail['pd12'], inv_detail['spread']))
        for inv_top_sector in inv_detail['top_sectors']:
            c_generic.execute('''INSERT INTO inv_top_sectors(inv_id, sector_desc, perc)
                  VALUES(?,?,?)''', (inv_detail['url'].split('/')[5], inv_top_sector['sector'], inv_top_sector['perc']))
db.commit()

c_generic.execute('''CREATE TABLE unfashionable_sectors (sector_desc text)''')
for row in c_select.execute('select iss.sector_desc from inv_search_sectors iss ' +
  'join inv_details id on iss.inv_id = id.inv_id ' +
  'where pd12 > -90 and pd12 < 100 ' +
  'group by iss.sector_desc having count(*) > 2 ' +
  'order by avg(pd12) limit 5'):
    c_generic.execute('''INSERT INTO unfashionable_sectors(sector_desc) VALUES(?)''', (row))
db.commit()

for unf_sector_row in c_unf_sector.execute('select iss.sector_desc from inv_search_sectors iss ' +
  'join inv_details id on iss.inv_id = id.inv_id ' +
  'where pd12 > -90 and pd12 < 100 ' +
  'group by iss.sector_desc having count(*) > 2 ' +
  'order by avg(pd12) limit 10'):
    unf_sector_desc = unf_sector_row[0]
    invsfile.write("# %s\n" % unf_sector_desc)
    invsfile.write("| Trust | Charge | Discount | Spread |\n")
    invsfile.write("| ----- | ------:| --------:| ------:|\n")
    for inv_detail in c_sectors.execute('select inv_url, inv_desc, charge, pd, spread from inv_details where inv_id in (select inv_id from inv_search_sectors where sector_desc = ?) and charge < 1 and spread < 5 order by charge, pd', (unf_sector_desc,)):
        invsfile.write("|[%s](%s \"Link\")|%s|%s|%s|\n" % (inv_detail[1], inv_detail[0], inv_detail[2], inv_detail[3], inv_detail[4]))
