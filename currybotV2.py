import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from web3.gas_strategies.time_based import fast_gas_price_strategy
import time
import json

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider('https://eth-sepolia.g.alchemy.com/v2/twYI0wmGMUKA1WM3pV9rw-CmwPpVK5wl'))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Adjust for Ethereum's PoA networks
web3.eth.set_gas_price_strategy(fast_gas_price_strategy)

# Set up accounts
private_key = ''
account = Account.from_key(private_key)

# Define DEX contract addresses
uniswap_address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'  # UNISWAP_TOKEN_CONTRACT_ADDRESS
sushiswap_address = '0x6B3595068778DD592e39A122f4f5a5cF09C90fE2'  # SUSHISWAP_TOKEN_CONTRACT_ADDRESS On Etherscan
abi = '0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24'  # Uniswap ABI

# Function to execute trade on Uniswap
def uniswap_trade(token0, token1, amount_in):
    try:
        uniswap_contract = web3.eth.contract(address=uniswap_address, abi=abi)  
        tx_hash = uniswap_contract.functions.swapExactTokensForTokens(
            amount_in,
            0,
            [token0, token1],
            account.address,
            int(time.time()) + 1000  
        ).buildTransaction({
            'chainId': 1,
            'gasPrice': web3.eth.generateGasPrice(),
            'nonce': web3.eth.getTransactionCount(account.address),
        })
        signed_tx = web3.eth.account.signTransaction(tx_hash, private_key)
        tx_receipt = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_receipt
    except Exception as e:
        print(f"Error executing Uniswap trade: {e}")

# Function to execute trade on SushiSwap
def sushiswap_trade(token0, token1, amount_in):
    try:
        sushiswap_contract = web3.eth.contract(address=sushiswap_address, abi=abi)  
        tx_hash = sushiswap_contract.functions.swapExactTokensForTokens(
            amount_in,
            0,
            [token0, token1],
            account.address,
            int(time.time()) + 1000  
        ).buildTransaction({
            'chainId': 1,
            'gasPrice': web3.eth.generateGasPrice(),
            'nonce': web3.eth.getTransactionCount(account.address),
        })
        signed_tx = web3.eth.account.signTransaction(tx_hash, private_key)
        tx_receipt = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_receipt
    except Exception as e:
        print(f"Error executing SushiSwap trade: {e}")

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



def get_token_prices():
    dex_registry_url = 'https://api.geckoterminal.com/api/v2/networks/eth/dexes?page=1'
    try:
        response = requests.get(dex_registry_url)
        response.raise_for_status()  # Check for any HTTP errors
        dex_data = response.json()
        formatted_data = json.dumps(dex_data, indent=4)
        print(formatted_data)        
        
        #print("DEX Data:", dex_data)  # Debug print statement
        
        # Extract pairs URL for each DEX
        dex_urls = {}
        for dex in formatted_data.get('data', []):
            dex_name = dex['attributes'].get('name')
            pairs_url = dex.get('attributes', {}).get('pairsUrl')
            if dex_name and pairs_url:
                dex_urls[dex_name] = pairs_url
        
        print("DEX URLs===>", dex_urls)  # Debug print statement
        
        # Fetch token prices from each DEX
        token_prices = {}
        for dex, url in dex_urls.items():
            response = requests.get(url)
            response.raise_for_status()  # Check for any HTTP errors
            data = response.json()
            for pair in data.get('data', {}).get('pairs', []):
                token0_symbol = pair['token0']['symbol']
                token1_symbol = pair['token1']['symbol']
                reserve0 = float(pair['reserve0'])
                reserve1 = float(pair['reserve1'])
                token_prices[(token0_symbol, token1_symbol)] = (reserve0, reserve1)
        
        return token_prices
    except Exception as e:
        print(f"Error fetching token prices: {e}")
        return {}

# Example usage
token_prices = get_token_prices()
print("Token prices:====>", token_prices)


# Function to identify arbitrage opportunities
def find_arbitrage_opportunities(token_prices):
    arbitrage_opportunities = []
    for (token0, token1), (reserve0, reserve1) in token_prices.items():
        if reserve0 > 0 and reserve1 > 0:
            price_ratio = reserve0 / reserve1
            if price_ratio > 1.01:  # Example threshold for arbitrage opportunity (1% price difference)
                arbitrage_opportunities.append((token0, token1))
    return arbitrage_opportunities

# Placeholder function to calculate trade amount with slippage tolerance
def calculate_trade_amount(reserve, slippage_tolerance):
    return reserve * (1 - slippage_tolerance)

# Start the main function
if __name__ == "__main__":
    main()