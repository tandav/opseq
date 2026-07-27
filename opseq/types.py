from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import Iterable
from collections.abc import Sequence
from typing import TypeVar

Op = TypeVar('Op')
Seq = tuple[Op, ...]
# OpsIterable = Iterable[Op] # kind of redundant, don't use
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]
OpsCallableNoArgs = Callable[[], Iterable[Op]]
Constraint = Callable[[Seq[Op]], bool]
LookbackConstraint = dict[int, Callable[[Op, Op], bool]]
IConstraint = dict[int, Callable[[Op], bool]]
GeneratorCallable = Callable[[Seq[Op]], Iterable[Seq[Op]]]
UniqueKeyOp = Callable[[Op], Hashable]
UniqueKeySeq = Callable[[Seq[Op]], Hashable]
