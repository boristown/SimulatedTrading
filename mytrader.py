def update_balance(positions, current_date, tickers, currentbalance, trailingStop):
    currentprofit = 0.0
    currentprofitrate = 0.0
    exitflag = False
    for position in positions:
        stoplosspoint = trailingStop * position["atr"] + 1
        symbolticker = tickers[position["symbol"]]
        if position["side"] == "buy":
            if position["highprice"] / symbolticker["l"]  > stoplosspoint:
                position["exitprice"] = position["highprice"] / stoplosspoint
                position["profit"] = position["size"] * (position["exitprice"] / position["entryprice"] - 1.0)
                currentprofit = currentprofit + position["profit"]
                position["exitdate"] = current_date
                exitflag = True
            if symbolticker["h"] > position["highprice"]:
                position["highprice"] = symbolticker["h"]
        else:
            if  symbolticker["h"] / position["lowprice"] > stoplosspoint:
                position["exitprice"] = position["lowprice"] * stoplosspoint
                position["profit"] = position["size"] * (position["entryprice"] / position["exitprice"] - 1.0)
                currentprofit = currentprofit + position["profit"]
                position["exitdate"] = current_date
                exitflag = True
            if symbolticker["l"] < position["lowprice"]:
                position["lowprice"] = symbolticker["l"]
    positions = [position for position in positions if position["exitdate"] != current_date]
    currentprofitrate = currentprofit / currentbalance
    currentbalance = currentbalance + currentprofit
    return positions, currentbalance, currentprofit, currentprofitrate

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
