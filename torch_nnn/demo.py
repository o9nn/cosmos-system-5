#!/usr/bin/env python3
"""
Demonstration of Nested Tensor Embeddings: Systems 1, 2, 3

This module demonstrates the mathematical structure of nested embeddings
and how they correspond to rooted trees, Ferrer diagrams, and nested
parentheses (Catalan structures).

Run with: python -m torch_nnn.demo
"""

from typing import List
import math


def catalan(n: int) -> int:
    """Compute the n-th Catalan number."""
    if n <= 1:
        return 1
    return math.comb(2 * n, n) // (n + 1)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demonstrate_catalan_sequence():
    """Show the Catalan number sequence and its significance."""
    print_section("CATALAN NUMBERS & NESTING STRUCTURES")

    print("""
The Catalan numbers count the number of distinct nesting structures:

  C_n = (2n)! / ((n+1)! × n!)

Each System-K has C_{K-1} distinct structures.
""")

    print("Catalan sequence:")
    for n in range(8):
        print(f"  C_{n} = {catalan(n):>4}  (System {n+1} has {catalan(n)} structure{'s' if catalan(n) != 1 else ''})")


def demonstrate_system1():
    """Demonstrate System 1: Atomic embeddings."""
    print_section("SYSTEM 1: ATOMS (Depth 0)")

    print("""
System 1 represents atomic/base tensors - the leaves of all nested structures.

Properties:
  - Nesting depth: 0
  - Catalan number: C_0 = 1
  - Single structure: ()

Representations:
  - Parentheses: ()
  - Tree:        ●  (single node)
  - Partition:   [1] = █

Mathematical interpretation:
  An atom is an indivisible unit. It's the base case from which
  all higher structures are built recursively.
""")

    # Create System 1 embedding
    from .systems import System1
    import numpy as np

    s1 = System1(embedding_dim=64)

    print("Example:")
    data = np.random.randn(10, 64)
    atom = s1.embed(data, role="word_embedding")
    print(f"  Created: {atom}")
    print(f"  Shape: {atom.shape}")
    print(f"  Depth: {atom.depth}")
    print(f"  System: {atom.system}")
    print(f"  Parentheses: {atom.to_parentheses()}")
    print(f"  Partition: {atom.to_partition()}")


def demonstrate_system2():
    """Demonstrate System 2: Pair embeddings."""
    print_section("SYSTEM 2: PAIRS (Depth 1)")

    print("""
System 2 introduces binary nesting - combining two atoms into a pair.

Properties:
  - Nesting depth: 1
  - Catalan number: C_1 = 1
  - Single structure: ((),())

Representations:
  - Parentheses: (()())
  - Tree:          ●
                  / \\
                 ●   ●
  - Partitions: [2] = ██  or [1,1] = █
                                     █

Mathematical interpretation:
  A pair is the Cartesian product of two atoms. Although there's only
  one structural pattern (binary node), pairs can be symmetric or
  asymmetric in their semantic relationship.
""")

    from .systems import System1, System2
    import numpy as np

    s1 = System1(embedding_dim=64)
    s2 = System2(base_system=s1)

    print("Example:")
    left = s1.embed(np.random.randn(64), role="query")
    right = s1.embed(np.random.randn(64), role="key")
    pair = s2.embed(left, right, role="attention_pair")

    print(f"  Created: {pair}")
    print(f"  Shape: {pair.shape}")
    print(f"  Depth: {pair.depth}")
    print(f"  System: {pair.system}")
    print(f"  Parentheses: {pair.to_parentheses()}")
    print(f"  Partition: {pair.to_partition()}")
    print(f"  Tree:\n{pair.to_tree()}")


def demonstrate_system3():
    """Demonstrate System 3: Triple embeddings with association choice."""
    print_section("SYSTEM 3: TRIPLES (Depth 2)")

    print("""
System 3 is where Catalan structure becomes non-trivial!

Properties:
  - Nesting depth: 2
  - Catalan number: C_2 = 2
  - TWO structures: ((()())()) and (()(()()))

Representations:
  LEFT-ASSOCIATIVE: ((a, b), c)          RIGHT-ASSOCIATIVE: (a, (b, c))

  Parentheses: ((()())())                Parentheses: (()(()()))

  Tree:       ●                          Tree:       ●
             / \\                                    / \\
            ●   c                                  a   ●
           / \\                                       / \\
          a   b                                      b   c

  This represents "first combine a,b,        This represents "first combine b,c,
   then add c"                                then add a"

Partitions of 3:
  [3]     = ███     (maximally balanced)
  [2,1]   = ██      (one pair + singleton)
            █
  [1,1,1] = █       (fully split)
            █
            █

Mathematical interpretation:
  The choice of association IS the structure. This is the first System
  where we must choose between multiple valid nesting patterns. In
  non-associative algebras, ((a*b)*c) ≠ (a*(b*c)).

Applications:
  - Query-Key-Value attention: ((Q⊗K)⊗V) - naturally left-associative
  - Subject-Verb-Object: linguistic structure
  - Head-Relation-Tail: knowledge graphs
  - Anchor-Positive-Negative: contrastive learning
""")

    from .systems import System1, System3
    from .systems.system3 import Association
    import numpy as np

    s1 = System1(embedding_dim=64)
    s3 = System3(base_system=s1)

    print("Example - Left associative ((a,b),c):")
    a = np.random.randn(64)
    b = np.random.randn(64)
    c = np.random.randn(64)

    triple_left = s3.embed_left(a, b, c, role="left_triple")
    print(f"  Created: {triple_left}")
    print(f"  Depth: {triple_left.depth}")
    print(f"  Parentheses: {triple_left.to_parentheses()}")
    print(f"  Tree:\n{triple_left.to_tree()}")

    print("\nExample - Right associative (a,(b,c)):")
    triple_right = s3.embed_right(a, b, c, role="right_triple")
    print(f"  Created: {triple_right}")
    print(f"  Parentheses: {triple_right.to_parentheses()}")
    print(f"  Tree:\n{triple_right.to_tree()}")

    print("\nReassociation (switching between structures):")
    reassociated = triple_left.reassociate()
    print(f"  Original:     {triple_left.to_parentheses()}")
    print(f"  Reassociated: {reassociated.to_parentheses()}")


