import pytest
from opseq.exceptions import SeqLengthError
from opseq import OpSeq


def test_simple(generator1):
    assert list(OpSeq(2, generator1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_length(generator1):
    assert all(len(seq) == 2 for seq in OpSeq(2, generator1))


def gen1(seq):
    yield seq + (0, 1)

def gen2(seq):
    yield seq + (0, 1)


@pytest.mark.parametrize('n, generator, expected', [
    (2, gen1, [(0, 1)]),
    (3, gen1, SeqLengthError),
])
def test_seq_length_error(n, generator, expected):
    if expected is SeqLengthError:
        with pytest.raises(SeqLengthError):
            list(OpSeq(n, generator))
    else:
        assert list(OpSeq(n, generator)) == expected

# from __future__ import annotations

# import itertools
# from collections import Counter






# def identity(x):
#     return x


# def is_different_startswith(a: str, b: str) -> bool:
#     return a[0] != b[0]


# def is_equal_endswith(a: str, b: str) -> bool:
#     return a[1] == b[1]


# def even_odd_interchange(prev, curr):
#     return is_even(prev) ^ is_even(curr)


# def is_candidate_constraint(candidate: tuple[str, ...]) -> bool:
#     return Counter(candidate)['A'] < 3


# def options_callable_0(x):
#     return [x + 1]


# def options_callable_1(x):
#     return [x + 1, x * 10]


# @pytest.fixture
# def options() -> tuple[int, ...]:
#     return 0, 1, 2, 3





# def test_prev_curr(options):
#     for cycle in OpSeq(5, options=options, curr_prev_constraint={-1: even_odd_interchange}, loop=True):  # type: ignore[var-annotated]
#         assert even_odd_interchange(cycle[-1], cycle[0])
#         for prev, curr in itertools.pairwise(cycle):
#             assert even_odd_interchange(prev, curr)


# def test_loop():
#     assert all(  # type: ignore[var-annotated]
#         is_different_startswith(seq[0], seq[-1]) and is_equal_endswith(seq[1], seq[-1])
#         for seq in OpSeq(
#             4,
#             options=('A0', 'A1', 'C0', 'D0', 'D1'),
#             curr_prev_constraint={-1: is_different_startswith, -2: is_equal_endswith},
#             loop=True,
#         )
#     )


# @pytest.mark.parametrize('parallel', [False, True])
# def test_prefix(options, parallel):
#     prefix = options[:3]
#     assert all(seq[:len(prefix)] == prefix for seq in OpSeq(5, options=options, prefix=prefix, parallel=parallel))  # type: ignore[var-annotated]


# @pytest.mark.parametrize('parallel', [False, True])
# def test_unique(options, parallel):
#     assert all(len(seq) == len(set(seq)) for seq in OpSeq(4, options=options, unique_key=identity, parallel=parallel))  # type: ignore[var-annotated]
#     assert any(len(seq) != len(set(seq)) for seq in OpSeq(4, options=options, parallel=parallel))  # type: ignore[var-annotated]


# @pytest.mark.parametrize('parallel', [False, True])
# def test_candidate_constraint(parallel):
#     assert all(  # type: ignore[var-annotated]
#         is_candidate_constraint(seq)
#         for seq in OpSeq(
#             n=4,
#             options='AB',
#             candidate_constraint=is_candidate_constraint,
#             parallel=parallel,
#         )
#     )


# @pytest.mark.parametrize('parallel', [False, True])
# def test_options_kind_callable(parallel):
#     assert list(OpSeq(3, options_callable=options_callable_0, prefix=(0,), parallel=parallel)) == [(0, 1, 2)]
#     assert list(OpSeq(3, options_callable=options_callable_1, prefix=(0,), parallel=parallel)) == [(0, 1, 2), (0, 1, 10), (0, 0, 1), (0, 0, 0)]


# @pytest.mark.parametrize('parallel', [False, True])
# def test_options_i(parallel):
#     options_i = [{1, 10}, {2, 20}, {3, 30}]
#     assert all(  # type: ignore[var-annotated]
#         all(item in options_i[i] for i, item in enumerate(seq))
#         for seq in OpSeq(3, options_i=options_i, parallel=parallel)
#     )
#     with pytest.raises(ValueError):
#         OpSeq(3, options_i=options_i[:2], parallel=parallel)


# def test_parallel():
#     options_0 = 0, 1, 2, 3, 4, 5, 6, 7, 8
#     a = OpSeq(5, options=options_0, i_constraints={0: is_even})
#     b = OpSeq(5, options=options_0, i_constraints={0: is_even}, parallel=True)
#     assert tuple(a) == tuple(b)

#     options_1 = 'A0', 'A1', 'C0', 'D0', 'D1', 'G0'
#     a = OpSeq(5, options=options_1, curr_prev_constraint={-1: is_different_startswith, -2: is_equal_endswith})
#     b = OpSeq(5, options=options_1, curr_prev_constraint={-1: is_different_startswith, -2: is_equal_endswith}, parallel=True)
#     assert tuple(a) == tuple(b)
