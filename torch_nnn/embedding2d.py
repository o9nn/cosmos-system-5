"""
2D Matrix Embeddings for Nested Tensors

Mathematical Foundation:
-----------------------
Moving from 1D (Catalan/ordered trees) to 2D (Matula/unordered trees):

1D Interval (Catalan):
  - Binary trees with ordered children
  - Left ≠ Right: (a,b) ≠ (b,a)
  - Structure count: C_n = 1, 1, 2, 5, 14, 42, ...
  - Represents: nested parentheses, Dyck paths

2D Plane (Matula):
  - Rooted trees with unordered children
  - Symmetric: {a,b} = {b,a}
  - Structure count: sys(n) = 1, 1, 2, 4, 9, 20, 48, ...
  - Represents: molecular structures, type hierarchies

The 2D embedding uses matrices where:
  - Rows index tree nodes
  - Columns index embedding dimensions
  - Matrix structure reflects tree structure via Matula encoding

Key insight: Matula number m encodes a tree, and m's prime factorization
directly gives the tree structure. This enables:
  - Integer ↔ Tree bijection
  - Compositional matrix operations
  - Structure-preserving embeddings
"""

from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, Dict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import math

from .matula import (
    MatulaTree, MatulaNode, sys, a000081,
    nth_prime, prime_index, prime_factorization,
    enumerate_matula_trees
)

# Try to import torch/numpy
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


@dataclass
class TreeEmbedding2D:
    """
    A 2D matrix embedding indexed by tree structure.

    The embedding is a matrix where:
    - Rows correspond to nodes in the tree
    - Columns are embedding dimensions
    - The tree structure (Matula number) determines row semantics

    Properties:
    - tree: The MatulaTree defining the structure
    - matrix: The embedding matrix (nodes × dims)
    - node_embeddings: Dict mapping node position to row index
    """
    tree: MatulaTree
    matrix: Any  # numpy array or torch tensor
    node_order: List[int] = field(default_factory=list)  # Matula numbers of nodes in row order

    def __post_init__(self):
        if not self.node_order:
            # Default: traverse tree and assign rows
            self.node_order = self._compute_node_order()

    def _compute_node_order(self) -> List[int]:
        """Compute canonical ordering of nodes for matrix rows."""
        order = []

        def traverse(node: MatulaNode):
            order.append(node.matula_number())
            # Sort children by Matula number for canonical order
            sorted_children = sorted(node.children, key=lambda c: c.matula_number())
            for child in sorted_children:
                traverse(child)

        traverse(self.tree.root)
        return order

    @property
    def matula(self) -> int:
        """Matula number of the tree structure."""
        return self.tree.matula

    @property
    def num_nodes(self) -> int:
        """Number of nodes (rows in matrix)."""
        return self.tree.size

    @property
    def embedding_dim(self) -> int:
        """Embedding dimension (columns in matrix)."""
        if hasattr(self.matrix, 'shape'):
            return self.matrix.shape[1] if len(self.matrix.shape) > 1 else 1
        return 0

    @property
    def shape(self) -> Tuple[int, int]:
        """Shape of embedding matrix."""
        return (self.num_nodes, self.embedding_dim)

    @property
    def system(self) -> int:
        """System number (edges in tree)."""
        return self.tree.system

    def node_embedding(self, node_matula: int) -> Any:
        """Get embedding for a specific node by its Matula number."""
        if node_matula not in self.node_order:
            raise ValueError(f"No node with Matula number {node_matula}")
        row = self.node_order.index(node_matula)
        return self.matrix[row]

    def root_embedding(self) -> Any:
        """Get embedding for the root node."""
        return self.matrix[0]

    def leaf_embeddings(self) -> Any:
        """Get embeddings for all leaf nodes."""
        leaf_rows = [i for i, m in enumerate(self.node_order) if m == 1]
        return self.matrix[leaf_rows]

    def subtree_embedding(self, node_matula: int) -> 'TreeEmbedding2D':
        """Extract embedding for a subtree."""
        # Find the node and its subtree
        subtree = MatulaTree.from_matula(node_matula)

        # Get rows corresponding to this subtree
        start_idx = self.node_order.index(node_matula)
        end_idx = start_idx + subtree.size

        return TreeEmbedding2D(
            tree=subtree,
            matrix=self.matrix[start_idx:end_idx],
            node_order=self.node_order[start_idx:end_idx]
        )

    def compose(self, other: 'TreeEmbedding2D', operation: str = 'concat') -> 'TreeEmbedding2D':
        """
        Compose two tree embeddings.

        Creates a new tree with both as children of a new root.
        The resulting Matula number is related to the product.
        """
        # Create combined tree
        combined_root = MatulaNode(children=[self.tree.root, other.tree.root])
        combined_tree = MatulaTree(root=combined_root)

        if operation == 'concat':
            # Stack matrices vertically, add root embedding
            if TORCH_AVAILABLE and isinstance(self.matrix, torch.Tensor):
                root_embed = torch.zeros(1, self.embedding_dim)
                combined_matrix = torch.cat([root_embed, self.matrix, other.matrix], dim=0)
            else:
                root_embed = np.zeros((1, self.embedding_dim))
                combined_matrix = np.concatenate([root_embed, self.matrix, other.matrix], axis=0)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        # Compute new node order
        combined_order = [combined_tree.matula] + self.node_order + other.node_order

        return TreeEmbedding2D(
            tree=combined_tree,
            matrix=combined_matrix,
            node_order=combined_order
        )

    def to_adjacency(self) -> Any:
        """
        Convert tree structure to adjacency matrix.

        Returns (num_nodes × num_nodes) matrix where A[i,j] = 1
        if node i is parent of node j.
        """
        n = self.num_nodes
        if TORCH_AVAILABLE and isinstance(self.matrix, torch.Tensor):
            adj = torch.zeros(n, n)
        else:
            adj = np.zeros((n, n))

        def fill_adjacency(node: MatulaNode, parent_idx: int, current_idx: List[int]):
            idx = current_idx[0]
            current_idx[0] += 1

            if parent_idx >= 0:
                adj[parent_idx, idx] = 1

            for child in sorted(node.children, key=lambda c: c.matula_number()):
                fill_adjacency(child, idx, current_idx)

        fill_adjacency(self.tree.root, -1, [0])
        return adj

    def __repr__(self) -> str:
        return f"TreeEmbedding2D(matula={self.matula}, shape={self.shape}, system={self.system})"


