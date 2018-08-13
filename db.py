#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
import sqlite3

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

        sector_table = soup.find('table', attrs={'summary': "Top 10 sectors"})
        if sector_table != None:
            table_rows = sector_table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                if len(row) > 1:
                    top_sectors.append({'sector': row[0], 'perc': row[1].replace('%', '')})

    return {'url': inv['inv_url'], 'inv_desc': inv['inv_desc'], 'charge': charge, 'pd': pd, 'pd12': pd12, 'top_sectors': top_sectors}

def get_etf_urls(sector):
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

def get_stock_urls(url):
    soup = get_soup(url)
    urls = []
    for link in soup.find_all('a'):
        if link.get('class') == ['link-subtle'] and link.get('href').find('shares-search-results') > 1:
            urls.append(link.get('href'))
    return urls


def get_stock_details(url):
    soup = get_soup(url)
    if soup != None:
        name = soup.title.text.split('|')[0]
        market_cap = None
        price = None
        pe_ratio = None
        volume = None
        for head_span in soup.find_all('span', attrs={'class': "ask price-divide"}):
            price = head_span.text.replace('£', '').replace(
                '$', '').replace('€', '').replace(',', '').split(' ')[0]
            if price.endswith('p'):
                price = str(float(price[0:-1]) / 100)
        for detail_div in soup.find_all('div', attrs={'class': "columns large-3 medium-4 small-6"}):
            try:
                if detail_div.span.text == 'Market capitalisation':
                    market_cap = detail_div.strong.text
                if detail_div.span.text == 'Volume':
                    if detail_div.strong.text == 'n/a':
                        volume = None
                    else:
                        volume = detail_div.strong.text.replace(',', '')
                if detail_div.span.text == 'P/E ratio':
                    if detail_div.strong.text == 'n/a':
                        pe_ratio = None
                    else:
                        pe_ratio = float(format_number(detail_div.strong.text))
            except AttributeError:
                pass

        if all([price, pe_ratio, volume]):
            fin_url = url + '/financial-statements-and-reports'
            fin_soup = get_soup(fin_url)
            tables = fin_soup.find_all('table', attrs={'class': "factsheet-table responsive"})
            if len(tables) > 0:
                table = tables[0]
                equity1 = None
                equity2 = None
                equity3 = None
                equity4 = None
                equity5 = None
                net_income1 = None
                net_income2 = None
                net_income3 = None
                net_income4 = None
                net_income5 = None
                total_liabilities = None
                current_assets = None
                current_liabilities = None
                current_assets_next = 'N'
                current_liabilities_next = 'N'

                for tr in table.find_all('tr'):
                    td = tr.find_all('td')
                    row = [i.text.replace('\t', '').replace(
                        '\r', '').replace('\n', '') for i in td]
                    if len(row) == 6:
                        if row[0] == 'Total Equity:':
                            equity1 = format_number(row[1])
                            equity2 = format_number(row[2])
                            equity3 = format_number(row[3])
                            equity4 = format_number(row[4])
                            equity5 = format_number(row[5])
                        if row[0] == 'Profit after tax from continuing operations:':
                            net_income1 = format_number(row[1])
                            net_income2 = format_number(row[2])
                            net_income3 = format_number(row[3])
                            net_income4 = format_number(row[4])
                            net_income5 = format_number(row[5])
                        if row[0] == 'Total Liabilities:':
                            total_liabilities = format_number(row[1])
                        if row[0] == 'Other Current Assets:':
                            current_assets_next = 'Y'
                        if row[0] == 'Other Current Liabilities:':
                            current_liabilities_next = 'Y'
                        if row[0] == '\xa0' and current_assets_next == 'Y':
                            current_assets_next = 'N'
                            current_assets = format_number(row[1])
                        if row[0] == '\xa0' and current_liabilities_next == 'Y':
                            current_liabilities_next = 'N'
                            current_liabilities = format_number(row[1])

                checkvars = [url, name, price, market_cap,
                             pe_ratio, volume, total_liabilities,
                             net_income1, equity1,
                             net_income2, equity2,
                             net_income3, equity3,
                             net_income4, equity4,
                             net_income5, equity5,
                             current_assets, current_liabilities]
                if all(checkvars):

                    try:
                        debt_ratio = round(
                            float(total_liabilities) / (float(equity1)), 2)
                        current_ratio = round(
                            float(current_assets) / float(current_liabilities), 2)
                        roe1 = round(float(net_income1) / float(equity1), 2)
                        roe2 = round(float(net_income2) / float(equity2), 2)
                        roe3 = round(float(net_income3) / float(equity3), 2)
                        roe4 = round(float(net_income4) / float(equity4), 2)
                        roe5 = round(float(net_income5) / float(equity5), 2)
                        pb_ratio = round(
                            float(price) / ((float(equity1) * 1000000) / int(volume)), 2)

                        return {'url': url, 'name': name, 'market_cap': market_cap,
                            'price': price, 'pe_ratio': pe_ratio, 'volume': volume,
                            'debt_ratio': debt_ratio, 'current_ratio': current_ratio,
                              'roe1': roe1, 'roe2': roe2, 'roe3': roe3, 'roe4': roe4, 'roe5': roe5,
                              'pb_ratio': pb_ratio}

                    except ValueError:
                        print("Value error processing %s" % url)
                        print("Price: %s Equity: %s Volume: %s" %
                              (price, equity1, volume))

                else:
                    return None

