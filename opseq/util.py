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
    if any(k >= 0 for k in constraints):
        raise KeyError('constraints keys must be negative')
    def _lookback_constraint(generator):
        @functools.wraps(generator)
        def constrainted_gen(*args, **kwargs):
            for seq in generator(*args, **kwargs):
                _constraints = {k: f for k, f in constraints.items() if abs(k) < len(seq)}
                for k, f in _constraints.items():
                    if not f(seq[k - 1], seq[-1]):
                        break
                else:
                    yield seq
        return constrainted_gen
    return _lookback_constraint
