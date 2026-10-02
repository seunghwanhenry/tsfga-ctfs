"""Wrapper / embedded baselines.

* dda_stepwise   : DDA-style (Wang et al. 2018) - correlation-ranked forward stepwise search
* pfi_sbs        : PFI-SBS (Schelthoff et al. 2022) - permutation importance + sequential backward
* rfe_ranking    : recursive feature elimination with RF importances
* lasso_select   : LassoCV with standardised inputs (non-zero coefficients)
* boruta_select  : lightweight Boruta (shadow features + binomial test) with RF
"""
from __future__ import annotations

import numpy as np
from scipy.stats import binomtest, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

from .evaluator import FitnessEvaluator


def _mask_of(names, feature_names):
    idx = {f: i for i, f in enumerate(feature_names)}
    m = np.zeros(len(feature_names), bool)
    m[[idx[f] for f in names]] = True
    return m


def dda_stepwise(X, y, feature_names, evaluator: FitnessEvaluator, max_k=None, tol=1e-4):
    """DDA-style: rank features by |Spearman rho| with the target (adaptive correlation
    surrogate), then forward stepwise selection that adds the next-ranked feature only if
    validation MRA improves by more than `tol`; stops when no candidate improves.

    Returns (selected, curve) where curve = [(k, MRA)] over the ranked prefix (for Fig. 5).
    """
    X = np.asarray(X, float)
    p = X.shape[1]
    rho = np.array([abs(spearmanr(X[:, j], y).correlation) for j in range(p)])
    rho = np.nan_to_num(rho)
    ranking = [feature_names[i] for i in np.argsort(-rho)]
    max_k = max_k or p
    selected, best = [], -np.inf
    curve = []
    for k, f in enumerate(ranking[:max_k], start=1):
        cand = selected + [f]
        v = evaluator.mra(_mask_of(cand, feature_names))
        curve.append((k, v))
        if v > best + tol:
            selected, best = cand, v
    return selected, ranking, curve


def pfi_sbs(X_tr, y_tr, feature_names, evaluator: FitnessEvaluator, seed=0, n_repeats=5,
            k_min=1, fast=True):
    """PFI-SBS: compute permutation feature importance once on the full model, then remove
    features one at a time from least important upwards, tracking validation MRA.
    Returns (best_subset, ranking_desc, curve[(k, MRA)]).
    """
    X_tr = np.asarray(X_tr, float)
    rf = RandomForestRegressor(n_estimators=60 if fast else 200, random_state=seed, n_jobs=1)
    rf.fit(X_tr, y_tr)
    pfi = permutation_importance(rf, evaluator.X_va, evaluator.y_va, n_repeats=n_repeats,
                                 random_state=seed, n_jobs=1).importances_mean
    order_desc = [feature_names[i] for i in np.argsort(-pfi)]     # most important first
    current = list(order_desc)
    curve, best_v, best_set = [], -np.inf, list(current)
    while len(current) >= k_min:
        v = evaluator.mra(_mask_of(current, feature_names))
        curve.append((len(current), v))
        if v > best_v:
            best_v, best_set = v, list(current)
        if len(current) == k_min:
            break
        current = current[:-1]                                    # drop least important
    curve.sort()
    return best_set, order_desc, curve


def rfe_ranking(X_tr, y_tr, feature_names, seed=0, step=1, fast=True):
    """RFE with RF impurity importance -> full ranking (best first)."""
    X_tr = np.asarray(X_tr, float)
    remaining = list(range(X_tr.shape[1]))
    eliminated = []
    while len(remaining) > 1:
        rf = RandomForestRegressor(n_estimators=40 if fast else 150, random_state=seed, n_jobs=1)
        rf.fit(X_tr[:, remaining], y_tr)
        imp = rf.feature_importances_
        n_drop = max(1, min(step, len(remaining) - 1))
        drop = [remaining[i] for i in np.argsort(imp)[:n_drop]]
        for d in drop:
            remaining.remove(d)
            eliminated.append(d)
    ranking_idx = remaining + eliminated[::-1]
    return [feature_names[i] for i in ranking_idx]


def lasso_select(X_tr, y_tr, feature_names, seed=0):
    Xs = StandardScaler().fit_transform(np.asarray(X_tr, float))
    m = LassoCV(cv=5, random_state=seed, n_alphas=50, max_iter=5000).fit(Xs, y_tr)
    sel = [f for f, c in zip(feature_names, m.coef_) if abs(c) > 1e-8]
    if not sel:                                              # degenerate -> keep the largest coef
        sel = [feature_names[int(np.argmax(np.abs(m.coef_)))]]
    return sel, m.alpha_


def boruta_select(X_tr, y_tr, feature_names, seed=0, n_iter=30, alpha=0.05, fast=True, perc=100):
    """Lightweight Boruta (Kursa & Rudnicki 2010) for regression with RF.

    Each iteration: append shuffled 'shadow' copies, fit RF, count a feature as a hit if its
    importance exceeds the `perc`-th percentile of shadow importances. After n_iter, a
    two-sided binomial test at level alpha confirms / rejects; undecided features are dropped.
    """
    rng = np.random.default_rng(seed)
    X_tr = np.asarray(X_tr, float)
    p = X_tr.shape[1]
    hits = np.zeros(p, int)
    active = np.ones(p, bool)
    decided = np.zeros(p, int)               # 1 confirmed, -1 rejected
    for it in range(n_iter):
        idx = np.flatnonzero(active)
        if len(idx) == 0:
            break
        Xa = X_tr[:, idx]
        shadow = Xa.copy()
        for j in range(shadow.shape[1]):
            shadow[:, j] = rng.permutation(shadow[:, j])
        rf = RandomForestRegressor(n_estimators=60 if fast else 200, max_features="sqrt",
                                   random_state=seed + it, n_jobs=1)
        rf.fit(np.hstack([Xa, shadow]), y_tr)
        imp = rf.feature_importances_
        real, sh = imp[:len(idx)], imp[len(idx):]
        thr = np.percentile(sh, perc)
        hits[idx] += (real > thr)
        # binomial decisions after a few iterations
        if it >= 4:
            for j in idx:
                pv_hi = binomtest(int(hits[j]), it + 1, 0.5, alternative="greater").pvalue
                pv_lo = binomtest(int(hits[j]), it + 1, 0.5, alternative="less").pvalue
                if pv_hi < alpha:
                    decided[j], active[j] = 1, False
                elif pv_lo < alpha:
                    decided[j], active[j] = -1, False
    confirmed = [feature_names[j] for j in range(p) if decided[j] == 1]
    tentative = [feature_names[j] for j in range(p) if decided[j] == 0]
    if not confirmed:                                      # keep tentative ones with most hits
        order = np.argsort(-hits)
        confirmed = [feature_names[j] for j in order[: max(1, p // 4)]]
    return confirmed, tentative
