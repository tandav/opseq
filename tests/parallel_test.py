"""parallel=True must produce exactly what the serial search produces, faster.

everything a worker touches is pickled, so the generators and constraints used
here are module level objects rather than lambdas.
"""
import operator
import os
import time

import pytest

from opseq import OpSeq
from opseq.__main__ import TASKS_PER_WORKER
from opseq.constraints import Lookback
from opseq.constraints import UniqueOp
from opseq.exceptions import SeqLengthError
from opseq.generators import AppendOp


def no_repeated_op(seq):
    return len(seq) == len(set(seq))


def starts_with_zero(seq):
    return seq[0] == 0


def sum_is_even(seq):
    return sum(seq) % 2 == 0


def variable_length_generator(seq):
    # extends by one op or by two, never past n=4
    yield (*seq, 0)
    if len(seq) + 2 <= 4:
        yield (*seq, 1, 1)


def overshoots_while_splitting(seq):
    yield (*seq, 0)
    yield (*seq, 1, 1)


def overshoots_below_the_split(seq):
    # short prefixes stay well formed, so the overshoot happens inside a worker
    # rather than while the parent is splitting the tree
    yield (*seq, 0)
    if len(seq) >= 3:
        yield (*seq, 1, 1)


def empty_generator(seq):
    return iter(())


CASES = [
    pytest.param({'n': 3, 'generator': AppendOp((0, 1, 2))}, id='plain'),
    pytest.param({'n': 4, 'generator': AppendOp('ab')}, id='non-int-ops'),
    pytest.param({'n': 3, 'generator': AppendOp(range(4)), 'constraints': [sum_is_even]}, id='constraints'),
    pytest.param({'n': 3, 'generator': AppendOp(range(4)), 'prefix_constraints': [no_repeated_op]}, id='prefix-constraints'),
    pytest.param({'n': 4, 'generator': AppendOp(range(3)), 'prefix': (1,), 'constraints': [starts_with_zero]}, id='prefix-filters-everything'),
    pytest.param({'n': 4, 'generator': AppendOp(range(4)), 'prefix': [0, 1]}, id='prefix'),
    pytest.param({'n': 4, 'generator': AppendOp(range(4)), 'prefix_constraints': Lookback.from_dict({-1: operator.ne}), 'constraints': [UniqueOp(key=abs)]}, id='library-constraints'),
    pytest.param({'n': 4, 'generator': variable_length_generator}, id='variable-length-generator'),
    pytest.param({'n': 0, 'generator': AppendOp((0, 1))}, id='n-zero'),
    pytest.param({'n': 3, 'generator': empty_generator}, id='empty-generator'),
]


@pytest.mark.parametrize('kwargs', CASES)
def test_parallel_matches_serial(kwargs):
    assert list(OpSeq(parallel=True, max_workers=2, **kwargs)) == list(OpSeq(**kwargs))


@pytest.mark.parametrize('max_workers', [1, 2, 3])
def test_parallel_matches_serial_for_any_worker_count(max_workers):
    generator = AppendOp(range(3))
    expected = list(OpSeq(4, generator))
    assert list(OpSeq(4, generator, parallel=True, max_workers=max_workers)) == expected


def test_parallel_uses_the_default_worker_count():
    generator = AppendOp((0, 1, 2))
    assert list(OpSeq(3, generator, parallel=True)) == list(OpSeq(3, generator))


def test_parallel_yields_every_seq_exactly_once():
    seqs = list(OpSeq(4, AppendOp(range(4)), parallel=True, max_workers=2))
    assert len(seqs) == len(set(seqs)) == 4 ** 4


def test_parallel_opseq_is_reiterable():
    opseq = OpSeq(3, AppendOp((0, 1)), parallel=True, max_workers=2)
    assert list(opseq) == list(opseq) == list(OpSeq(3, AppendOp((0, 1))))


def test_parallel_prefix_longer_than_n_raises():
    with pytest.raises(SeqLengthError):
        list(OpSeq(2, AppendOp((0, 1)), prefix=(0, 1, 0), parallel=True, max_workers=2))


def test_parallel_propagates_seq_length_error_raised_while_splitting():
    with pytest.raises(SeqLengthError):
        list(OpSeq(3, overshoots_while_splitting, parallel=True, max_workers=2))


def test_parallel_propagates_seq_length_error_raised_in_a_worker():
    # max_workers=1 keeps the split shallow, so the bad prefix is only reached
    # once a worker is already walking its subtree
    with pytest.raises(SeqLengthError):
        list(OpSeq(5, overshoots_below_the_split, parallel=True, max_workers=1))


def test_parallel_refills_the_in_flight_window():
    # one worker means a window of TASKS_PER_WORKER subtrees while the split
    # produces more than that, so the refill path has to run
    opseq = OpSeq(3, AppendOp(range(5)), parallel=True, max_workers=1)
    assert len(opseq._split(TASKS_PER_WORKER)) > TASKS_PER_WORKER
    assert list(opseq) == list(OpSeq(3, AppendOp(range(5))))


def test_parallel_supports_partial_consumption():
    # abandoning the iterator must shut the pool down instead of hanging
    opseq = OpSeq(4, AppendOp(range(4)), parallel=True, max_workers=2)
    assert next(iter(opseq)) == (0, 0, 0, 0)


# ==============================================================================
# speed
# ==============================================================================

WORK = 25_000


def cpu_heavy_constraint(seq):
    return sum(i * i for i in range(WORK)) >= 0


def _timed(opseq):
    start = time.perf_counter()
    seqs = list(opseq)
    return time.perf_counter() - start, seqs


@pytest.mark.slow
@pytest.mark.skipif((os.cpu_count() or 1) < 4, reason='needs at least 4 cpus to beat the process startup cost')
def test_parallel_is_faster_than_serial():
    generator = AppendOp(range(10))
    constraints = [cpu_heavy_constraint]

    serial_time, serial = _timed(OpSeq(3, generator, constraints=constraints))
    parallel_time, parallel = _timed(OpSeq(3, generator, constraints=constraints, parallel=True, max_workers=4))

    assert parallel == serial
    # measured ~2x on 4 workers; 0.75 leaves room for a busy machine
    assert parallel_time < serial_time * 0.75, f'serial={serial_time:.2f}s parallel={parallel_time:.2f}s'
