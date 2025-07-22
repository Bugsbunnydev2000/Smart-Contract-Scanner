import requests
import os
from dotenv import load_dotenv
from web3 import Web3
from slither import Slither
from slither.exceptions import SlitherError

load_dotenv()

API_KEYS = {
    "eth": os.getenv("ETHERSCAN_API_KEY"),
    "bsc": os.getenv("BSCSCAN_API_KEY"),
    "polygon": os.getenv("POLYGONSCAN_API_KEY"),
}

API_ENDPOINTS = {
    "eth": "https://api.etherscan.io/api",
    "bsc": "https://api.bscscan.com/api",
    "polygon": "https://api.polygonscan.com/api",
}

RPC_ENDPOINTS = {
    "eth": "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",  # Replace with your Infura key
    "bsc": "https://bsc-dataseed.binance.org/",
    "polygon": "https://polygon-rpc.com/",
}

def get_api_url(chain, address):
    if chain not in API_ENDPOINTS:
        raise ValueError(f"Unsupported chain: {chain}")
    return f"{API_ENDPOINTS[chain]}?module=contract&action=getsourcecode&address={address}&apikey={API_KEYS[chain]}"

def get_bytecode(chain, address):
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINTS[chain]))
        if not w3.is_connected():
            return None, f"❌ Failed to connect to {chain} RPC"
        bytecode = w3.eth.get_code(address).hex()
        return bytecode, None
    except Exception as e:
        return None, f"❌ Error fetching bytecode: {str(e)}"

def fetch_contract_source(chain, address):
    try:
        url = get_api_url(chain, address)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "1":
            error = f"❌ Error fetching contract: {data.get('result', 'Unknown error')}"
            # Fallback to bytecode analysis
            bytecode, bytecode_error = get_bytecode(chain, address)
            if bytecode_error:
                return None, error + f"\n{bytecode_error}"
            return {"source_code": None, "bytecode": bytecode}, error

        source_code = data["result"][0]["SourceCode"]
        if not source_code:
            error = "⚠️ Contract is not verified or source code not available."
            bytecode, bytecode_error = get_bytecode(chain, address)
            if bytecode_error:
                return None, error + f"\n{bytecode_error}"
            return {"source_code": None, "bytecode": bytecode}, error

        # Fetch implementation contract for proxies
        implementation = data["result"][0].get("Proxy") == "1" and data["result"][0].get("Implementation")
        implementation_code = None
        if implementation:
            impl_data, impl_error = fetch_contract_source(chain, implementation)
            if impl_data:
                implementation_code = impl_data["source_code"]

        return {"source_code": source_code, "implementation_code": implementation_code, "bytecode": None}, None
    except requests.RequestException as e:
        bytecode, bytecode_error = get_bytecode(chain, address)
        if bytecode_error:
            return None, f"❌ Network error: {str(e)}\n{bytecode_error}"
        return {"source_code": None, "bytecode": bytecode}, f"❌ Network error: {str(e)}"
    
def save_contract_to_file(chain, address, source_data, output_dir="contracts"):
    os.makedirs(output_dir, exist_ok=True)
    contract_file = os.path.join(output_dir, f"{chain}_{address}.sol")
    
    with open(contract_file, "w", encoding="utf-8") as f:
        if source_data["source_code"]:
            f.write("// Proxy Contract Source Code\n")
            f.write(source_data["source_code"] + "\n\n")
        if source_data.get("implementation_code"):
            f.write("// Implementation Contract Source Code\n")
            f.write(source_data["implementation_code"] + "\n")
        if not source_data["source_code"] and not source_data.get("implementation_code"):
            f.write("// No source code available\n")
            if source_data["bytecode"]:
                f.write(f"// Bytecode: {source_data['bytecode']}\n")
    
    print(f"📝 Contract saved to: {contract_file}")
    return contract_file