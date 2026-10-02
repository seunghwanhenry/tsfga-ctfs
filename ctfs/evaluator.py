"""Regressors, fitness evaluation (with memoisation) and final per-combo evaluation."""
from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

from . import metrics as M

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def make_regressor(name: str, seed: int = 0, fast: bool = False, n_jobs: int = 1, n_estimators=None):
    """Factory for the five regressors in the manuscript (Table II)."""
    name = name.lower()
    if name == "rf":
        return RandomForestRegressor(n_estimators=n_estimators or (30 if fast else 200), min_samples_leaf=2,
                                     max_features=1.0, random_state=seed, n_jobs=n_jobs)
    if name == "dt":
        return DecisionTreeRegressor(min_samples_leaf=5, random_state=seed)
    if name == "lgbm":
        import lightgbm as lgb
        return lgb.LGBMRegressor(n_estimators=100 if fast else 400, learning_rate=0.05,
                                 num_leaves=15, min_child_samples=10, subsample=0.8,
                                 colsample_bytree=0.8, random_state=seed, verbose=-1, n_jobs=n_jobs)
    if name == "mlp":
        return make_pipeline(StandardScaler(),
                             MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=300 if fast else 800,
                                          early_stopping=True, random_state=seed))
    if name == "svr":
        return make_pipeline(StandardScaler(), SVR(C=10.0, epsilon=0.1, gamma="scale"))
    raise ValueError(name)


class FitnessEvaluator:
    """Scores a feature mask by validation MRA. Memoised by mask.

    unit='pooled' : one model per process on the pooled train rows. Optional `ctx_tr/ctx_va`
                    (e.g. one-hot of product-operation combo) are ALWAYS appended as context
                    columns so that MRA differences reflect the candidate features and not
                    the between-combo CT level (which no candidate feature encodes).
    unit='combo'  : one model per (product, operation) combo, MRA averaged over combos
                    (identical to the final evaluation protocol; ~n_combos x slower).
    """

    def __init__(self, X_tr, y_tr, X_va, y_va, regressor="rf", seed=0, fast=True,
                 subsample: int | None = None, n_jobs: int = 1, n_estimators: int | None = None,
                 ctx_tr=None, ctx_va=None, groups_tr=None, groups_va=None, unit="pooled"):
        rng = np.random.default_rng(seed)
        X_tr, y_tr, X_va, y_va = map(np.asarray, (X_tr, y_tr, X_va, y_va))
        if subsample and len(X_tr) > subsample:
            idx = rng.choice(len(X_tr), subsample, replace=False)
            X_tr, y_tr = X_tr[idx], y_tr[idx]
            ctx_tr = None if ctx_tr is None else np.asarray(ctx_tr)[idx]
            groups_tr = None if groups_tr is None else np.asarray(groups_tr)[idx]
        self.X_tr, self.y_tr, self.X_va, self.y_va = X_tr, y_tr, X_va, y_va
        self.ctx_tr = None if ctx_tr is None else np.asarray(ctx_tr, float)
        self.ctx_va = None if ctx_va is None else np.asarray(ctx_va, float)
        self.unit = unit
        if unit == "combo":
            assert groups_tr is not None and groups_va is not None
            g_tr, g_va = np.asarray(groups_tr), np.asarray(groups_va)
            self.groups = [(np.flatnonzero(g_tr == g), np.flatnonzero(g_va == g))
                           for g in np.unique(g_va) if (g_tr == g).sum() >= 20 and (g_va == g).sum() >= 5]
        self.regressor, self.seed, self.fast, self.n_jobs = regressor, seed, fast, n_jobs
        self.n_estimators = n_estimators
        self.cache: dict[bytes, float] = {}
        self.n_evals = 0          # actual model fits (per mask)
        self.n_calls = 0          # including cache hits

    def _design(self, X, ctx, mask, rows=None):
        Xm = X[:, mask] if rows is None else X[rows][:, mask]
        if ctx is not None and self.unit == "pooled":
            Xm = np.hstack([Xm, ctx if rows is None else ctx[rows]])
        return Xm

    def _fit_predict(self, mask, rows_tr=None, rows_va=None):
        model = make_regressor(self.regressor, self.seed, self.fast, self.n_jobs, self.n_estimators)
        model.fit(self._design(self.X_tr, self.ctx_tr, mask, rows_tr),
                  self.y_tr if rows_tr is None else self.y_tr[rows_tr])
        return model.predict(self._design(self.X_va, self.ctx_va, mask, rows_va))

    def mra(self, mask) -> float:
        mask = np.asarray(mask, bool)
        self.n_calls += 1
        if mask.sum() == 0:
            return 0.0
        key = mask.tobytes()
        if key in self.cache:
            return self.cache[key]
        if self.unit == "combo":
            num = den = 0.0
            for rtr, rva in self.groups:
                pred = self._fit_predict(mask, rtr, rva)
                yv = self.y_va[rva]
                num += np.abs(yv - pred).sum()
                den += yv.sum()
            v = float(1.0 - num / max(den, 1e-12))
        else:
            v = M.mra(self.y_va, self._fit_predict(mask))
        self.cache[key] = v
        self.n_evals += 1
        return v


