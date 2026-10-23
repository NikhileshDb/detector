from dataclasses import dataclass

from analytics.sections.section_classifier import RouletteSection


@dataclass(frozen=True)
class Prediction:
    section: RouletteSection
    count: int
    probability: float
    baseline_probability: float
    deviation_pp: float
    ci_low: float | None = None
    ci_high: float | None = None


def sample_strength(occurrences: int) -> str:
    if occurrences < 10: return "VERY_LOW"
    if occurrences < 30: return "LOW"
    if occurrences < 100: return "MEDIUM"
    if occurrences < 500: return "HIGH"
    return "VERY_HIGH"
