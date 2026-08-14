import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


class ConcurrentAttemptDispatcher:
    """Dispatch scheduled work without blocking the precision scheduler thread."""

    def __init__(self, total: int, work: Callable, on_result: Callable,
                 is_terminal: Callable, cancel_remaining: Callable, on_done: Callable):
        self.total = total
        self.work = work
        self.on_result = on_result
        self.is_terminal = is_terminal
        self.cancel_remaining = cancel_remaining
        self.on_done = on_done
        self._pool = ThreadPoolExecutor(max_workers=max(1, total), thread_name_prefix="xiaomi-request")
        self._lock = threading.Lock()
        self._submitted = 0
        self._completed = 0
        self._terminal = False
        self._done_sent = False

    def submit(self, attempt) -> bool:
        with self._lock:
            if self._terminal:
                return True
            self._submitted += 1
        self._pool.submit(self._run, attempt)
        return False

    def _run(self, attempt):
        result = self.work(attempt)
        terminal = self.is_terminal(result)
        should_done = False
        with self._lock:
            self._completed += 1
            if terminal and not self._terminal:
                self._terminal = True
                self.cancel_remaining()
            if not self._done_sent and (terminal or (self._submitted == self.total and self._completed == self._submitted)):
                self._done_sent = True
                should_done = True
        self.on_result(attempt, result)
        if should_done:
            self.on_done(result if terminal else None)

    def cancel(self):
        with self._lock:
            self._terminal = True
        self.cancel_remaining()

    def shutdown(self):
        self._pool.shutdown(wait=False, cancel_futures=True)
