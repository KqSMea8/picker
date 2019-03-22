#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
# Symbols from http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip
# Stock = YahooFinancials(symbol)
# financials_json = Stock.get_financial_stmts('quarterly', 'balance')
# yahoo_financials.get_financial_stmts('quarterly', 'balance')
#

import multiprocessing as mp
from yahoofinancials import YahooFinancials

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_stock_data(chunk):

    Stock = YahooFinancials(chunk)
    financials_json = Stock.get_financial_stmts('annually', 'balance')
    stats_json = Stock.get_key_statistics_data()
    return Stock.get_pe_ratio()
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

Stock = YahooFinancials(symbol_list)
financials_json = Stock.get_financial_stmts('annually', 'balance')
stats_json = Stock.get_key_statistics_data()


# pool = mp.Pool(processes=25)
# for chunk in list(chunks(symbol_list, 2)):
#     print(get_stock_data(chunk))
