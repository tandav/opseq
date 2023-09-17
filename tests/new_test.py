from functools import partial
from opseq import OpSeq
from opseq.util import lookback_constraint


def options0(seq, options):
    yield from options


options1 = partial(options0, options=[0, 1])


# @lookback_constraint(constraints={-1: lambda prev, curr: prev != curr})
# def options2(seq):
#     ops = [0, 1, 2, 3]
#     if len(seq) == 0:
#         yield from ops
#     else:


def test_simple():
    assert list(OpSeq(2, options1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_lookback_constraint():
    pass
