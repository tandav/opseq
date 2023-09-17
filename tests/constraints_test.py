import pytest
import itertools
from opseq import OpSeq
from tests.conftest import _generator1
from tests.conftest import _generator2
# from opseq import constraints



@pytest.mark.parametrize('constraint, expected', [
    (lambda seq: seq[0] != 0, [(1, 0), (1, 1)]),
])
def test_prefix_constraints(generator1, constraint, expected):
    assert list(OpSeq(2, generator1, prefix_constraints=[constraint])) == expected


@pytest.mark.parametrize('constraint, expected', [
    (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
    (lambda seq: sum(seq) == 1, [(0, 1), (1, 0)]),
])
def test_constraint(generator1, constraint, expected):
    assert list(OpSeq(2, generator1, constraints=[constraint])) == expected


@pytest.mark.parametrize('generator, key, expected', [
    (_generator1, sum, [(0, 0), (0, 1), (1, 1)]),
    (_generator1, frozenset, [(0, 0), (0, 1), (1, 1)]),
    (_generator1, None, [(0, 0), (0, 1), (1, 0), (1, 1)]),
    (_generator2, None, [(0, 0), (0, 1), (1, 0), (1, 1)]),
])
def test_unique_key_seq(generator, key, expected):
    assert list(OpSeq(2, generator, unique_key_seq=key)) == expected


# @pytest.mark.parametrize('index, constraint, expected', [
#     (-1, lambda prev, curr: prev != curr, [(0, 1), (1, 0)]),
# ])
# def test_lookback_constraint(generator1, index, constraint, expected):
#     generator = constraints.lookback_constraint(index, constraint)(generator1)
#     assert list(OpSeq(2, generator)) == expected


