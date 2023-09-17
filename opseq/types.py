from typing import TypeVar
from collections.abc import Callable
from collections.abc import Sequence
from collections.abc import Iterable

Op = TypeVar('Op')
# OpsIterable = Iterable[Op] # kind of redundant, don't use
OpsFixedPerStep = Sequence[Iterable[Op]]
OpsCallableFromCurr = Callable[[Op], Iterable[Op]]
OpsCallableNoArgs = Callable[[], Iterable[Op]]
LookbackConstraint = dict[int, Callable[[Op, Op], bool]]
CandidateConstraint = Callable[[tuple[Op, ...]], bool]
IConstraint = dict[int, Callable[[Op], bool]]
