"""Transparent synthetic five-player macro stress tests, not LoL win forecasts."""
import json
from pathlib import Path

from .config import CONFIG
from .util import atomic_json

SCENARIOS = ("five_top", "five_mid", "five_jungle", "five_bot", "five_faker")
ZONES = ("top", "mid", "jungle", "bot")


def allocation(scenario: str, minute: int) -> tuple[int, ...]:
    if scenario not in SCENARIOS: raise ValueError(scenario)
    if scenario == "five_faker":
        # Purely hypothetical rotating five-person allocation; no Faker agent exists.
        return (1, 1, 1, 2) if minute < 10 else (1, 1, 2, 1) if minute < 20 else (1, 2, 1, 1)
    focus = {"five_top": 0, "five_mid": 1, "five_jungle": 2, "five_bot": 3}[scenario]
    return tuple(5 if j == focus else 0 for j in range(4))


def simulate(scenario: str, response_delay: int = 2, sharing: float = .7) -> list[dict]:
    if response_delay not in (1, 2, 4) or not 0 < sharing <= 1:
        raise ValueError("Unsupported synthetic controls")
    rows = []
    for tick, minute in enumerate(range(0, 36, 5)):
        ours = allocation(scenario, minute)
        focus = max(range(4), key=lambda i: ours[i])
        enemy = [1, 1, 1, 2]
        if scenario != "five_faker" and tick >= response_delay:
            donor = 3 if focus != 3 else 0
            enemy[donor] -= 1
            enemy[focus] += 1
        # Lane/jungle supplies are deliberately abstract, fixed units.
        resources = sum(min(1.0, n) + sharing * max(0, min(n - 1, 1)) for n in ours if n) / 5
        coverage = sum(n > 0 for n in ours) / 4
        local = max(0, ours[focus] - enemy[focus]) / 5
        pressure = min(1.0, .52 * local + .28 * coverage + .2 * resources)
        rows.append({"minute": minute, "allocation": dict(zip(ZONES, ours)),
                     "opponent_allocation": dict(zip(ZONES, enemy)),
                     "resource_access": round(resources, 4), "map_coverage": round(coverage, 4),
                     "local_pressure": round(local, 4), "composite": round(pressure, 4)})
    return rows


def generate(output: Path = CONFIG.root / "docs" / "data" / "challenge_scenarios.json") -> dict:
    grid = {scenario: {str(delay): {str(sharing): simulate(scenario, delay, sharing)
                                     for sharing in (.4, .7, 1.0)} for delay in (1, 2, 4)}
            for scenario in SCENARIOS}
    report = {"schema_version": 1, "type": "synthetic_stress_test", "calibrated_to_matches": False,
              "not_a_win_probability": True, "time_step_minutes": 5,
              "assumptions": {"zones": ZONES, "baseline_opponent": [1, 1, 1, 2],
                              "five_faker": "Hypothetical rotating allocation, not five trained Faker agents",
                              "resource_access": "One supply unit per occupied zone plus sharing fraction for at most one extra player, divided by five",
                              "map_coverage": "Occupied zones divided by four",
                              "local_pressure": "Positive player-count difference at strongest zone, divided by five",
                              "composite": "0.52 local pressure + 0.28 coverage + 0.20 resource access, clipped to one"},
              "scenarios": grid}
    atomic_json(output, report)
    return report


if __name__ == "__main__":
    result = generate()
    print(json.dumps({"scenarios": list(result["scenarios"]), "time_step_minutes": 5,
                      "calibrated_to_matches": False}))
