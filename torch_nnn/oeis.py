"""
OEIS Sequence Enumeration: A000041, A000055, A000081, A000108

Shows the relations between four fundamental combinatorial sequences
for System index s < 8, each counting a distinct class of tree/partition
structure:

  A000041(n)  = number of integer partitions of n
  A000055(n)  = number of free (unrooted, unordered) trees with n nodes
  A000081(n)  = number of rooted (unordered) trees with n nodes
  A000108(n)  = n-th Catalan number = number of ordered binary trees
                with n internal nodes (= n+1 leaves)

Correspondence at a glance (System s with shifted OEIS index n=s+1):

  s   n   A000041  A000055  A000081  A000108
  0   1      1        1        1        1
  1   2      1        1        1        1
  2   3      2        1        2        2
  3   4      3        2        4        5
  4   5      5        3        9       14
  5   6      7        6       20       42
  6   7     11       11       48      132
  7   8     15       23      115      429

Why these four sequences are related
-------------------------------------
- Partitions (A000041) provide the «shape» of any tree via its
  degree sequence / Prüfer encoding; every rooted tree gives a
  partition of n-1 (its edge-multiset sizes).
- Rooted trees (A000081) become free trees (A000055) when we forget
  the root: roughly A000055(n) ≈ A000081(n)/2 for large n.
- Ordered trees (Catalan, A000108) refine rooted trees by adding a
  left-to-right ordering on children, yielding more structures.
- The inequalities A000055 ≤ A000081 ≤ A000108 hold for all n ≥ 1,
  reflecting the successive «forgetting» of structure (root → order).

Run with: python -m torch_nnn.oeis
"""

from __future__ import annotations
from functools import lru_cache
from typing import Iterator, List, Tuple
import math


# ---------------------------------------------------------------------------
# A000041 — Integer partitions
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def a000041(n: int) -> int:
    """
    A000041(n): number of integer partitions of n.

    Values: 1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, ...
    (OEIS A000041 is 1-indexed starting at n=0.)
    """
    if n < 0:
        return 0
    # Standard DP over parts 1..n
    dp = [0] * (n + 1)
    dp[0] = 1
    for part in range(1, n + 1):
        for total in range(part, n + 1):
            dp[total] += dp[total - part]
    return dp[n]


def partitions_of(n: int) -> Iterator[Tuple[int, ...]]:
    """Yield all integer partitions of n in non-increasing order."""
    def _gen(remaining: int, max_part: int) -> Iterator[Tuple[int, ...]]:
        if remaining == 0:
            yield ()
            return
        for first in range(min(remaining, max_part), 0, -1):
            for rest in _gen(remaining - first, first):
                yield (first,) + rest

    yield from _gen(n, n)


# ---------------------------------------------------------------------------
# A000081 — Rooted unlabeled unordered trees (Matula trees)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def a000081(n: int) -> int:
    """
    A000081(n): number of unlabeled rooted trees with n nodes.

    Values: 0, 1, 1, 2, 4, 9, 20, 48, 115, ...
    (OEIS convention: a(0)=0 or 1 depending on source; here a(0)=0,
    a(1)=1 — one tree: the single node.)

    Uses the recurrence:
      a(n) = (1/(n-1)) * sum_{k=1}^{n-1} (sum_{d|k} d*a(d)) * a(n-k)
    """
    if n < 0:
        return 0
    if n == 0:
        return 0
    if n == 1:
        return 1
    total = 0
    for k in range(1, n):
        sigma = sum(d * a000081(d) for d in range(1, k + 1) if k % d == 0)
        total += sigma * a000081(n - k)
    return total // (n - 1)


