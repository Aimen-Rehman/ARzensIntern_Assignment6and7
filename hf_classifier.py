import sys
import csv
import argparse
from transformers import pipeline


def main():
    parser = argparse.ArgumentParser(description="Hugging Face Security Alert Classifier")
    parser.add_argument("--input-csv", type=str, default="sample_alerts.csv",
                        help="Path to input CSV containing security alerts")
    parser.add_argument("--threshold", type=float, default=0.75, help="Confidence thresholding (0.0 to 1.0)")
    args = parser.parse_args()

    print("Loading pre-trained model from local cache / Hugging Face...")
    classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

    classified_results = []

    try:
        with open(args.input_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                alert_text = row.get("alert_text", "")
                prediction = classifier(alert_text)[0]
                label = prediction["label"]
                score = prediction["score"]

                # Map classification logic to security context
                is_threat = "Threat" if score >= args.threshold and label == "NEGATIVE" else "Non-threat"

                classified_results.append({
                    "alert_id": row.get("alert_id", "N/A"),
                    "alert_text": alert_text,
                    "raw_label": label,
                    "confidence": round(score, 4),
                    "classification": is_threat
                })
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        sys.exit(1)

    # Save output
    output_file = "classified_output.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as cf:
        fieldnames = ["alert_id", "alert_text", "raw_label", "confidence", "classification"]
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for res in classified_results:
            writer.writerow(res)

    print(f"Batch classification complete. Results saved to {output_file}.")


if __name__ == "__main__":
    main()