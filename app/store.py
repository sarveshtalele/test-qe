tasks: dict[int, dict] = {}
_next_id: int = 1


def next_id() -> int:
    global _next_id
    n = _next_id
    _next_id += 1
    return n
