import functools
from opseq.types import Op
from opseq.types import Constraint
from opseq.types import UniqueKey



def prefix_constraint(constraint: Constraint[Op]):
    def _constraint(generator):
        @functools.wraps(generator)
        def constrainted_gen(*args, **kwargs):
            for seq in generator(*args, **kwargs):
                print(seq, constraint(seq))
                if not constraint(seq):
                    continue
                yield seq
        return constrainted_gen
    return _constraint


def constraint(constraint: Constraint[Op]):
    return prefix_constraint(lambda seq
    def _constraint(generator):
        @functools.wraps(generator)
        def constrainted_gen(*args, **kwargs):
            for seq in generator(*args, **kwargs):
                if not constraint(seq):
                    continue
                yield seq
        return constrainted_gen
    return _constraint


def unique(key: UniqueKey[Op] | None = None):
    if key is None:
        return prefix_constraint(lambda seq: len(seq) == len(set(seq)))
    return prefix_constraint(lambda seq: len(seq) == len(set(map(key, seq))))


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