def demonstrate_tree_enumeration():
    """Show all binary trees for small n."""
    print_section("ENUMERATING BINARY TREES")

    from .trees import enumerate_binary_trees, count_binary_trees

    print("All distinct binary tree shapes by leaf count:\n")

    for n in range(1, 5):
        count = count_binary_trees(n)
        print(f"n = {n} leaves: C_{n-1} = {count} tree(s)")
        for i, tree in enumerate(enumerate_binary_trees(n), 1):
            print(f"  {i}. {tree.to_parentheses()}")
        print()


def demonstrate_partitions():
    """Show partition structure for small n."""
    print_section("FERRER DIAGRAMS (PARTITIONS)")

    from .ferrer import partitions, partition_count, Partition

    print("Partitions represent the 'shape' of nesting.\n")

    for n in range(1, 5):
        count = partition_count(n)
        print(f"Partitions of {n}: (count = {count})")
        for p in partitions(n):
            diagram = p.to_diagram()
            bracket = p.to_brackets()
            lines = diagram.split('\n')
            # Print bracket aligned with diagram
            print(f"  {bracket:12} {lines[0]}")
            for line in lines[1:]:
                print(f"  {' ':12} {line}")
        print()


def demonstrate_correspondence():
    """Show the correspondence between structures."""
    print_section("STRUCTURE CORRESPONDENCES")

    print("""
For System K, we have three equivalent representations:

1. NESTED PARENTHESES (Dyck words)
   - Show grouping structure
   - () = atom, (AB) = pair containing A and B

2. ROOTED TREES
   - Leaves = atoms
   - Internal nodes = nesting operations
   - Binary trees for our systems

3. FERRER DIAGRAMS (Partitions)
   - Rows = nesting levels
   - Width = breadth at each level
   - Shape = structure signature

Example for System 3, Left-associative ((a,b),c):

  Parentheses: ((()())())

  Tree:       triple
             /      \\
          pair      atom
         /    \\       │
      atom   atom     c
        │      │
        a      b

  Partition signature: [2,1]
       ██
       █

The number of distinct structures follows Catalan numbers:
  System 1: C_0 = 1 structure
  System 2: C_1 = 1 structure
  System 3: C_2 = 2 structures
  System 4: C_3 = 5 structures
  System 5: C_4 = 14 structures
  ...
""")


def main():
    """Run all demonstrations."""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█  NESTED TENSOR EMBEDDINGS: torch.nnn                     █")
    print("█  Extension of torch.nn to Nested Neural Networks         █")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    demonstrate_catalan_sequence()
    demonstrate_system1()
    demonstrate_system2()
    demonstrate_system3()
    demonstrate_tree_enumeration()
    demonstrate_partitions()
    demonstrate_correspondence()

    print_section("SUMMARY")
    print("""
torch.nnn provides a mathematical framework for nested tensor embeddings:

┌─────────┬─────────┬───────────┬──────────────────────────┐
│ System  │  Depth  │  Catalan  │  Structure               │
├─────────┼─────────┼───────────┼──────────────────────────┤
│    1    │    0    │   C_0=1   │  Atom ()                 │
│    2    │    1    │   C_1=1   │  Pair ((),())            │
│    3    │    2    │   C_2=2   │  Triple ((()())()) etc   │
│    4    │    3    │   C_3=5   │  Quadruple (5 shapes)    │
│    5    │    4    │   C_4=14  │  Quintuple (14 shapes)   │
│   ...   │   ...   │    ...    │  ...                     │
└─────────┴─────────┴───────────┴──────────────────────────┘

Key insights:
1. Nesting depth increases linearly with System number
2. Structure count grows as Catalan numbers
3. Each structure corresponds to a tree shape
4. Partitions capture the "signature" of nesting balance

This framework enables:
- Hierarchical attention mechanisms
- Structured knowledge representations
- Compositional semantics in neural networks
- Association-aware learning
""")


if __name__ == "__main__":
    main()
