"""Statistics for REAL-data results produced outside this framework (e.g., the real-fab runs).

Input CSV: one row per (process, product, operation, method, seed) with at least an MRA column:

    process,product,operation,method,seed,MRA[,MAE,RMSE,MAPE,R2]
    lithography,P01,LITH-03,ALL,0,0.912
    lithography,P01,LITH-03,TSFGA,0,0.937
    ...

`method` must contain "TSFGA" (reference) and ideally "ALL"; other selectors are optional.
Seeds are averaged per (process, product, operation) before testing.

python tools/real_data_stats.py real_per_combo.csv results/real_stats

Outputs: table_mean_sd_<metric>.md (Table 3/4 format), wilcoxon_vs_TSFGA_<metric>.csv,
         friedman_<metric>.json, fig_cd_diagram_<metric>.png
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ctfs import stats as ST  # noqa: E402

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "results/real_stats"
os.makedirs(out, exist_ok=True)
df = pd.read_csv(src)
missing = {"process", "product", "operation", "method", "MRA"} - set(df.columns)
if missing:
    raise SystemExit(f"missing columns: {missing}")
if "seed" not in df.columns:
    df["seed"] = 0
metrics = [m for m in ("MRA", "MAE", "RMSE", "MAPE", "R2") if m in df.columns]
higher = {"MRA": True, "R2": True, "MAE": False, "RMSE": False, "MAPE": False}

for metric in metrics:
    unit = df.groupby(["process", "product", "operation", "method"])[metric].mean().reset_index()
    g = unit.groupby(["process", "method"])[metric]
    tab = pd.concat([g.mean().rename("mean"), g.std().rename("sd")], axis=1).reset_index()
    W = tab.pivot(index="process", columns="method", values="mean")
    S = tab.pivot(index="process", columns="method", values="sd")
    lines = ["| process | " + " | ".join(W.columns) + " |", "|---|" + "---|" * len(W.columns)]
    for p in W.index:
        rk = W.loc[p].rank(ascending=not higher[metric])
        lines.append(f"| {p} | " + " | ".join(f"{W.loc[p, m]:.4f} ± {S.loc[p, m]:.3f} ({int(rk[m])})" for m in W.columns) + " |")
    lines.append("| Average | " + " | ".join(f"{W[m].mean():.4f}" for m in W.columns) + " |")
    open(os.path.join(out, f"table_mean_sd_{metric}.md"), "w").write("\n".join(lines) + "\n")

    rows = []
    w = ST.wilcoxon_vs_reference(unit, "TSFGA", metric, higher[metric]); w["process"] = "ALL_PROCESSES"; rows.append(w)
    for p in unit.process.unique():
        wp = ST.wilcoxon_vs_reference(unit[unit.process == p], "TSFGA", metric, higher[metric]); wp["process"] = p; rows.append(wp)
    pd.concat(rows).assign(metric=metric).to_csv(os.path.join(out, f"wilcoxon_vs_TSFGA_{metric}.csv"), index=False)

    if unit.method.nunique() >= 3:
        fr = ST.friedman_nemenyi(unit, metric, higher[metric])
        json.dump({k: (v.to_dict() if hasattr(v, "to_dict") else v) for k, v in fr.items()},
                  open(os.path.join(out, f"friedman_{metric}.json"), "w"), indent=1, default=float)
        ST.plot_cd_diagram(fr["avg_rank"], fr["CD"], title=f"Nemenyi CD diagram ({metric}), N={fr['N']} units",
                           path=os.path.join(out, f"fig_cd_diagram_{metric}.png"))
        print(f"[{metric}] Friedman chi2={fr['statistic']:.2f} p={fr['p_value']:.2e} CD={fr['CD']:.3f}; "
              f"avg ranks: {fr['avg_rank'].round(2).to_dict()}")
print("written to", out)
