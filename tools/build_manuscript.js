/* Build the AEI-format manuscript, revision 4 (co-author comments of 2026-09-21 incorporated).
   node tools/build_manuscript_v4.js DATA.json RESULTS_DIR ORIG_FIGS OUT.docx EQ_DIR
*/
const fs = require("fs");
const path = require("path");
const sizeOf = (p) => { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; };
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel, ImageRun,
  BorderStyle, Footer, PageNumber, LevelFormat, VerticalAlign, TableLayoutType, TabStopType,
} = require("docx");

const [,, dataPath, resDir, origDir, outPath, eqDirArg] = process.argv;
const D = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const C = D.config;
const EQ_DIR = eqDirArg || path.join(path.dirname(outPath), "eq");
const DROP = new Set(["NSGA2"]);                       // multi-objective method removed from the comparison (comments 39, 40)
D.baseline_avg = D.baseline_avg.filter((r) => !DROP.has(r[0]));
D.recovery = D.recovery.filter((r) => !DROP.has(r[0]));
D.wilcoxon = D.wilcoxon.filter((r) => !DROP.has(r[0]));
{ const keep = D.baseline_per_process.methods.map((m) => !DROP.has(m));
  D.baseline_per_process.rows = D.baseline_per_process.rows.map((r) => [r[0], ...r.slice(1).filter((_, i) => keep[i])]);
  D.baseline_per_process.methods = D.baseline_per_process.methods.filter((m) => !DROP.has(m)); }
{ const keep = D.temporal.methods.map((m) => !DROP.has(m));
  D.temporal.rows = D.temporal.rows.map((r) => [r[0], r[1], ...r.slice(2, -1).filter((_, i) => keep[i]), r[r.length - 1]]);
  D.temporal.methods = D.temporal.methods.filter((m) => !DROP.has(m)); }

// ---------------------------------------------------------------- helpers
const FONT = "Times New Roman";
let figNo = 0, tabNo = 0;
const FIG_ORDER = ["framework", "sim_model", "real_violin", "real_mra_size", "real_corr_abc", "real_corr_de", "sim_violin",
  "sim_convergence", "sim_cd", "sim_mra_size", "sens_lambda_tau", "temporal", "selfreq", "shap", "appx_ga_sens"];
const TAB_ORDER = ["litreview", "factors", "regressors", "methods", "effect", "mra_pfr", "cfs", "ablation", "baselines_avg",
  "baselines_proc", "wilcoxon", "sens", "temporal", "recovery", "protocol", "appx_features", "appx_ga_sens"];
const F = (n) => { const i = FIG_ORDER.indexOf(n); if (i < 0) throw new Error("unknown figure " + n); return i + 1; };
const T = (n) => { const i = TAB_ORDER.indexOf(n); if (i < 0) throw new Error("unknown table " + n); return i + 1; };
const resolveRefs = (t) => t.replace(/\{\{fig:([A-Za-z_]+)\}\}/g, (_, n) => F(n)).replace(/\{\{tab:([A-Za-z_]+)\}\}/g, (_, n) => T(n));
const runs = (text, opts = {}) => {
  text = resolveRefs(text);
  const out = [];
  const re = /(\*[^*]+\*|\^[^^]+\^|~[^~]+~)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: 24, ...opts }));
    const t = m[0];
    if (t.startsWith("*")) out.push(new TextRun({ text: t.slice(1, -1), font: FONT, size: 24, italics: true, ...opts }));
    else if (t.startsWith("^")) out.push(new TextRun({ text: t.slice(1, -1), font: FONT, size: 24, superScript: true, ...opts }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: FONT, size: 24, subScript: true, italics: true, ...opts }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: 24, ...opts }));
  return out;
};
const P = (text, o = {}) => new Paragraph({ children: runs(text, o.run || {}), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: o.line || 360, after: o.after ?? 120, before: o.before ?? 0 }, indent: o.indent });
const H = (text, level) => new Paragraph({
  heading: level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: FONT, bold: true, size: level === 1 ? 26 : 24, italics: level === 3 })],
  spacing: { before: level === 1 ? 360 : 240, after: 120, line: 300 } });
const Bullets = (items) => items.map((t) => new Paragraph({ children: runs(t), numbering: { reference: "bul", level: 0 },
  spacing: { line: 360, after: 60 }, alignment: AlignmentType.JUSTIFIED }));
const Numbered = (items) => items.map((t) => new Paragraph({ children: runs(t), numbering: { reference: "num", level: 0 },
  spacing: { line: 360, after: 60 }, alignment: AlignmentType.JUSTIFIED }));
const Caption = (text) => new Paragraph({ children: runs(text, { size: 22 }), alignment: AlignmentType.JUSTIFIED, spacing: { before: 80, after: 240, line: 276 } });
const border = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function Tbl(name, title, header, rows, widths, opts = {}) {
  tabNo += 1;
  if (TAB_ORDER[tabNo - 1] !== name) throw new Error(`table order mismatch: expected ${TAB_ORDER[tabNo - 1]}, got ${name}`);
  let total = widths.reduce((a, b) => a + b, 0);
  if (total > 9026) { const f = 9026 / total; widths = widths.map((x) => Math.floor(x * f)); total = widths.reduce((a, b) => a + b, 0); }
  process.stderr.write(`[table ${tabNo} ${name}] width=${total} cols=${widths.length}\n`);
  const fsz = opts.fontSize || 18;
  const mk = (txt, bold, first, bottom) => new TableCell({
    width: { size: 0, type: WidthType.DXA }, borders: { top: none, bottom: bottom ? border : none, left: none, right: none },
    verticalAlign: VerticalAlign.CENTER, margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ children: runs(String(txt), { size: fsz, bold }), alignment: first ? AlignmentType.LEFT : (opts.leftAlignAll ? AlignmentType.LEFT : AlignmentType.CENTER), spacing: { line: 240, after: 0 } })] });
  const hdr = Array.isArray(header[0]) ? header : [header];
  const hdrRows = hdr.map((h, hi) => new TableRow({ tableHeader: true, children: h.map((t, i) => mk(t, true, i === 0, hi === hdr.length - 1)) }));
  const bodyRows = rows.map((r) => new TableRow({ children: r.map((t, i) => mk(t, String(r[0]).startsWith("Average") || String(r[0]).startsWith("Rank") || String(r[0]).startsWith("This study"), i === 0, false)) }));
  const table = new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [...hdrRows, ...bodyRows], borders: { top: border, bottom: border, left: none, right: none, insideHorizontal: none, insideVertical: none } });
  return [new Paragraph({ children: runs(`Table ${tabNo}. ${title}`, { size: 22 }), spacing: { before: 240, after: 80, line: 276 }, keepNext: true }), table,
          opts.note ? new Paragraph({ children: runs(opts.note, { size: 18 }), spacing: { before: 60, after: 240, line: 240 } }) : new Paragraph({ spacing: { after: 200 } })];
}
function Fig(name, files, caption, maxW = 600, opts = {}) {
  figNo += 1;
  if (FIG_ORDER[figNo - 1] !== name) throw new Error(`figure order mismatch: expected ${FIG_ORDER[figNo - 1]}, got ${name}`);
  const list = Array.isArray(files) ? files : [files];
  const stack = opts.stack || false;                       // one image per line (panels a, b, ...)
  const paras = [];
  const imgs = list.map((f) => { const { w, h } = sizeOf(f);
    const tw = Math.min(stack || list.length === 1 ? maxW : Math.floor(maxW / list.length) - 6, Math.round(w * 0.75));
    process.stderr.write(`[fig ${figNo} ${name}] ${path.basename(f)} native=${w}x${h} -> ${tw}x${Math.round(h * tw / w)}px\n`);
    return new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: tw, height: Math.round(h * tw / w) } }); });
  if (stack) imgs.forEach((im, i) => paras.push(new Paragraph({ children: [im], alignment: AlignmentType.CENTER, spacing: { before: i === 0 ? 200 : 60, after: 60 }, keepNext: true })));
  else paras.push(new Paragraph({ children: imgs, alignment: AlignmentType.CENTER, spacing: { before: 200, after: 60 }, keepNext: true }));
  return [...paras, Caption(`Fig. ${figNo}. ${caption}`)];
}
const Eq = (n) => {  // equation image in a borderless 2-cell table so that the number is vertically centred
  const f = path.join(EQ_DIR, `eq${n}.png`); const { w, h } = sizeOf(f);
  const img = new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: Math.round(w / 300 * 96 * 1.05), height: Math.round(h / 300 * 96 * 1.05) } });
  const cell = (children, width, align) => new TableCell({ width: { size: width, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    borders: { top: none, bottom: none, left: none, right: none }, margins: { top: 60, bottom: 60, left: 0, right: 0 },
    children: [new Paragraph({ children, alignment: align, spacing: { after: 0 } })] });
  return new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: [8226, 800], layout: TableLayoutType.FIXED,
    borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: [new TableRow({ children: [cell([img], 8226, AlignmentType.CENTER), cell([new TextRun({ text: `(${n})`, font: FONT, size: 24 })], 800, AlignmentType.RIGHT)] })] });
};
const R = (p) => path.join(resDir, p);
const O = (p) => path.join(origDir, p);
const fmtP = (p) => (p < 1e-4 ? "p < 10^-4^" : `p = ${p.toFixed(4)}`);
const lastProc = () => D.processes[D.processes.length - 1];
const b = (m) => D.baseline_avg.find((r) => r[0] === m);
const w = (m) => D.wilcoxon.find((r) => r[0] === m);
const pp = (m) => (Math.abs(parseFloat(w(m)[1])) * 100).toFixed(1);
const g = (k) => D.sens[k];
const pct1 = (x) => (100 * x).toFixed(1) + "%";

// ---------------------------------------------------------------- content
const body = [];
const add = (...x) => x.flat().forEach((e) => body.push(e));

// ===== Title page =====
add(new Paragraph({ children: [new TextRun({ text: "Two-stage genetic-algorithm feature selection for lot cycle-time prediction in semiconductor wafer fabrication: a real-fab case study and simulation-based validation", font: FONT, size: 32, bold: true })], alignment: AlignmentType.LEFT, spacing: { after: 240, line: 320 } }));
add(P("Seunghwan Song^a^, Byung Kwon Lee^a,*^", { align: AlignmentType.LEFT, line: 276 }));
add(P("^a^ Department of Industrial & Management Engineering, Korea National University of Transportation, 50 Daehak-ro, Chungju-si, Chungcheongbuk-do 27469, Republic of Korea", { align: AlignmentType.LEFT, line: 276, run: { size: 22 } }));
add(P("* Corresponding author. E-mail: leebk@ut.ac.kr (B.K. Lee).", { align: AlignmentType.LEFT, line: 276, run: { size: 22 } }));

