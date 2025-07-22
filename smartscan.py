from contract_fetcher import fetch_contract_source, save_contract_to_file
from gemini_analyzer import analyze_solidity_code, save_report
from colorama import Fore, Style
import argparse
import re
from tenacity import retry, stop_after_attempt, wait_exponential
import os 

def validate_address(address):
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        raise ValueError(f"Invalid address format: {address}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def main():
    parser = argparse.ArgumentParser(description="🔎 Smart Contract Security Scanner (ETH, BSC, Polygon)")
    parser.add_argument("address", help="Contract address (e.g., 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606EB48)")
    parser.add_argument("--chain", default="eth", choices=["eth", "bsc", "polygon"], help="Blockchain to scan (default: eth)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    try:
        validate_address(args.address)
        print(Fore.CYAN + f"\n🔍 Fetching contract on {args.chain.upper()} for address: {args.address}")

        source_data, error = fetch_contract_source(args.chain, args.address)
        if error:
            print(Fore.RED + error)
            if source_data and source_data["bytecode"]:
                print(Fore.YELLOW + "🔧 Attempting bytecode analysis...")
                contract_file = os.path.join("contracts", f"{args.chain}_{args.address}.bin")
                with open(contract_file, "w", encoding="utf-8") as f:
                    f.write(source_data["bytecode"])
                result, score = analyze_solidity_code(source_data, contract_file)
                print(Fore.YELLOW + "📋 Audit Report:\n")
                print(Fore.WHITE + result)
                save_report(args.chain, args.address, result, score)
                print(Fore.RED + "\n⚠️ Limited analysis performed due to missing source code.")
            return

        print(Fore.GREEN + "✅ Contract source code retrieved.")
        save_contract_to_file(args.chain, args.address, source_data)

        print(Fore.MAGENTA + "\n🧠 Analyzing contract...\n")
        contract_file = os.path.join("contracts", f"{args.chain}_{args.address}.sol")
        result, score = analyze_solidity_code(source_data, contract_file)

        print(Fore.YELLOW + "📋 Audit Report:\n")
        print(Fore.WHITE + result)

        save_report(args.chain, args.address, result, score)

        if score != "N/A":
            score_int = int(score)
            color = Fore.GREEN if score_int > 80 else Fore.YELLOW if score_int > 50 else Fore.RED
            print(f"\n{color}🔐 Final Security Score: {score}/100")
        else:
            print(Fore.RED + "\n⚠️ Could not determine security score.")
    except Exception as e:
        print(Fore.RED + f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()