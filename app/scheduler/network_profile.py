"""Robust Xiaomi HTTP-path measurements and finite timing recommendations."""

import math
import statistics
import threading
import time
from dataclasses import dataclass

from app.xiaomi.models import ResultKind


@dataclass(frozen=True)
class NetworkProfile:
    attempted: int
    usable: int
    discarded: int
    median_ms: float
    p10_ms: float
    p90_ms: float
    jitter_ms: float
    outbound_ms: float
    arrival_offsets_ms: tuple[int, int, int, int]
    fire_offsets_ms: tuple[float, float, float, float]
    quality: str


def _percentile(values: list[float], percentile: float) -> float:
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def _round_up(value: float, step: int = 10) -> int:
    return int(math.ceil(value / step) * step)


def _usable_samples(samples_ms: list[float]) -> tuple[list[float], int]:
    values = sorted(float(value) for value in samples_ms
                    if math.isfinite(float(value)) and 1.0 <= float(value) <= 15_000.0)
    if len(values) < 4:
        raise ValueError("At least 4 successful Xiaomi latency samples are required")
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    mad = statistics.median(deviations)
    # Keep normal route variation while rejecting isolated timeouts/server stalls.
    upper_limit = median + max(4.5 * mad, 250.0, median * 1.5)
    filtered = [value for value in values if value <= upper_limit]
    if len(filtered) < 4:
        filtered = values
    return filtered, len(values) - len(filtered)


def build_network_profile(samples_ms: list[float], *, attempted: int | None = None) -> NetworkProfile:
    """Create four network-specific server-arrival targets from HTTP RTT samples.

    RTT/2 is necessarily an estimate of outbound delay because the route can be
    asymmetric. The four attempts cover the reset boundary and widen only when
    the measured path is variable; they never become an unbounded request loop.
    """
    values, _ = _usable_samples(samples_ms)
    median = statistics.median(values)
    p10 = _percentile(values, 0.10)
    p90 = _percentile(values, 0.90)
    mad = statistics.median(abs(value - median) for value in values)
    robust_jitter = 1.4826 * mad
    spread = max(40.0, p90 - p10, robust_jitter * 2.0)
    spread = min(spread, 400.0)

    arrivals = (
        -_round_up(max(100.0, spread * 0.8)),
        _round_up(max(20.0, spread * 0.2)),
        _round_up(max(120.0, spread * 1.2)),
        _round_up(max(300.0, spread * 3.0)),
    )
    outbound = median / 2.0
    fires = tuple(outbound - arrival for arrival in arrivals)
    variability = p90 - p10
    quality = "STABLE" if variability <= 80 else "VARIABLE" if variability <= 200 else "UNSTABLE"
    total = attempted if attempted is not None else len(samples_ms)
    discarded = max(0, total - len(values))
    return NetworkProfile(total, len(values), discarded, median, p10, p90,
                          robust_jitter, outbound, arrivals, fires, quality)


def measure_xiaomi_path(client, cancel_event: threading.Event) -> NetworkProfile:
    """Warm four sessions, then collect exactly eight timed GET probes.

    No application POST is performed. Threads reflect the four independent
    channels used by the live scheduler without allowing an unbounded loop.
    """
    channels = [client.new_channel() for _ in range(4)]
    attempted = 0
    samples = []
    for measured_round in (False, True, True):
        if cancel_event.is_set():
            raise RuntimeError("Network measurement cancelled")
        round_results = []
        threads = []

        def probe(channel, sink):
            try:
                sink.append(channel.check_state())
            except Exception:
                sink.append((None, None))

        for channel in channels:
            thread = threading.Thread(target=probe, args=(channel, round_results), daemon=True)
            threads.append(thread)
            thread.start()
        deadline = time.monotonic() + 20.0
        for thread in threads:
            thread.join(max(0.0, deadline - time.monotonic()))
        if cancel_event.is_set():
            raise RuntimeError("Network measurement cancelled")
        for result, _ in list(round_results):
            if result and result.kind in (ResultKind.EXPIRED, ResultKind.INVALID):
                raise RuntimeError(result.message)
        if measured_round:
            attempted += 4
            for result, latency in list(round_results):
                if result and result.kind != ResultKind.NETWORK_ERROR and latency is not None:
                    samples.append(latency)
    return build_network_profile(samples, attempted=attempted)
