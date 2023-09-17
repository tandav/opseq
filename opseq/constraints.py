import functools
from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import Constraint
from collections.abc import Callable


def constraint(constraint: Constraint[Op]):
    def _constraint(generator):
        @functools.wraps(generator)
        def constrainted_gen(*args, **kwargs):
            for seq in generator(*args, **kwargs):
                if not constraint(seq):
                    continue
                yield seq
        return constrainted_gen
    return _constraint


def lookback_constraint(index: int, constraint: Constraint[Op]):
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