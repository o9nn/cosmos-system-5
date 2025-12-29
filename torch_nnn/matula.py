"""
Matula Numbers: Bijection between Positive Integers and Rooted Trees

Mathematical Foundation:
-----------------------
Matula numbers provide a canonical bijection N⁺ ↔ Rooted Trees (unlabeled, unordered).

The encoding uses the Fundamental Theorem of Arithmetic:
Every positive integer has a unique prime factorization.

Bijection Rules:
1. The single-node tree (leaf) ↔ 1
2. If tree T has Matula number m, then the tree with a new root
   connected to T has Matula number p_m (the m-th prime)
3. If trees T₁, T₂ have Matula numbers m₁, m₂, then the tree with
   root connected to both T₁ and T₂ has Matula number m₁ × m₂

Examples:
---------
1 ↔ ●                    (single node)
2 = p₁ ↔ ●─●             (root with leaf child)
3 = p₂ ↔ ●─●─●           (chain of 3)
4 = 2² ↔ ●<──●           (root with 2 leaf children)
          ╲──●
5 = p₃ ↔ ●─●─●─●         (chain of 4)
6 = 2×3 ↔ ●<──●          (root with leaf and chain-2 children)
          ╲──●─●
7 = p₄ ↔ ●─●<──●         (chain-2 then fork)
            ╲──●

This bijection is:
- Order-independent: swapping children gives same Matula number
- Canonical: each tree has exactly one Matula number
- Computable: prime factorization ↔ tree decomposition

The sequence sys(n) = A000081(n+1) counts trees by node count.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Iterator, Dict, Set
from dataclasses import dataclass, field
from functools import lru_cache
import math


# Prime utilities

@lru_cache(maxsize=10000)
def nth_prime(n: int) -> int:
    """
    Return the n-th prime number (1-indexed).
    p_1 = 2, p_2 = 3, p_3 = 5, ...
    """
    if n < 1:
        raise ValueError("Prime index must be >= 1")

    if n == 1:
        return 2

    # Sieve for finding primes
    primes = [2]
    candidate = 3

    while len(primes) < n:
        is_prime = True
        sqrt_candidate = int(math.sqrt(candidate)) + 1
        for p in primes:
            if p > sqrt_candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 2

    return primes[n - 1]


@lru_cache(maxsize=10000)
def prime_index(p: int) -> int:
    """
    Return the index of prime p (1-indexed).
    If p=2, return 1. If p=3, return 2. etc.
    """
    if p < 2:
        raise ValueError(f"{p} is not prime")

    if p == 2:
        return 1

    # Count primes up to p
    count = 1  # for 2
    for candidate in range(3, p + 1, 2):
        is_prime = True
        sqrt_candidate = int(math.sqrt(candidate)) + 1
        for divisor in range(3, sqrt_candidate, 2):
            if candidate % divisor == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
            if candidate == p:
                return count

    raise ValueError(f"{p} is not prime")


def is_prime(n: int) -> bool:
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """
    Return prime factorization as list of (prime, exponent) pairs.
    Example: 12 = 2² × 3 → [(2, 2), (3, 1)]
    """
    if n < 1:
        raise ValueError("n must be positive")
    if n == 1:
        return []

    factors = []
    d = 2

    while d * d <= n:
        exp = 0
        while n % d == 0:
            n //= d
            exp += 1
        if exp > 0:
            factors.append((d, exp))
        d += 1

    if n > 1:
        factors.append((n, 1))

    return factors


# A000081: Number of unlabeled rooted trees with n nodes

@lru_cache(maxsize=1000)
def a000081(n: int) -> int:
    """
    Compute A000081(n): number of unlabeled rooted trees with n nodes.

    sys(0) = a(1) = 1  (single node)
    sys(1) = a(2) = 1  (root + 1 child)
    sys(2) = a(3) = 2  (chain-3 or star-3)
    sys(3) = a(4) = 4
    sys(4) = a(5) = 9
    ...

    Uses the recurrence:
    a(n) = (1/(n-1)) * sum_{k=1}^{n-1} (sum_{d|k} d*a(d)) * a(n-k)
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1

    # Use the recurrence relation
    total = 0
    for k in range(1, n):
        # Compute sum_{d|k} d * a(d)
        divisor_sum = sum(d * a000081(d) for d in range(1, k + 1) if k % d == 0)
        total += divisor_sum * a000081(n - k)

    return total // (n - 1)


