"""Collect the numbers needed by tools/build_manuscript.js into manuscript_data.json.

python tools/build_manuscript_data.py results/quick manuscript_data.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

res = sys.argv[1] if len(sys.argv) > 1 else "results/quick"
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(res, "manuscript_data.json")

P = lambda *a: os.path.join(res, *a)
have = lambda *a: os.path.exists(P(*a))
f4 = lambda v: f"{v:.4f}"
f3 = lambda v: f"{v:.3f}"
pct = lambda v: f"{100 * v:.1f}%"

D = {}
cfg = json.load(open(P("config.json")))
D["config"] = dict(pop=cfg["ga"]["pop_size"], gen=cfg["ga"]["n_gen"], pc=cfg["ga"]["pc"], pm=cfg["ga"]["pm"],
                   lam=cfg["lambda"], thr=cfg["pcc_threshold"], seeds=len(cfg["seeds"]),
                   fitness_trees=cfg.get("fitness_n_estimators"), eval_trees=30 if cfg["eval_fast"] else 200,
                   fitness_unit=cfg.get("fitness_unit"))

s = pd.read_csv(P("main", "summary_by_seed.csv"))
procs = sorted(s.process.unique())
D["processes"] = procs
D["n_combos"] = int(pd.read_csv(P("main", "per_combo.csv")).groupby(["process", "product", "operation"]).ngroups)
meta = json.load(open(P("main", "meta.json")))
D["n_features"] = len(meta["feature_names"])
def _load_data(tag, which):
    """Read the cached data; if the parquet was not shipped, regenerate the synthetic fab from the config."""
    pq = P(tag, "data_with_splits.parquet")
    if os.path.exists(pq):
        return pd.read_parquet(pq)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from ctfs import experiments as E
    dfx, _ = E.load_dataset(cfg, which=which)
    return dfx
d = _load_data("main", "main")
D["data"] = dict(n_rows=int(len(d)), rows_per_process=int(len(d) / len(procs)),
                 ct_mean=float(d.ct.mean()), ct_median=float(d.ct.median()), ct_max=float(d.ct.max()),
                 n_products=int(d["product"].nunique()), n_ops_per_process=int(d.groupby("process").operation.nunique().iloc[0]),
                 start=str(d.timestamp.min().date()), end=str(d.timestamp.max().date()))
D["true_features"] = meta["true_features"]
D["redundant_groups"] = meta["redundant_groups"]
D["feature_category"] = meta["feature_category"]

# --- ablation (E1): rows per process, cols ALL/FILTER/GA/TSFGA, MRA mean±sd and PRF
g = s.groupby(["process", "method"])
def cell(p, m, col, fmt=f4, sd=True):
    v = g[col].mean().loc[(p, m)]
    sdv = g[col].std().loc[(p, m)]
    return f"{fmt(v)} ± {sdv:.3f}" if sd else fmt(v)
abl = []
for p in procs:
    abl.append([p.capitalize()] + [cell(p, m, "MRA") for m in ["ALL", "FILTER", "GA", "TSFGA"]]
               + [pct(g["PRF"].mean().loc[(p, m)]) for m in ["FILTER", "GA", "TSFGA"]]
               + [f"{g['n_selected'].mean().loc[(p, 'TSFGA')]:.1f}"])
avg = s.groupby("method")
abl.append(["Average"] + [f4(avg["MRA"].mean()[m]) for m in ["ALL", "FILTER", "GA", "TSFGA"]]
           + [pct(avg["PRF"].mean()[m]) for m in ["FILTER", "GA", "TSFGA"]] + [f"{avg['n_selected'].mean()['TSFGA']:.1f}"])
D["ablation"] = abl
fa = json.load(open(P("E3_stats", "friedman_ablation.json")))
ra = pd.read_csv(P("E3_stats", "friedman_avg_rank_ablation.csv")); ra.columns = ["method", "rank"]
D["ablation_stats"] = dict(chi2=fa["statistic"], p=fa["p_value"], CD=fa["CD"], N=fa["N"],
                           ranks={r.method: round(r["rank"], 2) for _, r in ra.iterrows()})

# --- baseline comparison (E6) averaged over processes
st = pd.read_csv(P("main", "E2_stability.csv"))
rk = pd.read_csv(P("E3_stats", "friedman_avg_rank_MRA.csv")); rk.columns = ["method", "avg_rank"]
A = avg[["MRA", "PRF", "CFS", "MAE", "RMSE", "R2", "time_s", "n_selected", "n_high_corr_pairs"]].mean()
A["jaccard"] = st.groupby("method").jaccard_mean.mean()
A["avg_rank"] = rk.set_index("method").avg_rank
A = A.sort_values("avg_rank")
D["baseline_avg"] = [[m, f4(r.MRA), pct(r.PRF), f3(r.CFS), f"{r.MAE:.3f}", f"{r.RMSE:.3f}", f3(r.R2),
                      f"{r.n_selected:.1f}", f"{r.n_high_corr_pairs:.1f}", f3(r.jaccard), f"{r.time_s:.1f}", f"{r.avg_rank:.2f}"]
                     for m, r in A.iterrows()]
# per-process MRA table with ranks
W = s.groupby(["process", "method"])["MRA"].mean().unstack("method")
methods_order = list(A.index)
rows = []
for p in procs:
    r = W.loc[p]; rank = r.rank(ascending=False)
    rows.append([p.capitalize()] + [f"{r[m]:.4f} ({int(rank[m])})" for m in methods_order])
rows.append(["Average"] + [f4(W[m].mean()) for m in methods_order])
D["baseline_per_process"] = dict(methods=methods_order, rows=rows)
fr = json.load(open(P("E3_stats", "friedman_MRA.json")))
D["friedman"] = dict(chi2=fr["statistic"], p=fr["p_value"], CD=fr["CD"], N=fr["N"], k=fr["k"])
Wx = pd.read_csv(P("E3_stats", "wilcoxon_vs_TSFGA.csv"))
Wx = Wx[(Wx.process == "ALL_PROCESSES") & (Wx.metric == "MRA")].set_index("method")
D["wilcoxon"] = [[m, f"{Wx.loc[m, 'mean_diff']:+.4f}", f"{Wx.loc[m, 'p_value']:.4f}" if Wx.loc[m, 'p_value'] >= 1e-4 else "<0.0001",
                  f"{int(Wx.loc[m, 'wins'])}/{int(Wx.loc[m, 'ties'])}/{int(Wx.loc[m, 'losses'])}"]
                 for m in methods_order if m in Wx.index]

# --- sensitivity (E4)
D["interim"] = []
if not have("E4_sensitivity", "sensitivity_by_seed.csv"):
    D["sensitivity"] = None
else:
  S = pd.read_csv(P("E4_sensitivity", "sensitivity_by_seed.csv"))
  D["seeds_sens"] = int(S.seed.nunique())
  sen = []
  for (param, val), gg in S.groupby(["param", "value"]):
    sen.append([param, str(val), f"{gg.MRA.mean():.4f} ± {gg.MRA.std():.3f}", pct(gg.PRF.mean()),
                f"{gg.n_selected.mean():.1f}", f3(gg.CFS.mean())])
  D["sensitivity"] = sen
  D["sens"] = {f"{param}={val}": dict(MRA=float(gg.MRA.mean()), PRF=float(gg.PRF.mean()), k=float(gg.n_selected.mean()),
                                       CFS=float(gg.CFS.mean())) for (param, val), gg in S.groupby(["param", "value"])}

# --- temporal (E7)
if not have("E7_temporal", "temporal_summary_by_seed.csv"):
    D["temporal"] = None; D["temporal_overlap"] = None
else:
  T = pd.read_csv(P("E7_temporal", "temporal_summary_by_seed.csv"))
  D["seeds_temporal"] = int(T.seed.nunique())
  tm = T.groupby(["split_mode", "process", "method"])["MRA"].mean().unstack("method")
  tmeth = [m for m in ["ALL", "FILTER", "mRMR", "MI", "DDA", "PFI-SBS", "NSGA2", "TSFGA"] if m in tm.columns]
  trows = []
  for mode in ["random", "temporal"]:
      for p in procs:
          r = tm.loc[(mode, p)]
          trows.append([mode, p.capitalize()] + [f4(r[m]) for m in tmeth] + [f"{r['TSFGA'] - r['ALL']:+.4f}"])
      r = tm.loc[mode].mean()
      trows.append([mode, "Average"] + [f4(r[m]) for m in tmeth] + [f"{r['TSFGA'] - r['ALL']:+.4f}"])
  D["temporal"] = dict(methods=tmeth, rows=trows)
  ov = pd.read_csv(P("E7_temporal", "E7_selection_overlap.csv"))
  D["temporal_overlap"] = {p: float(v) for p, v in ov.groupby("process").jaccard_random_vs_temporal.mean().items()}
  D["temporal_gain"] = {mode: float((tm.loc[mode]["TSFGA"] - tm.loc[mode]["ALL"]).mean()) for mode in ["random", "temporal"]}
  D["temporal_gain_min"] = {mode: float((tm.loc[mode]["TSFGA"] - tm.loc[mode]["ALL"]).min()) for mode in ["random", "temporal"]}


# --- transfer (E8)
if not have("E8_transfer", "E8_transfer_MRA.csv"):
    D["transfer"] = None
else:
  X = pd.read_csv(P("E8_transfer", "E8_transfer_MRA.csv"))
  XW = pd.read_csv(P("E8_transfer", "E8_wilcoxon.csv"))
  XW = XW[XW.method == "ALL"].set_index("regressor")
  regs = [r for r in ["rf", "lgbm", "mlp", "svr", "dt"] if r in set(X.regressor)]
  xrows = []
  for reg in regs:
      xr = X[X.regressor == reg]
      xrows.append([reg.upper()] + [f4(xr["ALL"].mean()), f4(xr["TSFGA(majority)"].mean()), f"{xr['gain_majority'].mean():+.4f}",
                    f"{XW.loc[reg, 'p_value']:.3f}", f"{int(XW.loc[reg, 'wins'])}/{int(XW.loc[reg, 'losses'])}"])
  D["transfer"] = xrows
  D["transfer_num"] = {reg: dict(gain=float(X[X.regressor == reg]["gain_majority"].mean()), p=float(XW.loc[reg, "p_value"]),
                                 wins=int(XW.loc[reg, "wins"]), losses=int(XW.loc[reg, "losses"])) for reg in regs}


# --- recovery / stability / insight (E10)
R = pd.read_csv(P("main", "E10_recovery.csv")).groupby("method")[["rec_precision", "rec_recall", "rec_f1"]].mean()
D["recovery"] = [[m, f3(r.rec_precision), f3(r.rec_recall), f3(r.rec_f1)] for m, r in R.sort_values("rec_f1", ascending=False).iterrows()]
if have("E10_interpret", "E10_common_core.json"):
    D["core_features"] = json.load(open(P("E10_interpret", "E10_common_core.json")))["common_core_features"]
else:   # derive from the TSFGA core features of the main run
    cores = [set(eval(r.core_features)) for _, r in st[st.method == "TSFGA"].iterrows()]
    D["core_features"] = sorted(set.intersection(*cores)) if cores else []
stab = st[st.method == "TSFGA"]
D["tsfga_core_by_process"] = {r.process: eval(r.core_features) for _, r in stab.iterrows()}
D["tsfga_jaccard_by_process"] = {r.process: round(r.jaccard_mean, 3) for _, r in stab.iterrows()}
if have("E10_interpret", "importance_selected_features.csv"):
    imp = pd.read_csv(P("E10_interpret", "importance_selected_features.csv"))
    D["top_importance"] = {p: [(r.feature, round(r.importance, 2), round(r.selection_freq, 2)) for _, r in
                               imp[imp.process == p].sort_values("importance", ascending=False).head(5).iterrows()] for p in procs}
    D["category_share"] = pd.read_csv(P("E10_interpret", "E10_category_share.csv")).to_dict(orient="records")
else:
    D["top_importance"] = None
    # category share of the majority-vote TSFGA subset, computed from selections
    from collections import Counter
    selj = json.load(open(P("main", "selections.json")))
    cs = []
    for p in procs:
        keys = [k for k in selj if k.startswith(f"{p}|TSFGA|")]
        cnt = Counter(f for k in keys for f in selj[k])
        maj = [f for f, c in cnt.items() if c >= len(keys) / 2]
        row = dict(process=p, lot=0, order=0, workshop=0, machine=0)
        for f in maj:
            row[meta["feature_category"].get(f, "workshop")] += 1
        cs.append(row)
    D["category_share"] = cs

# --- second dataset (E9)
if not have("E9_dataset2", "summary_by_seed.csv"):
    D["dataset2"] = None; D["dataset2_info"] = None
else:
  s2 = pd.read_csv(P("E9_dataset2", "summary_by_seed.csv"))
  D["seeds_dataset2"] = int(s2.seed.nunique())
  g2 = s2.groupby(["process", "method"])
  m2 = [m for m in ["ALL", "FILTER", "GA", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS", "NSGA2"] if m in set(s2.method)]
  r2 = []
  for p in sorted(s2.process.unique()):
      r2.append([p.capitalize()] + [f"{g2['MRA'].mean().loc[(p, m)]:.4f} ± {g2['MRA'].std().loc[(p, m)]:.3f}" for m in m2])
  a2 = s2.groupby("method")
  r2.append(["Average MRA"] + [f4(a2["MRA"].mean()[m]) for m in m2])
  r2.append(["Average PFR"] + [pct(a2["PRF"].mean()[m]) for m in m2])
  D["dataset2"] = dict(methods=m2, rows=r2, avg_mra={m: float(a2["MRA"].mean()[m]) for m in m2},
                       prf={m: pct(a2["PRF"].mean()[m]) for m in m2})
  d2 = _load_data("E9_dataset2", "dataset2")
  D["dataset2_info"] = dict(n_rows=int(len(d2)), n_products=int(d2["product"].nunique()), ct_mean=float(d2.ct.mean()),
                            ct_max=float(d2.ct.max()), n_combos=int(d2.groupby(["process", "product", "operation"]).ngroups))
D["n_evals"] = {m: float(v) for m, v in s.groupby("method").n_evals.mean().items()}
if have("main", "histories.csv"):
    hh = pd.read_csv(P("main", "histories.csv"))
    D["generations"] = {m: float(v) for m, v in hh.groupby(["method", "process", "seed"]).gen.max().groupby("method").mean().items()}
    D["best_fitness"] = {m: float(v) for m, v in hh.groupby(["method", "process", "seed"]).best.max().groupby("method").mean().items()}

json.dump(D, open(out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("wrote", out)
