import pytest

from opseq.generators import AppendOp


@pytest.mark.parametrize(
    ('options', 'seq', 'expected'), [
        ([0, 1], (), [(0,), (1,)]),
        ([0, 1], (9,), [(9, 0), (9, 1)]),
        ('ab', (), [('a',), ('b',)]),
        (range(3), (), [(0,), (1,), (2,)]),
        ([], (), []),
        ([], (9,), []),
        ([[0], [1]], (), [([0],), ([1],)]),
    ],
)
def test_append_op(options, seq, expected):
    assert list(AppendOp(options)(seq)) == expected


def test_append_op_extends_by_one_op():
    seq = ('a', 'b', 'c')
    assert all(len(new) == len(seq) + 1 and new[:len(seq)] == seq for new in AppendOp('xy')(seq))


def test_append_op_is_reusable():
    generator = AppendOp([0, 1])
    assert list(generator(())) == list(generator(())) == [(0,), (1,)]


def test_append_op_exhausts_iterator_options():
    # options are iterated on every call, so a one-shot iterator yields nothing the second time
    generator = AppendOp(iter([0, 1]))
    assert list(generator(())) == [(0,), (1,)]
    assert list(generator(())) == []
