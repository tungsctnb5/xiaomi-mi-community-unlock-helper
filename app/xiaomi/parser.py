from .models import ApiResult, ResultKind

def parse_state(payload: dict) -> ApiResult:
    code = payload.get("code")
    data = payload.get("data") or {}
    if code == 100004:
        return ApiResult(ResultKind.EXPIRED, "Session expired — login again.", True, raw=payload)
    if code not in (0, None):
        kind = ResultKind.INVALID if code in (100001, 100002) else ResultKind.UNKNOWN
        return ApiResult(kind, f"Session/state error (code {code})", kind == ResultKind.INVALID, raw=payload)
    is_pass, button = data.get("is_pass"), data.get("button_state")
    deadline = str(data.get("deadline_format") or data.get("deadline") or "")
    if is_pass == 1:
        return ApiResult(ResultKind.AUTHORIZED, "Account authorization confirmed", True, deadline=deadline, raw=payload)
    if is_pass == 4 and button == 1:
        return ApiResult(ResultKind.VALID, "Session valid; application is eligible", raw=payload)
    if is_pass == 4 and button == 2:
        return ApiResult(ResultKind.BLOCKED, "Account application is blocked", True, deadline=deadline, raw=payload)
    if is_pass == 4 and button == 3:
        return ApiResult(ResultKind.NOT_ELIGIBLE, "Account is not eligible (community source: under 30 days)", True, raw=payload)
    return ApiResult(ResultKind.UNKNOWN, f"Unknown account state: is_pass={is_pass}, button_state={button}", raw=payload)

def parse_apply(payload: dict) -> ApiResult:
    code = payload.get("code")
    data = payload.get("data") or {}
    deadline = str(data.get("deadline_format") or data.get("deadline") or "")
    if code == 100004:
        return ApiResult(ResultKind.EXPIRED, "Session expired — login again.", True, raw=payload)
    if code == 100003:
        return ApiResult(ResultKind.SUCCESS, "Request may have been accepted; verifying account state", True, True, raw=payload)
    if code == 100001:
        return ApiResult(ResultKind.INVALID, "Request rejected by Xiaomi", True, raw=payload)
    if code == 0:
        result = data.get("apply_result")
        if result == 1:
            return ApiResult(ResultKind.SUCCESS, "Request accepted; verification required", True, True, deadline, payload)
        if result == 3:
            # A pre-reset request can observe the previous day's full quota. Do
            # not suppress later scheduled attempts; conclude after all finish.
            return ApiResult(ResultKind.QUOTA_FULL, "Daily application quota is full", False, deadline=deadline, raw=payload)
        if result == 4:
            return ApiResult(ResultKind.BLOCKED, "Account application is blocked", True, deadline=deadline, raw=payload)
        if result in (2, 5, 6):
            return ApiResult(ResultKind.NOT_ELIGIBLE, f"Application not eligible (apply_result={result})", True, deadline=deadline, raw=payload)
    return ApiResult(ResultKind.UNKNOWN, f"Unknown Xiaomi response (code={code}, apply_result={data.get('apply_result')})", raw=payload)
