from websocket import create_connection
import json
from bs4 import BeautifulSoup
import winsound
from datetime import datetime
from avanza import Avanza, TimePeriod, InstrumentType, OrderType
from datetime import date
import telegram

api_key = ''
user_id = ''


bot = telegram.Bot(token=api_key)


frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
money = 500  # the amount of capital in SEK

today = datetime.today().strftime('%Y-%m-%d')
datum = date.fromisoformat(today)
list_ = ['order', 'Order', 'Avtal', 'avtal', 'ökar',
         'Ökar', 'beställning', 'Beställning', 'ORDER', 'AVTAL']

avanza = Avanza({
    'username': '',
    'password': '',
    'totpSecret': ''
})

# Copy the web brower header and input as a dictionary
headers = json.dumps({
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,sv;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'Upgrade',
    'Cookie': 'preview-split-size=45; _ga=GA1.2.70482285.1609364074; cookiebanner=off; __cfduid=dfab35becb51b3157bde1510cd36570471613581109; main-filter=(and(or(.properties.lang%3D%22sv%22))(or(a.list_id%3D35207)(a.list_id%3D35208)(a.list_id%3D35209)(a.list_id%3D919325)(a.list_id%3D35198)(a.list_id%3D29934)(a.list_id%3D4680265))); _66f23=http://10.60.2.152:8080; _gid=GA1.2.973761670.1614000961',
    'Host': 'mfn.se',
    'Origin': 'https://mfn.se',
    'Pragma': 'no-cache',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    'Sec-WebSocket-Key': 'UgkFXKCmIF/+6ebeKZdBtg==',
    'Sec-WebSocket-Version': '13',
    'Upgrade': 'websocket',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
})


def newsHandler():
    global start_time
    result = ws.recv()
    start_time = datetime.now()
    print("start: ", start_time)
    parsed_html = BeautifulSoup(result, 'html.parser')
    lista = parsed_html.get_text().splitlines()
    print(lista)
    lista = list(filter(None, lista))
    tid = lista[1]
    #newTime  = now - time3
    #newTime = newTime.total_seconds()
    return lista[2], lista[3]


def reader(ws):
    # Launch the connection to the server.
    # Printing all the result
    while True:
        try:
            newsStock, theNews = newsHandler()

            info = getStockInfo(newsStock)

            lastPrice = info['lastPrice']
            idet = info['id']
            amount = int(money/lastPrice)
            previousComp = ''
            lst = str(lastPrice).split('.')
            längd = len(lst[1])
            orderPrice = lastPrice + (lastPrice*10/100)
            price = round(orderPrice, längd-1)

            if(previousComp != newsStock):
                previousComp = newsStock
                if any(word in theNews for word in list_):
                    ordern = avanza.place_order(
                        '7802139', idet, OrderType.BUY, price, datum, amount)

                    print("before beep: ",
                          datetime.now()-start_time)
                    bot.send_message(chat_id=user_id, text=newsStock)
                    bot.send_message(chat_id=user_id, text=price)
                    bot.send_message(chat_id=user_id, text=theNews)

                    print(ordern)

                    print("price: ", price)

                    stockOptions(newsStock)
                    winsound.Beep(frequency, 100)
                    print(datetime.now())

            print(newsStock)
            print("time for execution: ",
                  datetime.now()-start_time)
            print("order priset: ", price)

            print(theNews)

        except Exception as e:
            print(e)
            break


def getStockInfo(stockName):
    stocken = avanza.search_for_stock(stockName)
    info = stocken['hits'][0]['topHits'][0]
    return info


def printTime():
    print(datetime.now())


def stockOptions(newsStock):
    optionInfo = avanza.search_for_instrument(
        InstrumentType.SUBSCRIPTION_OPTION, newsStock)
    if optionInfo['totalNumberOfHits'] > 0:
        optioner = []
        for option in optionInfo['hits'][0]['topHits']:
            optioner.append(option['tickerSymbol'])

        bot.send_message(chat_id=user_id, text=optioner)


if __name__ == "__main__":
    print(avanza)
    bot.send_message(chat_id=user_id, text="Bot started")

    while True:
        ws = create_connection(
            'wss://mfn.se/all/s?filter=(and(or(.properties.lang%3D%22sv%22))(or(a.list_id%3D35207)(a.list_id%3D35208)(a.list_id%3D35209)(a.list_id%3D919325)))', headers=headers)
        print("hej1")
        reader(ws)