# ---------------------------------------------------------------------------
# A000055 — Free (unrooted) unlabeled trees
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def a000055(n: int) -> int:
    """
    A000055(n): number of free trees (unrooted, unlabeled) with n nodes.

    Values: 1, 1, 1, 1, 2, 3, 6, 11, 23, 47, ...
    (Here a(0)=1 by convention — the empty tree.)

    Uses Otter's identity (generating functions):
      T(x) = R(x) - R(x)²/2 + R(x²)/2

    where R(x) = sum A000081(n) x^n and T(x) = sum A000055(n) x^n.

    In coefficient form:
      2·T(n) = 2·R(n) - sum_{j=1}^{n-1} R(j)·R(n-j)  +  [n even]·R(n/2)

    The R(x²)/2 term contributes R(n/2)/2 when n is even (coefficient of
    x^n in R(x²) is R(n/2)), and 0 when n is odd.
    """
    if n < 0:
        return 0
    if n <= 2:
        return 1

    two_t = 2 * a000081(n)

    # Subtract the R(x)^2 / 2 convolution
    for j in range(1, n):
        two_t -= a000081(j) * a000081(n - j)

    # Add the R(x^2) / 2 term (non-zero only when n is even)
    if n % 2 == 0:
        two_t += a000081(n // 2)

    return two_t // 2


# ---------------------------------------------------------------------------
# A000108 — Catalan numbers (ordered / plane / full binary trees)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def a000108(n: int) -> int:
    """
    A000108(n): the n-th Catalan number.

    C(n) = binomial(2n, n) / (n+1)

    In the tree context C(n) counts:
    - Ordered (plane) rooted trees with n+1 leaves
    - Full binary trees with n internal nodes
    - Dyck paths of length 2n
    - Ways to fully parenthesize n+1 factors

    Values: 1, 1, 2, 5, 14, 42, 132, 429, ...
    """
    if n < 0:
        return 0
    return math.comb(2 * n, n) // (n + 1)


# ---------------------------------------------------------------------------
# Enumeration helpers
# ---------------------------------------------------------------------------

def rooted_trees_with_nodes(n: int) -> List[Tuple]:
    """
    Return all rooted unlabeled unordered trees with n nodes as
    canonical nested tuples.  Each tuple represents the multiset of
    child subtrees (also as tuples).  The leaf is represented as ().

    Uses the same generation strategy as enumerate_matula_trees but
    returns pure tuples (no dependency on the matula module here).
    """
    if n < 1:
        return []
    if n == 1:
        return [()]

    seen = set()
    result = []

    def gen_children(remaining: int, min_tree: Tuple) -> Iterator[List[Tuple]]:
        if remaining == 0:
            yield []
            return
        for size in range(1, remaining + 1):
            for t in rooted_trees_with_nodes(size):
                if t < min_tree:
                    continue
                for rest in gen_children(remaining - size, t):
                    yield [t] + rest

    for children in gen_children(n - 1, ()):
        key = tuple(sorted(children))
        if key not in seen:
            seen.add(key)
            result.append(key)

    return sorted(result)


def catalan_trees_with_leaves(n: int) -> List[str]:
    """
    Return all ordered binary trees with n leaves as parenthesis strings.
    () = leaf, (AB) = internal node with left child A and right child B.
    Yields C(n-1) strings.
    """
    if n == 1:
        return ["()"]

    result = []
    for k in range(1, n):
        for left in catalan_trees_with_leaves(k):
            for right in catalan_trees_with_leaves(n - k):
                result.append(f"({left}{right})")
    return result


def free_trees_with_nodes(n: int) -> List[frozenset]:
    """
    Return all free (unrooted) trees with n nodes.

    We generate them by rooting each rooted tree at all possible
    nodes, deduplicate up to isomorphism, then return one
    representative per isomorphism class (as a frozenset of edges
    encoded via the canonical adjacency tuple).

    For small n this brute-force approach is fine.
    The count equals A000055(n).
    """
    if n <= 0:
        return []
    if n == 1:
        return [frozenset()]
    if n == 2:
        return [frozenset({(0, 1)})]

    # Generate all rooted trees; for each, compute the canonical
    # «free tree» by re-rooting at the centroid and normalising.
    rooted = rooted_trees_with_nodes(n)
    seen_canonicals = set()
    result = []

    for rt in rooted:
        # Build adjacency from the rooted tree tuple
        edges = _rooted_tuple_to_edges(rt, parent=-1, node_counter=[0])
        canonical = _canonical_free_tree(edges, n)
        if canonical not in seen_canonicals:
            seen_canonicals.add(canonical)
            result.append(frozenset(edges))

    return result


def _rooted_tuple_to_edges(
    subtree: Tuple,
    parent: int,
    node_counter: List[int],
) -> List[Tuple[int, int]]:
    """Convert a rooted tree tuple to an edge list (node ids assigned in DFS order)."""
    me = node_counter[0]
    node_counter[0] += 1
    edges = []
    if parent >= 0:
        edges.append((min(me, parent), max(me, parent)))
    for child in subtree:
        edges.extend(_rooted_tuple_to_edges(child, me, node_counter))
    return edges


def _canonical_free_tree(edges: List[Tuple[int, int]], n: int) -> Tuple:
    """
    Compute a canonical form for a free tree given as an edge list.

    We find the centroid (or centroid edge), then root there and
    produce a canonical rooted-tree tuple which serves as the key.
    """
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Subtree sizes rooted at 0
    size = [1] * n
    parent = [-1] * n
    order = []
    visited = [False] * n
    stack = [0]
    visited[0] = True
    while stack:
        node = stack.pop()
        order.append(node)
        for nb in adj[node]:
            if not visited[nb]:
                visited[nb] = True
                parent[nb] = node
                stack.append(nb)
    for node in reversed(order):
        p = parent[node]
        if p >= 0:
            size[p] += size[node]

    # Find centroid(s)
    centroids = []
    for v in range(n):
        heavy = max((size[c] for c in adj[v] if c != parent[v]), default=0)
        parent_size = n - size[v]
        if max(heavy, parent_size) <= n // 2:
            centroids.append(v)

    # For determinism, compute canonical form rooted at each centroid and
    # take the lexicographically smallest result.  This is essential when
    # the tree has a centroid *edge* (exactly two centroids): both roots
    # must be tried so that two different integer labellings of the same
    # free tree always collapse to the same canonical tuple.
    return min(_canonical_rooted(adj, c, -1) for c in centroids)


def _canonical_rooted(adj: List[List[int]], node: int, par: int) -> Tuple:
    """Recursively build canonical rooted-tree tuple."""
    children = sorted(
        (_canonical_rooted(adj, nb, node) for nb in adj[node] if nb != par)
    )
    return tuple(children)


# ---------------------------------------------------------------------------
# Table and display
# ---------------------------------------------------------------------------

def oeis_table(max_n: int = 7) -> str:
    """
    Return a formatted System-aligned correspondence table.

    Uses:
      s = System index (0..max_n)
      n = s + 1 (shifted OEIS index)

    with column mapping:
      A000041(s)   partitions
      A000055(n)   free trees
      A000081(n)   rooted trees
      A000108(s)   Catalan / ordered trees
    """
    lines = [
        "OEIS Sequences aligned to Systems s = 0 … {max_n}".format(max_n=max_n),
        "",
        "  s │ n │ A000041  │ A000055  │ A000081  │ A000108",
        "system│oeis│ partitions│ free trees│rooted trees│ Catalan",
        "────┼───┼──────────┼──────────┼──────────┼──────────",
    ]
    for s in range(max_n + 1):
        n = s + 1
        p = a000041(s)
        f = a000055(n)
        r = a000081(n)
        c = a000108(s)
        lines.append(f"  {s} │ {n:>1} │  {p:>6}  │  {f:>6}  │  {r:>6}  │  {c:>6}")
    return "\n".join(lines)


def show_partitions(max_n: int = 7) -> str:
    """List all integer partitions of n for n = 1 … max_n."""
    lines = ["A000041 — Integer Partitions", ""]
    for n in range(1, max_n + 1):
        parts_list = list(partitions_of(n))
        lines.append(f"  n={n}: {a000041(n)} partition(s)")
        for p in parts_list:
            lines.append(f"    {list(p)}")
    return "\n".join(lines)


def show_rooted_trees(max_n: int = 7) -> str:
    """List all rooted unordered trees with n nodes for n = 1 … max_n."""
    lines = ["A000081 — Rooted Unordered Trees (Matula)", ""]
    for n in range(1, max_n + 1):
        trees = rooted_trees_with_nodes(n)
        lines.append(f"  n={n}: {a000081(n)} rooted tree(s)")
        for t in trees:
            lines.append(f"    {_tree_to_str(t)}")
    return "\n".join(lines)


def _tree_to_str(t: Tuple) -> str:
    """Pretty-print a rooted tree tuple."""
    if not t:
        return "●"
    return "●(" + ", ".join(_tree_to_str(c) for c in t) + ")"


def show_catalan_trees(max_n: int = 7) -> str:
    """List all ordered binary trees counted by A000108(n) for n = 0 … max_n."""
    lines = ["A000108 — Ordered (Catalan) Trees", ""]
    for n in range(max_n + 1):
        # C(n) counts ordered trees with n+1 leaves
        trees = catalan_trees_with_leaves(n + 1)
        lines.append(f"  C({n})={a000108(n)}: ordered binary trees with {n+1} {'leaf' if n==0 else 'leaves'}")
        for t in trees:
            lines.append(f"    {t}")
    return "\n".join(lines)


def show_free_trees(max_n: int = 7) -> str:
    """List all free (unrooted) trees with n nodes for n = 1 … max_n."""
    lines = ["A000055 — Free (Unrooted) Trees", ""]
    for n in range(1, max_n + 1):
        count = a000055(n)
        lines.append(f"  n={n}: {count} free tree(s)")
        # Show the rooted representatives (centroid-rooted canonical form)
        reps = free_trees_with_nodes(n)
        for edges in reps:
            edge_str = "{" + ", ".join(f"{u}-{v}" for u, v in sorted(edges)) + "}"
            lines.append(f"    edges: {edge_str}")
    return "\n".join(lines)


def show_relations() -> str:
    """Explain the mathematical relationships between the four sequences."""
    return """\
Relations between A000041, A000055, A000081, A000108
=====================================================

1. ROOTED vs FREE TREES  (A000081 vs A000055)
   Every free tree on n nodes can be rooted in ≥1 ways.
   Rooting at each vertex of a free tree generally gives distinct
   rooted trees, so A000081(n) ≥ A000055(n) for n ≥ 1.
   For a free tree that is «symmetric» (has a centroid edge), two
   rootings collapse, which is why A000055 is strictly smaller.

   Example n=4:  A000081(4)=4, A000055(4)=2
     Rooted:  ●(●,●,●)  ●(●,●(●))  ●(●(●(●)))  ●(●(●),●)
     Free:    star ●-●-●-●-●  and  path ●-●-●-●

2. ROOTED vs ORDERED TREES  (A000081 vs A000108)
   Ordered (plane) trees fix a left-to-right order on children.
   Each unordered rooted tree with degree sequence d₁,d₂,…
   gives ∏ dᵢ! ordered trees, so A000108(n) ≥ A000081(n+1).
   (Here C(n) counts ordered trees with n+1 leaves ≡ n internal
   nodes, while A000081(n+1) counts rooted trees with n+1 nodes.)

3. PARTITIONS vs TREES  (A000041 vs A000081/A000108)
   The degree sequence of a rooted tree on n nodes is a partition
   of n-1 (the total number of edges).  Multiple trees can share
   the same degree-sequence partition, so A000041(n-1) is a lower
   bound on the number of distinct tree shapes.
   Conversely, the «hook-length formula» for standard Young tableaux
   counts the number of linear extensions of a tree partial order —
   connecting partitions to tree enumeration via representation theory.

4. CATALAN (A000108) AS REFINEMENT
   The Catalan number C(n) counts the same objects as A000081 but
   with ordered children.  Forgetting the order gives a surjection
   ordered → unordered trees; the fibre over each unordered tree T
   has size equal to the product of (k_v)! over internal nodes v,
   where k_v is the number of children of v.

Inequalities (for n ≥ 2):
   A000055(n)  ≤  A000081(n)  ≤  A000108(n-1)
   (free trees) ≤ (rooted trees) ≤ (ordered trees with n leaves)
"""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """Print a complete enumeration for System index s < 8."""
    sep = "\n" + "─" * 60 + "\n"

    print("\n" + "═" * 60)
    print("  OEIS Enumeration: A000041 · A000055 · A000081 · A000108")
    print("  Partitions · Free Trees · Rooted Trees · Catalan Trees")
    print("  for System s = 0 … 7 (with OEIS n = s+1 alignment)")
    print("═" * 60)

    print(sep)
    print(oeis_table(max_n=7))

    print(sep)
    print(show_relations())

    print(sep)
    print(show_partitions(max_n=7))

    print(sep)
    print(show_rooted_trees(max_n=7))

    print(sep)
    print(show_free_trees(max_n=7))

    print(sep)
    print(show_catalan_trees(max_n=7))


if __name__ == "__main__":
    main()
