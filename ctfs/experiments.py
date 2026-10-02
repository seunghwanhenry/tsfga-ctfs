"""Experiment orchestration. Every experiment writes CSV/JSON/PNG into <out>/<experiment>/.

E1  ablation      : ALL / FILTER / GA / TSFGA                                  (main run)
E2  seeds         : multi-seed convergence + Jaccard stability                 (main run)
E3  stats         : Wilcoxon, Friedman + Nemenyi, CD diagram                   (from main run)
E4  sensitivity   : OAT grid over lambda, PCC threshold, P, pc, pm
E5  metrics/time  : MRA/MAE/RMSE/MAPE/R2 + wall-clock per method               (main run)
E6  baselines     : mRMR, MI, DDA, PFI-SBS, BPSO, BGWO, NSGA-II, Boruta, LASSO, RFE (main run)
E7  temporal      : random vs chronological split
E8  transfer      : TSFGA-selected features evaluated with RF/LGBM/MLP/SVR/DT
E9  dataset2      : second (synthetic) fab with different structure
E10 interpret     : SHAP importance, selection-frequency map, ground-truth recovery
"""
from __future__ import annotations

import json
import os
import time
from collections import Counter

import numpy as np
import pandas as pd

from . import data as D
from . import metrics as M
from . import plots as PL
from . import stats as ST
from .evaluator import evaluate_features, make_regressor
from .methods import STOCHASTIC, run_method

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def _dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=_json_default)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def _as_list(x):
    if x is None:
        return None
    return list(x) if isinstance(x, (list, tuple, np.ndarray)) else [x]


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def load_dataset(cfg, which="main"):
    dc = cfg["data"] if which == "main" else cfg["dataset2"]
    if which == "main" and dc.get("source") == "real":
        df, meta = D.load_real(dc["path"], dc.get("feature_cols"))
        procs = dc.get("processes")
        if procs:
            procs = [procs] if isinstance(procs, str) else list(procs)
            df = df[df.process.isin(procs)].reset_index(drop=True)
    else:
        pr = dc.get("processes")
        procs = D.PROCESSES[:pr] if isinstance(pr, int) else ([pr] if isinstance(pr, str) else pr)
        kw = {k: v for k, v in dc.items() if k not in ("source", "path", "processes", "feature_cols", "name")}
        df, meta = D.make_synthetic_fab(name=dc.get("name", "FabA"), processes=procs, **kw)
    return df, meta


def _run_one(method, dproc, feats, cfg, seed, cache_path=None, **kw):
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)
    r = run_method(method, dproc, feats, cfg, seed=seed, **kw)
    if cache_path:
        _dump(r, cache_path)
    return r


def _per_combo(r, dproc, cfg, seed, process):
    pc = evaluate_features(dproc, r["selected"], regressor=cfg["eval_regressor"], seed=seed,
                           fast=cfg["eval_fast"], unit=cfg["eval_unit"], n_jobs=cfg["n_jobs"])
    pc["process"], pc["method"], pc["seed"] = process, r["method"], seed
    return pc


def _summary_row(r, dproc, feats, pc, process, seed, meta):
    tr = dproc[dproc.split == "train"]
    X = tr[r["selected"]].to_numpy(float) if r["selected"] else np.zeros((len(tr), 0))
    row = dict(process=process, method=r["method"], seed=seed, n_selected=r["n_selected"],
               PRF=M.prf(r["n_selected"], len(feats)), CFS=M.cfs_merit(X, tr["ct"].to_numpy(float)),
               n_high_corr_pairs=M.n_high_corr_pairs(X, 0.8), time_s=r["time_s"], n_evals=r["n_evals"],
               val_MRA=r["extra"].get("val_mra_selected"))
    for m in ("MRA", "MAE", "RMSE", "MAPE", "R2"):
        row[m] = pc[m].mean() if len(pc) else np.nan
        row[f"{m}_std"] = pc[m].std() if len(pc) else np.nan
    if meta.get("true_features"):
        row.update({f"rec_{k}": v for k, v in M.recovery(r["selected"], meta["true_features"][process],
                                                          meta.get("equivalence")).items()})
    return row


# --------------------------------------------------------------------------- #
# MAIN RUN: E1 ablation + E2 seeds + E5 metrics/time + E6 baselines
# --------------------------------------------------------------------------- #
def _job(process, method, seed, dproc, feats, cfg, meta, cache_path, tag, **kw):
    """One (process, method, seed) unit of work; safe to run in a worker process."""
    t0 = time.time()
    r = _run_one(method, dproc, feats, cfg, seed, cache_path, **kw)
    pc = _per_combo(r, dproc, cfg, seed, process)
    row = _summary_row(r, dproc, feats, pc, process, seed, meta)
    hist = [dict(process=process, method=method, seed=seed, **h) for h in r["extra"].get("history", [])]
    log(f"[{tag}] {process:13s} {method:8s} seed={seed} k={r['n_selected']:2d} "
        f"MRA={row['MRA']:.4f} t={r['time_s']:.1f}s ({time.time()-t0:.1f}s incl. eval)")
    return dict(process=process, method=method, seed=seed, selected=r["selected"], pc=pc, row=row, hist=hist)


