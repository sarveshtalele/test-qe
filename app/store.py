import threading

tasks_db: dict[int, dict] = {}
_lock = threading.Lock()
_counter = [0]


def next_id() -> int:
    with _lock:
        _counter[0] += 1
        return _counter[0]
