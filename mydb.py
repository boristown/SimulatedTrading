import mypsw
import mysql.connector
import math

def init_mycursor():
    myconnector = mysql.connector.connect(
      host=mypsw.host,
      user=mypsw.user,
      passwd=mypsw.passwd,
      database=mypsw.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor

def get_tags():
    tags = []
    myconnector, mycursor = init_mycursor()
    tags_statement = "SELECT distinct TAG FROM zeroai.tags"
    mycursor.execute(tags_statement)
    tags_results = mycursor.fetchall()
    for tag_result in tags_results:
        tags.append(str(tag_result[0]))
    return tags

def get_subtags(tagname, mycursor):
    subtags = []
    select_subtags_statment = "select * from subtags where tag = '" + tagname + "' and tag <> subtag"
    #print(select_subtags_statment)
    mycursor.execute(select_subtags_statment)
    subtags_results = mycursor.fetchall()
    for subtags_result in subtags_results:
        subtags.append(subtags_result[1])
    return subtags

def get_markets_from_endtags(endtags, mycursor):
    markets = []
    select_tags_statment = 'select * from tags where tag in (%s) ' % ','.join(['%s']*len(endtags))
    #print(select_tags_statment)
    mycursor.execute(select_tags_statment, endtags)
    tags_results = mycursor.fetchall()
    for tags_result in tags_results:
        markets.append(tags_result[1])
    return markets

def get_markets_from_tag(tagname, mycursor):
      nextsubtags = []
      endtags = []
      subtags = get_subtags(tagname, mycursor)
      if len(subtags) == 0:
          endtags.append(tagname)
      while len(subtags) > 0:
          for subtag in subtags:
              nextsubtag = get_subtags(subtag, mycursor)
              if len(nextsubtag) == 0:
                  endtags.append(subtag)
              else:
                  nextsubtags.extend(nextsubtag)
          subtags = nextsubtags
      markets = get_markets_from_endtags(endtags, mycursor)
      return markets

def get_symbols(tag):
    symbols = []
    myconnector, mycursor = init_mycursor()
    symbols = get_markets_from_tag(tag, mycursor)
    return symbols

def get_datelist(symbols):
    datelist = []
    myconnector, mycursor = init_mycursor()
    sql_statement = "SELECT distinct date FROM zeroai.pricehistory " \
        " where F <> 0.5 and  SYMBOL in (%s) order by date " % ','.join(['%s']*len(symbols))

    mycursor.execute(sql_statement, symbols)
    sql_results = mycursor.fetchall()
    for sql_result in sql_results:
        datelist.append(sql_result[0])
    return datelist

def get_atr(symbol, current_date):
    atr = 0.0
    myconnector, mycursor = init_mycursor()
    date_str = current_date.strftime("%Y-%m-%d")
    sql_statement = "select avg(TR) from ( SELECT h/l-1 as TR FROM zeroai.pricehistory " \
        " where DATE <= '" + date_str + "' and SYMBOL = '" + symbol + "' " \
        " order by DATE limit 120 ) TRS"
    mycursor.execute(sql_statement)
    sql_results = mycursor.fetchall()
    for sql_result in sql_results:
        atr = float(sql_result[0])
    return atr

def get_tickers(symbols, current_date):
    myconnector, mycursor = init_mycursor()
    bestsymbol = None
    score = 0.0
    side = 'buy'
    price = 0.0
    tickers = {}
    tickerlist = []
    date_str = current_date.strftime("%Y-%m-%d")
    sql_statement = "SELECT * FROM zeroai.pricehistory " \
        " where DATE = '" + date_str + "' and SYMBOL in (%s) " \
        " order by F " % ','.join(['%s']*len(symbols))
    mycursor.execute(sql_statement, symbols)
    sql_results = mycursor.fetchall()
    for sql_result in sql_results:
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
                       }
        tickerlist.append(result_item)
        tickers[sql_result[0]] = result_item

    if len(sql_result) >0:
        score1 = tickerlist[0]["f"] * 2 - 1
        score2 = tickerlist[-1]["f"] * 2 - 1
        if abs(score1) >= abs(score2):
            bestscore = score1
            bestrow = tickerlist[0]
        else:
            bestscore = score2
            bestrow = tickerlist[-1]
        bestsymbol = bestrow["symbol"]
        score = abs(bestscore) * 100
        if bestscore > 0:
            side = "buy"
        else:
            side = "sell"
        price = bestrow["c"]

    return bestsymbol, score, side, price, tickers

def write_trading_log(tag, aiversion, trailingStop, thresholdScore, leverage, datelist, balance, profit, profitrate, symboldict, atrdict, sizedict, scoredict, sidedict):
    myconnector, mycursor = init_mycursor()
    insert_val = []
    insert_sql = "INSERT INTO simulated (" \
            " TAG, DATE, AI, STOP, TSCORE, LEVERAGE,  BALANCE, PROFIT, PROFITRATE, SYMBOL, ATR, SIZE, SCORE, SIDE) VALUES (" \
            " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
            " ON DUPLICATE KEY UPDATE " \
            " BALANCE = VALUES(BALANCE), " \
            " PROFIT = VALUES(PROFIT), " \
            " PROFITRATE = VALUES(PROFITRATE), " \
            " SYMBOL = VALUES(SYMBOL), " \
            " ATR = VALUES(ATR), " \
            " SIZE = VALUES(SIZE), " \
            " SCORE = VALUES(SCORE), " \
            " SIDE = VALUES(SIDE) "

    for current_date in datelist:
        insert_val.append((
            tag, 
            current_date, 
            aiversion, 
            trailingStop, 
            thresholdScore,
            leverage,
            balance[current_date],
            profit[current_date],
            profitrate[current_date],
            symboldict[current_date],
            atrdict[current_date],
            sizedict[current_date],
            scoredict[current_date],
            sidedict[current_date]
            ))
    mycursor.executemany(insert_sql, insert_val)
    mydb.commit()    # 数据表内容有更新，必须使用到该语句
    print(mycursor.rowcount, 'TAG:"' + tag + '"更新成功。')
