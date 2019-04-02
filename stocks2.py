#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
# Symbols from http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip
#
# debt_ratio = balanceSheetHistory.totalCurrentLiabilities/balanceSheetHistory.totalStockholderEquity <0.5
# current_ratio = balanceSheetHistory.totalCurrentAssets/balanceSheetHistory.totalCurrentLiabilities >1.5
# roe = balanceSheetHistory.netIncome / balanceSheetHistory.totalStockholderEquity >0.08
# pe_ratio = get_pe_ratio() < 15
# pb_ratio = get_key_statistics_data().priceToBook < 1.5
# json.dumps(total_current_liabilities, indent=4, sort_keys=True)

import multiprocessing as mp
from yahoofinancials import YahooFinancials
import time
import json

symbols_list = []
symbols_file = open("symbols2.lst", "r")
for line in symbols_file:
    symbols_list.append(line.split('|')[0])

symbols_filtered_by_pe_ratio = []
start = time.time()
Stock = YahooFinancials(symbols_list)
pe_ratios = Stock.get_pe_ratio()
for symbol in symbols_list:
    if pe_ratios[symbol] != None and pe_ratios[symbol] < 15:
        symbols_filtered_by_pe_ratio.append(symbol)
end = time.time()
print('PE Filter: {}'.format(end - start))


symbols_filtered_by_pb_ratio = []
start = time.time()
Stock = YahooFinancials(symbols_filtered_by_pe_ratio)
key_stats_data = Stock.get_key_statistics_data()
for symbol in symbols_filtered_by_pe_ratio:
    if key_stats_data[symbol]['priceToBook'] != None and key_stats_data[symbol]['priceToBook'] < 1.5:
        symbols_filtered_by_pb_ratio.append(symbol)
end = time.time()
print('PB Filter: {}'.format(end - start))


start = time.time()
Stock = YahooFinancials(symbols_filtered_by_pb_ratio)
balance_sheet_data = Stock.get_financial_stmts('annual', 'balance')
income_sheet_data = Stock.get_financial_stmts('annual', 'income')
end = time.time()
print('Get sheet data: {}'.format(end - start))

for symbol in symbols_filtered_by_pb_ratio:
    bal1 = balance_sheet_data['balanceSheetHistory'][symbol][0]
    bal2 = balance_sheet_data['balanceSheetHistory'][symbol][1]
    bal3 = balance_sheet_data['balanceSheetHistory'][symbol][2]
    bal4 = balance_sheet_data['balanceSheetHistory'][symbol][3]
    bal1_key1 = next(iter(bal1))
    bal2_key1 = next(iter(bal2))
    bal3_key1 = next(iter(bal3))
    bal4_key1 = next(iter(bal4))
    inc1 = income_sheet_data['incomeStatementHistory'][symbol][0]
    inc2 = income_sheet_data['incomeStatementHistory'][symbol][1]
    inc3 = income_sheet_data['incomeStatementHistory'][symbol][2]
    inc4 = income_sheet_data['incomeStatementHistory'][symbol][3]
    inc1_key1 = next(iter(inc1))
    inc2_key1 = next(iter(inc2))
    inc3_key1 = next(iter(inc3))
    inc4_key1 = next(iter(inc4))

    total_current_liabilities1 = bal1[bal1_key1]['totalCurrentLiabilities']
    total_current_assets1 = bal1[bal1_key1]['totalCurrentAssets']
    total_stockholder_equity1 = bal1[bal1_key1]['totalStockholderEquity']
    total_stockholder_equity2 = bal2[bal2_key1]['totalStockholderEquity']
    total_stockholder_equity3 = bal3[bal3_key1]['totalStockholderEquity']
    total_stockholder_equity4 = bal4[bal4_key1]['totalStockholderEquity']
    net_income1 = inc1[inc1_key1]['netIncome']
    net_income2 = inc2[inc2_key1]['netIncome']
    net_income3 = inc3[inc3_key1]['netIncome']
    net_income4 = inc4[inc4_key1]['netIncome']
    pe_ratio = pe_ratios[symbol]
    pb_ratio = key_stats_data[symbol]['priceToBook']

    print('symbol: {} key_stats: {}'.format(symbol, pb_ratio))
