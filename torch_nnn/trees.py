"""
Rooted tree representations for nested tensor structures.

Mathematical Foundation:
-----------------------
A rooted tree is a connected acyclic graph with a distinguished root node.
Each nested tensor corresponds to a unique rooted tree where:
  - Leaves = Atomic tensors (System 1)
  - Internal nodes = Nesting operations (Pair, Triple, etc.)
  - Depth = Maximum path length from root to leaf
  - Branching = Number of children (arity of nesting)

Key Properties:
- System K tensors have trees with at most K leaves
- The number of distinct tree shapes is the Catalan number C_{K-1}
- Trees can be serialized as nested parentheses (Dyck words)
"""

from __future__ import annotations
from typing import List, Optional, Any, Iterator, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto
import functools


T = TypeVar('T')


class NodeType(Enum):
    """Type of node in the rooted tree."""
    LEAF = auto()       # Atomic tensor (no children)
    BINARY = auto()     # Pair node (2 children)
    TERNARY = auto()    # Triple node (3 children)
    NARY = auto()       # General n-ary node


@dataclass
class TreeNode:
    """
    A node in a rooted tree representing nested tensor structure.

    Each node contains:
    - value: The data at this node (tensor for leaves, label for internal)
    - children: List of child nodes (empty for leaves)
    - metadata: Optional additional information
    """
    value: Any
    children: List['TreeNode'] = field(default_factory=list)
    metadata: Optional[dict] = None

    @property
    def is_leaf(self) -> bool:
        """True if this node has no children."""
        return len(self.children) == 0

    @property
    def arity(self) -> int:
        """Number of children (branching factor)."""
        return len(self.children)

    @property
    def node_type(self) -> NodeType:
        """Determine the type of this node based on arity."""
        if self.arity == 0:
            return NodeType.LEAF
        elif self.arity == 2:
            return NodeType.BINARY
        elif self.arity == 3:
            return NodeType.TERNARY
        else:
            return NodeType.NARY

    @property
    def depth(self) -> int:
        """Compute depth of subtree rooted at this node."""
        if self.is_leaf:
            return 0
        return 1 + max(child.depth for child in self.children)

    @property
    def size(self) -> int:
        """Total number of nodes in subtree."""
        if self.is_leaf:
            return 1
        return 1 + sum(child.size for child in self.children)

    @property
    def leaf_count(self) -> int:
        """Number of leaves in subtree."""
        if self.is_leaf:
            return 1
        return sum(child.leaf_count for child in self.children)

    def leaves(self) -> Iterator['TreeNode']:
        """Iterate over all leaves in subtree (left to right)."""
        if self.is_leaf:
            yield self
        else:
            for child in self.children:
                yield from child.leaves()

    def preorder(self) -> Iterator['TreeNode']:
        """Preorder traversal: root, then children left to right."""
        yield self
        for child in self.children:
            yield from child.preorder()

    def postorder(self) -> Iterator['TreeNode']:
        """Postorder traversal: children left to right, then root."""
        for child in self.children:
            yield from child.postorder()
        yield self

    def map(self, f: Callable[[Any], Any]) -> 'TreeNode':
        """Apply function to all values, returning new tree."""
        new_children = [child.map(f) for child in self.children]
        return TreeNode(
            value=f(self.value),
            children=new_children,
            metadata=self.metadata.copy() if self.metadata else None
        )

    def fold(self, leaf_fn: Callable[[Any], T],
             node_fn: Callable[[Any, List[T]], T]) -> T:
        """
        Catamorphism (fold) over the tree.

        leaf_fn: Applied to leaf values
        node_fn: Applied to internal node value and list of child results
        """
        if self.is_leaf:
            return leaf_fn(self.value)
        child_results = [child.fold(leaf_fn, node_fn) for child in self.children]
        return node_fn(self.value, child_results)

    def to_parentheses(self) -> str:
        """Convert to nested parentheses representation."""
        if self.is_leaf:
            return "()"
        inner = "".join(child.to_parentheses() for child in self.children)
        return f"({inner})"

    def to_tuple(self) -> Any:
        """Convert to nested tuple representation."""
        if self.is_leaf:
            return self.value
        return tuple(child.to_tuple() for child in self.children)

    def pretty_print(self, prefix: str = "", is_last: bool = True) -> str:
        """Generate ASCII tree representation."""
        connector = "└── " if is_last else "├── "
        result = prefix + connector + str(self.value) + "\n"

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            result += child.pretty_print(new_prefix, is_last_child)

        return result

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"Leaf({self.value})"
        return f"Node({self.value}, children={len(self.children)})"


