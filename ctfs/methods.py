"""Uniform interface for every feature-selection method.

run_method(name, dproc, feature_names, cfg, seed) -> dict(
    method, selected (list[str]), n_selected, time_s, n_evals, extra (dict)
)

Method names
------------
ALL       : no selection (baseline)
FILTER    : TSFGA phase 1 only (PCC+MI filter)                   [ablation]
GA        : TSFGA phase 2 only (GA on all features)              [ablation]
TSFGA     : proposed two-stage method (filter -> GA)
mRMR, MI  : filter rankings, k chosen on validation
DDA       : DDA-style correlation-ranked stepwise (Wang 2018)
PFI-SBS   : permutation importance + sequential backward (Schelthoff 2022)
BPSO      : filter -> binary PSO, same fitness
BGWO      : filter -> binary GWO, same fitness
NSGA2     : filter -> NSGA-II (min #features, max MRA), knee/weighted pick
Boruta, LASSO, RFE : widely used embedded/wrapper baselines
"""
from __future__ import annotations

import numpy as np

from . import filters as FL
from . import wrappers as WR
from .evaluator import FitnessEvaluator, Timer, WeightedFitness
from .ga import BinaryGA
from .metaheuristics import NSGA2, BinaryGWO, BinaryPSO, pick_from_pareto

ALL_METHODS = ["ALL", "FILTER", "GA", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS",
               "BPSO", "BGWO", "NSGA2", "Boruta", "LASSO", "RFE"]
STOCHASTIC = {"GA", "TSFGA", "BPSO", "BGWO", "NSGA2", "Boruta", "RFE", "PFI-SBS", "mRMR", "MI"}


def _mask(names, feature_names):
    idx = {f: i for i, f in enumerate(feature_names)}
    m = np.zeros(len(feature_names), bool)
    m[[idx[f] for f in names]] = True
    return m


def _evaluator(dproc, feature_names, cfg, seed):
    tr, va = dproc[dproc.split == "train"], dproc[dproc.split == "val"]
    unit = cfg.get("fitness_unit", "pooled")
    combo_tr = (tr["product"].astype(str) + "|" + tr["operation"].astype(str)).to_numpy()
    combo_va = (va["product"].astype(str) + "|" + va["operation"].astype(str)).to_numpy()
    ctx_tr = ctx_va = None
    if unit == "pooled" and cfg.get("fitness_context", "combo_onehot") == "combo_onehot":
        cats = np.unique(np.concatenate([combo_tr, combo_va]))
        ctx_tr = (combo_tr[:, None] == cats[None, :]).astype(float)
        ctx_va = (combo_va[:, None] == cats[None, :]).astype(float)
    return FitnessEvaluator(tr[feature_names].to_numpy(float), tr["ct"].to_numpy(float),
                            va[feature_names].to_numpy(float), va["ct"].to_numpy(float),
                            regressor=cfg["fitness_regressor"], seed=seed, fast=True,
                            subsample=cfg.get("fitness_subsample"), n_jobs=cfg.get("n_jobs", 1),
                            n_estimators=cfg.get("fitness_n_estimators"),
                            ctx_tr=ctx_tr, ctx_va=ctx_va, groups_tr=combo_tr, groups_va=combo_va, unit=unit)


def _filter_phase(dproc, feature_names, cfg, seed, threshold=None):
    tr = dproc[dproc.split == "train"]
    thr = cfg["pcc_threshold"] if threshold is None else threshold
    if thr is None or thr >= 1.0:                          # 'no filter' option for sensitivity
        return list(feature_names), [], []
    return FL.pcc_mi_filter(tr[feature_names].to_numpy(float), tr["ct"].to_numpy(float),
                            feature_names, threshold=thr, seed=seed)


def _run_search(algo, search_feats, feature_names, ev, cfg, seed, ga_overrides=None):
    """Run a single-objective metaheuristic over `search_feats` with the weighted fitness."""
    n_total = len(feature_names)
    sub_idx = np.array([feature_names.index(f) for f in search_feats])

    def to_full(mask_sub):
        m = np.zeros(n_total, bool)
        m[sub_idx[np.asarray(mask_sub, bool)]] = True
        return m

    wf = WeightedFitness(ev, lam=cfg["lambda"], n_total=n_total, n_search=len(search_feats))
    fit_fn = lambda ms: wf(to_full(ms))
    g = dict(cfg["ga"])
    if ga_overrides:
        g.update(ga_overrides)
    if algo == "GA":
        opt = BinaryGA(len(search_feats), fit_fn, pop_size=g["pop_size"], n_gen=g["n_gen"],
                       pc=g["pc"], pm=g["pm"], n_elite=g["n_elite"], seed=seed,
                       patience=g.get("patience"))
    elif algo == "BPSO":
        opt = BinaryPSO(len(search_feats), fit_fn, pop_size=g["pop_size"], n_iter=g["n_gen"], seed=seed)
    elif algo == "BGWO":
        opt = BinaryGWO(len(search_feats), fit_fn, pop_size=g["pop_size"], n_iter=g["n_gen"], seed=seed)
    else:
        raise ValueError(algo)
    res = opt.run()
    full = to_full(res["best_mask"])
    comp = wf.components(full)
    return [f for f, b in zip(feature_names, full) if b], res, comp


