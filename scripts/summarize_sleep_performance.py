"""Reproduce the website's pooled window-level scores from its public exports."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets"
probability_path = ROOT / "sleep-probabilities.json"
probabilities = json.loads(probability_path.read_text())
observed = json.loads((ROOT / "sleep-ground-truth.json").read_text())

assert hashlib.sha256(probability_path.read_bytes()).hexdigest() == observed["probabilities_sha256"]
assert probabilities["stages"] == observed["stages"] == ["Wake", "N1", "N2", "N3"]
rows = probabilities["probabilities"]
labels = observed["labels"]
assert len(rows) == len(labels) == 9121
assert all(len(row) == 4 and abs(sum(row) - 1) < 1e-8 for row in rows)

predicted = [max(range(4), key=lambda stage: row[stage]) for row in rows]
confusion = [
    [sum(truth == actual and guess == predicted_stage
         for truth, guess in zip(labels, predicted))
     for predicted_stage in range(4)]
    for actual in range(4)
]
per_stage = []
for stage, name in enumerate(observed["stages"]):
    support = sum(confusion[stage])
    predicted_count = sum(confusion[row][stage] for row in range(4))
    true_positive = confusion[stage][stage]
    per_stage.append({
        "stage": name,
        "windows": support,
        "precision": true_positive / predicted_count,
        "recall": true_positive / support,
        "f1": 2 * true_positive / (support + predicted_count),
    })

print(json.dumps({
    "windows": len(labels),
    "macro_f1": sum(row["f1"] for row in per_stage) / 4,
    "balanced_accuracy": sum(row["recall"] for row in per_stage) / 4,
    "accuracy": sum(confusion[stage][stage] for stage in range(4)) / len(labels),
    "per_stage": per_stage,
    "confusion_rows_observed_columns_predicted": confusion,
}, indent=2))
