# opseq
a python library to build sequences of operations under arbitrary constraints.

you give it a length, a rule for growing a sequence by one step, and the
constraints the result must satisfy. it walks the search tree depth-first and
yields every sequence that survives — lazily, and optionally in parallel.

## install from [pypi](https://pypi.org/project/opseq/)
```sh
pip install opseq
```

## quick start
```python
from opseq import OpSeq
from opseq.generators import AppendOp

for seq in OpSeq(2, AppendOp('ab')):
    print(seq)
```
```
('a', 'a')
('a', 'b')
('b', 'a')
('b', 'b')
```

sequences are plain tuples, yielded in depth-first order. `OpSeq` is an iterable
and not an iterator: iterating it twice runs the search twice, and results are
produced lazily, so a huge search can be cut short with `itertools.islice`.

## how it works
the search is a tree. the root is `prefix` (the empty sequence by default), and
`generator(seq)` produces the children of every node. a branch is dropped as
soon as a `prefix_constraint` fails; a leaf of length `n` is yielded only if
every `constraint` passes.

| argument | meaning |
| --- | --- |
| `n` | length of the sequences to build |
| `generator` | callable `seq -> iterable of longer seqs`, called on every incomplete prefix |
| `prefix` | sequence to start the search from, default `()` |
| `constraints` | checked on complete sequences only (`len(seq) == n`) |
| `prefix_constraints` | checked on every non-empty prefix, complete sequences included. a failing prefix prunes its whole subtree |
| `parallel` | enumerate independent subtrees in worker processes, default `False` |
| `max_workers` | size of the process pool, default `os.cpu_count()` |

### constraints
`constraints` filter the finished sequences. use them for anything that can only
be judged once the sequence is complete:

```python
list(OpSeq(3, AppendOp(range(3)), constraints=[lambda seq: sum(seq) == 3]))
# [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 1, 1), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
```

### prefix_constraints
`prefix_constraints` prune. use them when a prefix that fails can never be
rescued by appending more ops — then the whole subtree below it is skipped
instead of being enumerated and thrown away at the end:

```python
import itertools

def no_repeat(seq):
    return all(a != b for a, b in itertools.pairwise(seq))

list(OpSeq(3, AppendOp(range(3)), prefix_constraints=[no_repeat]))
# [(0, 1, 0), (0, 1, 2), (0, 2, 0), (0, 2, 1), (1, 0, 1), (1, 0, 2), ...]
```

the same predicate passed as a `constraint` returns exactly the same sequences,
it just does the work at the end. the difference is what the search touches, and
it compounds with depth: at `n=8` over 3 options both return the same 384
sequences, but pruning reaches 576 complete sequences on the way instead of all
6561.

> [!WARNING]
> a constraint that a longer sequence could still satisfy must not go into
> `prefix_constraints`. `sum(seq) == 3` as a prefix constraint kills `(0,)`
> before it ever reaches `(0, 1, 2)`:
> ```python
> list(OpSeq(3, AppendOp(range(3)), prefix_constraints=[lambda seq: sum(seq) == 3]))
> # []
> ```

### prefix
`prefix` fixes the beginning of every sequence and searches only the subtree
below it:

```python
list(OpSeq(2, AppendOp(range(3)), prefix=[0]))
# [(0, 0), (0, 1), (0, 2)]
```

a prefix of length `n` yields itself (if it passes the constraints); a prefix
longer than `n` raises `SeqLengthError`. the empty prefix is never handed to
`prefix_constraints`, so `n=0` always yields exactly `[()]`.

## generators
a generator is any callable taking the current sequence and yielding longer
ones. `AppendOp` is the common case — append one of a fixed set of options:

```python
from opseq.generators import AppendOp

AppendOp(range(3))        # any collection that can be iterated more than once
AppendOp('abc')
AppendOp([{'a': 1}, {'b': 2}])  # ops need not be hashable
```

writing your own is just a function. it receives the prefix as a tuple and may
yield anything sequence-like (lists are coerced to tuples), so the next op can
depend on the ones already chosen:

