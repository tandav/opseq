import pytest
from opseq import OpSeq
from opseq.generators import AppendOp
from opseq import constraints as constraints_

def identity(x):
    return x

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
    (AppendOp([0, 1]), identity, [(0, 1), (1, 0)]),
    (AppendOp(['a', 'b']), str.lower, [('a', 'b'), ('b', 'a')]),
    (AppendOp(['a', 'A', 'b']), str.lower, [('a', 'b'), ('A', 'b'), ('b', 'a'), ('b', 'A')]),
    (AppendOp(['a', 'A']), str.lower, []),
    (AppendOp([['a'], ['A'], ['b']]), lambda op: op[0].lower(), [(['a'], ['b']), (['A'], ['b']), (['b'], ['a']), (['b'], ['A'])]),
])
def test_unique_key_op(generator, key, expected):
    results = list(OpSeq(2, generator, unique_key_op=key))
    results_no_unique = list(OpSeq(2, generator))
    assert results == expected
    assert all(len(seq) == len(set(map(key, seq))) for seq in results)
    assert any(len(seq) != len(set(map(key, seq))) for seq in results_no_unique)



@pytest.mark.parametrize('constraints, expected', [
    ({-1: lambda prev, curr: prev != curr}, [(0, 1), (1, 0)]),
    ({-1: lambda prev, curr: prev == curr}, [(0, 0), (1, 1)]),
])
def test_lookback_constraint(generator1, constraints, expected):
    assert list(OpSeq(2, generator1, lookback_constraints=constraints)) == expected

def is_even(x: int) -> bool:
    return x % 2 == 0


def test_len_constraint():
    opseq = OpSeq(4, generator=AppendOp([0, 1, 2]), constraints=constraints_.LenConstraint.from_dict({0: is_even}))
    assert all(is_even(seq[0]) for seq in opseq)