def run_method(name, dproc, feature_names, cfg, seed=0, threshold=None, ga_overrides=None,
               lam=None):
    feature_names = list(feature_names)
    cfg = dict(cfg)
    if lam is not None:
        cfg["lambda"] = lam
    extra = {}
    with Timer() as T:
        ev = _evaluator(dproc, feature_names, cfg, seed)
        base_mra = ev.mra(np.ones(len(feature_names), bool))
        extra["baseline_val_mra"] = base_mra

        if name == "ALL":
            selected = list(feature_names)

        elif name == "FILTER":
            selected, removed, log = _filter_phase(dproc, feature_names, cfg, seed, threshold)
            extra.update(removed=removed, filter_log=log)

        elif name in ("GA", "TSFGA", "BPSO", "BGWO"):
            if name == "GA":
                search = list(feature_names)
            else:
                search, removed, log = _filter_phase(dproc, feature_names, cfg, seed, threshold)
                extra.update(removed=removed, filter_log=log, n_after_filter=len(search))
            algo = "GA" if name in ("GA", "TSFGA") else name
            selected, res, comp = _run_search(algo, search, feature_names, ev, cfg, seed, ga_overrides)
            extra.update(history=res["history"], best_fitness=res["best_fitness"],
                         generations=res["generations"], fitness_components=comp)

        elif name == "NSGA2":
            search, removed, log = _filter_phase(dproc, feature_names, cfg, seed, threshold)
            extra.update(removed=removed, n_after_filter=len(search))
            n_total = len(feature_names)
            sub_idx = np.array([feature_names.index(f) for f in search])

            def obj(ms):
                m = np.zeros(n_total, bool)
                m[sub_idx[np.asarray(ms, bool)]] = True
                return int(m.sum()), ev.mra(m)
            g = dict(cfg["ga"])
            if ga_overrides:
                g.update(ga_overrides)
            opt = NSGA2(len(search), obj, pop_size=g["pop_size"], n_gen=g["n_gen"], seed=seed)
            res = opt.run()
            pareto_full = []
            for pm in res["pareto_masks"]:
                m = np.zeros(n_total, bool)
                m[sub_idx[pm]] = True
                pareto_full.append(m)
            pick_mask, pick_obj = pick_from_pareto(pareto_full, res["pareto_objs"], n_total,
                                                   lam=cfg["lambda"], mode=cfg.get("nsga2_pick", "knee"))
            selected = [f for f, b in zip(feature_names, pick_mask) if b]
            extra.update(history=res["history"], pareto=res["pareto_objs"], picked=pick_obj,
                         pareto_features=[[f for f, b in zip(feature_names, m) if b] for m in pareto_full])

        elif name in ("mRMR", "MI", "RFE"):
            tr = dproc[dproc.split == "train"]
            Xtr, ytr = tr[feature_names].to_numpy(float), tr["ct"].to_numpy(float)
            if name == "mRMR":
                ranking = FL.mrmr_ranking(Xtr, ytr, feature_names, seed=seed)
            elif name == "MI":
                ranking, _ = FL.mi_ranking(Xtr, ytr, feature_names, seed=seed)
            else:
                ranking = WR.rfe_ranking(Xtr, ytr, feature_names, seed=seed, step=cfg.get("rfe_step", 2))
            selected, k, curve, kbeat = FL.best_k_by_validation(ranking, feature_names, ev,
                                                                 k_max=cfg.get("rank_k_max"),
                                                                 baseline_mra=base_mra)
            extra.update(ranking=ranking, curve=curve, best_k=k, min_k_beating_baseline=kbeat)

        elif name == "DDA":
            tr = dproc[dproc.split == "train"]
            selected, ranking, curve = WR.dda_stepwise(tr[feature_names].to_numpy(float),
                                                       tr["ct"].to_numpy(float), feature_names, ev,
                                                       max_k=cfg.get("rank_k_max"))
            extra.update(ranking=ranking, curve=curve)

        elif name == "PFI-SBS":
            tr = dproc[dproc.split == "train"]
            selected, ranking, curve = WR.pfi_sbs(tr[feature_names].to_numpy(float),
                                                  tr["ct"].to_numpy(float), feature_names, ev, seed=seed)
            extra.update(ranking=ranking, curve=curve)

        elif name == "LASSO":
            tr = dproc[dproc.split == "train"]
            selected, alpha = WR.lasso_select(tr[feature_names].to_numpy(float),
                                              tr["ct"].to_numpy(float), feature_names, seed=seed)
            extra.update(alpha=alpha)

        elif name == "Boruta":
            tr = dproc[dproc.split == "train"]
            selected, tentative = WR.boruta_select(tr[feature_names].to_numpy(float),
                                                   tr["ct"].to_numpy(float), feature_names, seed=seed,
                                                   n_iter=cfg.get("boruta_iter", 30))
            extra.update(tentative=tentative)
        else:
            raise ValueError(f"unknown method {name}")

    extra["val_mra_selected"] = ev.mra(_mask(selected, feature_names)) if selected else 0.0
    return dict(method=name, selected=list(selected), n_selected=len(selected),
                time_s=T.elapsed, n_evals=ev.n_evals, extra=extra)
