import pytest

from opseq import OpSeq
from opseq import constraints



@pytest.mark.parametrize('constraint_, expected', [
    (lambda seq: seq[0] != 0, [(1, 0), (1, 1)]),
])
def test_prefix_constraint(generator1, constraint_, expected):
    generator = constraints.prefix_constraint(constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected



# @pytest.mark.parametrize('constraint_, expected', [
#     (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
#     # (lambda seq: sum(seq) == 1, [(0, 1), (1, 0)]),
# ])
# def test_constraint(generator1, constraint_, expected):
#     generator = constraints.constraint(constraint_)(generator1)
#     assert list(OpSeq(2, generator)) == expected


# @pytest.mark.parametrize('key, expected', [
#     # (None, [(0, 0), (0, 1), (1, 1)]),
#     (sum, [(0, 0), (0, 1), (1, 1)]),
#     # (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
# ])
# def test_unique(generator1, key, expected):
#     generator = constraints.unique(key)(generator1)
#     assert list(OpSeq(2, generator)) == expected


@pytest.mark.parametrize('index, constraint_, expected', [
    (-1, lambda prev, curr: prev != curr, [(0, 1), (1, 0)]),
])
def test_lookback_constraint(generator1, index, constraint_, expected):
    generator = constraints.lookback_constraint(index, constraint_)(generator1)
    assert list(OpSeq(2, generator)) == expected
