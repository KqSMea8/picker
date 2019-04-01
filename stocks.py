#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
# Symbols from http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip
# Stock = YahooFinancials(symbol)
# financials_json = Stock.get_financial_stmts('quarterly', 'balance')
# yahoo_financials.get_financial_stmts('quarterly', 'balance')
#

import multiprocessing as mp
from yahoofinancials import YahooFinancials
import time
import math
import urllib.request
import os

def get_stock_data(symbol):
    try:
        start = time.time()
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        fin_url = 'https://uk.finance.yahoo.com/quote/' + symbol + '/financials?p=' + symbol
        fin_req = urllib.request.Request(fin_url, data=None, headers=headers)
        fin_response = urllib.request.urlopen(fin_req)
        fin_page = fin_response.read()
        end = time.time()
        print('symbol: {} balance_sheet: {} time: {}'.format(symbol, type(fin_page), (end - start)))
    except:
        pass
    return 'x'

symbol_list = []
symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbol_list.append(line.split('|')[0])

pool = mp.Pool(processes=10)
list = pool.map(get_stock_data, symbol_list)
