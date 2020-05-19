import mydb

def update_balance(positions, current_date, tickers, currentbalance, trailingStop):
    currentprofit = 0.0
    currentprofitrate = 0.0
    exitflag = False
    exitsymbol = ""
    entrydate = None
    entryprice = 0.0
    exitprice = 0.0 
    exitprofit = 0.0
    for position in positions:
        stoplosspoint = trailingStop * position["atr"] + 1
        if position["symbol"] in tickers:
            symbolticker = tickers[position["symbol"]]
            if position["side"] == "buy":
                if symbolticker["l"] > 0 and position["highprice"] / symbolticker["l"]  > stoplosspoint:
                    position["exitprice"] = position["highprice"] / stoplosspoint
                    position["profit"] = position["size"] * (position["exitprice"] / position["entryprice"] - 1.0)
                    currentprofit = currentprofit + position["profit"]
                    if abs(position["profit"]) > exitprofit:
                        exitsymbol = position["symbol"]
                        entrydate = position["entrydate"]
                        entryprice = position["entryprice"]
                        exitprice = position["exitprice"]
                        exitprofit = abs(position["profit"])
                    position["exitdate"] = current_date
                    exitflag = True
                if symbolticker["h"] > position["highprice"]:
                    position["highprice"] = symbolticker["h"]
            else:
                if  position["lowprice"] > 0 and symbolticker["h"] / position["lowprice"] > stoplosspoint:
                    position["exitprice"] = position["lowprice"] * stoplosspoint
                    position["profit"] = position["size"] * (position["entryprice"] / position["exitprice"] - 1.0)
                    currentprofit = currentprofit + position["profit"]
                    if abs(position["profit"]) > exitprofit:
                        exitsymbol = position["symbol"]
                        entrydate = position["entrydate"]
                        entryprice = position["entryprice"]
                        exitprice = position["exitprice"]
                        exitprofit = abs(position["profit"])
                    position["exitdate"] = current_date
                    exitflag = True
                if symbolticker["l"] < position["lowprice"]:
                    position["lowprice"] = symbolticker["l"]
            position["exitprice"] = symbolticker["c"]
        else:
            if position["side"] == "buy":
                position["profit"] = position["size"] * (position["exitprice"] / position["entryprice"] - 1.0)
            else:
                position["profit"] = position["size"] * (position["entryprice"] / position["exitprice"] - 1.0)
            currentprofit = currentprofit + position["profit"]
            position["exitdate"] = current_date
            if abs(position["profit"]) > exitprofit:
                exitsymbol = position["symbol"]
                entrydate = position["entrydate"]
                entryprice = position["entryprice"]
                exitprice = position["exitprice"]
                exitprofit = abs(position["profit"])
            exitflag = True
    positions = [position for position in positions if position["exitdate"] != current_date]
    currentprofitrate = currentprofit / currentbalance
    currentbalance = currentbalance + currentprofit
    if currentbalance < 0:
        currentbalance = 0.0
    return positions, currentbalance, currentprofit, currentprofitrate, exitsymbol,  entrydate,  entryprice, exitprice, exitprofit 

def new_position(current_date, bestsymbol, side, atr, price, currentbalance, positionratio):
    position = {
        "symbol" : bestsymbol,
        "entrydate" : current_date,
        "exitdate" : current_date,
        "side": side,
        "size" : 0.0,
        "atr": atr,
        "entryprice":price,
        "balance":currentbalance,
        "highprice":price,
        "lowprice":price,
        "exitprice":price,
        "profit":0.0,
        }
    positionsize = currentbalance * 0.01 * positionratio / atr
    position["size"] = positionsize
    return position

def update_symbol_balance(symbol, trailingStop, positionratio):
    priceshistory = mydb.get_pricehistory(symbol)
    bestsymbol = symbol
    currentbalance = 1.0
    tradingcount = 0
    positions = []
    priceindex = -1
    for priceday in pricehistory:
        priceindex += 1
        if priceday["f"] is None or priceday["f"] == 0.5:
            continue
        score = (priceday["f"] * 2 - 1) * 100
        if score > 0:
            side = 'buy'
        else:
            side = 'sell'
        price =  priceday["c"]
        atr = priceday["atr"]
        result_item = { 
            "symbol": sql_result[0],
            "date": sql_result[1],
            "o": sql_result[2],
            "h": sql_result[3],
            "l": sql_result[4],
            "c": sql_result[5],
            "v": sql_result[6],
            "f": sql_result[7],
            "pricetime": sql_result[8],
            "predicttime": sql_result[9],
            "atr": sql_result[10],
                       }
        tickers = {
            symbol: priceday
            }
        current_date = priceday[date]
        positions, currentbalance, currentprofit, currentprofitrate, exitsymbol,  entrydate,  entryprice, exitprice, exitprofit = update_balance(positions, current_date, tickers, currentbalance, trailingStop)
        lastcloseprice = 0.0
        maxprice = 0.0
        minprice = 0.0
        tr = 0.0
        trsum = 0.0
        atrdaylist = pricehistory[priceindex-119 : priceindex+1]
        for atrdayitem in atrdaylist:
            if lastcloseprice == 0.0:
                lastcloseprice = atrdayitem["c"]
            maxprice = max(atrdayitem["h"], lastcloseprice)
            minprice = min(atrdayitem["l"], lastcloseprice)
            tr = maxprice / minprice - 1
            trsum = trsum + tr
            lastcloseprice = atrdayitem["c"]
        atr = trsum / 120.0
        mydb.set_atr_balance(bestsymbol, current_date, atr, currentbalance)
        if atr > 0.003 and price > 0:
            tradingcount = tradingcount + 1
            position = new_position(current_date, bestsymbol, side, atr, price, currentbalance, positionratio)
            positions.append(position)