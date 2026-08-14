import threading
import time
from datetime import datetime, timezone, timedelta
from app.scheduler.clock import SyncedClock
from app.scheduler.dispatcher import ConcurrentAttemptDispatcher
from app.scheduler.engine import AttemptScheduler

def test_slow_requests_do_not_delay_four_firings():
    clock=SyncedClock(); scheduler=AttemptScheduler(clock); fired=[]; results=[]; done=threading.Event()
    def work(attempt): time.sleep(.15); return False
    dispatcher=ConcurrentAttemptDispatcher(4,work,lambda a,r:results.append(a.number),bool,scheduler.cancel,lambda r:done.set())
    midnight=datetime.now(timezone.utc)+timedelta(milliseconds=90)
    def callback(attempt): fired.append((attempt.number,time.monotonic())); return dispatcher.submit(attempt)
    scheduler.start((75,50,25,0),callback,midnight); scheduler.thread.join(1); assert done.wait(1)
    assert [x[0] for x in fired]==[1,2,3,4]
    assert fired[-1][1]-fired[0][1] < .12
    assert sorted(results)==[1,2,3,4]
    dispatcher.shutdown()

def test_terminal_response_cancels_future_firings():
    clock=SyncedClock(); scheduler=AttemptScheduler(clock); fired=[]; done=threading.Event()
    dispatcher=ConcurrentAttemptDispatcher(4,lambda a: True,lambda a,r:None,bool,scheduler.cancel,lambda r:done.set())
    midnight=datetime.now(timezone.utc)+timedelta(milliseconds=300)
    scheduler.start((290,190,90,0),lambda a:fired.append(a.number) or dispatcher.submit(a),midnight)
    assert done.wait(1); scheduler.thread.join(1)
    assert fired==[1]
    dispatcher.shutdown()
