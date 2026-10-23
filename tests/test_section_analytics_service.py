from types import SimpleNamespace

from analytics.sections.markov_service import SectionMarkovService


def _repository(numbers):
    # Repository contract is newest-first.
    return SimpleNamespace(recent=lambda limit: [SimpleNamespace(round_id=i, number=str(n)) for i, n in reversed(list(enumerate(numbers)))])


def test_current_pattern_and_pattern_explorer():
    service = SectionMarkovService(_repository([7, 7, 23, 23, 17, 7, 7, 23, 23]))
    current = service.current_pattern(length=4, min_occurrences=1)
    assert current["pattern"] == "AABB"
    assert current["context_code"] == "VVTT"
    assert current["actual_next"] == {"ORPHELINS": 1}
    assert any(item["pattern"] == "AABB" for item in service.patterns(length=4, min_occurrences=1))


def test_overview_has_section_gap_fields():
    sections = SectionMarkovService(_repository([0, 7, 23])).overview()["sections"]
    zero = next(item for item in sections if item["section"] == "ZERO")
    assert zero["hits"] == 1
    assert zero["current_gap"] == 2