add(H("Highlights", 1));
add(Bullets([
  "A two-stage method selects cycle-time features: a redundancy filter, then a genetic-algorithm search.",
  "On 577,236 real wafer-lot records it halves the feature set, raises accuracy and removes every collinear pair.",
  "A simulated fab with known cycle-time drivers supplies statistical validation and driver recovery.",
  "The results yield a protocol for choosing a feature selection method for cycle-time prediction.",
]));

add(H("Abstract", 1));
add(P(`Lot cycle time (CT) governs on-time delivery in wafer fabrication, and it depends on dozens of collinear factors. Feature selection must therefore shrink the input set without discarding the factors that engineers need for root-cause analysis. This paper proposes a two-stage feature selection method with a genetic algorithm (TSFGA): a filter based on Pearson correlation and mutual information removes redundant features, and the genetic algorithm (GA) then searches the remaining features with a fitness that trades feature reduction against mean relative accuracy (MRA). On 577,236 wafer-lot records from six processes of a Korean fab, TSFGA removes 47.5% of the features, raises the MRA of a random forest by 2.2 percentage points and outperforms four feature selection methods from the CT literature on accuracy, reduction and redundancy. Real data cannot show whether the selected features are the true CT drivers, so the method was also tested on a simulated fab whose drivers are known by construction. Over 90 product–operation units and ten seeds, an ablation shows that the filter and GA stages are complementary (Friedman ${fmtP(D.ablation_stats.p)}); a comparison with twelve alternatives under one protocol, tested with Wilcoxon and Nemenyi statistics, shows that the gain over the all-feature model is significant, survives a chronological split and coincides with recovery of the true drivers. Two further results are practical: the second-stage optimizer and its mutation rate change the outcome, and ranking-based wrappers match the two-stage search when the drivers are few and additive. The paper closes with a protocol for choosing a feature selection method for CT prediction.`));
add(P("Keywords: cycle-time prediction; feature selection; genetic algorithm; semiconductor manufacturing; wafer fabrication; simulation", { align: AlignmentType.LEFT, line: 276 }));

// ===== 1 Introduction =====
add(H("1. Introduction", 1));
add(P("On-time delivery is a competitive requirement in semiconductor manufacturing, and lot cycle time (CT) is its key quantity [1]. CT is the time a lot—typically 25 wafers—needs to complete a processing step [2]; fabs use it to predict job completion [3] and to quote delivery dates [4,5]. CT prediction accuracy therefore translates directly into delivery performance."));
add(P("CT depends on many factors [6], and the operational relevance of most of them—tool utilization, queue length, work-in-process (WIP)—is uncertain [7]. Models that use every candidate factor overfit and run slowly, and collinear factors make both problems worse. Models built on a handful of hand-picked factors [11–13] cannot represent a fab with many products, routes and tool types [14]. A compact but sufficient feature subset is therefore the central requirement of CT prediction [8]."));
add(P("Dimensionality can be reduced by feature extraction or by feature selection. Extraction (principal component analysis, autoencoders) creates composite variables that a process engineer cannot trace back to a tool, a queue or a dispatching rule; selection keeps the original variables. Because CT models in a fab serve root-cause analysis and CT control [9,10]—the reason recent studies stress explainability [50–52]—selection is the appropriate choice. The selection methods published for CT prediction (Section 2) score features one at a time, search greedily and leave redundancy among the selected features uncontrolled."));
add(P("This paper proposes a two-stage feature selection method with a genetic algorithm (GA), abbreviated TSFGA. The filter stage removes redundant features with Pearson's correlation coefficient (PCC) and mutual information (MI), keeping from each collinear pair the member that carries more information about CT. The GA stage searches the filtered features with a fitness that combines the percentage of feature reduction (PFR) and the mean relative accuracy (MRA) of the predictor. Two studies evaluate the method. A case study on 577,236 wafer-lot records from a Korean fab establishes its value in practice. Real data, however, cannot show whether a method selects the factors that generate CT or only correlated proxies, and a stochastic method cannot be judged for stability from one run. A simulation study on a fab model whose CT drivers are known by construction closes both gaps. The contributions are:"));
add(Bullets([
  "A two-stage filter–GA method for CT feature selection. Its fitness trades reduction against accuracy explicitly, and its filter removes the multicollinearity that existing CT methods leave in place.",
  "A case study on 577,236 real wafer-lot records. TSFGA removes 47.5% of the features, raises MRA by 2.2 percentage points over the all-feature random forest and outperforms four CT feature selection methods on accuracy, reduction and redundancy.",
  "A simulated fab benchmark with the feature structure of the real data, process-specific CT drivers, redundant proxies and utilization drift. On it the two stages are validated with statistical tests over product–operation units, the true drivers are recovered, and the gain holds under a chronological split.",
  "A protocol for choosing a CT feature selection method, derived from thirteen methods run under one protocol. It states when to use the two-stage search, its swarm-based variant or a ranking-based wrapper, with the trade-offs quantified.",
]));
add(P("Section 2 reviews related work. Section 3 presents the method. Section 4 describes the data, the protocol, the compared methods and the metrics. Sections 5 and 6 report the real-fab and the simulation study. Section 7 discusses the findings and states the protocol; Section 8 concludes."));

// ===== 2 Literature review =====
add(H("2. Literature review", 1));
add(H("2.1. Cycle-time prediction in wafer fabrication", 2));
add(P("CT has been predicted with regression [11], fuzzy-neural systems [13], data mining [2], cloud-based interval estimation [1], hybrid clustering–learning schemes [5], deep learning [12,27] and, recently, explainable pipelines that expose the drivers of a prediction [14,29,50–52] or bound CT with fuzzy ensembles [51,58]. System-level work predicts WIP levels and CT distributions with data-driven aggregate models [53] or fab output from remaining-CT regressions [54]. Whatever the learner, these models take as inputs factors that describe the lot, the order, the workshop state and the tool state, and the choice of those factors dominates accuracy [7,8]. Queueing theory explains why the choice is hard: waiting time grows nonlinearly with utilization and queue length [46], so the factors interact, and many of them—the minimum, mean and maximum utilization over a window, for instance—are near-duplicates. Selection has to control redundancy."));
add(H("2.2. Feature selection for cycle-time prediction", 2));
add(P("Feature selection methods are filters, wrappers or embedded methods [16]. Filters score features by a statistic computed without the predictor. Meidan et al. [17] identified influential CT factors with a selective naïve Bayes classifier; Wang et al. [18] proposed mutual-information network decomposition (MI-ND) to isolate direct dependencies between factors and CT. Filters are cheap, but they ignore interactions among features and the predictor that will use them. Wrappers evaluate candidate subsets with the predictor. Wang et al. [6] developed data-driven analysis (DDA), which ranks factors by an adaptive logistic-regression correlation and adds them stepwise; Schelthoff et al. [19] ranked factors by permutation feature importance and removed them by sequential backward search (PFI-SBS) to predict step waiting times. Both account for predictive performance, but both score features individually, leave redundancy among the retained features uncontrolled and, being greedy, stop in local optima. Generic filters such as MI ranking and minimum-redundancy–maximum-relevance (mRMR) [36] and embedded methods such as the least absolute shrinkage and selection operator (LASSO) [34], recursive feature elimination (RFE) [35] and Boruta [33] are standard elsewhere in manufacturing but have rarely been benchmarked on CT. Shapley additive explanations (SHAP) have been used to improve process quality in semiconductor manufacturing [56] and to correct deep CT predictors after training [52]."));
add(H("2.3. Hybrid filter–wrapper feature selection", 2));
add(P("Hybrid methods run a cheap filter first and a wrapper on the survivors, combining the speed of the former with the accuracy of the latter [20,21,57]. Population-based algorithms suit the wrapper stage because a subset is a bit string: GAs with elitism and half-uniform crossover [25,26,41], binary particle swarm optimization (BPSO) [30] and binary grey wolf optimization (BGWO) [31] are the common choices [44]. Multi-objective variants return a Pareto front of subset size against accuracy [32,55]; they need a separate rule to pick one subset and are not pursued here. No hybrid method with a redundancy-aware filter has been reported for CT, and the candidate search algorithms have never been compared under one protocol."));
add(H("2.4. Research gap", 2));
add(P("Table {{tab:litreview}} classifies the CT studies that address feature selection by the CT quantity, the selection type, redundancy control, the search strategy and the validation. The gaps are visible in the columns. No CT-specific method controls redundancy, so the selected subsets still contain collinear features that obstruct interpretation. Every method scores features individually and searches greedily. Validation consisted of one run on one real dataset—no statistical test, no repetition of stochastic components, no check that the selected features are the actual CT drivers. This study closes the three gaps with a redundancy-aware two-stage method and a two-part evaluation on real and simulated fab data."));
add(Tbl("litreview", "Feature selection in cycle-time prediction studies.",
  ["Study", "CT quantity", "Feature selection", "Redundancy controlled", "Search", "Validation"],
  [["Meidan et al. [17]", "Lot CT", "Filter (selective naïve Bayes)", "No", "Ranking", "Real fab, single run"],
   ["Wang et al. [6]", "Lot CT", "Wrapper (DDA)", "No", "Greedy stepwise", "Single run"],
   ["Wang et al. [18]", "Lot CT", "Filter (MI-ND)", "Partly (indirect dependencies removed)", "Ranking", "Single run"],
   ["Schelthoff et al. [19]", "Step waiting time", "Wrapper (PFI-SBS)", "No", "Greedy backward", "Real fab, single run"],
   ["Lingitz et al. [8]", "Order lead time", "Feature importance only", "No", "—", "Real fab, single run"],
   ["Chen & Wang [14]; Wang [52]", "Job CT", "None (post-hoc explanation)", "—", "—", "Single run"],
   ["This study", "Step CT", "Two-stage filter + GA (TSFGA)", "Yes (PCC/MI filter)", "Population-based (GA)", "Real fab; simulated fab with known drivers, 10 seeds, statistical tests"]],
  [1900, 1300, 1900, 1500, 1300, 1900], { fontSize: 16, leftAlignAll: true }));

