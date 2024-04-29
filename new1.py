import requests
from datetime import datetime
import pandas as pd
import talib
import os
import time 
from dotenv import load_dotenv
import ccxt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Load API credentials from .env file
load_dotenv()
exchange_id = 'coinbase'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': os.getenv('BASE_API_KEY'),
    'secret': os.getenv('BASE_API_SECRET'),
})
BASE_API_KEY = os.getenv('BASE_API_KEY')
BASE_API_SECRET = os.getenv('BASE_API_SECRET')

# Initialize Coinbase client
client = exchange

def get_historical_data(symbol, days):
    url = f"https://api.coinbase.com/api/v2/prices/{symbol}-USD/historic"
    response = requests.get(url)
    data = response.json()
    return data

def parse_historical_data(data):
    print(data)
    parsed_data = []
    for timestamp, price in data:
        parsed_data.append({
            'timestamp': datetime.fromtimestamp(timestamp / 1000),
            'price': price
        })
    return parsed_data

def generate_signals(parsed_data):
    buy_signal = []
    sell_signal = []
    df = pd.DataFrame(parsed_data)
    df.set_index('timestamp', inplace=True)

    # Calculate MACD
    macd, signal, _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

    # Calculate RSI
    rsi = talib.RSI(df['close'], timeperiod=14)

    # Calculate Bollinger Bands
    bbands = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)

    # Generate signals based on strategies   
    for i in range(len(df)):
        macd_signal = macd[i] - signal[i] > 0
        rsi_signal = rsi[i] > 30 and rsi[i] < 70
        bbands_signal = bbands[i] > 2 * df['close'][i]

        if macd_signal and rsi_signal and bbands_signal:
            signals.append({
                'timestamp': df.index[i],
                'price': df['close'][i]
            })

    return signals

def execute_trade(side, quantity):
    try:
        trades = client.get_my_trades(symbol='BTCUSDT')

        print(trades)

        order = client.create_order(
            symbol='BTCUSDT',
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(f"Trade executed successfully: {order}")
    except Exception as e:
        print(f"Trade execution failed: {e}")

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

def train_model(data):
    X = []
    y = []
    for i in range(len(data) - 1):
        X.append([data[i]['close'], data[i]['high'], data[i]['low'], data[i]['volume']])
        y.append(data[i+1]['close'])
    X = np.array(X)
    y = np.array(y)
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model accuracy: {model.score(X_test, y_test):.2f}%")

def main():
    while True:
        try:
            # Retrieve historical data for Bitcoin (BTC)
            btc_historical_data = get_historical_data('bitcoin', 30)
            # Parse historical data
            parsed_btc_data = parse_historical_data(btc_historical_data)
            # Generate buy signals based on the integrated strategies
            buy_signals = generate_signals(parsed_btc_data)
            # Analyze trades
            analyze_trades(buy_signals, parsed_btc_data)#Analyse Trade is never used in the decision to buy or sell
            # Execute buy trade if conditions are met
            if len(buy_signals) > 0:
                for signal in buy_signals:
                    execute_trade("BUY", "BTC", "USDC", 0.0001)
                # Sleep for a short period to avoid excessive trading
                time.sleep(10)
            # Execute sell trade if conditions are met
            if sell_signal(parsed_btc_data):
                execute_trade("SELL", "BTC", "USDC", 0.0001)
                # Sleep for a short period to avoid excessive trading
                time.sleep(10)
            # Sleep for a short period to avoid excessive trading
            time.sleep(60)  # Adjust sleep time as needed
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print('Error in main loop:', e)

    # Train model
    train_model(parsed_data)

if __name__ == "__main__":
    main()
   # train_model(parsed_data)