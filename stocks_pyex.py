#!/usr/bin/env python3

from iexfinance.stocks import Stock
import pyEX

for symbol in pyEX.symbolsList()[:50]:
    try:
        stock = Stock(symbol)
        financials_json = stock.get_financials(period = 'annual')
        quote_json = stock.get_quote()
        stats_json = stock.get_key_stats()

        company_name = quote_json['companyName']
        pb_ratio = stats_json['priceToBook']
        pe_ratio = quote_json['peRatio']
        market_cap = quote_json['marketCap']
        dividend_yield = stats_json['dividendYield']

        current_debt = financials_json[0]['currentDebt'] if financials_json[0]['currentDebt'] else 1
        total_liabilities = financials_json[0]['totalLiabilities'] if financials_json[0]['totalLiabilities'] else 0
        total_debt = financials_json[0]['totalDebt'] if financials_json[0]['totalDebt'] else 0
        net_income1 = financials_json[0]['netIncome'] if financials_json[0]['netIncome'] else 0
        net_income2 = financials_json[1]['netIncome'] if financials_json[1]['netIncome'] else 0
        net_income3 = financials_json[2]['netIncome'] if financials_json[2]['netIncome'] else 0
        net_income4 = financials_json[3]['netIncome'] if financials_json[3]['netIncome'] else 0

        current_ratio = financials_json[0]['currentAssets'] / current_debt
        debt_ratio = total_liabilities / financials_json[0]['shareholderEquity']
        debt_to_liq_ratio = total_debt / financials_json[0]['currentAssets']
        roe1 = net_income1 / financials_json[0]['shareholderEquity']
        roe2 = net_income2 / financials_json[1]['shareholderEquity']
        roe3 = net_income3 / financials_json[2]['shareholderEquity']
        roe4 = net_income4 / financials_json[3]['shareholderEquity']

        if current_ratio > 1.5 and debt_ratio < 0.5 and pe_ratio < 15 and pb_ratio < 1.5:
            print(company_name)
    except:
        pass
