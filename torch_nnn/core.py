"""
Core nested tensor embedding classes.

Mathematical Foundation:
-----------------------
Nested tensors extend standard tensors by allowing recursive structure.
A nested tensor of depth D is either:
  - D=0: A base tensor (atom/leaf)
  - D>0: A tuple of nested tensors of depth ≤ D-1

This mirrors:
  - Rooted trees: depth = max path length from root
  - Ferrer diagrams: depth = number of rows in partition
  - Nested parentheses: depth = max nesting level

The embedding space for System-K has dimensionality that grows
with the Catalan structure of valid nestings.
"""

from __future__ import annotations
from typing import Union, Tuple, List, Optional, Iterator, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
import math


class NestingLevel(Enum):
    """Enumeration of nesting depths corresponding to Systems."""
    ATOM = 0      # System 1: Base tensor, no nesting
    PAIR = 1      # System 2: Binary nesting (a, b)
    TRIPLE = 2    # System 3: Ternary nesting
    QUAD = 3      # System 4: Quaternary nesting
    QUINT = 4     # System 5: Quinary nesting
    # Extensible to System-N


@dataclass
class TensorShape:
    """
    Represents the shape of a nested tensor.

    For nested tensors, shape is itself nested:
    - Atom: (d1, d2, ..., dn) - standard tuple
    - Pair: ((shape1), (shape2)) - nested tuple
    - Triple: (((s1), (s2)), (s3)) - deeper nesting
    """
    dims: Tuple[int, ...]
    nested_shapes: Optional[Tuple['TensorShape', ...]] = None

    @property
    def is_atomic(self) -> bool:
        """True if this is a leaf/atom shape with no nested structure."""
        return self.nested_shapes is None

    @property
    def depth(self) -> int:
        """Compute the nesting depth of this shape."""
        if self.is_atomic:
            return 0
        return 1 + max(s.depth for s in self.nested_shapes)

    @property
    def total_dims(self) -> int:
        """Total number of dimensions across all nested shapes."""
        if self.is_atomic:
            return len(self.dims)
        return sum(s.total_dims for s in self.nested_shapes)

    def to_tuple(self) -> Union[Tuple[int, ...], Tuple[Any, ...]]:
        """Convert to nested tuple representation."""
        if self.is_atomic:
            return self.dims
        return tuple(s.to_tuple() for s in self.nested_shapes)

    @classmethod
    def from_tuple(cls, t: Union[Tuple[int, ...], Tuple[Any, ...]]) -> 'TensorShape':
        """Construct TensorShape from nested tuple."""
        if all(isinstance(x, int) for x in t):
            return cls(dims=t)
        nested = tuple(cls.from_tuple(x) for x in t)
        return cls(dims=(), nested_shapes=nested)

    def __repr__(self) -> str:
        return f"TensorShape({self.to_tuple()})"


class NestedTensor(ABC):
    """
    Abstract base class for nested tensors.

    A nested tensor represents a hierarchical embedding structure where
    tensors can contain other tensors, forming a tree-like structure.

    Mathematical Properties:
    -----------------------
    1. Nesting Depth: Maximum depth of the tree structure
    2. Branching Factor: Number of children at each node
    3. Catalan Structure: Number of valid nesting patterns
    4. Partition Signature: Ferrer diagram representation

    The nesting corresponds to:
    - () = atom (System 1)
    - (()) = pair containing atom (System 2)
    - ((())) or (()()) = triple structures (System 3)
    """

    @property
    @abstractmethod
    def depth(self) -> int:
        """Return the nesting depth of this tensor."""
        pass

    @property
    @abstractmethod
    def shape(self) -> TensorShape:
        """Return the nested shape of this tensor."""
        pass

    @property
    @abstractmethod
    def system(self) -> int:
        """Return the System number (1, 2, 3, ...) for this tensor."""
        pass

    @abstractmethod
    def flatten(self) -> List[Any]:
        """Flatten nested structure to list of atoms."""
        pass

    @abstractmethod
    def to_tree(self) -> 'RootedTree':
        """Convert to rooted tree representation."""
        pass

    @abstractmethod
    def to_parentheses(self) -> str:
        """Convert to nested parentheses string representation."""
        pass

    @abstractmethod
    def to_partition(self) -> 'Partition':
        """Convert to Ferrer diagram partition representation."""
        pass


@dataclass
class AtomTensor(NestedTensor):
    """
    System 1: Atomic tensor - the base case.

    An atom is a leaf node with no children. It represents a
    standard tensor with a flat shape (d1, d2, ..., dn).

    In tree terms: a single node with no children
    In parentheses: ()
    In partition: [1] (single row of length 1)
    """
    data: Any  # The actual tensor data (torch.Tensor, numpy array, etc.)
    _shape: TensorShape = field(default_factory=lambda: TensorShape(dims=(1,)))

    def __post_init__(self):
        # Infer shape from data if possible
        if hasattr(self.data, 'shape'):
            self._shape = TensorShape(dims=tuple(self.data.shape))
        elif isinstance(self.data, (int, float)):
            self._shape = TensorShape(dims=())  # Scalar

    @property
    def depth(self) -> int:
        return 0

    @property
    def shape(self) -> TensorShape:
        return self._shape

    @property
    def system(self) -> int:
        return 1

    def flatten(self) -> List[Any]:
        return [self.data]

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(value=self.data, children=[]))

    def to_parentheses(self) -> str:
        return "()"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        return Partition(parts=(1,))

    def __repr__(self) -> str:
        return f"AtomTensor(shape={self._shape.dims})"


