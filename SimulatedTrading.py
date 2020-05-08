import mydb
import mytrader

tags = mydb.get_tags()
trailingStop = 2
thresholdScore = 20
positionratio = 1
aiversion = '海龟4号20%'

for tag in tags :
    #if tag =='上海' or tag =='全球股指' or tag =='加密货币' or tag =='商品期货' or tag =='外汇':
    #    continue
    symbols = mydb.get_symbols(tag)
    datelist = mydb.get_datelist(symbols)
    currentbalance = 1.0
    positions = []
    balancedict = {}
    profit = {}
    profitrate = {}
    symboldict = {}
    atrdict = {}
    sizedict = {}
    scoredict = {}
    sidedict = {}
    ordersdict = {}
    print("TAG:" + tag)
    for current_date in datelist:
        bestsymbol, score, side, price, tickers, atr = mydb.get_tickers(symbols, current_date)
        positions, currentbalance, currentprofit, currentprofitrate = mytrader.update_balance(positions, current_date, tickers, currentbalance, trailingStop)
        balancedict[current_date] = currentbalance
        profit[current_date] = currentprofit
        profitrate[current_date] = currentprofitrate
        ordersdict[current_date] = len(positions)
        if atr is None:
            atr = mydb.get_atr(bestsymbol, current_date)
        print("$"+ str(currentbalance) + ";" + tag + ":" + str(current_date) + ";Score:" + str(score) + ";ATR:" + str(atr) + ";Positions:" + str(len(positions))+";Symbol:" + str(bestsymbol) + ";Side:" + side)
        if score > thresholdScore and atr > 0.003 and price > 0:
            symboldict[current_date] = bestsymbol
            atrdict[current_date] = atr
            position = mytrader.new_position(current_date, bestsymbol, side, atr, price, currentbalance,positionratio)
            positions.append(position)
            sizedict[current_date] = position["size"]
            scoredict[current_date] = score
            sidedict[current_date] = side
    mydb.write_trading_log(tag, aiversion, trailingStop, thresholdScore, positionratio, datelist, balancedict, profit, profitrate, symboldict, atrdict, sizedict, scoredict, sidedict, ordersdict)
