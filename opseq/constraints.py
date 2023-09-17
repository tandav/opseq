from __future__ import annotations
# import functools
from collections.abc import Iterable
import typing as tp
from opseq.types import Seq
from opseq.types import Op
from collections.abc import Generator

class Lookback:
    def __init__(self, index, constraint):
        if index >= 0:
            raise KeyError('constraint index must be negative')
        self.index = index
        self.constraint = constraint

    def __call__(self, seq: Seq[Op]) -> bool:
        if len(seq) == 1:
            return True
        if abs(self.index) > len(seq):
            return False
        return self.constraint(seq[self.index - 1], seq[-1])


class UniqueOp:
    def __init__(self, key):
        self.key = key

    def __call__(self, seq: Seq[Op]) -> bool:
        return len(seq) == len(set(map(self.key, seq)))


class UniqueSeq:
    def __init__(self, key, seen_keys):
        self.key = key
        self.seen_keys = seen_keys

    def __call__(self, seq: Seq[Op]) -> bool:
        k = self.key(seq)
        if k in self.seen_keys:
            return False
        self.seen_keys.add(k)
        return True


class LenConstraint:
    def __init__(self, length: int, constraint: tp.Callable[[Seq[Op]], bool]):
        self.length = length
        self.constraint = constraint

    @classmethod
    def from_dict(cls, d: dict[int, tp.Callable[[Seq[Op]], bool]]) -> list[LenConstraint]:
        return [cls(length, constraint) for length, constraint in d.items()]

    def __call__(self, seq: Seq[Op]) -> bool:
        return len(seq) == self.length and self.constraint(seq)
