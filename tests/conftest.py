import pytest
from functools import partial


def generator0(seq, options):
    for op in options:
        yield seq + (op,)


@pytest.fixture
def generator1():
    return partial(generator0, options=[0, 1])
