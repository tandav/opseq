from typing import TypeVar
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Sequence
from collections.abc import Iterable

Op = TypeVar('Op')
Seq = tuple[Op, ...]
# OpsIterable = Iterable[Op] # kind of redundant, don't use
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]
OpsCallableNoArgs = Callable[[], Iterable[Op]]
Constraint = Callable[[Seq[Op]], bool]
LookbackConstraint = dict[int, Callable[[Op, Op], bool]]
IConstraint = dict[int, Callable[[Op], bool]]
GeneratorCallable = Callable[[Seq[Op]], Generator[Op, None, None]]
