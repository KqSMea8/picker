#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
from yahoofinancials import YahooFinancials
from finsymbols import symbols

pyEX.symbolsList()

for stock in symbols.get_nasdaq_symbols():


Stock = YahooFinancials(stock)

yahoo_financials.get_financial_stmts('quarterly', 'balance')
