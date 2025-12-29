"""
System 3: Triple/Ternary Tensors - The Emergence of Association Ambiguity

Mathematical Properties:
-----------------------
- Nesting Depth: 2 (double nesting)
- Catalan Number: C_2 = 2 (two structures!)
- Parentheses: ((()())()) or (()(()()))
- Trees: Two distinct binary tree shapes with 3 leaves
- Partitions: [3], [2,1], [1,1,1]

System 3 is where the Catalan structure first becomes non-trivial.
With C_2 = 2, there are TWO distinct ways to associate three elements:

1. Left-associative: ((a ⊗ b) ⊗ c)  -  "first combine a,b, then add c"
2. Right-associative: (a ⊗ (b ⊗ c))  -  "first combine b,c, then add a"

This mirrors fundamental concepts in:
- Algebra: (a * b) * c vs a * (b * c)
- Language: ((hot dog) stand) vs (hot (dog stand))
- Neural networks: Sequential vs skip connections

The choice of association IS the structure. Isomorphic algebras may
have different associative behaviors, captured by the Catalan variants.
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto
import math

from .system1 import System1, AtomicEmbedding
from .system2 import System2, PairEmbedding, PairType

# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


T = TypeVar('T')


class Association(Enum):
    """The two Catalan-2 association patterns for triples."""
    LEFT = auto()   # ((a, b), c) - left-associative
    RIGHT = auto()  # (a, (b, c)) - right-associative


class TripleRole(Enum):
    """Semantic roles in a triple."""
    SUBJECT_VERB_OBJECT = auto()  # Linguistic triple
    QUERY_KEY_VALUE = auto()       # Attention triple
    HEAD_RELATION_TAIL = auto()    # Knowledge graph triple
    ANCHOR_POSITIVE_NEGATIVE = auto()  # Contrastive triple
    ENCODER_DECODER_CROSS = auto()  # Transformer triple
    GENERIC = auto()                # Unspecified


@dataclass
class TripleEmbedding:
    """
    A triple embedding in System 3.

    Represents a ternary nesting structure with explicit association choice.
    The association determines the hierarchical structure:

    LEFT:  ((first ⊗ second) ⊗ third)
           The first two elements form a pair, then combine with third.

    RIGHT: (first ⊗ (second ⊗ third))
           The last two elements form a pair, then combine with first.

    This is the first System where STRUCTURE ITSELF is a choice.
    Different associations create different embeddings even for
    the same atomic inputs.

    Properties:
    - first, second, third: The three atomic embeddings
    - association: LEFT or RIGHT structure choice
    - triple_role: Semantic interpretation of the triple
    """
    first: AtomicEmbedding
    second: AtomicEmbedding
    third: AtomicEmbedding
    association: Association = Association.LEFT
    triple_role: TripleRole = TripleRole.GENERIC
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Nesting depth is 2 for triples."""
        return 2

    @property
    def system(self) -> int:
        """System number is 3 for triples."""
        return 3

    @property
    def shape(self) -> Tuple:
        """Shape as nested tuple reflecting association."""
        s1, s2, s3 = self.first.shape, self.second.shape, self.third.shape
        if self.association == Association.LEFT:
            return ((s1, s2), s3)
        else:
            return (s1, (s2, s3))

    @property
    def embedding_dims(self) -> Tuple[int, int, int]:
        """Embedding dimensions of all three atoms."""
        return (self.first.embedding_dim, self.second.embedding_dim, self.third.embedding_dim)

    def flatten(self) -> List[Any]:
        """Flatten to list of atomic data."""
        return self.first.flatten() + self.second.flatten() + self.third.flatten()

    def atoms(self) -> Tuple[AtomicEmbedding, AtomicEmbedding, AtomicEmbedding]:
        """Return all three atomic embeddings."""
        return (self.first, self.second, self.third)

    def inner_pair(self) -> PairEmbedding:
        """
        Return the inner pair based on association.

        LEFT: (first, second)
        RIGHT: (second, third)
        """
        if self.association == Association.LEFT:
            return PairEmbedding(
                left=self.first,
                right=self.second,
                semantic_role="inner_pair"
            )
        else:
            return PairEmbedding(
                left=self.second,
                right=self.third,
                semantic_role="inner_pair"
            )

    def outer_pair(self) -> PairEmbedding:
        """
        Return the outer pair (inner_pair combined with remaining).

        This conceptually pairs the inner_pair with the third element.
        """
        inner = self.inner_pair()
        if self.association == Association.LEFT:
            return PairEmbedding(
                left=inner.compose_concat(),  # Flatten inner pair to atom
                right=self.third,
                semantic_role="outer_pair"
            )
        else:
            return PairEmbedding(
                left=self.first,
                right=inner.compose_concat(),
                semantic_role="outer_pair"
            )

    def to_tree(self) -> 'RootedTree':
        """
        Convert to rooted tree reflecting association structure.

        LEFT:     triple
                 /      \\
              pair     third
             /    \\
          first  second

        RIGHT:    triple
                 /      \\
             first     pair
                      /    \\
                  second  third
        """
        from ..trees import RootedTree, TreeNode

        first_node = self.first.to_tree().root
        second_node = self.second.to_tree().root
        third_node = self.third.to_tree().root

        if self.association == Association.LEFT:
            inner_pair = TreeNode(value="pair", children=[first_node, second_node])
            root = TreeNode(
                value="triple",
                children=[inner_pair, third_node],
                metadata={"association": "LEFT", "role": self.triple_role.name}
            )
        else:
            inner_pair = TreeNode(value="pair", children=[second_node, third_node])
            root = TreeNode(
                value="triple",
                children=[first_node, inner_pair],
                metadata={"association": "RIGHT", "role": self.triple_role.name}
            )

        return RootedTree(root=root)

    def to_partition(self) -> 'Partition':
        """
        Convert to partition based on structure balance.

        - All equal: [3]
        - Two equal: [2,1]
        - All different: [1,1,1]
        """
        from ..ferrer import Partition
        dims = self.embedding_dims
        if dims[0] == dims[1] == dims[2]:
            return Partition(parts=(3,))
        elif dims[0] == dims[1] or dims[1] == dims[2] or dims[0] == dims[2]:
            return Partition(parts=(2, 1))
        else:
            return Partition(parts=(1, 1, 1))

    def to_parentheses(self) -> str:
        """Represent as nested parentheses showing association."""
        p1 = self.first.to_parentheses()
        p2 = self.second.to_parentheses()
        p3 = self.third.to_parentheses()

        if self.association == Association.LEFT:
            return f"(({p1}{p2}){p3})"
        else:
            return f"({p1}({p2}{p3}))"

    def map(self, f: Callable[[Any], Any]) -> 'TripleEmbedding':
        """Apply function to all atoms' data."""
        return TripleEmbedding(
            first=self.first.map(f),
            second=self.second.map(f),
            third=self.third.map(f),
            association=self.association,
            triple_role=self.triple_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def reassociate(self) -> 'TripleEmbedding':
        """Return the same triple with opposite association."""
        new_assoc = Association.RIGHT if self.association == Association.LEFT else Association.LEFT
        return TripleEmbedding(
            first=self.first,
            second=self.second,
            third=self.third,
            association=new_assoc,
            triple_role=self.triple_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def rotate_left(self) -> 'TripleEmbedding':
        """Rotate elements: (a,b,c) -> (b,c,a)"""
        return TripleEmbedding(
            first=self.second,
            second=self.third,
            third=self.first,
            association=self.association,
            triple_role=self.triple_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def rotate_right(self) -> 'TripleEmbedding':
        """Rotate elements: (a,b,c) -> (c,a,b)"""
        return TripleEmbedding(
            first=self.third,
            second=self.first,
            third=self.second,
            association=self.association,
            triple_role=self.triple_role,
            semantic_role=self.semantic_role,
            metadata=self.metadata.copy()
        )

    def compose_hierarchical(self) -> AtomicEmbedding:
        """
        Compose following the association hierarchy.

        LEFT: compose(compose(first, second), third)
        RIGHT: compose(first, compose(second, third))

        Returns to System 1.
        """
        inner = self.inner_pair().compose_concat()
        if self.association == Association.LEFT:
            outer = PairEmbedding(left=inner, right=self.third)
        else:
            outer = PairEmbedding(left=self.first, right=inner)
        return outer.compose_concat()

    def compose_flat(self) -> AtomicEmbedding:
        """Compose by concatenating all three (ignores association)."""
        if TORCH_AVAILABLE and hasattr(self.first.data, 'shape'):
            composed = torch.cat([self.first.data, self.second.data, self.third.data], dim=-1)
        else:
            import numpy as np
            composed = np.concatenate([self.first.data, self.second.data, self.third.data], axis=-1)

        return AtomicEmbedding(
            data=composed,
            semantic_role=f"flat_triple({self.semantic_role})" if self.semantic_role else "flat_triple"
        )

    def __repr__(self) -> str:
        assoc = "L" if self.association == Association.LEFT else "R"
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return f"TripleEmbedding[{assoc}](first={self.first.shape}, second={self.second.shape}, third={self.third.shape}{role})"


class System3:
    """
    System 3: The Ternary/Triple Embedding System.

    This level introduces association ambiguity - the first point
    where structure itself becomes a meaningful choice.

    Catalan Analysis:
    ----------------
    C_2 = 2: Two ways to associate three elements.

    ((a b) c)  vs  (a (b c))

    This is the Catalan number for n=2, counting binary trees with 3 leaves.

    Tree Representations:
    --------------------
    LEFT:       ∧           RIGHT:      ∧
               / \\                     / \\
              ∧   c                   a   ∧
             / \\                         / \\
            a   b                       b   c

    Ferrer Diagrams:
    ---------------
    [3] = ███       (maximally balanced)
    [2,1] = ██      (one pair + one singleton)
            █
    [1,1,1] = █     (fully unbalanced)
              █
              █

    Structure Space:
    ---------------
    System 3 has a 2-dimensional structure space:
    - Dimension 1: Association (LEFT/RIGHT)
    - Dimension 2: Partition shape ([3], [2,1], [1,1,1])

    The full embedding lives in Atoms × Structures.

    Usage:
    ------
    >>> s3 = System3(embedding_dim=64)
    >>> triple = s3.embed_left(a, b, c)  # ((a,b),c)
    >>> alt = triple.reassociate()        # (a,(b,c))
    >>> tree = triple.to_tree()
    >>> parens = triple.to_parentheses()  # "((()())())"
    """

    def __init__(
        self,
        base_system: Optional[System1] = None,
        pair_system: Optional[System2] = None,
        embedding_dim: int = 64
    ):
        """
        Initialize System 3.

        Args:
            base_system: System 1 for atomic embeddings
            pair_system: System 2 for pair operations
            embedding_dim: Default dimensionality
        """
        self.base_system = base_system or System1(embedding_dim=embedding_dim)
        self.pair_system = pair_system or System2(base_system=self.base_system, embedding_dim=embedding_dim)
        self.embedding_dim = embedding_dim
        self._catalan = 2  # C_2 = 2

    @property
    def depth(self) -> int:
        """Maximum nesting depth in System 3."""
        return 2

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures (C_2 = 2)."""
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
        association: Association = Association.LEFT,
        triple_role: TripleRole = TripleRole.GENERIC,
        role: Optional[str] = None
    ) -> TripleEmbedding:
        """
        Create a triple embedding from three inputs.

        Args:
            first, second, third: The three elements
            association: LEFT or RIGHT structure
            triple_role: Semantic role classification
            role: Optional label

        Returns:
            TripleEmbedding with specified structure
        """
        return TripleEmbedding(
            first=self._ensure_atom(first, "first"),
            second=self._ensure_atom(second, "second"),
            third=self._ensure_atom(third, "third"),
            association=association,
            triple_role=triple_role,
            semantic_role=role
        )

    def embed_left(
        self,
        first: Any,
        second: Any,
        third: Any,
        role: Optional[str] = None
    ) -> TripleEmbedding:
        """Create left-associative triple: ((first, second), third)"""
        return self.embed(first, second, third, Association.LEFT, role=role)

    def embed_right(
        self,
        first: Any,
        second: Any,
        third: Any,
        role: Optional[str] = None
    ) -> TripleEmbedding:
        """Create right-associative triple: (first, (second, third))"""
        return self.embed(first, second, third, Association.RIGHT, role=role)

    def embed_qkv(
        self,
        query: Any,
        key: Any,
        value: Any,
        association: Association = Association.LEFT
    ) -> TripleEmbedding:
        """
        Create query-key-value triple for attention.

        Default LEFT association: ((Q ⊗ K) ⊗ V)
        This matches how attention computes: softmax(QK^T)V
        """
        return self.embed(
            query, key, value,
            association=association,
            triple_role=TripleRole.QUERY_KEY_VALUE,
            role="attention"
        )

    def embed_svo(
        self,
        subject: Any,
        verb: Any,
        obj: Any,
        association: Association = Association.LEFT
    ) -> TripleEmbedding:
        """Create subject-verb-object linguistic triple."""
        return self.embed(
            subject, verb, obj,
            association=association,
            triple_role=TripleRole.SUBJECT_VERB_OBJECT,
            role="linguistic"
        )

    def embed_hrt(
        self,
        head: Any,
        relation: Any,
        tail: Any,
        association: Association = Association.LEFT
    ) -> TripleEmbedding:
        """Create head-relation-tail knowledge graph triple."""
        return self.embed(
            head, relation, tail,
            association=association,
            triple_role=TripleRole.HEAD_RELATION_TAIL,
            role="knowledge_graph"
        )

    def embed_contrastive(
        self,
        anchor: Any,
        positive: Any,
        negative: Any,
        association: Association = Association.LEFT
    ) -> TripleEmbedding:
        """Create anchor-positive-negative contrastive triple."""
        return self.embed(
            anchor, positive, negative,
            association=association,
            triple_role=TripleRole.ANCHOR_POSITIVE_NEGATIVE,
            role="contrastive"
        )

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all structures in System 3.

        Returns: ["((()())())", "(()(()())) "] - both associations
        """
        return ["((()())())", "(()(()()))"]

    def enumerate_partitions(self) -> List['Partition']:
        """Enumerate all partitions for System 3 (partitions of 3)."""
        from ..ferrer import Partition
        return [
            Partition(parts=(3,)),
            Partition(parts=(2, 1)),
            Partition(parts=(1, 1, 1))
        ]

    def structure_trees(self) -> List['RootedTree']:
        """Get both canonical trees for System 3 structures."""
        from ..trees import RootedTree, TreeNode, leaf, pair, triple_left, triple_right

        a, b, c = leaf("a"), leaf("b"), leaf("c")
        return [
            triple_left(a, b, c),   # LEFT: ((a,b),c)
            triple_right(a, b, c)   # RIGHT: (a,(b,c))
        ]

    def associator(
        self,
        triple: TripleEmbedding,
        target: Association
    ) -> TripleEmbedding:
        """
        Apply the associator to change association.

        In category theory, the associator is the natural isomorphism:
        α: (A ⊗ B) ⊗ C → A ⊗ (B ⊗ C)

        This transforms between the two Catalan structures.
        """
        if triple.association == target:
            return triple  # Already in target form
        return triple.reassociate()

    def __repr__(self) -> str:
        return f"System3(embedding_dim={self.embedding_dim}, structures={self._catalan})"


# Neural network layers (if torch available)
if TORCH_AVAILABLE:
    class TripleLayer(nn.Module):
        """
        Neural network layer for System 3 triple embeddings.

        Processes three inputs according to a specified association,
        creating hierarchically structured embeddings.

        Architecture (LEFT):
            first  \\
                    > pair_layer \\
            second /              > compose_layer -> output
            third ---------------/

        Architecture (RIGHT):
            first ---------------\\
                                  > compose_layer -> output
            second \\            /
                    > pair_layer
            third  /
        """

        def __init__(
            self,
            in_features: int,
            hidden_features: int,
            out_features: int,
            association: Association = Association.LEFT,
            bias: bool = True
        ):
            super().__init__()
            self.in_features = in_features
            self.hidden_features = hidden_features
            self.out_features = out_features
            self.association = association

            # Three input projections
            self.first_proj = nn.Linear(in_features, hidden_features, bias=bias)
            self.second_proj = nn.Linear(in_features, hidden_features, bias=bias)
            self.third_proj = nn.Linear(in_features, hidden_features, bias=bias)

            # Inner pair composition
            self.inner_compose = nn.Linear(hidden_features * 2, hidden_features, bias=bias)

            # Outer composition
            self.outer_compose = nn.Linear(hidden_features * 2, out_features, bias=bias)

            self.system = System3(embedding_dim=out_features)

        @property
        def depth(self) -> int:
            return 2

        def forward(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor
        ) -> TripleEmbedding:
            """
            Forward pass processing a triple of inputs.

            Follows the association structure for hierarchical composition.
            """
            f1 = self.first_proj(first)
            f2 = self.second_proj(second)
            f3 = self.third_proj(third)

            if self.association == Association.LEFT:
                # ((first, second), third)
                inner = self.inner_compose(torch.cat([f1, f2], dim=-1))
                outer = self.outer_compose(torch.cat([inner, f3], dim=-1))
            else:
                # (first, (second, third))
                inner = self.inner_compose(torch.cat([f2, f3], dim=-1))
                outer = self.outer_compose(torch.cat([f1, inner], dim=-1))

            # Return as TripleEmbedding with original structure
            return TripleEmbedding(
                first=AtomicEmbedding(data=f1, semantic_role="first"),
                second=AtomicEmbedding(data=f2, semantic_role="second"),
                third=AtomicEmbedding(data=f3, semantic_role="third"),
                association=self.association,
                semantic_role="triple_layer_output",
                metadata={"composed": outer}
            )

        def forward_composed(
            self,
            first: torch.Tensor,
            second: torch.Tensor,
            third: torch.Tensor
        ) -> AtomicEmbedding:
            """Forward pass returning composed output (System 1)."""
            triple = self.forward(first, second, third)
            return AtomicEmbedding(
                data=triple.metadata["composed"],
                semantic_role="composed_triple"
            )

        def __repr__(self) -> str:
            assoc = "LEFT" if self.association == Association.LEFT else "RIGHT"
            return f"TripleLayer({self.in_features} -> {self.out_features}, association={assoc})"


    class AttentionTripleLayer(nn.Module):
        """
        Attention-based triple layer implementing Query-Key-Value.

        Uses the natural QKV structure of attention, where:
        - Query and Key form the inner pair (attention scores)
        - Value combines with attention output

        This is fundamentally LEFT-associative: ((Q ⊗ K) ⊗ V)
        """

        def __init__(
            self,
            embed_dim: int,
            num_heads: int = 1,
            dropout: float = 0.0
        ):
            super().__init__()
            self.embed_dim = embed_dim
            self.num_heads = num_heads

            self.q_proj = nn.Linear(embed_dim, embed_dim)
            self.k_proj = nn.Linear(embed_dim, embed_dim)
            self.v_proj = nn.Linear(embed_dim, embed_dim)
            self.out_proj = nn.Linear(embed_dim, embed_dim)

            self.dropout = nn.Dropout(dropout)
            self.scale = (embed_dim // num_heads) ** -0.5

            self.system = System3(embedding_dim=embed_dim)

        @property
        def depth(self) -> int:
            return 2

        def forward(
            self,
            query: torch.Tensor,
            key: torch.Tensor,
            value: torch.Tensor
        ) -> TripleEmbedding:
            """
            Attention forward pass.

            Implements: Attention(Q, K, V) = softmax(QK^T / sqrt(d)) V

            The structure is ((Q ⊗ K) ⊗ V):
            1. Inner pair: Q ⊗ K -> attention scores
            2. Outer: scores ⊗ V -> attended output
            """
            q = self.q_proj(query)
            k = self.k_proj(key)
            v = self.v_proj(value)

            # Inner pair: QK attention
            attn_scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale
            attn_probs = torch.softmax(attn_scores, dim=-1)
            attn_probs = self.dropout(attn_probs)

            # Outer: apply to V
            attn_output = torch.matmul(attn_probs, v)
            output = self.out_proj(attn_output)

            return TripleEmbedding(
                first=AtomicEmbedding(data=q, semantic_role="query"),
                second=AtomicEmbedding(data=k, semantic_role="key"),
                third=AtomicEmbedding(data=v, semantic_role="value"),
                association=Association.LEFT,  # Attention is inherently left-associative
                triple_role=TripleRole.QUERY_KEY_VALUE,
                semantic_role="attention_output",
                metadata={"output": output, "attn_probs": attn_probs}
            )

        def __repr__(self) -> str:
            return f"AttentionTripleLayer(embed_dim={self.embed_dim}, heads={self.num_heads})"

else:
    class TripleLayer:
        """Placeholder for TripleLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for TripleLayer")

    class AttentionTripleLayer:
        """Placeholder for AttentionTripleLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for AttentionTripleLayer")
