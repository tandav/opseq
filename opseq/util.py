def lookback_(seq: tuple[Op, ...], k: int) -> Op:
    if k >= 0:
        raise ValueError('k must be negative')
    return seq[-k]