def _run_jobs(jobs, workers):
    """Run a list of (callable, kwargs) either sequentially or with joblib (loky processes)."""
    if workers is None or workers == 1 or len(jobs) <= 1:
        return [f(**kw) for f, kw in jobs]
    from joblib import Parallel, delayed
    # heavy jobs (metaheuristics) first so that the tail of the schedule is short
    order = sorted(range(len(jobs)), key=lambda i: 0 if jobs[i][1]["method"] in STOCHASTIC else 1)
    res = Parallel(n_jobs=workers, backend="loky", verbose=0)(delayed(jobs[i][0])(**jobs[i][1]) for i in order)
    inv = {i: k for k, i in enumerate(order)}
    return [res[inv[i]] for i in range(len(jobs))]


def run_main(cfg, out, df=None, meta=None, methods=None, seeds=None, tag="main"):
    out = _ensure(os.path.join(out, tag))
    cache = _ensure(os.path.join(out, "cache"))
    if df is None:
        df, meta = load_dataset(cfg)
    feats = list(meta["feature_names"])
    methods = _as_list(methods or cfg["methods"])
    seeds = _as_list(seeds or cfg["seeds"])
    df = D.assign_splits(df, cfg["split"]["mode"], cfg["split"]["ratios"], cfg["split"]["seed"])
    procs = list(df.process.unique())
    jobs = []
    for p in procs:
        dproc = D.process_frame(df, p)
        for method in methods:
            for seed in seeds:
                jobs.append((_job, dict(process=p, method=method, seed=seed, dproc=dproc, feats=feats, cfg=cfg,
                                        meta=meta, cache_path=os.path.join(cache, f"{p}_{method}_{seed}.json"), tag=tag)))
    log(f"[{tag}] {len(jobs)} jobs ({len(procs)} processes x {len(methods)} methods x {len(seeds)} seeds), "
        f"workers={cfg.get('workers', 1)}")
    results = _run_jobs(jobs, cfg.get("workers", 1))
    summary = pd.DataFrame([r["row"] for r in results])
    per_combo = pd.concat([r["pc"] for r in results], ignore_index=True)
    histories = pd.DataFrame([h for r in results for h in r["hist"]])
    selections = {f"{r['process']}|{r['method']}|{r['seed']}": r["selected"] for r in results}
    summary.to_csv(os.path.join(out, "summary_by_seed.csv"), index=False)
    per_combo.to_csv(os.path.join(out, "per_combo.csv"), index=False)
    histories.to_csv(os.path.join(out, "histories.csv"), index=False)
    _dump(selections, os.path.join(out, "selections.json"))
    df.to_parquet(os.path.join(out, "data_with_splits.parquet"))
    _dump({k: v for k, v in meta.items() if k != "proc_cfg"}, os.path.join(out, "meta.json"))
    make_main_tables(cfg, out, summary, per_combo, histories, selections, meta, df)
    return summary, per_combo, histories, selections


def _agg(summary, cols):
    g = summary.groupby(["process", "method"])
    out = g[cols].mean()
    sd = g[cols].std().add_suffix("_sd")
    return pd.concat([out, sd], axis=1).reset_index()


