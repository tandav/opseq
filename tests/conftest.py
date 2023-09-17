import pytest
# from functools import partial


class Generator:
    def __init__(self, options):
        self.options = options
    
    def __call__(self, seq):
        for op in self.options:
            yield seq + (op,)

# def _generator(seq, options):
    # for op in options:
        # yield seq + (op,)

_generator1 = Generator([0, 1])
_generator2 = Generator(['a', 'A', 'b'])
# _generator2 = partial(_generator, options=['a', 'A'])

@pytest.fixture
def generator1():
    return _generator1
