import pytest
from opseq import OpSeq
from tests.conftest import Generator


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


@pytest.mark.parametrize('key, expected', [
    (sum, [(0, 0), (0, 1), (1, 1)]),
    (frozenset, [(0, 0), (0, 1), (1, 1)]),
    (lambda seq: seq, [(0, 0), (0, 1), (1, 0), (1, 1)]),
])
def test_unique_key_seq(generator1, key, expected):
    opseq = OpSeq(2, generator1, unique_key_seq=key)
    assert list(opseq) == expected
    assert list(opseq) == expected  # test multiple iterations give same result


@pytest.mark.parametrize('generator, key, expected', [
    (Generator([0, 1]), lambda op: op, [(0, 1), (1, 0)]),
    (Generator(['a', 'b']), str.lower, [('a', 'b'), ('b', 'a')]),
    (Generator(['a', 'A', 'b']), str.lower, [('a', 'b'), ('A', 'b'), ('b', 'a'), ('b', 'A')]),
    (Generator(['a', 'A']), str.lower, []),
])
def test_unique_key_op(generator, key, expected):
    assert list(OpSeq(2, generator, unique_key_op=key)) == expected


# @pytest.mark.parametrize('index, constraint, expected', [
#     (-1, lambda prev, curr: prev != curr, [(0, 1), (1, 0)]),
# ])
# def test_lookback_constraint(generator1, index, constraint, expected):
#     generator = constraints.lookback_constraint(index, constraint)(generator1)
#     assert list(OpSeq(2, generator)) == expected


