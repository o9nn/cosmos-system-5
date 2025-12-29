"""
torch.nnn - Nested Neural Networks

Extension of torch.nn to support nested tensor embeddings modeled as:
- Rooted trees (hierarchical depth structures)
- Ferrer/Young diagrams (partition representations)
- Nested parentheses (Catalan-structured tuples)

Systems 1-N represent increasing nesting depths:
- System 1: Atoms (depth 0) - base tensors, leaves
- System 2: Pairs (depth 1) - binary nesting, (a, b)
- System 3: Triples (depth 2) - ternary nesting, ((a, b), c) or (a, (b, c))
- System N: N-ary nesting with Catalan(N-1) structural possibilities

The nesting follows the Catalan number sequence for structural variants:
C_0=1, C_1=1, C_2=2, C_3=5, C_4=14, ...

Each System-K has C_{K-1} distinct nesting structures.
"""

from .core import NestedTensor, NestingLevel
from .trees import RootedTree, TreeNode
from .ferrer import FerrerDiagram, Partition
from .systems import System1, System2, System3

__version__ = "0.1.0"
__all__ = [
    "NestedTensor",
    "NestingLevel",
    "RootedTree",
    "TreeNode",
    "FerrerDiagram",
    "Partition",
    "System1",
    "System2",
    "System3",
]
