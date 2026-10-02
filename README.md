# TSFGA — Two-stage feature selection for lot cycle-time prediction

Code, simulated-fab benchmark and results accompanying

> S. Song, B.K. Lee, *Two-stage feature selection for lot cycle-time prediction in semiconductor wafer fabrication:
> a real-fab case study with simulation-based validation*, submitted to **Advanced Engineering Informatics**, 2026.

TSFGA removes redundant features with a Pearson-correlation / mutual-information filter and then searches the
remaining features with a genetic algorithm whose fitness trades feature reduction against mean relative accuracy
(MRA). This repository contains

* `ctfs/` — the method, 13 comparison methods (filter, wrapper, embedded, swarm-based variants), the evaluation
  protocol (product–operation units, random / chronological splits, Wilcoxon, Friedman + Nemenyi), and the
  **simulated-fab generator with known cycle-time drivers**;
* `results/full/` — every table and figure of the simulation study in the paper (CSV + Markdown + PNG), including
  the raw per-unit scores (`main/per_combo.csv`) and the selected subsets of every run (`main/selections.json`);
* `tools/` — scripts that rebuild the manuscript tables from the results and compute statistics for external
  (e.g. real-fab) results;
* `paper/equations/` — LaTeX sources of the manuscript equations.

The real fab data (577,236 wafer-lot records) are confidential and are **not** included; the loader accepts any
dataset with the schema below.

## Install

```bash
pip install -r requirements.txt        # Python ≥ 3.10
```

## Reproduce the simulation study

```bash
# smoke test (≈2 min, 1 core)
python run_experiments.py --preset quick --exp main stats --out results/smoke \
    --set data.processes=2 data.products_per_process=2 data.ops_per_product=2 data.records_per_combo=120 \
          ga.pop_size=6 ga.n_gen=2 seeds=0,1 methods=ALL,FILTER,TSFGA,mRMR

# full study as in the paper (6 processes, P=80, G=200, 10 seeds, 13 methods; ≈400 core-hours)
python run_experiments.py --preset full --exp all --out results/full --set workers=-1
```

Stages: `main` (ablation + 13-method comparison, Tables 8–10), `stats` (Wilcoxon / Friedman / Nemenyi, Table 11,
Fig. 9), `sensitivity` (λ, τ, GA parameters; Table 12, B.1), `temporal` (chronological split; Table 13),
`transfer`, `dataset2` (second fab instance), `interpret` (SHAP, selection frequency, driver recovery; Table 14),
`report`. Every (process, method, seed) job is cached, so an interrupted run resumes with the same command.
`run_full.ipynb` wraps the same commands for Jupyter users; `run_full.bat` is a Windows launcher.

The statistics reported in the paper exclude the multi-objective NSGA-II run (`results/full/E3_stats_without_NSGA2/`);
the complete 14-method results are in `results/full/E3_stats/`.

## Run on your own fab data

One row per lot and operation step (CSV / Parquet / XLSX):

| column | meaning |
|---|---|
| `lot_id`, `product`, `operation`, `process` | identifiers; `process` is the major process used to split the data |
| `timestamp` | step start time (used for the chronological split) |
| `ct` | cycle time of the step — the target |
| all other columns | candidate features |

```bash
python run_experiments.py --preset full --data my_fab.csv --exp all --out results/my_fab
python tools/real_data_stats.py per_unit_results.csv results/my_fab_stats   # statistics for results produced elsewhere
```

`tools/export_synthetic.py` writes a synthetic dataset in this schema as a template.

## Package layout

```
ctfs/data.py            simulated fab (queueing-based CT model, 54 features, redundant proxies, drift), loader, splits
ctfs/filters.py         PCC/MI filter (stage 1), MI, mRMR, best-k selection
ctfs/ga.py              GA (stage 2): roulette + elitism, HUX crossover, bit-flip mutation, early stopping
ctfs/metaheuristics.py  binary PSO, binary GWO (bGWO2), NSGA-II
ctfs/wrappers.py        DDA-style stepwise, PFI-SBS, RFE, LASSO, Boruta
ctfs/methods.py         uniform interface for all methods
ctfs/evaluator.py       random forest, memoised fitness, per-unit evaluation
ctfs/metrics.py         MRA, PFR, CFS, MAE, RMSE, R², Jaccard, driver recovery
ctfs/stats.py           Wilcoxon, Friedman + Nemenyi, CD diagram
ctfs/experiments.py     experiment orchestration and report
ctfs/config.py          presets (quick / full) and overrides
```

## License

MIT — see `LICENSE`. Please cite the paper (see `CITATION.cff`) if you use the code or the benchmark.
