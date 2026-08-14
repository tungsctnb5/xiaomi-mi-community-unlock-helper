import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import ntplib

SERVERS=("time.apple.com","time.cloudflare.com","pool.ntp.org","ntp0.ntp-servers.net")

@dataclass
class ClockSample:
    offset: float
    delay: float
    server: str

class SyncedClock:
    def __init__(self): self.offset=0.0; self.delay=0.0; self.server="system"; self._mono=time.monotonic(); self._utc=time.time()
    def sync(self, servers=SERVERS, samples=2):
        found=[]
        for server in servers:
            for _ in range(samples):
                try:
                    r=ntplib.NTPClient().request(server,version=3,timeout=1.5)
                    found.append(ClockSample(r.offset,r.delay,server))
                except Exception: pass
        if not found: raise RuntimeError("No NTP server responded")
        best=sorted(found,key=lambda x:x.delay)[:max(1,min(3,len(found)))]
        self.offset=statistics.median(x.offset for x in best); self.delay=min(x.delay for x in best); self.server=min(best,key=lambda x:x.delay).server
        self._mono=time.monotonic(); self._utc=time.time()+self.offset
        return ClockSample(self.offset,self.delay,self.server)
    def timestamp(self): return self._utc+(time.monotonic()-self._mono)
    def utc_now(self): return datetime.fromtimestamp(self.timestamp(),timezone.utc)
    def beijing_now(self): return self.utc_now().astimezone(timezone(timedelta(hours=8)))
    def monotonic_for(self, utc_timestamp): return time.monotonic()+(utc_timestamp-self.timestamp())

def next_beijing_midnight(clock: SyncedClock):
    now=clock.beijing_now(); nxt=(now+timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
    return nxt
