from __future__ import annotations

import itertools
import typing as tp
from concurrent.futures import ProcessPoolExecutor

from opseq import exceptions
from opseq.types import Op

if tp.TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Iterator

    from opseq.types import Constraint
    from opseq.types import GeneratorCallable
    from opseq.types import Seq


class OpSeq(tp.Generic[Op]):
    def __init__(
        self,
        n: int,
        generator: GeneratorCallable[Op],
        prefix: Iterable[Op] = (),
        constraints: Iterable[Constraint[Op]] = (),
        prefix_constraints: Iterable[Constraint[Op]] = (),
        parallel: bool = False,
    ) -> None:
        self.n = n
        self.generator = generator
        self.prefix = prefix
        self.constraints = list(constraints)
        self.prefix_constraints = list(prefix_constraints)
        self.parallel = parallel

    def __iter__(self) -> Iterator[Seq[Op]]:
        # self.prefix_queue = multiprocessing.Queue()
        # self.prefix_queue.put(self.prefix)
        return self._iter(self.prefix)

    def _iter(self, prefix: Iterable[Op] = ()) -> Generator[Seq[Op]]:
        seq = tuple(prefix)
        if seq and not all(constraint(seq) for constraint in self.prefix_constraints):
            return
        if len(seq) < self.n:
            seqs = self.generator(seq)
            if self.parallel:
                # self.prefix_queue += seqs
                with ProcessPoolExecutor() as executor:
                    for result in executor.map(self._iter, seqs):
                        yield from result
            else:
                yield from itertools.chain.from_iterable(self._iter(longer) for longer in seqs)
            return
        if len(seq) > self.n:
            raise exceptions.SeqLengthError
        if not all(constraint(seq) for constraint in self.constraints):
            return
        yield seq
