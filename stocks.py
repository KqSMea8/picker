#!/usr/bin/env python3
# Using https://github.com/alpacahq/pylivetrader/blob/master/examples/graham-fundamentals/GrahamFundamentals.py

import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
import time
import timeout_decorator
from iexfinance.base import _IEXBase
from iexfinance.stocks import Stock
import sqlite3
import os


sys.setrecursionlimit(50000)
@timeout_decorator.timeout(10, use_signals=False)

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
    # start = time.time()
    soup = get_soup(url)
    # end = time.time()
    # print("Fetch time: {} - {}".format(end - start, url))
    urls = []
    try:
        for link in soup.find_all('a'):
            if link.get('class') == ['link-subtle'] and link.get('href').find('shares-search-results') > 1:
                urls.append(link.get('href'))
        return urls
    except:
        return None


def filter_fundamental_df(fundamental_df):
    # This is where we remove stocks that don't meet our investment criteria.
    return fundamental_df[
        (fundamental_df.current_ratio > 1.5) &
        (fundamental_df.debt_to_liq_ratio < 1.1) &
        (fundamental_df.pe_ratio < 9) &
        (fundamental_df.pb_ratio < 1.2) &
        (fundamental_df.dividend_yield > 1.0)
    ]


def get_stock_info(url):
    # start = time.time()
    soup = get_soup(url)
    # end = time.time()
    fundamentals_dict = {}
    fundamentals_dict['url'] = url
    fundamentals_dict['company_name'] = None
    fundamentals_dict['current_ratio'] = None
    fundamentals_dict['debt_ratio'] = None
    fundamentals_dict['debt_to_liq_ratio'] = None
    fundamentals_dict['pb_ratio'] = None
    fundamentals_dict['pe_ratio'] = None
    fundamentals_dict['market_cap'] = None
    fundamentals_dict['dividend_yield'] = None
    fundamentals_dict['roe1'] = None
    fundamentals_dict['roe2'] = None
    fundamentals_dict['roe3'] = None
    fundamentals_dict['roe4'] = None

    try:
        share_id = soup.find('h1').text.split('(')[1].split(')')[0]
        stock = Stock(share_id)
        financials_json = stock.get_financials(period = 'annual')
        quote_json = stock.get_quote()
        stats_json = stock.get_key_stats()
    except:
        return fundamentals_dict

    try:
        current_debt = financials_json[0]['currentDebt'] if financials_json[0]['currentDebt'] else 1
        fundamentals_dict['current_ratio'] = financials_json[0]['currentAssets'] / current_debt
    except:
        pass

    try:
        total_liabilities = financials_json[0]['totalLiabilities'] if financials_json[0]['totalLiabilities'] else 0
        fundamentals_dict['debt_ratio'] = total_liabilities / financials_json[0]['shareholderEquity']
    except:
        pass

    try:
        total_debt = financials_json[0]['totalDebt'] if financials_json[0]['totalDebt'] else 0
        fundamentals_dict['debt_to_liq_ratio'] = total_debt / financials_json[0]['currentAssets']
    except:
        pass

    try:
        net_income1 = financials_json[0]['netIncome'] if financials_json[0]['netIncome'] else 0
        fundamentals_dict['roe1'] = net_income1 / financials_json[0]['shareholderEquity']
    except:
        pass

    try:
        net_income2 = financials_json[1]['netIncome'] if financials_json[1]['netIncome'] else 0
        fundamentals_dict['roe2'] = net_income2 / financials_json[1]['shareholderEquity']
    except:
        pass

    try:
        net_income3 = financials_json[2]['netIncome'] if financials_json[2]['netIncome'] else 0
        fundamentals_dict['roe3'] = net_income3 / financials_json[2]['shareholderEquity']
    except:
        pass

    try:
        net_income4 = financials_json[3]['netIncome'] if financials_json[3]['netIncome'] else 0
        fundamentals_dict['roe4'] = net_income1 / financials_json[3]['shareholderEquity']
    except:
        pass

    fundamentals_dict['company_name'] = quote_json['companyName']
    fundamentals_dict['pb_ratio'] = stats_json['priceToBook']
    fundamentals_dict['pe_ratio'] = quote_json['peRatio']
    fundamentals_dict['market_cap'] = quote_json['marketCap']
    fundamentals_dict['dividend_yield'] = stats_json['dividendYield']
    return fundamentals_dict

# stocksfile = open('stocks.md', 'w')
# stocksfile.write("# Stocks\n")
# stocksfile.write("| Stock | Debt Ratio (<0.5) | Current Ratio (>1.5) | Ave ROE (>0.08)| P/E Ratio (<15)| P/B Ratio (<1.5)| Spread % |\n")
# stocksfile.write("| ----- | -----------------:| -------------------:| --------------:| --------------:| ---------------:| --------:|\n")

try:
    os.remove('stocks.db')
except OSError:
    pass

db = sqlite3.connect('stocks.db')
c = db.cursor()
c.execute('''CREATE TABLE stocks (url text, company_name text, current_ratio real,
    debt_ratio real, debt_to_liq_ratio real, pb_ratio real, pe_ratio real,
    market_cap real, dividend_yield real, roe1 real, roe2 real, roe3 real,
    roe4 real)''')

pool = mp.Pool(processes=20)
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']
# letters = ['a']
letter_urls = ['http://www.hl.co.uk/shares/shares-search-results/' + l for l in letters]
stock_urls_list = pool.map(get_stock_urls, letter_urls)

for stock_urls in stock_urls_list:
    stocks = pool.map(get_stock_info, stock_urls)
    for stock in stocks:
        c.execute('''INSERT INTO stocks (
                url,
                company_name,
                current_ratio,
                debt_ratio,
                debt_to_liq_ratio,
                pb_ratio,
                pe_ratio,
                market_cap,
                dividend_yield,
                roe1,
                roe2,
                roe3,
                roe4)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                stock['url'],
                stock['company_name'],
                stock['current_ratio'],
                stock['debt_ratio'],
                stock['debt_to_liq_ratio'],
                stock['pb_ratio'],
                stock['pe_ratio'],
                stock['market_cap'],
                stock['dividend_yield'],
                stock['roe1'],
                stock['roe2'],
                stock['roe3'],
                stock['roe4'] ))

        db.commit()
#
#     for stock in stocks:
#         if stock != None and stock["debt_ratio"] < 0.5 and stock["current_ratio"] > 1.5 and stock["roe1"] > 0.08 and stock["roe2"] > 0.08 and stock["roe3"] > 0.08 and stock["roe4"] > 0.08 and stock["roe5"] > 0.08 and stock["pe_ratio"] < 15 and stock["pb_ratio"] < 1.5 and stock["spread"] < 5:
#             avg_roe = round((stock["roe1"] + stock["roe2"] + stock["roe3"] + stock["roe4"] + stock["roe5"])/5, 2)
#             stocksfile.write("|[%s](%s \"Link\")|%s|%s|%s|%s|%s|%s|\n" % (stock["name"], stock["url"], stock["debt_ratio"], stock["current_ratio"], avg_roe, stock["pe_ratio"], stock["pb_ratio"], stock["spread"]))
