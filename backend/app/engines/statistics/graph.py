"""Graph analysis engine (cooccurrence graph, centrality, communities)."""

from typing import Any

import networkx as nx
import numpy as np
from networkx.algorithms.community import louvain_communities

from app.core.game_definitions import GameConfig

from .base import BaseStatisticsEngine
from .cooccurrence import CooccurrenceEngine


class GraphEngine(BaseStatisticsEngine):
    """Build cooccurrence graph and compute centrality + community metrics."""

    def compute(self, draws: np.ndarray, game: GameConfig) -> dict[int | str, Any]:
        n_draws = draws.shape[0]
        if n_draws == 0:
            return {
                "communities": [],
                "centrality": {},
                "density": 0.0,
                "clustering_coefficient": 0.0,
            }

        # Get the raw cooccurrence matrix from CooccurrenceEngine
        cooc_engine = CooccurrenceEngine()
        cooc_matrix = cooc_engine.get_cooccurrence_matrix(draws, game)

        n = game.numbers_pool
        min_num = game.min_number

        # Build weighted graph
        graph = nx.Graph()
        for i in range(n):
            graph.add_node(i + min_num)

        for i in range(n):
            for j in range(i + 1, n):
                weight = int(cooc_matrix[i, j])
                if weight > 0:
                    graph.add_edge(i + min_num, j + min_num, weight=weight)

        # Centrality metrics
        degree_centrality = nx.degree_centrality(graph)
        betweenness = nx.betweenness_centrality(graph, weight="weight")

        try:
            eigenvector = nx.eigenvector_centrality(graph, weight="weight", max_iter=1000)
        except nx.PowerIterationFailedConvergence:
            # Fallback: uniform values instead of zeros so downstream scoring stays balanced
            n_nodes = graph.number_of_nodes()
            uniform = 1.0 / n_nodes if n_nodes > 0 else 0.0
            eigenvector = {node: uniform for node in graph.nodes()}

        # Community detection (Louvain)
        try:
            communities = louvain_communities(graph, weight="weight", seed=42)
            community_list = [sorted(list(c)) for c in communities]
        except Exception:
            community_list = []

        # Build node-to-community mapping
        node_community = {}
        for idx, comm in enumerate(community_list):
            for node in comm:
                node_community[node] = idx

        centrality = {}
        for node in graph.nodes():
            centrality[node] = {
                "degree": round(degree_centrality.get(node, 0), 4),
                "betweenness": round(betweenness.get(node, 0), 4),
                "eigenvector": round(eigenvector.get(node, 0), 4),
                "community": node_community.get(node, -1),
            }

        return {
            "communities": community_list,
            "centrality": centrality,
            "density": round(nx.density(graph), 4),
            "clustering_coefficient": round(nx.average_clustering(graph, weight="weight"), 4),
        }

    def get_name(self) -> str:
        return "graph"
