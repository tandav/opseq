# opseq
a python library to build permutations sequences with various constraints

## install from [pypi](https://pypi.org/project/opseq/)
```sh
pip install opseq
```

## features
- TODO
- parallel building

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
