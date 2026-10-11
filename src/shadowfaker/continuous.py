"""Resolution-independent scoring contract for future observed Faker actions.

Grid cells are display coordinates only. This evaluator deliberately has no
interpolation path: an observed label needs a source and exact timestamp.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

MAP_UNITS = 15_000.0


@dataclass(frozen=True)
class ObservedAction:
    match_id: str
    issued_at_ms: int
    observed_at_ms: int
    action: str
    xy: tuple[float, float] | None
    source: str
    perspective: str


@dataclass(frozen=True)
class ForecastAction:
    match_id: str
    issued_at_ms: int
    predicted_at_ms: int
    action: str
    xy: tuple[float, float] | None


def display_cell(xy: tuple[float, float], grid: int) -> tuple[int, int]:
    if grid < 2 or not all(math.isfinite(v) and 0 <= v <= 1 for v in xy):
        raise ValueError("Invalid grid or normalized coordinates")
    return tuple(min(grid - 1, int(v * grid)) for v in xy)


def distance_units(a: tuple[float, float], b: tuple[float, float]) -> float:
    if not all(math.isfinite(v) and 0 <= v <= 1 for v in (*a, *b)):
        raise ValueError("Invalid normalized coordinates")
    return MAP_UNITS * math.dist(a, b)


def score(pairs: list[tuple[ForecastAction, ObservedAction]], *,
          horizon_seconds: float, radius_units: float, time_tolerance_seconds: float) -> dict:
    """Joint action/time/place accuracy on observed labels, not interpolations.

    Missing spatial labels are counted separately, never silently counted as
    successful positions. The caller must freeze match splits and thresholds.
    """
    if not (0 < horizon_seconds <= 60 and radius_units > 0 and time_tolerance_seconds >= 0):
        raise ValueError("Invalid evaluation thresholds")
    eligible = action_hits = temporal_hits = spatial_pairs = joint_hits = missing_xy = 0
    distances = []
    for forecast, observed in pairs:
        if (forecast.match_id, forecast.issued_at_ms) != (observed.match_id, observed.issued_at_ms):
            raise ValueError("Forecast and observation identity mismatch")
        if not observed.source or not observed.perspective:
            raise ValueError("Observed action requires provenance and perspective")
        if observed.observed_at_ms <= observed.issued_at_ms:
            raise ValueError("Observed label must occur after forecast time")
        if observed.observed_at_ms - observed.issued_at_ms > horizon_seconds * 1000:
            continue
        eligible += 1
        action_ok = forecast.action == observed.action
        time_ok = abs(forecast.predicted_at_ms - observed.observed_at_ms) <= time_tolerance_seconds * 1000
        action_hits += action_ok
        temporal_hits += time_ok
        if observed.xy is None:
            missing_xy += 1
            continue
        if forecast.xy is None:
            spatial_pairs += 1
            continue
        distance = distance_units(forecast.xy, observed.xy)
        distances.append(distance)
        spatial_pairs += 1
        joint_hits += bool(action_ok and time_ok and distance <= radius_units)
    return {"eligible": eligible, "action_accuracy": action_hits / eligible if eligible else None,
            "temporal_accuracy": temporal_hits / eligible if eligible else None,
            "spatially_observed": spatial_pairs, "spatial_label_missing": missing_xy,
            "joint_action_time_place_accuracy": joint_hits / spatial_pairs if spatial_pairs else None,
            "mean_distance_units": sum(distances) / len(distances) if distances else None,
            "radius_units": radius_units, "horizon_seconds": horizon_seconds,
            "time_tolerance_seconds": time_tolerance_seconds}
