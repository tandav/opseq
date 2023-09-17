import abc
import itertools
from collections.abc import Iterable
from collections.abc import Generator
from collections.abc import Callable
from typing import Any
from concurrent.futures import ProcessPoolExecutor
import tqdm
from functools import partial

from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import CandidateConstraint
from opseq.types import IConstraint
from opseq import util


class OpSeqBase(abc.ABC):
    def __init__(
        self,
        n: int,
        generator: Callable,
        lookback_constraint: LookbackConstraint[Op] | None = None,
        # curr_prev_constraint: CurrPrevConstraint[Op] | None = None,
        # candidate_constraint: CandidateConstraint[Op] | None = None,
        # i_constraints: IConstraint[Op] | None = None,
        # unique_key: Callable[[Op], Any] | None = None,
        prefix: tuple[Op, ...] = (),
        # loop: bool = False,
    ):
        # arg validation
        if lookback_constraint is not None:
            generator = util.lookback_constraint(lookback_constraint)(generator)
        # if curr_prev_constraint is not None:
        #     if any(k >= 0 for k in curr_prev_constraint):
        #         raise KeyError('curr_prev_constraint keys must be negative')
        #     if abs(max(curr_prev_constraint.keys())) >= n:
        #         raise IndexError('max index to look back in curr_prev_constraint should be less than n')

        # attributes
        self.n = n
        self.generator = generator
        # self.curr_prev_constraint = curr_prev_constraint
        # self.candidate_constraint = candidate_constraint
        # self.i_constraints = i_constraints
        # self.unique_key = unique_key
        self.prefix = prefix
        # self.loop = loop

    # @abc.abstractmethod
    # def generate_options(self, seq: tuple[Op, ...]) -> Generator[Op, None, None]:
    #     ...

    def __iter__(self) -> Generator[tuple[Op, ...], None, None]:
        return self._iter(self.prefix)

    def _iter(self, prefix: tuple[Op, ...] = ()) -> Generator[tuple[Op, ...], None, None]:
        if len(prefix) == self.n:
            yield prefix
            return
        yield from itertools.chain.from_iterable(
            self._iter(seq)
            for seq in self.generator(prefix)
        )




        # seq = prefix or ()
    #     ops = self.generate_options(seq)
    #     ops = tuple(ops)
    #     map_func = partial(self._generate_candidates, seq=seq)
    #     if len(prefix) == len(self.prefix):
    #         it = tqdm.tqdm(map(map_func, ops), total=len(ops))
    #     else:
    #         it = map(map_func, ops)
    #     it = itertools.chain.from_iterable(it)
    #     yield from it

    # def _generate_candidates(self, op: Op, seq: tuple[Op, ...]) -> Iterable[tuple[Op, ...]]:
    #     def inner() -> Iterable[tuple[Op, ...]]:
    #         candidate = (*seq, op)
    #         if len(candidate) < self.n:
    #             yield from self._iter(prefix=candidate)
    #             return
    #         yield candidate
    #     return tuple(inner())
