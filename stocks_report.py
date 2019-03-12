#!/usr/bin/env python3
import sqlite3
import os

stocksfile = open('stocks.md', 'w')
stocksfile.write("# Stocks\n")
stocksfile.write("| Company Name |\n")
stocksfile.write("| ------------ |\n")

db = sqlite3.connect('stocks.db')
c = db.cursor()

# for row in c.execute('select company_name,  round(total_debt / equity1, 2) debt_equity_ratio, '
for row in c.execute('select company_name, '
  + 'round(total_liabilities / equity1, 2) debt_equity_ratio, '
  + 'pe_ratio, '
  + 'pb_ratio, '
  + 'current_assets/current_debt current_ratio, '
  + 'dividend_yield, '
  + 'market_cap, '
  + 'total_debt/current_assets debt_to_liq_ratio, '
  + 'net_income1 / equity1 roe1, '
  + 'net_income2 / equity2 roe2, '
  + 'net_income3 / equity3 roe3, '
  + 'net_income4 / equity4 roe4 '
  + 'from stocks '
  + 'where '
  + '      debt_equity_ratio < 0.5 '
  + '  and pb_ratio < 1.5 '
  + '  and pe_ratio < 15 '
  # + '  and current_ratio > 1.5 '
  # + '  and current_ratio < 2.5 '
  + '  and roe1 > 0.08 and roe2 > 0.08 and roe3 > 0.08 and roe4 > 0.08 '
  # + '  and debt_to_liq_ratio < 1.1 '
  # + '  and dividend_yield > 1.0 '
  + 'order by debt_equity_ratio'):
        stocksfile.write("|%s|\n" % (row[0]))
