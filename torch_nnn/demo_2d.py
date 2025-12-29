#!/usr/bin/env python3
"""
Demonstration of 2D Nested Tensor Embeddings via Matula Numbers

This module demonstrates the mathematical structure of unordered
rooted trees and their bijection with positive integers (Matula numbers).

Run with: python -m torch_nnn.demo_2d
"""

from .matula import (
    sys, a000081, MatulaTree, MatulaNode,
    enumerate_matula_trees, nth_prime, prime_index,
    prime_factorization
)
from .embedding2d import System2D, TreeEmbedding2D, compare_1d_2d


def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demonstrate_sys_sequence():
    """Show the sys(n) = A000081 sequence."""
    print_section("THE sys(n) SEQUENCE: Unordered Rooted Trees")

    print("""
Unlike Catalan numbers (ordered trees), sys(n) counts UNORDERED
rooted trees where child order doesn't matter.

sys(n) = A000081(n+1) = number of rooted trees with n edges
""")

    print("sys(n) sequence:")
    for n in range(12):
        print(f"  sys({n:2d}) = {sys(n):>5}  (trees with {n} edges, {n+1} nodes)")

    print("\n" + compare_1d_2d(10))


def demonstrate_matula_bijection():
    """Show the Matula number ↔ Tree bijection."""
    print_section("MATULA NUMBER BIJECTION: N⁺ ↔ Trees")

    print("""
Every positive integer corresponds to a unique rooted tree.

ENCODING RULES:
  1 ↔ single node ●

  If T has Matula number m, then the tree with a new root
  connected to T has Matula number p_m (the m-th prime).

  If T₁, T₂ have Matula numbers m₁, m₂, then the tree with
  root connected to both has Matula number m₁ × m₂.

EXAMPLES:
  1 = 1           →  ●           (single node)
  2 = p₁          →  ●─●         (prime for tree-1)
  3 = p₂          →  ●─●─●       (prime for tree-2)
  4 = 2²          →  ●<●         (two copies of tree-2's child)
                      ╲●
  5 = p₃          →  ●─●─●─●     (prime for tree-3)
  6 = 2 × 3       →  ●<●─●       (product: tree-2 child × tree-3 child)
                      ╲●
  7 = p₄          →  ●─●<●       (prime for tree-4)
                        ╲●
  8 = 2³          →  ●<●         (three copies of tree-2's child)
                      ├●
                      ╲●
""")

    print("First 20 Matula numbers and their trees:\n")
    for m in range(1, 21):
        tree = MatulaTree.from_matula(m)
        print(f"  Matula {m:2d}: nodes={tree.size}, height={tree.height}")
        for line in str(tree).split('\n')[1:]:  # Skip empty first line
            print(f"           {line}")


def demonstrate_prime_structure():
    """Show how prime factorization gives tree structure."""
    print_section("PRIME FACTORIZATION → TREE STRUCTURE")

    print("""
The tree structure is encoded in the prime factorization:

  m = p₁^a₁ × p₂^a₂ × ... × pₖ^aₖ

means the root has:
  - a₁ children that are trees with Matula number 1 (leaves)
  - a₂ children that are trees with Matula number 2
  - etc.

Since pₙ is the n-th prime, and tree n has Matula m_n,
the child has structure of tree m_n.
""")

    examples = [
        12,   # 2² × 3 = star(2) with one chain-2
        18,   # 2 × 3² = two chain-2s
        24,   # 2³ × 3
        30,   # 2 × 3 × 5
        60,   # 2² × 3 × 5
    ]

    for m in examples:
        factors = prime_factorization(m)
        tree = MatulaTree.from_matula(m)

        factor_str = " × ".join(
            f"p_{prime_index(p)}^{e}" if e > 1 else f"p_{prime_index(p)}"
            for p, e in factors
        )
        factor_str2 = " × ".join(
            f"{p}^{e}" if e > 1 else str(p)
            for p, e in factors
        )

        print(f"\n  Matula {m} = {factor_str2} = {factor_str}")
        print(f"  Nodes: {tree.size}, Height: {tree.height}")
        for line in str(tree).split('\n')[1:]:
            print(f"    {line}")


def demonstrate_tree_enumeration():
    """Show all trees for small systems."""
    print_section("TREE ENUMERATION BY SYSTEM")

    print("All distinct rooted tree structures by node count:\n")

    for k in range(6):
        trees = list(enumerate_matula_trees(k + 1))
        print(f"sys({k}) = {len(trees)} tree(s) with {k+1} nodes:")

        for i, tree in enumerate(trees):
            if k <= 3:
                # Show full tree for small cases
                print(f"  [{i+1}] Matula={tree.matula}")
                for line in str(tree).split('\n')[1:]:
                    print(f"      {line}")
            else:
                # Just Matula numbers for larger
                print(f"  [{i+1}] Matula={tree.matula}, height={tree.height}")

        print()


