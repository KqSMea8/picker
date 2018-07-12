#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup


def format_number(stringin):
    return stringin.replace('(', '-').replace(')', '').replace(',', '') if stringin != 'n/a' and stringin != 'cn/a' else None


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

for l in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0-9']:
    req_letter = urllib.request.Request('http://www.hl.co.uk/shares/shares-search-results/' + l, data=None, headers=headers)
    with urllib.request.urlopen(req_letter) as response_letter:
        page_letter = response_letter.read()
        soup_letter = BeautifulSoup(page_letter, "lxml")
        for search_link in soup_letter.find_all('a'):
            if search_link.get('class') == ['link-subtle'] and search_link.get('href').find('shares-search-results') > 1:
                url = search_link.get('href')
                req_search = urllib.request.Request(url, data=None, headers=headers)
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
                        with urllib.request.urlopen(req_fin) as response_fin:
                            page_fin = response_fin.read()
                            soup_fin = BeautifulSoup(page_fin, "lxml")
                            table = soup_fin.find_all('table')[0]
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

                            if all([url, name, price, market_cap, pe_ratio, volume, equity, net_income1, total_assets1, total_liabilities1,net_income2, total_assets2, total_liabilities2, net_income3, total_assets3, total_liabilities3,net_income4, total_assets4, total_liabilities4, net_income5, total_assets5, total_liabilities5,current_assets, current_liabilities]):
                                print("GOOD,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (url, name, price, market_cap, pe_ratio, volume, equity, net_income1, total_assets1, total_liabilities1,net_income2, total_assets2, total_liabilities2, net_income3, total_assets3, total_liabilities3,net_income4, total_assets4, total_liabilities4, net_income5, total_assets5, total_liabilities5,current_assets, current_liabilities))
                                debt_ratio = round(total_liabilities1/(total_assets1 - total_liabilities1), 2)
                                current_ratio = round(current_assets/current_liabilities, 2)
                                roe1 = round(net_income1/(total_assets1 - total_liabilities1), 2)
                                roe2 = round(net_income2/(total_assets2 - total_liabilities2), 2)
                                roe3 = round(net_income3/(total_assets3 - total_liabilities3), 2)
                                roe4 = round(net_income4/(total_assets4 - total_liabilities4), 2)
                                roe5 = round(net_income5/(total_assets5 - total_liabilities5), 2)
                                pb_ratio = round(price/((equity*1000000)/volume), 2)
