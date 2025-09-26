from datetime import date

from src.logic.scheduler_node import compute_poi_scores
from src.models import CandidatePOI, POISource
from src.utils.geo import cluster_pois


def _make_poi(idx: int) -> CandidatePOI:
    return CandidatePOI(
        poi_id=f"poi_{idx}",
        name=f"POI {idx}",
        lat=35.0 + idx * 0.01,
        lon=135.0 + idx * 0.01,
        category="museum" if idx % 2 == 0 else "food",
        popularity=0.5 + 0.1 * idx,
        min_dwell=60,
        source=POISource(name="demo", url="https://demo", fetched_at=date.today().isoformat()),
    )


def test_compute_poi_scores_prefers_theme_weight():
    pois = [_make_poi(i) for i in range(3)]
    weights = {"museum": 1.2, "food": 0.8, "other": 0.5}
    scores = compute_poi_scores(pois, weights)
    assert scores["poi_0"] > scores["poi_1"]


def test_cluster_pois_returns_expected_clusters():
    pois = [_make_poi(i) for i in range(5)]
    clusters = cluster_pois(pois, min_k=2, max_k=3)
    assert 2 <= len(clusters) <= 3
    assert sum(len(bucket) for bucket in clusters.values()) == len(pois)
