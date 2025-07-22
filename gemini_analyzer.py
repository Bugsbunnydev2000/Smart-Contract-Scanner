import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import json
from slither import Slither
from slither.exceptions import SlitherError

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_solidity_code(source_data, contract_file):
    if not source_data["source_code"]:
        # Bytecode-only analysis
        bytecode = source_data["bytecode"]
        slither_result = ""
        try:
            slither = Slither(contract_file, solc_force_bytecode=True)
            issues = []
            for detector in slither.detectors:
                if detector.impact in ["High", "Medium"]:
                    issues.append(f"{detector.description}: {detector.impact} severity")
            slither_result = "\n".join(issues) or "No high/medium severity issues detected."
        except SlitherError as e:
            slither_result = f"Slither error: {str(e)}"

        result = (
            "# Analysis Report\n"
            "⚠️ Source code not available. Performed limited bytecode analysis.\n"
            f"# Static Analysis Results (Slither)\n{slither_result}\n"
            "Recommendation: Contact the contract owner to verify the source code on the blockchain explorer."
        )
        return result, "N/A"

    prompt = (
        "You are a professional smart contract auditor. Carefully audit the following Solidity code:\n\n"
        "- Identify malicious patterns (e.g. backdoors, owner-only minting, honeypots, tx.origin usage).\n"
        "- Check for vulnerabilities like reentrancy, integer overflows, unchecked calls, gas griefing, timestamp dependence.\n"
        "- Be concise but clear. Explain risks in **non-technical** language.\n"
        "- Give an overall SECURITY SCORE from 0 (dangerous) to 100 (safe).\n"
        "- End your answer with this line exactly: 'Security Score: XX/100'.\n\n"
        f"Proxy Contract:\n{source_data['source_code']}\n\n"
        f"Implementation Contract:\n{source_data.get('implementation_code', 'N/A')}"
    )
    try:
        # Gemini AI analysis
        response = model.generate_content(prompt)
        gemini_result = response.text.strip()
        score_match = re.search(r"Security Score:\s*(\d{1,3})/100", gemini_result)
        gemini_score = score_match.group(1) if score_match else "N/A"

        # Slither static analysis
        slither_result = ""
        try:
            slither = Slither(contract_file)
            issues = []
            for detector in slither.detectors:
                if detector.impact in ["High", "Medium"]:
                    issues.append(f"{detector.description}: {detector.impact} severity")
            slither_result = "\n".join(issues) or "No high/medium severity issues detected."
        except SlitherError as e:
            slither_result = f"Slither error: {str(e)}"

        # Combine results
        combined_result = (
            f"# AI Audit Results\n{gemini_result}\n\n"
            f"# Static Analysis Results (Slither)\n{slither_result}"
        )
        return combined_result, gemini_score
    except Exception as e:
        return f"❌ Analysis error: {str(e)}", "N/A"

def save_report(chain, address, result, score, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, f"{chain}_{address}.md")
    json_path = os.path.join(output_dir, f"{chain}_{address}.json")
    
    if os.path.exists(md_path) or os.path.exists(json_path):
        raise FileExistsError(f"Report for {chain}_{address} already exists. Use --overwrite to replace.")

    # Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Audit Report: `{chain}:{address}`\n\n")
        f.write(result + "\n")
        f.write(f"\n**Final Score: {score}/100**\n")

    # JSON
    json.dump({
        "chain": chain,
        "address": address,
        "score": score,
        "report": result
    }, open(json_path, "w", encoding="utf-8"), indent=2)

    print(f"📦 Report saved as: {md_path} and {json_path}")