def demonstrate_system2d():
    """Show the System2D embedding class."""
    print_section("SYSTEM2D: 2D MATRIX EMBEDDINGS")

    print("""
Each System-K creates matrix embeddings for trees with K edges:
  - Rows = tree nodes
  - Columns = embedding dimensions
  - Structure indexed by Matula number
""")

    for k in range(5):
        sys2d = System2D(k, embedding_dim=64)
        print(f"\nSystem2D(k={k}):")
        print(f"  Structures: {sys2d.num_structures}")
        print(f"  Nodes/tree: {sys2d.num_nodes}")
        print(f"  Matula numbers: {sys2d.matula_numbers()}")

        # Create sample embedding
        if sys2d.num_structures > 0:
            first_tree = sys2d.structures()[0]
            embed = sys2d.embed_randn(first_tree)
            print(f"  Example embedding shape: {embed.shape}")


def demonstrate_tree_operations():
    """Show tree operations and composition."""
    print_section("TREE OPERATIONS")

    print("\nBasic tree constructors:")

    # Leaf
    leaf = MatulaTree.leaf()
    print(f"\n  MatulaTree.leaf():")
    print(f"    Matula={leaf.matula}, size={leaf.size}")
    print(str(leaf))

    # Chain
    chain = MatulaTree.chain(4)
    print(f"\n  MatulaTree.chain(4):")
    print(f"    Matula={chain.matula}, size={chain.size}")
    print(str(chain))

    # Star
    star = MatulaTree.star(3)
    print(f"\n  MatulaTree.star(3):")
    print(f"    Matula={star.matula}, size={star.size}")
    print(str(star))

    # Composition
    print("\nTree composition:")
    t1 = MatulaTree.chain(2)
    t2 = MatulaTree.star(2)
    combined = t1.product(t2)
    print(f"\n  chain(2).product(star(2)):")
    print(f"    Matula={combined.matula}, size={combined.size}")
    print(str(combined))


def demonstrate_mathematical_properties():
    """Show key mathematical properties."""
    print_section("MATHEMATICAL PROPERTIES")

    print("""
Key relationships:

1. BIJECTION COMPLETENESS
   Every positive integer is a valid Matula number.
   Every rooted tree has exactly one Matula number.

2. MULTIPLICATIVE STRUCTURE
   Matula(T₁ ∪ T₂) = Matula(T₁) × Matula(T₂)
   (when T₁, T₂ are children of same root)

3. PRIME ENCODING
   Matula(root → T) = p_{Matula(T)}
   The m-th prime encodes "add root to tree m"

4. CANONICAL ORDERING
   Matula numbers provide a total order on trees.
   Lower Matula = "simpler" structure.

5. SIZE BOUNDS
   For trees with n nodes: Matula ∈ [1, 2^{n-1}]
   Chain has largest Matula for its size.
""")

    # Verify multiplicative property
    print("\nMultiplicative property example:")
    t1 = MatulaTree.from_matula(2)  # ●─●
    t2 = MatulaTree.from_matula(3)  # ●─●─●

    m1, m2 = t1.matula, t2.matula
    combined = MatulaTree.from_matula(m1 * m2)

    print(f"  Tree 1 (Matula={m1}): {t1.size} nodes")
    print(f"  Tree 2 (Matula={m2}): {t2.size} nodes")
    print(f"  Product (Matula={m1}×{m2}={m1*m2}): {combined.size} nodes")
    print(f"    = root with both as children")


def main():
    """Run all demonstrations."""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█  2D NESTED TENSOR EMBEDDINGS via MATULA NUMBERS          █")
    print("█  Unordered Rooted Trees ↔ Positive Integers              █")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    demonstrate_sys_sequence()
    demonstrate_matula_bijection()
    demonstrate_prime_structure()
    demonstrate_tree_enumeration()
    demonstrate_system2d()
    demonstrate_tree_operations()
    demonstrate_mathematical_properties()

    print_section("SUMMARY")
    print("""
torch.nnn provides TWO embedding paradigms:

┌─────────────────────────────────────────────────────────────┐
│  1D EMBEDDINGS (Catalan)    │  2D EMBEDDINGS (Matula)       │
├─────────────────────────────┼───────────────────────────────┤
│  Ordered binary trees       │  Unordered rooted trees       │
│  Left ≠ Right               │  Children unordered           │
│  C_n = 1,1,2,5,14,42,...    │  sys(n) = 1,1,2,4,9,20,48,...│
│  Sequential nesting         │  Hierarchical nesting         │
│  Language, attention        │  Molecules, types, graphs     │
└─────────────────────────────┴───────────────────────────────┘

The Matula bijection provides:
  • Canonical tree representation
  • Compositional structure via multiplication
  • Natural indexing for matrix embeddings
  • Efficient tree operations via number theory
""")


if __name__ == "__main__":
    main()