if __name__ == '__main__':

    sys.setrecursionlimit(50000)
    db = sqlite3.connect('picker.db')
    pool = mp.Pool(processes=10)

    header_soup = get_soup('http://www.hl.co.uk/shares/investment-trusts')
    sectors = []
    for sector_select in header_soup.find_all('select', attrs={'id': "sectorid"}):
        for sector_option in sector_select.find_all('option'):
            sector_id = sector_option.get('value')
            sector_desc = sector_option.text
            if sector_id != '':
                sectors.append({'id': sector_id, 'desc': sector_desc})

    c_generic = db.cursor()

    inv_list = pool.map(get_invtrust_urls, sectors)
    try:
        c_generic.execute('''DROP TABLE inv_search_sectors''')
    except sqlite3.OperationalError:
        pass
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

    try:
        c_generic.execute('''DROP TABLE inv_details''')
    except sqlite3.OperationalError:
        pass
    c_generic.execute('''CREATE TABLE inv_details (inv_id text, inv_url text, inv_desc text, charge real, pd real, pd12 real)''')
    try:
        c_generic.execute('''DROP TABLE inv_top_sectors''')
    except sqlite3.OperationalError:
        pass
    c_generic.execute('''CREATE TABLE inv_top_sectors (inv_id text, sector_desc text, perc real)''')

    for inv_detail in inv_details:
       if inv_detail['charge'] != '' and inv_detail['charge'] != None:
            c_generic.execute('''INSERT INTO inv_details(inv_id, inv_url, inv_desc, charge, pd, pd12)
                  VALUES(?,?,?,?,?,?)''', (inv_detail['url'].split('/')[5], inv_detail['url'], inv_detail['inv_desc'], inv_detail['charge'], inv_detail['pd'], inv_detail['pd12']))
            for inv_top_sector in inv_detail['top_sectors']:
                c_generic.execute('''INSERT INTO inv_top_sectors(inv_id, sector_desc, perc)
                      VALUES(?,?,?)''', (inv_detail['url'].split('/')[5], inv_top_sector['sector'], inv_top_sector['perc']))
    db.commit()

    try:
        c_generic.execute('''DROP VIEW v_sector_averages''')
    except sqlite3.OperationalError:
        pass
    c_generic.execute('create view v_sector_averages as ' +
        'select iss.sector_desc, round(avg(pd12)) avg  ' +
        'from inv_search_sectors iss  ' +
        'join inv_details id on iss.inv_id = id.inv_id  ' +
        'where pd12 > -90 and pd12 < 100 ' +
        'group by iss.sector_desc having count(*) > 2 ')
    db.commit()
