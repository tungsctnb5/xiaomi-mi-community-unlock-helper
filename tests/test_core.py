import json
import threading
import time
from datetime import datetime, timezone, timedelta
import pytest
import requests
from app.logging.redaction import mask_token,redact_text
from app.scheduler.clock import SyncedClock
from app.scheduler.engine import AttemptScheduler
from app.xiaomi.client import XiaomiClient
from app.xiaomi.models import ResultKind
from app.xiaomi.parser import parse_apply,parse_state

def test_redaction():
    token="abcdefghijkxyz"; out=redact_text(f"Cookie: new_bbs_serviceToken={token}; x=1")
    assert token not in out and "abcd****xyz" in out

@pytest.mark.parametrize("payload,kind",[
 ({"code":0,"data":{"apply_result":1}},ResultKind.SUCCESS),
 ({"code":0,"data":{"apply_result":3}},ResultKind.QUOTA_FULL),
 ({"code":0,"data":{"apply_result":4}},ResultKind.BLOCKED),
 ({"code":100004},ResultKind.EXPIRED),
])
def test_apply_mapping(payload,kind): assert parse_apply(payload).kind==kind

def test_state_mapping():
    assert parse_state({"code":0,"data":{"is_pass":4,"button_state":1}}).kind==ResultKind.VALID
    assert parse_state({"code":0,"data":{"is_pass":1}}).kind==ResultKind.AUTHORIZED
    assert parse_state({"code":100004}).message=="Session expired — login again."

class FakeNtp:
    offset=.0128; delay=.021; tx_time=time.time()+offset
def test_ntp_offset(monkeypatch):
    monkeypatch.setattr("ntplib.NTPClient.request",lambda *a,**k:FakeNtp())
    c=SyncedClock(); x=c.sync(("fake",),2); assert x.offset==pytest.approx(.0128) and x.delay==pytest.approx(.021)

def test_four_attempts_and_no_infinite_loop():
    c=SyncedClock(); c._mono=time.monotonic(); c._utc=time.time()
    scheduler=AttemptScheduler(c); seen=[]
    midnight=datetime.now(timezone.utc)+timedelta(milliseconds=70)
    scheduler.start((60,40,20,0),lambda a:seen.append(a) or False,midnight)
    scheduler.thread.join(1); assert [x.number for x in seen]==[1,2,3,4] and not scheduler.thread.is_alive()

def test_cancel():
    c=SyncedClock(); scheduler=AttemptScheduler(c); seen=[]
    scheduler.start((0,),lambda a:seen.append(a),datetime.now(timezone.utc)+timedelta(seconds=2)); scheduler.cancel(); scheduler.thread.join(1)
    assert seen==[]

def test_stop_after_success():
    c=SyncedClock(); seen=[]; scheduler=AttemptScheduler(c); midnight=datetime.now(timezone.utc)+timedelta(milliseconds=50)
    scheduler.start((40,20,0),lambda a:seen.append(a) or True,midnight); scheduler.thread.join(1); assert len(seen)==1

class FakeResponse:
    def __init__(self,payload): self.payload=payload; self.status_code=200; self.text=json.dumps(payload)
    def json(self): return self.payload
class FakeSession:
    def __init__(self,payload=None,error=None): self.payload=payload; self.error=error; self.calls=0
    def mount(self,*a,**k): pass
    def request(self,*a,**k):
        self.calls+=1
        if self.error: raise self.error
        return FakeResponse(self.payload)
def test_mock_quota_full():
    s=FakeSession({"code":0,"data":{"apply_result":3}}); r,_=XiaomiClient("fake","A"*40,s).apply(); assert r.kind==ResultKind.QUOTA_FULL and s.calls==1
def test_network_timeout():
    s=FakeSession(error=requests.Timeout("mock timeout")); r,_=XiaomiClient("fake","A"*40,s).apply(); assert r.kind==ResultKind.NETWORK_ERROR
