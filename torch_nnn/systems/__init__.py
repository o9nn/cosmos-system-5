"""
Systems 1-N: Nested tensor embedding hierarchies.

Each System-K defines a specific level of nesting complexity:

System 1 (Atoms):
  - Depth: 0
  - Structure: ()
  - Catalan: C_0 = 1 structure
  - Partition: [1]
  - Tensors: Standard flat tensors

System 2 (Pairs):
  - Depth: 1
  - Structure: ((),())
  - Catalan: C_1 = 1 structure
  - Partitions: [2], [1,1]
  - Tensors: Paired/bipartite tensors

System 3 (Triples):
  - Depth: 2
  - Structures: (((),()),()) or ((),((),()))
  - Catalan: C_2 = 2 structures
  - Partitions: [3], [2,1], [1,1,1]
  - Tensors: Tripartite tensors with association choice

The embedding dimension grows with the Catalan structure:
  System K embeds into space with C_{K-1} structural variants.
"""

from .system1 import System1, AtomicEmbedding
from .system2 import System2, PairEmbedding
from .system3 import System3, TripleEmbedding

__all__ = [
    "System1", "AtomicEmbedding",
    "System2", "PairEmbedding",
    "System3", "TripleEmbedding",
]
