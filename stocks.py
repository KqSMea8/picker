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

symbols_list = []
symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbols_list.append(line.split('|')[0])

symbols_filtered = []
Stock = YahooFinancials(symbols_list)
pe_ratios = Stock.get_pe_ratio()
for symbol in symbols_list:
    if pe_ratios[symbol] != None and pe_ratios[symbol] < 15:
        symbols_filtered.append({'symbol': symbol, 'pe_ratio': pe_ratios[symbol]})

print(symbols_filtered)
# pool = mp.Pool(processes=10)
# list = pool.map(get_pe_ratio, symbol_list)
