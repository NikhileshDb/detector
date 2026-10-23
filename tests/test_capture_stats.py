import pytest

from analytics.capture_stats import CaptureStatsAccumulator
from storage.capture_stats_repository import CaptureStatsRepository


def test_summary_reports_rates_and_wheel_coverage():
    stats = CaptureStatsAccumulator()
    for i in range(61):
        stats.push(i / 60, is_duplicate=i % 2 == 1, wheel_visible=i < 30)

    summary = stats.summary()

    assert summary.frames == 61
    assert summary.unique_frames == 31
    assert summary.duration_seconds == pytest.approx(1.0)
    assert summary.stream_fps == pytest.approx(30.0)
    assert summary.wheel_view_ratio == pytest.approx(30 / 61)


def test_wheel_ratio_is_none_without_wheel_checks():
    stats = CaptureStatsAccumulator()
    stats.push(0.0, False)
    stats.push(0.1, False)

    assert stats.summary().wheel_view_ratio is None


def test_reset_clears_round():
    stats = CaptureStatsAccumulator()
    stats.push(0.0, False)
    stats.reset()

    assert stats.summary() is None


def test_repository_round_trip(database, round_repository):
    stored_round = round_repository.create(sequence=1)
    stats = CaptureStatsAccumulator()
    stats.push(0.0, False, True)
    stats.push(0.5, False, False)
    summary = stats.summary()

    repository = CaptureStatsRepository(database)
    repository.save(stored_round.id, summary)

    assert repository.get(stored_round.id) == summary
    assert repository.get(999) is None
