"""Statistical comparison of methods over product-operation combinations.

* wilcoxon_vs_reference : paired Wilcoxon signed-rank (reference vs each other method)
* friedman_nemenyi      : Friedman test + Nemenyi post-hoc (average ranks, critical distance)
* plot_cd_diagram       : Demsar (2006) critical-difference diagram
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _pivot(df, value="MRA"):
    """df rows: process, product, operation, method, <value> -> wide (block x method)."""
    key = ["process", "product", "operation"]
    return df.pivot_table(index=key, columns="method", values=value, aggfunc="mean").dropna()


def wilcoxon_vs_reference(df, reference="TSFGA", value="MRA", higher_better=True, alpha=0.05):
    W = _pivot(df, value)
    rows = []
    for m in W.columns:
        if m == reference:
            continue
        a, b = W[reference].to_numpy(), W[m].to_numpy()
        d = a - b
        if np.allclose(d, 0):
            p, stat = 1.0, 0.0
        else:
            stat, p = stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
        wins = int((d > 0).sum()) if higher_better else int((d < 0).sum())
        losses = int((d < 0).sum()) if higher_better else int((d > 0).sum())
        rows.append(dict(reference=reference, method=m, n=len(d), mean_diff=float(d.mean()),
                         median_diff=float(np.median(d)), W=float(stat), p_value=float(p),
                         wins=wins, ties=int((d == 0).sum()), losses=losses,
                         significant=bool(p < alpha),
                         better=("reference" if (d.mean() > 0) == higher_better else m)))
    return pd.DataFrame(rows)


def friedman_nemenyi(df, value="MRA", higher_better=True, alpha=0.05):
    W = _pivot(df, value)
    k, N = W.shape[1], W.shape[0]
    ranks = W.rank(axis=1, ascending=not higher_better)          # 1 = best
    avg_rank = ranks.mean().sort_values()
    if k < 3:
        return dict(avg_rank=avg_rank, p_value=np.nan, statistic=np.nan, CD=np.nan, k=k, N=N)
    stat, p = stats.friedmanchisquare(*[W[c].to_numpy() for c in W.columns])
    q_alpha = stats.studentized_range.ppf(1 - alpha, k, np.inf) / np.sqrt(2)
    CD = q_alpha * np.sqrt(k * (k + 1) / (6.0 * N))
    # Iman-Davenport correction
    chi2 = stat
    ff = (N - 1) * chi2 / (N * (k - 1) - chi2) if N * (k - 1) - chi2 > 0 else np.inf
    p_ff = 1 - stats.f.cdf(ff, k - 1, (k - 1) * (N - 1)) if np.isfinite(ff) else 0.0
    pair = []
    names = list(avg_rank.index)
    for i in range(k):
        for j in range(i + 1, k):
            diff = abs(avg_rank[names[i]] - avg_rank[names[j]])
            pair.append(dict(a=names[i], b=names[j], rank_diff=diff, significant=bool(diff > CD)))
    return dict(avg_rank=avg_rank, statistic=float(stat), p_value=float(p),
                iman_davenport_F=float(ff), p_value_ID=float(p_ff), CD=float(CD), k=k, N=N,
                pairwise=pd.DataFrame(pair))


def plot_cd_diagram(avg_rank: pd.Series, CD: float, title="", path=None, ax=None):
    """Critical-difference diagram (Demsar 2006). Lower rank = better."""
    import matplotlib.pyplot as plt

    avg_rank = avg_rank.sort_values()
    names, r = list(avg_rank.index), avg_rank.to_numpy()
    k = len(names)
    lo, hi = np.floor(r.min()), np.ceil(r.max())
    lo, hi = max(1, lo), max(hi, lo + 1)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(7, 1.2 + 0.35 * k))
    ax.plot([lo, hi], [0, 0], color="k", lw=1)
    for t in np.arange(lo, hi + 0.001, 1):
        ax.plot([t, t], [0, 0.15], color="k", lw=1)
        ax.text(t, 0.25, f"{int(t)}", ha="center", va="bottom", fontsize=9)
    # CD bar
    ax.plot([lo, lo + CD], [0.75, 0.75], color="k", lw=2)
    ax.text(lo + CD / 2, 0.85, f"CD = {CD:.2f}", ha="center", fontsize=9)
    # method stems: half left (better), half right
    half = int(np.ceil(k / 2))
    for i, (n, ri) in enumerate(zip(names, r)):
        if i < half:
            y = -0.6 - 0.45 * i
            ax.plot([ri, ri], [0, y], color="k", lw=0.8)
            ax.plot([lo - 0.1, ri], [y, y], color="k", lw=0.8)
            ax.text(lo - 0.15, y, f"{n} ({ri:.2f})", ha="right", va="center", fontsize=9)
        else:
            y = -0.6 - 0.45 * (k - 1 - i)
            ax.plot([ri, ri], [0, y], color="k", lw=0.8)
            ax.plot([ri, hi + 0.1], [y, y], color="k", lw=0.8)
            ax.text(hi + 0.15, y, f"{n} ({ri:.2f})", ha="left", va="center", fontsize=9)
    # cliques: groups not significantly different
    cliques = []
    for i in range(k):
        j = i
        while j + 1 < k and r[j + 1] - r[i] <= CD:
            j += 1
        if j > i and not any(i >= a and j <= b for a, b in cliques):
            cliques.append((i, j))
    for c, (a, b) in enumerate(cliques):
        y = -0.25 - 0.12 * c
        ax.plot([r[a] - 0.05, r[b] + 0.05], [y, y], color="k", lw=3, solid_capstyle="round")
    ax.set_xlim(lo - 2.2, hi + 2.2)
    ax.set_ylim(-0.6 - 0.45 * half - 0.3, 1.2)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    if own and path:
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
    return ax
