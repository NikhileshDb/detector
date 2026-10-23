from collections import Counter, defaultdict
from collections.abc import Sequence

from analytics.sections.section_classifier import RouletteSection


def encode_structural_pattern(values: Sequence[RouletteSection]) -> str:
    """Encode repeated-value shape (AABB, ABAB, ABCA, etc.)."""
    symbols: dict[RouletteSection, str] = {}
    result: list[str] = []
    for value in values:
        if value not in symbols:
            symbols[value] = chr(ord("A") + len(symbols))
        result.append(symbols[value])
    return "".join(result)


def scan_structural_patterns(
    sequence: Sequence[RouletteSection | None],
    length: int,
    min_occurrences: int = 1,
) -> list[dict]:
    """Scan contiguous sections and collect actual/structural next states.

    None is a missing-round boundary. Windows and their following state are
    never allowed to cross one of those boundaries.
    """
    if length < 1:
        raise ValueError("length must be positive")
    if min_occurrences < 1:
        raise ValueError("min_occurrences must be positive")

    grouped: dict[str, dict] = {}
    eligible = 0
    for segment in _segments(sequence):
        if len(segment) <= length:
            continue
        for index in range(len(segment) - length):
            eligible += 1
            context = segment[index:index + length]
            following = segment[index + length]
            pattern = encode_structural_pattern(context)
            item = grouped.setdefault(pattern, {
                "pattern": pattern,
                "length": length,
                "occurrences": 0,
                "actual_next": Counter(),
                "structural_next": Counter(),
            })
            item["occurrences"] += 1
            item["actual_next"][following.value] += 1
            labels = {value: chr(ord("A") + pos) for pos, value in enumerate(dict.fromkeys(context))}
            behavior = labels.get(following, "NEW_STATE")
            item["structural_next"][f"NEXT_{behavior}" if behavior != "NEW_STATE" else behavior] += 1

    output = []
    for item in grouped.values():
        if item["occurrences"] < min_occurrences:
            continue
        output.append({
            **item,
            "eligible_windows": eligible,
            "support": item["occurrences"] / eligible if eligible else 0.0,
            "actual_next": dict(item["actual_next"]),
            "structural_next": dict(item["structural_next"]),
        })
    return sorted(output, key=lambda item: item["occurrences"], reverse=True)


def _segments(sequence: Sequence[RouletteSection | None]):
    segment: list[RouletteSection] = []
    for value in sequence:
        if value is None:
            if segment:
                yield segment
                segment = []
        else:
            segment.append(value)
    if segment:
        yield segment
