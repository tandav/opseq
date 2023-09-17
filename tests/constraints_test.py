import itertools

import pytest
from opseq import OpSeq
from opseq.generators import AppendOp
from opseq import constraints as constraints_

def identity(x):
    return x

def is_different_startswith(a: str, b: str) -> bool:
    return a[0] != b[0]


def is_equal_endswith(a: str, b: str) -> bool:
    return a[1] == b[1]


def even_odd_interchange(prev, curr):
    return is_even(prev) ^ is_even(curr)


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
    (AppendOp([0, 1]), identity, [(0, 1), (1, 0)]),
    (AppendOp(['a', 'b']), str.lower, [('a', 'b'), ('b', 'a')]),
    (AppendOp(['a', 'A', 'b']), str.lower, [('a', 'b'), ('A', 'b'), ('b', 'a'), ('b', 'A')]),
    (AppendOp(['a', 'A']), str.lower, []),
    (AppendOp([['a'], ['A'], ['b']]), lambda op: op[0].lower(), [(['a'], ['b']), (['A'], ['b']), (['b'], ['a']), (['b'], ['A'])]),
])
def test_unique_key_op(generator, key, expected):
    results = list(OpSeq(2, generator, prefix_constraints=[constraints_.UniqueOp(key)]))
    results_no_unique = list(OpSeq(2, generator))
    assert results == expected
    assert all(len(seq) == len(set(map(key, seq))) for seq in results)
    assert any(len(seq) != len(set(map(key, seq))) for seq in results_no_unique)


@pytest.mark.parametrize('opseq, expected', [
    (
        OpSeq(2, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({-1: lambda prev, curr: prev != curr})), 
        [(0, 1), (1, 0)],
    ),
    (
        OpSeq(2, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({-1: lambda prev, curr: prev == curr})), 
        [(0, 0), (1, 1)],
    ),
    (
        OpSeq(3, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({
            -1: lambda prev, curr: prev != curr,
            -2: lambda prev, curr: prev == curr,
        })), 
        [(0, 1, 0), (1, 0, 1)],
    ),
    (
        OpSeq(3, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({
            -1: lambda prev, curr: prev == curr,
            -2: lambda prev, curr: prev == curr,
        })), 
        [(0, 0, 0), (1, 1, 1)],
    ),
    (
        OpSeq(3, AppendOp(options=[0, 1, 2]), prefix_constraints=constraints_.Lookback.from_dict({
            -1: lambda prev, curr: prev != curr,
            -2: lambda prev, curr: prev != curr,
        })), 
        [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)],
    ),
])
def test_lookback_constraint(opseq, expected):
    assert list(opseq) == expected


@pytest.mark.parametrize('opseq, expected', [
    (
        OpSeq(
            3, 
            AppendOp(options=[0, 1, 2]), 
            prefix_constraints=constraints_.Lookback.from_dict({
                -1: lambda prev, curr: prev != curr,
                -2: lambda prev, curr: prev != curr,
            },loop=True)
        ),
        [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)],
    ),
])
def test_lookback_constraint_loop1(opseq, expected):
    assert list(opseq) == expected


def test_lookback_constraint_loop2():
    opseq = OpSeq(
        4,
        AppendOp(options=('A0', 'A1', 'C0', 'D0', 'D1')),
        constraints=constraints_.Lookback.from_dict({-1: is_different_startswith, -2: is_equal_endswith}, loop=True),
    )
    assert all(
        is_different_startswith(seq[0], seq[-1]) and is_equal_endswith(seq[1], seq[-1])
        for seq in opseq
    )


def test_lookback_constraint_loop3():
    for seq in OpSeq(
        5, 
        AppendOp(range(4)),
        constraints=constraints_.Lookback.from_dict({-1: even_odd_interchange}, loop=True),
        prefix_constraints=constraints_.Lookback.from_dict({-1: even_odd_interchange}),
    ):
        assert even_odd_interchange(seq[-1], seq[0])
        for prev, curr in itertools.pairwise(seq):
            assert even_odd_interchange(prev, curr)


def is_even(x: int) -> bool:
    return x % 2 == 0


def test_len_constraint():
    opseq = OpSeq(4, generator=AppendOp([0, 1, 2]), constraints=constraints_.LenConstraint.from_dict({0: is_even}))
    assert all(is_even(seq[0]) for seq in opseq)

