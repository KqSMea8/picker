#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

file = open("output.csv","w")
for l in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0-9']:
    req_letter = urllib.request.Request('http://www.hl.co.uk/shares/shares-search-results/' + l, data=None, headers=headers)
    with urllib.request.urlopen(req_letter) as response_letter:
        page_letter = response_letter.read()
        soup_letter = BeautifulSoup(page_letter, "lxml")
        for search_link in soup_letter.find_all('a'):
            if search_link.get('class') == ['link-subtle'] and search_link.get('href').find('shares-search-results') > 1:
                url = search_link.get('href')
                req_search = urllib.request.Request(url, data=None, headers=headers)
                print("Trying %s" % url)
                try:
                    with urllib.request.urlopen(req_search) as response_search:
                        page_search = response_search.read()
                        soup_search = BeautifulSoup(page_search, "lxml")
                        name = soup_search.title.text.split('|')[0]
                        market_cap = None
                        price = None
                        pe_ratio = None
                        volume = None

                        for head_span in soup_search.find_all('span', attrs={'class': "ask price-divide"}):
                            price=head_span.text.replace('£', '').replace('$', '').replace('€', '').replace(',', '').split(' ')[0]
                            if price.endswith('p'):
                                price = float(price[0:-1])/100

                        for detail_div in soup_search.find_all('div', attrs={'class': "columns large-3 medium-4 small-6"}):
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
                                        pe_ratio = detail_div.strong.text
                            except AttributeError:
                                pass

                        if all([price, pe_ratio, volume]):
                            url_fin=url + '/financial-statements-and-reports'
                            req_fin = urllib.request.Request(url_fin, data=None, headers=headers)
                            print("Trying %s" % url_fin)
                            with urllib.request.urlopen(req_fin) as response_fin:
                                page_fin = response_fin.read()
                                soup_fin = BeautifulSoup(page_fin, "lxml")
                                tables = soup_fin.find_all('table')
                                if len(tables) > 0:
                                    table = tables[0]
                                    equity = None
                                    net_income1 = None
                                    total_assets1 = None
                                    total_liabilities1 = None
                                    net_income2 = None
                                    total_assets2 = None
                                    total_liabilities2 = None
                                    net_income3 = None
                                    total_assets3 = None
                                    total_liabilities3 = None
                                    net_income4= None
                                    total_assets4 = None
                                    total_liabilities4 = None
                                    net_income5 = None
                                    total_assets5 = None
                                    total_liabilities5 = None
                                    current_assets = None
                                    current_liabilities = None

                                    current_assets_next='N'
                                    current_liabilities_next='N'
                                    for tr in table.find_all('tr'):
                                        td = tr.find_all('td')
                                        row = [i.text.replace('\t', '').replace('\r', '').replace('\n', '') for i in td]
                                        if len(row) == 6:
                                            if row[0] == 'Total Equity:':
                                                equity = row[1].replace('(', '-').replace(')', '').replace(',', '') if row[1] != 'n/a' and row[1] != 'cn/a' else None
                                            if row[0] == 'Profit after tax from continuing operations:':
                                                net_income1 = format_number(row[1])
                                                net_income2 = format_number(row[2])
                                                net_income3 = format_number(row[3])
                                                net_income4 = format_number(row[4])
                                                net_income5 = format_number(row[5])
                                            if row[0] == 'Total Assets:':
                                                total_assets1 = format_number(row[1])
                                                total_assets2 = format_number(row[2])
                                                total_assets3 = format_number(row[3])
                                                total_assets4 = format_number(row[4])
                                                total_assets5 = format_number(row[5])
                                            if row[0] == 'Total Liabilities:':
                                                total_liabilities1 = format_number(row[1])
                                                total_liabilities2 = format_number(row[2])
                                                total_liabilities3 = format_number(row[3])
                                                total_liabilities4 = format_number(row[4])
                                                total_liabilities5 = format_number(row[5])
                                            if row[0] == 'Other Current Assets:':
                                                current_assets_next='Y'
                                            if row[0] == 'Other Current Liabilities:':
                                                current_liabilities_next='Y'
                                            if row[0] == '\xa0' and current_assets_next == 'Y':
                                                current_assets_next='N'
                                                current_assets = format_number(row[1])
                                            if row[0] == '\xa0' and current_liabilities_next == 'Y':
                                                current_liabilities_next='N'
                                                current_liabilities = format_number(row[1])

                                    print("url: %s" % url)
                                    print("name: %s" % name)
                                    print("price: %s" % price)
                                    print("market_cap: %s" % market_cap)
                                    print("pe_ratio: %s" % pe_ratio)
                                    print("volume: %s" % volume)
                                    print("equity: %s" % equity)
                                    print("net_income1: %s" % net_income1)
                                    print("total_assets1: %s" % total_assets1)
                                    print("total_liabilities1: %s" % total_liabilities1)
                                    print("net_income2: %s" % net_income2)
                                    print("total_assets2: %s" % total_assets2)
                                    print("total_liabilities2: %s" % total_liabilities2)
                                    print("net_income3: %s" % net_income3)
                                    print("total_assets3: %s" % total_assets3)
                                    print("total_liabilities3: %s" % total_liabilities3)
                                    print("net_income4: %s" % net_income4)
                                    print("total_assets4: %s" % total_assets4)
                                    print("total_liabilities4: %s" % total_liabilities4)
                                    print("net_income5: %s" % net_income5)
                                    print("total_assets5: %s" % total_assets5)
                                    print("total_liabilities5: %s" % total_liabilities5)
                                    print("current_assets: %s" % current_assets)
                                    print("current_liabilities: %s" % current_liabilities)
                                    if all([url, name, price, market_cap, pe_ratio, volume, equity, net_income1, total_assets1,
                                        total_liabilities1,net_income2, total_assets2, total_liabilities2, net_income3, total_assets3,
                                        total_liabilities3,net_income4, total_assets4, total_liabilities4, net_income5, total_assets5,
                                        total_liabilities5,current_assets, current_liabilities]):

                                        print("Trying calcs")
                                        try:
                                            debt_ratio = round(float(total_liabilities1)/(float(total_assets1) - float(total_liabilities1)), 2)
                                            current_ratio = round(float(current_assets)/float(current_liabilities), 2)
                                            roe1 = round(float(net_income1)/(float(total_assets1) - float(total_liabilities1)), 2)
                                            roe2 = round(float(net_income2)/(float(total_assets2) - float(total_liabilities2)), 2)
                                            roe3 = round(float(net_income3)/(float(total_assets3) - float(total_liabilities3)), 2)
                                            roe4 = round(float(net_income4)/(float(total_assets4) - float(total_liabilities4)), 2)
                                            roe5 = round(float(net_income5)/(float(total_assets5) - float(total_liabilities5)), 2)
                                            pb_ratio = round(float(price)/((float(equity) * 1000000) / int(volume)), 2)

                                            if debt_ratio < 0.5 and current_ratio > 1.5 and roe1 > 0.08 and roe2 > 0.08 and roe3 > 0.08 and roe4 > 0.08 and roe5 > 0.08 and float(pe_ratio) < 15 and pb_ratio < 1.5:

                                                file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %
                                                    (url, name, price, market_cap, pe_ratio, volume, equity,
                                                     net_income1, total_assets1, total_liabilities1,
                                                     net_income2, total_assets2, total_liabilities2,
                                                     net_income3, total_assets3, total_liabilities3,
                                                     net_income4, total_assets4, total_liabilities4,
                                                     net_income5, total_assets5, total_liabilities5,
                                                     current_assets, current_liabilities,
                                                     debt_ratio, current_ratio, roe1, roe2, roe3, roe5, pb_ratio))

                                        except ValueError:
                                            print("Value error processing %s" % url)
                                            print("Price: %s Equity: %s Volume: %s" % (price, equity, volume))


                except urllib.error.HTTPError:
                    print('ERROR: %s - %s %s' % (req_search.full_url, code, msg))