class WeightedFitness:
    """Manuscript Eq. 3: F = PRF + lambda * MRA (PRF relative to the ORIGINAL feature count)."""

    def __init__(self, evaluator: FitnessEvaluator, lam: float, n_total: int, n_search: int | None = None):
        self.ev, self.lam, self.n_total = evaluator, lam, n_total
        self.n_search = n_search or n_total
        self.history = []

    def __call__(self, mask) -> float:
        mask = np.asarray(mask, bool)
        k = int(mask.sum())
        if k == 0:
            return -1.0
        prf = 1.0 - k / self.n_total
        m = self.ev.mra(mask)
        return prf + self.lam * m

    def components(self, mask):
        mask = np.asarray(mask, bool)
        k = int(mask.sum())
        return dict(n_selected=k, PRF=1.0 - k / self.n_total, MRA=self.ev.mra(mask))


def evaluate_features(dproc: pd.DataFrame, features, regressor="rf", seed=0, fast=False,
                      unit="combo", n_jobs=1) -> pd.DataFrame:
    """Final evaluation of a feature subset on the TEST split.

    unit='combo'  : one model per (product, operation) combo (manuscript protocol);
                    returns one row per combo.
    unit='pooled' : one model for the whole process.
    """
    features = list(features)
    rows = []
    if len(features) == 0:
        return pd.DataFrame(rows)
    if unit == "pooled":
        tr, te = dproc[dproc.split == "train"], dproc[dproc.split == "test"]
        model = make_regressor(regressor, seed, fast, n_jobs)
        model.fit(tr[features].to_numpy(float), tr["ct"].to_numpy(float))
        pred = model.predict(te[features].to_numpy(float))
        rows.append(dict(product="ALL", operation="ALL", n_test=len(te),
                         **M.all_metrics(te["ct"].to_numpy(float), pred)))
        return pd.DataFrame(rows)
    for (prod, op), g in dproc.groupby(["product", "operation"]):
        tr, te = g[g.split == "train"], g[g.split == "test"]
        if len(tr) < 20 or len(te) < 5:
            continue
        model = make_regressor(regressor, seed, fast, n_jobs)
        model.fit(tr[features].to_numpy(float), tr["ct"].to_numpy(float))
        pred = model.predict(te[features].to_numpy(float))
        rows.append(dict(product=prod, operation=op, n_test=len(te),
                         **M.all_metrics(te["ct"].to_numpy(float), pred)))
    return pd.DataFrame(rows)


class Timer:
    def __enter__(self):
        self.t = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.elapsed = time.perf_counter() - self.t
