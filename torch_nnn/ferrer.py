"""
Ferrer/Young diagram representations for nested tensor structures.

Mathematical Foundation:
-----------------------
A Ferrer diagram (or Young diagram) is a graphical representation of
an integer partition. A partition of n is a way of writing n as a sum
of positive integers, where order doesn't matter.

For example, partitions of 4:
  [4]       = ████
  [3,1]     = ███
              █
  [2,2]     = ██
              ██
  [2,1,1]   = ██
              █
              █
  [1,1,1,1] = █
              █
              █
              █

Connection to Nested Tensors:
- Partition [n] = single tensor of dimension n (flat)
- Partition [k, m] = nested pair with dimensions k and m
- Shape of partition = nesting structure

The conjugate (transpose) of a partition gives the dual nesting.
"""

from __future__ import annotations
from typing import Tuple, List, Iterator, Optional
from dataclasses import dataclass
import functools


@dataclass(frozen=True)
class Partition:
    """
    An integer partition represented as a tuple of parts.

    Parts are stored in non-increasing order: parts[0] >= parts[1] >= ...

    Properties:
    - n (weight): sum of all parts
    - length: number of parts
    - width: largest part (first part)
    """
    parts: Tuple[int, ...]

    def __post_init__(self):
        # Validate: parts must be non-increasing positive integers
        for i, p in enumerate(self.parts):
            if p <= 0:
                raise ValueError(f"Parts must be positive, got {p}")
            if i > 0 and p > self.parts[i - 1]:
                raise ValueError("Parts must be non-increasing")

    @classmethod
    def from_list(cls, parts: List[int]) -> 'Partition':
        """Create partition from list, sorting into canonical form."""
        sorted_parts = tuple(sorted(parts, reverse=True))
        # Remove zeros
        sorted_parts = tuple(p for p in sorted_parts if p > 0)
        if not sorted_parts:
            sorted_parts = (0,)  # Empty partition
        return cls(parts=sorted_parts)

    @property
    def n(self) -> int:
        """Weight of partition (sum of parts)."""
        return sum(self.parts)

    @property
    def weight(self) -> int:
        """Alias for n."""
        return self.n

    @property
    def length(self) -> int:
        """Number of parts (rows in Ferrer diagram)."""
        return len(self.parts)

    @property
    def width(self) -> int:
        """Largest part (columns in Ferrer diagram)."""
        return self.parts[0] if self.parts else 0

    def conjugate(self) -> 'Partition':
        """
        Compute the conjugate (transpose) partition.

        The conjugate swaps rows and columns in the Ferrer diagram.

        Example: [4,2,1] -> [3,2,1,1]
        ████      ██
        ██    ->  ██
        █         █
                  █
        """
        if not self.parts or self.parts[0] == 0:
            return Partition(parts=(0,))

        # Count how many parts are >= each value
        conjugate_parts = []
        for j in range(1, self.parts[0] + 1):
            count = sum(1 for p in self.parts if p >= j)
            if count > 0:
                conjugate_parts.append(count)

        return Partition(parts=tuple(conjugate_parts))

    def hook_length(self, i: int, j: int) -> int:
        """
        Compute hook length at position (i, j) (0-indexed).

        Hook length = cells to the right + cells below + 1

        Used in the hook length formula for counting standard tableaux.
        """
        if i >= self.length or j >= self.parts[i]:
            raise ValueError(f"Position ({i},{j}) out of bounds")

        # Cells to the right in row i
        arm = self.parts[i] - j - 1

        # Cells below in column j
        leg = sum(1 for k in range(i + 1, self.length) if self.parts[k] > j)

        return arm + leg + 1

    def hook_lengths(self) -> List[List[int]]:
        """Compute all hook lengths as a 2D array."""
        return [
            [self.hook_length(i, j) for j in range(self.parts[i])]
            for i in range(self.length)
        ]

    def dimension(self) -> int:
        """
        Compute dimension of corresponding irrep of S_n.

        Uses the hook length formula:
        dim = n! / (product of all hook lengths)
        """
        import math
        hooks = self.hook_lengths()
        product = 1
        for row in hooks:
            for h in row:
                product *= h
        return math.factorial(self.n) // product

    def to_diagram(self, box: str = "█", empty: str = " ") -> str:
        """Render as ASCII Ferrer diagram."""
        lines = []
        for p in self.parts:
            lines.append(box * p)
        return "\n".join(lines)

    def to_brackets(self) -> str:
        """Render as bracket notation: [4,2,1]."""
        return "[" + ",".join(str(p) for p in self.parts) + "]"

    @property
    def depth(self) -> int:
        """
        Nesting depth interpretation.

        For tensor embeddings:
        - [n] has depth 0 (flat tensor)
        - [k, m, ...] has depth = length - 1
        """
        return self.length - 1

    @property
    def system(self) -> int:
        """
        Infer System number from partition.

        System K corresponds to partitions of K.
        """
        return self.n

    def dominates(self, other: 'Partition') -> bool:
        """
        Check if self dominates other in dominance order.

        λ dominates μ if sum(λ[:k]) >= sum(μ[:k]) for all k.
        """
        if self.n != other.n:
            raise ValueError("Can only compare partitions of same n")

        sum_self = 0
        sum_other = 0
        max_len = max(self.length, other.length)

        for k in range(max_len):
            if k < self.length:
                sum_self += self.parts[k]
            if k < other.length:
                sum_other += other.parts[k]
            if sum_self < sum_other:
                return False

        return True

    def __iter__(self) -> Iterator[int]:
        return iter(self.parts)

    def __getitem__(self, i: int) -> int:
        if i < self.length:
            return self.parts[i]
        return 0  # Parts beyond length are 0

    def __repr__(self) -> str:
        return f"Partition{self.parts}"


