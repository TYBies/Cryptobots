import json
import requests
from datetime import datetime
import pandas as pd
import talib
import os
from dotenv import load_dotenv
import time
import ccxt

# Load environment variables from .env file
load_dotenv()

# Get API key and secret from environment variables
API_KEY = os.getenv('BASE_API_KEY')
API_SECRET = os.getenv('BASE_API_SECRET')


# Create an instance of the Coinbase exchange class
exchange = ccxt.coinbase({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True
})

def get_account_balance(symbol):
    try:
        balances = exchange.fetch_balance()
        for currency, balance in balances['total'].items():
            if currency==symbol:
             print(f"{currency}: {balance}")
        return balance

    except ccxt.ExchangeError as e:
        print('Exchange error while fetching account balance:', e)
    except ccxt.NetworkError as e:
        print('Network error while fetching account balance:', e)
    except Exception as e:
        print('Error while fetching account balance:', e)
    return None

def execute_trade(side, base_currency, quote_currency, quantity):
    try:
        print('#########',get_account_balance(quote_currency))
        # Get account balance for the quote currency
        balance  = get_account_balance(quote_currency)
        total_cost = quantity

        if side == "BUY":
            # Get the current market price for the trading pair
            ticker = exchange.fetch_ticker(f"{base_currency}/{quote_currency}")
            market_price = ticker['last']

            # Calculate the total cost of the trade
            total_cost = quantity * market_price

        # Check if the total cost exceeds the balance
        if total_cost > balance:
            print('quote_currency',quote_currency)
            print('totalCost->',total_cost,'Balance->',balance )
            print("Insufficient balance. Trade cannot be executed.")
            return

        # Proceed with the trade
        order = exchange.create_market_buy_order(
            symbol=f"{base_currency}/{quote_currency}",
            amount=quantity,  # Not needed for market buys
            price=None  # Specify the market price
        ) if side == "BUY" else exchange.create_market_sell_order(
            symbol=f"{base_currency}/{quote_currency}",
            amount=quantity,  # Not needed for market sells
            price=None  # Specify the market price
        )
        print(f"Trade executed successfully: {order}")
    except ccxt.NetworkError as e:
        print(f"Network error occurred: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error occurred: {e}")
    except Exception as e:
        print(f"Error occurred during trade execution: {e}")

def get_historical_data(symbol, days):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    data = response.json()
    return data['prices']

def parse_historical_data(data):
    parsed_data = []
    for timestamp, price in data:
        parsed_data.append({
            'timestamp': datetime.fromtimestamp(timestamp / 1000),
            'price': price
        })
    return parsed_data

def analyze_trades(trades, parsed_data):
    total_trades = len(trades)
    successful_trades = 0

    for trade in trades:
        trade_timestamp = trade['timestamp']
        trade_price = trade['price']

        # Find the index of the trade in the parsed data
        trade_index = next((i for i, item in enumerate(parsed_data) if item['timestamp'] == trade_timestamp and item['price'] == trade_price), None)

        if trade_index is not None and trade_index < len(parsed_data) - 1:
            closing_price = parsed_data[trade_index + 1]['price']
            if closing_price > trade_price:
                successful_trades += 1
                print(f"Trade Timestamp: {trade_timestamp}, Opening Price: {trade_price}, Closing Price: {closing_price}, Result: Successful")
            else:
                print(f"Trade Timestamp: {trade_timestamp}, Opening Price: {trade_price}, Closing Price: {closing_price}, Result: Unsuccessful")

    win_rate = (successful_trades / total_trades) * 100 if total_trades > 0 else 0
    print(f"Total Trades: {total_trades}")
    print(f"Successful Trades: {successful_trades}")
    print(f"Win Rate: {win_rate:.2f}%")


def generate_signals(parsed_data):
    df = pd.DataFrame(parsed_data)
    df.set_index('timestamp', inplace=True)

    # Calculate MACD
    macd, signal, _ = talib.MACD(df['price'], fastperiod=12, slowperiod=26, signalperiod=9)

    # Calculate RSI
    rsi = talib.RSI(df['price'], timeperiod=14)

    # Calculate Moving Averages
    short_ma = df['price'].rolling(window=20).mean()
    long_ma = df['price'].rolling(window=50).mean()

    # Generate signals based on strategies
    signals = []
    for i in range(len(df)):
        macd_signal = macd.iloc[i] - signal.iloc[i] > 0
        ma_crossover_signal = short_ma.iloc[i] > long_ma.iloc[i]
        rsi_signal = rsi.iloc[i] > 30 and rsi.iloc[i] < 70

        if macd_signal and ma_crossover_signal and rsi_signal:
            signals.append({
                'timestamp': df.index[i],
                'price': df['price'].iloc[i]
            })

    return signals

def sell_signal(price_data):
    # Suppose we want to sell if the price drops below a certain threshold
    sell_threshold = 0.95 * price_data[-1]['price']  # Sell if the current price is 5% lower than the last price
    if price_data[-1]['price'] < sell_threshold:
        return True
    return False

def main():
    while True:
        try:
            # Retrieve historical data for Bitcoin (BTC)
            btc_historical_data = get_historical_data('ethereum', 30)
            # Parse historical data
            parsed_btc_data = parse_historical_data(btc_historical_data)
            # Generate buy signals based on the integrated strategies
            buy_signals = generate_signals(parsed_btc_data)
            # Analyze trades
            analyze_trades(buy_signals, parsed_btc_data)#Analyse Trade is never used in the decision to buy or sell
            # Execute buy trade if conditions are met
            if len(buy_signals) > 0:
                for signal in buy_signals:
                    execute_trade("BUY", "ETH", "USDC", 0.0001)
                # Sleep for a short period to avoid excessive trading
                time.sleep(10)
            # Execute sell trade if conditions are met
            if sell_signal(parsed_btc_data):
                execute_trade("SELL", "ETH", "USDC", 0.0001)
                # Sleep for a short period to avoid excessive trading
                time.sleep(10)
            # Sleep for a short period to avoid excessive trading
            time.sleep(60)  # Adjust sleep time as needed
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print('Error in main loop:', e)

if __name__ == "__main__":
    main()
