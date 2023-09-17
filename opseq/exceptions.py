OPTIONS_EXCEPTION = TypeError('options, options_i, options_callable are mutually exclusive. Only 1 must be not None')


class OptionsError(Exception):
    pass


class MultipleOptionsError(OptionsError):
    def __init__(self, options: tuple[Op, ...]) -> None:
        super().__init__(f'Only 1 of options, options_i, options_callable must be not None. options: {options}')
