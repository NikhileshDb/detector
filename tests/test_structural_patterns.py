from analytics.sections.section_classifier import RouletteSection as S
from analytics.sections.structural_patterns import encode_structural_pattern, scan_structural_patterns


def test_structural_encoder():
    assert encode_structural_pattern([S.VOISINS, S.VOISINS, S.TIERS, S.TIERS]) == "AABB"
    assert encode_structural_pattern([S.VOISINS, S.TIERS, S.VOISINS, S.TIERS]) == "ABAB"
    assert encode_structural_pattern([S.VOISINS, S.TIERS, S.ORPHELINS, S.VOISINS]) == "ABCA"
    assert encode_structural_pattern([S.VOISINS, S.TIERS, S.ORPHELINS, S.ZERO]) == "ABCD"


def test_scan_collects_actual_and_structural_continuations():
    result = scan_structural_patterns([S.VOISINS, S.VOISINS, S.TIERS, S.TIERS, S.ORPHELINS], 4)[0]
    assert result["pattern"] == "AABB"
    assert result["occurrences"] == 1
    assert result["actual_next"] == {"ORPHELINS": 1}
    assert result["structural_next"] == {"NEW_STATE": 1}


def test_missing_boundary_prevents_cross_boundary_windows():
    sequence = [S.VOISINS, S.TIERS, None, S.TIERS, S.ORPHELINS]
    assert scan_structural_patterns(sequence, 2) == []