// ===== 3 Method =====
add(H("3. Proposed method", 1));
add(H("3.1. Overview", 2));
add(P("TSFGA combines a filter stage with a GA stage (Fig. {{fig:framework}}). The filter removes redundant features with PCC and MI at negligible cost. The GA then searches the filtered features for the subset that best balances size against accuracy. A GA is used because it operates directly on the binary subset representation, escapes local optima through crossover and mutation [22,23] and accepts any fitness function [44]; other population-based algorithms can take its place, and two of them (BPSO and BGWO) are evaluated as alternatives in Section 6. Throughout, the target variable is the CT of a lot at an operation step, and 'features' are the candidate input factors of Table {{tab:factors}}."));
add(Fig("framework", O("image1.png"), "Overall framework of the proposed two-stage feature selection method (TSFGA)."));
add(H("3.2. Filter stage based on PCC and MI", 2));
add(P("The filter stage removes collinear features while keeping those relevant to CT. Collinearity between two features is measured by the PCC, which is inexpensive, has an intuitive scale and is standard in CT studies [6,24]. For candidate features *x*~i~ and *x*~j~ with *n* samples, where *x*~ik~ is the *k*-th sample of *x*~i~ and *x̄*~i~ its mean,"));
add(Eq(1));
add(P("|*r*~ij~| = 1 means that the two features carry the same linear information; values near zero mean they are unrelated. *r*~ij~ therefore measures redundancy between features, not relevance to CT. Relevance is measured by MI, which assumes no distribution and captures nonlinear dependence:"));
add(Eq(2));
add(P("where *p*(*x*, *y*) is the joint distribution of the feature *X* and the CT *Y*, *p*(*x*) and *p*(*y*) are the marginals, and log is the natural logarithm (MI in nats). MI is zero for independent variables and grows with dependence; for continuous features it is estimated with the k-nearest-neighbor estimator [48]. The filter proceeds in five steps: (1) compute *r*~ij~ for all feature pairs; (2) flag pairs with |*r*~ij~| > *τ*, where *τ* = 0.8 was set with domain experts in a preliminary investigation and is varied in Section 6.3; (3) compute the MI of each member of a flagged pair with CT; (4) process the flagged pairs from the highest |*r*~ij~| downward and remove the member with the lower MI, skipping a pair if one member has already been removed; (5) return the remaining features as the filtered subset."));
add(H("3.3. GA stage with a reduction–accuracy fitness function", 2));
add(P("The GA searches the filtered subset. An individual is a chromosome of *d* genes, one per filtered feature; gene *j* = 1 selects feature *j*. The initial population of *P* individuals is random, each gene set to 1 with probability 0.5 [25]. The fitness of individual *i* combines the PFR with the MRA of the predictor trained on the selected features:"));
add(Eq(3));
add(Eq(4));
add(Eq(5));
add(P("where λ weights accuracy against reduction, |features(*i*)| is the number of selected features, |total features| is the number of original features (54), ct~k~ is the CT of the *k*-th lot step and ĉt~ik~ its prediction with subset *i*. Eq. (3) is equivalent to the convex combination (1 − *w*)·PFR + *w*·MRA with *w* = λ/(1 + λ). The unnormalized form keeps PFR on its natural [0, 1] scale, so λ reads directly as the accuracy gain that compensates for one unit of reduction. MRA is computed on the validation split of each product–operation unit (Section 4.3) and averaged; the GA therefore optimizes exactly the quantity that is reported in the evaluation. Parents are chosen by roulette-wheel selection with elitism, which copies the fittest individuals into the next generation unchanged [25]. Offspring are produced by half-uniform crossover (HUX), which keeps matching genes and swaps exactly half of the differing genes to maximize diversity [26,41], followed by bit-flip mutation with rate *p*~m~. An offspring with no selected gene is repaired by setting one random gene to 1. The search stops after *G* generations or after 40 consecutive generations without improvement of the best fitness, and returns the best individual. Identical chromosomes recur across generations, so fitness values are memoized and the number of model fits stays well below *P* × *G*."));
add(H("3.4. Computational cost", 2));
add(P("Let *d* be the number of features and *n* the number of training rows. The filter costs O(*d*^2^*n*) for the correlation matrix plus O(*q*·*n* log *n*) for the MI estimates of the *q* flagged pairs—negligible. The GA cost is the number of fitness evaluations, each of which trains the predictor once. With memoization that number equals the number of distinct chromosomes visited: 60–85% of *P* × *G* early in a run and far fewer after convergence. The same bound holds for the swarm-based alternatives, so run times in Section 6 are compared at equal population size and iteration count."));

// ===== 4 Experimental design =====
add(H("4. Experimental design", 1));
add(H("4.1. Real fab dataset", 2));
add(P("The real dataset is a wafer-lot transaction log from a fab in South Korea: 577,236 records, one per lot and operation step, covering 90 days from May to July 2023. A lot comprises 25 wafers and passes through roughly 400–1000 operation steps; the target is the time each step takes. Candidate features were extracted from the manufacturing execution system, the supply-chain management system and the automated material handling system (AMHS). Table {{tab:factors}} lists the 54 features in four categories; each factor is a group of features—'utilization', for example, comprises the average, minimum and maximum tool utilization over the past week. The features include variables from earlier CT studies [19,27] and variables defined with domain experts. The data were split into six major processes—lithography, implantation, etching, metalization, deposition and planarization—because their CT distributions and process structures differ; feature selection was run and evaluated per process."));
add(Tbl("factors", "Investigated factors for cycle-time prediction (real fab data).", ["Type", "Factors", "# of features"],
  [["Wafer lot characteristics", "Priority of lot, lot size, number of layers in each product", "6"],
   ["Order characteristics", "Tardiness, percentage of due-date completion, product mix", "3"],
   ["Workshop condition", "WIP in the fab, workload of the AMHS, weekend, holidays", "19"],
   ["Machine state", "Utilization, production performance, waiting-queue length, number of machines per process", "26"]], [2600, 5400, 1360]));
add(H("4.2. Simulated fab with known cycle-time drivers", 2));
add(P("The simulation study does what the real data cannot. Real data do not reveal which factors generate CT, so a method that selects correlated proxies is indistinguishable from one that selects the drivers; in the simulated fab the drivers are known by construction, and precision and recall of driver recovery can be measured. The GA is stochastic, and the real-data experiments were single runs; the simulation permits repeated runs and statistical tests over many product–operation units. The real data are confidential; the simulated data and the generator can be released, which makes the benchmark reproducible."));
add(P(`Fig. {{fig:sim_model}} shows the structure of the simulation model. It generates lot-step records with the schema and the four feature categories of the real data (54 features). For each process, product and operation a base processing time and a base waiting time are drawn. The CT of a lot step is the processing time—scaled by lot size and, in lithography and etching, by the number of layers—plus a waiting time that grows with effective utilization ρ as ρ/(1 − ρ) raised to a process-specific exponent [46] and is modulated by queue length, process WIP, lot priority, weekend and holiday flags, AMHS load, tool downtime and, in some processes, batch size or set-up time; log-normal noise is applied. Ten drivers are common to all processes and one to three are process specific, giving 10–13 drivers per process (Appendix A, Table {{tab:appx_features}}). Eleven further features are proxies correlated at |r| > 0.8 with a driver (minimum and maximum utilization, fab and area WIP, availability as one minus the downtime ratio, among others); the remaining features are noise. Utilization and WIP drift upward over the 90-day horizon, so a chronological split is harder than a random split. The instance used here has ${D.processes.length} processes, ${D.data.n_products} products and ${D.data.n_ops_per_process} operations per process (${D.n_combos} product–operation units, ${D.data.n_rows.toLocaleString()} records; CT mean ${D.data.ct_mean.toFixed(1)} h, median ${D.data.ct_median.toFixed(1)} h).`));
add(Fig("sim_model", R("fig_sim_model.png"), "Structure of the simulated fab: sampled drivers, step cycle-time model, feature construction and the analyses the benchmark enables."));
add(H("4.3. Evaluation protocol", 2));
add(P(`Line experts require the method to be assessed per product and operation, so each process dataset is divided into product–operation units rather than cross-validation folds (a lithography dataset with four products and 16 operations yields 64 units). Each unit is split into training (50%), validation (25%) and test (25%) records. The real-fab study uses a random split. The simulation study uses both a random split and a chronological split, in which the first 50% of a unit's records in time train the model, the next 25% validate it and the last 25% test it; no future record enters training, and the utilization drift separates training from test. Feature selection uses the training and validation records of all units of a process. The selected subset is then evaluated by training one predictor per unit on its training records and scoring its test records, which gives a distribution of scores over units. On the simulated fab every stochastic method was run with ${C.seeds} seeds in the main comparison and ${D.seeds_temporal} seeds in the chronological analysis; results are mean ± standard deviation over seeds.`));
add(H("4.4. Predictor and parameter settings", 2));
add(P("A random forest (RF) [45] from scikit-learn [28] is the predictor in the fitness function and in the evaluation. In a set-up experiment on the real data, five regressors were combined with TSFGA—support vector regression (SVR), decision tree (DT), RF, LightGBM (LGBM) [47] and a multilayer perceptron (MLP)—and RF was best on average (Table {{tab:regressors}}). RF is also the usual choice in CT studies and yields feature importances for explanation [14,29]."));
add(Tbl("regressors", "Comparison of MRA with different regressors combined with TSFGA (real fab data).",
  ["Major process", "SVR", "DT", "RF", "LGBM", "MLP"],
  [["Lithography", "0.9306", "0.8978", "0.9360", "0.9198", "0.9365"], ["Implantation", "0.9273", "0.9016", "0.9317", "0.9165", "0.9291"],
   ["Etching", "0.9267", "0.8960", "0.9312", "0.9159", "0.9325"], ["Metalization", "0.9530", "0.9271", "0.9450", "0.9418", "0.9517"],
   ["Deposition", "0.9252", "0.8905", "0.9328", "0.9143", "0.9230"], ["Planarization", "0.9248", "0.9167", "0.9308", "0.9337", "0.9334"],
   ["Average", "0.9313", "0.9049", "0.9346", "0.9237", "0.9344"]], [2200, 1400, 1400, 1400, 1400, 1400]));
