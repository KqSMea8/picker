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

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_stock_data(chunk):
    start = time.time()
    Stock = YahooFinancials(chunk)
    financials_json = Stock.get_financial_stmts('annually', 'balance')
    stats_json = Stock.get_key_statistics_data()
    end = time.time()
    print("length: {} time: {}".format(len(chunk), end - start))
    return {'fin': financials_json, 'stats': stats_json}
    # return Stock.get_pe_ratio()
    # stock_data = {}
    #
    # stock_data['company_name'] = symbol['company_name']
    # stock_data['pe_ratio'] = Stock.get_pe_ratio()
    # stock_data['pb_ratio'] = stats_json[0]
    # return stock_data

symbol_list = []

symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbol_list.append(line.split('|')[0])

symbol_count = len(symbol_list)
procs = 10
# chunksize = math.ceil(symbol_count / procs)
chunksize = 1000
pool = mp.Pool(processes=procs)
chunk = list(chunks(symbol_list, chunksize))
list = pool.map(get_stock_data, chunk)
