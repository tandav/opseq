import itertools

import pytest

from opseq import OpSeq
from opseq import constraints as constraints_
from opseq.generators import AppendOp


def is_even(x: int) -> bool:
    return x % 2 == 0


def identity(x):
    return x


def is_different_startswith(a: str, b: str) -> bool:
    return a[0] != b[0]


def is_equal_endswith(a: str, b: str) -> bool:
    return a[1] == b[1]


def even_odd_interchange(prev, curr):
    return is_even(prev) ^ is_even(curr)


def not_equal(prev, curr):
    return prev != curr


def never(prev, curr):
    return False


@pytest.mark.parametrize(
    ('constraint', 'expected'), [
        (lambda seq: seq[0] != 0, [(1, 0), (1, 1)]),
    ],
)
def test_prefix_constraints(generator1, constraint, expected):
    assert list(OpSeq(2, generator1, prefix_constraints=[constraint])) == expected


@pytest.mark.parametrize(
    ('constraint', 'expected'), [
        (lambda seq: seq != (0, 0), [(0, 1), (1, 0), (1, 1)]),
        (lambda seq: sum(seq) == 1, [(0, 1), (1, 0)]),
    ],
)
def test_constraint(generator1, constraint, expected):
    assert list(OpSeq(2, generator1, constraints=[constraint])) == expected


@pytest.mark.parametrize(
    ('generator', 'key', 'expected'), [
        (AppendOp([0, 1]), identity, [(0, 1), (1, 0)]),
        (AppendOp(['a', 'b']), str.lower, [('a', 'b'), ('b', 'a')]),
        (AppendOp(['a', 'A', 'b']), str.lower, [('a', 'b'), ('A', 'b'), ('b', 'a'), ('b', 'A')]),
        (AppendOp(['a', 'A']), str.lower, []),
        (AppendOp([['a'], ['A'], ['b']]), lambda op: op[0].lower(), [(['a'], ['b']), (['A'], ['b']), (['b'], ['a']), (['b'], ['A'])]),
    ],
)
def test_unique_key_op(generator, key, expected):
    results = list(OpSeq(2, generator, prefix_constraints=[constraints_.UniqueOp(key)]))
    results_no_unique = list(OpSeq(2, generator))
    assert results == expected
    assert all(len(seq) == len(set(map(key, seq))) for seq in results)
    assert any(len(seq) != len(set(map(key, seq))) for seq in results_no_unique)


@pytest.mark.parametrize(
    ('opseq', 'expected'), [
        (
            OpSeq(2, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({-1: lambda prev, curr: prev != curr})),
            [(0, 1), (1, 0)],
        ),
        (
            OpSeq(2, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({-1: lambda prev, curr: prev == curr})),
            [(0, 0), (1, 1)],
        ),
        (
            OpSeq(
                3, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({
                    -1: lambda prev, curr: prev != curr,
                    -2: lambda prev, curr: prev == curr,
                }),
            ),
            [(0, 1, 0), (1, 0, 1)],
        ),
        (
            OpSeq(
                3, AppendOp(options=[0, 1]), prefix_constraints=constraints_.Lookback.from_dict({
                    -1: lambda prev, curr: prev == curr,
                    -2: lambda prev, curr: prev == curr,
                }),
            ),
            [(0, 0, 0), (1, 1, 1)],
        ),
        (
            OpSeq(
                3, AppendOp(options=[0, 1, 2]), prefix_constraints=constraints_.Lookback.from_dict({
                    -1: lambda prev, curr: prev != curr,
                    -2: lambda prev, curr: prev != curr,
                }),
            ),
            [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)],
        ),
    ],
)
def test_lookback_constraint(opseq, expected):
    assert list(opseq) == expected


@pytest.mark.parametrize(
    ('opseq', 'expected'), [
        (
            OpSeq(
                3,
                AppendOp(options=[0, 1, 2]),
                prefix_constraints=constraints_.Lookback.from_dict(
                    {
                        -1: lambda prev, curr: prev != curr,
                        -2: lambda prev, curr: prev != curr,
                    }, loop=True,
                ),
            ),
            [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)],
        ),
    ],
)
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


@pytest.mark.parametrize('index', [0, 1, 5])
def test_lookback_positive_index_raises(index):
    with pytest.raises(KeyError):
        constraints_.Lookback(index, not_equal)


@pytest.mark.parametrize('loop', [False, True])
@pytest.mark.parametrize(
    ('index', 'seq'), [
        (-1, (0,)),
        (-2, (0,)),
        (-2, (0, 0)),
        (-3, (0, 0, 0)),
    ],
)
def test_lookback_is_vacuously_true_for_short_seqs(index, seq, loop):
    assert constraints_.Lookback(index, never, loop=loop)(seq)


