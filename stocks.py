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
import math
import sqlite3

def get_stock_data(stock_data):
    start = time.time()
    symbol = stock_data['symbol']
    Stock = YahooFinancials(symbol)
    stock_data['pe_ratio'] = Stock.get_pe_ratio()
    if stock_data['pe_ratio'] != None and stock_data['pe_ratio'] < 15:
        key_stock_data = Stock.get_key_statistics_data()
        stock_data['pb_ratio'] = key_stock_data[symbol]['priceToBook']
        if stock_data['pb_ratio'] != None and stock_data['pb_ratio'] < 1.5:
            balance_sheet_data = Stock.get_financial_stmts('annual', 'balance')
            income_sheet_data = Stock.get_financial_stmts('annual', 'income')
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

            stock_data['liabilities'] = bal1[bal1_key1]['totalCurrentLiabilities']
            stock_data['assets'] = bal1[bal1_key1]['totalCurrentAssets']
            stock_data['equity1'] = bal1[bal1_key1]['totalStockholderEquity']
            stock_data['equity2'] = bal2[bal2_key1]['totalStockholderEquity']
            stock_data['equity3'] = bal3[bal3_key1]['totalStockholderEquity']
            stock_data['equity4'] = bal4[bal4_key1]['totalStockholderEquity']
            stock_data['net_income1'] = inc1[inc1_key1]['netIncome']
            stock_data['net_income2'] = inc2[inc2_key1]['netIncome']
            stock_data['net_income3'] = inc3[inc3_key1]['netIncome']
            stock_data['net_income4'] = inc4[inc4_key1]['netIncome']

    end = time.time()
    print('got: {} - {}'.format(symbol, round(end - start)))
    return stock_data


symbols_list = []
symbols_file = open("symbols.lst", "r")
for line in symbols_file:
    symbols_list.append({'symbol': line.split('|')[0], 'company_name': line.split('|')[1].rstrip()})

start = time.time()
pool = mp.Pool(processes=100)
stock_data = pool.map(get_stock_data, symbols_list)
end = time.time()

db = sqlite3.connect('stocks.db')
c = db.cursor()
c.execute('''DROP TABLE stocks''')
c.execute('''CREATE TABLE stocks (symbol text,
    company_name text,
    pb_ratio real,
    pe_ratio real,
    assets real,
    liabilities real,
    net_income1 real,
    net_income2 real,
    net_income3 real,
    net_income4 real,
    equity1 real,
    equity2 real,
    equity3 real,
    equity4 real)''')


for stock in stock_data:
    if 'liabilities' in stock:
        c.execute('''INSERT INTO stocks (
                symbol,
                company_name,
                pb_ratio,
                pe_ratio,
                assets,
                liabilities,
                net_income1,
                net_income2,
                net_income3,
                net_income4,
                equity1,
                equity2,
                equity3,
                equity4
                )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                stock['symbol'],
                stock['company_name'],
                stock['pb_ratio'],
                stock['pe_ratio'],
                stock['assets'],
                stock['liabilities'],
                stock['net_income1'],
                stock['net_income2'],
                stock['net_income3'],
                stock['net_income4'],
                stock['equity1'],
                stock['equity2'],
                stock['equity3'],
                stock['equity4']
                ))
        db.commit()

print('Ave time: {}'.format(round((end - start) / len(symbols_list), 2)))