add(P(`The GA ran with population size *P* = ${C.pop}, *G* = ${C.gen} generations, crossover rate *p*~c~ = ${C.pc}, mutation rate *p*~m~ = ${C.pm}, two elites, λ = ${C.lam} and τ = ${C.thr}. These values were fixed in preliminary experiments on the real data; their sensitivity is reported in Section 6.3 (λ, τ) and Appendix B (GA parameters). The simulated fab used the same values, and the swarm-based alternatives received the same population size and iteration count. The RF in the fitness function had ${C.fitness_trees} trees and the RF in the evaluation ${C.eval_trees} trees, with scikit-learn defaults otherwise.`));
add(H("4.5. Compared feature selection methods", 2));
add(P("On the real data TSFGA was compared with the two CT-specific wrappers—data-driven analysis (DDA) [6] and permutation feature importance with sequential backward search (PFI-SBS) [19]—and with two filters, minimum-redundancy–maximum-relevance (mRMR) [36] and mutual-information ranking (MI). On the simulated fab the comparison covers the thirteen methods of Table {{tab:methods}}: the two ablation configurations (filter stage alone; GA stage alone on all 54 features), TSFGA, two variants in which BPSO [30] or BGWO [31] replaces the GA under the same filter and fitness, the four methods above and three embedded methods. For ranking-based methods the subset size is the one that maximizes validation MRA (the star markers of Fig. {{fig:real_mra_size}}); DDA accepts features stepwise on validation MRA."));
add(Tbl("methods", "Feature selection methods compared on the simulated fab.",
  ["Abbreviation", "Method", "Type", "Subset size determined by", "Ref."],
  [["ALL", "No selection (all 54 features)", "Baseline", "—", "—"],
   ["FILTER", "Filter stage of TSFGA only (PCC/MI)", "Filter (ablation)", "Threshold τ", "Sec. 3.2"],
   ["GA", "GA stage of TSFGA only, on all 54 features", "Wrapper (ablation)", "Fitness (PFR + λ·MRA)", "Sec. 3.3"],
   ["TSFGA", "Two-stage filter + GA (proposed)", "Hybrid", "Fitness (PFR + λ·MRA)", "Sec. 3"],
   ["BPSO", "Filter + binary particle swarm optimization", "Hybrid (variant)", "Same fitness as TSFGA", "[30]"],
   ["BGWO", "Filter + binary grey wolf optimization (bGWO2)", "Hybrid (variant)", "Same fitness as TSFGA", "[31]"],
   ["mRMR", "Minimum redundancy–maximum relevance ranking", "Filter", "Best validation MRA over top-*k*", "[36]"],
   ["MI", "Mutual-information ranking", "Filter", "Best validation MRA over top-*k*", "[49]"],
   ["DDA", "Data-driven analysis: correlation-ranked stepwise search", "Wrapper", "Forward stepwise on validation MRA", "[6]"],
   ["PFI-SBS", "Permutation feature importance + sequential backward search", "Wrapper", "Best validation MRA over the backward path", "[19]"],
   ["RFE", "Recursive feature elimination with RF importances", "Wrapper", "Best validation MRA over top-*k*", "[35]"],
   ["LASSO", "L1-regularized linear regression", "Embedded", "Non-zero coefficients (cross-validated α)", "[34]"],
   ["Boruta", "Shadow-feature test with RF importances", "Embedded", "Confirmed features (binomial test)", "[33]"]],
  [1300, 3300, 1500, 2300, 800], { fontSize: 16, leftAlignAll: true }));
add(H("4.6. Metrics and statistical tests", 2));
add(P("One metric per objective: MRA (Eq. 5) for accuracy, PFR (Eq. 4) for reduction, and the correlation-based feature-subset merit (CFS) [40] for relevance with low redundancy,"));
add(Eq(6));
add(P("where *k* is the subset size, *ρ̄*~sy~ the mean absolute PCC between selected features and CT, and *ρ̄*~ss~ the mean absolute PCC among selected features. The simulated fab adds the mean absolute error (MAE), the root mean squared error (RMSE) and the coefficient of determination (R²) of the predictions, and four measures of the selection itself: the number of selected pairs with |r| > 0.8, the wall-clock selection time, the stability of the subset across seeds as the mean pairwise Jaccard index, and—because the drivers are known—the precision, recall and F1 of driver recovery, where a retained proxy counts as a hit. Methods are compared over product–operation units with the paired Wilcoxon signed-rank test [39]; all methods jointly with the Friedman test [49] and the Nemenyi post-hoc test, reported as critical-difference (CD) diagrams [38]."));

// ===== 5 Real-fab case study =====
add(H("5. Real-fab case study", 1));
add(H("5.1. Effect of the proposed method", 2));
add(P("TSFGA was applied to each of the six processes, and the RF trained on all features was compared with the RF trained on the selected subset (TSFGA–RF). Fig. {{fig:real_violin}} shows the MRA distribution over the product–operation units of each process before (green) and after (red) selection; dotted lines are quartiles. Every process improved. Table {{tab:effect}} gives the numbers: the largest gain is in deposition, +3.1 percentage points of MRA (hereafter %p) with 22 of 54 features retained (59.3% reduction); on average MRA rose by 2.2%p and the feature set shrank by 47.5%. With lot CTs of 50–100 days, 2.2%p of MRA is 1.1–2.2 days—a margin that matters for delivery commitments to downstream operations and customers."));
add(Fig("real_violin", O("image4.png"), "MRA distributions over product–operation units before (green) and after (red) applying TSFGA to the RF predictor, for the six major processes (real fab data).", 420));
add(Tbl("effect", "Effect of TSFGA on MRA and PFR (real fab data; mean ± standard deviation over product–operation units).",
  ["Major process", "MRA, RF (all features)", "MRA, TSFGA–RF", "PFR", "# selected"],
  [["Lithography", "0.9088 ± 0.018", "0.9360 ± 0.015", "46.3%", "29"], ["Implantation", "0.9128 ± 0.028", "0.9317 ± 0.019", "48.1%", "28"],
   ["Etching", "0.9036 ± 0.023", "0.9312 ± 0.021", "48.1%", "28"], ["Metalization", "0.9266 ± 0.018", "0.9450 ± 0.018", "37.0%", "34"],
   ["Deposition", "0.9018 ± 0.024", "0.9328 ± 0.020", "59.3%", "22"], ["Planarization", "0.9245 ± 0.017", "0.9308 ± 0.019", "46.3%", "29"],
   ["Average", "0.9130", "0.9346", "47.5%", "28"]], [2200, 2100, 2100, 1400, 1400]));
add(H("5.2. Comparison with other feature selection methods", 2));
add(P("Fig. {{fig:real_mra_size}} plots MRA against subset size for metalization and planarization, the processes in which TSFGA ranks highest (first, by the largest margin) and lowest (third) in Table {{tab:mra_pfr}}. The dashed line is the all-feature baseline; stars mark each method's best MRA, squares the smallest subset that beats the baseline. TSFGA has the highest peak in metalization and the second highest, after DDA, in planarization. In both processes it beats the baseline with the fewest features, the direct effect of the reduction term in its fitness."));
add(Fig("real_mra_size", [O("image5.png"), O("image6.png")], "MRA versus feature-subset size for (top) metalization and (bottom) planarization (real fab data). Subset sizes run up to the size of the filtered subset of the first stage.", 470, { stack: true }));
add(P("Table {{tab:mra_pfr}} reports MRA and PFR for all six processes with ranks in parentheses. TSFGA has the best MRA and the best PFR in four processes and the best average of both. PFI-SBS leads in lithography and DDA in planarization, each with a far larger subset. Table {{tab:cfs}} compares CFS merit: TSFGA is second to mRMR, whose selection criterion is a close relative of CFS, and the gap to mRMR is small next to the gap to the other three methods."));
add(Tbl("mra_pfr", "MRA and PFR of the compared methods (real fab data; rank in parentheses).",
  [["Major process", "MRA", "", "", "", "", "PFR", "", "", "", ""], ["", "mRMR", "MI", "DDA", "PFI-SBS", "TSFGA", "mRMR", "MI", "DDA", "PFI-SBS", "TSFGA"]],
  [["Lithography", "0.9066 (5)", "0.9088 (4)", "0.9210 (3)", "0.9376 (1)", "0.9360 (2)", "50.0% (1)", "22.2% (4)", "27.8% (3)", "22.2% (4)", "46.3% (2)"],
   ["Implantation", "0.9040 (5)", "0.9054 (4)", "0.9248 (2)", "0.9228 (3)", "0.9317 (1)", "35.2% (2)", "31.5% (3)", "18.5% (4)", "5.6% (5)", "48.1% (1)"],
   ["Etching", "0.8972 (5)", "0.8998 (4)", "0.9158 (3)", "0.9226 (2)", "0.9312 (1)", "37.1% (2)", "22.2% (4)", "24.1% (3)", "5.6% (5)", "48.1% (1)"],
   ["Metalization", "0.9258 (4)", "0.9240 (5)", "0.9379 (3)", "0.9398 (2)", "0.9450 (1)", "35.2% (3)", "40.7% (1)", "33.3% (4)", "31.9% (5)", "37.0% (2)"],
   ["Deposition", "0.9001 (4)", "0.8979 (5)", "0.9137 (2)", "0.9108 (3)", "0.9328 (1)", "35.2% (2)", "20.4% (3)", "11.1% (4)", "9.3% (5)", "59.3% (1)"],
   ["Planarization", "0.9250 (4)", "0.9239 (5)", "0.9369 (1)", "0.9325 (2)", "0.9308 (3)", "27.8% (2)", "25.9% (4)", "27.8% (2)", "24.1% (5)", "46.3% (1)"],
   ["Average", "0.9098", "0.9099", "0.9250", "0.9277", "0.9346", "36.7%", "27.2%", "23.8%", "16.4%", "47.5%"],
   ["Rank sum", "27", "27", "14", "13", "9", "12", "19", "20", "29", "8"]],
  [1500, 800, 800, 800, 900, 900, 800, 800, 800, 900, 900], { fontSize: 16 }));
add(Tbl("cfs", "CFS merit of the selected subsets (real fab data; rank in parentheses).",
  ["Major process", "mRMR", "MI", "DDA", "PFI-SBS", "TSFGA"],
  [["Lithography", "0.2928 (2)", "0.2684 (5)", "0.2808 (3)", "0.2804 (4)", "0.3014 (1)"], ["Implantation", "0.3082 (1)", "0.2754 (5)", "0.2810 (4)", "0.2907 (2)", "0.2828 (3)"],
   ["Etching", "0.2902 (2)", "0.2815 (3)", "0.2751 (5)", "0.2757 (4)", "0.3024 (1)"], ["Metalization", "0.3872 (1)", "0.3254 (3)", "0.3112 (5)", "0.3151 (4)", "0.3634 (2)"],
   ["Deposition", "0.2441 (1)", "0.2190 (4)", "0.2185 (5)", "0.2327 (3)", "0.2377 (2)"], ["Planarization", "0.2820 (3)", "0.2990 (1)", "0.2867 (2)", "0.2203 (5)", "0.2779 (4)"],
   ["Average", "0.3008", "0.2781", "0.2756", "0.2692", "0.2943"], ["Rank sum", "10", "21", "24", "22", "13"]],
  [2200, 1400, 1400, 1400, 1400, 1400]));
