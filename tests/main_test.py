import pytest

from opseq import OpSeq
from opseq.exceptions import SeqLengthError
from opseq.generators import AppendOp


def test_simple(generator1):
    assert list(OpSeq(2, generator1)) == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_length(generator1):
    assert all(len(seq) == 2 for seq in OpSeq(2, generator1))


def gen1(seq):
    yield (*seq, 0, 1)


def gen2(seq):
    yield (*seq, 0, 1)


@pytest.mark.parametrize(
    ('n', 'generator', 'expected'), [
        (2, gen1, [(0, 1)]),
        (3, gen1, SeqLengthError),
    ],
)
def test_seq_length_error(n, generator, expected):
    if expected is SeqLengthError:
        with pytest.raises(SeqLengthError):
            list(OpSeq(n, generator))
    else:
        assert list(OpSeq(n, generator)) == expected


def test_prefix():
    options = 0, 1, 2, 3
    prefix = options[:3]
    assert all(seq[:len(prefix)] == prefix for seq in OpSeq(5, AppendOp(options), prefix=prefix))


def test_prefix_of_length_n_is_the_only_seq():
    assert list(OpSeq(2, AppendOp([0, 1]), prefix=(0, 1))) == [(0, 1)]


def test_prefix_longer_than_n_raises(generator1):
    with pytest.raises(SeqLengthError):
        list(OpSeq(2, generator1, prefix=(0, 1, 0)))


def test_prefix_is_coerced_to_tuple(generator1):
    assert list(OpSeq(2, generator1, prefix=[0])) == [(0, 0), (0, 1)]


def test_n_zero_yields_the_empty_seq(generator1):
    assert list(OpSeq(0, generator1)) == [()]


def test_empty_prefix_skips_prefix_constraints(generator1):
    # the empty prefix is never passed to prefix_constraints, so n=0 yields () regardless
    assert list(OpSeq(0, generator1, prefix_constraints=[lambda seq: False])) == [()]


def test_prefix_constraints_see_every_prefix_including_complete_seqs(generator1):
    seen = []

    def record(seq):
        seen.append(seq)
        return True

    list(OpSeq(2, generator1, prefix_constraints=[record]))
    assert seen == [(0,), (0, 0), (0, 1), (1,), (1, 0), (1, 1)]


def test_constraints_see_only_complete_seqs(generator1):
    seen = []

    def record(seq):
        seen.append(seq)
        return True

    list(OpSeq(2, generator1, constraints=[record]))
    assert seen == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_multiple_constraints_all_must_pass():
    generator = AppendOp([0, 1, 2])
    assert list(OpSeq(2, generator, constraints=[lambda seq: seq[0] == 0, lambda seq: seq[1] == 2])) == [(0, 2)]


def test_multiple_prefix_constraints_all_must_pass():
    generator = AppendOp([0, 1, 2])
    assert list(OpSeq(2, generator, prefix_constraints=[lambda seq: seq[0] == 0, lambda seq: seq[-1] != 1])) == [(0, 0), (0, 2)]


def test_generator_yielding_nothing():
    assert list(OpSeq(2, lambda seq: iter(()))) == []


def test_generator_may_yield_non_tuples():
    def list_generator(seq):
        yield [*seq, 0]

    assert list(OpSeq(2, list_generator)) == [(0, 0)]


def variable_length_generator(seq, n=3):
    yield (*seq, 0)
    if len(seq) + 2 <= n:
        yield (*seq, 1, 1)


def test_generator_may_extend_by_more_than_one_op():
    assert list(OpSeq(3, variable_length_generator)) == [(0, 0, 0), (0, 1, 1), (1, 1, 0)]


def test_generator_overshooting_n_raises():
    def overshooting_generator(seq):
        yield (*seq, 0)
        yield (*seq, 1, 1)

    with pytest.raises(SeqLengthError):
        list(OpSeq(3, overshooting_generator))


def test_opseq_is_reiterable(generator1):
    opseq = OpSeq(2, generator1)
    assert list(opseq) == list(opseq) == [(0, 0), (0, 1), (1, 0), (1, 1)]


# from __future__ import annotations

# from collections import Counter


# def is_candidate_constraint(candidate: tuple[str, ...]) -> bool:
#     return Counter(candidate)['A'] < 3


# def options_callable_0(x):
#     return [x + 1]


# def options_callable_1(x):
#     return [x + 1, x * 10]


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
