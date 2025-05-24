import os
import time
import krakenex
from pykrakenapi import KrakenAPI
from dotenv import load_dotenv

# Load environment variables (used for local development)
load_dotenv()

# Get secrets from environment
API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Initialize Kraken API
api = krakenex.API(API_KEY, API_SECRET)
k = KrakenAPI(api)

# Config from environment or defaults
PAIR = os.getenv("trading_pair", "ETHUSD")
USD_TO_TRADE = float(os.getenv("TRADE_AMOUNT", 5))
PROFIT_THRESHOLD = float(os.getenv("PROFIT_THRESHOLD", 1.01))  # Default to 1% gain

# Track state
last_buy_price = None

def get_current_price():
    try:
        ticker = api.query_public('Ticker', {'pair': PAIR})
        price = float(ticker['result'][list(ticker['result'].keys())[0]]['c'][0])
        print(f"[PRICE] Current price for {PAIR}: ${price}")
        return price
    except Exception as e:
        print("[ERROR] Failed to fetch price:", e)
        return None

def buy_eth(current_price):
    global last_buy_price
    volume = round(USD_TO_TRADE / current_price, 6)
    try:
        print(f"[ACTION] Buying {volume} {PAIR[:3]} at ${current_price}")
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
        asset_code = 'XETH' if 'ETH' in PAIR else 'XXBT'  # adapt based on pair
        crypto_balance = float(balance.get(asset_code, 0))
        if crypto_balance > 0.0001:
            print(f"[ACTION] Selling {crypto_balance} at ${current_price}")
            response = k.add_standard_order(
                pair=PAIR,
                type='sell',
                ordertype='market',
                volume=str(round(crypto_balance, 6))
            )
            print("[SUCCESS] Sell order placed:", response)
            last_buy_price = None
        else:
            print("[INFO] Not enough crypto to sell.")
    except Exception as e:
        print("[ERROR] Sell failed:", e)

def run_bot():
    global last_buy_price
    print("[BOT] Starting strategy...")
    print(f"[CONFIG] Pair: {PAIR} | Amount: ${USD_TO_TRADE} | Threshold: {PROFIT_THRESHOLD * 100 - 100:.2f}%")

    while True:
        try:
            current_price = get_current_price()
            if current_price:
                if last_buy_price is None:
                    buy_eth(current_price)
                elif current_price >= last_buy_price * PROFIT_THRESHOLD:
                    sell_eth(current_price)
                else:
                    print(f"[WAIT] Holding. Current: ${current_price:.2f}, Target: ${last_buy_price * PROFIT_THRESHOLD:.2f}")
            else:
                print("[INFO] No price. Skipping...")

        except Exception as e:
            print("[ERROR] Bot exception:", e)

        time.sleep(30)

if __name__ == "__main__":
    run_bot()
