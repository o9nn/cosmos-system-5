"""
System 5: Quint/Quinary Tensors - The Fourteen Association Structures

Mathematical Properties:
-----------------------
- Nesting Depth: 4 (quadruple nesting)
- Catalan Number: C_4 = 14 (fourteen structures)
- Rooted parentheses (canonical): [(((()())())())()]
- System Order: 5 (5 nodes in inner tree, half-length = 5)
- Partitions: all partitions of 5

System 5 has C_4 = 14 distinct association structures for five elements
(a, b, c, d, e). This is the system referenced in the problem statement:
"pentadic relations (and 7-ary) have quaternary order".

Key insight from the problem statement:
- Pentadic relations have QUATERNARY order (not quintic)
- The partition [1,1,1,1] (four parts) has order 4
- Arity relations are indexed by Matula primes
- Order is indexed by integer partitions

In neural network terms:
- 5-way multi-task learning heads
- Pentic contrastive learning
- Deep hierarchical sequence encoders
- Token + position + segment + layer + type embeddings
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

from .system1 import System1, AtomicEmbedding
from .system2 import System2, PairEmbedding, PairType
from .system3 import System3, TripleEmbedding
from .system4 import System4, QuadEmbedding, Association4

# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


class Association5(Enum):
    """The fourteen Catalan-4 association patterns for quints."""
    # 14 full binary tree shapes with 5 leaves
    LL_LL = auto()   # ((((a,b),c),d),e)   — fully left
    LL_LR = auto()   # (((a,(b,c)),d),e)
    LL_BAL = auto()  # (((a,b),(c,d)),e)
    LL_RL = auto()   # ((a,((b,c),d)),e)
    LL_RR = auto()   # ((a,(b,(c,d))),e)
    BAL_L = auto()   # ((a,b),((c,d),e))   — balanced left
    BAL_R = auto()   # ((a,b),(c,(d,e)))
    RL_LL = auto()   # (a,(((b,c),d),e))
    RL_LR = auto()   # (a,((b,(c,d)),e))
    RL_BAL = auto()  # (a,((b,c),(d,e)))
    RL_RL = auto()   # (a,(b,((c,d),e)))
    RL_RR = auto()   # (a,(b,(c,(d,e))))   — fully right
    SP_L = auto()    # ((a,(b,c)),(d,e))   — split left
    SP_R = auto()    # (((a,b),c),(d,e))   — split right


class QuintRole(Enum):
    """Semantic roles in a quint."""
    TOKEN_POS_SEG_LAYER_TYPE = auto()  # 5-part transformer embedding
    FIVE_WAY_CONTRASTIVE = auto()      # 5-way contrastive learning
    GENERIC = auto()


@dataclass
class QuintEmbedding:
    """
    A quint embedding in System 5.

    Represents a quinary nesting structure with explicit association choice.
    There are C_4 = 14 distinct ways to associate five elements.

    The canonical (LL_LL) form: ((((a,b),c),d),e)
    In rooted parentheses: [(((()())())())()]

    Properties:
    - first, second, third, fourth, fifth: The five atomic embeddings
    - association: One of the 14 Association5 choices
    - quint_role: Semantic interpretation

    Notes:
    - Pentadic relations have quaternary order (partition [1,1,1,1] has 4 parts)
    - 7-ary relations also have quaternary order
    """
    first: AtomicEmbedding
    second: AtomicEmbedding
    third: AtomicEmbedding
    fourth: AtomicEmbedding
    fifth: AtomicEmbedding
    association: Association5 = Association5.LL_LL
    quint_role: QuintRole = QuintRole.GENERIC
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Nesting depth is 4 for quints."""
        return 4

    @property
    def system(self) -> int:
        """System number is 5 for quints."""
        return 5

    @property
    def embedding_dims(self) -> Tuple[int, int, int, int, int]:
        """Embedding dimensions of all five atoms."""
        return (
            self.first.embedding_dim, self.second.embedding_dim,
            self.third.embedding_dim, self.fourth.embedding_dim,
            self.fifth.embedding_dim
        )

    def flatten(self) -> List[Any]:
        """Flatten to list of atomic data."""
        return (
            self.first.flatten() + self.second.flatten() +
            self.third.flatten() + self.fourth.flatten() +
            self.fifth.flatten()
        )

    def atoms(self) -> Tuple[
        AtomicEmbedding, AtomicEmbedding, AtomicEmbedding,
        AtomicEmbedding, AtomicEmbedding
    ]:
        """Return all five atomic embeddings."""
        return (self.first, self.second, self.third, self.fourth, self.fifth)

    def to_parentheses(self) -> str:
        """Represent as nested parentheses showing association."""
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()
        p4 = self.fourth.to_parentheses()
        p5 = self.fifth.to_parentheses()
        a = Association5
        if self.association == a.LL_LL:
            return f"(((({p1}{p2}){p3}){p4}){p5})"
        elif self.association == a.LL_LR:
            return f"((({p1}({p2}{p3})){p4}){p5})"
        elif self.association == a.LL_BAL:
            return f"((({p1}{p2})({p3}{p4})){p5})"
        elif self.association == a.LL_RL:
            return f"(({p1}(({p2}{p3}){p4})){p5})"
        elif self.association == a.LL_RR:
            return f"(({p1}({p2}({p3}{p4}))){p5})"
        elif self.association == a.BAL_L:
            return f"(({p1}{p2})(({p3}{p4}){p5}))"
        elif self.association == a.BAL_R:
            return f"(({p1}{p2})({p3}({p4}{p5})))"
        elif self.association == a.RL_LL:
            return f"({p1}((({p2}{p3}){p4}){p5}))"
        elif self.association == a.RL_LR:
            return f"({p1}(({p2}({p3}{p4})){p5}))"
        elif self.association == a.RL_BAL:
            return f"({p1}(({p2}{p3})({p4}{p5})))"
        elif self.association == a.RL_RL:
            return f"({p1}({p2}(({p3}{p4}){p5})))"
        elif self.association == a.RL_RR:
            return f"({p1}({p2}({p3}({p4}{p5}))))"
        elif self.association == a.SP_L:
            return f"(({p1}({p2}{p3}))({p4}{p5}))"
        else:  # SP_R
            return f"((({p1}{p2}){p3})({p4}{p5}))"

    def to_rooted_parentheses(self) -> str:
        """
        Represent using '[]' for root and '()' for inner nodes.

        Canonical (LL_LL): [(((()())())())()]
        """
        return self.to_tree().to_rooted_parentheses()

    def to_tree(self) -> 'RootedTree':
        """Convert to rooted tree reflecting association structure."""
        from ..trees import RootedTree, TreeNode

        n1, n2, n3, n4, n5 = (
            self.first.to_tree().root, self.second.to_tree().root,
            self.third.to_tree().root, self.fourth.to_tree().root,
            self.fifth.to_tree().root
        )
        a = Association5

        def _pair(x, y):
            return TreeNode(value="pair", children=[x, y])

        if self.association == a.LL_LL:
            ab = _pair(n1, n2)
            abc = _pair(ab, n3)
            abcd = _pair(abc, n4)
            root = TreeNode(value="quint", children=[abcd, n5])
        elif self.association == a.LL_LR:
            bc = _pair(n2, n3)
            abc = _pair(n1, bc)
            abcd = _pair(abc, n4)
            root = TreeNode(value="quint", children=[abcd, n5])
        elif self.association == a.LL_BAL:
            ab = _pair(n1, n2)
            cd = _pair(n3, n4)
            abcd = _pair(ab, cd)
            root = TreeNode(value="quint", children=[abcd, n5])
        elif self.association == a.LL_RL:
            bc = _pair(n2, n3)
            bcd = _pair(bc, n4)
            abcd = _pair(n1, bcd)
            root = TreeNode(value="quint", children=[abcd, n5])
        elif self.association == a.LL_RR:
            cd = _pair(n3, n4)
            bcd = _pair(n2, cd)
            abcd = _pair(n1, bcd)
            root = TreeNode(value="quint", children=[abcd, n5])
        elif self.association == a.BAL_L:
            ab = _pair(n1, n2)
            cd = _pair(n3, n4)
            cde = _pair(cd, n5)
            root = TreeNode(value="quint", children=[ab, cde])
        elif self.association == a.BAL_R:
            ab = _pair(n1, n2)
            de = _pair(n4, n5)
            cde = _pair(n3, de)
            root = TreeNode(value="quint", children=[ab, cde])
        elif self.association == a.RL_LL:
            bc = _pair(n2, n3)
            bcd = _pair(bc, n4)
            bcde = _pair(bcd, n5)
            root = TreeNode(value="quint", children=[n1, bcde])
        elif self.association == a.RL_LR:
            cd = _pair(n3, n4)
            bcd = _pair(n2, cd)
            bcde = _pair(bcd, n5)
            root = TreeNode(value="quint", children=[n1, bcde])
        elif self.association == a.RL_BAL:
            bc = _pair(n2, n3)
            de = _pair(n4, n5)
            bcde = _pair(bc, de)
            root = TreeNode(value="quint", children=[n1, bcde])
        elif self.association == a.RL_RL:
            cd = _pair(n3, n4)
            cde = _pair(cd, n5)
            bcde = _pair(n2, cde)
            root = TreeNode(value="quint", children=[n1, bcde])
        elif self.association == a.RL_RR:
            de = _pair(n4, n5)
            cde = _pair(n3, de)
            bcde = _pair(n2, cde)
            root = TreeNode(value="quint", children=[n1, bcde])
        elif self.association == a.SP_L:
            bc = _pair(n2, n3)
            abc = _pair(n1, bc)
            de = _pair(n4, n5)
            root = TreeNode(value="quint", children=[abc, de])
        else:  # SP_R
            ab = _pair(n1, n2)
            abc = _pair(ab, n3)
            de = _pair(n4, n5)
            root = TreeNode(value="quint", children=[abc, de])

        return RootedTree(root=root)

    def to_partition(self) -> 'Partition':
        """Convert to partition based on structure balance."""
        from ..ferrer import Partition
        dims = list(self.embedding_dims)
        dims.sort(reverse=True)
        # Simple heuristic: count consecutive equal dims
        if dims[0] == dims[4]:
            return Partition(parts=(5,))
        elif dims[0] == dims[1] == dims[2] == dims[3]:
            return Partition(parts=(4, 1))
        elif dims[1] == dims[2] == dims[3] == dims[4]:
            return Partition(parts=(1, 4))
        elif dims[0] == dims[1] == dims[2]:
            return Partition(parts=(3, 1, 1))
        elif dims[2] == dims[3] == dims[4]:
            return Partition(parts=(1, 1, 3))
        elif dims[0] == dims[1] and dims[2] == dims[3]:
            return Partition(parts=(2, 2, 1))
        elif dims[0] == dims[1] and dims[3] == dims[4]:
            return Partition(parts=(2, 1, 2))
        elif dims[2] == dims[3] and dims[0] == dims[1]:
            return Partition(parts=(2, 2, 1))
        elif dims[0] == dims[1]:
            return Partition(parts=(2, 1, 1, 1))
        elif dims[3] == dims[4]:
            return Partition(parts=(1, 1, 1, 2))
        else:
            return Partition(parts=(1, 1, 1, 1, 1))

    def map(self, f: Callable[[Any], Any]) -> 'QuintEmbedding':
        """Apply function to all atoms' data."""
        return QuintEmbedding(
            first=self.first.map(f),
            second=self.second.map(f),
            third=self.third.map(f),
            fourth=self.fourth.map(f),
            fifth=self.fifth.map(f),
            association=self.association,
            quint_role=self.quint_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def reassociate(self, target: Association5) -> 'QuintEmbedding':
        """Return the same quint with a different association."""
        return QuintEmbedding(
            first=self.first, second=self.second, third=self.third,
            fourth=self.fourth, fifth=self.fifth,
            association=target,
            quint_role=self.quint_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def __repr__(self) -> str:
        assoc = self.association.name
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return (
            f"QuintEmbedding[{assoc}]("
            f"first={self.first.shape}, second={self.second.shape}, "
            f"third={self.third.shape}, fourth={self.fourth.shape}, "
            f"fifth={self.fifth.shape}{role})"
        )


class System5:
    """
    System 5: The Quinary/Quint Embedding System.

    This level has C_4 = 14 distinct association structures for five elements.

    Catalan Analysis:
    ----------------
    C_4 = 14: Fourteen ways to associate five elements.

    Key insight: pentadic relations have quaternary ORDER (4 parts in the
    canonical integer partition [1,1,1,1]), even though they have quinary
    ARITY (5 elements). The partition order is indexed by integer partitions,
    while arity is indexed by Matula primes.

    Rooted Parentheses (canonical LL_LL):
    [(((()())())())()]

    System Order = 5 (5 nodes in the inner tree, half-length = 5).

    Usage:
    ------
    >>> s5 = System5(embedding_dim=64)
    >>> quint = s5.embed_ll_ll(a, b, c, d, e)  # ((((a,b),c),d),e)
    >>> tree = quint.to_tree()
    >>> parens = quint.to_rooted_parentheses()  # "[(((()())())())()]"
    """

    def __init__(
        self,
        base_system: Optional[System1] = None,
        pair_system: Optional[System2] = None,
        triple_system: Optional[System3] = None,
        quad_system: Optional[System4] = None,
        embedding_dim: int = 64
    ):
        """
        Initialize System 5.

        Args:
            base_system: System 1 for atomic embeddings
            pair_system: System 2 for pair operations
            triple_system: System 3 for triple operations
            quad_system: System 4 for quad operations
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
        self.quad_system = quad_system or System4(
            base_system=self.base_system,
            pair_system=self.pair_system,
            triple_system=self.triple_system,
            embedding_dim=embedding_dim
        )
        self.embedding_dim = embedding_dim
        self._catalan = 14  # C_4 = 14

    @property
    def depth(self) -> int:
        """Maximum nesting depth in System 5."""
        return 4

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures (C_4 = 14)."""
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
        fifth: Union[AtomicEmbedding, Any],
        association: Association5 = Association5.LL_LL,
        quint_role: QuintRole = QuintRole.GENERIC,
        role: Optional[str] = None
    ) -> QuintEmbedding:
        """
        Create a quint embedding from five inputs.

        Args:
            first, second, third, fourth, fifth: The five elements
            association: One of the 14 Association5 structures
            quint_role: Semantic role classification
            role: Optional label

        Returns:
            QuintEmbedding with specified structure
        """
        return QuintEmbedding(
            first=self._ensure_atom(first, "first"),
            second=self._ensure_atom(second, "second"),
            third=self._ensure_atom(third, "third"),
            fourth=self._ensure_atom(fourth, "fourth"),
            fifth=self._ensure_atom(fifth, "fifth"),
            association=association,
            quint_role=quint_role,
            semantic_role=role
        )

    def embed_ll_ll(self, a: Any, b: Any, c: Any, d: Any, e: Any,
                    role: Optional[str] = None) -> QuintEmbedding:
        """Create fully left-associative quint: ((((a,b),c),d),e)"""
        return self.embed(a, b, c, d, e, Association5.LL_LL, role=role)

    def embed_ll_bal(self, a: Any, b: Any, c: Any, d: Any, e: Any,
                     role: Optional[str] = None) -> QuintEmbedding:
        """Create left-balanced quint: (((a,b),(c,d)),e)"""
        return self.embed(a, b, c, d, e, Association5.LL_BAL, role=role)

    def embed_bal_l(self, a: Any, b: Any, c: Any, d: Any, e: Any,
                    role: Optional[str] = None) -> QuintEmbedding:
        """Create balanced-left quint: ((a,b),((c,d),e))"""
        return self.embed(a, b, c, d, e, Association5.BAL_L, role=role)

    def embed_bal_r(self, a: Any, b: Any, c: Any, d: Any, e: Any,
                    role: Optional[str] = None) -> QuintEmbedding:
        """Create balanced-right quint: ((a,b),(c,(d,e)))"""
        return self.embed(a, b, c, d, e, Association5.BAL_R, role=role)

    def embed_rl_rr(self, a: Any, b: Any, c: Any, d: Any, e: Any,
                    role: Optional[str] = None) -> QuintEmbedding:
        """Create fully right-associative quint: (a,(b,(c,(d,e))))"""
        return self.embed(a, b, c, d, e, Association5.RL_RR, role=role)

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all 14 structures in System 5.

        Returns parentheses strings for each of the 14 association forms.
        """
        a = AtomicEmbedding(data=None, embedding_dim=self.embedding_dim)
        results = []
        for assoc in Association5:
            q = QuintEmbedding(
                first=a, second=a, third=a, fourth=a, fifth=a,
                association=assoc
            )
            results.append(q.to_parentheses())
        return results

    def enumerate_partitions(self) -> List['Partition']:
        """Enumerate all partitions for System 5 (partitions of 5)."""
        from ..ferrer import Partition
        return [
            Partition(parts=(5,)),
            Partition(parts=(4, 1)),
            Partition(parts=(3, 2)),
            Partition(parts=(3, 1, 1)),
            Partition(parts=(2, 2, 1)),
            Partition(parts=(2, 1, 1, 1)),
            Partition(parts=(1, 1, 1, 1, 1))
        ]

    def __repr__(self) -> str:
        return f"System5(embedding_dim={self.embedding_dim}, structures={self._catalan})"


# Neural network layers (if torch available)
if TORCH_AVAILABLE:
    class QuintLayer(nn.Module):
        """
        Neural network layer for System 5 quint embeddings.

        Processes five inputs according to a specified association structure,
        creating hierarchically structured embeddings.

        Uses the fully left-associative (LL_LL) structure by default:
            ((((f1,f2),f3),f4),f5)
        """

        def __init__(
            self,
            in_features: int,
            hidden_features: int,
            out_features: int,
            association: Association5 = Association5.LL_LL,
            bias: bool = True
        ):
            super().__init__()
            self.in_features = in_features
            self.hidden_features = hidden_features
            self.out_features = out_features
            self.association = association

            # Five input projections
            self.projs = nn.ModuleList([
                nn.Linear(in_features, hidden_features, bias=bias)
                for _ in range(5)
            ])

            # Three inner composition layers
            self.compose1 = nn.Linear(hidden_features * 2, hidden_features, bias=bias)
            self.compose2 = nn.Linear(hidden_features * 2, hidden_features, bias=bias)
            self.compose3 = nn.Linear(hidden_features * 2, hidden_features, bias=bias)
            self.compose4 = nn.Linear(hidden_features * 2, out_features, bias=bias)

            self.system = System5(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 4

        def forward(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor,
            fourth: torch.Tensor,
            fifth: torch.Tensor
        ) -> QuintEmbedding:
            """
            Forward pass with fully left-associative composition (LL_LL):
            ((((f1,f2),f3),f4),f5)
            """
            f = [proj(x) for proj, x in zip(
                self.projs, [first, second, third, fourth, fifth]
            )]

            i1 = self.compose1(torch.cat([f[0], f[1]], dim=-1))
            i2 = self.compose2(torch.cat([i1, f[2]], dim=-1))
            i3 = self.compose3(torch.cat([i2, f[3]], dim=-1))
            out = self.compose4(torch.cat([i3, f[4]], dim=-1))

            return QuintEmbedding(
                first=AtomicEmbedding(data=f[0], semantic_role="first"),
                second=AtomicEmbedding(data=f[1], semantic_role="second"),
                third=AtomicEmbedding(data=f[2], semantic_role="third"),
                fourth=AtomicEmbedding(data=f[3], semantic_role="fourth"),
                fifth=AtomicEmbedding(data=f[4], semantic_role="fifth"),
                association=self.association,
                semantic_role="quint_layer_output",
                metadata={"composed": out}
            )

        def forward_composed(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor,
            fourth: torch.Tensor,
            fifth: torch.Tensor
        ) -> AtomicEmbedding:
            """Forward pass returning composed output (System 1)."""
            quint = self.forward(first, second, third, fourth, fifth)
            return AtomicEmbedding(
                data=quint.metadata["composed"],
                semantic_role="composed_quint"
            )

        def __repr__(self) -> str:
            return (
                f"QuintLayer({self.in_features} -> {self.out_features}, "
                f"association={self.association.name})"
            )

else:
    class QuintLayer:
        """Placeholder for QuintLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for QuintLayer")
