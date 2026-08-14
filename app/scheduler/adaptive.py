import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class LatencyStats:
    median_ms: float
    p90_ms: float
    jitter_ms: float
    outbound_ms: float


def latency_stats(samples_ms: list[float]) -> LatencyStats:
    if not samples_ms:
        raise ValueError("At least one latency sample is required")
    values = sorted(float(x) for x in samples_ms)
    median = statistics.median(values)
    p90 = values[min(len(values) - 1, max(0, int(len(values) * .9)))]
    jitter = statistics.pstdev(values) if len(values) > 1 else 0.0
    # RTT/2 is an estimate; internet routes can be asymmetric. Keep this visible
    # in the UI instead of presenting it as an exact server timestamp.
    return LatencyStats(median, p90, jitter, median / 2.0)


def fire_offsets_ms(arrival_offsets_ms: list[float], outbound_ms: float) -> list[float]:
    """Convert desired server arrival offsets after midnight to scheduler offsets before midnight."""
    return [outbound_ms - arrival for arrival in arrival_offsets_ms]
