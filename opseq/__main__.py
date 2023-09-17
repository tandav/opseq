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
    def generate_options(self, seq: tuple[Op, ...]) -> Generator[Op, None, None]:
        yield from self.options