add(P("Collinearity inside the selected subsets was checked for metalization, where the subset sizes of the five methods are closest. Figs. {{fig:real_corr_abc}}–{{fig:real_corr_de}} show the absolute PCC between selected features; red bars exceed 0.8. mRMR, MI, DDA and PFI-SBS retain 6, 5, 4 and 2 such pairs. TSFGA retains none."));
add(Fig("real_corr_abc", O("image7.png"), "Absolute PCC among the selected features for the metalization process (real fab data): (a) mRMR, (b) MI, (c) DDA.", 620));
add(Fig("real_corr_de", O("image8.png"), "Absolute PCC among the selected features for the metalization process, continued: (d) PFI-SBS, (e) TSFGA. Red bars denote |r| > 0.8.", 620));
add(H("5.3. Summary of the case study", 2));
add(P("On all three criteria the case favors TSFGA. Accuracy: the best average MRA (0.9346 against 0.9277 for PFI-SBS, the runner-up) and first place in four of six processes; where it trails, it trails narrowly—0.16%p behind PFI-SBS in lithography, 0.61%p behind DDA in planarization—while keeping 24.1 and 18.5 percentage points fewer features. Reduction: 47.5% of the features removed against 16–37% for the other methods, giving the smallest subset in five processes. Redundancy: the only method with no collinear pair, and a CFS merit second only to mRMR, which optimizes a CFS-like criterion and pays with the lowest accuracy of the five methods, tied with MI (average MRA 0.9098). No competitor holds up on all three at once. DDA and PFI-SBS approach TSFGA on accuracy with subsets two to three times larger and collinear; mRMR and MI produce compact subsets and lose 2.5%p of MRA. For an engineer who needs a small, interpretable, collinearity-free set of CT factors, this is the practical case for the method."));

// ===== 6 Simulation study =====
add(H("6. Simulation study", 1));
add(P(`This section uses the simulated fab of Section 4.2 for the analyses the real data cannot support: an ablation of the two stages, a statistically tested comparison with the methods of Table {{tab:methods}}, the sensitivity to λ and τ, a chronological validation and the recovery of the true drivers. Numbers are averages over the ${D.n_combos} product–operation units and ${C.seeds} seeds unless stated otherwise. MRA levels are lower than on the real data because the simulated CT is heavy-tailed and each unit has only ${Math.round(D.data.rows_per_process / (D.n_combos / D.processes.length) * 0.5)} training rows; the comparisons, not the levels, carry the information.`));
add(H("6.1. Ablation of the two stages", 2));
{
  const a = D.ablation[D.ablation.length - 1];
  const dFilter = (parseFloat(a[2]) - parseFloat(a[1])) * 100;
  add(P(`Table {{tab:ablation}} compares the all-feature RF (ALL), the filter alone (FILTER), the GA on all 54 features (GA) and the full method (TSFGA). The filter alone removes about ${a[5]} of the features and ${Math.abs(dFilter) < 0.5 ? "leaves accuracy unchanged" : (dFilter < 0 ? `costs ${Math.abs(dFilter).toFixed(1)}%p of MRA` : `adds ${dFilter.toFixed(1)}%p of MRA`)}${dFilter < -0.2 ? "—with a noisy MI estimate, the discarded member of a correlated pair is occasionally the driver rather than its proxy" : ""}. The GA alone raises accuracy but keeps larger subsets (PFR ${a[6]}) with a wide seed-to-seed spread. The combination reaches the highest MRA with the smallest subsets (PFR ${a[7]}, ${a[8]} features). A Friedman test [49] over the ${D.ablation_stats.N} units rejects equality of the four configurations (χ^2^ = ${D.ablation_stats.chi2.toFixed(2)}, ${fmtP(D.ablation_stats.p)}); the average ranks are TSFGA ${D.ablation_stats.ranks.TSFGA}, GA ${D.ablation_stats.ranks.GA}, ALL ${D.ablation_stats.ranks.ALL} and FILTER ${D.ablation_stats.ranks.FILTER}, all further apart than the Nemenyi CD [38] of ${D.ablation_stats.CD.toFixed(2)}. TSFGA ranks first in ${D.ablation.slice(0, -1).filter(r => parseFloat(r[4]) >= Math.max(parseFloat(r[1]), parseFloat(r[2]), parseFloat(r[3]))).length} of ${D.processes.length} processes. Fig. {{fig:sim_violin}} shows the per-unit distributions; Fig. {{fig:sim_convergence}} shows the best fitness over generations. Pre-filtering starts the population in a better region, and the GA on the filtered space stalls later and higher than on the unfiltered space: best fitness ${D.best_fitness.TSFGA.toFixed(3)} against ${D.best_fitness.GA.toFixed(3)}, termination after ${Math.round(D.generations.TSFGA)} against ${Math.round(D.generations.GA)} generations on average.`));
}
add(Tbl("ablation", "Ablation on the simulated fab: MRA (mean ± standard deviation over seeds), PFR and selected-subset size.",
  [["Process", "MRA", "", "", "", "PFR", "", "", "# selected"], ["", "ALL", "FILTER", "GA", "TSFGA", "FILTER", "GA", "TSFGA", "TSFGA"]],
  D.ablation, [1700, 1300, 1300, 1300, 1300, 900, 900, 900, 900]));
add(Fig("sim_violin", R("main/fig_E1_violin_before_after.png"), "MRA distributions over product–operation units before (ALL) and after (TSFGA) selection on the simulated fab (seed 0)."));
add(Fig("sim_convergence", R("main/fig_E2_convergence.png"), "Convergence of the best fitness (mean ± standard deviation over seeds) for TSFGA, the GA on the unfiltered space, BPSO and BGWO."));
add(H("6.2. Comparison with twelve alternatives", 2));
add(P(`Table {{tab:baselines_avg}} lists the thirteen methods averaged over processes, ordered by Friedman average rank on MRA; Table {{tab:baselines_proc}} gives the per-process MRA with ranks. The Friedman test rejects equality (χ^2^ = ${D.friedman.chi2.toFixed(1)}, ${fmtP(D.friedman.p)}, N = ${D.friedman.N}, k = ${D.friedman.k}), with a Nemenyi CD of ${D.friedman.CD.toFixed(2)} ranks (Fig. {{fig:sim_cd}}). Table {{tab:wilcoxon}} gives the paired Wilcoxon tests [39] of TSFGA against each method.`));
add(Tbl("baselines_avg", "Feature selection methods on the simulated fab, averaged over processes and seeds (ordered by Friedman average rank on MRA).",
  ["Method", "MRA", "PFR", "CFS", "MAE", "RMSE", "R²", "# feat.", "# |r|>0.8", "Jaccard", "Time (s)", "Avg rank"],
  D.baseline_avg, [1200, 780, 700, 700, 700, 700, 700, 700, 800, 780, 780, 780], { fontSize: 16,
    note: "Jaccard: mean pairwise Jaccard index of the selected subsets across seeds (1 = identical). Time: wall-clock selection time per process on one CPU core. FILTER, ALL and LASSO are deterministic given the split." }));
{
  const M = D.baseline_per_process.methods, rows = D.baseline_per_process.rows;
  const procRows = rows.filter(r => r[0] !== "Average"), avgRow = rows.find(r => r[0] === "Average");
  const trows = M.map((m, j) => [m, ...procRows.map(r => r[1 + j]), avgRow[1 + j]]);
  add(Tbl("baselines_proc", "MRA per process on the simulated fab (rank within the process in parentheses; methods ordered by Friedman average rank).",
    ["Method", ...procRows.map(r => r[0]), "Average"], trows, [1300, ...procRows.map(() => 1100), 1100], { fontSize: 15 }));
}
add(Tbl("wilcoxon", "Paired Wilcoxon signed-rank tests of TSFGA against each method over product–operation units (MRA). Positive differences favor TSFGA.",
  ["Method", "Mean diff. (TSFGA − method)", "p-value", "Wins/ties/losses"], D.wilcoxon, [2000, 2600, 1600, 2000]));
add(Fig("sim_cd", R("E3_stats/fig_E3_cd_diagram_MRA.png"), "Nemenyi critical-difference diagram of the thirteen methods on MRA over product–operation units (lower rank is better; bars connect methods that are not significantly different)."));
add(P(`The two-stage design holds whichever optimizer occupies the second stage. TSFGA, BPSO and BGWO share the filter and the fitness, and all three beat no selection (TSFGA − ALL = +${pp("ALL")}%p MRA, ${w("ALL")[2] === "<0.0001" ? "p < 10^-4^" : "p = " + w("ALL")[2]}), the filter alone, LASSO and the GA on the unfiltered space (+${pp("GA")}%p, p = ${w("GA")[2]}). All three return subsets with no pair above |r| = 0.8 (column '# |r|>0.8'); the ranking wrappers keep ${b("DDA")[8]}–${b("PFI-SBS")[8]} such pairs, and MI, Boruta and ALL keep ${b("MI")[8]}–${b("ALL")[8]}.`));
add(P(`The optimizer itself changes the result. Under the same filter, fitness, population size and iteration count, BGWO reaches a higher best fitness than the GA (${D.best_fitness.BGWO.toFixed(3)} against ${D.best_fitness.TSFGA.toFixed(3)}, averaged over runs) and a higher MRA: +${pp("BGWO")}%p, Wilcoxon ${w("BGWO")[2] === "<0.0001" ? "p < 10^-4^" : "p = " + w("BGWO")[2]}, ${w("BGWO")[3].split("/")[2]} of ${D.friedman.N} units. It does so with ${b("BGWO")[7]} features on average, a seed-to-seed Jaccard index of ${b("BGWO")[9]} and one ninth of the run time, because its position update contracts onto a small subset within a few iterations and the memoized fitness is then rarely re-evaluated. BPSO also exceeds TSFGA (+${pp("BPSO")}%p). The GA, at the mutation rate *p*~m~ = ${C.pm} of the real-data study—about ${(C.pm * 43).toFixed(1)} gene flips per offspring in a 43-gene chromosome—stalls at a lower fitness with a far less stable subset (Jaccard ${b("TSFGA")[9]}). Appendix B shows that halving the mutation rate removes most of the difference.`));
add(P(`The ranking wrappers are the strongest competitors on this benchmark. PFI-SBS, RFE and DDA reach MRA ${b("RFE")[1]}–${b("PFI-SBS")[1]}, significantly above TSFGA at its reference setting, with 54 fitness evaluations; Boruta is indistinguishable from TSFGA (p = ${w("Boruta")[2]}). Fig. {{fig:sim_mra_size}} shows why. The generating model is sparse and largely additive, so a good importance ranking followed by a scan of the 54 nested subsets lands in the optimum region at once. Section 7 draws the consequences for the choice of method.`));
add(Fig("sim_mra_size", R(`main/fig_E6_mra_vs_size_${lastProc()}.png`), `Validation MRA versus subset size on the simulated fab (${lastProc()}): ranking-based methods as curves, stars mark the returned subsets, squares the smallest subsets exceeding the all-feature baseline (dashed).`));
add(H("6.3. Sensitivity to λ and τ", 2));
{
  const m = (k) => g(k).MRA.toFixed(4), kk = (k) => g(k).k.toFixed(1), pr = (k) => (100 * g(k).PRF).toFixed(1) + "%";
  add(P(`Table {{tab:sens}} and Fig. {{fig:sens_lambda_tau}} report the one-at-a-time sensitivity of TSFGA to its two method-specific parameters around the reference setting, averaged over the six processes and ${D.seeds_sens} seeds; the GA parameters are treated in Appendix B. λ sets the trade-off monotonically. From λ = 0.5 to λ = 10 the subset grows from ${kk("lambda=0.5")} to ${kk("lambda=10.0")} features (PFR ${pr("lambda=0.5")} to ${pr("lambda=10.0")}) and MRA rises from ${m("lambda=0.5")} to ${m("lambda=10.0")}; the return diminishes above λ = 5, where λ = 5 and λ = 10 give the same MRA. λ ≈ 2–5 is a reasonable range, and λ must be reported with every result. τ has a smaller, one-directional effect: the stricter the filter, the higher the MRA (${m("pcc_threshold=0.7")} at τ = 0.7, ${m("pcc_threshold=0.8")} at 0.8, ${m("pcc_threshold=0.9")} at 0.9, ${m("pcc_threshold=1.0")} with the filter disabled). This confirms the ablation from a second angle and suggests τ = 0.7 over the 0.8 used on the real data.`));
}
add(Tbl("sens", "One-at-a-time sensitivity of TSFGA to λ and τ on the simulated fab (averaged over processes and seeds).",
  ["Parameter", "Value", "MRA", "PFR", "# selected", "CFS"],
  D.sensitivity.filter(r => r[0] === "lambda" || r[0] === "pcc_threshold").map(r => [r[0] === "lambda" ? "λ" : "τ", r[1].replace(".0", ""), ...r.slice(2)]), [2000, 1200, 2000, 1400, 1400, 1400]));
