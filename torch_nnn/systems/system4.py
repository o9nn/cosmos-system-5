"""
System 4: Quad/Quaternary Tensors - The Five Association Structures

Mathematical Properties:
-----------------------
- Nesting Depth: 3 (triple nesting)
- Catalan Number: C_3 = 5 (five structures)
- Rooted parentheses (canonical): [(()())()]
- System Order: 4 (4 nodes in inner tree, half-length = 4)
- Partitions: [4], [3,1], [2,2], [2,1,1], [1,1,1,1]

System 4 introduces the five distinct association structures for four
elements (a, b, c, d). This is the first system where the "balanced"
split structure ((a,b),(c,d)) appears as a distinct canonical form.

Key distinctions from the problem statement:
- "Quaternary" (4 distinct vars) vs "Tetradic" (2×2 orthogonal pairs)
- Tetradic relations [1,1][1,1] => [1,2,1] have ternary order 3
- True quaternary order 4 cannot be reduced to compound binary order 2(2)

The 5 structures (C_3 = 5):
1. LEFT_LEFT:   (((a,b),c),d)  — fully left-associative
2. LEFT_RIGHT:  ((a,(b,c)),d)
3. BALANCED:    ((a,b),(c,d))  — the "balanced" split
4. RIGHT_LEFT:  (a,((b,c),d))
5. RIGHT_RIGHT: (a,(b,(c,d))) — fully right-associative

In neural network terms:
- Quadruplet losses (anchor, positive, negative, hard-negative)
- Multi-head attention with 4 projections
- 2×2 matrix products (balanced split structure)
- Deep hierarchical encoders (left-associative chaining)
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

from .system1 import System1, AtomicEmbedding
from .system2 import System2, PairEmbedding, PairType
from .system3 import System3, TripleEmbedding, Association as Association3

# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


class Association4(Enum):
    """The five Catalan-3 association patterns for quads."""
    LEFT_LEFT = auto()    # (((a,b),c),d)  — fully left-associative
    LEFT_RIGHT = auto()   # ((a,(b,c)),d)
    BALANCED = auto()     # ((a,b),(c,d))  — balanced split
    RIGHT_LEFT = auto()   # (a,((b,c),d))
    RIGHT_RIGHT = auto()  # (a,(b,(c,d))) — fully right-associative


class QuadRole(Enum):
    """Semantic roles in a quad."""
    ANCHOR_POS_NEG_HARD = auto()   # Quadruplet contrastive
    QUERY_KEY_VALUE_MASK = auto()  # Masked attention
    ENCODER_DECODER_MEM_CTX = auto()  # Encoder-decoder with memory
    GENERIC = auto()


@dataclass
class QuadEmbedding:
    """
    A quad embedding in System 4.

    Represents a quaternary nesting structure with explicit association choice.
    There are C_3 = 5 distinct ways to associate four elements.

    The canonical (LEFT_LEFT) form: (((a,b),c),d)
    In rooted parentheses: [(()())()]

    Properties:
    - first, second, third, fourth: The four atomic embeddings
    - association: One of the 5 Association4 choices
    - quad_role: Semantic interpretation
    """
    first: AtomicEmbedding
    second: AtomicEmbedding
    third: AtomicEmbedding
    fourth: AtomicEmbedding
    association: Association4 = Association4.LEFT_LEFT
    quad_role: QuadRole = QuadRole.GENERIC
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Nesting depth is 3 for quads."""
        return 3

    @property
    def system(self) -> int:
        """System number is 4 for quads."""
        return 4

    @property
    def shape(self) -> Tuple:
        """Shape as nested tuple reflecting association."""
        s1, s2, s3, s4 = (
            self.first.shape, self.second.shape,
            self.third.shape, self.fourth.shape
        )
        a = Association4
        if self.association == a.LEFT_LEFT:
            return (((s1, s2), s3), s4)
        elif self.association == a.LEFT_RIGHT:
            return ((s1, (s2, s3)), s4)
        elif self.association == a.BALANCED:
            return ((s1, s2), (s3, s4))
        elif self.association == a.RIGHT_LEFT:
            return (s1, ((s2, s3), s4))
        else:  # RIGHT_RIGHT
            return (s1, (s2, (s3, s4)))

    @property
    def embedding_dims(self) -> Tuple[int, int, int, int]:
        """Embedding dimensions of all four atoms."""
        return (
            self.first.embedding_dim, self.second.embedding_dim,
            self.third.embedding_dim, self.fourth.embedding_dim
        )

    def flatten(self) -> List[Any]:
        """Flatten to list of atomic data."""
        return (
            self.first.flatten() + self.second.flatten() +
            self.third.flatten() + self.fourth.flatten()
        )

    def atoms(self) -> Tuple[AtomicEmbedding, AtomicEmbedding, AtomicEmbedding, AtomicEmbedding]:
        """Return all four atomic embeddings."""
        return (self.first, self.second, self.third, self.fourth)

    def inner_triple(self) -> TripleEmbedding:
        """
        Return the inner triple based on association.

        LEFT_LEFT:   (first, second, third)  LEFT-assoc
        LEFT_RIGHT:  (first, second, third)  RIGHT-assoc via (first,(second,third))
        BALANCED:    inner pair (first, second)
        RIGHT_LEFT:  (second, third, fourth) LEFT-assoc
        RIGHT_RIGHT: (second, third, fourth) RIGHT-assoc
        """
        a = Association4
        if self.association in (a.LEFT_LEFT,):
            return TripleEmbedding(
                first=self.first, second=self.second, third=self.third,
                association=Association3.LEFT, semantic_role="inner_triple"
            )
        elif self.association in (a.LEFT_RIGHT,):
            return TripleEmbedding(
                first=self.first, second=self.second, third=self.third,
                association=Association3.RIGHT, semantic_role="inner_triple"
            )
        elif self.association in (a.RIGHT_LEFT,):
            return TripleEmbedding(
                first=self.second, second=self.third, third=self.fourth,
                association=Association3.LEFT, semantic_role="inner_triple"
            )
        elif self.association in (a.RIGHT_RIGHT,):
            return TripleEmbedding(
                first=self.second, second=self.third, third=self.fourth,
                association=Association3.RIGHT, semantic_role="inner_triple"
            )
        else:  # BALANCED: inner pair
            return TripleEmbedding(
                first=self.first, second=self.second, third=self.third,
                association=Association3.LEFT, semantic_role="inner_triple"
            )

    def inner_pair(self) -> PairEmbedding:
        """
        For BALANCED association, return the left pair (first, second).
        For other associations, return the innermost pair.
        """
        a = Association4
        if self.association == a.BALANCED:
            return PairEmbedding(left=self.first, right=self.second,
                                 semantic_role="inner_pair_left")
        elif self.association in (a.LEFT_LEFT, a.LEFT_RIGHT):
            return PairEmbedding(left=self.first, right=self.second,
                                 semantic_role="inner_pair")
        else:
            return PairEmbedding(left=self.second, right=self.third,
                                 semantic_role="inner_pair")

    def to_tree(self) -> 'RootedTree':
        """
        Convert to rooted tree reflecting association structure.

        LEFT_LEFT:          quad
                           /    \\
                        triple   d
                        /    \\
                      pair    c
                     /    \\
                    a      b
        """
        from ..trees import RootedTree, TreeNode

        n1, n2, n3, n4 = (
            self.first.to_tree().root, self.second.to_tree().root,
            self.third.to_tree().root, self.fourth.to_tree().root
        )
        a = Association4
        if self.association == a.LEFT_LEFT:
            ab = TreeNode(value="pair", children=[n1, n2])
            abc = TreeNode(value="triple", children=[ab, n3])
            root = TreeNode(value="quad", children=[abc, n4],
                            metadata={"association": "LEFT_LEFT"})
        elif self.association == a.LEFT_RIGHT:
            bc = TreeNode(value="pair", children=[n2, n3])
            abc = TreeNode(value="triple", children=[n1, bc])
            root = TreeNode(value="quad", children=[abc, n4],
                            metadata={"association": "LEFT_RIGHT"})
        elif self.association == a.BALANCED:
            ab = TreeNode(value="pair", children=[n1, n2])
            cd = TreeNode(value="pair", children=[n3, n4])
            root = TreeNode(value="quad", children=[ab, cd],
                            metadata={"association": "BALANCED"})
        elif self.association == a.RIGHT_LEFT:
            bc = TreeNode(value="pair", children=[n2, n3])
            bcd = TreeNode(value="triple", children=[bc, n4])
            root = TreeNode(value="quad", children=[n1, bcd],
                            metadata={"association": "RIGHT_LEFT"})
        else:  # RIGHT_RIGHT
            cd = TreeNode(value="pair", children=[n3, n4])
            bcd = TreeNode(value="triple", children=[n2, cd])
            root = TreeNode(value="quad", children=[n1, bcd],
                            metadata={"association": "RIGHT_RIGHT"})
        return RootedTree(root=root)

    def to_partition(self) -> 'Partition':
        """
        Convert to partition based on structure balance.

        - All equal: [4]
        - Three equal: [3,1] or [1,3]
        - Two pairs: [2,2]
        - One pair + two singles: [2,1,1] or [1,1,2]
        - All different: [1,1,1,1]
        """
        from ..ferrer import Partition
        dims = self.embedding_dims
        if dims[0] == dims[1] == dims[2] == dims[3]:
            return Partition(parts=(4,))
        elif dims[0] == dims[1] == dims[2]:
            return Partition(parts=(3, 1))
        elif dims[1] == dims[2] == dims[3]:
            return Partition(parts=(1, 3))
        elif dims[0] == dims[1] and dims[2] == dims[3]:
            return Partition(parts=(2, 2))
        elif dims[0] == dims[1]:
            return Partition(parts=(2, 1, 1))
        elif dims[2] == dims[3]:
            return Partition(parts=(1, 1, 2))
        else:
            return Partition(parts=(1, 1, 1, 1))

    def to_parentheses(self) -> str:
        """Represent as nested parentheses showing association."""
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()
        p4 = self.fourth.to_parentheses()
        a = Association4
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

    def to_rooted_parentheses(self) -> str:
        """
        Represent using '[]' for root and '()' for inner nodes.

        Canonical (LEFT_LEFT): [(()())()]
        """
        return self.to_tree().to_rooted_parentheses()

    def map(self, f: Callable[[Any], Any]) -> 'QuadEmbedding':
        """Apply function to all atoms' data."""
        return QuadEmbedding(
            first=self.first.map(f),
            second=self.second.map(f),
            third=self.third.map(f),
            fourth=self.fourth.map(f),
            association=self.association,
            quad_role=self.quad_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def reassociate(self, target: Association4) -> 'QuadEmbedding':
        """Return the same quad with a different association."""
        return QuadEmbedding(
            first=self.first,
            second=self.second,
            third=self.third,
            fourth=self.fourth,
            association=target,
            quad_role=self.quad_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def compose_hierarchical(self) -> AtomicEmbedding:
        """Compose following the association hierarchy (returns to System 1)."""
        a = Association4
        if self.association == a.LEFT_LEFT:
            # (((a,b),c),d)
            ab = PairEmbedding(left=self.first, right=self.second).compose_concat()
            abc = PairEmbedding(left=ab, right=self.third).compose_concat()
            return PairEmbedding(left=abc, right=self.fourth).compose_concat()
        elif self.association == a.LEFT_RIGHT:
            # ((a,(b,c)),d)
            bc = PairEmbedding(left=self.second, right=self.third).compose_concat()
            abc = PairEmbedding(left=self.first, right=bc).compose_concat()
            return PairEmbedding(left=abc, right=self.fourth).compose_concat()
        elif self.association == a.BALANCED:
            # ((a,b),(c,d))
            ab = PairEmbedding(left=self.first, right=self.second).compose_concat()
            cd = PairEmbedding(left=self.third, right=self.fourth).compose_concat()
            return PairEmbedding(left=ab, right=cd).compose_concat()
        elif self.association == a.RIGHT_LEFT:
            # (a,((b,c),d))
            bc = PairEmbedding(left=self.second, right=self.third).compose_concat()
            bcd = PairEmbedding(left=bc, right=self.fourth).compose_concat()
            return PairEmbedding(left=self.first, right=bcd).compose_concat()
        else:  # RIGHT_RIGHT
            # (a,(b,(c,d)))
            cd = PairEmbedding(left=self.third, right=self.fourth).compose_concat()
            bcd = PairEmbedding(left=self.second, right=cd).compose_concat()
            return PairEmbedding(left=self.first, right=bcd).compose_concat()

    def __repr__(self) -> str:
        assoc = self.association.name
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return (
            f"QuadEmbedding[{assoc}]("
            f"first={self.first.shape}, second={self.second.shape}, "
            f"third={self.third.shape}, fourth={self.fourth.shape}{role})"
        )


class System4:
    """
    System 4: The Quaternary/Quad Embedding System.

    This level introduces the balanced split (BALANCED association), where
    the four elements divide into two pairs of equal status.

    Catalan Analysis:
    ----------------
    C_3 = 5: Five ways to associate four elements.

    (((a b) c) d)     LEFT_LEFT
    ((a (b c)) d)     LEFT_RIGHT
    ((a b) (c d))     BALANCED   ← new structure not in System 3
    (a ((b c) d))     RIGHT_LEFT
    (a (b (c d)))     RIGHT_RIGHT

    Tree Representations:
    --------------------
    LEFT_LEFT:   (((a,b),c),d) — linear chain, depth 3
    BALANCED:    ((a,b),(c,d)) — symmetric split, depth 2

    Rooted Parentheses (canonical LEFT_LEFT):
    [(()())()]

    Key Insight:
    -----------
    The BALANCED association ((a,b),(c,d)) demonstrates that quaternary
    systems are not reducible to iterated binary systems. The "tetradic"
    relation [1,1][1,1] => [1,2,1] has ternary order 3, but true
    quaternary order 4 requires the balanced structure.

    Ferrer Diagrams:
    ---------------
    [4]     = ████
    [3,1]   = ███  [2,2]  = ██  [2,1,1] = ██  [1,1,1,1] = █
              █           ██             █                   █
                                         █                   █
                                                             █

    Usage:
    ------
    >>> s4 = System4(embedding_dim=64)
    >>> quad = s4.embed_left_left(a, b, c, d)   # (((a,b),c),d)
    >>> balanced = s4.embed_balanced(a, b, c, d) # ((a,b),(c,d))
    >>> tree = quad.to_tree()
    >>> parens = quad.to_rooted_parentheses()    # "[(()())()]"
    """

    def __init__(
        self,
        base_system: Optional[System1] = None,
        pair_system: Optional[System2] = None,
        triple_system: Optional[System3] = None,
        embedding_dim: int = 64
    ):
        """
        Initialize System 4.

        Args:
            base_system: System 1 for atomic embeddings
            pair_system: System 2 for pair operations
            triple_system: System 3 for triple operations
            embedding_dim: Default dimensionality
        """
        self.base_system = base_system or System1(embedding_dim=embedding_dim)
        self.pair_system = pair_system or System2(
            base_system=self.base_system, embedding_dim=embedding_dim
        )
        self.triple_system = triple_system or System3(
            base_system=self.base_system,
            pair_system=self.pair_system,
            embedding_dim=embedding_dim
        )
        self.embedding_dim = embedding_dim
        self._catalan = 5  # C_3 = 5

    @property
    def depth(self) -> int:
        """Maximum nesting depth in System 4."""
        return 3

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures (C_3 = 5)."""
        return self._catalan

    @property
    def structure_count(self) -> int:
        """Alias for catalan_number."""
        return self._catalan

    def _ensure_atom(self, x: Union[AtomicEmbedding, Any], role: str) -> AtomicEmbedding:
        """Convert to AtomicEmbedding if needed."""
        if isinstance(x, AtomicEmbedding):
            return x
        return self.base_system.embed(x, role=role)

    def embed(
        self,
        first: Union[AtomicEmbedding, Any],
        second: Union[AtomicEmbedding, Any],
        third: Union[AtomicEmbedding, Any],
        fourth: Union[AtomicEmbedding, Any],
        association: Association4 = Association4.LEFT_LEFT,
        quad_role: QuadRole = QuadRole.GENERIC,
        role: Optional[str] = None
    ) -> QuadEmbedding:
        """
        Create a quad embedding from four inputs.

        Args:
            first, second, third, fourth: The four elements
            association: One of the 5 Association4 structures
            quad_role: Semantic role classification
            role: Optional label

        Returns:
            QuadEmbedding with specified structure
        """
        return QuadEmbedding(
            first=self._ensure_atom(first, "first"),
            second=self._ensure_atom(second, "second"),
            third=self._ensure_atom(third, "third"),
            fourth=self._ensure_atom(fourth, "fourth"),
            association=association,
            quad_role=quad_role,
            semantic_role=role
        )

    def embed_left_left(self, a: Any, b: Any, c: Any, d: Any,
                        role: Optional[str] = None) -> QuadEmbedding:
        """Create fully left-associative quad: (((a,b),c),d)"""
        return self.embed(a, b, c, d, Association4.LEFT_LEFT, role=role)

    def embed_left_right(self, a: Any, b: Any, c: Any, d: Any,
                         role: Optional[str] = None) -> QuadEmbedding:
        """Create left-right quad: ((a,(b,c)),d)"""
        return self.embed(a, b, c, d, Association4.LEFT_RIGHT, role=role)

    def embed_balanced(self, a: Any, b: Any, c: Any, d: Any,
                       role: Optional[str] = None) -> QuadEmbedding:
        """Create balanced quad: ((a,b),(c,d)) — the 2×2 split."""
        return self.embed(a, b, c, d, Association4.BALANCED, role=role)

    def embed_right_left(self, a: Any, b: Any, c: Any, d: Any,
                         role: Optional[str] = None) -> QuadEmbedding:
        """Create right-left quad: (a,((b,c),d))"""
        return self.embed(a, b, c, d, Association4.RIGHT_LEFT, role=role)

    def embed_right_right(self, a: Any, b: Any, c: Any, d: Any,
                          role: Optional[str] = None) -> QuadEmbedding:
        """Create fully right-associative quad: (a,(b,(c,d)))"""
        return self.embed(a, b, c, d, Association4.RIGHT_RIGHT, role=role)

    def embed_quadruplet(
        self, anchor: Any, positive: Any, negative: Any, hard_negative: Any
    ) -> QuadEmbedding:
        """
        Create an anchor/positive/negative/hard-negative quadruplet
        for contrastive learning.
        """
        return self.embed(
            anchor, positive, negative, hard_negative,
            association=Association4.LEFT_LEFT,
            quad_role=QuadRole.ANCHOR_POS_NEG_HARD,
            role="quadruplet_contrastive"
        )

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all 5 structures in System 4.

        Returns parentheses strings for each of the 5 association forms.
        """
        a = AtomicEmbedding(data=None, embedding_dim=self.embedding_dim)
        results = []
        for assoc in Association4:
            q = QuadEmbedding(
                first=a, second=a, third=a, fourth=a,
                association=assoc
            )
            results.append(q.to_parentheses())
        return results

    def enumerate_partitions(self) -> List['Partition']:
        """Enumerate all partitions for System 4 (partitions of 4)."""
        from ..ferrer import Partition
        return [
            Partition(parts=(4,)),
            Partition(parts=(3, 1)),
            Partition(parts=(2, 2)),
            Partition(parts=(2, 1, 1)),
            Partition(parts=(1, 1, 1, 1))
        ]

    def structure_trees(self) -> List['RootedTree']:
        """Get all 5 canonical trees for System 4 structures."""
        from ..trees import RootedTree, TreeNode, leaf, pair

        a, b, c, d = leaf("a"), leaf("b"), leaf("c"), leaf("d")
        ab = pair(a, b, "pair")
        cd = pair(c, d, "pair")
        bc = pair(b, c, "pair")
        abc_ll = pair(pair(a, b, "pair"), c, "triple")
        abc_lr = pair(a, pair(b, c, "pair"), "triple")
        bcd_rl = pair(pair(b, c, "pair"), d, "triple")
        bcd_rr = pair(b, pair(c, d, "pair"), "triple")
        return [
            pair(abc_ll, d, "quad"),   # LEFT_LEFT
            pair(abc_lr, d, "quad"),   # LEFT_RIGHT
            pair(ab, cd, "quad"),      # BALANCED
            pair(a, bcd_rl, "quad"),   # RIGHT_LEFT
            pair(a, bcd_rr, "quad"),   # RIGHT_RIGHT
        ]

    def __repr__(self) -> str:
        return f"System4(embedding_dim={self.embedding_dim}, structures={self._catalan})"


# Neural network layers (if torch available)
if TORCH_AVAILABLE:
    class QuadLayer(nn.Module):
        """
        Neural network layer for System 4 quad embeddings.

        Processes four inputs according to a specified association structure,
        creating hierarchically structured embeddings.

        Architecture (LEFT_LEFT):
            first  \\
                    > inner_pair \\
            second /              > inner_triple \\
            third  ---------------/              > compose -> output
            fourth ---------------------------------/
        """

        def __init__(
            self,
            in_features: int,
            hidden_features: int,
            out_features: int,
            association: Association4 = Association4.LEFT_LEFT,
            bias: bool = True
        ):
            super().__init__()
            self.in_features = in_features
            self.hidden_features = hidden_features
            self.out_features = out_features
            self.association = association

            # Four input projections
            self.first_proj = nn.Linear(in_features, hidden_features, bias=bias)
            self.second_proj = nn.Linear(in_features, hidden_features, bias=bias)
            self.third_proj = nn.Linear(in_features, hidden_features, bias=bias)
            self.fourth_proj = nn.Linear(in_features, hidden_features, bias=bias)

            # Inner compositions
            self.inner_compose1 = nn.Linear(hidden_features * 2, hidden_features, bias=bias)
            self.inner_compose2 = nn.Linear(hidden_features * 2, hidden_features, bias=bias)
            self.outer_compose = nn.Linear(hidden_features * 2, out_features, bias=bias)

            self.system = System4(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 3

        def forward(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor,
            fourth: torch.Tensor
        ) -> QuadEmbedding:
            """
            Forward pass processing a quad of inputs.

            Follows the association structure for hierarchical composition.
            """
            f1 = self.first_proj(first)
            f2 = self.second_proj(second)
            f3 = self.third_proj(third)
            f4 = self.fourth_proj(fourth)

            a = Association4
            if self.association == a.LEFT_LEFT:
                # (((f1,f2),f3),f4)
                i1 = self.inner_compose1(torch.cat([f1, f2], dim=-1))
                i2 = self.inner_compose2(torch.cat([i1, f3], dim=-1))
                out = self.outer_compose(torch.cat([i2, f4], dim=-1))
            elif self.association == a.LEFT_RIGHT:
                # ((f1,(f2,f3)),f4)
                i1 = self.inner_compose1(torch.cat([f2, f3], dim=-1))
                i2 = self.inner_compose2(torch.cat([f1, i1], dim=-1))
                out = self.outer_compose(torch.cat([i2, f4], dim=-1))
            elif self.association == a.BALANCED:
                # ((f1,f2),(f3,f4))
                i1 = self.inner_compose1(torch.cat([f1, f2], dim=-1))
                i2 = self.inner_compose2(torch.cat([f3, f4], dim=-1))
                out = self.outer_compose(torch.cat([i1, i2], dim=-1))
            elif self.association == a.RIGHT_LEFT:
                # (f1,((f2,f3),f4))
                i1 = self.inner_compose1(torch.cat([f2, f3], dim=-1))
                i2 = self.inner_compose2(torch.cat([i1, f4], dim=-1))
                out = self.outer_compose(torch.cat([f1, i2], dim=-1))
            else:  # RIGHT_RIGHT
                # (f1,(f2,(f3,f4)))
                i1 = self.inner_compose1(torch.cat([f3, f4], dim=-1))
                i2 = self.inner_compose2(torch.cat([f2, i1], dim=-1))
                out = self.outer_compose(torch.cat([f1, i2], dim=-1))

            return QuadEmbedding(
                first=AtomicEmbedding(data=f1, semantic_role="first"),
                second=AtomicEmbedding(data=f2, semantic_role="second"),
                third=AtomicEmbedding(data=f3, semantic_role="third"),
                fourth=AtomicEmbedding(data=f4, semantic_role="fourth"),
                association=self.association,
                semantic_role="quad_layer_output",
                metadata={"composed": out}
            )

        def forward_composed(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor,
            fourth: torch.Tensor
        ) -> AtomicEmbedding:
            """Forward pass returning composed output (System 1)."""
            quad = self.forward(first, second, third, fourth)
            return AtomicEmbedding(
                data=quad.metadata["composed"],
                semantic_role="composed_quad"
            )

        def __repr__(self) -> str:
            return (
                f"QuadLayer({self.in_features} -> {self.out_features}, "
                f"association={self.association.name})"
            )

else:
    class QuadLayer:
        """Placeholder for QuadLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for QuadLayer")
