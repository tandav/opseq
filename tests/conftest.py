import pytest


class Generator:
    def __init__(self, options):
        self.options = options
    
    def __call__(self, seq):
        for op in self.options:
            yield seq + (op,)


@pytest.fixture
def generator1():
    return Generator([0, 1])
