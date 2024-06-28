import pandas as pd
from moralis import evm_api
from collections import defaultdict

# Initialize your Moralis API key
api_key = "YOUR_API_KEY"

# Load the CSV file
df = pd.read_csv('C:/Users/elnag/Documents/BAM/FinTech/All_Active_Farcaster_Users.csv')

# Filter accounts with at least 3000 followers
df = df[df['followers'] >= 3000]

def get_valid_addresses(addresses):
    """Extract all valid addresses from a pipe-separated string."""
    return [addr.strip() for addr in addresses.split('|') if addr.startswith('0x') and len(addr) == 42]

# Prepare to collect results
results = []

# Iterate through the DataFrame
for index, row in df.iterrows():
    addresses = get_valid_addresses(row['addresses'])
    aggregate_tokens = defaultdict(float)  # Dictionary to sum usd_values by token

    for address in addresses:
        params = {
            "chain": "base",  # Use the correct chain identifier
            "address": address
        }
        try:
            # Fetch token balances for each address
            result = evm_api.wallets.get_wallet_token_balances_price(api_key=api_key, params=params)
            # Aggregate token values across all addresses
            for token in result['result']:
                if token['usd_value'] is not None:
                    aggregate_tokens[(token['symbol'], token['token_address'])] += token['usd_value']
        except Exception as e:
            print(f"Failed to fetch data for address {address}: {e}")

    # Sort tokens by aggregated USD value and pick the top 10
    sorted_tokens = sorted(aggregate_tokens.items(), key=lambda item: -item[1])[:10]
    token_data = {}
    for i, ((symbol, address), usd_value) in enumerate(sorted_tokens, 1):
        token_data[f'token_{i}_symbol'] = symbol
        token_data[f'token_{i}_address'] = address
        token_data[f'token_{i}_usd_value'] = usd_value

    # Append the row with new token data
    results.append({
        'fid': row['fid'],
        'fname': row['fname'],
        **token_data
    })

# Convert results to a DataFrame for further analysis or saving
results_df = pd.DataFrame(results)
print(results_df.head())

# Save or further process your results as needed
results_df.to_csv('aggregated_token_balances_v2.csv', index=False)
