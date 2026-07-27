from __future__ import annotations

import typing as tp

from opseq.types import Op

if tp.TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable

    from opseq.types import Seq


class AppendOp(tp.Generic[Op]):
    def __init__(self, options: Iterable[Op]) -> None:
        self.options = options

    def __call__(self, seq: Seq[Op]) -> Generator[Seq[Op]]:
        for op in self.options:
            yield (*seq, op)
