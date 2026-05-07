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
    NEST = 0      # System 0: Base nestor, embedding space
    ATOM = 1      # System 1: Unary tensor (a) => {()} = M{2} viz. Monadic relation [1], no nesting
    PAIR = 2      # System 2: Binary nesting (a,b) => {(),()()} = Matula {3,4} viz. Dyadic relation [1,1]
    TRIP = 3      # System 3: Ternary nesting (a,b,c) viz. Triadic relation [1,1,1]
    QUAD = 4      # System 4: Quaternary nesting (a,b,c,d) viz. Tetradic relation [1,1][1,1] => [1,2,1]
    QUIN = 5      # System 5: Quinary nesting (a,b,c,d,e) viz. Pentadic relation [1,1,1,1]
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
class VoidTensor(NestedTensor):
    """
    System 0: Void/Nest tensor - the root embedding space.

    The void is the empty rooted tree with no children.
    It acts as the universal container / base nestor into which
    all higher-system tensors are embedded.

    In tree terms: the root node [] with no children
    In parentheses: [] (root void, distinct from tree nodes)
    In partition: [] (empty partition)

    Notes:
    - The root node '[]' is distinguished from tree nodes '()'
    - System 0 represents the embedding space itself
    - System order = 0 (half the length of inner string = 0)
    """

    @property
    def depth(self) -> int:
        return 0

    @property
    def shape(self) -> TensorShape:
        return TensorShape(dims=())

    @property
    def system(self) -> int:
        return 0

    def flatten(self) -> List[Any]:
        return []

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(value="void", children=[]))

    def to_parentheses(self) -> str:
        return "[]"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        return Partition(parts=())

    def __repr__(self) -> str:
        return "VoidTensor()"


