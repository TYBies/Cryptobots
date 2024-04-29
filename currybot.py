import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from web3.gas_strategies.time_based import fast_gas_price_strategy
import time

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider('https://eth-sepolia.g.alchemy.com/v2/twYI0wmGMUKA1WM3pV9rw-CmwPpVK5wl'))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Adjust for Ethereum's PoA networks
web3.eth.set_gas_price_strategy(fast_gas_price_strategy)

# Set up accounts
private_key = '5347fc463069230c234ddbcd4dffa2b1324ec08af4472b15df34c7a27d831a8a'
account = Account.from_key(private_key)

# Define DEX contract addresses
uniswap_address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'#UNISWAP_TOKEN_CONTRACT_ADDRESS
sushiswap_address = '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2'#SUSHISWAP_TOKEN_CONTRACT_ADDRESS On Etherscan
abi ='0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24'#Uniswap ABI

# Function to execute trade on Uniswap
def uniswap_trade(token0, token1, amount_in):
    uniswap_contract = web3.eth.contract(address=uniswap_address, abi=abi)  # Replace UNISWAP_ABI with the ABI of Uniswap contract
    tx_hash = uniswap_contract.functions.swapExactTokensForTokens(
        amount_in,
        0,
        [token0, token1],
        account.address,
        int(time.time()) + 1000  # Set deadline to 1000 seconds from now
    ).buildTransaction({
        'chainId': 1,
        'gasPrice': web3.eth.generateGasPrice(),
        'nonce': web3.eth.getTransactionCount(account.address),
    })
    signed_tx = web3.eth.account.signTransaction(tx_hash, private_key)
    tx_receipt = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_receipt

# Function to execute trade on SushiSwap
def sushiswap_trade(token0, token1, amount_in):
    sushiswap_contract = web3.eth.contract(address=sushiswap_address, abi=abi)  # Replace SUSHISWAP_ABI with the ABI of SushiSwap contract
    tx_hash = sushiswap_contract.functions.swapExactTokensForTokens(
        amount_in,
        0,
        [token0, token1],
        account.address,
        int(time.time()) + 1000  # Set deadline to 1000 seconds from now
    ).buildTransaction({
        'chainId': 1,
        'gasPrice': web3.eth.generateGasPrice(),
        'nonce': web3.eth.getTransactionCount(account.address),
    })
    signed_tx = web3.eth.account.signTransaction(tx_hash, private_key)
    tx_receipt = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_receipt

# Main function to orchestrate the arbitrage process
def main():
    try:
        while True:
            # Fetch token prices from DEXs
            token_prices = get_token_prices()
            
            # Identify arbitrage opportunities
            arbitrage_opportunities = find_arbitrage_opportunities(token_prices)
            
            # Execute arbitrage trades
            for token0, token1 in arbitrage_opportunities:
                try:
                    print(f"Arbitrage opportunity detected for {token0}-{token1}. Execute trade...")
                    # Execute buy on DEX with lower price and sell on DEX with higher price
                    # Placeholder logic to determine which DEX has lower price
                    if token_prices[(token0, token1)][0] < token_prices[(token0, token1)][1]:
                        amount_to_trade = calculate_trade_amount(token_prices[(token0, token1)][0])  # Replace with your own logic
                        uniswap_trade(token0, token1, amount_to_trade)
                    else:
                        amount_to_trade = calculate_trade_amount(token_prices[(token0, token1)][1])  # Replace with your own logic
                        sushiswap_trade(token0, token1, amount_to_trade)
                    print("Trade executed successfully!")
                except Exception as e:
                    print(f"Error executing arbitrage trade: {e}")
            
            # Wait for some time before checking for arbitrage opportunities again
            time.sleep(60)  # Example: Check every 60 seconds
    except KeyboardInterrupt:
        print("Arbitrage bot terminated by user.")

# Function to fetch token prices from DEXs
        
def get_token_prices():
    dex_urls = 'https://api.geckoterminal.com/api/v2/networks/eth/dexes?page=1'
    token_prices = {}
    for dex, url in dex_urls.items():
        try:
            response = requests.post(url, json={'query': '{pairs(first: 10) {token0 {symbol} token1 {symbol} reserve0 reserve1}}'})
            data = response.json()
            for pair in data['data']['pairs']:
                token0_symbol = pair['token0']['symbol']
                token1_symbol = pair['token1']['symbol']
                reserve0 = float(pair['reserve0'])
                reserve1 = float(pair['reserve1'])
                token_prices[(token0_symbol, token1_symbol)] = (reserve0, reserve1)
        except Exception as e:
            print(f"Error fetching data from {dex}: {e}")
    return token_prices

# Function to identify arbitrage opportunities
def find_arbitrage_opportunities(token_prices):
    arbitrage_opportunities = []
    for (token0, token1), (reserve0, reserve1) in token_prices.items():
        # Placeholder logic for identifying arbitrage opportunities
        # Arbitrage opportunity exists if the price on one DEX is significantly higher than the other
        if reserve0 > 0 and reserve1 > 0:
            price_ratio = reserve0 / reserve1
            if price_ratio > 1.01:  # Example threshold for arbitrage opportunity (1% price difference)
                arbitrage_opportunities.append((token0, token1))
    return arbitrage_opportunities

# Placeholder function to calculate trade amount with slippage tolerance
def calculate_trade_amount(reserve, slippage_tolerance):
    return reserve * (1 - slippage_tolerance)

# Main function to orchestrate the arbitrage process
def main():
    slippage_tolerance = 0.02  # 2% slippage tolerance
    try:
        while True:
            # Fetch token prices from DEXs
            token_prices = get_token_prices()
            
            # Identify arbitrage opportunities
            arbitrage_opportunities = find_arbitrage_opportunities(token_prices)
            
            # Execute arbitrage trades
            for token0, token1 in arbitrage_opportunities:
                try:
                    print(f"Arbitrage opportunity detected for {token0}-{token1}. Execute trade...")
                    # Execute buy on DEX with lower price and sell on DEX with higher price
                    # Placeholder logic to determine which DEX has lower price
                    if token_prices[(token0, token1)][0] < token_prices[(token0, token1)][1]:
                        amount_to_trade = calculate_trade_amount(token_prices[(token0, token1)][0], slippage_tolerance)
                        uniswap_trade(token0, token1, amount_to_trade)
                    else:
                        amount_to_trade = calculate_trade_amount(token_prices[(token0, token1)][1], slippage_tolerance)
                        sushiswap_trade(token0, token1, amount_to_trade)
                    print("Trade executed successfully!")
                except Exception as e:
                    print(f"Error executing arbitrage trade: {e}")
            
            # Wait for some time before checking for arbitrage opportunities again
            time.sleep(60)  # Example: Check every 60 seconds
    except KeyboardInterrupt:
        print("Arbitrage bot terminated by user.")