def sys(n: int) -> int:
    """
    Return the number of structures in System n.

    sys(n) = A000081(n + 1) = number of rooted trees with n+1 nodes
           = number of rooted trees with n edges

    sys(0) = 1:  ●
    sys(1) = 1:  ●─●
    sys(2) = 2:  ●─●─● or ●<●
                           ╲●
    sys(3) = 4:  (four trees with 4 nodes)
    sys(4) = 9:  (nine trees with 5 nodes)
    ...
    """
    return a000081(n + 1)


# Matula Tree: Rooted tree with Matula number encoding

@dataclass
class MatulaNode:
    """
    A node in a rooted tree with Matula number encoding.

    Children are stored as a multiset (unordered, with multiplicity).
    """
    children: List['MatulaNode'] = field(default_factory=list)
    label: Optional[str] = None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def degree(self) -> int:
        """Number of children (out-degree)."""
        return len(self.children)

    @property
    def size(self) -> int:
        """Total number of nodes in subtree."""
        return 1 + sum(child.size for child in self.children)

    @property
    def height(self) -> int:
        """Height of subtree (0 for leaf)."""
        if self.is_leaf:
            return 0
        return 1 + max(child.height for child in self.children)

    def matula_number(self) -> int:
        """
        Compute the Matula number for this subtree.

        Leaf → 1
        Node with children → product of p_{matula(child)} for each child
        """
        if self.is_leaf:
            return 1

        result = 1
        for child in self.children:
            child_matula = child.matula_number()
            result *= nth_prime(child_matula)

        return result

    def canonical_form(self) -> 'MatulaNode':
        """
        Return tree in canonical form (children sorted by Matula number).
        """
        if self.is_leaf:
            return MatulaNode(children=[], label=self.label)

        canonical_children = [child.canonical_form() for child in self.children]
        canonical_children.sort(key=lambda c: c.matula_number())
        return MatulaNode(children=canonical_children, label=self.label)

    def to_tuple(self) -> Tuple:
        """Convert to nested tuple representation (canonical)."""
        if self.is_leaf:
            return ()
        canonical = self.canonical_form()
        return tuple(sorted(child.to_tuple() for child in canonical.children))

    def pretty_print(self, prefix: str = "", is_last: bool = True) -> str:
        """ASCII tree representation."""
        connector = "└── " if is_last else "├── "
        label = self.label or f"m={self.matula_number()}"
        result = prefix + connector + label + "\n"

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            result += child.pretty_print(new_prefix, is_last_child)

        return result

    def __repr__(self) -> str:
        return f"MatulaNode(matula={self.matula_number()}, size={self.size})"


