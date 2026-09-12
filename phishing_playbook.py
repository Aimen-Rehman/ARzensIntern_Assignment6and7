import os
import sys
import json
import yaml
import argparse
import requests
from datetime import datetime

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def load_blacklist():
    if not os.path.exists("blacklist_domains.txt"):
        return []
    with open("blacklist_domains.txt", "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

def audit_log(action, details):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details
    }
    with open("playbook.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def check_virustotal(indicator, api_key):
    if not api_key or api_key == "your_vt_api_key_here":
        return 0
    headers = {"x-apikey": api_key}
    url = f"https://www.virustotal.com/api/v3/search?query={indicator}"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return 50
    except Exception:
        pass
    return 0

def execute_playbook(email_file, dry_run=False, rollback=False):
    config = load_config()
    blacklist = load_blacklist()

    if rollback:
        print("[ROLLBACK] Reversing previous containment actions...")
        audit_log("ROLLBACK", "Rolled back quarantine and block rules.")
        return

    with open(email_file, "r") as f:
        email_data = json.load(f)

    sender = email_data.get("sender", "").lower()
    domain = sender.split("@")[-1] if "@" in sender else ""
    subject = email_data.get("subject", "")
    attachment_hash = email_data.get("attachment_hash", "")

    print(f"Processing email from: {sender} | Subject: {subject}")
    audit_log("INGEST", f"Processed email from {sender}")

    risk_score = 0
    if domain in blacklist:
        risk_score += 90
        print(f"[!] Domain {domain} found in local blacklist!")

    vt_key = config.get("virustotal_api_key", "")
    if attachment_hash:
        vt_score = check_virustotal(attachment_hash, vt_key)
        risk_score += vt_score

    print(f"Calculated Risk Score: {risk_score}")
    audit_log("RISK_SCORE", f"Score calculated: {risk_score}")

    if risk_score >= 80:
        action = "High Risk - Auto-block and Quarantine"
        if not dry_run:
            print(action)
        else:
            print(f"[DRY-RUN] Would execute: {action}")
    elif 40 <= risk_score < 80:
        action = "Medium Risk - Analyst Review Required (Human-in-the-Loop)"
        print(action)
        audit_log("HUMAN_REVIEW_TRIGGERED", "Pending analyst sign-off.")
    else:
        action = "Low Risk - Log Only"
        print(action)

    audit_log("COMPLETED", f"Action taken: {action}")

def main():
    parser = argparse.ArgumentParser(description="Phishing Response SOAR Playbook")
    parser.add_argument("--email-file", type=str, default="sample_email.json", help="Path to sample email JSON")
    parser.add_argument("--dry-run", action="store_true", help="Run playbook in dry-run mode")
    parser.add_argument("--rollback", action="store_true", help="Rollback previous automated actions")
    args = parser.parse_args()

    execute_playbook(args.email_file, dry_run=args.dry_run, rollback=args.rollback)

if __name__ == "__main__":
    main()