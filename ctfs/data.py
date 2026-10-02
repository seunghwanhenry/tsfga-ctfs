"""
Data layer for cycle-time (CT) feature-selection experiments.

Two entry points:
  * make_synthetic_fab(...)  -> synthetic wafer-lot transaction data with KNOWN relevant features
  * load_real(...)           -> your real MES/SCM/AMHS extract (see README for schema)

Required schema (both sources):
  lot_id, product, operation, process, timestamp, ct, <feature columns...>

`process` is the major process (lithography, implantation, ...).
Feature selection is run per `process`; evaluation is per (product, operation) combo,
which mirrors the manuscript's Section III.B protocol.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

META_COLS = ["lot_id", "product", "operation", "process", "timestamp", "ct"]

PROCESSES = ["lithography", "implantation", "etching",
             "metalization", "deposition", "planarization"]


# --------------------------------------------------------------------------- #
# Synthetic fab generator
# --------------------------------------------------------------------------- #
def _feature_catalog():
    """Return the 54-feature catalog (4 categories) mimicking Table I of the manuscript.

    Each entry: (name, category)
    """
    cat = []
    # Wafer lot characteristics (6)
    cat += [(f, "lot") for f in
            ["priority", "lot_size", "n_layers", "hot_lot", "rework_flag", "lot_age_days"]]
    # Order characteristics (3)
    cat += [(f, "order") for f in ["tardiness", "due_pct", "product_mix"]]
    # Workshop condition (19)
    cat += [(f, "workshop") for f in
            ["wip_fab", "wip_area", "wip_process", "wip_upstream", "wip_downstream",
             "wip_ratio", "wip_fab_7d_avg", "amhs_load_avg", "amhs_load_min", "amhs_load_max",
             "amhs_queue", "weekend", "holiday", "shift", "day_of_week", "hour",
             "lots_released_24h", "lots_out_24h", "moves_per_hour"]]
    # Machine state (26)
    cat += [(f, "machine") for f in
            ["util_avg", "util_min", "util_max", "perf_avg", "perf_min", "perf_max",
             "queue_len_avg", "queue_len_min", "queue_len_max", "n_machines",
             "n_machines_down", "n_machines_pm", "mttr", "mtbf", "setup_time",
             "batch_size", "recipe_changes", "oee", "availability", "quality_rate",
             "tool_age", "chamber_count", "loadport_wait", "dispatch_score",
             "alarm_count_24h", "throughput_7d"]]
    assert len(cat) == 54, len(cat)
    return cat


FEATURE_CATALOG = _feature_catalog()
FEATURE_NAMES = [f for f, _ in FEATURE_CATALOG]
FEATURE_CATEGORY = dict(FEATURE_CATALOG)


def make_synthetic_fab(name: str = "FabA",
                       processes=None,
                       products_per_process: int = 3,
                       ops_per_product: int = 4,
                       records_per_combo: int = 300,
                       start: str = "2023-05-01",
                       days: int = 90,
                       noise_sd: float = 0.12,
                       nonlinearity: float = 1.0,
                       drift: float = 0.15,
                       seed: int = 0):
    """Generate a synthetic wafer-lot transaction dataset with a queueing-inspired CT model.

    Ground truth (per process) is a subset of ~8-11 features that drive CT through
    a nonlinear waiting-time model; several other features are deliberately
    redundant (|r| > 0.8 with a true feature) and the rest are pure noise.

    Returns
    -------
    df   : DataFrame with META_COLS + 54 features
    meta : dict with 'true_features' (per process), 'redundant_groups', 'noise_features'
    """
    rng = np.random.default_rng(seed)
    processes = list(processes or PROCESSES)
    t0 = pd.Timestamp(start)

    # process-specific structure: which optional drivers matter and how strong
    proc_cfg = {}
    for i, p in enumerate(processes):
        proc_cfg[p] = dict(
            base_wait=rng.uniform(2.0, 6.0),          # hours
            util_exp=rng.uniform(0.6, 1.1) * nonlinearity,
            queue_coef=rng.uniform(0.02, 0.08),
            wip_coef=rng.uniform(0.3, 0.9),
            prio_coef=rng.uniform(0.25, 0.5),
            weekend_coef=rng.uniform(0.15, 0.45),
            layers_coef=rng.uniform(0.0, 0.25) if p in ("lithography", "etching") else 0.0,
            batch_coef=rng.uniform(0.1, 0.35) if p in ("deposition", "implantation") else 0.0,
            amhs_coef=rng.uniform(0.1, 0.4),
            down_coef=rng.uniform(0.1, 0.3),
            setup_coef=rng.uniform(0.0, 0.2) if p in ("metalization", "planarization") else 0.0,
        )

    rows = []
    for p in processes:
        c = proc_cfg[p]
        for pi in range(products_per_process):
            product = f"P{pi+1:02d}"
            n_layers_prod = int(rng.integers(20, 45))
            for oi in range(ops_per_product):
                operation = f"{p[:4].upper()}-{oi+1:02d}"
                base_pt = rng.uniform(0.8, 3.0)              # processing hours
                n_machines_base = int(rng.integers(2, 9))
                n = records_per_combo
                # timestamps uniformly across the horizon
                ts_hours = np.sort(rng.uniform(0, days * 24, n))
                ts = t0 + pd.to_timedelta(ts_hours, unit="h")
                frac = ts_hours / (days * 24)               # 0..1 progress (for drift)

                # ---- true drivers -------------------------------------------------
                priority = rng.choice([1, 2, 3], size=n, p=[0.15, 0.6, 0.25])
                lot_size = np.clip(np.round(rng.normal(25, 1.5, n)), 12, 25)
                n_layers = n_layers_prod + rng.integers(-2, 3, n)
                util_avg = np.clip(rng.beta(5, 3, n) * 0.85 + drift * 0.12 * frac, 0.25, 0.88)
                queue_len_avg = np.clip(rng.gamma(2.0, 3.0, n) * (0.5 + util_avg), 0, None)
                wip_process = np.clip(rng.normal(120, 25, n) * (0.6 + util_avg) + drift * 30 * frac, 20, None)
                weekend = (ts.dayofweek >= 5).astype(int)
                holiday = (rng.random(n) < 0.03).astype(int)
                amhs_load_avg = np.clip(rng.beta(4, 3, n), 0.05, 0.99)
                n_machines = np.clip(n_machines_base + rng.integers(-1, 2, n), 1, None)
                n_machines_down = np.clip(rng.poisson(0.4, n), 0, n_machines - 1)
                batch_size = rng.choice([1, 2, 4, 6], size=n)
                setup_time = np.clip(rng.gamma(2, 0.25, n), 0, None)

                # ---- queueing-inspired CT ----------------------------------------
                proc_time = base_pt * (lot_size / 25.0) * (1 + c["layers_coef"] * (n_layers - 30) / 30)
                eff_util = np.clip(util_avg * n_machines / np.maximum(n_machines - n_machines_down, 1), 0.25, 0.88)
                wait = (c["base_wait"]
                        * (eff_util / (1 - eff_util)) ** c["util_exp"]
                        * (1 + c["queue_coef"] * queue_len_avg)
                        * (1 + c["wip_coef"] * (wip_process / 120.0 - 1))
                        * (1 - c["prio_coef"] * (priority == 1) + 0.5 * c["prio_coef"] * (priority == 3))
                        * (1 + c["weekend_coef"] * weekend + 0.6 * holiday)
                        * (1 + c["amhs_coef"] * (amhs_load_avg - 0.5))
                        * (1 + c["batch_coef"] * (batch_size - 1) / 5)
                        * (1 + c["setup_coef"] * setup_time)
                        * (1 + c["down_coef"] * n_machines_down))
                ct = (proc_time + wait) * np.exp(rng.normal(0, noise_sd, n))
                ct = np.clip(ct, 0.2, None)

                # ---- redundant features (|r| > 0.8 with true drivers) -------------
                util_min = np.clip(util_avg - rng.uniform(0.02, 0.10, n), 0, 1)
                util_max = np.clip(util_avg + rng.uniform(0.01, 0.06, n), 0, 1)
                queue_len_min = np.clip(queue_len_avg - rng.gamma(1.5, 1.0, n), 0, None)
                queue_len_max = queue_len_avg + rng.gamma(1.5, 1.0, n)
                wip_fab = wip_process * 8 + rng.normal(0, 60, n)
                wip_area = wip_process * 2.2 + rng.normal(0, 25, n)
                wip_fab_7d_avg = wip_fab * 0.9 + rng.normal(0, 40, n)
                amhs_load_min = np.clip(amhs_load_avg - rng.uniform(0.02, 0.12, n), 0, 1)
                amhs_load_max = np.clip(amhs_load_avg + rng.uniform(0.02, 0.08, n), 0, 1)
                availability = np.clip(1 - n_machines_down / n_machines - rng.uniform(0, 0.03, n), 0, 1)
                oee = availability * util_avg * rng.uniform(0.95, 1.0, n)

                # ---- weakly-related / noise features -------------------------------
                fdict = dict(
                    priority=priority, lot_size=lot_size, n_layers=n_layers,
                    hot_lot=(priority == 1).astype(int) * (rng.random(n) < 0.8),
                    rework_flag=(rng.random(n) < 0.05).astype(int),
                    lot_age_days=rng.gamma(3, 6, n),
                    tardiness=rng.normal(0, 2, n), due_pct=rng.uniform(0, 1, n),
                    product_mix=rng.uniform(0.1, 0.6, n),
                    wip_fab=wip_fab, wip_area=wip_area, wip_process=wip_process,
                    wip_upstream=rng.normal(80, 20, n), wip_downstream=rng.normal(80, 20, n),
                    wip_ratio=wip_process / np.maximum(wip_fab, 1),
                    wip_fab_7d_avg=wip_fab_7d_avg,
                    amhs_load_avg=amhs_load_avg, amhs_load_min=amhs_load_min, amhs_load_max=amhs_load_max,
                    amhs_queue=rng.poisson(3, n), weekend=weekend, holiday=holiday,
                    shift=rng.integers(0, 3, n), day_of_week=ts.dayofweek.values, hour=ts.hour.values,
                    lots_released_24h=rng.poisson(40, n), lots_out_24h=rng.poisson(40, n),
                    moves_per_hour=rng.normal(300, 40, n),
                    util_avg=util_avg, util_min=util_min, util_max=util_max,
                    perf_avg=rng.uniform(0.7, 1.0, n), perf_min=rng.uniform(0.5, 0.8, n),
                    perf_max=rng.uniform(0.9, 1.0, n),
                    queue_len_avg=queue_len_avg, queue_len_min=queue_len_min, queue_len_max=queue_len_max,
                    n_machines=n_machines, n_machines_down=n_machines_down,
                    n_machines_pm=rng.poisson(0.3, n), mttr=rng.gamma(2, 1.5, n), mtbf=rng.gamma(4, 20, n),
                    setup_time=setup_time, batch_size=batch_size, recipe_changes=rng.poisson(2, n),
                    oee=oee, availability=availability, quality_rate=rng.uniform(0.9, 1.0, n),
                    tool_age=rng.uniform(0, 10, n), chamber_count=rng.integers(1, 5, n),
                    loadport_wait=rng.gamma(1.5, 0.3, n), dispatch_score=rng.normal(0, 1, n),
                    alarm_count_24h=rng.poisson(1.5, n), throughput_7d=rng.normal(500, 50, n),
                )
                block = pd.DataFrame(fdict)[FEATURE_NAMES]
                block.insert(0, "ct", ct)
                block.insert(0, "timestamp", ts)
                block.insert(0, "process", p)
                block.insert(0, "operation", operation)
                block.insert(0, "product", product)
                block.insert(0, "lot_id", [f"L{rng.integers(1e6):06d}" for _ in range(n)])
                rows.append(block)

    df = pd.concat(rows, ignore_index=True)

    true_common = ["priority", "lot_size", "util_avg", "queue_len_avg", "wip_process",
                   "weekend", "holiday", "amhs_load_avg", "n_machines", "n_machines_down"]
    true_features = {}
    for p in processes:
        c = proc_cfg[p]
        tf = list(true_common)
        if c["layers_coef"] > 0:
            tf.append("n_layers")
        if c["batch_coef"] > 0:
            tf.append("batch_size")
        if c["setup_coef"] > 0:
            tf.append("setup_time")
        true_features[p] = tf
    meta = dict(
        name=name,
        true_features=true_features,
        redundant_groups=[["util_avg", "util_min", "util_max", "oee"],
                          ["queue_len_avg", "queue_len_min", "queue_len_max"],
                          ["wip_process", "wip_fab", "wip_area", "wip_fab_7d_avg"],
                          ["amhs_load_avg", "amhs_load_min", "amhs_load_max"],
                          ["n_machines_down", "availability"]],
        feature_names=FEATURE_NAMES,
        feature_category=FEATURE_CATEGORY,
        proc_cfg=proc_cfg,
    )
    # a redundant proxy (e.g. util_min) counts as recovering its group's true driver
    meta["equivalence"] = {f: g[0] for g in meta["redundant_groups"] for f in g}
    return df, meta


# --------------------------------------------------------------------------- #
# Real data
# --------------------------------------------------------------------------- #
def load_real(path: str, feature_cols=None) -> tuple[pd.DataFrame, dict]:
    """Load a real extract. Accepts .csv / .parquet / .xlsx.

    The file must contain META_COLS. Everything else is treated as a feature
    unless `feature_cols` is given.
    """
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    elif path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    missing = [c for c in META_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    feats = list(feature_cols) if feature_cols else [c for c in df.columns if c not in META_COLS]
    meta = dict(name=path, true_features=None, feature_names=feats,
                feature_category={f: "unknown" for f in feats})
    return df, meta


# --------------------------------------------------------------------------- #
# Splitting
# --------------------------------------------------------------------------- #
def assign_splits(df: pd.DataFrame, mode: str = "random",
                  ratios=(0.5, 0.25, 0.25), seed: int = 0) -> pd.DataFrame:
    """Add a `split` column in {train, val, test} per (process, product, operation) combo.

    mode='random'   : the manuscript's protocol (random 50/25/25 within each combo)
    mode='temporal' : chronological 50/25/25 within each combo (no look-ahead leakage)
    """
    assert abs(sum(ratios) - 1) < 1e-9
    rng = np.random.default_rng(seed)
    out = df.copy()
    out["split"] = "train"
    for _, idx in out.groupby(["process", "product", "operation"]).indices.items():
        idx = np.asarray(idx)
        if mode == "random":
            order = rng.permutation(idx)
        elif mode == "temporal":
            order = idx[np.argsort(out.loc[idx, "timestamp"].values)]
        else:
            raise ValueError(mode)
        n = len(order)
        n_tr = int(round(ratios[0] * n))
        n_va = int(round(ratios[1] * n))
        out.loc[order[:n_tr], "split"] = "train"
        out.loc[order[n_tr:n_tr + n_va], "split"] = "val"
        out.loc[order[n_tr + n_va:], "split"] = "test"
    return out


def process_frame(df: pd.DataFrame, process: str) -> pd.DataFrame:
    return df[df["process"] == process].reset_index(drop=True)


def xy(df: pd.DataFrame, features, split=None):
    d = df if split is None else df[df["split"] == split]
    return d[list(features)].to_numpy(dtype=float), d["ct"].to_numpy(dtype=float)