```python
def growing(seq):
    last = seq[-1] if seq else 0
    yield (*seq, last + 1)
    yield (*seq, last + 10)

list(OpSeq(3, growing))
# [(1, 2, 3), (1, 2, 12), (1, 11, 12), (1, 11, 21), (10, 11, 12), (10, 11, 21), (10, 20, 21), (10, 20, 30)]
```

a generator may also add more than one op at a time, and may add a different
number of ops per branch — it just must not overshoot `n`:

```python
def one_or_two(seq):
    yield (*seq, 0)
    if len(seq) + 2 <= 4:
        yield (*seq, 1, 1)

list(OpSeq(4, one_or_two))
# [(0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 1, 0), (1, 1, 0, 0), (1, 1, 1, 1)]
```

## built-in constraints
`opseq.constraints` has ready-made callables for the recurring cases. they are
ordinary constraints — pass them in `constraints` or `prefix_constraints`.

### Lookback
compares the last op with the one `index` ops back. `index` must be negative:

```python
import operator
from opseq.constraints import Lookback

# no two adjacent ops are equal
list(OpSeq(3, AppendOp(range(3)), prefix_constraints=[Lookback(-1, operator.ne)]))
```

a sequence too short to have an op `index` back passes vacuously, which is what
makes `Lookback` usable as a `prefix_constraint`.

`from_dict` builds several at once, keyed by index:

```python
Lookback.from_dict({-1: operator.ne, -2: operator.eq})
```

with `loop=True` the sequence is treated as a cycle and only the wraparound
pairs are checked — the interior is somebody else's problem. pair the looping
version (as a `constraint`, it needs the finished sequence) with the plain one
(as a `prefix_constraint`) to get a cyclic sequence:

```python
list(OpSeq(
    3, AppendOp(range(3)),
    prefix_constraints=Lookback.from_dict({-1: operator.ne}),
    constraints=Lookback.from_dict({-1: operator.ne}, loop=True),
))
# [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
```

### UniqueOp
no two ops share a key. the key must return something hashable:

```python
from opseq.constraints import UniqueOp

list(OpSeq(2, AppendOp(['a', 'A', 'b']), prefix_constraints=[UniqueOp(str.lower)]))
# [('a', 'b'), ('A', 'b'), ('b', 'a'), ('b', 'A')]
```

### LenConstraint
applies a constraint at one exact length. it is a conjunction, not an
implication: a sequence of any other length fails outright, so it belongs in
`constraints` with `length == n`:

```python
from opseq.constraints import LenConstraint

list(OpSeq(3, AppendOp([0, 1]), constraints=LenConstraint.from_dict({3: lambda seq: sum(seq) == 1})))
# [(0, 0, 1), (0, 1, 0), (1, 0, 0)]
```

## parallel building
`parallel=True` splits the search tree into independent subtrees and enumerates
them in worker processes. sequences come back in the same order as the serial
search, so both modes produce identical output.

```python
from opseq import OpSeq
from opseq.generators import AppendOp

def sum_is_even(seq):
    return sum(seq) % 2 == 0

if __name__ == '__main__':
    for seq in OpSeq(5, AppendOp(range(8)), constraints=[sum_is_even], parallel=True):
        print(seq)
```

the generator and the constraints are pickled and sent to the workers, so they
must be importable module level objects (not lambdas or closures), and the
calling code must be guarded by `if __name__ == '__main__':` on spawn platforms
(windows, macos). pass `max_workers=` to cap the pool, it defaults to
`os.cpu_count()`.

parallel pays for process startup, so it wins when the constraints are
expensive; a cheap search is faster serially.

## errors
`opseq.exceptions.SeqLengthError` (a `ValueError`) is raised when a sequence
grows past `n` — a generator adding too many ops at once, or a `prefix` longer
than `n`. it crosses the process boundary intact, so `parallel=True` raises it
the same way.

## development
```sh
pip install -e '.[dev]'
pytest                    # -m 'not slow' to skip the timing benchmarks
pre-commit run --all-files
make bumpver PART=minor
```