@dataclass
class FerrerDiagram:
    """
    A Ferrer diagram with additional structure for nested tensor mapping.

    Beyond the basic partition, this tracks:
    - Labels for each box (for tensor dimension mapping)
    - Nesting structure interpretation
    - Conversion to/from tree representation
    """
    partition: Partition
    labels: Optional[List[List[str]]] = None

    def __post_init__(self):
        if self.labels is None:
            # Default labels: row,col coordinates
            self.labels = [
                [f"({i},{j})" for j in range(self.partition.parts[i])]
                for i in range(self.partition.length)
            ]

    @property
    def n(self) -> int:
        return self.partition.n

    @property
    def shape(self) -> Tuple[int, ...]:
        """Return the partition as a shape tuple."""
        return self.partition.parts

    def row(self, i: int) -> List[str]:
        """Get labels in row i."""
        if i >= len(self.labels):
            return []
        return self.labels[i]

    def column(self, j: int) -> List[str]:
        """Get labels in column j."""
        col = []
        for i, row in enumerate(self.labels):
            if j < len(row):
                col.append(row[j])
        return col

    def corners(self) -> List[Tuple[int, int]]:
        """
        Find corner positions (removable boxes).

        A box at (i,j) is a corner if removing it still gives a valid partition.
        """
        corners = []
        for i in range(self.partition.length):
            j = self.partition.parts[i] - 1
            # Check if (i, j) is a corner
            is_corner = True
            if i + 1 < self.partition.length:
                if self.partition.parts[i + 1] >= self.partition.parts[i]:
                    is_corner = False
            if is_corner:
                corners.append((i, j))
        return corners

    def add_box(self, i: int, label: str = "new") -> 'FerrerDiagram':
        """Add a box to row i, if valid."""
        new_parts = list(self.partition.parts)
        if i < len(new_parts):
            new_parts[i] += 1
        else:
            new_parts.append(1)

        # Check validity
        if i > 0 and new_parts[i] > new_parts[i - 1]:
            raise ValueError(f"Cannot add box to row {i}")

        new_labels = [row.copy() for row in self.labels]
        if i < len(new_labels):
            new_labels[i].append(label)
        else:
            new_labels.append([label])

        return FerrerDiagram(
            partition=Partition(parts=tuple(new_parts)),
            labels=new_labels
        )

    def remove_corner(self, i: int) -> 'FerrerDiagram':
        """Remove the corner box from row i."""
        corners = self.corners()
        corner_rows = [c[0] for c in corners]
        if i not in corner_rows:
            raise ValueError(f"Row {i} does not have a removable corner")

        new_parts = list(self.partition.parts)
        new_parts[i] -= 1
        if new_parts[i] == 0:
            new_parts = new_parts[:i]

        new_labels = [row.copy() for row in self.labels]
        new_labels[i] = new_labels[i][:-1]
        if not new_labels[i]:
            new_labels = new_labels[:i]

        return FerrerDiagram(
            partition=Partition(parts=tuple(new_parts)) if new_parts else Partition(parts=(0,)),
            labels=new_labels if new_labels else [[]]
        )

    def to_tree(self) -> 'RootedTree':
        """
        Convert Ferrer diagram to rooted tree.

        The conversion interprets rows as nesting levels:
        - Row 0 (longest) = outermost nesting
        - Row k = nesting at depth k
        """
        from .trees import RootedTree, TreeNode

        if self.partition.n == 0:
            return RootedTree(root=TreeNode(value="empty", children=[]))

        if self.partition.length == 1:
            # Single row = flat structure
            children = [
                TreeNode(value=label, children=[])
                for label in self.labels[0]
            ]
            return RootedTree(
                root=TreeNode(value="row", children=children)
            )

        # Multiple rows = nested structure
        # Each column becomes a path from root to leaf
        def build_column_tree(col: int) -> TreeNode:
            col_labels = self.column(col)
            if len(col_labels) == 1:
                return TreeNode(value=col_labels[0], children=[])
            # Nested: first label contains rest
            inner = build_column_tree_recursive(col_labels[1:])
            return TreeNode(value=col_labels[0], children=[inner])

        def build_column_tree_recursive(labels: List[str]) -> TreeNode:
            if len(labels) == 1:
                return TreeNode(value=labels[0], children=[])
            inner = build_column_tree_recursive(labels[1:])
            return TreeNode(value=labels[0], children=[inner])

        column_trees = []
        for j in range(self.partition.width):
            column_trees.append(build_column_tree(j))

        return RootedTree(
            root=TreeNode(value="diagram", children=column_trees)
        )

    def to_ascii(self) -> str:
        """Render as ASCII diagram with labels."""
        lines = []
        for i, row in enumerate(self.labels):
            line = " ".join(f"[{label}]" for label in row)
            lines.append(line)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"FerrerDiagram({self.partition})"

    def __str__(self) -> str:
        return self.to_ascii()


