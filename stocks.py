#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
# Symbols from http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip
#
# debt_ratio = balanceSheetHistory.totalCurrentLiabilities/balanceSheetHistory.totalStockholderEquity <0.5
# current_ratio = balanceSheetHistory.totalCurrentAssets/balanceSheetHistory.totalCurrentLiabilities >1.5
# roe = balanceSheetHistory.netIncome / balanceSheetHistory.totalStockholderEquity >0.08
# pe_ratio = get_pe_ratio() < 15
# pb_ratio = get_key_statistics_data().priceToBook < 1.5


import multiprocessing as mp
from yahoofinancials import YahooFinancials
import time

def get_stock_data(symbol):
    Stock = YahooFinancials(symbol)
    return {'symbol': symbol, 'pe_ratio': Stock.get_pe_ratio()}

symbols_list = []
symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbols_list.append(line.split('|')[0])

pool = mp.Pool(processes=1000)
start = time.time()
pe_ratios = pool.map(get_stock_data, symbols_list)
end = time.time()
print('PE Filter: {} - {}'.format(end - start, len(symbols_list)))
#
# symbols_filtered = []
# for symbol in symbols_list:
#     if pe_ratios[symbol] != None and pe_ratios[symbol] < 15:
#         symbols_filtered.append(symbol)

print(pe_ratios)
