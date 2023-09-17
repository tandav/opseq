import pytest

from opseq import OpSeq
from opseq import constraints


def test_simple(generator1):
    assert list(OpSeq(2, generator1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


@pytest.mark.parametrize('constraint_, expected', [
    (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
])
def test_constraint(generator1, constraint_, expected):
    generator = constraints.constraint(constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected


# @pytest.mark.parametrize('constraint_, expected', [
#     (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
# ])
# def test_unique():
#     assert list(OpSeq(2, generator1, unique_key=lambda op: op)) == [(0, 1), (1, 0)]


@pytest.mark.parametrize('index, constraint_, expected', [
    (-1, lambda prev, curr: prev != curr, [(0, 1), (1, 0)]),
])
def test_lookback_constraint(generator1, index, constraint_, expected):
    generator = constraints.lookback_constraint(index, constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected
