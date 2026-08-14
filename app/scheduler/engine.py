import threading
import time
from dataclasses import dataclass
from typing import Callable
from .clock import SyncedClock, next_beijing_midnight

@dataclass
class Attempt:
    number:int; offset_ms:float; target_wall:float; actual_wall:float; error_ms:float

class AttemptScheduler:
    def __init__(self, clock:SyncedClock): self.clock=clock; self._cancel=threading.Event(); self.thread=None
    def cancel(self): self._cancel.set()
    def start(self, offsets, callback:Callable[[Attempt],bool], midnight=None):
        if self.thread and self.thread.is_alive(): raise RuntimeError("Scheduler already running")
        self._cancel.clear(); midnight=midnight or next_beijing_midnight(self.clock)
        targets=[midnight.timestamp()-o/1000 for o in offsets]
        def run():
            for i,(offset,target) in enumerate(zip(offsets,targets),1):
                deadline=self.clock.monotonic_for(target)
                while not self._cancel.is_set():
                    left=deadline-time.monotonic()
                    if left<=0: break
                    self._cancel.wait(min(max(left-0.003,0.0002),0.25))
                if self._cancel.is_set(): break
                while time.monotonic()<deadline and not self._cancel.is_set(): pass
                actual=self.clock.timestamp(); attempt=Attempt(i,offset,target,actual,(actual-target)*1000)
                if callback(attempt): self._cancel.set(); break
        self.thread=threading.Thread(target=run,name="attempt-scheduler",daemon=True); self.thread.start(); return midnight
