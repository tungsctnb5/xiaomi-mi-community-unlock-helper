import hashlib
import json
import secrets
import time
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from .models import ApiResult, ResultKind
from .parser import parse_apply, parse_state

BASE = "https://sgp-api.buy.mi.com/bbs/api/global"

def stable_device_id(storage: Path) -> str:
    storage.parent.mkdir(parents=True, exist_ok=True)
    if storage.exists():
        value = storage.read_text().strip()
        if len(value) == 40: return value
    value = hashlib.sha1(secrets.token_bytes(32)).hexdigest().upper()
    storage.write_text(value)
    storage.chmod(0o600)
    return value

class XiaomiClient:
    def __init__(self, token: str, device_id: str, session=None):
        self.token, self.device_id = token, device_id
        self.session = session or requests.Session()
        self.session.mount("https://", HTTPAdapter(pool_connections=1, pool_maxsize=4, max_retries=0))
    @property
    def headers(self):
        return {"Cookie": f"new_bbs_serviceToken={self.token};versionCode=500411;versionName=5.4.11;deviceId={self.device_id};",
                "Content-Type":"application/json; charset=utf-8", "User-Agent":"okhttp/4.12.0", "Connection":"keep-alive",
                "Accept-Encoding":"gzip, deflate"}
    def _call(self, method, path, **kwargs):
        start=time.perf_counter()
        try:
            response=self.session.request(method, BASE+path, headers=self.headers, timeout=(3,15), **kwargs)
            latency=(time.perf_counter()-start)*1000
            try: payload=response.json()
            except Exception: payload={"http_status":response.status_code,"body":response.text[:1000]}
            return payload, latency
        except requests.RequestException as exc:
            return ApiResult(ResultKind.NETWORK_ERROR, f"Network error: {exc}", raw={}), (time.perf_counter()-start)*1000
    def warmup(self): return self._call("GET", "/user/bl-switch/state")
    def check_state(self):
        payload, latency=self._call("GET", "/user/bl-switch/state")
        return (payload if isinstance(payload,ApiResult) else parse_state(payload)), latency
    def apply(self):
        payload, latency=self._call("POST", "/apply/bl-auth", data=json.dumps({"is_retry":True},separators=(",",":")))
        return (payload if isinstance(payload,ApiResult) else parse_apply(payload)), latency

    def new_channel(self):
        """A separate keep-alive channel for one independently timed attempt."""
        return XiaomiClient(self.token, self.device_id)
