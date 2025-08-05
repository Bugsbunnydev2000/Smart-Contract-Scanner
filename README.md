# Smart-Contract-Scanner
A Python-based tool for auditing smart contracts on Ethereum, Binance Smart Chain (BSC), and Polygon

Smart Contract Security Scanner
SmartScan is a powerful Python tool for auditing smart contracts on Ethereum, Binance Smart Chain (BSC), and Polygon. It fetches contract source code or bytecode from blockchain explorers, analyzes it for vulnerabilities using Gemini AI and Slither, and generates detailed security reports.

**Note.**

**The website is currently not working, so run it via CLI and terminal to see the results.**


# ✨ Features

Multi-Chain Support: Fetches contracts from Ethereum, BSC, and Polygon using Etherscan, BscScan, and Polygonscan APIs.

AI-Powered Analysis: Uses Gemini AI to detect vulnerabilities like reentrancy, integer overflows, and backdoors.

Static Analysis with Slither: Identifies high and medium severity issues using the Slither framework.

Bytecode Fallback: Analyzes bytecode for unverified contracts when source code is unavailable.

Proxy Contract Support: Retrieves and analyzes implementation contracts for proxy patterns.

Comprehensive Reports: Saves audit results as Markdown (.md) and JSON (.json) files in a reports directory.

Colorized Output: Uses colorama for clear, user-friendly terminal output.

# 🛠 Prerequisites

Python: Version 3.8 or higher.

API Keys:

Etherscan: etherscan.io

BscScan: bscscan.com

Polygonscan: polygonscan.com

Gemini AI: aistudio.google.com


# 📦 Installation


Install Dependencies:

```
pip install -r requirements.txt
```

Configure API Keys:Create a .env file in the project root:

ETHERSCAN_API_KEY= your_etherscan_api_key

BSCSCAN_API_KEY= your_bscscan_api_key

POLYGONSCAN_API_KEY= your_polygonscan_api_key

GEMINI_API_KEY= your_gemini_api_key


# 🚀 Usage

Run smartscan.py with a contract address and optional chain (eth, bsc, or polygon). Use --overwrite to replace existing reports.

Syntax

python smartscan.py <contract_address> [--chain <chain>] [--overwrite]

Examples

Ethereum (e.g., USDC):
```
python smartscan.py 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606EB48 --chain eth --overwrite
```

BSC:
```
python smartscan.py 0x55d398326f99059fF775485246999027B3197955 --chain bsc
```

Polygon:
```
python smartscan.py 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359 --chain polygon
```


# Output

Console: Shows fetching progress, analysis results, and a security score (0-100).

Files:

Contract source: contracts/<chain>_<address>.sol

Audit reports: reports/<chain>_<address>.md and reports/<chain>_<address>.json


# Example 
If you want to see the reported examples, go to the example folder.

📜 License
Licensed under the GNU AGPLv3. This ensures the code remains free, forkable, and protected against direct copying without sharing modifications.
⚠️ Disclaimer
This tool is for informational purposes only. Always conduct professional audits before interacting with smart contracts.
