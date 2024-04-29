import ccxt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key and secret from environment variables
API_KEY = os.getenv('BASE_API_KEY')
API_SECRET = os.getenv('BASE_API_SECRET')
try:
    # Create an instance of the Coinbase exchange class
    exchange = ccxt.coinbase({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True  
    })
  
    # Example: Fetch account information
    accounts = exchange.fetch_accounts()

    # Print account information
    for account in accounts:
        print(account)

except ccxt.NetworkError as e:
    print('Network error:', e)
except ccxt.ExchangeError as e:
    print('Exchange error:', e)
except Exception as e:
    print('Error:', e)
