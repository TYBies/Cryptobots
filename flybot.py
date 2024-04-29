import requests
from datetime import datetime
import pandas as pd
import talib
import os
from dotenv import load_dotenv
from binance.client import Client
import time

# Load API credentials from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Initialize Binance client
client = Client(API_KEY, API_SECRET)

# Define functions to interact with Binance API...


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
        macd_signal = macd[i] - signal[i] > 0
        ma_crossover_signal = short_ma[i] > long_ma[i]
        rsi_signal = rsi[i] > 30 and rsi[i] < 70
        
        if macd_signal and ma_crossover_signal and rsi_signal:
            signals.append({
                'timestamp': df.index[i],
                'price': df['price'][i]
            })
    
    return signals

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


# Define the backtesting period (e.g., 6 months)
backtesting_period_days = 30

# Retrieve historical data for Bitcoin (BTC) for the backtesting period
btc_historical_data = get_historical_data('ethereum', backtesting_period_days)

# Parse historical data
parsed_btc_data = parse_historical_data(btc_historical_data)

# Generate buy signals based on the integrated strategies
buy_signals = generate_signals(parsed_btc_data)

# Analyze trades
analyze_trades(buy_signals, parsed_btc_data)
