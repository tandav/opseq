from __future__ import annotations

import itertools
import os
import typing as tp
from collections import deque
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

# how many subtrees to hand to each worker: enough to even out subtrees of very
# different sizes, few enough to keep the breadth-first split and the ipc cheap
TASKS_PER_WORKER = 4

# a single subtree is the whole search: running it in a worker only adds ipc
MIN_PARALLEL_TASKS = 2


class OpSeq(tp.Generic[Op]):
    """Enumerate every sequence of length n that satisfies constraints.

    with parallel=True the search tree is split into independent subtrees which
    are enumerated in worker processes. sequences are yielded in the same order
    as the serial search, so both modes produce identical output.

    parallel=True pickles the generator and the constraints, so they must be
    importable module level objects (not lambdas or closures), and the calling
    code must be guarded by `if __name__ == '__main__':` on spawn platforms.
    """

    def __init__(
        self,
        n: int,
        generator: GeneratorCallable[Op],
        prefix: Iterable[Op] = (),
        constraints: Iterable[Constraint[Op]] = (),
        prefix_constraints: Iterable[Constraint[Op]] = (),
        parallel: bool = False,
        max_workers: int | None = None,
    ) -> None:
        self.n = n
        self.generator = generator
        self.prefix = tuple(prefix)
        self.constraints = tuple(constraints)
        self.prefix_constraints = tuple(prefix_constraints)
        self.parallel = parallel
        self.max_workers = max_workers

    def __iter__(self) -> Iterator[Seq[Op]]:
        if self.parallel:
            return self._parallel_iter()
        return self._iter(self.prefix)

    def _iter(self, prefix: Iterable[Op] = ()) -> Generator[Seq[Op]]:
        """Depth-first search over the subtree rooted at prefix.

        an explicit stack rather than recursion: `yield from` recursion makes
        every sequence bubble up through one generator frame per op.
        """
        n = self.n
        generator = self.generator
        constraints = self.constraints
        prefix_constraints = self.prefix_constraints
        stack = [tuple(prefix)]
        while stack:
            seq = stack.pop()
            if seq and prefix_constraints and not all(constraint(seq) for constraint in prefix_constraints):
                continue
            if len(seq) < n:
                # children are pushed reversed so they pop in generated order
                stack.extend([tuple(longer) for longer in generator(seq)][::-1])
                continue
            if len(seq) > n:
                raise exceptions.SeqLengthError
            if constraints and not all(constraint(seq) for constraint in constraints):
                continue
            yield seq

    def _parallel_iter(self) -> Generator[Seq[Op]]:
        n_workers = self._n_workers()
        in_flight = n_workers * TASKS_PER_WORKER
        tasks = self._split(in_flight)
        if len(tasks) < MIN_PARALLEL_TASKS:
            # nothing to spread: an empty search, or n reached before any branching
            yield from self._iter(self.prefix)
            return
        # never spawn a process that has no subtree to work on
        with ProcessPoolExecutor(max_workers=min(n_workers, len(tasks))) as executor:
            queued = iter(tasks)
            # results are yielded in order, so submitting every subtree at once
            # would buffer the whole search in memory. keep a bounded window
            # instead, wide enough that no worker ever runs out of subtrees
            futures = deque(executor.submit(self._collect, task) for task in itertools.islice(queued, in_flight))
            while futures:
                seqs = futures.popleft().result()
                # refill before yielding, so a worker starts while the consumer
                # is still walking the results we already have
                task = next(queued, None)
                if task is not None:
                    futures.append(executor.submit(self._collect, task))
                yield from seqs

    def _n_workers(self) -> int:
        if self.max_workers is not None:
            return self.max_workers
        return os.cpu_count() or 1

    def _split(self, min_tasks: int) -> list[Seq[Op]]:
        """Grow the prefix breadth-first into at least min_tasks subtree roots.

        each level replaces a prefix by its children in place, so the roots stay
        in depth-first order and concatenating their results keeps serial order.
        """
        if self.prefix and not all(constraint(self.prefix) for constraint in self.prefix_constraints):
            return []
        tasks = [self.prefix]
        while len(tasks) < min_tasks:
            if all(len(seq) >= self.n for seq in tasks):
                break
            next_tasks: list[Seq[Op]] = []
            for seq in tasks:
                if len(seq) >= self.n:
                    next_tasks.append(seq)
                    continue
                for generated in self.generator(seq):
                    longer = tuple(generated)
                    # same order of checks as _iter, so both modes raise alike
                    if not all(constraint(longer) for constraint in self.prefix_constraints):
                        continue
                    if len(longer) > self.n:
                        raise exceptions.SeqLengthError
                    next_tasks.append(longer)
            if not next_tasks:
                return []
            tasks = next_tasks
        return tasks

    def _collect(self, prefix: Seq[Op]) -> list[Seq[Op]]:
        """Enumerate one subtree eagerly. runs in a worker process."""
        return list(self._iter(prefix))
