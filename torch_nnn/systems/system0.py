"""
System 0: Void/Nest — The Root Embedding Space

Mathematical Properties:
-----------------------
- Nesting Depth: 0 (no content)
- System Order: 0 (half-length of inner parentheses = 0)
- Parentheses: [] (root void, distinguished from tree nodes)
- Tree: Root node with no children
- Partition: [] (empty)

System 0 is the base nestor — the universal embedding space from which
all higher systems emerge. It is the empty rooted tree, represented by
the root bracket '[]' with no inner content.

Key distinctions:
- Root node '[]' is distinct from tree nodes '()'
- System 0 is NOT the same as System 1 (atom); it has no content at all
- It serves as the identity/unit for the nesting hierarchy

In neural network terms:
- The ambient feature space (before any structure is imposed)
- The null embedding / padding token
- The "ground state" of the nested embedding hierarchy
"""

from __future__ import annotations
from typing import Any, Optional, List
from dataclasses import dataclass, field


# Try to import torch if available
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None


@dataclass
class VoidEmbedding:
    """
    A void embedding in System 0.

    Represents the empty/null state — the root of all nesting hierarchies.
    There is exactly one void structure: [] (the root with no children).

    Properties:
    - embedding_dim: Dimension of the ambient embedding space
    - semantic_role: Optional label

    In rooted parentheses: "[]"
    System order: 0
    """
    embedding_dim: int = 0
    semantic_role: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        """Nesting depth is 0 for void."""
        return 0

    @property
    def system(self) -> int:
        """System number is 0 for void."""
        return 0

    @property
    def shape(self):
        """Void has no shape."""
        return ()

    def flatten(self) -> List[Any]:
        """Flatten returns nothing (empty list)."""
        return []

    def to_tree(self) -> 'RootedTree':
        """Convert to empty rooted tree."""
        from ..trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(value="void", children=[]))

    def to_partition(self) -> 'Partition':
        """Convert to empty partition."""
        from ..ferrer import Partition
        return Partition(parts=())

    def to_parentheses(self) -> str:
        """Represent as empty rooted brackets."""
        return "[]"

    def to_rooted_parentheses(self) -> str:
        """Rooted parentheses representation (same as to_parentheses for System 0)."""
        return "[]"

    def __repr__(self) -> str:
        role = f", role='{self.semantic_role}'" if self.semantic_role else ""
        return f"VoidEmbedding(dim={self.embedding_dim}{role})"


class System0:
    """
    System 0: The Void/Nest Embedding System.

    This is the zeroth layer — the ambient embedding space itself.
    It has no structure, no atoms, and no nesting. All higher systems
    are built on top of System 0 as their foundational container.

    Tree Representation:
    -------------------
    The empty rooted tree: a root node [] with no children.
    In rooted parentheses: "[]"

    System Order:
    ------------
    0 — half the length of the inner parentheses string = 0.

    Partition:
    ---------
    [] = empty (no parts)

    Relationship to Higher Systems:
    --------------------------------
    System 0  []          ← void, embedding space
    System 1  [()]        ← single atom
    System 2  [()()]      ← binary pair
    System 3  [(())()]    ← ternary (assoc double)
    System 4  [(()())()]  ← quaternary (assoc triple)

    Usage:
    ------
    >>> s0 = System0(embedding_dim=64)
    >>> void = s0.embed()
    >>> tree = void.to_tree()    # Empty rooted tree
    >>> parens = void.to_parentheses()  # "[]"
    """

    def __init__(self, embedding_dim: int = 64):
        """
        Initialize System 0.

        Args:
            embedding_dim: Dimensionality of the ambient embedding space
        """
        self.embedding_dim = embedding_dim
        self._catalan = 1  # C_{-1} = 1 (one void structure)

    @property
    def depth(self) -> int:
        """Nesting depth is 0 for System 0."""
        return 0

    @property
    def catalan_number(self) -> int:
        """Number of distinct structures: 1 (only the void)."""
        return self._catalan

    @property
    def structure_count(self) -> int:
        """Alias for catalan_number."""
        return self._catalan

    def embed(self, role: Optional[str] = None) -> VoidEmbedding:
        """
        Create a void embedding.

        Args:
            role: Optional semantic label

        Returns:
            VoidEmbedding representing the empty structure
        """
        return VoidEmbedding(
            embedding_dim=self.embedding_dim,
            semantic_role=role
        )

    def enumerate_structures(self) -> List[str]:
        """
        Enumerate all structures in System 0.

        Returns: ["[]"] — the single void structure
        """
        return ["[]"]

    def structure_tree(self) -> 'RootedTree':
        """Get the canonical tree for System 0 (empty rooted tree)."""
        from ..trees import RootedTree, TreeNode
        return RootedTree(root=TreeNode(value="void", children=[]))

    def __repr__(self) -> str:
        return f"System0(embedding_dim={self.embedding_dim})"


# Neural network layer (if torch available)
if TORCH_AVAILABLE:
    class VoidLayer(nn.Module):
        """
        Neural network layer for System 0 void embeddings.

        This layer produces a learned "null" representation —
        a zero-content embedding that serves as the base for
        all nested structures. Useful as a padding/mask token
        or as an initializer for nested sequence models.
        """

        def __init__(self, embedding_dim: int):
            super().__init__()
            self.embedding_dim = embedding_dim
            # Learnable null vector (the "void" embedding)
            self.null_embedding = nn.Parameter(torch.zeros(embedding_dim))
            self.system = System0(embedding_dim=embedding_dim)

        @property
        def depth(self) -> int:
            return 0

        def forward(self, batch_size: int = 1) -> VoidEmbedding:
            """
            Forward pass returning a VoidEmbedding.

            Args:
                batch_size: Number of void embeddings to produce

            Returns:
                VoidEmbedding containing the null vector
            """
            data = self.null_embedding.unsqueeze(0).expand(batch_size, -1)
            return VoidEmbedding(
                embedding_dim=self.embedding_dim,
                semantic_role="void_layer_output",
                metadata={"data": data}
            )

        def __repr__(self) -> str:
            return f"VoidLayer(embedding_dim={self.embedding_dim})"

else:
    class VoidLayer:
        """Placeholder for VoidLayer when PyTorch is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required for VoidLayer")
