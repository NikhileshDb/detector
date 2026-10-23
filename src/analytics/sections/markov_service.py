from analytics.sections.markov_model import STATES, baseline, build_markov_model, current_context
from analytics.sections.section_classifier import SECTION_CODES, get_section
from analytics.sections.structural_patterns import encode_structural_pattern, scan_structural_patterns
from analytics.sections.validation import compare_models


class SectionMarkovService:
    def __init__(self, spin_repository):
        self.spin_repository = spin_repository

    def sequence(self, window: int | None = 500):
        spins = self.spin_repository.recent(window or 1000000)
        spins.reverse()
        return [(spin.round_id, int(spin.number), get_section(spin.number)) for spin in spins]

    def current(self, window=1000, order=3, min_occurrences=20):
        seq = [item[2] for item in self.sequence(window)]
        result = current_context(seq, order, min_occurrences)
        result["predictions"] = [_prediction_json(prediction) for prediction in result["predictions"]]
        return result

    def matrix(self, window=500):
        seq = [item[2] for item in self.sequence(window)]
        model = build_markov_model(seq, 1)
        cells = []
        for source in STATES:
            for prediction in model.get((source,), {}).get("predictions", []):
                cells.append({"from": source.value, "to": prediction.section.value, "code": SECTION_CODES[prediction.section], "count": prediction.count, "historical_probability": prediction.probability, "baseline_probability": prediction.baseline_probability, "deviation_pp": prediction.deviation_pp, "ci_low": prediction.ci_low, "ci_high": prediction.ci_high})
        return {"states": [s.value for s in STATES], "matrix": cells}

    def recent(self, limit=50):
        return [{"round_id": rid, "number": number, "section": section.value, "code": SECTION_CODES[section]} for rid, number, section in self.sequence(limit)]

    def contexts(self, window=1000, order=3, min_occurrences=20):
        seq = [item[2] for item in self.sequence(window)]
        result = []
        for context, item in build_markov_model(seq, order, min_occurrences).items():
            result.append({"context_code": ''.join(SECTION_CODES[s] for s in context), "context": [s.value for s in context], "occurrences": item["occurrences"], "sample_strength": _strength(item["occurrences"]), "next": {p.section.value: {"count": p.count, "historical_probability": p.probability, "baseline_probability": p.baseline_probability, "deviation_pp": p.deviation_pp} for p in item["predictions"]}})
        return sorted(result, key=lambda x: x["occurrences"], reverse=True)

    def overview(self, window=100):
        sequence = [item[2] for item in self.sequence(window)]
        total = len(sequence)
        rows = []
        for section in STATES:
            hits = sum(value == section for value in sequence)
            gaps = []
            running = 0
            for value in sequence:
                if value == section:
                    gaps.append(running); running = 0
                else: running += 1
            rows.append({"section": section.value, "code": SECTION_CODES[section], "hits": hits, "percentage": hits / total * 100 if total else 0, "baseline_probability": baseline(section), "deviation_pp": ((hits / total) - baseline(section)) * 100 if total else -baseline(section) * 100, "current_gap": running, "average_gap": sum(gaps) / len(gaps) if gaps else None, "max_gap": max(gaps) if gaps else None})
        return {"window": total, "sections": rows}

    def patterns(self, length=4, window=1000, min_occurrences=20, sort="occurrences"):
        sequence = [item[2] for item in self.sequence(window)]
        items = scan_structural_patterns(sequence, length, min_occurrences)
        if sort == "support":
            items.sort(key=lambda item: item["support"], reverse=True)
        elif sort == "largest_deviation":
            items.sort(key=lambda item: max((abs(item.get("deviation_pp", 0)),), default=0), reverse=True)
        return items

    def current_pattern(self, length=4, window=1000, min_occurrences=20):
        sequence = [item[2] for item in self.sequence(window)]
        context = sequence[-length:]
        if len(context) < length:
            return {"pattern": None, "length": length, "current_context": [s.value for s in context], "context_code": ''.join(SECTION_CODES[s] for s in context), "occurrences": 0, "support": 0.0, "structural_next": {}, "actual_next": {}, "sample_strength": "VERY_LOW"}
        pattern = encode_structural_pattern(context)
        symbol_mapping = {}
        for section, symbol in zip(dict.fromkeys(context), dict.fromkeys(pattern)):
            symbol_mapping[symbol] = section.value
        item = next((value for value in scan_structural_patterns(sequence, length, 1) if value["pattern"] == pattern), None)
        if item is None:
            item = {"occurrences": 0, "eligible_windows": max(0, len(sequence) - length), "support": 0.0, "structural_next": {}, "actual_next": {}}
        return {"pattern": pattern, "length": length, "current_context": [s.value for s in context], "context_code": ''.join(SECTION_CODES[s] for s in context), "symbol_mapping": symbol_mapping, **item, "sample_strength": _strength(item["occurrences"])}

    def validation(self, start_after=20, window=1000, min_occurrences=20):
        return compare_models([item[2] for item in self.sequence(window)], start_after, min_occurrences)


def _strength(value):
    if value < 10: return "VERY_LOW"
    if value < 30: return "LOW"
    if value < 100: return "MEDIUM"
    if value < 500: return "HIGH"
    return "VERY_HIGH"


def _prediction_json(prediction):
    return {
        "section": prediction.section.value,
        "code": SECTION_CODES[prediction.section],
        "count": prediction.count,
        "historical_probability": prediction.probability,
        "baseline_probability": prediction.baseline_probability,
        "deviation_pp": prediction.deviation_pp,
        "ci_low": prediction.ci_low,
        "ci_high": prediction.ci_high,
    }
