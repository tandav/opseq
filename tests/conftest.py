import pytest
from functools import partial


def _generator(seq, options):
    for op in options:
        yield seq + (op,)

_generator1 = partial(_generator, options=[0, 1])
_generator2 = partial(_generator, options=['a', 'A', 'b'])
# _generator2 = partial(_generator, options=['a', 'A'])

@pytest.fixture
def generator1():
    return _generator1
