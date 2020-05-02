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
        " where SYMBOL in (%s) order by date " % ','.join(['%s']*len(symbols))

    mycursor.execute(sql_statement, symbols)
    sql_results = mycursor.fetchall()
    for sql_result in sql_results:
        datelist.append(sql_result[0])
    return datelist

def get_tickers(symbols, current_date):
    bestsymbol = None
    score = 0.0
    side = 'buy'
    atr = 0.0
    price = 0.0
    tickers = {}
    tickerlist = []
    date_str = current_date.strftime("%Y-%m-%d")
    sql_statement = "SELECT * FROM zeroai.pricehistory " \
        " where DATE = '" + date_str + "' and SYMBOL in (%s) " \
        " order by F " % ','.join(['%s']*len(markets))
    mycursor.execute(sql_statement, markets)
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
        if math.abs(score1) >= math.abs(score2):
            bestscore = score1
            bestrow = tickerlist[0]
        else:
            bestscore = score2
            bestrow = tickerlist[-1]
        bestsymbol = bestrow["symbol"]
        score = math.abs(bestscore) * 100
        if bestscore > 0:
            side = "buy"
        else:
            side = "sell"
        price = bestrow["c"]

    return bestsymbol, score, side, atr, price, tickers

def write_trading_log(tag, aiversion, trailingStop, thresholdScore, balance, profit, profitrate, symboldict, atrdict, sizedict):

    return
