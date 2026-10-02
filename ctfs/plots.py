"""Figure helpers (matplotlib/seaborn, publication style)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=0.9)
PALETTE = "tab10"


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def violin_before_after(per_combo: pd.DataFrame, path, before="ALL", after="TSFGA", value="MRA"):
    """Manuscript Fig. 4: per-process violin of per-combo MRA before/after selection."""
    d = per_combo[per_combo.method.isin([before, after])].copy()
    d["stage"] = np.where(d.method == before, f"Before ({before})", f"After ({after})")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    sns.violinplot(data=d, x="process", y=value, hue="stage", split=True, inner="quart",
                   palette={f"Before ({before})": "#8fd18f", f"After ({after})": "#f08080"}, ax=ax, cut=0)
    ax.set_xlabel("")
    ax.set_ylabel(value)
    ax.legend(loc="lower right", frameon=True)
    _save(fig, path)


def convergence(seed_runs: pd.DataFrame, path, methods=None, by="process"):
    """Best-fitness vs generation, mean +/- std across seeds. seed_runs rows: process, method, seed, gen, best."""
    methods = methods or sorted(seed_runs.method.unique())
    procs = sorted(seed_runs[by].unique())
    n = len(procs)
    cols = min(3, n)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.0 * rows), squeeze=False)
    for ax, p in zip(axes.flat, procs):
        for m in methods:
            d = seed_runs[(seed_runs[by] == p) & (seed_runs.method == m)]
            if d.empty:
                continue
            g = d.groupby("gen")["best"].agg(["mean", "std"]).reset_index()
            ax.plot(g.gen, g["mean"], label=m)
            ax.fill_between(g.gen, g["mean"] - g["std"].fillna(0), g["mean"] + g["std"].fillna(0), alpha=0.2)
        ax.set_title(p)
        ax.set_xlabel("generation")
        ax.set_ylabel("best fitness")
    for ax in axes.flat[n:]:
        ax.axis("off")
    axes.flat[0].legend(fontsize=8)
    _save(fig, path)


def sensitivity(df: pd.DataFrame, param, path, metrics=("MRA_mean", "PRF_mean")):
    """One-at-a-time sensitivity: x = parameter value, lines = processes."""
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.2 * len(metrics), 3.2))
    for ax, met in zip(np.atleast_1d(axes), metrics):
        for p, g in df.groupby("process"):
            g = g.sort_values(param)
            ax.plot(g[param].astype(str), g[met], marker="o", label=p)
        ax.set_xlabel(param)
        ax.set_ylabel(met.replace("_mean", ""))
    np.atleast_1d(axes)[0].legend(fontsize=7)
    _save(fig, path)


def mra_vs_size(curves: dict, baseline: float, stars: dict, squares: dict, path, title=""):
    """Manuscript Fig. 5: validation MRA vs subset size per method with star (best) and square
    (min size beating baseline) markers, plus the all-feature baseline line."""
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for m, curve in curves.items():
        c = np.array(curve)
        line, = ax.plot(c[:, 0], c[:, 1], marker=".", ms=3, lw=1, label=m)
        if m in stars and stars[m] is not None:
            ax.plot(*stars[m], marker="*", ms=12, color=line.get_color(), ls="none")
        if m in squares and squares[m] is not None:
            ax.plot(*squares[m], marker="s", ms=7, mfc="none", color=line.get_color(), ls="none")
    ax.axhline(baseline, color="red", ls="--", lw=1, label="all features")
    ax.set_xlabel("feature subset size")
    ax.set_ylabel("validation MRA")
    ax.set_title(title)
    ax.legend(fontsize=7, ncol=2)
    _save(fig, path)


def corr_heatmaps(X_by_method: dict, path, threshold=0.8):
    """Manuscript Fig. 6 (2-D version): |PCC| among selected features per method."""
    n = len(X_by_method)
    fig, axes = plt.subplots(1, n, figsize=(3.6 * n, 3.4))
    for ax, (m, (X, names)) in zip(np.atleast_1d(axes), X_by_method.items()):
        if X.shape[1] < 2:
            ax.set_title(f"{m} (k={X.shape[1]})")
            ax.axis("off")
            continue
        C = np.abs(np.nan_to_num(np.corrcoef(X, rowvar=False)))
        np.fill_diagonal(C, np.nan)
        sns.heatmap(C, vmin=0, vmax=1, cmap="RdYlGn_r", ax=ax, cbar=False, square=True,
                    xticklabels=False, yticklabels=False)
        iu = np.triu_indices_from(C, 1)
        n_hi = int((C[iu] > threshold).sum())
        ax.set_title(f"{m} (k={X.shape[1]}, |r|>{threshold}: {n_hi})", fontsize=9)
    _save(fig, path)


def pareto_front(pareto_objs, picked, tsfga_point, path, title=""):
    P = np.array(pareto_objs, float)
    fig, ax = plt.subplots(figsize=(4.5, 3.4))
    order = np.argsort(P[:, 0])
    ax.plot(P[order, 0], P[order, 1], "o-", ms=4, label="NSGA-II Pareto front")
    ax.plot(picked[0], picked[1], "D", ms=9, mfc="none", mec="k", label="NSGA-II pick")
    if tsfga_point is not None:
        ax.plot(tsfga_point[0], tsfga_point[1], "*", ms=13, color="red", label="TSFGA")
    ax.set_xlabel("# features")
    ax.set_ylabel("validation MRA")
    ax.set_title(title)
    ax.legend(fontsize=8)
    _save(fig, path)


def selection_frequency(freq: pd.DataFrame, path, category=None, top=None):
    """Heatmap feature x process of selection frequency across seeds."""
    d = freq.copy()
    if top:
        d = d.loc[d.mean(axis=1).sort_values(ascending=False).index[:top]]
    if category is not None:
        d = d.loc[sorted(d.index, key=lambda f: (category.get(f, "z"), f))]
    fig, ax = plt.subplots(figsize=(1.1 * d.shape[1] + 3, 0.22 * d.shape[0] + 1.5))
    sns.heatmap(d, vmin=0, vmax=1, cmap="Blues", ax=ax, cbar_kws=dict(label="selection frequency"),
                yticklabels=True)
    ax.set_xlabel("")
    _save(fig, path)


def bar_importance(imp: pd.Series, path, title="", top=20):
    imp = imp.sort_values(ascending=True).tail(top)
    fig, ax = plt.subplots(figsize=(5, 0.28 * len(imp) + 1))
    ax.barh(imp.index, imp.values, color="#4c72b0")
    ax.set_title(title)
    ax.set_xlabel("mean |SHAP| (or permutation importance)")
    _save(fig, path)


def grouped_bars(df: pd.DataFrame, x, y, hue, path, ylabel=None, title="", err=None):
    n_x = df[x].nunique()
    fig, ax = plt.subplots(figsize=(max(8, 0.75 * n_x + 2), 3.8))
    sns.barplot(data=df, x=x, y=y, hue=hue, ax=ax, errorbar=None)
    if n_x > 8:
        ax.tick_params(axis="x", labelsize=7, rotation=45)
    ax.set_ylabel(ylabel or y)
    ax.set_xlabel("")
    ax.set_title(title)
    ax.legend(fontsize=7, ncol=3)
    lo = df[y].min()
    ax.set_ylim(max(0, lo - 0.05), min(1.0, df[y].max() + 0.02))
    _save(fig, path)
