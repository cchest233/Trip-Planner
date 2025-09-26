"""Geospatial helpers for clustering POIs."""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

import numpy as np
from sklearn.cluster import KMeans

from src.models import CandidatePOI


def cluster_pois(
    pois: Sequence[CandidatePOI],
    min_k: int = 3,
    max_k: int = 5,
) -> Dict[int, List[CandidatePOI]]:
    """Cluster POIs geographically using KMeans."""

    if not pois:
        return {}
    k = max(min_k, min(max_k, len(pois)))
    coords = np.array([[poi.lat, poi.lon] for poi in pois])
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(coords)
    clusters: Dict[int, List[CandidatePOI]] = {}
    for label, poi in zip(labels, pois):
        clusters.setdefault(int(label), []).append(poi)
    return clusters


def select_top_pois(cluster: Iterable[CandidatePOI], scores: Dict[str, float], limit: int) -> List[CandidatePOI]:
    """Select POIs with highest score based on provided score mapping."""

    sorted_pois = sorted(cluster, key=lambda poi: scores.get(poi.poi_id, 0.0), reverse=True)
    return sorted_pois[:limit]


__all__ = ["cluster_pois", "select_top_pois"]
