import abc
import itertools
from collections.abc import Iterable
from collections.abc import Generator
from collections.abc import Callable
from typing import Any
from concurrent.futures import ProcessPoolExecutor
import tqdm
from functools import partial
from functools import partialmethod

from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import Seq
from opseq.types import Constraint
from opseq.types import UniqueKeyOp
from opseq.types import UniqueKeySeq
from opseq import constraints


class OpSeqBase(abc.ABC):
    def __init__(
        self,
        n: int,
        generator: Callable,
        constraints: Iterable[Constraint[Op]] = (),
        prefix_constraints: Iterable[Constraint[Op]] = (),
        # lookback_constraints: Iterable[LookbackConstraint[Op]] = (),
        # unique_key: Callable[[Op], Any] | None = None,
        unique_key_op: UniqueKeyOp[Op] | None = None,
        unique_key_seq: UniqueKeySeq[Op] | None = None,
        prefix: Seq[Op] = (),
        # loop: bool = False,
    ):
        # arg validation
        # if lookback_constraint is not None:
            # generator = util.lookback_constraint(lookback_constraint)(generator)
        # if curr_prev_constraint is not None:
        #     if any(k >= 0 for k in curr_prev_constraint):
        #         raise KeyError('curr_prev_constraint keys must be negative')
        #     if abs(max(curr_prev_constraint.keys())) >= n:
        #         raise IndexError('max index to look back in curr_prev_constraint should be less than n')

        # attributes
        self.n = n
        self.generator = generator
        self.constraints = list(constraints)
        self.prefix_constraints = list(prefix_constraints)
        # self.curr_prev_constraint = curr_prev_constraint
        # self.candidate_constraint = candidate_constraint
        # self.i_constraints = i_constraints
        self.unique_key_op = unique_key_op
        self.unique_key_seq = unique_key_seq

        if unique_key_seq is not None:
            # self.constraints.append(self.unique_seq_constraint)
            # self.constraints.append(partialmethod(self.unique_seq_constraint, key=unique_key_seq))
            self.constraints.append(partial(self.unique_seq_constraint, key=unique_key_seq))

        self.seen_keys = set()
        self.prefix = prefix
        # self.loop = loop

    # def unique_seq_constraint(self, seq: Seq[Op]) -> bool:
    #     if self.unique_key_seq is None:
    #         return True
    #     key = self.unique_key_seq(seq)
    #     if key in self.seen_keys:
    #         return False
    #     self.seen_keys.add(key)
    #     return True
    
    def unique_seq_constraint(self, seq: Seq[Op], key) -> bool:
        # if self.unique_key_seq is None:
            # return True
        k = key(seq)
        if k in self.seen_keys:
            return False
        self.seen_keys.add(k)
        return True

    def __iter__(self) -> Generator[Seq[Op], None, None]:
        self.seen_keys = set()
        return self._iter(self.prefix)

    def _iter(self, prefix: Seq[Op] = ()) -> Generator[Seq[Op], None, None]:
        if prefix and not all(constraint(prefix) for constraint in self.prefix_constraints):
            return
        if len(prefix) < self.n:
            yield from itertools.chain.from_iterable(self._iter(seq) for seq in self.generator(prefix))
            return
        if not all(constraint(prefix) for constraint in self.constraints):
            return
        # if self.unique_key_seq is not None:
        #     key = self.unique_key_seq(prefix)
        #     if key in self.seen_keys:
        #         return
        #     self.seen_keys.add(key)
        yield prefix




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

    # def _generate_candidates(self, op: Op, seq: Seq[Op]) -> Iterable[Seq[Op]]:
    #     def inner() -> Iterable[Seq[Op]]:
    #         candidate = (*seq, op)
    #         if len(candidate) < self.n:
    #             yield from self._iter(prefix=candidate)
    #             return
    #         yield candidate
    #     return tuple(inner())
