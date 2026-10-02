#!/usr/bin/env python
"""CLI for the CT feature-selection experiment suite.

Examples
--------
# end-to-end synthetic validation (quick preset)
python run_experiments.py --preset quick --exp all --out results/quick

# real data, manuscript-scale
python run_experiments.py --preset full --data data/fab.csv --exp main --out results/full
python run_experiments.py --preset full --data data/fab.csv --exp stats sensitivity temporal transfer interpret report --out results/full

# override any config key
python run_experiments.py --preset full --set ga.pop_size=40 ga.n_gen=100 seeds=0,1,2,3,4
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctfs import experiments as E                     # noqa: E402
from ctfs.config import PRESETS, parse_value, set_nested  # noqa: E402

EXPS = ["main", "stats", "sensitivity", "temporal", "transfer", "dataset2", "interpret", "report"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="quick", choices=list(PRESETS))
    ap.add_argument("--exp", nargs="+", default=["all"], help=f"{EXPS} or 'all'")
    ap.add_argument("--data", default=None, help="path to real data (csv/parquet/xlsx)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--set", nargs="*", default=[], help="config overrides key=value")
    a = ap.parse_args()

    cfg = copy.deepcopy(PRESETS[a.preset])
    if a.data:
        cfg["data"] = dict(source="real", path=a.data, processes=None, seed=0)
    for kv in a.set:
        k, v = kv.split("=", 1)
        set_nested(cfg, k, parse_value(v))
    out = a.out or os.path.join("results", cfg["name"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=1, default=str)

    exps = EXPS if a.exp == ["all"] else a.exp
    t0 = time.time()
    for e in exps:
        E.log(f"===== {e} =====")
        if e == "main":
            E.run_main(cfg, out)
        elif e == "stats":
            E.run_stats(cfg, out)
        elif e == "sensitivity":
            E.run_sensitivity(cfg, out)
        elif e == "temporal":
            E.run_temporal(cfg, out)
        elif e == "transfer":
            E.run_transfer(cfg, out)
        elif e == "dataset2":
            E.run_dataset2(cfg, out)
        elif e == "interpret":
            E.run_interpret(cfg, out)
        elif e == "report":
            E.write_report(cfg, out)
        else:
            raise SystemExit(f"unknown experiment {e}")
        E.log(f"===== {e} done ({(time.time()-t0)/60:.1f} min elapsed) =====")


if __name__ == "__main__":
    main()