# Partition enumeration utilities

def partitions(n: int) -> Iterator[Partition]:
    """
    Generate all partitions of n.

    Uses the "decreasing sequence" algorithm.
    """
    if n == 0:
        yield Partition(parts=(0,))
        return

    def generate(n: int, max_part: int) -> Iterator[Tuple[int, ...]]:
        if n == 0:
            yield ()
            return
        for first in range(min(n, max_part), 0, -1):
            for rest in generate(n - first, first):
                yield (first,) + rest

    for parts in generate(n, n):
        yield Partition(parts=parts)


def partition_count(n: int) -> int:
    """
    Count the number of partitions of n.

    Uses Euler's recurrence (exact for small n, approximation for large).
    """
    if n <= 0:
        return 1

    # Dynamic programming
    dp = [0] * (n + 1)
    dp[0] = 1

    for i in range(1, n + 1):
        for j in range(i, n + 1):
            dp[j] += dp[j - i]

    return dp[n]


def partitions_of_length(n: int, k: int) -> Iterator[Partition]:
    """Generate all partitions of n with exactly k parts."""
    for p in partitions(n):
        if p.length == k:
            yield p


def partitions_with_max_part(n: int, max_part: int) -> Iterator[Partition]:
    """Generate partitions of n where no part exceeds max_part."""
    for p in partitions(n):
        if p.width <= max_part:
            yield p


def partition_to_nesting(p: Partition) -> str:
    """
    Convert partition to nested parentheses representation.

    Example: [3,2,1] -> ((()()())(()())) or similar
    """
    # Build nesting based on partition structure
    if p.n == 0:
        return "()"

    if p.length == 1:
        # Single row: flat tuple
        return "(" + "()" * p.parts[0] + ")"

    # Multiple rows: nested structure
    # Each part becomes a group
    groups = ["()" * part for part in p.parts]
    return "(" + "".join(f"({g})" for g in groups) + ")"


def nesting_to_partition(s: str) -> Partition:
    """
    Convert nested parentheses to partition.

    Counts atoms at each nesting depth.
    """
    depths = []
    current_depth = 0

    for char in s:
        if char == '(':
            current_depth += 1
        elif char == ')':
            if s[s.index(char) - 1] == '(':
                # This is a leaf ()
                depths.append(current_depth)
            current_depth -= 1

    # Convert depth counts to partition
    from collections import Counter
    counts = Counter(depths)
    parts = sorted(counts.values(), reverse=True)
    return Partition.from_list(parts)
