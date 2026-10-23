from collections import Counter, defaultdict
from math import sqrt

from analytics.sections.models import Prediction
from analytics.sections.section_classifier import RouletteSection, SECTION_CODES, SECTION_NUMBERS

STATES = tuple(RouletteSection)


def baseline(section: RouletteSection) -> float:
    return len(SECTION_NUMBERS[section]) / 37


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0: return (0.0, 0.0)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    spread = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, centre - spread), min(1.0, centre + spread)


def build_markov_model(sequence: list[RouletteSection], order: int, min_occurrences: int = 1) -> dict[tuple[RouletteSection, ...], dict]:
    if not 1 <= order <= 5: raise ValueError("order must be between 1 and 5")
    counts: dict[tuple[RouletteSection, ...], Counter] = defaultdict(Counter)
    for index in range(order, len(sequence)):
        counts[tuple(sequence[index - order:index])][sequence[index]] += 1
    result = {}
    for context, next_counts in counts.items():
        total = sum(next_counts.values())
        if total < min_occurrences: continue
        predictions = [_prediction(section, next_counts[section], total) for section in STATES]
        result[context] = {"occurrences": total, "predictions": predictions}
    return result


def _prediction(section, count, total):
    probability = count / total if total else 0.0
    low, high = wilson_interval(count, total)
    return Prediction(section, count, probability, baseline(section), (probability - baseline(section)) * 100, low, high)


def current_context(sequence: list[RouletteSection], order: int, min_occurrences: int = 20) -> dict:
    requested = tuple(sequence[-order:]) if len(sequence) >= order else tuple(sequence)
    used = min(order, len(requested))
    while used >= 1:
        context = tuple(requested[-used:])
        model = build_markov_model(sequence, used, min_occurrences)
        if context in model:
            return {"requested_order": order, "used_order": used, "backoff_used": used != order, "context": context, "context_code": ''.join(SECTION_CODES[s] for s in context), **model[context]}
        used -= 1
    return {"requested_order": order, "used_order": 0, "backoff_used": True, "fallback_to_baseline": True, "context": requested, "context_code": ''.join(SECTION_CODES[s] for s in requested), "occurrences": 0, "predictions": [_prediction(s, 0, 1) for s in STATES]}
