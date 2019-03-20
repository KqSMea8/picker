#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
# Symbols from http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip
# from yahoofinancials import YahooFinancials
# Stock = YahooFinancials(symbol)
# financials_json = Stock.get_financial_stmts('quarterly', 'balance')
# yahoo_financials.get_financial_stmts('quarterly', 'balance')
#

import multiprocessing as mp

pool = mp.Pool(processes=1)

def get_stock_data(symbol):
    stock_data = []
    print(symbol)
    stock_data['company_name'] = symbol['company_name']
    return stock_data

symbol_list = []

symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbol_list.append({'symbol': line.split('|')[0], 'company_name': line.split('|')[1].rstrip()})

stocks = pool.map(get_stock_data, symbol_list)

for stock in stocks:
    print(stock['company_name'])
