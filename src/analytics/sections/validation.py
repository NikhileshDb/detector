from math import log

from analytics.sections.markov_model import baseline, current_context, STATES


def evaluate_walk_forward(sequence, start_after=20, order=3, min_occurrences=20):
    predictions = []
    start = max(start_after, order)
    for point in range(start, len(sequence)):
        training = sequence[:point]
        model = current_context(training, order, min_occurrences)
        probabilities = {p.section: p.probability for p in model["predictions"]}
        if model.get("fallback_to_baseline") or not any(probabilities.values()):
            probabilities = {state: baseline(state) for state in STATES}
        predictions.append((probabilities, sequence[point]))
    return predictions


def score_predictions(predictions):
    if not predictions:
        return {"evaluated_predictions": 0, "log_loss": None, "brier_score": None, "top1_accuracy": None, "calibration": []}
    losses = []
    briers = []
    correct = 0
    buckets = {i: {"count": 0, "predicted_probability": 0.0, "observed_frequency": 0} for i in range(10)}
    for probabilities, actual in predictions:
        actual_probability = max(probabilities.get(actual, 0.0), 1e-15)
        losses.append(-log(actual_probability))
        briers.append(sum((probabilities.get(state, 0.0) - (1.0 if state == actual else 0.0)) ** 2 for state in STATES))
        if max(probabilities, key=probabilities.get) == actual: correct += 1
        for state, probability in probabilities.items():
            bucket = min(9, int(probability * 10))
            buckets[bucket]["count"] += 1
            buckets[bucket]["predicted_probability"] += probability
            buckets[bucket]["observed_frequency"] += int(state == actual)
    calibration = [{"bucket": f"{i * 10}-{(i + 1) * 10}%", "count": value["count"], "predicted_probability": value["predicted_probability"] / value["count"], "observed_frequency": value["observed_frequency"] / value["count"]} for i, value in buckets.items() if value["count"]]
    return {"evaluated_predictions": len(predictions), "log_loss": sum(losses) / len(losses), "brier_score": sum(briers) / len(briers), "top1_accuracy": correct / len(predictions), "calibration": calibration}


def compare_models(sequence, start_after=20, min_occurrences=20):
    baseline_scores = score_predictions([({state: baseline(state) for state in STATES}, actual) for actual in sequence[max(start_after, 1):]])
    models = [{"model": "BASELINE", **baseline_scores}]
    for order in range(1, 6):
        scores = score_predictions(evaluate_walk_forward(sequence, start_after, order, min_occurrences))
        models.append({"model": f"MARKOV_ORDER_{order}", **scores, "log_loss_improvement": baseline_scores["log_loss"] - scores["log_loss"] if scores["log_loss"] is not None else None, "brier_improvement": baseline_scores["brier_score"] - scores["brier_score"] if scores["brier_score"] is not None else None, "accuracy_delta": scores["top1_accuracy"] - baseline_scores["top1_accuracy"] if scores["top1_accuracy"] is not None else None})
    return {"evaluated_predictions": len(sequence[max(start_after, 1):]), "models": models}