def make_main_tables(cfg, out, summary, per_combo, histories, selections, meta, df):
    feats = list(meta["feature_names"])
    # ---- E1 ablation table (Table III analogue + ablation) --------------------
    abl = summary[summary.method.isin(["ALL", "FILTER", "GA", "TSFGA"])]
    t = _agg(abl, ["MRA", "MAE", "RMSE", "MAPE", "R2", "PRF", "n_selected", "CFS", "time_s"])
    t.to_csv(os.path.join(out, "E1_ablation.csv"), index=False)
    _pivot_table(t, "MRA", "E1_ablation_MRA", out)
    _pivot_table(t, "PRF", "E1_ablation_PRF", out)
    if "TSFGA" in set(per_combo.method) and "ALL" in set(per_combo.method):
        PL.violin_before_after(per_combo[per_combo.seed == per_combo.seed.min()],
                               os.path.join(out, "fig_E1_violin_before_after.png"))
    # ---- E6 baseline comparison (Table IV / V analogue) -------------------------
    t6 = _agg(summary, ["MRA", "MAE", "RMSE", "MAPE", "R2", "PRF", "n_selected", "CFS",
                         "n_high_corr_pairs", "time_s", "n_evals"])
    t6.to_csv(os.path.join(out, "E6_baselines.csv"), index=False)
    for metric in ("MRA", "PRF", "CFS", "MAE", "RMSE", "MAPE", "R2", "time_s", "n_high_corr_pairs"):
        _pivot_table(t6, metric, f"E6_{metric}", out, rank=metric in ("MRA", "PRF", "CFS", "R2", "MAE", "RMSE", "MAPE"),
                     higher_better=metric not in ("MAE", "RMSE", "MAPE", "time_s", "n_high_corr_pairs"))
    # ---- E5 metrics + time table (long) -----------------------------------------
    t6.to_csv(os.path.join(out, "E5_metrics_time.csv"), index=False)
    # ---- E2 seeds: convergence + stability --------------------------------------
    if len(histories):
        PL.convergence(histories, os.path.join(out, "fig_E2_convergence.png"),
                       methods=[m for m in ["TSFGA", "GA", "BPSO", "BGWO"] if m in set(histories.method)])
    stab = []
    for p in summary.process.unique():
        for m in summary.method.unique():
            sets = [selections[k] for k in selections if k.startswith(f"{p}|{m}|")]
            cnt = Counter(f for s in sets for f in s)
            stab.append(dict(process=p, method=m, n_seeds=len(sets),
                             jaccard_mean=M.mean_pairwise_jaccard(sets),
                             n_selected_mean=np.mean([len(s) for s in sets]),
                             n_selected_sd=np.std([len(s) for s in sets]),
                             core_features=[f for f, c in cnt.items() if c == len(sets)],
                             n_core=sum(1 for c in cnt.values() if c == len(sets))))
    stab = pd.DataFrame(stab)
    stab.to_csv(os.path.join(out, "E2_stability.csv"), index=False)
    _pivot_table(stab, "jaccard_mean", "E2_jaccard", out)
    # ---- Fig.5 analogue: MRA vs subset size (from cached extras) -----------------
    _fig5(cfg, out, df, feats, summary)
    # ---- Fig.6 analogue: correlation heatmaps among selected features -----------
    _fig6(out, df, selections, summary)
    # ---- NSGA-II Pareto fronts ---------------------------------------------------
    _pareto_figs(out, summary)
    # ---- selection frequency map --------------------------------------------------
    freq = _selection_frequency(selections, feats, "TSFGA")
    if freq is not None:
        freq.to_csv(os.path.join(out, "E2_selection_frequency_TSFGA.csv"))
        PL.selection_frequency(freq, os.path.join(out, "fig_E2_selection_frequency_TSFGA.png"),
                               category=meta.get("feature_category"))
    # ---- ground-truth recovery (synthetic) ---------------------------------------
    if "rec_f1" in summary.columns:
        rec = summary.groupby(["process", "method"])[["rec_precision", "rec_recall", "rec_f1"]].mean().reset_index()
        rec.to_csv(os.path.join(out, "E10_recovery.csv"), index=False)
        _pivot_table(rec, "rec_f1", "E10_recovery_f1", out)