@dataclass
class MatulaTree:
    """
    A rooted tree with Matula number encoding.

    The Matula number uniquely identifies the tree structure
    (up to child reordering, which doesn't matter for unordered trees).
    """
    root: MatulaNode

    @property
    def matula(self) -> int:
        """The Matula number of this tree."""
        return self.root.matula_number()

    @property
    def size(self) -> int:
        """Number of nodes."""
        return self.root.size

    @property
    def height(self) -> int:
        """Height of tree."""
        return self.root.height

    @property
    def system(self) -> int:
        """System number (size - 1 = number of edges)."""
        return self.size - 1

    @classmethod
    def from_matula(cls, m: int) -> 'MatulaTree':
        """
        Construct tree from Matula number.

        Uses prime factorization to recursively build the tree.
        """
        if m < 1:
            raise ValueError("Matula number must be positive")

        def build_node(matula: int) -> MatulaNode:
            if matula == 1:
                return MatulaNode()

            # Factor the Matula number
            factors = prime_factorization(matula)

            children = []
            for prime, exp in factors:
                # Each prime factor p_k contributes a child with Matula number k
                child_matula = prime_index(prime)
                for _ in range(exp):
                    children.append(build_node(child_matula))

            return MatulaNode(children=children)

        return cls(root=build_node(m))

    @classmethod
    def leaf(cls) -> 'MatulaTree':
        """Create single-node tree (Matula = 1)."""
        return cls(root=MatulaNode())

    @classmethod
    def chain(cls, n: int) -> 'MatulaTree':
        """Create chain/path tree with n nodes."""
        if n < 1:
            raise ValueError("Chain must have at least 1 node")
        if n == 1:
            return cls.leaf()

        # Build chain from bottom up
        node = MatulaNode()
        for _ in range(n - 1):
            node = MatulaNode(children=[node])
        return cls(root=node)

    @classmethod
    def star(cls, k: int) -> 'MatulaTree':
        """Create star tree with k leaves (k+1 nodes total)."""
        if k < 0:
            raise ValueError("Star must have non-negative leaves")
        children = [MatulaNode() for _ in range(k)]
        return cls(root=MatulaNode(children=children))

    def attach(self, subtree: 'MatulaTree') -> 'MatulaTree':
        """
        Attach a subtree as a new child of this tree's root.
        Returns new tree (immutable operation).
        """
        new_children = self.root.children.copy()
        new_children.append(subtree.root)
        return MatulaTree(root=MatulaNode(children=new_children))

    def product(self, other: 'MatulaTree') -> 'MatulaTree':
        """
        Combine two trees under a new root.
        Result has Matula number = self.matula * other.matula (if both were children)
        """
        return MatulaTree(root=MatulaNode(children=[self.root, other.root]))

    def canonical(self) -> 'MatulaTree':
        """Return canonical form of this tree."""
        return MatulaTree(root=self.root.canonical_form())

    def is_isomorphic(self, other: 'MatulaTree') -> bool:
        """Check if two trees are isomorphic (have same Matula number)."""
        return self.matula == other.matula

    def __eq__(self, other: 'MatulaTree') -> bool:
        return self.matula == other.matula

    def __hash__(self) -> int:
        return hash(self.matula)

    def __repr__(self) -> str:
        return f"MatulaTree(matula={self.matula}, size={self.size})"

    def __str__(self) -> str:
        return self.root.pretty_print()


# Enumeration of trees by size

def enumerate_matula_trees(n: int) -> Iterator[MatulaTree]:
    """
    Enumerate all rooted trees with n nodes.

    Yields sys(n-1) = A000081(n) distinct trees.
    """
    if n < 1:
        return

    if n == 1:
        yield MatulaTree.leaf()
        return

    # Generate trees by considering all ways to partition n-1 edges
    # among children of the root
    seen: Set[int] = set()

    def generate_children(remaining: int, min_matula: int) -> Iterator[List[MatulaNode]]:
        """Generate all multisets of children using 'remaining' nodes."""
        if remaining == 0:
            yield []
            return

        # For each possible child tree size
        for child_size in range(1, remaining + 1):
            # For each tree of that size
            for child_tree in enumerate_matula_trees(child_size):
                if child_tree.matula < min_matula:
                    continue  # Enforce canonical ordering

                # Recursively generate remaining children
                for rest in generate_children(remaining - child_size, child_tree.matula):
                    yield [child_tree.root] + rest

    for children in generate_children(n - 1, 1):
        tree = MatulaTree(root=MatulaNode(children=children))
        matula = tree.matula
        if matula not in seen:
            seen.add(matula)
            yield tree


def matula_trees_up_to(max_size: int) -> Dict[int, List[MatulaTree]]:
    """
    Return dictionary mapping size → list of all trees of that size.
    """
    result = {}
    for n in range(1, max_size + 1):
        result[n] = list(enumerate_matula_trees(n))
    return result


# First few Matula numbers and their trees
MATULA_TABLE = """
Matula#  Nodes  Structure
-------  -----  ---------
1        1      ●
2        2      ●─●
3        3      ●─●─●
4        3      ●<●
              ╲●
5        4      ●─●─●─●
6        4      ●<●─●
              ╲●
7        4      ●─●<●
                 ╲●
8        4      ●<●
              ╲●
              ╲●
9        4      ●<●
              ╲●─●
...
"""
