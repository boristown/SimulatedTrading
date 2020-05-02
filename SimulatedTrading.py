import mydb
import mytrader
import math

tags = mydb.get_tags()
trailingStop = 2.0
thresholdScore = 90
aiversion = '海龟4号'

for tag in tags:
    symbols = mydb.get_symbols(tag)
    datelist = mydb.get_datelist(symbols)
    currentbalance = 1.0
    positions = []
    balance = {}
    profit = {}
    profitrate = {}
    symboldict = {}
    atrdict = {}
    sizedict = {}
    for current_date in datelist:
        bestsymbol, score, side, atr, price, tickers = mydb.get_tickers(symbols, current_date)
        positions, currentbalance, currentprofit, currentprofitrate = mytrader.update_balance(positions, current_date, tickers, currentbalance)
        balance[current_date] = currentbalance
        profit[current_date] = currentprofit
        profitrate[current_date] = currentprofitrate
        if math.abs(score) > thresholdScore:
            symboldict[current_date] = bestsymbol
            atrdict[current_date] = atr
            position = mytrader.new_position(current_date, bestsymbol, side, atr, price, balance)
            positions.append(position)
            sizedict[current_date] = position["size"]
    mydb.write_trading_log(tag, aiversion, trailingStop, thresholdScore, balance, profit, profitrate, symboldict, atrdict, sizedict)