add(Fig("sens_lambda_tau", [R("E4_sensitivity/fig_E4_lambda.png"), R("E4_sensitivity/fig_E4_pcc_threshold.png")], "Sensitivity of MRA (left panels) and PFR (right panels) to the fitness weight λ (top) and the PCC threshold τ (bottom), per process.", 600, { stack: true }));
add(H("6.4. Chronological validation", 2));
add(P(`Utilization and WIP drift over the simulated horizon, so a chronological split is the realistic deployment case. Table {{tab:temporal}} compares the random and chronological splits for ${D.temporal.methods.length} methods with ${D.seeds_temporal} seeds. The gain of TSFGA over the all-feature RF survives: ${(D.temporal_gain.temporal * 100).toFixed(1)}%p MRA under the chronological split against ${(D.temporal_gain.random * 100).toFixed(1)}%p under the random split, positive in every process (minimum ${(D.temporal_gain_min.temporal * 100).toFixed(1)}%p), with the ranking of methods unchanged. The improvements above are therefore not leakage between adjacent records. The subsets chosen under the two splits overlap only moderately (Jaccard ${Object.values(D.temporal_overlap).map(v => v.toFixed(2)).join(", ")} for ${Object.keys(D.temporal_overlap).join(", ")}); this instability is examined next.`));
{
  const M = D.temporal.methods, idx = (m) => 2 + M.indexOf(m);
  const pick = (split, proc) => D.temporal.rows.find(r => r[0] === split && r[1] === proc);
  const procs = [...new Set(D.temporal.rows.map(r => r[1]))];
  const cols = ["ALL", "PFI-SBS", "TSFGA"];
  const trows = procs.map(pr => [pr, ...cols.map(m => pick("random", pr)[idx(m)]), pick("random", pr).slice(-1)[0],
                                     ...cols.map(m => pick("temporal", pr)[idx(m)]), pick("temporal", pr).slice(-1)[0]]);
  add(Tbl("temporal", `Random versus chronological split on the simulated fab: MRA of the all-feature RF, the strongest ranking wrapper and TSFGA, and the gain of TSFGA over ALL (${D.seeds_temporal} seeds; the other methods of Table {{tab:methods}} are shown in Fig. {{fig:temporal}}).`,
    [["Process", "Random split", "", "", "", "Chronological split", "", "", ""], ["", "ALL", "PFI-SBS", "TSFGA", "TSFGA − ALL", "ALL", "PFI-SBS", "TSFGA", "TSFGA − ALL"]],
    trows, [1400, 900, 950, 900, 1050, 900, 950, 900, 1050], { fontSize: 16 }));
}
add(Fig("temporal", R("E7_temporal/fig_E7_temporal_vs_random.png"), "MRA of the compared methods under the random and chronological splits on the simulated fab."));
add(H("6.5. Stability, driver recovery and engineering insight", 2));
add(P(`The Jaccard column of Table {{tab:baselines_avg}} quantifies the instability. The GA-based methods vary strongly across seeds (TSFGA ${b("TSFGA")[9]}, GA ${b("GA")[9]}); the deterministic rankers (mRMR ${b("mRMR")[9]}, MI ${b("MI")[9]}) and BGWO (${b("BGWO")[9]}) do not. GA seeds reach subsets of similar fitness that differ in their weakly informative members and agree on the strong drivers: the features selected in every seed were ${Object.entries(D.tsfga_core_by_process).map(([p, f]) => `${f.join(", ")} (${p})`).join("; ")}—tool availability, the retained proxy of downtime, and a utilization statistic in every process. A majority-vote subset over several runs, not a single run, should therefore be reported.`));
add(P(`Table {{tab:recovery}} gives the precision, recall and F1 of driver recovery, a retained proxy counting as a hit. The population-based methods trade recall for compactness. BGWO keeps almost only drivers (precision ${D.recovery.find(r => r[0] === "BGWO")[1]}) but only ${(parseFloat(D.recovery.find(r => r[0] === "BGWO")[2]) * 100).toFixed(0)}% of them; TSFGA keeps ${(parseFloat(D.recovery.find(r => r[0] === "TSFGA")[2]) * 100).toFixed(0)}% of the drivers at a precision of ${D.recovery.find(r => r[0] === "TSFGA")[1]}, so its larger subsets carry noise features that the fitness cannot separate from weak drivers with ${Math.round(D.data.rows_per_process / (D.n_combos / D.processes.length) * 0.5)} training rows per unit. DDA and Boruta balance the two best (F1 ${D.recovery[0][3]} and ${D.recovery[1][3]}). Fig. {{fig:selfreq}} shows the selection frequency of every feature by TSFGA across seeds and processes. Across the six majority-vote TSFGA subsets, ${["machine", "workshop", "lot", "order"].map(c => D.category_share.reduce((a, r) => a + (r[c] || 0), 0)).reduce((a, b) => a + b, 0)} features are selected in total: ${D.category_share.reduce((a, r) => a + (r.machine || 0), 0)} machine-state, ${D.category_share.reduce((a, r) => a + (r.workshop || 0), 0)} workshop, ${D.category_share.reduce((a, r) => a + (r.lot || 0), 0)} lot and ${D.category_share.reduce((a, r) => a + (r.order || 0), 0)} order features—the same dominance of machine-state factors as in the real data. Fig. {{fig:shap}} gives the mean absolute SHAP values [37] of the majority-vote subset for ${lastProc()}: ${D.top_importance[lastProc()].slice(0, 3).map(t => t[0]).join(", ")} dominate, as in the generating model.`));
add(Tbl("recovery", "Recovery of the true CT drivers on the simulated fab (averaged over processes and seeds; a retained proxy of a driver counts as a hit).",
  ["Method", "Precision", "Recall", "F1"], D.recovery, [2200, 1600, 1600, 1600]));
add(Fig("selfreq", R("main/fig_E2_selection_frequency_TSFGA.png"), "Selection frequency of each feature by TSFGA across seeds, per process (simulated fab). Features are grouped by category (lot, machine, order, workshop).", 480));
add(Fig("shap", R(`E10_interpret/fig_E10_importance_${lastProc()}.png`), `Mean absolute SHAP value of the features in the majority-vote TSFGA subset for ${lastProc()} (simulated fab).`, 420));

// ===== 7 Discussion =====
add(H("7. Discussion", 1));
add(P(`Three results hold across the real-fab and the simulation study. The two stages are complementary: the filter removes the multicollinearity that CT feature selection methods have ignored, so the selected subsets contain no highly correlated pair on either dataset, and it shrinks the search space, so the GA terminates later and at a higher fitness than on the unfiltered space, with smaller subsets. The gain over the all-feature RF is robust: significant over ${D.friedman.N} product–operation units and ten seeds, present in every process, intact under a chronological split with drift, and reproduced on a second simulated fab instance with a different structure (results in the released repository). λ is the most influential setting of the method; λ ≈ 2–5 balanced the objectives here, and the value must be reported with any result.`));
add(P(`The second stage deserves as much attention as the filter. Under the same filter, fitness and budget, BGWO attains a higher fitness than the GA at the real-data settings and ${pp("BGWO")}%p more MRA, with ${b("BGWO")[7]} features, a Jaccard stability of ${b("BGWO")[9]} and a fraction of the run time; BPSO also exceeds the GA. Appendix B traces the difference to the mutation rate of ${C.pm} carried over from the real-data study. Halving it to 0.05 (≈2/*d*, consistent with the usual recommendation of order 1/*d* [22,23]) lifts the GA to MRA ${D.sens["ga.pm=0.05"].MRA.toFixed(4)}, within ${((parseFloat(b("BGWO")[1]) - D.sens["ga.pm=0.05"].MRA) * 100).toFixed(1)}%p of BGWO and level with the best ranking wrappers, with fewer and less redundant features. The real-data results were obtained at *p*~m~ = 0.1; that setting stays the reference, and the real-data gains are, if anything, understated. The ranking wrappers mark the other boundary. When the drivers are few and mainly additive, an importance ranking followed by a scan of nested subsets is cheaper than population-based search at the reference setting, at least as accurate and far more stable across runs. On the real data, where TSFGA led in four of six processes, the drivers evidently interact—the case in which a nested-subset scan misses combinations.`));
add(P("Table {{tab:protocol}} condenses these findings into a protocol, which we regard as a contribution in its own right. For the situations a CT engineer meets in practice, it names the method to use and the outcome to expect, with the trade-offs quantified on the benchmark. It also fixes two reporting practices without which results of stochastic feature selection cannot be compared: state λ, and report a majority-vote subset over several runs."));
add(Tbl("protocol", "Recommended protocol for feature selection in cycle-time prediction, with trade-offs quantified on the simulated fab (MRA gain over the all-feature RF, subset size, run time per process on one core).",
  ["Situation", "Recommended method", "Evidence"],
  [["Collinearity-free, interpretable subset required (root-cause analysis, engineering review)", "Two-stage method: PCC/MI filter (τ ≈ 0.7–0.8) + population-based search (TSFGA with *p*~m~ ≈ 2/*d*, or BGWO)", `0 pairs with |r| > 0.8 versus ${b("DDA")[8]}–${b("PFI-SBS")[8]} for ranking wrappers; MRA gain +${pp("ALL")}%p (TSFGA) to +${(parseFloat(b("BGWO")[1]) * 100 - parseFloat(b("ALL")[1]) * 100).toFixed(1)}%p (BGWO) with ${b("TSFGA")[7]}–${b("BGWO")[7]} features`],
   ["Interactions among factors expected; accuracy is the priority; compute budget available", "Two-stage method with GA (real data: first in 4 of 6 processes, +2.2%p, 47.5% reduction) or BGWO", `BGWO: best MRA and fitness on the benchmark; run time ${b("BGWO")[10]} s versus ${b("TSFGA")[10]} s for the GA`],
   ["Few, mainly additive drivers expected; small compute budget", "Ranking wrapper: PFI-SBS or RFE (54 fitness evaluations)", `MRA ${b("RFE")[1]}–${b("PFI-SBS")[1]} in ${b("PFI-SBS")[10]}–${b("RFE")[10]} s; Jaccard ${b("PFI-SBS")[9]}–${b("RFE")[9]}; ${b("DDA")[8]}–${b("PFI-SBS")[8]} collinear pairs remain`],
   ["Stability across runs required (subset to be frozen in a production model)", "BGWO, or majority vote over ≥ 5 runs of the GA", `Jaccard ${b("BGWO")[9]} (BGWO) versus ${b("TSFGA")[9]} (single GA runs)`],
   ["Any deployment", "Report λ (and τ); validate on a chronological split; re-validate the subset if the predictor is changed", `λ moves MRA by ${((g("lambda=10.0").MRA - g("lambda=0.5").MRA) * 100).toFixed(1)}%p and subset size from ${g("lambda=0.5").k.toFixed(1)} to ${g("lambda=10.0").k.toFixed(1)}; chronological gain ${(D.temporal_gain.temporal * 100).toFixed(1)}%p versus random ${(D.temporal_gain.random * 100).toFixed(1)}%p`]],
  [3000, 3100, 3260], { fontSize: 16, leftAlignAll: true }));