@dataclass
class PairTensor(NestedTensor):
    """
    System 2: Pair tensor - binary nesting.

    A pair contains exactly two nested tensors, which may be
    atoms or further nested structures.

    Structure: (left, right)

    In tree terms: a node with exactly 2 children
    In parentheses: (()()) for two atoms, ((())()) for nested left
    In partition: [2] or [1,1] depending on structure

    Catalan number C_1 = 1, so there's exactly one binary structure.
    """
    left: NestedTensor
    right: NestedTensor

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    @property
    def shape(self) -> TensorShape:
        return TensorShape(
            dims=(),
            nested_shapes=(self.left.shape, self.right.shape)
        )

    @property
    def system(self) -> int:
        return 2

    def flatten(self) -> List[Any]:
        return self.left.flatten() + self.right.flatten()

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        left_tree = self.left.to_tree()
        right_tree = self.right.to_tree()
        return RootedTree(
            root=TreeNode(
                value="pair",
                children=[left_tree.root, right_tree.root]
            )
        )

    def to_parentheses(self) -> str:
        return f"({self.left.to_parentheses()}{self.right.to_parentheses()})"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        # Pair structure maps to partition [2] or [1,1]
        left_depth = self.left.depth
        right_depth = self.right.depth
        if left_depth == right_depth:
            return Partition(parts=(2,))  # Balanced: [2]
        return Partition(parts=(1, 1))  # Unbalanced: [1,1]

    def __repr__(self) -> str:
        return f"PairTensor(left={self.left}, right={self.right})"


@dataclass
class TripleTensor(NestedTensor):
    """
    System 3: Triple tensor - ternary nesting.

    A triple contains three nested tensors with a specific
    association structure. There are C_2 = 2 distinct structures:

    1. Left-associative: ((a, b), c)
    2. Right-associative: (a, (b, c))

    In tree terms: a node with 3 leaves, but internal structure varies
    In parentheses: ((()())()) or (()(()()))
    In partition: [3], [2,1], or [1,1,1]
    """

    class Association(Enum):
        LEFT = auto()   # ((a, b), c)
        RIGHT = auto()  # (a, (b, c))

    first: NestedTensor
    second: NestedTensor
    third: NestedTensor
    association: Association = Association.LEFT

    @property
    def depth(self) -> int:
        base_depth = max(self.first.depth, self.second.depth, self.third.depth)
        return 2 + base_depth  # Triple adds 2 levels of nesting

    @property
    def shape(self) -> TensorShape:
        if self.association == self.Association.LEFT:
            # ((first, second), third)
            inner = TensorShape(
                dims=(),
                nested_shapes=(self.first.shape, self.second.shape)
            )
            return TensorShape(dims=(), nested_shapes=(inner, self.third.shape))
        else:
            # (first, (second, third))
            inner = TensorShape(
                dims=(),
                nested_shapes=(self.second.shape, self.third.shape)
            )
            return TensorShape(dims=(), nested_shapes=(self.first.shape, inner))

    @property
    def system(self) -> int:
        return 3

    def flatten(self) -> List[Any]:
        return self.first.flatten() + self.second.flatten() + self.third.flatten()

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        t1 = self.first.to_tree()
        t2 = self.second.to_tree()
        t3 = self.third.to_tree()

        if self.association == self.Association.LEFT:
            # ((a, b), c)
            inner = TreeNode(value="pair", children=[t1.root, t2.root])
            return RootedTree(root=TreeNode(value="triple", children=[inner, t3.root]))
        else:
            # (a, (b, c))
            inner = TreeNode(value="pair", children=[t2.root, t3.root])
            return RootedTree(root=TreeNode(value="triple", children=[t1.root, inner]))

    def to_parentheses(self) -> str:
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()

        if self.association == self.Association.LEFT:
            return f"(({p1}{p2}){p3})"
        else:
            return f"({p1}({p2}{p3}))"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        # Map triple structure to partition based on depths
        depths = sorted([self.first.depth, self.second.depth, self.third.depth], reverse=True)
        if depths[0] == depths[1] == depths[2]:
            return Partition(parts=(3,))  # All equal: [3]
        elif depths[0] == depths[1] or depths[1] == depths[2]:
            return Partition(parts=(2, 1))  # Two equal: [2,1]
        else:
            return Partition(parts=(1, 1, 1))  # All different: [1,1,1]

    def __repr__(self) -> str:
        assoc = "L" if self.association == self.Association.LEFT else "R"
        return f"TripleTensor({assoc}: {self.first}, {self.second}, {self.third})"


def catalan(n: int) -> int:
    """
    Compute the n-th Catalan number.

    C_n = (2n)! / ((n+1)! * n!)

    Catalan numbers count:
    - Valid parenthesizations of n+1 factors
    - Full binary trees with n+1 leaves
    - Paths in a grid that don't cross the diagonal
    - Distinct nesting structures in System-(n+1)
    """
    if n <= 1:
        return 1
    return math.comb(2 * n, n) // (n + 1)


def count_structures(system: int) -> int:
    """
    Count the number of distinct nesting structures for a given System.

    System K has C_{K-1} distinct structures where C is the Catalan number.
    """
    if system < 1:
        raise ValueError("System number must be >= 1")
    return catalan(system - 1)


def nesting_depth(system: int) -> int:
    """
    Return the maximum nesting depth for a given System.

    System K has maximum depth K-1 (System 1 has depth 0, etc.)
    """
    return system - 1
