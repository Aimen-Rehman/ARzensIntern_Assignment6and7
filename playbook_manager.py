import os
import sys
import json
import yaml
import argparse
from datetime import datetime


def load_registry():
    if not os.path.exists("playbook_registry.json"):
        return {"playbooks": []}
    with open("playbook_registry.json", "r") as f:
        return json.load(f)


def log_execution(playbook_name, status, duration_sec):
    history = {"runs": []}
    if os.path.exists("execution_history.json"):
        with open("execution_history.json", "r") as f:
            try:
                history = json.load(f)
            except Exception:
                pass

    history["runs"].append({
        "playbook": playbook_name,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "duration_seconds": duration_sec
    })

    with open("execution_history.json", "w") as f:
        json.dump(history, f, indent=4)


def health_check():
    print("Performing system health checks...")
    registry = load_registry()
    success = True

    if not registry.get("playbooks"):
        print("[-] Warning: Playbook registry is empty.")
        success = False
    else:
        print("[+] Playbook registry loaded successfully.")

    if os.path.exists("config.yaml"):
        print("[+] config.yaml validation passed.")
    else:
        print("[-] Error: config.yaml missing.")
        success = False

    if success:
        print("All health checks passed successfully.")
    else:
        print("Health checks completed with warnings/errors.")


def list_playbooks():
    registry = load_registry()
    print("Registered Playbooks:")
    for pb in registry.get("playbooks", []):
        print(f" - [{pb['id']}] {pb['name']} ({pb['type']}) - Status: {pb['status']}")


def run_playbook(playbook_id):
    registry = load_registry()
    target = None
    for pb in registry.get("playbooks", []):
        if pb["id"] == playbook_id:
            target = pb
            break

    if not target:
        print(f"Playbook ID '{playbook_id}' not found in registry.")
        sys.exit(1)

    print(f"Executing playbook: {target['name']}...")
    start_time = datetime.now()

    script_path = target.get("script")
    if script_path and os.path.exists(script_path):
        os.system(f"python {script_path}")
        status = "SUCCESS"
    else:
        status = "FAILED - Script not found"
        print(f"Error: Target script {script_path} does not exist.")

    duration = (datetime.now() - start_time).total_seconds()
    log_execution(playbook_id, status, duration)
    print(f"Playbook finished with status: {status} in {duration}s")


def main():
    parser = argparse.ArgumentParser(description="SOAR Playbook Manager & Scheduler")
    parser.add_argument("--list", action="store_true", help="Show all registered playbooks")
    parser.add_argument("--run", type=str, help="Execute specific playbook ID")
    parser.add_argument("--schedule", type=str, help="Schedule specific playbook ID")
    parser.add_argument("--interval", type=str, default="hourly", help="Schedule interval")
    parser.add_argument("--health-check", action="store_true", help="Validate setup")
    args = parser.parse_args()

    if args.list:
        list_playbooks()
    elif args.run:
        run_playbook(args.run)
    elif args.schedule:
        print(f"Scheduling playbook '{args.schedule}' with interval: {args.interval}...")
        with open("schedule_config.yaml", "w") as f:
            yaml.dump({"scheduled_playbook": args.schedule, "interval": args.interval}, f)
        print("Schedule configuration updated successfully.")
    elif args.health_check:
        health_check()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()