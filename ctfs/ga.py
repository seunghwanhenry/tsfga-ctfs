"""Binary genetic algorithm used in phase 2 of TSFGA (manuscript Section II.B)."""
from __future__ import annotations

import numpy as np


def hux_crossover(p1: np.ndarray, p2: np.ndarray, rng: np.random.Generator):
    """Half-uniform crossover: children inherit matching bits and swap exactly half
    of the non-matching bits (Fig. 3 of the manuscript)."""
    diff = np.flatnonzero(p1 != p2)
    c1, c2 = p1.copy(), p2.copy()
    if len(diff) >= 2:
        swap = rng.choice(diff, size=len(diff) // 2, replace=False)
        c1[swap], c2[swap] = p2[swap], p1[swap]
    return c1, c2


def roulette_select(fitness: np.ndarray, rng: np.random.Generator, n: int) -> np.ndarray:
    f = fitness - fitness.min() + 1e-9          # shift to positive
    p = f / f.sum()
    return rng.choice(len(fitness), size=n, replace=True, p=p)


class BinaryGA:
    """Elitist binary GA with roulette-wheel selection, HUX crossover and bit-flip mutation.

    Parameters mirror the manuscript: pop_size (P), n_gen (G), pc, pm, plus n_elite.
    `fitness_fn(mask) -> float` (higher is better).
    """

    def __init__(self, n_bits: int, fitness_fn, pop_size=80, n_gen=200, pc=0.5, pm=0.1,
                 n_elite=2, seed=0, init_prob=0.5, patience=None):
        self.n_bits, self.fit, self.P, self.G = n_bits, fitness_fn, pop_size, n_gen
        self.pc, self.pm, self.n_elite, self.patience = pc, pm, n_elite, patience
        self.init_prob = init_prob
        self.rng = np.random.default_rng(seed)

    def _init_pop(self):
        pop = self.rng.random((self.P, self.n_bits)) < self.init_prob
        for i in range(self.P):
            if not pop[i].any():
                pop[i, self.rng.integers(self.n_bits)] = True
        return pop

    def run(self):
        pop = self._init_pop()
        fit = np.array([self.fit(ind) for ind in pop])
        best_idx = int(np.argmax(fit))
        best, best_fit = pop[best_idx].copy(), float(fit[best_idx])
        hist = [dict(gen=0, best=best_fit, mean=float(fit.mean()), n_selected=int(best.sum()))]
        stall = 0
        for g in range(1, self.G + 1):
            elite_idx = np.argsort(-fit)[:self.n_elite]
            new_pop = [pop[i].copy() for i in elite_idx]
            parents = roulette_select(fit, self.rng, self.P)
            i = 0
            while len(new_pop) < self.P:
                p1, p2 = pop[parents[i % self.P]], pop[parents[(i + 1) % self.P]]
                i += 2
                if self.rng.random() < self.pc:
                    c1, c2 = hux_crossover(p1, p2, self.rng)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                for c in (c1, c2):
                    flip = self.rng.random(self.n_bits) < self.pm
                    c[flip] = ~c[flip]
                    if not c.any():
                        c[self.rng.integers(self.n_bits)] = True
                    if len(new_pop) < self.P:
                        new_pop.append(c)
            pop = np.array(new_pop)
            fit = np.array([self.fit(ind) for ind in pop])
            gi = int(np.argmax(fit))
            if fit[gi] > best_fit + 1e-12:
                best, best_fit, stall = pop[gi].copy(), float(fit[gi]), 0
            else:
                stall += 1
            hist.append(dict(gen=g, best=best_fit, mean=float(fit.mean()), n_selected=int(best.sum())))
            if self.patience and stall >= self.patience:
                break
        return dict(best_mask=best, best_fitness=best_fit, history=hist, generations=len(hist) - 1)
