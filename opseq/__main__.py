import itertools
from collections.abc import Iterable
from collections.abc import Generator
from collections.abc import Callable
from typing import Any
from concurrent.futures import ProcessPoolExecutor
import tqdm
import multiprocessing
from functools import partial

from opseq import exceptions
from opseq.types import Op
from opseq.types import LookbackConstraint
from opseq.types import Seq
from opseq.types import Constraint
from opseq.types import UniqueKeyOp
from opseq.types import UniqueKeySeq
from opseq import constraints as constraints_


class OpSeq:
    def __init__(
        self,
        n: int,
        generator: Callable,
        prefix: Seq[Op] = (),
        constraints: Iterable[Constraint[Op]] = (),
        prefix_constraints: Iterable[Constraint[Op]] = (),
    ):
        self.n = n
        self.generator = generator
        self.constraints = list(constraints)
        self.prefix_constraints = list(prefix_constraints)
        self.seen_keys = set()
        self.prefix = prefix

    def __iter__(self) -> Generator[Seq[Op], None, None]:
        self.seen_keys.clear()
        self.prefix_queue = multiprocessing.Queue()
        self.prefix_queue.put(self.prefix)
        return self._iter(self.prefix)

    def _iter(self, prefix: Seq[Op] = ()) -> Generator[Seq[Op], None, None]:
        prefix = tuple(prefix)
        if prefix and not all(constraint(prefix) for constraint in self.prefix_constraints):
            return
        if len(prefix) < self.n:
            seqs = self.generator(prefix)
            # self.prefix_queue += seqs
            yield from itertools.chain.from_iterable(self._iter(seq) for seq in seqs)
            return
        if len(prefix) > self.n:
            raise exceptions.SeqLengthError
        if not all(constraint(prefix) for constraint in self.constraints):
            return
        yield prefix
