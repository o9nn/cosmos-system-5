"""
System 1: Atomic/Base Tensors - The Foundation of Nested Embeddings

Mathematical Properties:
-----------------------
- Nesting Depth: 0 (no nesting)
- Catalan Number: C_0 = 1 (one structure)
- Parentheses: ()
- Tree: Single leaf node
- Partition: [1] (single box)

System 1 represents the base case - standard tensors without nesting.
These are the "atoms" from which all higher systems are built.

In neural network terms:
- Standard linear layers
- Convolutions
- Embeddings
- Any operation on flat tensors

The key insight is that System 1 tensors are the leaves in higher
system trees. Every nested structure eventually bottoms out at atoms.
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import math


# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


@dataclass
class AtomicEmbedding:
    """
    An atomic embedding in System 1.

    This wraps a standard tensor with metadata about its role
    in the nested embedding hierarchy.

    Properties:
    - data: The underlying tensor data
    - shape: Tensor dimensions
    - embedding_dim: Size of the embedding vector
    - semantic_role: Optional label for the embedding's meaning
    """
    data: Any  # torch.Tensor or numpy array
    embedding_dim: int = 0
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if hasattr(self.data, 'shape'):
            if len(self.data.shape) > 0:
                self.embedding_dim = self.data.shape[-1]

    @property
    def shape(self) -> Tuple[int, ...]:
        if hasattr(self.data, 'shape'):
            return tuple(self.data.shape)
        return ()

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def depth(self) -> int:
        """Nesting depth is always 0 for atoms."""
        return 0

    @property
    def system(self) -> int:
        """System number is always 1 for atoms."""
        return 1

    def to_tree(self) -> 'RootedTree':
        """Convert to single-node tree."""
        from ..trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(
            value=self.semantic_role or "atom",
            children=[],
            metadata={"shape": self.shape, "embedding_dim": self.embedding_dim}
        ))

    def to_partition(self) -> 'Partition':
        """Convert to trivial partition [1]."""
        from ..ferrer import Partition
        return Partition(parts=(1,))

    def to_parentheses(self) -> str:
        """Represent as empty parentheses (leaf)."""
        return "()"

    def flatten(self) -> List[Any]:
        """Flatten returns the atom itself."""
        return [self.data]

    def map(self, f: Callable[[Any], Any]) -> 'AtomicEmbedding':
        """Apply function to data."""
        return AtomicEmbedding(
            data=f(self.data),
            embedding_dim=self.embedding_dim,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def __repr__(self) -> str:
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return f"AtomicEmbedding(shape={self.shape}, dim={self.embedding_dim}{role})"


class System1:
    """
    System 1: The Atomic Embedding System.

    This is the foundation layer that provides:
    1. Standard tensor operations
    2. Base embeddings for higher systems
    3. Leaf node creation for nested structures

    Catalan Analysis:
    ----------------
    C_0 = 1: There is exactly one way to "parenthesize" a single element.
    The structure () represents an atom with no internal subdivision.

    Tree Representation:
    -------------------
    A single leaf node with no children.

    Ferrer Diagram:
    --------------
    [1] = █  (single box)

    Usage:
    ------
    >>> s1 = System1(embedding_dim=64)
    >>> atom = s1.embed(data)
    >>> tree = atom.to_tree()  # Single node
    >>> parens = atom.to_parentheses()  # "()"
    """

    def __init__(self, embedding_dim: int = 64):
        """
        Initialize System 1.

        Args:
            embedding_dim: Default dimensionality for embeddings
        """
        self.embedding_dim = embedding_dim
        self._catalan = 1  # C_0 = 1

    @property
    def depth(self) -> int:
        """Maximum nesting depth in System 1."""
        return 0

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures (C_0 = 1)."""
        return self._catalan

    @property
    def structure_count(self) -> int:
        """Alias for catalan_number."""
        return self._catalan

    def embed(self, data: Any, role: Optional[str] = None) -> AtomicEmbedding:
        """
        Create an atomic embedding from data.

        Args:
            data: Tensor data (torch.Tensor, numpy array, or list)
            role: Optional semantic label

        Returns:
            AtomicEmbedding wrapping the data
        """
        return AtomicEmbedding(
            data=data,
            embedding_dim=self.embedding_dim,
            semantic_role=role
        )

    def zeros(self, *shape: int, role: Optional[str] = None) -> AtomicEmbedding:
        """Create zero-initialized atomic embedding."""
        if TORCH_AVAILABLE:
            data = torch.zeros(*shape)
        else:
            import numpy as np
            data = np.zeros(shape)
        return self.embed(data, role=role)

    def ones(self, *shape: int, role: Optional[str] = None) -> AtomicEmbedding:
        """Create ones-initialized atomic embedding."""
        if TORCH_AVAILABLE:
            data = torch.ones(*shape)
        else:
            import numpy as np
            data = np.ones(shape)
        return self.embed(data, role=role)

    def randn(self, *shape: int, role: Optional[str] = None) -> AtomicEmbedding:
        """Create random normal-initialized atomic embedding."""
        if TORCH_AVAILABLE:
            data = torch.randn(*shape)
        else:
            import numpy as np
            data = np.random.randn(*shape)
        return self.embed(data, role=role)

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all structures in System 1.

        Returns: ["()"] - the single atomic structure
        """
        return ["()"]

    def structure_tree(self) -> 'RootedTree':
        """Get the canonical tree for System 1 structure."""
        from ..trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(value="atom", children=[]))

    def __repr__(self) -> str:
        return f"System1(embedding_dim={self.embedding_dim})"


# Neural network layer (if torch available)
if TORCH_AVAILABLE:
    class AtomicLayer(nn.Module):
        """
        Neural network layer for System 1 atomic embeddings.

        This is essentially a standard linear layer with System 1 metadata.
        It serves as the base building block for nested neural networks.
        """

        def __init__(self, in_features: int, out_features: int, bias: bool = True):
            super().__init__()
            self.linear = nn.Linear(in_features, out_features, bias=bias)
            self.system = System1(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 0

        def forward(self, x: torch.Tensor) -> AtomicEmbedding:
            """
            Forward pass returning an AtomicEmbedding.

            Args:
                x: Input tensor

            Returns:
                AtomicEmbedding containing the transformed tensor
            """
            output = self.linear(x)
            return self.system.embed(output, role="linear_output")

        def __repr__(self) -> str:
            return f"AtomicLayer({self.linear.in_features} -> {self.linear.out_features})"
else:
    # Placeholder if torch not available
    class AtomicLayer:
        """Placeholder for AtomicLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for AtomicLayer")
