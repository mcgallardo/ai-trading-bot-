import os
import time
import krakenex
from pykrakenapi import KrakenAPI
from dotenv import load_dotenv

# Load environment variables (KRAKEN_API_KEY and KRAKEN_API_SECRET)
load_dotenv()
API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Set up Kraken API
api = krakenex.API(API_KEY, API_SECRET)
k = KrakenAPI(api)

# Config
PAIR = 'ETHUSD'
USD_TO_TRADE = 15.00
PROFIT_THRESHOLD = 1.01  # 1% gain triggers sell

# State tracking
last_buy_price = None

def get_current_price():
    try:
        ticker = api.query_public('Ticker', {'pair': PAIR})
        price = float(ticker['result'][list(ticker['result'].keys())[0]]['c'][0])
        print(f"[PRICE] Current ETH price: ${price}")
        return price
    except Exception as e:
        print("[ERROR] Failed to fetch price:", e)
        return None

def buy_eth(current_price):
    global last_buy_price
    volume = round(USD_TO_TRADE / current_price, 6)
    try:
        print(f"[ACTION] Buying {volume} ETH at ${current_price}")
        response = k.add_standard_order(
            pair=PAIR,
            type='buy',
            ordertype='market',
            volume=str(volume)
        )
        print("[SUCCESS] Buy order placed:", response)
        last_buy_price = current_price
    except Exception as e:
        print("[ERROR] Buy failed:", e)

def sell_eth(current_price):
    global last_buy_price
    try:
        balance = k.get_account_balance()
        eth_balance = float(balance.get('XETH', 0))
        if eth_balance > 0.0001:
            print(f"[ACTION] Selling {eth_balance} ETH at ${current_price}")
            response = k.add_standard_order(
                pair=PAIR,
                type='sell',
                ordertype='market',
                volume=str(round(eth_balance, 6))
            )
            print("[SUCCESS] Sell order placed:", response)
            last_buy_price = None
        else:
            print("[INFO] No ETH available to sell.")
    except Exception as e:
        print("[ERROR] Sell failed:", e)

def run_bot():
    global last_buy_price
    print("[BOT] Starting ETH flip strategy bot...")
    print(f"[CONFIG] Trade Pair: {PAIR} | USD to Trade: ${USD_TO_TRADE} | Profit Target: {int((PROFIT_THRESHOLD - 1) * 100)}%")

    while True:
        try:
            current_price = get_current_price()
            if current_price:
                if last_buy_price is None:
                    buy_eth(current_price)
                elif current_price >= last_buy_price * PROFIT_THRESHOLD:
                    sell_eth(current_price)
                else:
                    print(f"[WAIT] Holding. Current: ${current_price}, Target: ${round(last_buy_price * PROFIT_THRESHOLD, 2)}")
            else:
                print("[INFO] Price not available. Skipping this cycle.")

        except Exception as e:
            print("[ERROR] Bot exception:", e)

        time.sleep(30)

if __name__ == "__main__":
    run_bot()
