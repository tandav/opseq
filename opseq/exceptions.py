# OPTIONS_EXCEPTION = TypeError('options, options_i, options_callable are mutually exclusive. Only 1 must be not None')


# class OptionsError(Exception):
#     pass


# class MultipleOptionsError(OptionsError):
#     def __init__(self, options: tuple[Op, ...]) -> None:
#         super().__init__(f'Only 1 of options, options_i, options_callable must be not None. options: {options}')


class SeqLengthError(ValueError):
    # the default argument keeps the exception picklable: pickle rebuilds an
    # exception as cls(*args), and args is the message passed to ValueError.
    # workers raise this across a process boundary, so it must round-trip.
    def __init__(self, message: str = 'generator generated sequence of length > n') -> None:
        super().__init__(message)
