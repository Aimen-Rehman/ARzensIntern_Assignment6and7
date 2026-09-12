import os
import sys
import json
import csv
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_log_content(log_text, dry_run=False):
    prompt = f"""
    You are an expert security analyst. Analyze the following security log entry and provide:
    1. Event Summary (1-2 sentences)
    2. Severity (Low, Medium, High, Critical)
    3. Recommended Action

    Log Entry:
    {log_text}

    Format your response strictly as JSON with keys: "summary", "severity", "recommended_action".
    """

    if dry_run:
        print("[DRY-RUN] Would send prompt to OpenAI:")
        return {"summary": "Dry-run simulation summary", "severity": "Low", "recommended_action": "None"}

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content
        usage = response.usage
        cost = (usage.prompt_tokens * 0.0015 / 1000) + (usage.completion_tokens * 0.002 / 1000)

        with open("cost_tracker.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["gpt-3.5-turbo", usage.total_tokens, cost])

        return json.loads(content)
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="OpenAI Security Log Analyzer")
    parser.add_argument("--log-file", type=str, help="Path to log file")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without API calls")
    args = parser.parse_args()

    logs = []
    if args.log_file:
        if os.path.exists(args.log_file):
            with open(args.log_file, "r") as f:
                logs = f.readlines()
        else:
            print(f"Log file {args.log_file} not found.")
            sys.exit(1)

    results = []
    for line in logs:
        line = line.strip()
        if not line:
            continue
        print(f"Analyzing: {line}")
        res = analyze_log_content(line, dry_run=args.dry_run)
        results.append({"log": line, **res})

    with open("analyzed_output.json", "w") as jf:
        json.dump(results, jf, indent=4)

    with open("analyzed_output.csv", "w", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(["Log", "Summary", "Severity", "Recommended Action"])
        for r in results:
            writer.writerow([r.get("log"), r.get("summary"), r.get("severity"), r.get("recommended_action")])

    print("Analysis complete. Saved to analyzed_output.json and analyzed_output.csv.")


if __name__ == "__main__":
    main()