@dataclass
class RootedTree:
    """
    A rooted tree representing the structure of a nested tensor.

    The tree captures the hierarchical nesting pattern:
    - System 1: Single leaf node
    - System 2: Binary tree (one internal node, two leaves)
    - System 3: Trees with 3 leaves (Catalan(2) = 2 shapes)

    Isomorphisms:
    - Nested tuples: tree <-> ((a, b), c) or (a, (b, c))
    - Dyck paths: tree <-> balanced parentheses
    - Ferrer diagrams: tree shape <-> partition
    """
    root: TreeNode

    @property
    def depth(self) -> int:
        """Maximum depth of the tree."""
        return self.root.depth

    @property
    def size(self) -> int:
        """Total number of nodes."""
        return self.root.size

    @property
    def leaf_count(self) -> int:
        """Number of leaves (= System number)."""
        return self.root.leaf_count

    @property
    def system(self) -> int:
        """Infer System number from leaf count."""
        return self.root.leaf_count

    def leaves(self) -> Iterator[TreeNode]:
        """Iterate over leaves."""
        return self.root.leaves()

    def leaf_values(self) -> List[Any]:
        """Get values of all leaves."""
        return [leaf.value for leaf in self.leaves()]

    def to_parentheses(self) -> str:
        """Convert to Dyck word (balanced parentheses)."""
        return self.root.to_parentheses()

    def to_tuple(self) -> Any:
        """Convert to nested tuple."""
        return self.root.to_tuple()

    @classmethod
    def from_tuple(cls, t: Any) -> 'RootedTree':
        """Construct tree from nested tuple."""
        if not isinstance(t, tuple):
            # Leaf
            return cls(root=TreeNode(value=t, children=[]))

        # Internal node
        children = [cls.from_tuple(child).root for child in t]
        return cls(root=TreeNode(value="node", children=children))

    @classmethod
    def from_parentheses(cls, s: str) -> 'RootedTree':
        """
        Construct tree from balanced parentheses string.

        Examples:
        - "()" -> single leaf (System 1)
        - "(()())" -> binary tree with 2 leaves (System 2)
        - "((()())())" -> left-assoc triple (System 3)
        """
        def parse(s: str, pos: int) -> tuple[TreeNode, int]:
            if pos >= len(s) or s[pos] != '(':
                raise ValueError(f"Expected '(' at position {pos}")

            pos += 1  # consume '('

            if s[pos] == ')':
                # Leaf: ()
                return TreeNode(value="leaf", children=[]), pos + 1

            # Internal node: collect children until ')'
            children = []
            while pos < len(s) and s[pos] != ')':
                child, pos = parse(s, pos)
                children.append(child)

            if pos >= len(s) or s[pos] != ')':
                raise ValueError(f"Expected ')' at position {pos}")

            return TreeNode(value="node", children=children), pos + 1

        root, end_pos = parse(s, 0)
        if end_pos != len(s):
            raise ValueError(f"Extra characters after position {end_pos}")

        return cls(root=root)

    def is_isomorphic(self, other: 'RootedTree') -> bool:
        """Check if two trees have the same shape (ignoring values)."""
        def same_shape(n1: TreeNode, n2: TreeNode) -> bool:
            if n1.arity != n2.arity:
                return False
            return all(
                same_shape(c1, c2)
                for c1, c2 in zip(n1.children, n2.children)
            )
        return same_shape(self.root, other.root)

    def canonical_form(self) -> str:
        """
        Compute canonical string form for shape comparison.

        This is the lexicographically smallest parentheses form
        among all equivalent representations.
        """
        def canonical(node: TreeNode) -> str:
            if node.is_leaf:
                return "()"
            child_forms = sorted(canonical(c) for c in node.children)
            return "(" + "".join(child_forms) + ")"

        return canonical(self.root)

    def __repr__(self) -> str:
        return f"RootedTree(depth={self.depth}, leaves={self.leaf_count})"

    def __str__(self) -> str:
        return self.root.pretty_print(prefix="", is_last=True)


# Tree construction utilities

def leaf(value: Any = None) -> RootedTree:
    """Create a single-leaf tree (System 1)."""
    return RootedTree(root=TreeNode(value=value or "leaf", children=[]))


def pair(left: RootedTree, right: RootedTree, label: str = "pair") -> RootedTree:
    """Create a binary tree from two subtrees."""
    return RootedTree(
        root=TreeNode(
            value=label,
            children=[left.root, right.root]
        )
    )


def triple_left(a: RootedTree, b: RootedTree, c: RootedTree) -> RootedTree:
    """Create left-associative triple: ((a, b), c)"""
    ab = pair(a, b, label="inner")
    return pair(ab, c, label="triple")


def triple_right(a: RootedTree, b: RootedTree, c: RootedTree) -> RootedTree:
    """Create right-associative triple: (a, (b, c))"""
    bc = pair(b, c, label="inner")
    return pair(a, bc, label="triple")


def enumerate_binary_trees(n: int) -> Iterator[RootedTree]:
    """
    Enumerate all distinct binary tree shapes with n leaves.

    This generates Catalan(n-1) trees for n >= 1.
    """
    if n == 1:
        yield leaf()
        return

    # For n > 1, split into left and right subtrees
    for k in range(1, n):
        # k leaves on left, (n-k) leaves on right
        for left_tree in enumerate_binary_trees(k):
            for right_tree in enumerate_binary_trees(n - k):
                yield pair(left_tree, right_tree)


def count_binary_trees(n: int) -> int:
    """Count binary trees with n leaves (Catalan number C_{n-1})."""
    from .core import catalan
    return catalan(n - 1)
