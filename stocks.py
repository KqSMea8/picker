#!/usr/bin/env python3
# Using https://github.com/alpacahq/pylivetrader/blob/master/examples/graham-fundamentals/GrahamFundamentals.py

from iexfinance.stocks import Stock
import pyEX
import sqlite3
import os
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=2)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_stock_data(symbol, financials_json, quote_json, stats_json):

    data_dict = {'symbol': symbol,
                'company_name': None,
                'pb_ratio': None,
                'pe_ratio': None,
                'market_cap': None,
                'dividend_yield': None,
                'current_assets': None,
                'current_debt': None,
                'total_assets': None,
                'total_liabilities': None,
                'total_debt': None,
                'net_income1': None,
                'net_income2': None,
                'net_income3': None,
                'net_income4': None,
                'equity1': None,
                'equity2': None,
                'equity3': None,
                'equity4': None}

    try:
        data_dict['company_name'] = quote_json[symbol]['companyName']
        data_dict['pe_ratio'] = quote_json[symbol]['peRatio']
        data_dict['market_cap'] = quote_json[symbol]['marketCap']

        data_dict['pb_ratio'] = stats_json[symbol]['priceToBook']
        data_dict['dividend_yield'] = stats_json[symbol]['dividendYield']

        data_dict['current_assets'] = financials_json[symbol][0]['currentAssets']
        data_dict['current_debt'] = financials_json[symbol][0]['currentDebt']
        data_dict['total_assets'] = financials_json[symbol][0]['totalAssets']
        data_dict['total_liabilities'] = financials_json[symbol][0]['totalLiabilities']
        data_dict['total_debt'] = financials_json[symbol][0]['totalDebt']
        data_dict['net_income1'] = financials_json[symbol][0]['netIncome']
        data_dict['net_income2'] = financials_json[symbol][1]['netIncome']
        data_dict['net_income3'] = financials_json[symbol][2]['netIncome']
        data_dict['net_income4'] = financials_json[symbol][3]['netIncome']

        data_dict['equity1'] = financials_json[symbol][0]['shareholderEquity']
        data_dict['equity2'] = financials_json[symbol][1]['shareholderEquity']
        data_dict['equity3'] = financials_json[symbol][2]['shareholderEquity']
        data_dict['equity4'] = financials_json[symbol][3]['shareholderEquity']
    except:
        pass

    return data_dict

try:
    os.remove('stocks.db')
except OSError:
    pass

db = sqlite3.connect('stocks.db')
c = db.cursor()
c.execute('''CREATE TABLE stocks (symbol text,
    company_name text,
    pb_ratio real,
    pe_ratio real,
    market_cap real,
    dividend_yield real,
    current_assets real,
    current_debt real,
    total_assets real,
    total_liabilities real,
    total_debt real,
    net_income1 real,
    net_income2 real,
    net_income3 real,
    net_income4 real,
    equity1 real,
    equity2 real,
    equity3 real,
    equity4 real)''')


for chunk in list(chunks(pyEX.symbolsList(), 100)):
    stocks = Stock(chunk)
    financials_json = stocks.get_financials(period = 'annual')
    quote_json = stocks.get_quote()
    stats_json = stocks.get_key_stats()
    for symbol in chunk:
        stock = get_stock_data(symbol, financials_json, quote_json, stats_json)
        c.execute('''INSERT INTO stocks (
                symbol,
                company_name,
                pb_ratio,
                pe_ratio,
                market_cap,
                dividend_yield,
                current_assets,
                current_debt,
                total_assets,
                total_liabilities,
                total_debt,
                net_income1,
                net_income2,
                net_income3,
                net_income4,
                equity1,
                equity2,
                equity3,
                equity4
                )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                stock['symbol'],
                stock['company_name'],
                stock['pb_ratio'],
                stock['pe_ratio'],
                stock['market_cap'],
                stock['dividend_yield'],
                stock['current_assets'],
                stock['current_debt'],
                stock['total_assets'],
                stock['total_liabilities'],
                stock['total_debt'],
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
