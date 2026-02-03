import csv
import json
import os
import sys
from typing import Dict, List, Tuple
from collections import defaultdict

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.modules.prompt_parser import parse_prompt

DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "app", "data", "synthetic_dataset.csv"
)
RESULTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "app", "data", "evaluation_results.json"
)


def load_dataset() -> List[Dict]:
    """Load synthetic dataset from CSV."""
    rows = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def normalize_email(email: str) -> str:
    """Normalize email for comparison."""
    return email.lower().strip() if email else ""


def normalize_tasks(tasks: List[str]) -> List[str]:
    """Normalize task list for comparison."""
    return [t.strip() for t in tasks if t.strip()]


def calculate_task_metrics(predicted: List[str], ground_truth: List[str]) -> Dict:
    """
    Calculate precision, recall, F1 for task extraction.
    Uses simple string matching (case-insensitive, whitespace normalized).
    """
    pred_set = set(t.lower().strip() for t in predicted)
    truth_set = set(t.lower().strip() for t in ground_truth)
    
    if not truth_set:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "exact_match": False,
        }
    
    true_positives = len(pred_set & truth_set)
    false_positives = len(pred_set - truth_set)
    false_negatives = len(truth_set - pred_set)
    
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    exact_match = pred_set == truth_set
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match,
    }


def evaluate_parser() -> Dict:
    """
    Run evaluation on entire dataset.
    Returns comprehensive metrics and failure cases.
    """
    dataset = load_dataset()
    total = len(dataset)
    
    # Metrics tracking
    email_correct = 0
    email_failures = []
    
    task_metrics = []
    task_exact_matches = 0
    task_failures = []
    
    print(f"Evaluating parser on {total} samples...\n")
    
    for i, row in enumerate(dataset, 1):
        row_id = row["id"]
        raw_prompt = row["raw_prompt"]
        gt_email = normalize_email(row["recipient_email"])
        gt_tasks = json.loads(row["tasks"])
        
        # Parse with our parser
        pred_email, pred_tasks = parse_prompt(raw_prompt)
        pred_email_norm = normalize_email(pred_email) if pred_email else ""
        pred_tasks_norm = normalize_tasks(pred_tasks)
        gt_tasks_norm = normalize_tasks(gt_tasks)
        
        # Email evaluation
        email_match = pred_email_norm == gt_email
        if email_match:
            email_correct += 1
        else:
            email_failures.append({
                "id": row_id,
                "predicted": pred_email,
                "ground_truth": gt_email,
                "prompt_snippet": raw_prompt[:150],
            })
        
        # Task evaluation
        metrics = calculate_task_metrics(pred_tasks_norm, gt_tasks_norm)
        task_metrics.append(metrics)
        
        if metrics["exact_match"]:
            task_exact_matches += 1
        else:
            task_failures.append({
                "id": row_id,
                "predicted_count": len(pred_tasks_norm),
                "ground_truth_count": len(gt_tasks_norm),
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "prompt_snippet": raw_prompt[:150],
            })
        
        # Progress indicator
        if i % 100 == 0:
            print(f"Processed {i}/{total} samples...")
    
    # Aggregate task metrics
    avg_precision = sum(m["precision"] for m in task_metrics) / total
    avg_recall = sum(m["recall"] for m in task_metrics) / total
    avg_f1 = sum(m["f1"] for m in task_metrics) / total
    
    # Email accuracy
    email_accuracy = email_correct / total
    
    # Task exact match rate
    task_exact_match_rate = task_exact_matches / total
    
    results = {
        "total_samples": total,
        "email_extraction": {
            "accuracy": email_accuracy,
            "correct": email_correct,
            "incorrect": total - email_correct,
            "top_failures": email_failures[:20],  # Top 20 failures
        },
        "task_extraction": {
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1": avg_f1,
            "exact_match_rate": task_exact_match_rate,
            "exact_matches": task_exact_matches,
            "partial_matches": total - task_exact_matches,
            "top_failures": task_failures[:20],  # Top 20 failures by F1
        },
    }
    
    return results


def print_results(results: Dict):
    """Print evaluation results in a readable format."""
    print("\n" + "=" * 80)
    print("PARSER EVALUATION RESULTS")
    print("=" * 80)
    
    print(f"\nTotal Samples: {results['total_samples']}")
    
    print("\n--- EMAIL EXTRACTION ---")
    email = results["email_extraction"]
    print(f"Accuracy: {email['accuracy']:.2%} ({email['correct']}/{results['total_samples']})")
    print(f"Correct: {email['correct']}")
    print(f"Incorrect: {email['incorrect']}")
    
    if email["top_failures"]:
        print(f"\nTop Email Extraction Failures (showing {len(email['top_failures'])}):")
        for i, failure in enumerate(email["top_failures"][:5], 1):
            print(f"\n  {i}. ID: {failure['id']}")
            print(f"     Predicted: {failure['predicted']}")
            print(f"     Ground Truth: {failure['ground_truth']}")
            print(f"     Prompt: {failure['prompt_snippet']}...")
    
    print("\n--- TASK EXTRACTION ---")
    task = results["task_extraction"]
    print(f"Avg Precision: {task['avg_precision']:.2%}")
    print(f"Avg Recall: {task['avg_recall']:.2%}")
    print(f"Avg F1 Score: {task['avg_f1']:.2%}")
    print(f"Exact Match Rate: {task['exact_match_rate']:.2%} ({task['exact_matches']}/{results['total_samples']})")
    
    if task["top_failures"]:
        print(f"\nTop Task Extraction Failures (showing {len(task['top_failures'])}):")
        for i, failure in enumerate(task["top_failures"][:5], 1):
            print(f"\n  {i}. ID: {failure['id']}")
            print(f"     Predicted Count: {failure['predicted_count']}, Ground Truth Count: {failure['ground_truth_count']}")
            print(f"     Precision: {failure['precision']:.2%}, Recall: {failure['recall']:.2%}, F1: {failure['f1']:.2%}")
            print(f"     Prompt: {failure['prompt_snippet']}...")
    
    print("\n" + "=" * 80)


def save_results(results: Dict):
    """Save results to JSON file for later analysis."""
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results saved to: {RESULTS_PATH}")


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        print("Please run generate_dataset.py first.")
        sys.exit(1)
    
    results = evaluate_parser()
    print_results(results)
    save_results(results)
    
    # Exit code based on performance
    email_acc = results["email_extraction"]["accuracy"]
    task_f1 = results["task_extraction"]["avg_f1"]
    
    if email_acc >= 0.95 and task_f1 >= 0.90:
        print("\n Parser performance is EXCELLENT!")
        return 0
    elif email_acc >= 0.85 and task_f1 >= 0.75:
        print("\n Parser performance is GOOD but could be improved.")
        return 0
    else:
        print("\n Parser performance needs improvement.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
