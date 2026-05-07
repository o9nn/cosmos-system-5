"""
Systems 0-N: Nested tensor embedding hierarchies.

Each System-K defines a specific level of nesting complexity:

System 0 (Void/Nest):
  - Depth: 0
  - Structure: []  (root void, empty)
  - Catalan: 1 structure (the void)
  - Partition: [] (empty)
  - The base embedding space; no atoms

System 1 (Atoms):
  - Depth: 0
  - Structure: [()]
  - Catalan: C_0 = 1 structure
  - Partition: [1]
  - Tensors: Standard flat tensors

System 2 (Pairs):
  - Depth: 1
  - Structure: [()()]
  - Catalan: C_1 = 1 structure
  - Partitions: [2], [1,1]
  - Tensors: Paired/bipartite tensors

System 3 (Triples):
  - Depth: 2
  - Structures: [(())()], [(()())]  — 2 canonical shapes
  - Catalan: C_2 = 2 structures
  - Partitions: [3], [2,1], [1,1,1]
  - Tensors: Tripartite tensors with association choice

System 4 (Quads):
  - Depth: 3
  - Canonical: [(()())()]
  - Catalan: C_3 = 5 structures
  - Partitions: [4], [3,1], [2,2], [2,1,1], [1,1,1,1]
  - Tensors: Quaternary tensors; includes balanced split ((a,b),(c,d))

System 5 (Quints):
  - Depth: 4
  - Canonical: [(((()())())())()]
  - Catalan: C_4 = 14 structures
  - Partitions: all partitions of 5
  - Tensors: Quinary tensors; pentadic relations have quaternary order

Notes:
- Root node '[]' is distinguished from tree nodes '()'
- System order = half the length of the inner parentheses string
- Arity relations are indexed by Matula primes
- Order is indexed by integer partitions
"""

from .system0 import System0, VoidEmbedding
from .system1 import System1, AtomicEmbedding
from .system2 import System2, PairEmbedding
from .system3 import System3, TripleEmbedding
from .system4 import System4, QuadEmbedding, Association4
from .system5 import System5, QuintEmbedding, Association5

__all__ = [
    "System0", "VoidEmbedding",
    "System1", "AtomicEmbedding",
    "System2", "PairEmbedding",
    "System3", "TripleEmbedding",
    "System4", "QuadEmbedding", "Association4",
    "System5", "QuintEmbedding", "Association5",
]
