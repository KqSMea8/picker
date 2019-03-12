#!/usr/bin/env python3
import sqlite3
import os

stocksfile = open('stocks.md', 'w')
stocksfile.write("# Stocks\n")
stocksfile.write("| Company Name | D/E Ratio | P/E Ratio | P/B Ratio | Current Ratio | ROE1 | ROE2 | ROE3 | ROE4 | Dividend Yield | D/L Ratio | Market Cap |\n")
stocksfile.write("| ------------ | ---------:| ---------:| ---------:| -------------:| ----:| ----:| ----:| ----:| --------------:| ---------:| ----------:|\n")

db = sqlite3.connect('stocks.db')
c = db.cursor()

# for row in c.execute('select company_name,  round(total_debt / equity1, 2) debt_equity_ratio, '
for row in c.execute('select company_name, '
  + 'round(total_liabilities / equity1, 2) debt_equity_ratio, '
  + 'pe_ratio, '
  + 'pb_ratio, '
  + 'round(current_assets/current_debt, 2) current_ratio, '
  + 'round(net_income1 / equity1, 2) roe1, '
  + 'round(net_income2 / equity2, 2) roe2, '
  + 'round(net_income3 / equity3, 2) roe3, '
  + 'round(net_income4 / equity4, 2) roe4, '
  + 'dividend_yield, '
  + 'round(total_debt/current_assets, 2) debt_to_liq_ratio, '
  + 'market_cap '
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
        stocksfile.write("|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], ))
