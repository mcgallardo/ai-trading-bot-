import os
import time
import krakenex
from pykrakenapi import KrakenAPI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

api = krakenex.API(API_KEY, API_SECRET)
k = KrakenAPI(api)

# CONFIGURATION
PAIR = 'ETHUSD'
USD_TO_TRADE = 5.00
PROFIT_THRESHOLD = 1.01  # Sell when price goes up 1%
print("Bot started.")
print(f"Pair: {PAIR}")
print(f"USD to trade: {USD_TO_TRADE}")
print(f"Profit threshold: {PROFIT_THRESHOLD}")

# TRACKING
last_buy_price = None

def get_current_price():
    try:
        ticker = api.query_public('Ticker', {'pair': PAIR})
        price = float(ticker['result'][list(ticker['result'].keys())[0]]['c'][0])
        print(f"Current market price: {price}")
        return price
    except Exception as e:
        print("Price fetch error:", e)
        return None

def buy_eth():
    price = get_current_price()
    if price:
        volume = round(USD_TO_TRADE / price, 6)
        print(f"Buying {volume} ETH at ${price}")
        response = api.query_private('AddOrder', {
            'pair': PAIR,
            'type': 'buy',
            'ordertype': 'market',
            'volume': volume
        })
        print("Buy response:", response)
        return price
    return None

def sell_eth():
    balance = k.get_account_balance()
    eth = float(balance.get('XETH', 0))
    if eth > 0.0001:
        print(f"Selling {eth} ETH")
        response = api.query_private('AddOrder', {
            'pair': PAIR,
            'type': 'sell',
            'ordertype': 'market',
            'volume': round(eth, 6)
        })
        print("Sell response:", response)

def run_bot():
    global last_buy_price
    while True:
        try:
            current_price = get_current_price()
            print(f"Current ETH price: ${current_price}")

            if last_buy_price is None:
                last_buy_price = buy_eth()
            elif current_price and current_price >= last_buy_price * PROFIT_THRESHOLD:
                sell_eth()
                last_buy_price = None

        except Exception as e:
            print("Bot error:", e)

        time.sleep(30)

if __name__ == "__main__":
    print("AI Trading Bot started...")
    run_bot()
