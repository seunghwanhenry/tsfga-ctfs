"""Competing binary metaheuristics with the same fitness interface as BinaryGA.

* BinaryPSO  : Kennedy & Eberhart (1997) sigmoid-transfer BPSO
* BinaryGWO  : Emary et al. (2016) binary grey wolf optimizer (sigmoid transfer)
* NSGA2      : Deb et al. (2002) with objectives (min #features, max MRA);
               uses the same HUX + bit-flip operators as the GA for a fair comparison.
"""
from __future__ import annotations

import numpy as np

from .ga import hux_crossover


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _ensure_nonempty(mask, rng):
    if not mask.any():
        mask[rng.integers(len(mask))] = True
    return mask


class BinaryPSO:
    def __init__(self, n_bits, fitness_fn, pop_size=80, n_iter=200, w=0.9, c1=2.0, c2=2.0,
                 vmax=6.0, seed=0):
        self.n, self.fit, self.P, self.T = n_bits, fitness_fn, pop_size, n_iter
        self.w, self.c1, self.c2, self.vmax = w, c1, c2, vmax
        self.rng = np.random.default_rng(seed)

    def run(self):
        rng = self.rng
        X = rng.random((self.P, self.n)) < 0.5
        for i in range(self.P):
            _ensure_nonempty(X[i], rng)
        V = rng.uniform(-1, 1, (self.P, self.n))
        fit = np.array([self.fit(x) for x in X])
        pbest, pbest_fit = X.copy(), fit.copy()
        g = int(np.argmax(fit))
        gbest, gbest_fit = X[g].copy(), float(fit[g])
        hist = [dict(gen=0, best=gbest_fit, mean=float(fit.mean()), n_selected=int(gbest.sum()))]
        for t in range(1, self.T + 1):
            w = self.w - (self.w - 0.4) * t / self.T           # linearly decreasing inertia
            r1, r2 = rng.random((self.P, self.n)), rng.random((self.P, self.n))
            V = w * V + self.c1 * r1 * (pbest.astype(float) - X) + self.c2 * r2 * (gbest.astype(float) - X)
            V = np.clip(V, -self.vmax, self.vmax)
            X = rng.random((self.P, self.n)) < _sigmoid(V)
            for i in range(self.P):
                _ensure_nonempty(X[i], rng)
            fit = np.array([self.fit(x) for x in X])
            imp = fit > pbest_fit
            pbest[imp], pbest_fit[imp] = X[imp], fit[imp]
            g = int(np.argmax(pbest_fit))
            if pbest_fit[g] > gbest_fit:
                gbest, gbest_fit = pbest[g].copy(), float(pbest_fit[g])
            hist.append(dict(gen=t, best=gbest_fit, mean=float(fit.mean()), n_selected=int(gbest.sum())))
        return dict(best_mask=gbest, best_fitness=gbest_fit, history=hist, generations=self.T)


class BinaryGWO:
    """Binary grey wolf optimizer, bGWO2 variant of Emary et al. (2016):
    the three leader-guided continuous positions are averaged and squashed with a
    sigmoid transfer function, then sampled to a binary vector."""

    def __init__(self, n_bits, fitness_fn, pop_size=80, n_iter=200, seed=0):
        self.n, self.fit, self.P, self.T = n_bits, fitness_fn, pop_size, n_iter
        self.rng = np.random.default_rng(seed)

    def run(self):
        rng = self.rng
        X = rng.random((self.P, self.n)) < 0.5
        for i in range(self.P):
            _ensure_nonempty(X[i], rng)
        fit = np.array([self.fit(x) for x in X])
        order = np.argsort(-fit)
        leaders = [X[order[k]].copy() for k in range(3)]
        lfit = [float(fit[order[k]]) for k in range(3)]
        hist = [dict(gen=0, best=lfit[0], mean=float(fit.mean()), n_selected=int(leaders[0].sum()))]
        for t in range(1, self.T + 1):
            a = 2 - 2 * t / self.T
            Xf = X.astype(float)
            newX = np.empty_like(X)
            for i in range(self.P):
                xs = []
                for leader in leaders:
                    A = 2 * a * rng.random(self.n) - a
                    C = 2 * rng.random(self.n)
                    Dl = np.abs(C * leader - Xf[i])
                    xs.append(leader - A * Dl)
                xc = (xs[0] + xs[1] + xs[2]) / 3.0
                prob = _sigmoid(10.0 * (xc - 0.5))
                newX[i] = _ensure_nonempty(rng.random(self.n) < prob, rng)
            X = newX
            fit = np.array([self.fit(x) for x in X])
            # update alpha/beta/delta with the best of the union (elitist leaders)
            cand = list(zip(list(fit), [x.copy() for x in X])) + list(zip(lfit, leaders))
            cand.sort(key=lambda z: -z[0])
            uniq, seen = [], set()
            for f, x in cand:
                k = x.tobytes()
                if k not in seen:
                    seen.add(k)
                    uniq.append((f, x))
                if len(uniq) == 3:
                    break
            lfit, leaders = [float(u[0]) for u in uniq], [u[1] for u in uniq]
            hist.append(dict(gen=t, best=lfit[0], mean=float(fit.mean()), n_selected=int(leaders[0].sum())))
        return dict(best_mask=leaders[0], best_fitness=lfit[0], history=hist, generations=self.T)