// ===== 8 Conclusions =====
add(H("8. Conclusions", 1));
add(P("This study developed TSFGA, a two-stage feature selection method for lot CT prediction in wafer fabrication: a PCC/MI redundancy filter followed by a GA whose fitness balances feature reduction against accuracy. On 577,236 real wafer-lot records the method removed 47.5% of the features, raised the MRA of a random forest by 2.2 percentage points, outperformed four feature selection methods from the CT literature and eliminated collinear feature pairs. On a simulated fab with known CT drivers, statistical tests over 90 product–operation units and ten seeds established that the two stages are complementary, that the gain over the all-feature model is robust and survives a chronological split, that λ sets the reduction–accuracy trade-off and must be reported, and that the selected features are the drivers of the generating model. The simulation also showed that the second-stage optimizer and its mutation rate matter—a binary grey wolf optimizer under the same filter and fitness outperformed the GA at the real-data settings, and halving the mutation rate recovered most of the difference—and it delimited the conditions under which ranking-based wrappers are competitive. A protocol for selecting features for CT prediction condenses these results."));
add(P("The limitations are these. The real-fab results come from one fab, one 90-day window and single runs, and the data are no longer accessible, so they could not be repeated with the tuned mutation rate. The simulated fab rests on queueing relationships but is simpler than discrete-event testbeds such as the Measurement and Improvement of Manufacturing Capacity (MIMAC) models [43] or the SMT2020 semiconductor manufacturing testbed [42]. All selection used a random forest; a subset selected with one learner has to be re-validated before another learner uses it. The mutation-rate finding rests on the simulation alone. Future work will validate the method on discrete-event fab testbeds and a second real fab with repeated runs, apply the tuned GA and the grey-wolf variant to real data, replace the weighted-sum fitness with a formulation that carries an explicit redundancy term, and connect the selected features to a CT-control loop with counterfactual explanations."));

// ===== back matter =====
add(H("CRediT authorship contribution statement", 1));
add(P("Seunghwan Song: Conceptualization, Methodology, Software, Investigation, Data curation, Writing – original draft, Visualization. Byung Kwon Lee: Conceptualization, Supervision, Validation, Writing – review & editing, Project administration, Funding acquisition."));
add(H("Declaration of competing interest", 1));
add(P("The authors report there are no competing interests to declare."));
add(H("Data availability", 1));
add(P("The data that support the findings of this study are available from the authors on reasonable request. The fab simulator and the experiment code are available at [repository URL to be added]."));
add(H("Acknowledgements", 1));
add(P("[Funding agency and grant number to be added.]"));

add(H("Appendix A. Feature catalog of the simulated fab", 1));
add(P("Table {{tab:appx_features}} lists the 54 features of the simulator. True CT drivers (present in the generating model) are marked with †; features marked ‡ are redundant proxies correlated at |r| > 0.8 with a driver; all others are noise. Process-specific drivers: number of layers (lithography, etching), batch size (deposition, implantation), set-up time (metalization, planarization)."));
{
  const cats = { lot: "Wafer lot characteristics", order: "Order characteristics", workshop: "Workshop condition", machine: "Machine state" };
  const trueAll = new Set(Object.values(D.true_features).flat());
  const proxies = new Set(D.redundant_groups.flatMap((gr) => gr.slice(1)));
  const rows = Object.keys(cats).map((c) => [cats[c], Object.entries(D.feature_category).filter(([, cc]) => cc === c)
    .map(([f]) => f + (trueAll.has(f) ? "†" : proxies.has(f) ? "‡" : "")).join(", "), String(Object.values(D.feature_category).filter((cc) => cc === c).length)]);
  add(Tbl("appx_features", "Features of the simulated fab by category.", ["Category", "Features", "#"], rows, [2200, 6100, 1000], { fontSize: 16, leftAlignAll: true }));
}
add(H("Appendix B. GA parameter settings and their sensitivity", 1));
{
  const m = (k) => g(k).MRA.toFixed(4), kk = (k) => g(k).k.toFixed(1);
  add(P(`The GA settings of Section 4.4 (*P* = ${C.pop}, *G* = ${C.gen}, *p*~c~ = ${C.pc}, *p*~m~ = ${C.pm}, two elites) were fixed in preliminary experiments on the real data over *P* ∈ {40, 80, 120}, *p*~c~ ∈ {0.3, 0.5, 0.8} and *p*~m~ ∈ {0.05, 0.1, 0.2} [placeholder—please confirm the ranges actually explored]. Table {{tab:appx_ga_sens}} and Fig. {{fig:appx_ga_sens}} report the one-at-a-time sensitivity of TSFGA to the same parameters on the simulated fab (six processes, ${D.seeds_sens} seeds, other settings at their reference values). Crossover rate and population size barely matter: MRA ${[m("ga.pc=0.3"), m("ga.pc=0.5"), m("ga.pc=0.8")].sort().filter((_, i, a) => i === 0 || i === a.length - 1).join("–")} over *p*~c~ and ${[m("ga.pop_size=40.0"), m("ga.pop_size=80.0"), m("ga.pop_size=120.0")].sort().filter((_, i, a) => i === 0 || i === a.length - 1).join("–")} over *P*, so the search budget is not the constraint. The mutation rate does. *p*~m~ = 0.05 raises MRA from ${m("ga.pm=0.1")} to ${m("ga.pm=0.05")} (+${((g("ga.pm=0.05").MRA - g("ga.pm=0.1").MRA) * 100).toFixed(1)}%p), shrinks the subset from ${kk("ga.pm=0.1")} to ${kk("ga.pm=0.05")} features and lifts the CFS merit from ${g("ga.pm=0.1").CFS.toFixed(3)} to ${g("ga.pm=0.05").CFS.toFixed(3)}; *p*~m~ = 0.2 worsens all three. At *p*~m~ = 0.05 the GA reaches MRA ${m("ga.pm=0.05")}, within ${((parseFloat(b("BGWO")[1]) - g("ga.pm=0.05").MRA) * 100).toFixed(1)}%p of BGWO (Table {{tab:baselines_avg}}). A rate of about 2/*d* for the *d* = 43 filtered features is therefore recommended. The 0.1 used on the real data flips about four genes per offspring, which keeps the population from settling on the small optima of this objective.`));
}
add(Tbl("appx_ga_sens", "One-at-a-time sensitivity of TSFGA to the GA parameters on the simulated fab (averaged over processes and seeds).",
  ["Parameter", "Value", "MRA", "PFR", "# selected", "CFS"],
  D.sensitivity.filter(r => r[0].startsWith("ga.")).map(r => [r[0].replace("ga.pm", "mutation rate p~m~").replace("ga.pc", "crossover rate p~c~").replace("ga.pop_size", "population size P"), r[1].replace(".0", ""), ...r.slice(2)]), [2400, 1000, 2000, 1400, 1400, 1400]));
add(Fig("appx_ga_sens", [R("E4_sensitivity/fig_E4_ga_pm.png"), R("E4_sensitivity/fig_E4_ga_pop_size.png")], "Sensitivity of MRA (left panels) and PFR (right panels) to the mutation rate (top) and the population size (bottom) of the GA, per process (simulated fab).", 600, { stack: true }));

