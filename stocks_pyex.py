#!/usr/bin/env python3

from iexfinance.stocks import Stock
import pyEX

for symbol in pyEX.symbolsList():
    stock = Stock(symbol)
    financials_json = stock.get_financials(period = 'annual')
    quote_json = stock.get_quote()
    stats_json = stock.get_key_stats()
