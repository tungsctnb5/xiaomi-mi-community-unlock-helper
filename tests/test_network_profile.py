import math
import threading
from types import SimpleNamespace

import pytest

from app.scheduler.network_profile import build_network_profile,measure_xiaomi_path
from app.xiaomi.models import ResultKind


def test_stable_path_uses_compact_four_attempt_baseline():
    profile=build_network_profile([92,95,98,100,102,104,106,108],attempted=8)
    assert profile.quality=="STABLE"
    assert profile.usable==8
    assert profile.discarded==0
    assert profile.arrival_offsets_ms==(-100,20,120,300)
    assert len(profile.fire_offsets_ms)==4
    assert profile.fire_offsets_ms==tuple(profile.outbound_ms-value for value in profile.arrival_offsets_ms)


def test_variable_path_widens_attempts_while_remaining_finite():
    profile=build_network_profile([80,100,130,170,220,260,300,340],attempted=8)
    assert profile.quality=="UNSTABLE"
    assert profile.arrival_offsets_ms[0] <= -100
    assert profile.arrival_offsets_ms[1] >= 20
    assert profile.arrival_offsets_ms[2] >= 120
    assert profile.arrival_offsets_ms[3] > 300
    assert len(profile.arrival_offsets_ms)==4
    assert profile.arrival_offsets_ms==tuple(sorted(profile.arrival_offsets_ms))


def test_isolated_server_stall_is_discarded():
    profile=build_network_profile([90,92,94,96,98,100,102,4000],attempted=8)
    assert profile.usable==7
    assert profile.discarded==1
    assert profile.median_ms==96
    assert profile.arrival_offsets_ms==(-100,20,120,300)


@pytest.mark.parametrize("samples", [[],[100,110,120],[math.nan,100,110,120],[0,100,110,120]])
def test_requires_four_valid_samples(samples):
    with pytest.raises(ValueError,match="4 successful"):
        build_network_profile(samples)


def test_extreme_variability_is_bounded_and_never_creates_more_requests():
    profile=build_network_profile([10,20,50,200,800,1200,2000,5000],attempted=8)
    assert len(profile.arrival_offsets_ms)==4
    assert profile.arrival_offsets_ms[0] >= -320
    assert profile.arrival_offsets_ms[-1] <= 1200
    assert all(math.isfinite(value) for value in profile.fire_offsets_ms)


def test_measurement_is_four_warmups_plus_eight_gets_and_never_applies():
    calls=[]
    class Channel:
        def check_state(self):
            calls.append("GET")
            return SimpleNamespace(kind=ResultKind.VALID,message="valid"),100+len(calls)
        def apply(self):
            pytest.fail("Network measurement must never POST an application")
    class Client:
        def new_channel(self): return Channel()
    profile=measure_xiaomi_path(Client(),threading.Event())
    assert calls==["GET"]*12
    assert profile.attempted==8
    assert profile.usable==8
    assert len(profile.arrival_offsets_ms)==4


def test_measurement_stops_on_expired_session():
    class Channel:
        def check_state(self):
            return SimpleNamespace(kind=ResultKind.EXPIRED,message="Session expired — login again."),100
    class Client:
        def new_channel(self): return Channel()
    with pytest.raises(RuntimeError,match="Session expired"):
        measure_xiaomi_path(Client(),threading.Event())


def test_measurement_honors_cancel_before_next_round():
    cancelled=threading.Event(); cancelled.set()
    class Channel:
        def check_state(self): return SimpleNamespace(kind=ResultKind.VALID,message="valid"),100
    class Client:
        def new_channel(self): return Channel()
    with pytest.raises(RuntimeError,match="cancelled"):
        measure_xiaomi_path(Client(),cancelled)
