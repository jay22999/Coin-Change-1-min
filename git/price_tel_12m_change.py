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
diffper = {
    "per": {

    },
    "val": {

    }


}

dp = diffper["per"]
dv = diffper["val"]
ex = []
fut_per_set = 1.3
spot_per_set = 2
main_coin = ["ADAUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "MATICUSDT", "CAKEUSDT"]
main_coin_pr = 0.5


symbols = requests.get(
    "https://api.binance.com/api/v3/exchangeInfo")
symbols = symbols.json()
symbols = symbols["symbols"]

future_pair = requests.get(
    "https://fapi.binance.com/fapi/v1/pmExchangeInfo")
future_pair = future_pair.json()
future_pair = future_pair["notionalLimits"]

for i in future_pair:
    if i["symbol"].endswith("USDT") and i["symbol"] != "BTTCUSDT" and i["symbol"] != "NBTUSDT":
        fut_pair.append(i["symbol"])

for i in symbols:
    if i["symbol"].endswith("USDT") and i["symbol"] != "BTTCUSDT" and i["symbol"] != "NBTUSDT":
        coin_list.append(f'{(i["symbol"]).lower()}@kline_1m')


def on_messege(binancesocket, messege):
    json_messege = json.loads(messege)
    new_json_messege = json_messege["k"]
    o = float(new_json_messege["o"])
    c = float(new_json_messege["c"])
    h = float(new_json_messege["h"])
    v = float(new_json_messege["n"])
    e = json_messege["E"]
    kline = new_json_messege["x"]

    a = int(str(e)[:10])
    percentage = round((((c - o)*100)/c), 3)
    # if json_messege['s'] == "BTCUSDT":
    #     if c > 16900 or c < 16700:
    #         y = [c, time.ctime(time.time(
    #             )), json_messege['s'], f"https://www.binance.com/en/trade/{json_messege['s'][:-4]}_{json_messege['s'][-4:]}?layout=pro&theme=dark&type=spot", "Spot"]
    #         tbot(y, json_messege['s'])
    if percentage >= fut_per_set:
        if json_messege['s'] in fut_pair:
            y = ["Fut", percentage, time.ctime(time.time(
            )), json_messege['s'], f"https://www.binance.com/en/trade/{json_messege['s'][:-4]}_{json_messege['s'][-4:]}?layout=pro&theme=dark&type=spot"]
        else:
            y = [percentage, time.ctime(time.time(
            )), json_messege['s'], f"https://www.binance.com/en/trade/{json_messege['s'][:-4]}_{json_messege['s'][-4:]}?layout=pro&theme=dark&type=spot", "Spot"]

        # tbot(y, json_messege['s'])

        if kline == True:
            if json_messege['s'] not in fut_pair and percentage >= spot_per_set and json_messege['s'] in ex:
                ex.remove(json_messege['s'])
                # print(ex, "in kline")
                tbot(y, json_messege['s'])
            elif json_messege['s'] in fut_pair and json_messege['s'] in ex:
                ex.remove(json_messege['s'])
                # print(ex, "in kline")
                tbot(y, json_messege['s'])

        else:
            if json_messege['s'] not in fut_pair and percentage >= spot_per_set and json_messege['s'] not in ex:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])
            elif json_messege['s'] in fut_pair and json_messege['s'] not in ex:
                ex.append(json_messege['s'])
                tbot(y, json_messege['s'])
    if percentage >= main_coin_pr or (percentage + (percentage*2)) >= main_coin_pr:
        for i in main_coin:
            if i == json_messege['s']:
                y = [percentage, time.ctime(time.time(
                    )), json_messege['s'], f"https://www.binance.com/en/trade/{json_messege['s'][:-4]}_{json_messege['s'][-4:]}?layout=pro&theme=dark&type=spot", "Spot"]
                tbot(y, json_messege['s'])


def on_error(binancesocket, error):
    print(error)


def on_close(binancesocket, close_status_code, close_msg):
    print("close")


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


binancesocket = WebSocketApp(
    "wss://stream.binance.com:9443/ws", on_message=on_messege, on_close=on_close, on_error=on_error, on_open=on_open
)

binancesocket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, dispatcher=rel)
rel.signal(2, rel.abort)
rel.dispatch()
