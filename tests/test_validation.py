from analytics.sections.section_classifier import RouletteSection as S
from analytics.sections.validation import evaluate_walk_forward, score_predictions


def test_walk_forward_does_not_use_target_in_training():
    sequence = [S.ZERO, S.VOISINS, S.TIERS, S.ORPHELINS] * 8
    predictions = evaluate_walk_forward(sequence, start_after=4, order=1, min_occurrences=1)
    assert len(predictions) == len(sequence) - 4
    # The first prediction is generated from sequence[:4], never sequence[4].
    assert predictions[0][1] is S.ZERO


def test_scores_are_returned_for_multiclass_predictions():
    sequence = [S.ZERO, S.VOISINS]
    predictions = [({S.ZERO: 0.5, S.VOISINS: 0.5, S.TIERS: 0.0, S.ORPHELINS: 0.0}, actual) for actual in sequence]
    result = score_predictions(predictions)
    assert result["evaluated_predictions"] == 2
    assert result["log_loss"] > 0
    assert result["brier_score"] >= 0
