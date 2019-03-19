#!/usr/bin/env python3
# Using https://pypi.org/project/yahoofinancials/
from yahoofinancials import YahooFinancials

ticker = 'AAPL'
yahoo_financials = YahooFinancials(ticker)

yahoo_financials.get_financial_stmts('quarterly', 'balance')