class System2D:
    """
    2D Embedding System using Matula-indexed trees.

    Each System-K represents trees with K edges (K+1 nodes).
    sys(K) gives the number of distinct tree structures.

    sys(0) = 1:  Single node ●
    sys(1) = 1:  Edge ●─●
    sys(2) = 2:  Chain ●─●─● or Fork ●<●
                                     ╲●
    sys(3) = 4:  Four distinct 4-node trees
    sys(4) = 9:  Nine distinct 5-node trees
    ...
    """

    def __init__(self, system_number: int, embedding_dim: int = 64):
        """
        Initialize a 2D system.

        Args:
            system_number: Which system (0, 1, 2, 3, ...)
            embedding_dim: Dimension of node embeddings
        """
        self.k = system_number
        self.embedding_dim = embedding_dim
        self._structures = None

    @property
    def num_structures(self) -> int:
        """Number of distinct tree structures."""
        return sys(self.k)

    @property
    def num_nodes(self) -> int:
        """Number of nodes per tree."""
        return self.k + 1

    @property
    def num_edges(self) -> int:
        """Number of edges per tree."""
        return self.k

    def structures(self) -> List[MatulaTree]:
        """Enumerate all tree structures in this system."""
        if self._structures is None:
            self._structures = list(enumerate_matula_trees(self.num_nodes))
        return self._structures

    def matula_numbers(self) -> List[int]:
        """Get Matula numbers for all structures."""
        return [t.matula for t in self.structures()]

    def embed_zeros(self, structure: Union[int, MatulaTree]) -> TreeEmbedding2D:
        """Create zero-initialized embedding for a structure."""
        if isinstance(structure, int):
            structure = MatulaTree.from_matula(structure)

        if TORCH_AVAILABLE:
            matrix = torch.zeros(structure.size, self.embedding_dim)
        else:
            matrix = np.zeros((structure.size, self.embedding_dim))

        return TreeEmbedding2D(tree=structure, matrix=matrix)

    def embed_randn(self, structure: Union[int, MatulaTree]) -> TreeEmbedding2D:
        """Create random normal-initialized embedding for a structure."""
        if isinstance(structure, int):
            structure = MatulaTree.from_matula(structure)

        if TORCH_AVAILABLE:
            matrix = torch.randn(structure.size, self.embedding_dim)
        else:
            matrix = np.random.randn(structure.size, self.embedding_dim)

        return TreeEmbedding2D(tree=structure, matrix=matrix)

    def embed_data(self, structure: Union[int, MatulaTree], data: Any) -> TreeEmbedding2D:
        """Create embedding from data matrix."""
        if isinstance(structure, int):
            structure = MatulaTree.from_matula(structure)

        return TreeEmbedding2D(tree=structure, matrix=data)

    def __repr__(self) -> str:
        return f"System2D(k={self.k}, structures={self.num_structures}, nodes={self.num_nodes})"


# Comparison: 1D vs 2D structure counts

def compare_1d_2d(max_n: int = 10) -> str:
    """
    Compare Catalan (1D) vs A000081 (2D) structure counts.
    """
    from .core import catalan

    lines = [
        "╔═══════════╦═══════════════════╦═══════════════════╗",
        "║  System   ║  1D (Catalan)     ║  2D (Matula)      ║",
        "║    n      ║  Ordered Trees    ║  Unordered Trees  ║",
        "╠═══════════╬═══════════════════╬═══════════════════╣",
    ]

    for n in range(max_n):
        cat_n = catalan(n)
        sys_n = sys(n)
        lines.append(f"║    {n:<2}     ║      {cat_n:<6}        ║      {sys_n:<6}        ║")

    lines.append("╚═══════════╩═══════════════════╩═══════════════════╝")
    return "\n".join(lines)


def visualize_system_structures(k: int) -> str:
    """
    Visualize all tree structures in System-K.
    """
    system = System2D(k)
    structures = system.structures()

    lines = [
        f"System {k}: {system.num_structures} structure(s) with {system.num_nodes} nodes",
        "=" * 50
    ]

    for i, tree in enumerate(structures, 1):
        lines.append(f"\nStructure {i}: Matula number = {tree.matula}")
        lines.append(str(tree))

    return "\n".join(lines)
