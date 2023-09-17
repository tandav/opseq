import pytest

from functools import partial
from opseq import OpSeq
from opseq.util import constraint
from opseq.util import lookback_constraint


def generator0(seq, options):
    for op in options:
        yield seq + (op,)


generator1 = partial(generator0, options=[0, 1])


def test_simple():
    assert list(OpSeq(2, generator1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


@pytest.mark.parametrize('constraint_, expected', [
    (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
])
def test_constraint(constraint_, expected):
    generator = constraint(constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected


@pytest.mark.parametrize('index, constraint_, expected', [
    (-1, lambda prev, curr: prev != curr, [(0, 1), (1, 0)]),
])
def test_lookback_constraint(index, constraint_, expected):
    generator = lookback_constraint(index, constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected
