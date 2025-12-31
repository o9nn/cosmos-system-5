"""
System 2: Pair/Binary Tensors - The First Level of Nesting

Mathematical Properties:
-----------------------
- Nesting Depth: 1 (single nesting level)
- Catalan Number: C_1 = 1 (one binary structure)
- Parentheses: (()())
- Tree: Binary tree with 2 leaves
- Partitions: [2], [1,1]

System 2 introduces the fundamental concept of pairing - combining
two atomic embeddings into a structured whole. This is the first
departure from flat tensors.

In neural network terms:
- Siamese networks (processing pairs)
- Bilinear operations
- Attention (query-key pairs)
- Contrastive learning pairs

Key insight: Although there's only C_1 = 1 way to parenthesize
two elements, the partition representation captures whether
the pair is "balanced" [1,1] or "unified" [2].
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto
import math

from .system1 import System1, AtomicEmbedding

# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


T = TypeVar('T')


class PairType(Enum):
    """Classification of pair relationships."""
    SYMMETRIC = auto()    # Both elements have equal status
    ASYMMETRIC = auto()   # First element dominant (e.g., query > key)
    HIERARCHICAL = auto()  # One contains the other conceptually


@dataclass
class PairEmbedding:
    """
    A paired embedding in System 2.

    Represents a binary nesting structure (left, right) where
    left and right are atomic embeddings from System 1.

    The pair captures:
    - Structural relationship between two tensors
    - Compositional semantics (how atoms combine)
    - Interaction patterns (symmetric vs asymmetric)

    Properties:
    - left: First atomic embedding
    - right: Second atomic embedding
    - pair_type: Relationship classification
    - composition_dim: Dimension of composed output
    """
    left: AtomicEmbedding
    right: AtomicEmbedding
    pair_type: PairType = PairType.SYMMETRIC
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Nesting depth is 1 for pairs."""
        return 1

    @property
    def system(self) -> int:
        """System number is 2 for pairs."""
        return 2

    @property
    def shape(self) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        """Shape as nested tuple."""
        return (self.left.shape, self.right.shape)

    @property
    def embedding_dims(self) -> Tuple[int, int]:
        """Embedding dimensions of both atoms."""
        return (self.left.embedding_dim, self.right.embedding_dim)

    def flatten(self) -> List[Any]:
        """Flatten to list of atomic data."""
        return self.left.flatten() + self.right.flatten()

    def atoms(self) -> Tuple[AtomicEmbedding, AtomicEmbedding]:
        """Return both atomic embeddings."""
        return (self.left, self.right)

    def to_tree(self) -> 'RootedTree':
        """Convert to binary tree."""
        from ..trees import RootedTree, TreeNode
        left_node = self.left.to_tree().root
        right_node = self.right.to_tree().root
        return RootedTree(root=TreeNode(
            value=self.semantic_role or "pair",
            children=[left_node, right_node],
            metadata={
                "pair_type": self.pair_type.name,
                "shapes": self.shape
            }
        ))

    def to_partition(self) -> 'Partition':
        """
        Convert to partition based on pair balance.

        - Balanced pair (equal dims): [2]
        - Unbalanced pair: [1,1]
        """
        from ..ferrer import Partition
        if self.left.embedding_dim == self.right.embedding_dim:
            return Partition(parts=(2,))
        return Partition(parts=(1, 1))

    def to_parentheses(self) -> str:
        """Represent as nested parentheses."""
        return f"({self.left.to_parentheses()}{self.right.to_parentheses()})"

    def map(self, f: Callable[[Any], Any]) -> 'PairEmbedding':
        """Apply function to both atoms' data."""
        return PairEmbedding(
            left=self.left.map(f),
            right=self.right.map(f),
            pair_type=self.pair_type,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def swap(self) -> 'PairEmbedding':
        """Return pair with left and right swapped."""
        return PairEmbedding(
            left=self.right,
            right=self.left,
            pair_type=self.pair_type,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def compose_concat(self) -> AtomicEmbedding:
        """Compose by concatenation (returns to System 1)."""
        if TORCH_AVAILABLE and hasattr(self.left.data, 'shape'):
            composed = torch.cat([self.left.data, self.right.data], dim=-1)
        else:
            import numpy as np
            composed = np.concatenate([self.left.data, self.right.data], axis=-1)

        return AtomicEmbedding(
            data=composed,
            semantic_role=f"concat({self.semantic_role})" if self.semantic_role else "concat"
        )

    def compose_sum(self) -> AtomicEmbedding:
        """Compose by summation (returns to System 1)."""
        composed = self.left.data + self.right.data
        return AtomicEmbedding(
            data=composed,
            semantic_role=f"sum({self.semantic_role})" if self.semantic_role else "sum"
        )

    def compose_product(self) -> AtomicEmbedding:
        """Compose by element-wise product (returns to System 1)."""
        composed = self.left.data * self.right.data
        return AtomicEmbedding(
            data=composed,
            semantic_role=f"product({self.semantic_role})" if self.semantic_role else "product"
        )

    def __repr__(self) -> str:
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return f"PairEmbedding(left={self.left.shape}, right={self.right.shape}, type={self.pair_type.name}{role})"


class System2:
    """
    System 2: The Binary/Pair Embedding System.

    This level introduces the first nesting, allowing two atomic
    embeddings to be combined into a structured pair.

    Catalan Analysis:
    ----------------
    C_1 = 1: There is exactly one way to pair two elements: (a, b)
    The structure (()()) represents a binary node with two leaf children.

    Tree Representation:
    -------------------
         pair
        /    \\
      left  right

    Ferrer Diagrams:
    ---------------
    [2] = ██     (balanced pair)
    [1,1] = █    (unbalanced pair)
            █

    Nesting Pattern:
    ---------------
    System 2 = System 1 × System 1
    A pair is the Cartesian product of two atoms.

    Usage:
    ------
    >>> s1 = System1(embedding_dim=64)
    >>> s2 = System2(base_system=s1)
    >>> left = s1.embed(data1, role="query")
    >>> right = s1.embed(data2, role="key")
    >>> pair = s2.embed(left, right)
    >>> tree = pair.to_tree()  # Binary tree
    >>> parens = pair.to_parentheses()  # "(()())"
    """

    def __init__(self, base_system: Optional[System1] = None, embedding_dim: int = 64):
        """
        Initialize System 2.

        Args:
            base_system: System 1 for atomic embeddings (created if not provided)
            embedding_dim: Default dimensionality
        """
        self.base_system = base_system or System1(embedding_dim=embedding_dim)
        self.embedding_dim = embedding_dim
        self._catalan = 1  # C_1 = 1

    @property
    def depth(self) -> int:
        """Maximum nesting depth in System 2."""
        return 1

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures (C_1 = 1)."""
        return self._catalan

    @property
    def structure_count(self) -> int:
        """Alias for catalan_number."""
        return self._catalan

    def embed(
        self,
        left: Union[AtomicEmbedding, Any],
        right: Union[AtomicEmbedding, Any],
        pair_type: PairType = PairType.SYMMETRIC,
        role: Optional[str] = None
    ) -> PairEmbedding:
        """
        Create a pair embedding from two inputs.

        Args:
            left: First element (AtomicEmbedding or raw data)
            right: Second element (AtomicEmbedding or raw data)
            pair_type: Relationship type between elements
            role: Optional semantic label

        Returns:
            PairEmbedding containing both atoms
        """
        # Convert raw data to atoms if needed
        if not isinstance(left, AtomicEmbedding):
            left = self.base_system.embed(left, role="left")
        if not isinstance(right, AtomicEmbedding):
            right = self.base_system.embed(right, role="right")

        return PairEmbedding(
            left=left,
            right=right,
            pair_type=pair_type,
            semantic_role=role
        )

    def embed_symmetric(self, left: Any, right: Any, role: Optional[str] = None) -> PairEmbedding:
        """Create a symmetric pair (order doesn't matter semantically)."""
        return self.embed(left, right, PairType.SYMMETRIC, role)

    def embed_asymmetric(self, primary: Any, secondary: Any, role: Optional[str] = None) -> PairEmbedding:
        """Create an asymmetric pair (first element is primary)."""
        return self.embed(primary, secondary, PairType.ASYMMETRIC, role)

    def embed_hierarchical(self, container: Any, contained: Any, role: Optional[str] = None) -> PairEmbedding:
        """Create a hierarchical pair (first contains second)."""
        return self.embed(container, contained, PairType.HIERARCHICAL, role)

    def zeros_pair(
        self,
        left_shape: Tuple[int, ...],
        right_shape: Tuple[int, ...],
        role: Optional[str] = None
    ) -> PairEmbedding:
        """Create zero-initialized pair."""
        left = self.base_system.zeros(*left_shape, role="left")
        right = self.base_system.zeros(*right_shape, role="right")
        return self.embed(left, right, role=role)

    def randn_pair(
        self,
        left_shape: Tuple[int, ...],
        right_shape: Tuple[int, ...],
        role: Optional[str] = None
    ) -> PairEmbedding:
        """Create random normal-initialized pair."""
        left = self.base_system.randn(*left_shape, role="left")
        right = self.base_system.randn(*right_shape, role="right")
        return self.embed(left, right, role=role)

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all structures in System 2.

        Returns: ["(()())"] - the single binary structure
        """
        return ["(()())"]

    def enumerate_partitions(self) -> List['Partition']:
        """Enumerate all partitions for System 2 (partitions of 2)."""
        from ..ferrer import Partition
        return [Partition(parts=(2,)), Partition(parts=(1, 1))]

    def structure_tree(self) -> 'RootedTree':
        """Get the canonical tree for System 2 structure."""
        from ..trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(
            value="pair",
            children=[
                TreeNode(value="left", children=[]),
                TreeNode(value="right", children=[])
            ]
        ))

    def __repr__(self) -> str:
        return f"System2(embedding_dim={self.embedding_dim})"


# Neural network layers (if torch available)
if TORCH_AVAILABLE:
    class PairLayer(nn.Module):
        """
        Neural network layer for System 2 pair embeddings.

        Processes pairs of inputs through parallel pathways,
        then combines them via a learned composition.

        Architecture:
            left_input  -> left_linear  \\
                                         > composition -> output
            right_input -> right_linear /
        """

        def __init__(
            self,
            in_features: int,
            out_features: int,
            composition: str = "concat",
            bias: bool = True
        ):
            """
            Initialize PairLayer.

            Args:
                in_features: Input dimension for each atom
                out_features: Output dimension
                composition: How to compose ("concat", "sum", "bilinear")
                bias: Whether to use bias in linear layers
            """
            super().__init__()
            self.in_features = in_features
            self.out_features = out_features
            self.composition_type = composition

            # Parallel pathways for left and right
            self.left_linear = nn.Linear(in_features, out_features, bias=bias)
            self.right_linear = nn.Linear(in_features, out_features, bias=bias)

            # Composition layer
            if composition == "concat":
                self.compose = nn.Linear(out_features * 2, out_features, bias=bias)
            elif composition == "bilinear":
                self.compose = nn.Bilinear(out_features, out_features, out_features, bias=bias)
            else:  # sum
                self.compose = None

            self.system = System2(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 1

        def forward(
            self,
            left: torch.Tensor,
            right: torch.Tensor
        ) -> PairEmbedding:
            """
            Forward pass processing a pair of inputs.

            Args:
                left: Left input tensor
                right: Right input tensor

            Returns:
                PairEmbedding containing processed tensors
            """
            left_out = self.left_linear(left)
            right_out = self.right_linear(right)

            left_atom = AtomicEmbedding(data=left_out, semantic_role="left")
            right_atom = AtomicEmbedding(data=right_out, semantic_role="right")

            return PairEmbedding(
                left=left_atom,
                right=right_atom,
                semantic_role="pair_layer_output"
            )

        def forward_composed(
            self,
            left: torch.Tensor,
            right: torch.Tensor
        ) -> AtomicEmbedding:
            """
            Forward pass with composition (returns to System 1).

            Args:
                left: Left input tensor
                right: Right input tensor

            Returns:
                AtomicEmbedding of the composed output
            """
            left_out = self.left_linear(left)
            right_out = self.right_linear(right)

            if self.composition_type == "concat":
                composed = self.compose(torch.cat([left_out, right_out], dim=-1))
            elif self.composition_type == "bilinear":
                composed = self.compose(left_out, right_out)
            else:  # sum
                composed = left_out + right_out

            return AtomicEmbedding(
                data=composed,
                semantic_role="composed_pair"
            )

        def __repr__(self) -> str:
            return f"PairLayer({self.in_features} -> {self.out_features}, composition={self.composition_type})"


    class SiameseLayer(nn.Module):
        """
        Siamese layer: processes pairs with shared weights.

        Both inputs go through the same network, creating
        a symmetric pair embedding.
        """

        def __init__(self, in_features: int, out_features: int, bias: bool = True):
            super().__init__()
            self.shared_linear = nn.Linear(in_features, out_features, bias=bias)
            self.system = System2(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 1

        def forward(self, left: torch.Tensor, right: torch.Tensor) -> PairEmbedding:
            """Process both inputs through shared weights."""
            left_out = self.shared_linear(left)
            right_out = self.shared_linear(right)

            return PairEmbedding(
                left=AtomicEmbedding(data=left_out, semantic_role="siamese_left"),
                right=AtomicEmbedding(data=right_out, semantic_role="siamese_right"),
                pair_type=PairType.SYMMETRIC,
                semantic_role="siamese_output"
            )

        def __repr__(self) -> str:
            return f"SiameseLayer({self.shared_linear.in_features} -> {self.shared_linear.out_features})"

else:
    class PairLayer:
        """Placeholder for PairLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for PairLayer")

    class SiameseLayer:
        """Placeholder for SiameseLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for SiameseLayer")
