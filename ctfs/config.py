"""Experiment configuration presets.

QUICK : small synthetic run used to validate the whole pipeline end-to-end (1 CPU, ~30-40 min).
FULL  : manuscript-scale settings (P=80, G=200, 6 processes, >=10 seeds) for the real fab data.

Override any key from the CLI with --set key=value (nested keys with dots, e.g. --set ga.pop_size=40).
"""
from __future__ import annotations

import copy

QUICK = dict(
    name="quick",
    data=dict(source="synthetic", path=None, processes=3, products_per_process=3, ops_per_product=3,
              records_per_combo=300, seed=0, noise_sd=0.10, drift=0.15),
    dataset2=dict(name="FabB", processes=3, products_per_process=2, ops_per_product=3,
                  records_per_combo=300, seed=17, noise_sd=0.18, nonlinearity=1.6, drift=0.3),
    split=dict(mode="random", ratios=(0.5, 0.25, 0.25), seed=0),
    fitness_regressor="rf", fitness_unit="combo", fitness_context="combo_onehot",
    fitness_subsample=None, fitness_n_estimators=20, n_jobs=1,
    eval_regressor="rf", eval_fast=True, eval_unit="combo",
    pcc_threshold=0.8, **{"lambda": 2.0},
    ga=dict(pop_size=16, n_gen=10, pc=0.5, pm=0.1, n_elite=2, patience=None),
    nsga2_pick="knee",
    rank_k_max=None, rfe_step=3, boruta_iter=20,
    seeds=[0, 1, 2],
    workers=1,                      # parallel (process, method, seed) jobs; -1 = all cores
    methods=["ALL", "FILTER", "GA", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS",
             "BPSO", "BGWO", "NSGA2", "Boruta", "LASSO", "RFE"],
    # quick preset keeps the sensitivity grid small (1 CPU); the full preset sweeps P, pc, pm too
    sensitivity=dict(seeds=[0, 1],
                     grid={"lambda": [0.5, 2.0, 5.0],
                           "pcc_threshold": [0.7, 0.8, 1.0]}),
    temporal=dict(methods=["ALL", "FILTER", "TSFGA", "DDA", "PFI-SBS"], seeds=[0]),
    transfer=dict(regressors=["rf", "lgbm", "mlp", "svr", "dt"]),
    dataset2_methods=["ALL", "FILTER", "TSFGA", "PFI-SBS"], dataset2_seeds=[0, 1],
    interpret=dict(n_shap=300),
)

FULL = copy.deepcopy(QUICK)
FULL.update(
    name="full",
    # synthetic Fab A at full scale; pass --data path/to/fab.csv to switch to the real extract
    data=dict(source="synthetic", path=None, processes=6, products_per_process=3, ops_per_product=5,
              records_per_combo=300, seed=0, noise_sd=0.10, drift=0.15),
    dataset2=dict(name="FabB", processes=6, products_per_process=3, ops_per_product=5,
                  records_per_combo=300, seed=17, noise_sd=0.18, nonlinearity=1.6, drift=0.3),
    n_jobs=1, workers=-1, eval_fast=True, fitness_unit="combo", fitness_subsample=None, fitness_n_estimators=20,
    ga=dict(pop_size=80, n_gen=200, pc=0.5, pm=0.1, n_elite=2, patience=40),
    rfe_step=1, boruta_iter=50,
    seeds=list(range(10)),
    sensitivity=dict(seeds=[0, 1, 2],
                     grid={"lambda": [0.5, 1.0, 2.0, 5.0, 10.0],
                           "pcc_threshold": [0.7, 0.8, 0.9, 1.0],
                           "ga.pop_size": [40, 80, 120],
                           "ga.pc": [0.3, 0.5, 0.8],
                           "ga.pm": [0.05, 0.1, 0.2]}),
    temporal=dict(methods=["ALL", "FILTER", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS", "NSGA2"],
                  seeds=list(range(5))),
    dataset2_methods=["ALL", "FILTER", "GA", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS", "NSGA2"],
    dataset2_seeds=list(range(5)),
    interpret=dict(n_shap=2000),
)

# alias kept for backward compatibility
FULL_SIM = copy.deepcopy(FULL)
FULL_SIM["name"] = "full_sim"

PRESETS = dict(quick=QUICK, full=FULL, full_sim=FULL_SIM)


def set_nested(cfg: dict, dotted: str, value):
    keys = dotted.split(".")
    d = cfg
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = value


def get_nested(cfg: dict, dotted: str):
    d = cfg
    for k in dotted.split("."):
        d = d[k]
    return d


def parse_value(v: str):
    if v[:1] in "[{":
        import json
        return json.loads(v)
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("none", "null"):
        return None
    if "," in v:
        return [parse_value(x) for x in v.split(",")]
    return v
