from functools import partial
from opseq import OpSeq
from opseq.util import lookback_constraint


def generator0(seq, options):
    for op in options:
        yield seq + (op,)


generator1 = partial(generator0, options=[0, 1])


# @lookback_constraint(constraints={-1: lambda prev, curr: prev != curr})
@lookback_constraint(-1, lambda prev, curr: prev != curr)
def generator2(seq):
    yield from generator1(seq)
    # ops = [0, 1, 2, 3]
    # for op in ops:
    #     yield seq + (op,)


def test_simple():
    assert list(OpSeq(2, generator1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_lookback_constraint():
    # assert list(OpSeq(2, generator1, lookback_constraint={-1: lambda prev, curr: prev != curr})) == [(0, 1), (1, 0)]
    assert list(OpSeq(2, generator2)) == [(0, 1), (1, 0)]
