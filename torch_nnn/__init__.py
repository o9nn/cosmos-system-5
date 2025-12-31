"""
torch.nnn - Nested Neural Networks

Extension of torch.nn to support nested tensor embeddings modeled as:
- Rooted trees (hierarchical depth structures)
- Ferrer/Young diagrams (partition representations)
- Nested parentheses (Catalan-structured tuples)
- Matula numbers (2D unordered tree bijection)

Two embedding paradigms:

1D EMBEDDINGS (Catalan-indexed, ordered trees):
  - Binary trees where child order matters
  - Structure count follows Catalan numbers: 1, 1, 2, 5, 14, 42, ...
  - Use: Sequential/linear nesting (language, attention)

2D EMBEDDINGS (Matula-indexed, unordered trees):
  - Rooted trees where child order doesn't matter
  - Structure count follows A000081: 1, 1, 2, 4, 9, 20, 48, 115, ...
  - Use: Hierarchical/matrix nesting (molecules, types)

Systems 0-N represent increasing tree sizes:
  sys(0) = 1:  ●           (single node)
  sys(1) = 1:  ●─●         (one edge)
  sys(2) = 2:  ●─●─● or ●<● (chain or fork)
  sys(3) = 4:  (four 4-node trees)
  sys(4) = 9:  (nine 5-node trees)
  ...

The Matula number bijection: N⁺ ↔ Rooted Trees
  1 ↔ ●, 2 ↔ ●─●, 3 ↔ ●─●─●, 4 ↔ ●<●, 5 ↔ ●─●─●─●, ...
"""

# 1D Catalan-indexed structures (ordered trees)
from .core import NestedTensor, NestingLevel
from .trees import RootedTree, TreeNode
from .ferrer import FerrerDiagram, Partition
from .systems import System1, System2, System3

# 2D Matula-indexed structures (unordered trees)
from .matula import (
    MatulaTree,
    MatulaNode,
    sys,
    a000081,
    nth_prime,
    prime_index,
    enumerate_matula_trees,
)
from .embedding2d import TreeEmbedding2D, System2D

__version__ = "0.2.0"
__all__ = [
    # 1D (Catalan)
    "NestedTensor",
    "NestingLevel",
    "RootedTree",
    "TreeNode",
    "FerrerDiagram",
    "Partition",
    "System1",
    "System2",
    "System3",
    # 2D (Matula)
    "MatulaTree",
    "MatulaNode",
    "sys",
    "a000081",
    "nth_prime",
    "prime_index",
    "enumerate_matula_trees",
    "TreeEmbedding2D",
    "System2D",
]
