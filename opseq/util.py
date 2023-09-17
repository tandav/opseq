import functools
from opseq.types import Op
from opseq.types import LookbackConstraint
from collections.abc import Callable


def lookback_constraint(
    seq: tuple[Op, ...],
    # prefix: tuple[Op, ...],
    # op: Op,
    constraints: LookbackConstraint[Op],
) -> Op:
    if any(k >= 0 for k in constraints):
        raise KeyError('constraints keys must be negative')
    for k, f in constraints.items():
        if abs(k) > len(seq):
            continue
        # ops = [op for op in ops if f(seq[k], op)]

def lookback_constraint(constraints: LookbackConstraint[Op]):
    def decorator_repeat(func):
        @functools.wraps(func)
        def constrainted_gen(*args, **kwargs):
            for _ in range(constraints):
                value = func(*args, **kwargs)
            return value
        return constrainted_gen
    return decorator_repeat