def _pivot_table(t, metric, name, out, rank=False, higher_better=True):
    W = t.pivot(index="process", columns="method", values=metric)
    if f"{metric}_sd" in t.columns:
        S = t.pivot(index="process", columns="method", values=f"{metric}_sd")
    else:
        S = None
    W.loc["Average"] = W.mean()
    W.to_csv(os.path.join(out, f"{name}.csv"))
    # markdown with mean ± sd and rank in parentheses
    lines = ["| process | " + " | ".join(W.columns) + " |", "|---|" + "---|" * len(W.columns)]
    ranks_sum = None
    for p, row in W.iterrows():
        cells = []
        rk = row.rank(ascending=not higher_better) if rank else None
        if rank and p != "Average":
            ranks_sum = rk if ranks_sum is None else ranks_sum + rk
        for m in W.columns:
            v = row[m]
            s = f"{v:.4f}" if abs(v) < 100 else f"{v:.1f}"
            if S is not None and p != "Average" and not np.isnan(S.loc[p, m]):
                s += f" ± {S.loc[p, m]:.3f}"
            if rank and p != "Average":
                s += f" ({int(rk[m])})"
            cells.append(s)
        lines.append(f"| {p} | " + " | ".join(cells) + " |")
    if rank and ranks_sum is not None:
        lines.append("| rank sum | " + " | ".join(str(int(ranks_sum[m])) for m in W.columns) + " |")
    with open(os.path.join(out, f"{name}.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def _fig5(cfg, out, df, feats, summary):
    cache = os.path.join(out, "cache")
    seed = int(summary.seed.min())
    for p in summary.process.unique():
        curves, stars, squares, base = {}, {}, {}, None
        for m in ("mRMR", "MI", "DDA", "PFI-SBS", "RFE"):
            fp = os.path.join(cache, f"{p}_{m}_{seed}.json")
            if not os.path.exists(fp):
                continue
            r = json.load(open(fp))
            ex = r["extra"]
            base = ex.get("baseline_val_mra", base)
            if "curve" in ex and ex["curve"]:
                c = ex["curve"]
                curves[m] = c
                stars[m] = (r["n_selected"], ex["val_mra_selected"])       # the subset actually returned
                kb = next((t for t in sorted(c) if base is not None and t[1] > base), None)
                squares[m] = kb
        fp = os.path.join(cache, f"{p}_TSFGA_{seed}.json")
        if os.path.exists(fp):
            r = json.load(open(fp))
            stars["TSFGA"] = (r["n_selected"], r["extra"]["val_mra_selected"])
            curves["TSFGA"] = [stars["TSFGA"]]
        if curves and base is not None:
            PL.mra_vs_size(curves, base, stars, squares, os.path.join(out, f"fig_E6_mra_vs_size_{p}.png"), title=p)


def _fig6(out, df, selections, summary):
    seed = int(summary.seed.min())
    for p in summary.process.unique():
        tr = df[(df.process == p) & (df.split == "train")]
        Xs = {}
        for m in ("mRMR", "MI", "DDA", "PFI-SBS", "TSFGA"):
            key = f"{p}|{m}|{seed}"
            if key in selections and selections[key]:
                Xs[m] = (tr[selections[key]].to_numpy(float), selections[key])
        if Xs:
            PL.corr_heatmaps(Xs, os.path.join(out, f"fig_E6_corr_{p}.png"))


def _pareto_figs(out, summary):
    cache = os.path.join(out, "cache")
    seed = int(summary.seed.min())
    for p in summary.process.unique():
        fp = os.path.join(cache, f"{p}_NSGA2_{seed}.json")
        ft = os.path.join(cache, f"{p}_TSFGA_{seed}.json")
        if not os.path.exists(fp):
            continue
        r = json.load(open(fp))
        ts = None
        if os.path.exists(ft):
            t = json.load(open(ft))
            ts = (t["n_selected"], t["extra"]["val_mra_selected"])
        PL.pareto_front(r["extra"]["pareto"], r["extra"]["picked"], ts,
                        os.path.join(out, f"fig_E6_pareto_{p}.png"), title=p)


def _selection_frequency(selections, feats, method):
    keys = [k for k in selections if k.split("|")[1] == method]
    if not keys:
        return None
    procs = sorted({k.split("|")[0] for k in keys})
    freq = pd.DataFrame(0.0, index=feats, columns=procs)
    for p in procs:
        ks = [k for k in keys if k.startswith(f"{p}|")]
        for k in ks:
            for f in selections[k]:
                freq.loc[f, p] += 1.0 / len(ks)
    return freq


# --------------------------------------------------------------------------- #
# E3 statistics
# --------------------------------------------------------------------------- #
def run_stats(cfg, out, main_tag="main"):
    src = os.path.join(out, main_tag)
    out3 = _ensure(os.path.join(out, "E3_stats"))
    pc = pd.read_csv(os.path.join(src, "per_combo.csv"))
    # average over seeds per (process, product, operation, method) so blocks are combos
    agg = pc.groupby(["process", "product", "operation", "method"])[["MRA", "MAE", "RMSE"]].mean().reset_index()
    rows = []
    for metric, hb in (("MRA", True), ("MAE", False), ("RMSE", False)):
        w = ST.wilcoxon_vs_reference(agg, "TSFGA", metric, hb)
        w["metric"] = metric
        rows.append(w)
        # per process too
        for p in agg.process.unique():
            wp = ST.wilcoxon_vs_reference(agg[agg.process == p], "TSFGA", metric, hb)
            wp["metric"], wp["process"] = metric, p
            rows.append(wp)
    W = pd.concat(rows, ignore_index=True)
    W["process"] = W.get("process", pd.Series(dtype=object)).fillna("ALL_PROCESSES")
    W.to_csv(os.path.join(out3, "wilcoxon_vs_TSFGA.csv"), index=False)
    fr = ST.friedman_nemenyi(agg, "MRA", True)
    fr["avg_rank"].to_csv(os.path.join(out3, "friedman_avg_rank_MRA.csv"))
    fr["pairwise"].to_csv(os.path.join(out3, "nemenyi_pairwise_MRA.csv"), index=False)
    _dump({k: v for k, v in fr.items() if k not in ("avg_rank", "pairwise")}, os.path.join(out3, "friedman_MRA.json"))
    ST.plot_cd_diagram(fr["avg_rank"], fr["CD"], title=f"Nemenyi CD diagram (MRA), N={fr['N']} combos",
                       path=os.path.join(out3, "fig_E3_cd_diagram_MRA.png"))
    # ablation-only Friedman
    sub = agg[agg.method.isin(["ALL", "FILTER", "GA", "TSFGA"])]
    fr2 = ST.friedman_nemenyi(sub, "MRA", True)
    _dump({k: v for k, v in fr2.items() if k not in ("avg_rank", "pairwise")}, os.path.join(out3, "friedman_ablation.json"))
    fr2["avg_rank"].to_csv(os.path.join(out3, "friedman_avg_rank_ablation.csv"))
    ST.plot_cd_diagram(fr2["avg_rank"], fr2["CD"], title="Ablation: Nemenyi CD (MRA)",
                       path=os.path.join(out3, "fig_E3_cd_diagram_ablation.png"))
    log(f"[E3] Friedman p={fr['p_value']:.2e}, CD={fr['CD']:.3f}; avg ranks:\n{fr['avg_rank'].round(2).to_string()}")
    return W, fr


# --------------------------------------------------------------------------- #
# E4 sensitivity (one-at-a-time)
# --------------------------------------------------------------------------- #
def run_sensitivity(cfg, out, main_tag="main"):
    out4 = _ensure(os.path.join(out, "E4_sensitivity"))
    cache = _ensure(os.path.join(out4, "cache"))
    df = pd.read_parquet(os.path.join(out, main_tag, "data_with_splits.parquet"))
    meta = json.load(open(os.path.join(out, main_tag, "meta.json")))
    feats = meta["feature_names"]
    grid = cfg["sensitivity"]["grid"]
    seeds = _as_list(cfg["sensitivity"]["seeds"])
    jobs, tags = [], []
    for param, values in grid.items():
        for v in _as_list(values):
            for p in df.process.unique():
                dproc = D.process_frame(df, p)
                for seed in seeds:
                    kw = {}
                    if param == "lambda":
                        kw["lam"] = v
                    elif param == "pcc_threshold":
                        kw["threshold"] = v
                    elif param.startswith("ga."):
                        kw["ga_overrides"] = {param.split(".", 1)[1]: v}
                    # canonical cache key on the EFFECTIVE parameters so that the default
                    # configuration (shared by every grid) is only run once
                    eff_lam = kw.get("lam", cfg["lambda"])
                    eff_thr = kw.get("threshold", cfg["pcc_threshold"])
                    eff_ga = dict(cfg["ga"], **kw.get("ga_overrides", {}))
                    cp = os.path.join(cache, f"{p}_lam{eff_lam}_thr{eff_thr}_P{eff_ga['pop_size']}"
                                             f"_pc{eff_ga['pc']}_pm{eff_ga['pm']}_{seed}.json")
                    jobs.append((_job, dict(process=p, method="TSFGA", seed=seed, dproc=dproc, feats=feats, cfg=cfg,
                                            meta=meta, cache_path=cp, tag=f"E4 {param}={v}", **kw)))
                    tags.append((param, v))
    # de-duplicate identical effective configurations (same cache path) before running
    seen, uniq_jobs, uniq_idx = {}, [], []
    for i, (f, kw) in enumerate(jobs):
        key = kw["cache_path"]
        if key not in seen:
            seen[key] = len(uniq_jobs)
            uniq_jobs.append((f, kw))
        uniq_idx.append(seen[key])
    log(f"[E4] {len(jobs)} grid points, {len(uniq_jobs)} distinct runs, workers={cfg.get('workers', 1)}")
    uniq_res = _run_jobs(uniq_jobs, cfg.get("workers", 1))
    rows = []
    for (param, v), ui in zip(tags, uniq_idx):
        row = dict(uniq_res[ui]["row"])
        row.update(param=param, value=v)
        rows.append(row)
    S = pd.DataFrame(rows)
    S.to_csv(os.path.join(out4, "sensitivity_by_seed.csv"), index=False)
    A = S.groupby(["param", "value", "process"])[["MRA", "PRF", "n_selected", "CFS", "time_s"]].agg(["mean", "std"])
    A.columns = [f"{a}_{b}" for a, b in A.columns]
    A = A.reset_index()
    A.to_csv(os.path.join(out4, "sensitivity_summary.csv"), index=False)
    for param in grid:
        d = A[A.param == param].rename(columns={"value": param})
        PL.sensitivity(d, param, os.path.join(out4, f"fig_E4_{param.replace('.', '_')}.png"))
    # compact table: average over processes
    T = S.groupby(["param", "value"])[["MRA", "PRF", "n_selected", "CFS"]].mean().round(4).reset_index()
    T.to_csv(os.path.join(out4, "sensitivity_avg_over_processes.csv"), index=False)
    return S


# --------------------------------------------------------------------------- #
# E7 temporal split
# --------------------------------------------------------------------------- #
def run_temporal(cfg, out, main_tag="main"):
    out7 = _ensure(os.path.join(out, "E7_temporal"))
    df, meta = load_dataset(cfg)
    methods = _as_list(cfg["temporal"]["methods"])
    seeds = _as_list(cfg["temporal"]["seeds"])
    res = {}
    for mode in ("random", "temporal"):
        c = dict(cfg)
        c["split"] = dict(cfg["split"], mode=mode)
        s, pc, _, _ = run_main(c, out7, df=df, meta=meta, methods=methods, seeds=seeds, tag=f"split_{mode}")
        s["split_mode"] = mode
        pc["split_mode"] = mode
        res[mode] = (s, pc)
    S = pd.concat([res["random"][0], res["temporal"][0]], ignore_index=True)
    S.to_csv(os.path.join(out7, "temporal_summary_by_seed.csv"), index=False)
    A = S.groupby(["split_mode", "process", "method"])[["MRA", "MAE", "RMSE", "MAPE", "R2", "PRF", "n_selected"]].agg(["mean", "std"])
    A.columns = [f"{a}_{b}" for a, b in A.columns]
    A = A.reset_index()
    A.to_csv(os.path.join(out7, "temporal_summary.csv"), index=False)
    # delta of TSFGA over ALL under each split
    piv = S.groupby(["split_mode", "process", "method"])["MRA"].mean().unstack("method")
    piv["gain_TSFGA_vs_ALL"] = piv["TSFGA"] - piv["ALL"]
    piv.to_csv(os.path.join(out7, "E7_temporal_vs_random_MRA.csv"))
    PL.grouped_bars(S.groupby(["split_mode", "process", "method"])["MRA"].mean().reset_index()
                    .assign(x=lambda d: d.process + "\n" + d.split_mode), "x", "MRA", "method",
                    os.path.join(out7, "fig_E7_temporal_vs_random.png"), title="MRA: random vs temporal split")
    # feature overlap between the two splits (TSFGA)
    sel_r = json.load(open(os.path.join(out7, "split_random", "selections.json")))
    sel_t = json.load(open(os.path.join(out7, "split_temporal", "selections.json")))
    ov = []
    for p in df.process.unique():
        for seed in seeds:
            a, b = sel_r.get(f"{p}|TSFGA|{seed}", []), sel_t.get(f"{p}|TSFGA|{seed}", [])
            ov.append(dict(process=p, seed=seed, jaccard_random_vs_temporal=M.jaccard(a, b)))
    pd.DataFrame(ov).to_csv(os.path.join(out7, "E7_selection_overlap.csv"), index=False)
    return A


# --------------------------------------------------------------------------- #
# E8 model transferability of the selected subset
# --------------------------------------------------------------------------- #
def run_transfer(cfg, out, main_tag="main"):
    out8 = _ensure(os.path.join(out, "E8_transfer"))
    df = pd.read_parquet(os.path.join(out, main_tag, "data_with_splits.parquet"))
    meta = json.load(open(os.path.join(out, main_tag, "meta.json")))
    sel = json.load(open(os.path.join(out, main_tag, "selections.json")))
    feats = meta["feature_names"]
    rows, pcs = [], []
    for p in df.process.unique():
        dproc = D.process_frame(df, p)
        # majority-vote subset across seeds (features selected in >= 50% of seeds)
        keys = [k for k in sel if k.startswith(f"{p}|TSFGA|")]
        cnt = Counter(f for k in keys for f in sel[k])
        majority = [f for f, c in cnt.items() if c >= len(keys) / 2] or sel[keys[0]]
        seed0 = sel[keys[0]]
        for reg in cfg["transfer"]["regressors"]:
            for label, fs in (("ALL", feats), ("TSFGA(seed0)", seed0), ("TSFGA(majority)", majority)):
                try:
                    pc = evaluate_features(dproc, fs, regressor=reg, seed=0, fast=cfg["eval_fast"],
                                           unit=cfg["eval_unit"], n_jobs=cfg["n_jobs"])
                except Exception as e:      # e.g. lightgbm missing
                    log(f"[E8] {reg} failed: {e}")
                    continue
                pc["process"], pc["regressor"], pc["features"] = p, reg, label
                pcs.append(pc)
                rows.append(dict(process=p, regressor=reg, features=label, n_features=len(fs),
                                 **{m: pc[m].mean() for m in ("MRA", "MAE", "RMSE", "MAPE", "R2")},
                                 MRA_std=pc["MRA"].std()))
                log(f"[E8] {p} {reg} {label} k={len(fs)} MRA={rows[-1]['MRA']:.4f}")
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(out8, "transfer_summary.csv"), index=False)
    pd.concat(pcs, ignore_index=True).to_csv(os.path.join(out8, "transfer_per_combo.csv"), index=False)
    piv = T.pivot_table(index=["process", "regressor"], columns="features", values="MRA")
    piv["gain_majority"] = piv["TSFGA(majority)"] - piv["ALL"]
    piv.to_csv(os.path.join(out8, "E8_transfer_MRA.csv"))
    PL.grouped_bars(T.assign(x=lambda d: d.process + "\n" + d.regressor), "x", "MRA", "features",
                    os.path.join(out8, "fig_E8_transfer.png"), title="Selected-subset transfer across regressors")
    # paired Wilcoxon per regressor (ALL vs majority) over combos
    PC = pd.concat(pcs, ignore_index=True)
    wrows = []
    for reg in PC.regressor.unique():
        d = PC[PC.regressor == reg].rename(columns={"features": "method"})
        w = ST.wilcoxon_vs_reference(d, "TSFGA(majority)", "MRA", True)
        w["regressor"] = reg
        wrows.append(w)
    pd.concat(wrows).to_csv(os.path.join(out8, "E8_wilcoxon.csv"), index=False)
    return T


# --------------------------------------------------------------------------- #
# E9 second dataset
# --------------------------------------------------------------------------- #
def run_dataset2(cfg, out):
    df, meta = load_dataset(cfg, which="dataset2")
    s, pc, h, sel = run_main(cfg, out, df=df, meta=meta, methods=cfg["dataset2_methods"],
                             seeds=cfg.get("dataset2_seeds"), tag="E9_dataset2")
    return s


# --------------------------------------------------------------------------- #
# E10 interpretability
# --------------------------------------------------------------------------- #
def run_interpret(cfg, out, main_tag="main"):
    out10 = _ensure(os.path.join(out, "E10_interpret"))
    df = pd.read_parquet(os.path.join(out, main_tag, "data_with_splits.parquet"))
    meta = json.load(open(os.path.join(out, main_tag, "meta.json")))
    sel = json.load(open(os.path.join(out, main_tag, "selections.json")))
    feats = meta["feature_names"]
    cat = meta.get("feature_category", {})
    try:
        import shap
        have_shap = True
    except Exception:
        have_shap = False
    rows, imp_all = [], {}
    for p in df.process.unique():
        dproc = D.process_frame(df, p)
        keys = [k for k in sel if k.startswith(f"{p}|TSFGA|")]
        cnt = Counter(f for k in keys for f in sel[k])
        majority = [f for f, c in cnt.items() if c >= len(keys) / 2] or sel[keys[0]]
        tr, te = dproc[dproc.split == "train"], dproc[dproc.split == "test"]
        model = make_regressor("rf", 0, fast=cfg["eval_fast"], n_jobs=cfg["n_jobs"])
        model.fit(tr[majority].to_numpy(float), tr["ct"].to_numpy(float))
        Xs = te[majority].to_numpy(float)
        n = min(cfg["interpret"]["n_shap"], len(Xs))
        Xs = Xs[np.random.default_rng(0).choice(len(Xs), n, replace=False)]
        if have_shap:
            ex = shap.TreeExplainer(model)
            sv = ex.shap_values(Xs)
            imp = pd.Series(np.abs(sv).mean(axis=0), index=majority)
            kind = "mean|SHAP|"
        else:
            from sklearn.inspection import permutation_importance
            pi = permutation_importance(model, Xs, te["ct"].to_numpy(float)[:n], n_repeats=5, random_state=0)
            imp = pd.Series(pi.importances_mean, index=majority)
            kind = "permutation"
        imp_all[p] = imp
        PL.bar_importance(imp, os.path.join(out10, f"fig_E10_importance_{p}.png"), title=f"{p} ({kind})")
        for f, v in imp.items():
            rows.append(dict(process=p, feature=f, category=cat.get(f, ""), importance=v, kind=kind,
                             selection_freq=cnt[f] / len(keys),
                             is_true=(f in meta["true_features"][p]) if meta.get("true_features") else None))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(out10, "importance_selected_features.csv"), index=False)
    # category share of selected features per process
    share = R.groupby(["process", "category"]).size().unstack(fill_value=0)
    share.to_csv(os.path.join(out10, "E10_category_share.csv"))
    # common core across processes
    procs = list(df.process.unique())
    core = set.intersection(*[set(R[R.process == p].feature) for p in procs]) if procs else set()
    _dump(dict(common_core_features=sorted(core), n_processes=len(procs)), os.path.join(out10, "E10_common_core.json"))
    # cross-process selection frequency heatmap (all methods vs TSFGA) already in main; add union
    freq = _selection_frequency(sel, feats, "TSFGA")
    if freq is not None:
        PL.selection_frequency(freq, os.path.join(out10, "fig_E10_selection_frequency.png"), category=cat)
    # ground-truth recovery per method (synthetic)
    if meta.get("true_features"):
        rec = []
        for k, s in sel.items():
            p, m, seed = k.split("|")
            rec.append(dict(process=p, method=m, seed=int(seed),
                            **M.recovery(s, meta["true_features"][p], meta.get("equivalence")),
                            n_redundant_kept=sum(1 for g in meta["redundant_groups"] if len(set(g) & set(s)) > 1)))
        rec = pd.DataFrame(rec)
        rec.to_csv(os.path.join(out10, "recovery_by_seed.csv"), index=False)
        A = rec.groupby("method")[["precision", "recall", "f1", "n_redundant_kept"]].mean().sort_values("f1", ascending=False)
        A.to_csv(os.path.join(out10, "E10_recovery_by_method.csv"))
        log(f"[E10] ground-truth recovery by method:\n{A.round(3).to_string()}")
    return R


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def write_report(cfg, out):
    parts = [f"# CTFS experiment report ({cfg['name']} preset)\n"]

    def add_md(title, path):
        if os.path.exists(path):
            parts.append(f"\n## {title}\n\n" + open(path).read())

    def add_csv(title, path, **kw):
        if os.path.exists(path):
            parts.append(f"\n## {title}\n\n" + pd.read_csv(path, **kw).round(4).to_markdown(index=False) + "\n")

    add_md("E1 Ablation – MRA (mean ± sd over seeds; rank)", os.path.join(out, "main", "E1_ablation_MRA.md"))
    add_md("E1 Ablation – PRF", os.path.join(out, "main", "E1_ablation_PRF.md"))
    add_md("E2 Stability – mean pairwise Jaccard across seeds", os.path.join(out, "main", "E2_jaccard.md"))
    add_csv("E3 Wilcoxon signed-rank vs TSFGA (all processes)",
            os.path.join(out, "E3_stats", "wilcoxon_vs_TSFGA.csv"))
    fj = os.path.join(out, "E3_stats", "friedman_MRA.json")
    if os.path.exists(fj):
        fr = json.load(open(fj))
        parts.append(f"\n## E3 Friedman test (MRA)\n\nchi2 = {fr['statistic']:.3f}, p = {fr['p_value']:.2e}, "
                     f"Iman–Davenport p = {fr['p_value_ID']:.2e}, Nemenyi CD = {fr['CD']:.3f} (k={fr['k']}, N={fr['N']})\n")
        rk = pd.read_csv(os.path.join(out, "E3_stats", "friedman_avg_rank_MRA.csv"))
        rk.columns = ["method", "avg_rank"]
        parts.append(rk.round(3).to_markdown(index=False) + "\n")
    add_csv("E4 Sensitivity (average over processes and seeds)",
            os.path.join(out, "E4_sensitivity", "sensitivity_avg_over_processes.csv"))
    add_md("E6 Baselines – MRA", os.path.join(out, "main", "E6_MRA.md"))
    add_md("E6 Baselines – PRF", os.path.join(out, "main", "E6_PRF.md"))
    add_md("E6 Baselines – CFS", os.path.join(out, "main", "E6_CFS.md"))
    add_md("E5 Baselines – wall-clock time (s)", os.path.join(out, "main", "E6_time_s.md"))
    add_md("E5 Baselines – MAE", os.path.join(out, "main", "E6_MAE.md"))
    add_md("E5 Baselines – R2", os.path.join(out, "main", "E6_R2.md"))
    add_md("E6 Baselines – # feature pairs with |r|>0.8", os.path.join(out, "main", "E6_n_high_corr_pairs.md"))
    add_csv("E7 Temporal vs random split – MRA", os.path.join(out, "E7_temporal", "E7_temporal_vs_random_MRA.csv"))
    add_csv("E7 TSFGA selection overlap (random vs temporal)", os.path.join(out, "E7_temporal", "E7_selection_overlap.csv"))
    add_csv("E8 Transfer of TSFGA subset to other regressors – MRA", os.path.join(out, "E8_transfer", "E8_transfer_MRA.csv"))
    add_csv("E8 Wilcoxon (majority subset vs ALL per regressor)", os.path.join(out, "E8_transfer", "E8_wilcoxon.csv"))
    add_md("E9 Second dataset – MRA", os.path.join(out, "E9_dataset2", "E6_MRA.md"))
    add_md("E9 Second dataset – PRF", os.path.join(out, "E9_dataset2", "E6_PRF.md"))
    add_csv("E10 Ground-truth recovery by method (synthetic only)",
            os.path.join(out, "E10_interpret", "E10_recovery_by_method.csv"))
    add_csv("E10 Category share of TSFGA-selected features", os.path.join(out, "E10_interpret", "E10_category_share.csv"))
    figs = []
    for root, _, files in os.walk(out):
        for f in sorted(files):
            if f.endswith(".png"):
                figs.append(os.path.relpath(os.path.join(root, f), out))
    parts.append("\n## Figures\n\n" + "\n".join(f"- {f}" for f in figs) + "\n")
    with open(os.path.join(out, "REPORT.md"), "w") as f:
        f.write("\n".join(parts))
    log(f"report written to {os.path.join(out, 'REPORT.md')}")