@dataclass
class AtomTensor(NestedTensor):
    """
    System 1: Atomic tensor - the base case.

    An atom is a leaf node with no children. It represents a
    standard tensor with a flat shape (d1, d2, ..., dn).

    In tree terms: a single node with no children
    In parentheses (inner): ()
    In rooted parentheses: [()]
    In partition: [1] (single row of length 1)

    Notes:
    - Nesting depth 0; system order = 1 (half-length of inner string)
    - Matula number 2: the tree with one child
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
    In rooted parentheses: [()()]
    In partition: [2] or [1,1] depending on structure

    Catalan number C_1 = 1, so there's exactly one binary structure.
    System order = 2 (2 nodes in inner tree, half-length = 2).
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

    1. Left-associative: ((a, b), c)  — rooted: [(())()]
    2. Right-associative: (a, (b, c)) — rooted: [(()())] (non-canonical)

    In rooted parentheses (canonical LEFT): [(())()]
    In partition: [3], [2,1], or [1,1,1]

    System order = 3 (3 nodes in inner tree, half-length = 3).
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


@dataclass
class QuadTensor(NestedTensor):
    """
    System 4: Quad tensor - quaternary nesting.

    A quad contains four nested tensors (a, b, c, d) with one of
    C_3 = 5 distinct association structures.

    The 5 association structures correspond to the 5 full binary trees
    with 4 leaves:
    1. LEFT_LEFT:    (((a,b),c),d)   — rooted: [(()())()]
    2. LEFT_RIGHT:   ((a,(b,c)),d)
    3. BALANCED:     ((a,b),(c,d))
    4. RIGHT_LEFT:   (a,((b,c),d))
    5. RIGHT_RIGHT:  (a,(b,(c,d)))

    In rooted parentheses (canonical LEFT_LEFT): [(()())()]
    System order = 4 (4 nodes in inner tree, half-length = 4).

    Notes:
    - Distinguishes quaternary (4 distinct vars) from tetradic (2×2 pairs)
    - Tetradic relations [1,1][1,1] => [1,2,1] have ternary order 3
    - True quaternary order 4 cannot be reduced to compound binary order 2(2)
    """

    class Association(Enum):
        LEFT_LEFT = auto()    # (((a,b),c),d)
        LEFT_RIGHT = auto()   # ((a,(b,c)),d)
        BALANCED = auto()     # ((a,b),(c,d))
        RIGHT_LEFT = auto()   # (a,((b,c),d))
        RIGHT_RIGHT = auto()  # (a,(b,(c,d)))

    first: NestedTensor
    second: NestedTensor
    third: NestedTensor
    fourth: NestedTensor
    association: Association = Association.LEFT_LEFT

    @property
    def depth(self) -> int:
        base_depth = max(
            self.first.depth, self.second.depth,
            self.third.depth, self.fourth.depth
        )
        return 3 + base_depth

    @property
    def shape(self) -> TensorShape:
        s1, s2, s3, s4 = (
            self.first.shape, self.second.shape,
            self.third.shape, self.fourth.shape
        )
        if self.association == self.Association.LEFT_LEFT:
            # (((a,b),c),d)
            ab = TensorShape(dims=(), nested_shapes=(s1, s2))
            abc = TensorShape(dims=(), nested_shapes=(ab, s3))
            return TensorShape(dims=(), nested_shapes=(abc, s4))
        elif self.association == self.Association.LEFT_RIGHT:
            # ((a,(b,c)),d)
            bc = TensorShape(dims=(), nested_shapes=(s2, s3))
            abc = TensorShape(dims=(), nested_shapes=(s1, bc))
            return TensorShape(dims=(), nested_shapes=(abc, s4))
        elif self.association == self.Association.BALANCED:
            # ((a,b),(c,d))
            ab = TensorShape(dims=(), nested_shapes=(s1, s2))
            cd = TensorShape(dims=(), nested_shapes=(s3, s4))
            return TensorShape(dims=(), nested_shapes=(ab, cd))
        elif self.association == self.Association.RIGHT_LEFT:
            # (a,((b,c),d))
            bc = TensorShape(dims=(), nested_shapes=(s2, s3))
            bcd = TensorShape(dims=(), nested_shapes=(bc, s4))
            return TensorShape(dims=(), nested_shapes=(s1, bcd))
        else:  # RIGHT_RIGHT
            # (a,(b,(c,d)))
            cd = TensorShape(dims=(), nested_shapes=(s3, s4))
            bcd = TensorShape(dims=(), nested_shapes=(s2, cd))
            return TensorShape(dims=(), nested_shapes=(s1, bcd))

    @property
    def system(self) -> int:
        return 4

    def flatten(self) -> List[Any]:
        return (
            self.first.flatten() + self.second.flatten() +
            self.third.flatten() + self.fourth.flatten()
        )

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        t1, t2, t3, t4 = (
            self.first.to_tree(), self.second.to_tree(),
            self.third.to_tree(), self.fourth.to_tree()
        )
        a = self.Association
        if self.association == a.LEFT_LEFT:
            ab = TreeNode(value="pair", children=[t1.root, t2.root])
            abc = TreeNode(value="triple", children=[ab, t3.root])
            root = TreeNode(value="quad", children=[abc, t4.root])
        elif self.association == a.LEFT_RIGHT:
            bc = TreeNode(value="pair", children=[t2.root, t3.root])
            abc = TreeNode(value="triple", children=[t1.root, bc])
            root = TreeNode(value="quad", children=[abc, t4.root])
        elif self.association == a.BALANCED:
            ab = TreeNode(value="pair", children=[t1.root, t2.root])
            cd = TreeNode(value="pair", children=[t3.root, t4.root])
            root = TreeNode(value="quad", children=[ab, cd])
        elif self.association == a.RIGHT_LEFT:
            bc = TreeNode(value="pair", children=[t2.root, t3.root])
            bcd = TreeNode(value="triple", children=[bc, t4.root])
            root = TreeNode(value="quad", children=[t1.root, bcd])
        else:  # RIGHT_RIGHT
            cd = TreeNode(value="pair", children=[t3.root, t4.root])
            bcd = TreeNode(value="triple", children=[t2.root, cd])
            root = TreeNode(value="quad", children=[t1.root, bcd])
        return RootedTree(root=root)

    def to_parentheses(self) -> str:
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()
        p4 = self.fourth.to_parentheses()
        a = self.Association
        if self.association == a.LEFT_LEFT:
            return f"((({p1}{p2}){p3}){p4})"
        elif self.association == a.LEFT_RIGHT:
            return f"(({p1}({p2}{p3})){p4})"
        elif self.association == a.BALANCED:
            return f"(({p1}{p2})({p3}{p4}))"
        elif self.association == a.RIGHT_LEFT:
            return f"({p1}(({p2}{p3}){p4}))"
        else:  # RIGHT_RIGHT
            return f"({p1}({p2}({p3}{p4})))"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        depths = sorted(
            [self.first.depth, self.second.depth,
             self.third.depth, self.fourth.depth],
            reverse=True
        )
        if depths[0] == depths[3]:
            return Partition(parts=(4,))
        elif depths[0] == depths[1] == depths[2]:
            return Partition(parts=(3, 1))
        elif depths[1] == depths[2] == depths[3]:
            return Partition(parts=(1, 3))
        elif depths[0] == depths[1] and depths[2] == depths[3]:
            return Partition(parts=(2, 2))
        elif depths[0] == depths[1]:
            return Partition(parts=(2, 1, 1))
        elif depths[2] == depths[3]:
            return Partition(parts=(1, 1, 2))
        else:
            return Partition(parts=(1, 1, 1, 1))

    def __repr__(self) -> str:
        assoc = self.association.name
        return (
            f"QuadTensor({assoc}: {self.first}, {self.second}, "
            f"{self.third}, {self.fourth})"
        )


@dataclass
class QuintTensor(NestedTensor):
    """
    System 5: Quint tensor - quinary nesting.

    A quint contains five nested tensors (a, b, c, d, e) with one of
    C_4 = 14 distinct association structures.

    The canonical (fully left-associative) form:
        ((((a,b),c),d),e)   — rooted: [(((()())())())()]

    In rooted parentheses (canonical LEFT_LEFT_LEFT_LEFT): [(((()())())())()]
    System order = 5 (5 nodes in inner tree, half-length = 5).

    Notes:
    - Pentadic relations have quaternary order
    - 14 distinct structure trees (Catalan(4) = 14)
    """

    class Association(Enum):
        LEFT_LEFT_LEFT = auto()    # ((((a,b),c),d),e)
        LEFT_LEFT_RIGHT = auto()   # (((a,(b,c)),d),e)
        LEFT_BALANCED = auto()     # (((a,b),(c,d)),e)
        LEFT_RIGHT_LEFT = auto()   # ((a,((b,c),d)),e)
        LEFT_RIGHT_RIGHT = auto()  # ((a,(b,(c,d))),e)
        BALANCED_LEFT = auto()     # ((a,b),((c,d),e)) - balanced split
        BALANCED_RIGHT = auto()    # ((a,b),(c,(d,e)))
        RIGHT_LEFT_LEFT = auto()   # (a,(((b,c),d),e))
        RIGHT_LEFT_RIGHT = auto()  # (a,((b,(c,d)),e))
        RIGHT_BALANCED = auto()    # (a,((b,c),(d,e)))
        RIGHT_RIGHT_LEFT = auto()  # (a,(b,((c,d),e)))
        RIGHT_RIGHT_RIGHT = auto() # (a,(b,(c,(d,e))))
        SPLIT_LEFT = auto()        # ((a,(b,c)),(d,e))
        SPLIT_RIGHT = auto()       # (((a,b),c),(d,e))

    first: NestedTensor
    second: NestedTensor
    third: NestedTensor
    fourth: NestedTensor
    fifth: NestedTensor
    association: Association = Association.LEFT_LEFT_LEFT

    @property
    def depth(self) -> int:
        base_depth = max(
            self.first.depth, self.second.depth, self.third.depth,
            self.fourth.depth, self.fifth.depth
        )
        return 4 + base_depth

    @property
    def shape(self) -> TensorShape:
        s1, s2, s3, s4, s5 = (
            self.first.shape, self.second.shape, self.third.shape,
            self.fourth.shape, self.fifth.shape
        )
        # Return shape for canonical left-associative form
        # (full shape enumeration for all 14 variants omitted for brevity)
        ab = TensorShape(dims=(), nested_shapes=(s1, s2))
        abc = TensorShape(dims=(), nested_shapes=(ab, s3))
        abcd = TensorShape(dims=(), nested_shapes=(abc, s4))
        return TensorShape(dims=(), nested_shapes=(abcd, s5))

    @property
    def system(self) -> int:
        return 5

    def flatten(self) -> List[Any]:
        return (
            self.first.flatten() + self.second.flatten() +
            self.third.flatten() + self.fourth.flatten() +
            self.fifth.flatten()
        )

    def to_tree(self) -> 'RootedTree':
        from .trees import RootedTree, TreeNode
        t1, t2, t3, t4, t5 = (
            self.first.to_tree(), self.second.to_tree(),
            self.third.to_tree(), self.fourth.to_tree(),
            self.fifth.to_tree()
        )
        a = self.Association
        if self.association == a.LEFT_LEFT_LEFT:
            ab = TreeNode(value="pair", children=[t1.root, t2.root])
            abc = TreeNode(value="triple", children=[ab, t3.root])
            abcd = TreeNode(value="quad", children=[abc, t4.root])
            root = TreeNode(value="quint", children=[abcd, t5.root])
        else:
            # Fallback: flat n-ary node for unimplemented associations
            root = TreeNode(
                value="quint",
                children=[t1.root, t2.root, t3.root, t4.root, t5.root],
                metadata={"association": self.association.name}
            )
        return RootedTree(root=root)

    def to_parentheses(self) -> str:
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()
        p4 = self.fourth.to_parentheses()
        p5 = self.fifth.to_parentheses()
        a = self.Association
        if self.association == a.LEFT_LEFT_LEFT:
            return f"(((({p1}{p2}){p3}){p4}){p5})"
        elif self.association == a.LEFT_LEFT_RIGHT:
            return f"((({p1}({p2}{p3})){p4}){p5})"
        elif self.association == a.LEFT_BALANCED:
            return f"((({p1}{p2})({p3}{p4})){p5})"
        elif self.association == a.LEFT_RIGHT_LEFT:
            return f"(({p1}(({p2}{p3}){p4})){p5})"
        elif self.association == a.LEFT_RIGHT_RIGHT:
            return f"(({p1}({p2}({p3}{p4}))){p5})"
        elif self.association == a.BALANCED_LEFT:
            return f"(({p1}{p2})(({p3}{p4}){p5}))"
        elif self.association == a.BALANCED_RIGHT:
            return f"(({p1}{p2})({p3}({p4}{p5})))"
        elif self.association == a.RIGHT_LEFT_LEFT:
            return f"({p1}((({p2}{p3}){p4}){p5}))"
        elif self.association == a.RIGHT_LEFT_RIGHT:
            return f"({p1}(({p2}({p3}{p4})){p5}))"
        elif self.association == a.RIGHT_BALANCED:
            return f"({p1}(({p2}{p3})({p4}{p5})))"
        elif self.association == a.RIGHT_RIGHT_LEFT:
            return f"({p1}({p2}(({p3}{p4}){p5})))"
        elif self.association == a.RIGHT_RIGHT_RIGHT:
            return f"({p1}({p2}({p3}({p4}{p5}))))"
        elif self.association == a.SPLIT_LEFT:
            return f"(({p1}({p2}{p3}))({p4}{p5}))"
        else:  # SPLIT_RIGHT
            return f"((({p1}{p2}){p3})({p4}{p5}))"

    def to_partition(self) -> 'Partition':
        from .ferrer import Partition
        depths = sorted(
            [self.first.depth, self.second.depth, self.third.depth,
             self.fourth.depth, self.fifth.depth],
            reverse=True
        )
        if depths[0] == depths[4]:
            return Partition(parts=(5,))
        elif depths[0] == depths[1] == depths[2] == depths[3]:
            return Partition(parts=(4, 1))
        elif depths[1] == depths[2] == depths[3] == depths[4]:
            return Partition(parts=(1, 4))
        elif depths[0] == depths[1] == depths[2]:
            return Partition(parts=(3, 1, 1))
        elif depths[2] == depths[3] == depths[4]:
            return Partition(parts=(1, 1, 3))
        elif depths[0] == depths[1] and depths[3] == depths[4]:
            return Partition(parts=(2, 1, 2))
        elif depths[0] == depths[1]:
            return Partition(parts=(2, 1, 1, 1))
        elif depths[3] == depths[4]:
            return Partition(parts=(1, 1, 1, 2))
        else:
            return Partition(parts=(1, 1, 1, 1, 1))

    def __repr__(self) -> str:
        assoc = self.association.name
        return (
            f"QuintTensor({assoc}: {self.first}, {self.second}, "
            f"{self.third}, {self.fourth}, {self.fifth})"
        )


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

    System 0 has 1 structure (the void).
    System K (K >= 1) has C_{K-1} distinct structures where C is the Catalan number.
    """
    if system < 0:
        raise ValueError("System number must be >= 0")
    if system == 0:
        return 1  # Only the void
    return catalan(system - 1)


def nesting_depth(system: int) -> int:
    """
    Return the maximum nesting depth for a given System.

    System 0 has depth 0 (void/empty).
    System K (K >= 1) has maximum depth K-1 (System 1 has depth 0, etc.)
    """
    if system < 0:
        raise ValueError("System number must be >= 0")
    if system == 0:
        return 0
    return system - 1
