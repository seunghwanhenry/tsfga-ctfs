"""Evaluation metrics used throughout the experiments."""
from __future__ import annotations

import numpy as np
import pandas as pd


def mra(y_true, y_pred) -> float:
    """Mean relative accuracy (manuscript Eq. 5): 1 - sum|y - yhat| / sum(y)."""
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    return float(1.0 - np.abs(y_true - y_pred).sum() / max(y_true.sum(), 1e-12))


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def mape(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    denom = np.maximum(np.abs(y_true), 1e-9)
    return float(np.mean(np.abs(y_true - y_pred) / denom) * 100.0)


def r2(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, float)
    y_pred = np.asarray(y_pred, float)
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    return float(1 - ss_res / max(ss_tot, 1e-12))


def all_metrics(y_true, y_pred) -> dict:
    return dict(MRA=mra(y_true, y_pred), MAE=mae(y_true, y_pred), RMSE=rmse(y_true, y_pred),
                MAPE=mape(y_true, y_pred), R2=r2(y_true, y_pred))


def prf(n_selected: int, n_total: int) -> float:
    """Percentage of feature reduction (manuscript Eq. 4)."""
    return float(1.0 - n_selected / n_total)


def cfs_merit(X: np.ndarray, y: np.ndarray) -> float:
    """CFS merit (manuscript Eq. 6): k*rho_sy / sqrt(k + k(k-1)*rho_ss).

    rho_sy = mean |PCC(feature, target)|, rho_ss = mean |PCC(feature_i, feature_j)| (i != j).
    """
    X = np.asarray(X, float)
    k = X.shape[1]
    if k == 0:
        return 0.0
    Xs = X.std(axis=0)
    keep = Xs > 0
    if keep.sum() == 0:
        return 0.0
    X = X[:, keep]
    k = X.shape[1]
    r_sy = np.abs([np.corrcoef(X[:, j], y)[0, 1] for j in range(k)])
    r_sy = np.nan_to_num(r_sy).mean()
    if k == 1:
        return float(r_sy)
    C = np.abs(np.corrcoef(X, rowvar=False))
    C = np.nan_to_num(C)
    r_ss = (C.sum() - np.trace(C)) / (k * (k - 1))
    return float(k * r_sy / np.sqrt(k + k * (k - 1) * r_ss))


def n_high_corr_pairs(X: np.ndarray, threshold: float = 0.8) -> int:
    X = np.asarray(X, float)
    if X.shape[1] < 2:
        return 0
    C = np.abs(np.nan_to_num(np.corrcoef(X, rowvar=False)))
    iu = np.triu_indices_from(C, k=1)
    return int((C[iu] > threshold).sum())


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean_pairwise_jaccard(sets) -> float:
    sets = list(sets)
    if len(sets) < 2:
        return 1.0
    vals = [jaccard(sets[i], sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets))]
    return float(np.mean(vals))


def recovery(selected, true_features, equivalence=None) -> dict:
    """Precision / recall / F1 of recovering the ground-truth feature set (synthetic only).

    `equivalence` maps redundant proxies to their group's true driver, so selecting
    util_min instead of util_avg still counts as a hit (but selecting both counts once).
    """
    eq = equivalence or {}
    s = {eq.get(f, f) for f in selected}
    t = {eq.get(f, f) for f in true_features}
    tp = len(s & t)
    p = tp / len(s) if s else 0.0
    r = tp / len(t) if t else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return dict(precision=p, recall=r, f1=f1)


def summarize(df: pd.DataFrame, by, cols=("MRA", "MAE", "RMSE", "MAPE", "R2")) -> pd.DataFrame:
    g = df.groupby(list(by))[list(cols)]
    out = g.agg(["mean", "std"])
    out.columns = [f"{a}_{b}" for a, b in out.columns]
    return out.reset_index()
