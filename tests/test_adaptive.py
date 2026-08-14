import pytest
from app.scheduler.adaptive import fire_offsets_ms,latency_stats

def test_latency_calibration_and_adaptive_offsets():
    stats=latency_stats([220,240,242,244,300])
    assert stats.median_ms==242
    assert stats.outbound_ms==121
    assert fire_offsets_ms([-100,20,120,300],stats.outbound_ms)==[221,101,1,-179]

def test_quota_full_does_not_cancel_remaining_attempts():
    from app.xiaomi.parser import parse_apply
    result=parse_apply({"code":0,"data":{"apply_result":3}})
    assert result.kind.value=="QUOTA FULL"
    assert result.terminal is False
