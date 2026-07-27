import pickle

from opseq.exceptions import SeqLengthError


def test_seq_length_error_has_a_default_message():
    assert str(SeqLengthError()) == 'generator generated sequence of length > n'


def test_seq_length_error_survives_pickling():
    # workers raise it across a process boundary, so pickle must be able to
    # rebuild it from its args
    restored = pickle.loads(pickle.dumps(SeqLengthError()))
    assert isinstance(restored, SeqLengthError)
    assert str(restored) == str(SeqLengthError())
