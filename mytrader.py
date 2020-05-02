def update_balance(positions, current_date, tickers, currentbalance):
    currentprofit = 0.0
    currentprofitrate = 0.0

    return positions, currentbalance, currentprofit, currentprofitrate

def new_position(current_date, bestsymbol, side, atr, price, balance):
    position = {"size" : 0.0}
    return position