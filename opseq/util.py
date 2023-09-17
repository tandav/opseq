import functools
from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import Constraint
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

def lookback_constraint(index: int, constraint: Constraint[Op]):
    # if any(k >= 0 for k in constraints):
        # raise KeyError('constraints keys must be negative')
    if index >= 0:
        raise KeyError('constraint index must be negative')
    def _lookback_constraint(generator):
        @functools.wraps(generator)
        def constrainted_gen(*args, **kwargs):
            for seq in generator(*args, **kwargs):
                if len(seq) == 1:
                    yield seq
                    continue
                if abs(index) > len(seq):
                    continue
                if not constraint(seq[index - 1], seq[-1]):
                    continue
                yield seq
        return constrainted_gen
    return _lookback_constraint
