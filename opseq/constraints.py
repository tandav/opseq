from __future__ import annotations

import typing as tp

# import functools
from opseq.types import Op

if tp.TYPE_CHECKING:
    from opseq.types import Seq
    from opseq.types import UniqueKeyOp


class Lookback(tp.Generic[Op]):
    def __init__(self, index: int, constraint: tp.Callable[[Op, Op], bool], loop: bool = False) -> None:
        if index >= 0:
            raise KeyError('constraint index must be negative')
        self.index = index
        self.constraint = constraint
        self.loop = loop

    @classmethod
    def from_dict(cls, d: dict[int, tp.Callable[[Op, Op], bool]], loop: bool = False) -> list[Lookback[Op]]:
        return [cls(index, constraint, loop) for index, constraint in d.items()]

    def __call__(self, seq: Seq[Op]) -> bool:
        if len(seq) == 1:
            return True
        if abs(self.index) >= len(seq):
            return True
        if self.loop:
            return all(
                self.constraint(seq[(i + self.index) % len(seq)], seq[i])
                for i in range(abs(self.index))
            )
        return self.constraint(seq[self.index - 1], seq[-1])


class UniqueOp(tp.Generic[Op]):
    def __init__(self, key: UniqueKeyOp[Op]) -> None:
        self.key = key

    def __call__(self, seq: Seq[Op]) -> bool:
        return len(seq) == len(set(map(self.key, seq)))


class LenConstraint(tp.Generic[Op]):
    def __init__(self, length: int, constraint: tp.Callable[[Seq[Op]], bool]) -> None:
        self.length = length
        self.constraint = constraint

    @classmethod
    def from_dict(cls, d: dict[int, tp.Callable[[Seq[Op]], bool]]) -> list[LenConstraint[Op]]:
        return [cls(length, constraint) for length, constraint in d.items()]

    def __call__(self, seq: Seq[Op]) -> bool:
        return len(seq) == self.length and self.constraint(seq)
