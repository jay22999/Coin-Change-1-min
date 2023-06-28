import json
import ssl
from websocket import WebSocketApp
import rel
import requests
import math
import time

incpercentage = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]


def tbot(txt, coin):
    bot_mess = requests.get(
        "https://api.telegram.org/bot5611639078:AAHzCAzDdSKxGsGmpcrfKdctylf8wrtXYSA/getupdates")
    bot_mess = json.loads(bot_mess.content)

    if len(bot_mess["result"]) != 0:
        if bot_mess["result"][-1]["message"]["from"]["first_name"] == "j@y":
            bot_chatid = bot_mess["result"][-1]['message']['chat']['id']
            # new_txt = f"lp|{txt[0]} | {txt[1]} | {txt[2]} | {txt[4]} | {float(depth['asks'][0][0])} | {pr[10.0][0]} |  {pr[10.0][1]} | {txt[3]}"
            new_txt = f"{txt[0]} | {txt[1]} | {txt[2]} | {txt[4]} | {txt[3]}"
            send_text = f"https://api.telegram.org/bot5611639078:AAHzCAzDdSKxGsGmpcrfKdctylf8wrtXYSA/sendMessage?chat_id={bot_chatid}&text={new_txt}"
            print(new_txt, "new_txt")
            requests.post(send_text)

    else:
        print("PLZ SEND MESSEGE TO BOT")


coin_list = []
fut_pair = []
ex = []
fut_per_set = 1.3
minus_fut_per_set = -0.7
spot_per_set = 2
main_coin = ["ADAUSDT", "BTCUSDT", "ETHUSDT",
             "SOLUSDT", "MATICUSDT"]
main_coin_pr = 0.5
minus_main_coin_pr = -0.5

# retrive symbols from exchange
symbols = requests.get(
    "https://api.binance.com/api/v3/exchangeInfo")
symbols = symbols.json()
symbols = symbols["symbols"]

# retrive future pairs from exchange
future_pair = requests.get(
    "https://fapi.binance.com/fapi/v1/pmExchangeInfo")
future_pair = future_pair.json()
future_pair = future_pair["notionalLimits"]

# filter out required pairs from future and spot
for i in future_pair:
    if i["symbol"].endswith("USDT") and i["symbol"] != "BTTCUSDT" and i["symbol"] != "NBTUSDT":
        fut_pair.append(i["symbol"])

for i in symbols:
    if i["symbol"].endswith("USDT") and i["symbol"] != "BTTCUSDT" and i["symbol"] != "NBTUSDT":
        coin_list.append(f'{(i["symbol"]).lower()}@kline_1m')


def pair(coin_name, pr):
    if coin_name in fut_pair:
        y = ["Fut", pr, coin_name,
             f"https://www.binance.com/en/trade/{coin_name[:-4]}_{coin_name[-4:]}?layout=pro&theme=dark&type=spot", time.ctime(time.time())]
        return y
    else:
        y = [pr, time.ctime(time.time(
        )), coin_name, f"https://www.binance.com/en/trade/{coin_name[:-4]}_{coin_name[-4:]}?layout=pro&theme=dark&type=spot", "Spot"]
        return y


def on_messege(binancesocket, messege):
    json_messege = json.loads(messege)
    new_json_messege = json_messege["k"]
    o = float(new_json_messege["o"])
    c = float(new_json_messege["c"])
    h = float(new_json_messege["h"])
    v = float(new_json_messege["n"])
    e = json_messege["E"]
    kline = new_json_messege["x"]

    percentage = round((((c - o)*100)/c), 3)

    # on complition of kline conditions check and symbol pair name remove from ex

    if kline == True:
        if json_messege['s'] in ex:
            if json_messege['s'] not in fut_pair and percentage >= spot_per_set:
                ex.remove(json_messege['s'])

            elif json_messege['s'] in fut_pair and percentage >= fut_per_set:
                ex.remove(json_messege['s'])

            elif json_messege['s'] in main_coin and percentage >= main_coin_pr:
                ex.remove(json_messege['s'])

            elif json_messege['s'] in main_coin and percentage <= minus_main_coin_pr:
                ex.remove(json_messege['s'])

            elif json_messege['s'] in fut_pair and percentage <= minus_fut_per_set:
                ex.remove(json_messege['s'])

    else:
        # spot pair percentage filter
        y = pair(json_messege['s'], percentage)
        if json_messege['s'] not in ex:
            if json_messege['s'] not in fut_pair and percentage >= spot_per_set:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])

            # future pair percentage filter
            elif json_messege['s'] in fut_pair and percentage >= fut_per_set:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])

            elif json_messege['s'] in main_coin and percentage >= main_coin_pr:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])

            elif json_messege['s'] in main_coin and percentage <= minus_main_coin_pr:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])

            elif json_messege['s'] in fut_pair and percentage <= minus_fut_per_set:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])


def on_open(binancesocket):
    print("opened")
    length = math.ceil(len(coin_list)/28)
    for i in range(length):
        x = i*28
        y = (x+28)
        if y > len(coin_list):
            y = len(coin_list)

        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": coin_list[x:y],
            "id": 1
        }

        binancesocket.send(json.dumps(subscribe_message))
        time.sleep(1)


def startwebsocket():
    binancesocket = WebSocketApp(
        "wss://stream.binance.com:9443/ws", on_message=on_messege, on_close=on_close, on_error=on_error, on_open=on_open
    )

    binancesocket.run_forever(
        sslopt={"cert_reqs": ssl.CERT_NONE}, dispatcher=rel)
    rel.signal(2, rel.abort)
    rel.dispatch()


def on_close(binancesocket, close_status_code, close_msg):
    print("close")
    startwebsocket()


def on_error(binancesocket, error):
    print(error)


startwebsocket()
