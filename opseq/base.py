import itertools
from collections.abc import Iterable
from collections.abc import Generator
from collections.abc import Callable
from typing import Any
from concurrent.futures import ProcessPoolExecutor
import tqdm
from functools import partial

from opseq import exceptions
from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import Seq
from opseq.types import Constraint
from opseq.types import UniqueKeyOp
from opseq.types import UniqueKeySeq
from opseq import constraints as constraints_


class OpSeqBase:
    def __init__(
        self,
        n: int,
        generator: Callable,
        prefix: Seq[Op] = (),
        constraints: Iterable[Constraint[Op]] = (),
        prefix_constraints: Iterable[Constraint[Op]] = (),
        lookback_constraints: LookbackConstraint[Op] | None = None,
        unique_key_op: UniqueKeyOp[Op] | None = None,
        unique_key_seq: UniqueKeySeq[Op] | None = None,
        # loop: bool = False,
    ):
        # attributes
        self.n = n
        self.generator = generator
        self.constraints = list(constraints)
        self.prefix_constraints = list(prefix_constraints)

        if lookback_constraints is not None:
            for index, constraint in lookback_constraints.items(): 
                self.prefix_constraints.append(constraints_.Lookback(index, constraint))

        # self.i_constraints = i_constraints
        self.seen_keys = set()

        if unique_key_op is not None:
            self.prefix_constraints.append(constraints_.UniqueOp(unique_key_op))

        if unique_key_seq is not None:
            self.constraints.append(constraints_.UniqueSeq(unique_key_seq, self.seen_keys))

        self.prefix = prefix
        # self.loop = loop

    def __iter__(self) -> Generator[Seq[Op], None, None]:
        self.seen_keys.clear()
        return self._iter(self.prefix)

    def _iter(self, prefix: Seq[Op] = ()) -> Generator[Seq[Op], None, None]:
        prefix = tuple(prefix)
        if prefix and not all(constraint(prefix) for constraint in self.prefix_constraints):
            return
        if len(prefix) < self.n:
            seqs = self.generator(prefix)
            seqs = constraints_.seq_length(seqs, len(prefix) + 1)
            yield from itertools.chain.from_iterable(self._iter(seq) for seq in seqs)
            return
        if not all(constraint(prefix) for constraint in self.constraints):
            return
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
