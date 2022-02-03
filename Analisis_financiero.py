import yfinance as yf2
yf2.pdr_override()
import yahoo_fin.stock_info as yf
import numpy as np
import pandas as pd
from pandas_datareader import data as web
import matplotlib.pyplot as plt
import time



balance_sheet = []
income_statement = []
cfs = []
years = []
profitability_score = 0
leverage_score = 0
operating_efficiency_score = 0
pe_ratio = 0

summary = pd.DataFrame(columns=["Ticker", "PE Ratio", "Profitability", "Leverage", "Operating efficiency"])
tickers = yf.tickers_sp500()
#tickers = list(sav_set)
#print(type(tickers))
#print(len(tickers2))

def get_data(ticker):
    global balance_sheet
    global income_statement
    global cfs
    global years
    balance_sheet = yf.get_balance_sheet(ticker)
    income_statement = yf.get_income_statement(ticker)
    cfs = yf.get_cash_flow(ticker)
    years = balance_sheet.columns

def pe(ticker):
    global pe_ratio
    pe_ratio = yf.get_quote_table(ticker)["PE Ratio (TTM)"]
    if pe_ratio != pe_ratio: #Check if NaN 
        pe_ratio = 0

def profitability():
    global profitability_score
    # Scores 1 and 2 - Net Income
    net_income = income_statement[years[0]]["netIncome"]
    net_income_py = income_statement[years[1]]["netIncome"]
    ni_score = 1 if net_income > 0 else 0
    ni_score_2 = 1 if net_income > net_income_py else 0
    
    #Score 3 - Operating Cash Flow
    op_cf = cfs[years[0]]["totalCashFromOperatingActivities"]
    op_cf_score = 1 if op_cf > 0 else 0
    
    #Score 4 - Change in Return of Assets (ROA)
    Avrg_of_total_assets = (balance_sheet[years[0]]["totalAssets"] + 
                        balance_sheet[years[1]]["totalAssets"]) / 2 
    Avrg_of_total_assets_py = (balance_sheet[years[1]]["totalAssets"] + balance_sheet[years[2]]["totalAssets"]) / 2                                                                            
    RoA = net_income / Avrg_of_total_assets
    RoA_py = net_income_py / Avrg_of_total_assets_py
    RoA_score = 1 if RoA > RoA_py else 0
                                                                                   
    # Score 5 Accruals
    total_assets = balance_sheet[years[0]]["totalAssets"]                                                                               
    accrual = op_cf / total_assets                                                                       
    accruals_score = 1 if accrual > RoA else 0  
                                 
    profitability_score = ni_score + ni_score_2 + op_cf_score + RoA_score + accruals_score
    

def leverage():
    global leverage_score
    # Score 6 - Long term debt Ratio
    try:
        lt_debt = balance_sheet[years[0]]["longTermDebt"]
        total_assets = balance_sheet[years[0]]["totalAssets"]  
        deb_ratio = lt_debt / total_assets
        deb_ratio_score = 1 if deb_ratio > 0.40 else 0
    except:
        deb_ratio_score = 1
    # Score 7 - Current Ratio
    current_assets = balance_sheet[years[0]]["totalCurrentAssets"]
    current_liab = balance_sheet[years[0]]["totalCurrentLiabilities"]
    current_ratio = current_assets / current_liab
    current_ratio_score = 1 if current_ratio > 1 else 0 
    
    leverage_score = deb_ratio_score + current_ratio_score
  

def operating_efficiency():
    global operating_efficiency_score
    #Score 8 - Change in gross margin
    gp = income_statement[years[0]]["grossProfit"]
    gp_py = income_statement[years[1]]["grossProfit"]
    revenue = income_statement[years[0]]["totalRevenue"]
    revenue_py = income_statement[years[1]]["totalRevenue"]
    gm = gp / revenue
    gm_py = gp_py / revenue_py
    gm_score = 1 if gm > gm_py else 0
    
    #Score 9 - Change in asset turnover 
    Avrg_of_total_assets = (balance_sheet[years[0]]["totalAssets"] + 
                        balance_sheet[years[1]]["totalAssets"]) / 2 
    Avrg_of_total_assets_py = (balance_sheet[years[1]]["totalAssets"] + balance_sheet[years[2]]["totalAssets"]) / 2
    
    asset_turnover = Avrg_of_total_assets / revenue
    asset_turnover_py = Avrg_of_total_assets_py / revenue_py
    asset_turnover_score = 1 if asset_turnover > asset_turnover_py else 0 
    
    operating_efficiency_score = gm_score + asset_turnover_score
    
        
for ticker in tickers[100:101]:
    try:
        get_data(ticker)
        pe(ticker)
        profitability()
        leverage()
        operating_efficiency()
        new_row = {"Ticker": ticker, "PE Ratio": pe_ratio, "Profitability": profitability_score, "Leverage": leverage_score, "Operating efficiency": operating_efficiency_score}
        summary = summary.append(new_row, ignore_index=True)
        print(ticker + " added")
        time.sleep(3)
    except:
        print("Something went wrong with " + ticker)
summary["Total Score"] = summary["Profitability"] + summary["Leverage"] + summary["Operating efficiency"]

print(summary)