add(H("References", 1));
const refs = [
  "T. Chen, H.C. Wu, A new cloud computing method for establishing asymmetric cycle time intervals in a wafer fabrication factory, J. Intell. Manuf. 28 (2017) 1095–1107.",
  "P. Backus, M. Janakiram, S. Mowzoon, C. Runger, A. Bhargava, Factory cycle-time prediction with a data-mining approach, IEEE Trans. Semicond. Manuf. 19 (2) (2006) 252–258.",
  "B. Mor, G. Mosheiov, D. Shabtay, A note: Minmax due-date assignment problem with lead-time cost, Comput. Oper. Res. 40 (8) (2013) 2161–2164.",
  "J.C. Serrano-Ruiz, J. Mula, R. Poler, Smart manufacturing scheduling: A literature review, J. Manuf. Syst. 61 (2021) 265–287.",
  "G.M. Lee, X. Gao, A hybrid approach combining fuzzy C-means-based genetic algorithm and machine learning for predicting job cycle times for semiconductor manufacturing, Appl. Sci. 11 (16) (2021) 7428.",
  "J. Wang, J. Zhang, X. Wang, A data driven cycle time prediction with feature selection in a semiconductor wafer fabrication system, IEEE Trans. Semicond. Manuf. 31 (1) (2018) 173–182.",
  "J. Wang, J. Zhang, Big data analytics for forecasting cycle time in semiconductor wafer fabrication system, Int. J. Prod. Res. 54 (23) (2016) 7231–7244.",
  "L. Lingitz, V. Gallina, F. Ansari, D. Gyulai, A. Pfeiffer, W. Sihn, L. Monostori, Lead time prediction using machine learning algorithms: A case study by a semiconductor manufacturer, Procedia CIRP 72 (2018) 1051–1056.",
  "F. Barhebwa-Mushamuka, S. Dauzère-Pérès, C. Yugma, A global scheduling approach for cycle time control in complex manufacturing systems, Int. J. Prod. Res. 61 (2) (2023) 559–579.",
  "I. Taifa, T. Vhora, Cycle time reduction for productivity improvement in the manufacturing industry, J. Ind. Eng. Manag. Stud. 6 (2) (2019) 147–164.",
  "D.Y. Sha, R.L. Storch, C.H. Liu, Development of a regression-based method with case-based tuning to solve the due date assignment problem, Int. J. Prod. Res. 45 (1) (2007) 65–82.",
  "Y.C. Wang, T. Chen, M.C. Chiu, An explainable deep-learning approach for job cycle time prediction, Decis. Anal. J. 6 (2023) 100153.",
  "T. Chen, Y.C. Wang, An iterative procedure for optimizing the performance of the fuzzy-neural job cycle time estimation approach in a wafer fabrication factory, Math. Probl. Eng. 2013 (2013) 740478.",
  "T. Chen, Y.C. Wang, A two-stage explainable artificial intelligence approach for classification-based job cycle time prediction, Int. J. Adv. Manuf. Technol. 123 (2022) 2031–2042.",
  "H. Yang, S. Kumara, S.T. Bukkapatnam, F. Tsung, The internet of things for smart manufacturing: A review, IISE Trans. 51 (11) (2019) 1190–1216.",
  "G. Chandrashekar, F. Sahin, A survey on feature selection methods, Comput. Electr. Eng. 40 (1) (2014) 16–28.",
  "Y. Meidan, B. Lerner, G. Rabinowitz, M. Hassoun, Cycle-time key factor identification and prediction in semiconductor manufacturing using machine learning and data mining, IEEE Trans. Semicond. Manuf. 24 (2) (2011) 237–248.",
  "J. Wang, P. Zheng, J. Zhang, Big data analytics for cycle time related feature selection in the semiconductor wafer fabrication system, Comput. Ind. Eng. 143 (2020) 106362.",
  "K. Schelthoff, C. Jacobi, E. Schlosser, D. Plohmann, M. Janus, K. Furmans, Feature selection for waiting time predictions in semiconductor wafer fabs, IEEE Trans. Semicond. Manuf. 35 (3) (2022) 546–555.",
  "X.F. Song, Y. Zhang, D.W. Gong, X.Y. Sun, Feature selection using bare-bones particle swarm optimization with mutual information, Pattern Recognit. 112 (2021) 107804.",
  "M. Ghosh, R. Guha, R. Sarkar, A. Abraham, A wrapper-filter feature selection technique based on ant colony optimization, Neural Comput. Appl. 32 (2020) 7839–7857.",
  "J.J. Grefenstette, Optimization of control parameters for genetic algorithms, IEEE Trans. Syst. Man Cybern. 16 (1) (1986) 122–128.",
  "A. Hassanat, K. Almohammadi, E. Alkafaween, E. Abunawas, A. Hammouri, V.B.S. Prasath, Choosing mutation and crossover ratios for genetic algorithms—a review with a new dynamic approach, Information 10 (12) (2019) 390.",
  "T.C. Tin, K.L. Chiew, S.C. Phang, S.N. Sze, P.S. Tan, Incoming work-in-progress prediction in semiconductor fabrication foundry using long short-term memory, Comput. Intell. Neurosci. 2019 (2019) 8729367.",
  "J. Louzada, C.G. Camilo-Junior, A. Vincenzi, C. Rodrigues, An elitist evolutionary algorithm for automatically generating test data, in: Proc. IEEE Congr. Evol. Comput. (CEC), 2012, pp. 1–8.",
  "S. Rathee, S. Ratnoo, Feature selection using multi-objective CHC genetic algorithm, Procedia Comput. Sci. 167 (2020) 1656–1664.",
  "W. Fang, Y. Guo, W. Liao, K. Ramani, S. Huang, Big data driven jobs remaining time prediction in discrete manufacturing system: a deep learning-based approach, Int. J. Prod. Res. 58 (9) (2020) 2751–2766.",
  "F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, É. Duchesnay, Scikit-learn: Machine learning in Python, J. Mach. Learn. Res. 12 (2011) 2825–2830.",
  "T. Chen, Y.C. Wang, A modified random forest incremental interpretation method for explaining artificial and deep neural networks in cycle time prediction, Decis. Anal. J. 7 (2023) 100226.",
  "J. Kennedy, R.C. Eberhart, A discrete binary version of the particle swarm algorithm, in: Proc. IEEE Int. Conf. Syst. Man Cybern., vol. 5, 1997, pp. 4104–4108.",
  "E. Emary, H.M. Zawbaa, A.E. Hassanien, Binary grey wolf optimization approaches for feature selection, Neurocomputing 172 (2016) 371–381.",
  "K. Deb, A. Pratap, S. Agarwal, T. Meyarivan, A fast and elitist multiobjective genetic algorithm: NSGA-II, IEEE Trans. Evol. Comput. 6 (2) (2002) 182–197.",
  "M.B. Kursa, W.R. Rudnicki, Feature selection with the Boruta package, J. Stat. Softw. 36 (11) (2010) 1–13.",
  "R. Tibshirani, Regression shrinkage and selection via the lasso, J. R. Stat. Soc. Ser. B 58 (1) (1996) 267–288.",
  "I. Guyon, J. Weston, S. Barnhill, V. Vapnik, Gene selection for cancer classification using support vector machines, Mach. Learn. 46 (2002) 389–422.",
  "H. Peng, F. Long, C. Ding, Feature selection based on mutual information: criteria of max-dependency, max-relevance, and min-redundancy, IEEE Trans. Pattern Anal. Mach. Intell. 27 (8) (2005) 1226–1238.",
  "S.M. Lundberg, S.-I. Lee, A unified approach to interpreting model predictions, in: Adv. Neural Inf. Process. Syst. 30, 2017, pp. 4765–4774.",
  "J. Demšar, Statistical comparisons of classifiers over multiple data sets, J. Mach. Learn. Res. 7 (2006) 1–30.",
  "F. Wilcoxon, Individual comparisons by ranking methods, Biometrics Bull. 1 (6) (1945) 80–83.",
  "M.A. Hall, Correlation-based feature selection for machine learning, PhD thesis, University of Waikato, Hamilton, New Zealand, 1999.",
  "L.J. Eshelman, The CHC adaptive search algorithm: how to have safe search when engaging in nontraditional genetic recombination, in: Foundations of Genetic Algorithms, vol. 1, Morgan Kaufmann, 1991, pp. 265–283.",
  "D. Kopp, M. Hassoun, A. Kalir, L. Mönch, SMT2020—A semiconductor manufacturing testbed, IEEE Trans. Semicond. Manuf. 33 (4) (2020) 522–531.",
  "J.W. Fowler, J. Robinson, Measurement and improvement of manufacturing capacity (MIMAC) designed experiment report, SEMATECH Technology Transfer #95062861A-TR, 1995.",
  "B. Xue, M. Zhang, W.N. Browne, X. Yao, A survey on evolutionary computation approaches to feature selection, IEEE Trans. Evol. Comput. 20 (4) (2016) 606–626.",
  "L. Breiman, Random forests, Mach. Learn. 45 (1) (2001) 5–32.",
  "W.J. Hopp, M.L. Spearman, Factory Physics, third ed., Waveland Press, Long Grove, IL, 2011.",
  "G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, T.-Y. Liu, LightGBM: A highly efficient gradient boosting decision tree, in: Adv. Neural Inf. Process. Syst. 30, 2017, pp. 3146–3154.",
  "A. Kraskov, H. Stögbauer, P. Grassberger, Estimating mutual information, Phys. Rev. E 69 (2004) 066138.",
  "M. Friedman, The use of ranks to avoid the assumption of normality implicit in the analysis of variance, J. Am. Stat. Assoc. 32 (200) (1937) 675–701.",
  "P. Gao, J. Wang, R. Zhong, J. Zhang, Neuron synergy based explainable neural network for manufacturing cycle time forecasting, J. Manuf. Syst. 71 (2023) 695–706.",
  "T.C.T. Chen, C.W. Lin, Y.C. Lin, A fuzzy collaborative forecasting approach based on XAI applications for cycle time range estimation, Appl. Soft Comput. 151 (2024) 111122.",
  "Y.-C. Wang, Explainability driven post-hoc correction enhancing deep neural network performance for job cycle time prediction, Int. J. Adv. Manuf. Technol. 142 (2026) 107–118.",
  "P.C. Deenen, J. Middelhuis, A. Akcay, I.J.B.F. Adan, Data-driven aggregate modeling of a semiconductor wafer fab to predict WIP levels and cycle time distributions, Flex. Serv. Manuf. J. 36 (2) (2024) 567–596.",
  "A. Wartelle, S. Dauzère-Pérès, C. Yugma, Q. Christ, R. Roussel, Forecasting wafer fab outputs using lot remaining cycle time prediction in semiconductor manufacturing, in: Proc. 2025 IEEE 21st Int. Conf. Autom. Sci. Eng. (CASE), Los Angeles, CA, USA, 2025, pp. 911–914.",
  "R. Jiao, B.H. Nguyen, B. Xue, M. Zhang, A survey on evolutionary multiobjective feature selection in classification: approaches, applications, and challenges, IEEE Trans. Evol. Comput. 28 (4) (2024), https://doi.org/10.1109/TEVC.2023.3292527.",
  "J. Senoner, T. Netland, S. Feuerriegel, Using explainable artificial intelligence to improve process quality: evidence from semiconductor manufacturing, Manag. Sci. 68 (8) (2022) 5704–5723.",
  "M. Hammami, S. Bechikh, C.-C. Hung, L. Ben Said, A multi-objective hybrid filter-wrapper evolutionary approach for feature selection, Memetic Comput. 11 (2019), https://doi.org/10.1007/s12293-018-0269-2.",
  "T.C.T. Chen, Y.C. Lin, Fuzzified deep neural network ensemble approach for estimating cycle time range, Appl. Soft Comput. 130 (2022) 109697.",
];
refs.forEach((r, i) => add(new Paragraph({ children: runs(`[${i + 1}] ${r}`, { size: 20 }), spacing: { after: 60, line: 260 }, indent: { left: 500, hanging: 500 }, alignment: AlignmentType.LEFT })));

// ---------------------------------------------------------------- document
const doc = new Document({
  creator: "CTFS manuscript builder v4",
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: "000000" }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: "000000" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, italics: true, color: "000000" }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
    ] },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("wrote", outPath, "figures:", figNo, "tables:", tabNo); });
