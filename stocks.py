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
        return None


def get_stock_urls(url):
    soup = get_soup(url)
    urls = []
    for link in soup.find_all('a'):
        if link.get('class') == ['link-subtle'] and link.get('href').find('shares-search-results') > 1:
            urls.append(link.get('href'))
    return urls


def get_stock_info(url):
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

stocksfile = open('stocks.md', 'w')
stocksfile.write("# Stocks\n")
stocksfile.write("| Stock | Debt Ratio | Current Ratio | Ave ROE | P/E Ratio | P/B Ratio |\n")
stocksfile.write("| ----- | ----------:| -------------:| -------:| ---------:| ---------:|\n")

pool = mp.Pool(processes=20)
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']
letter_urls = ['http://www.hl.co.uk/shares/shares-search-results/' + l for l in letters]

stock_urls_list = pool.map(get_stock_urls, letter_urls)

for stock_urls in stock_urls_list:
    stocks = pool.map(get_stock_info, stock_urls)

    for stock in stocks:
        if stock != None and stock["debt_ratio"] < 0.5 and stock["current_ratio"] > 1.5 and stock["roe1"] > 0.08 and stock["roe2"] > 0.08 and stock["roe3"] > 0.08 and stock["roe4"] > 0.08 and stock["roe5"] > 0.08 and stock["pe_ratio"] < 15 and stock["pb_ratio"] < 1.5:
            avg_roe = round((stock["roe1"] + stock["roe2"] + stock["roe3"] + stock["roe4"] + stock["roe5"])/5, 2)
            stocksfile.write("|[%s](%s \"Link\")|%s|%s|%s|%s|%s|\n" % (stock["name"], stock["url"], stock["debt_ratio"], stock["current_ratio"], avg_roe, stock["pe_ratio"], stock["pb_ratio"]))
