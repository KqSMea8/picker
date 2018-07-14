#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

file = open("output.csv","w")
file.write('url,')
file.write('name,')
file.write('price,')
file.write('market_cap,')
file.write('pe_ratio,')
file.write('volume,')
file.write('equity1,')
file.write('net_income1,')
file.write('equity2,')
file.write('net_income2,')
file.write('equity3,')
file.write('net_income3,')
file.write('equity4,')
file.write('net_income4,')
file.write('equity5,')
file.write('net_income5,')
file.write('total_liabilities')
file.write('current_assets,')
file.write('current_liabilities,')
file.write('debt_ratio,')
file.write('current_ratio,')
file.write('roe1,')
file.write('roe2,')
file.write('roe3,')
file.write('roe4,')
file.write('roe5,')
file.write('pb_ratio')
file.write('/n')

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
                                price = str(float(price[0:-1])/100)

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
                                        pe_ratio = float(detail_div.strong.text)
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
                                    equity1 = None
                                    net_income1 = None
                                    equity2 = None
                                    net_income2 = None
                                    equity3 = None
                                    net_income3 = None
                                    equity4 = None
                                    net_income4= None
                                    equity5 = None
                                    net_income5 = None
                                    total_liabilities = None
                                    current_assets = None
                                    current_liabilities = None

                                    current_assets_next='N'
                                    current_liabilities_next='N'
                                    for tr in table.find_all('tr'):
                                        td = tr.find_all('td')
                                        row = [i.text.replace('\t', '').replace('\r', '').replace('\n', '') for i in td]
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
                                                current_assets_next='Y'
                                            if row[0] == 'Other Current Liabilities:':
                                                current_liabilities_next='Y'
                                            if row[0] == '\xa0' and current_assets_next == 'Y':
                                                current_assets_next='N'
                                                current_assets = format_number(row[1])
                                            if row[0] == '\xa0' and current_liabilities_next == 'Y':
                                                current_liabilities_next='N'
                                                current_liabilities = format_number(row[1])

                                    if all([url, name, price, market_cap, pe_ratio, volume,
                                            equity1, net_income1,
                                            equity2, net_income2,
                                            equity3, net_income3,
                                            equity4, net_income4,
                                            equity5, net_income5,
                                            total_liabilities,
                                            current_assets, current_liabilities]):

                                        print("Trying calcs")
                                        try:
                                            debt_ratio = round(float(total_liabilities)/(float(equity1)), 2)
                                            current_ratio = round(float(current_assets)/float(current_liabilities), 2)
                                            roe1 = round(float(net_income1)/float(equity1), 2)
                                            roe2 = round(float(net_income2)/float(equity2), 2)
                                            roe3 = round(float(net_income3)/float(equity3), 2)
                                            roe4 = round(float(net_income4)/float(equity4), 2)
                                            roe5 = round(float(net_income5)/float(equity5), 2)
                                            pb_ratio = round(float(price)/((float(equity1) * 1000000) / int(volume)), 2)

                                            if debt_ratio < 0.5 and current_ratio > 1.5 and roe1 > 0.08 and roe2 > 0.08 and roe3 > 0.08 and roe4 > 0.08 and roe5 > 0.08 and pe_ratio < 15 and pb_ratio < 1.5:

                                                file.write(url + ',')
                                                file.write(name + ',')
                                                file.write(price + ',')
                                                file.write(market_cap + ',')
                                                file.write(str(pe_ratio) + ',')
                                                file.write(volume + ',')
                                                file.write(equity1 + ',')
                                                file.write(net_income1 + ',')
                                                file.write(equity2 + ',')
                                                file.write(net_income2 + ',')
                                                file.write(equity3 + ',')
                                                file.write(net_income3 + ',')
                                                file.write(equity4 + ',')
                                                file.write(net_income4 + ',')
                                                file.write(equity5 + ',')
                                                file.write(net_income5 + ',')
                                                file.write(total_liabilities + ',')
                                                file.write(current_assets + ',')
                                                file.write(current_liabilities + ',')
                                                file.write(str(debt_ratio) + ',')
                                                file.write(str(current_ratio) + ',')
                                                file.write(str(roe1) + ',')
                                                file.write(str(roe2) + ',')
                                                file.write(str(roe3) + ',')
                                                file.write(str(roe4) + ',')
                                                file.write(str(roe5) + ',')
                                                file.write(str(pb_ratio))
                                                file.write('/n')

                                        except ValueError:
                                            print("Value error processing %s" % url)
                                            print("Price: %s Equity: %s Volume: %s" % (price, equity1, volume))


                except urllib.error.HTTPError:
                    print('ERROR: %s - %s' % (req_search.full_url, msg))
