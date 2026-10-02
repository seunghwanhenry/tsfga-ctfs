"""Filter-based feature selection: PCC+MI redundancy filter (TSFGA phase 1), MI, mRMR."""
from __future__ import annotations

import numpy as np
from sklearn.feature_selection import mutual_info_regression


def mi_with_target(X, y, seed=0, n_neighbors=5) -> np.ndarray:
    return mutual_info_regression(X, y, random_state=seed, n_neighbors=n_neighbors)


def abs_corr_matrix(X) -> np.ndarray:
    C = np.corrcoef(np.asarray(X, float), rowvar=False)
    return np.abs(np.nan_to_num(C))


def pcc_mi_filter(X, y, feature_names, threshold: float = 0.8, seed: int = 0):
    """Phase 1 of TSFGA (manuscript Section II.A, Steps 1-5).

    1. PCC matrix for all pairs
    2. pairs with |r| > threshold
    3. MI of each member with the target
    4. drop the member with the lower MI (pairs processed from highest |r| downwards;
       a pair is skipped if one member was already dropped)
    5. remaining features = filtered subset

    Returns (kept_names, removed_names, log) where log lists (kept, dropped, |r|).
    """
    X = np.asarray(X, float)
    names = list(feature_names)
    p = X.shape[1]
    C = abs_corr_matrix(X)
    mi = mi_with_target(X, y, seed)
    iu = np.triu_indices(p, k=1)
    pairs = [(C[i, j], i, j) for i, j in zip(*iu) if C[i, j] > threshold]
    pairs.sort(reverse=True)
    removed = set()
    log = []
    for r, i, j in pairs:
        if i in removed or j in removed:
            continue
        drop, keep = (i, j) if mi[i] < mi[j] else (j, i)
        removed.add(drop)
        log.append((names[keep], names[drop], float(r)))
    kept = [names[i] for i in range(p) if i not in removed]
    return kept, [names[i] for i in sorted(removed)], log


def mi_ranking(X, y, feature_names, seed=0):
    mi = mi_with_target(X, y, seed)
    order = np.argsort(-mi)
    return [feature_names[i] for i in order], mi[order]


def mrmr_ranking(X, y, feature_names, max_k=None, seed=0, scheme="MIQ"):
    """Greedy mRMR: relevance = MI(f; y), redundancy = mean |PCC(f, selected)|.

    scheme='MID' (difference) or 'MIQ' (quotient). Returns ordered feature list.
    """
    X = np.asarray(X, float)
    p = X.shape[1]
    max_k = max_k or p
    rel = mi_with_target(X, y, seed)
    C = abs_corr_matrix(X)
    selected = [int(np.argmax(rel))]
    remaining = [i for i in range(p) if i not in selected]
    while remaining and len(selected) < max_k:
        red = C[np.ix_(remaining, selected)].mean(axis=1)
        if scheme == "MID":
            score = rel[remaining] - red
        else:
            score = rel[remaining] / (red + 1e-6)
        nxt = remaining[int(np.argmax(score))]
        selected.append(nxt)
        remaining.remove(nxt)
    return [feature_names[i] for i in selected]


def best_k_by_validation(ranking, feature_names, evaluator, k_min=1, k_max=None, baseline_mra=None):
    """For a ranked list, evaluate top-k subsets on validation and return
    (best_subset, best_k, curve, min_k_beating_baseline).

    curve: list of (k, MRA). This reproduces the star/square logic of Fig. 5.
    """
    idx = {f: i for i, f in enumerate(feature_names)}
    k_max = k_max or len(ranking)
    curve = []
    best_k, best_v = None, -np.inf
    min_k_beat = None
    for k in range(k_min, min(k_max, len(ranking)) + 1):
        mask = np.zeros(len(feature_names), bool)
        mask[[idx[f] for f in ranking[:k]]] = True
        v = evaluator.mra(mask)
        curve.append((k, v))
        if v > best_v:
            best_v, best_k = v, k
        if baseline_mra is not None and min_k_beat is None and v > baseline_mra:
            min_k_beat = k
    return list(ranking[:best_k]), best_k, curve, min_k_beat