# --------------------------------------------------------------------------- #
# NSGA-II
# --------------------------------------------------------------------------- #
def fast_non_dominated_sort(F):
    """F: (n, m) objective matrix to MINIMISE. Returns list of fronts (lists of indices)."""
    n = len(F)
    S = [[] for _ in range(n)]
    cnt = np.zeros(n, int)
    fronts = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if np.all(F[p] <= F[q]) and np.any(F[p] < F[q]):
                S[p].append(q)
            elif np.all(F[q] <= F[p]) and np.any(F[q] < F[p]):
                cnt[p] += 1
        if cnt[p] == 0:
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in S[p]:
                cnt[q] -= 1
                if cnt[q] == 0:
                    nxt.append(q)
        i += 1
        fronts.append(nxt)
    return fronts[:-1]


def crowding_distance(F, idx):
    idx = list(idx)
    d = np.zeros(len(idx))
    if len(idx) <= 2:
        return np.full(len(idx), np.inf)
    sub = F[idx]
    for m in range(F.shape[1]):
        order = np.argsort(sub[:, m])
        d[order[0]] = d[order[-1]] = np.inf
        rng_m = sub[order[-1], m] - sub[order[0], m]
        if rng_m == 0:
            continue
        for k in range(1, len(idx) - 1):
            d[order[k]] += (sub[order[k + 1], m] - sub[order[k - 1], m]) / rng_m
    return d


class NSGA2:
    """Two-objective NSGA-II: minimise (#features, -MRA).

    `objective_fn(mask) -> (n_selected, mra)`.
    """

    def __init__(self, n_bits, objective_fn, pop_size=80, n_gen=200, pc=0.9, pm=None, seed=0):
        self.n, self.obj, self.P, self.G = n_bits, objective_fn, pop_size, n_gen
        self.pc, self.pm = pc, (pm if pm is not None else 1.0 / n_bits)
        self.rng = np.random.default_rng(seed)

    def _eval(self, pop):
        return np.array([[k, -m] for k, m in (self.obj(x) for x in pop)], float)

    def _tournament(self, rank, crowd):
        i, j = self.rng.integers(self.P, size=2)
        if rank[i] != rank[j]:
            return i if rank[i] < rank[j] else j
        return i if crowd[i] > crowd[j] else j

    def run(self):
        rng = self.rng
        pop = rng.random((self.P, self.n)) < 0.5
        for i in range(self.P):
            _ensure_nonempty(pop[i], rng)
        F = self._eval(pop)
        hist = []
        for g in range(self.G + 1):
            fronts = fast_non_dominated_sort(F)
            rank = np.zeros(len(pop), int)
            crowd = np.zeros(len(pop))
            for r, fr in enumerate(fronts):
                rank[fr] = r
                crowd[fr] = crowding_distance(F, fr)
            hist.append(dict(gen=g, best=float(-F[:, 1].min()), n_front=len(fronts[0]),
                             mean=float(-F[:, 1].mean())))
            if g == self.G:
                break
            children = []
            while len(children) < self.P:
                p1 = pop[self._tournament(rank, crowd)]
                p2 = pop[self._tournament(rank, crowd)]
                if rng.random() < self.pc:
                    c1, c2 = hux_crossover(p1, p2, rng)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                for c in (c1, c2):
                    flip = rng.random(self.n) < self.pm
                    c[flip] = ~c[flip]
                    children.append(_ensure_nonempty(c, rng))
            children = np.array(children[:self.P])
            Fc = self._eval(children)
            R, FR = np.vstack([pop, children]), np.vstack([F, Fc])
            fronts = fast_non_dominated_sort(FR)
            new_idx = []
            for fr in fronts:
                if len(new_idx) + len(fr) <= self.P:
                    new_idx += fr
                else:
                    cd = crowding_distance(FR, fr)
                    order = np.argsort(-cd)
                    new_idx += [fr[k] for k in order[: self.P - len(new_idx)]]
                    break
            pop, F = R[new_idx], FR[new_idx]
        fronts = fast_non_dominated_sort(F)
        pareto = fronts[0]
        # unique pareto solutions
        seen, P_masks, P_obj = set(), [], []
        for i in pareto:
            key = pop[i].tobytes()
            if key in seen:
                continue
            seen.add(key)
            P_masks.append(pop[i].copy())
            P_obj.append((int(F[i, 0]), float(-F[i, 1])))
        return dict(pareto_masks=P_masks, pareto_objs=P_obj, history=hist, generations=self.G)


def pick_from_pareto(pareto_masks, pareto_objs, n_total, lam=None, mode="knee"):
    """Choose one Pareto solution: 'weighted' (same F as TSFGA) or 'knee' (max distance to
    the line joining the two extreme points)."""
    objs = np.array(pareto_objs, float)          # (k, mra)
    if len(objs) == 1:
        return pareto_masks[0], pareto_objs[0]
    if mode == "weighted":
        assert lam is not None
        score = (1 - objs[:, 0] / n_total) + lam * objs[:, 1]
        i = int(np.argmax(score))
    else:
        k = (objs[:, 0] - objs[:, 0].min()) / max(np.ptp(objs[:, 0]), 1e-9)
        m = (objs[:, 1] - objs[:, 1].min()) / max(np.ptp(objs[:, 1]), 1e-9)
        # utopia point: k=0 (few features), m=1 (high MRA)
        i = int(np.argmin(np.sqrt(k ** 2 + (1 - m) ** 2)))
    return pareto_masks[i], pareto_objs[i]
