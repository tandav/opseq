from __future__ import annotations

import itertools
import pickle
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Any
from typing import TypeVar
from opseq.base import OpSeqBase
import tqdm
from opseq.types import Op


class OpSeqOptions(OpSeqBase):
    def __init__(
        self,
        *,
        options: Iterable[Op],
        **kwargs,
    ):
        options_seq = tuple(options)
        if len(options_seq) != len(frozenset(options_seq)):
            raise ValueError('options should be unique')
        self.options = options
        super().__init__(**kwargs)
    
    def generate_options(self, seq: tuple[Op, ...]) -> Generator[Op, None, None]:
        yield from self.options


# TODO: merge options_i and options_callable into options_callable (options_callable should also take index as arguement)
# TODO: try also merge curr_prev_constraint, candidate_constraint, i_constraints into a single constraint function

class OpSeq(OpSeqBase):
    def __init__(  # noqa: C901
        self,
        n: int,
        options: OpsIterable[Op] | None = None,
        options_i: OpsFixedPerStep[Op] | None = None,
        options_callable: OpsCallableFromCurr[Op] | None = None,
        options_callable_no_args: OpsCallableNoArgs[Op] | None = None,
        curr_prev_constraint: dict[int, Callable[[Op, Op], bool]] | None = None,
        candidate_constraint: Callable[[tuple[Op, ...]], bool] | None = None,
        i_constraints: dict[int, Callable[[Op], bool]] | None = None,
        unique_key: Callable[[Op], Any] | None = None,
        prefix: tuple[Op, ...] = (),
        *,
        loop: bool = False,
        parallel: bool = False,
    ) -> None:

        self.n = n
        self.options: tuple[Op, ...] | None
        self.options_i: OpsFixedPerStep[Op] | None
        self.options_callable: OpsCallableFromCurr[Op] | None
        self.generate_options: Callable[[tuple[Op, ...]], Iterable[Op]]

        if options is not None:
            if not (options_i is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            options_seq = tuple(options)
            if len(options_seq) != len(frozenset(options_seq)):
                raise ValueError('options should be unique')
            self.options = options_seq
            self.generate_options = self._generate_options_iterable
        elif options_i is not None:
            if not (options is None and options_callable is None):
                raise OPTIONS_EXCEPTION
            if len(options_i) != n:
                raise ValueError('options_i should have options for each step up to n')
            self.options = options
            self.generate_options = self._generate_options_fixed_per_step
        elif options_callable is not None:
            if not (options is None and options_i is None):
                raise OPTIONS_EXCEPTION
            self.options = options
            self.generate_options = self._generate_options_callable_from_curr
        self.options_i = options_i
        self.options_callable = options_callable

        if curr_prev_constraint is not None and not all(k < 0 for k in curr_prev_constraint):
            raise KeyError('curr_prev_constraint keys must be negative')
        self.curr_prev_constraint = curr_prev_constraint
        self.candidate_constraint = candidate_constraint
        self.i_constraints = i_constraints
        self.unique_key = unique_key
        self.loop = loop
        self.prefix = prefix
        self.parallel = parallel

    def _generate_options_iterable(self, seq: tuple[Op, ...]) -> Iterable[Op]:  # noqa: ARG002 # pylint: disable=unused-argument
        if self.options is not None:
            return self.options
        raise TypeError

    def _generate_options_fixed_per_step(self, seq: tuple[Op, ...]) -> Iterable[Op]:
        if self.options_i is not None:
            return self.options_i[len(seq)]
        raise TypeError

    def _generate_options_callable_from_curr(self, seq: tuple[Op, ...]) -> Iterable[Op]:
        if self.options_callable is not None:
            return self.options_callable(seq[-1])
        raise TypeError
