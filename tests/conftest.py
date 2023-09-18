import pytest

from opseq.generators import AppendOp


@pytest.fixture
def generator1():
    return AppendOp(options=[0, 1])