@pytest.mark.parametrize(
    ('index', 'seq', 'expected'), [
        (-1, (0, 1), True),
        (-1, (0, 0), False),
        (-1, (0, 0, 1), True),  # only the last pair is checked, the (0, 0) prefix is somebody else's problem
        (-2, (0, 1, 2), True),
        (-2, (0, 1, 0), False),
        (-2, (0, 0, 1, 0), False),
    ],
)
def test_lookback_compares_last_op_with_the_one_index_back(index, seq, expected):
    assert constraints_.Lookback(index, not_equal)(seq) is expected


@pytest.mark.parametrize(
    ('index', 'seq', 'expected'), [
        (-1, (0, 1, 2), True),
        (-1, (0, 1, 0), False),
        (-1, (5, 5, 5, 1), True),  # interior pairs are not checked in loop mode
        (-2, (0, 1, 2, 3), True),
        (-2, (0, 1, 0, 3), False),
        (-2, (0, 1, 2, 1), False),
    ],
)
def test_lookback_loop_checks_only_the_wraparound_pairs(index, seq, expected):
    assert constraints_.Lookback(index, not_equal, loop=True)(seq) is expected


def test_lookback_loop_alone_does_not_constrain_interior_pairs():
    seqs = list(OpSeq(3, AppendOp([0, 1]), constraints=constraints_.Lookback.from_dict({-1: not_equal}, loop=True)))
    assert all(seq[-1] != seq[0] for seq in seqs)
    assert any(seq[0] == seq[1] for seq in seqs)


@pytest.mark.parametrize('loop', [False, True])
def test_lookback_from_dict(loop):
    lookbacks = constraints_.Lookback.from_dict({-1: not_equal, -3: never}, loop=loop)
    assert [(lookback.index, lookback.constraint, lookback.loop) for lookback in lookbacks] == [(-1, not_equal, loop), (-3, never, loop)]


def test_lookback_from_dict_empty():
    assert constraints_.Lookback.from_dict({}) == []


def test_lookback_from_dict_defaults_to_no_loop():
    assert all(not lookback.loop for lookback in constraints_.Lookback.from_dict({-1: not_equal}))


@pytest.mark.parametrize(
    ('seq', 'expected'), [
        ((), True),
        ((1,), True),
        ((1, 2), True),
        ((1, 1), False),
        ((1, 2, 1), False),
    ],
)
def test_unique_op(seq, expected):
    assert constraints_.UniqueOp(identity)(seq) is expected


def test_unique_op_uses_the_key():
    assert constraints_.UniqueOp(str.lower)(('a', 'A')) is False
    assert constraints_.UniqueOp(identity)(('a', 'A')) is True


def test_unique_op_requires_hashable_keys():
    with pytest.raises(TypeError):
        constraints_.UniqueOp(identity)(([0], [1]))


def test_unique_op_placement_does_not_change_results():
    generator = AppendOp([0, 1, 2])
    unique = constraints_.UniqueOp(identity)
    expected = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    assert list(OpSeq(2, generator, constraints=[unique])) == expected
    assert list(OpSeq(2, generator, prefix_constraints=[unique])) == expected


def sum_is_one(seq):
    return sum(seq) == 1


def always_true(seq):
    return True


def test_len_constraint():
    opseq = OpSeq(3, AppendOp([0, 1]), constraints=constraints_.LenConstraint.from_dict({3: sum_is_one}))
    assert list(opseq) == [(0, 0, 1), (0, 1, 0), (1, 0, 0)]


@pytest.mark.parametrize(
    ('seq', 'expected'), [
        ((0, 1), True),
        ((1, 1), False),
        ((0, 0, 1), False),  # right sum, wrong length
        ((1,), False),
        ((), False),
    ],
)
def test_len_constraint_requires_the_exact_length(seq, expected):
    assert constraints_.LenConstraint(2, sum_is_one)(seq) is expected


@pytest.mark.parametrize('length', [0, 2, 4])
def test_len_constraint_of_other_length_rejects_everything(length):
    # LenConstraint is a conjunction, not an implication: a length mismatch fails outright
    opseq = OpSeq(3, AppendOp([0, 1]), constraints=[constraints_.LenConstraint[int](length, always_true)])
    assert list(opseq) == []


def test_len_constraint_as_prefix_constraint_rejects_every_shorter_prefix():
    opseq = OpSeq(3, AppendOp([0, 1]), prefix_constraints=[constraints_.LenConstraint[int](3, always_true)])
    assert list(opseq) == []


def test_len_constraint_from_dict():
    len_constraints = constraints_.LenConstraint.from_dict({2: sum_is_one, 3: identity})
    assert [(len_constraint.length, len_constraint.constraint) for len_constraint in len_constraints] == [(2, sum_is_one), (3, identity)]
