import mydb
import mytrader

tags = mydb.get_tags()
trailingStop = 1
thresholdScore = 5
positionratio = 1
aiversion = '海龟3号100%'

for tag in tags :
    #if tag =='上海' or tag =='全球股指' or tag =='加密货币' or tag =='商品期货' or tag =='外汇' or tag =='深圳':
    #    continue
    symbols = mydb.get_symbols(tag)
    #for symbol in symbols:
    #    mytrader.update_symbol_balance(symbol, trailingStop, positionratio)
    if len(symbols) == 0:
        continue
    datelist = mydb.get_datelist(symbols)
    currentbalance = 1.0
    tradingcount = 0
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
    exitsymboldict = {}
    entrydatedict = {}
    entrypricedict = {}
    exitpricedict = {}
    exitprofitdict = {}
    print("TAG:" + tag)
    for current_date in datelist:
        bestsymbol, score, side, price, tickers, atr = mydb.get_tickers(symbols, current_date)
        positions, currentbalance, currentprofit, currentprofitrate, exitsymbol,  entrydate,  entryprice, exitprice, exitprofit = mytrader.update_balance(positions, current_date, tickers, currentbalance, trailingStop)
        if bestsymbol is None or bestsymbol == "":
            continue
        balancedict[current_date] = currentbalance
        profit[current_date] = currentprofit
        profitrate[current_date] = currentprofitrate
        ordersdict[current_date] = len(positions)
        exitsymboldict[current_date] = exitsymbol
        entrydatedict[current_date] = entrydate
        entrypricedict [current_date] = entryprice
        exitpricedict[current_date] = exitprice
        exitprofitdict[current_date] = exitprofit
        if atr is None:
            atr = mydb.get_atr(bestsymbol, current_date)
        print("$"+ str(currentbalance) + ";Count:" +str(tradingcount) + ";" + tag + ":" + str(current_date) + ";Score:" + str(score) + ";ATR:" + str(atr) + ";Positions:" + str(len(positions))+";Symbol:" + str(bestsymbol) + ";Side:" + side)
        if score > thresholdScore and atr > 0.003 and price > 0:
            tradingcount = tradingcount + 1
            symboldict[current_date] = bestsymbol
            atrdict[current_date] = atr
            position = mytrader.new_position(current_date, bestsymbol, side, atr, price, currentbalance,positionratio)
            positions.append(position)
            sizedict[current_date] = position["size"]
            scoredict[current_date] = score
            sidedict[current_date] = side
    mydb.write_trading_log(tag, aiversion, trailingStop, thresholdScore, positionratio, datelist, balancedict, tradingcount, profit, profitrate, symboldict, atrdict, sizedict, scoredict, sidedict, ordersdict,
                           exitsymboldict,
                           entrydatedict,
                           entrypricedict,
                           exitpricedict,
                           exitprofitdict
                           )
