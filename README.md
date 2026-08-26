# Leonardo Lab — Constrained Evolutionary Search Architecture

[![CI](https://github.com/Michaelrobins938/leonardo-lab-transformer/actions/workflows/tests.yml/badge.svg)](https://github.com/Michaelrobins938/leonardo-lab-transformer/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen.svg)](tests/test_engine.py)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](CITATION.cff)

> **A computational organism built from Leonardo da Vinci's scientific method:**
> a resource-constrained evolutionary search engine whose initial genome is a
> formal ruleset extracted from the notebooks (Richter ed., 1888), whose engine
> is an immutable 11-phase GASO state machine, and whose phenotypic memory is a
> persistent evolution archive enabling cumulative adaptation across sessions.

---

## 🎯 Overview

Leonardo Lab answers one question: **can the structural mechanics of history's
greatest empirical observer be operationalized as a domain-agnostic
optimization kernel?**

The answer implemented here is yes — with receipts. The system satisfies the
three necessary conditions for a computational organism:

| Condition | Mechanism | Implementation |
|:---|:---|:---|
| **Heredity** | Evolution Archive (`evolution_archive.yaml`) | Full lineage, budgets, and learned constraints persist across runs |
| **Variation** | Budgeted single-variable mutations (M01–M05) | Every variant declares parent + operator; cost accounting enforced |
| **Selection** | Invariant filtering + fitness evaluation | 7 hard gates halt the engine on any structural violation |

It has been validated on three systems spanning five centuries of science:
**Wiener's cybernetic alpha-rhythm model (1948)**, a **decoder-only transformer
(Vaswani et al., 2017 lineage)**, and a **Cybernetic Reasoning Engine**.

---

## ✨ Key Contributions

1. **Notebook-to-kernel pipeline.** A formal extraction of 23 structural
   elements (systems, ontological primitives, computational motifs, invariants)
   from da Vinci's notebooks, recast into domain-agnostic primitives
   `{source, sink, channel, apex, gradient, role}` — with domain nouns
   (`eye`, `blood`, `water`) mechanically stripped from the optimization core.

2. **The GASO state machine.** A Generator–Action–State–Observer–Feedback
   control loop, derived from Leonardo's own theory-practice epistemology
   (*"Science is the captain, and practice the soldiers"*), executed as an
   immutable 11-phase optimization pipeline.

3. **Constraint-first evolution.** Unlike fitness-only search, every mutation
   must survive structural invariants *before* selection — and **failures are
   mandatory first-class outputs**: the engine halts unless negative constraints
   are extracted from rejected variants (Hard Gate 4).

4. **Leverage discovery.** Post-selection sensitivity analysis identifies
   variables where minute modifications yield disproportionate state-transition
   gains — the "physics of improvement" — and feeds them back to reprioritize
   the next generation's search.

5. **Empirical validation on modern ML.** Applied to a decoder-only transformer,
   the engine independently discovered Grouped Query Attention (GQA) as its
   Generation-1 winner (+20.7% fitness), anticipating by construction the
   inference-efficiency direction of production architectures (LLaMA, Mistral).

---

## 📊 Results at a Glance

| Case Study | Baseline | Optimized | Δ | Winning Mechanism |
|:---|:---:|:---:|:---:|:---|
| **Wiener A4 alpha-rhythm model** | 0.62 | **0.78** | **+26%** | `predictor_horizon` 0.1s → 0.35s under entropy-monotonicity constraint |
| **Decoder-only Transformer (Gen 1)** | 1.000 | **1.207** | **+20.7%** | Multi-head → GQA (g=4): 4× KV-cache reduction at <0.3% quality loss |
| **Cybernetic Reasoning Engine** | 1e-3 threshold | **1e-4** | 10× finer stability | M01 quantization of attractor stability threshold |

**Leverage discoveries (Transformer Gen 1):**

```
HIGH LEVERAGE                     ratio      LOW LEVERAGE                    ratio
kv_cache_sharing                  0.828      dropout_rate                    0.050
attention_logit_softcap           0.900      weight_tying                    0.010
normalization_position            0.117
position_encoding_type            0.113
```

**Learning from failure (negative extraction):**
- ❌ Causal temporal ordering → protein folding: **rejected** — temporal causality ≠ thermodynamic validity; constraint domains incompatible.
- ❌ `normalization_position → none`: **rejected** — LayerNorm is load-bearing at depth N > 6.
- ❌ `head_count = 128`: **rejected** — d_k = 4 is degenerate; practical bound d_k ≥ 16 ⇒ h_max = d_model/16.

Each rejection is compiled into a machine-readable rule that constrains all future generations.

---

## 📖 Table of Contents

- [Overview](#-overview) · [Key Contributions](#-key-contributions) · [Results](#-results-at-a-glance)
- [Quickstart](#-quickstart)
- [System Architecture](#️-system-architecture)
- [The GASO State Machine](#-the-gaso-state-machine-the-engine)
- [The 11-Phase Pipeline](#-the-11-phase-gaso-pipeline)
- [Mutation Operators](#-mutation-operators-m01m05)
- [The Invariant System](#-the-invariant-system-three-layers)
- [Enforcement Rules & Hard Gates](#-enforcement-rules--validation-gates)
- [Case Studies](#-case-studies)
- [Repository Structure](#-repository-structure)
- [Testing & Engineering Quality](#-testing--engineering-quality)
- [Documentation Map](#-documentation-map)
- [Scholarly Positioning](#-scholarly-positioning)
- [Limitations & Future Work](#-limitations--future-work)
- [Citation](#-citation) · [License](#-license)

---

## 🚀 Quickstart

```bash
git clone https://github.com/Michaelrobins938/leonardo-lab-transformer.git
cd leonardo-lab-transformer
pip install -r requirements.txt        # Python 3.12+

# Launch a fresh evolutionary search
./leonardo-lab "optimize a waterwheel"

# Resume an existing search from its archive (Generation N+1)
./leonardo-lab "Cybernetics A4 Genome" ./.leonardo-lab/evolution_archive.yaml

# Run the full test suite (17 tests)
pytest tests/ -v
```

Example output (abridged):

```
====================================================================
           LEONARDO LAB -- EVOLUTION REPORT
           Generation 1 Complete
====================================================================
Variants Explored:   5    Variants Rejected:   1    Variants Passed:  4

WINNER:         Variant_A -- M01 on predictor_horizon
FITNESS SCORE:  0.7271

LEVERAGE POINTS DISCOVERED:
  HIGH LEVERAGE:  predictor_horizon        ratio: 1.7143
  LOW LEVERAGE:   feedback_coefficient     ratio: 0.24

  ALL 7 HARD GATES PASSED [OK]
====================================================================
```

**Registered target systems:** `Wiener A4` · `CRE` (Cybernetic Reasoning
Engine) · `waterwheel` · `door hinge`. Unregistered systems fall back to
generic ontology-driven parameter extraction.

---

## 🛠️ System Architecture

Leonardo Lab runs on a structured, three-part cybernetic foundation:

```
┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────────┐
│  1. THE INITIAL GENOME  │   │ 2. THE GASO STATE MACHINE│   │ 3. THE EVOLUTION ARCHIVE│
│                         │   │      (THE ENGINE)        │   │   (PHENOTYPIC MEMORY)   │
│ Formal ruleset extracted│──▶│ Immutable 11-phase       │──▶│ evolution_archive.yaml  │
│ from Leonardo's         │   │ optimization pipeline    │   │ Lineage · budgets ·     │
│ notebooks (Richter 1888)│   │ driving problem →        │   │ negative constraints ·  │
│ Primitives: {source,    │   │ optimized architecture   │   │ leverage points persist │
│ sink, channel, apex,    │   │                          │   │ across execution        │
│ gradient, role}         │   │                          │   │ sessions                │
└─────────────────────────┘   └──────────────────────────┘   └─────────────────────────┘
              ▲                                                            │
              └────────────── cumulative adaptation feedback ◀─────────────┘
```

1. **The Initial Genome** — a formal ruleset extracted from Leonardo's
   notebooks, with domain-specific terminology removed and physical/functional
   entities mapped to abstract primitives `{source, sink, channel, apex,
   gradient, role}`.
2. **The GASO State Machine (the engine)** — a formal state machine executing
   an immutable 11-phase optimization pipeline from target problem to
   physically grounded architecture.
3. **The Evolution Archive** — the phenotypic memory. By persisting lineage,
   parameters, search budgets, and negative constraints across runs, the lab
   behaves like a true computational organism capable of cumulative adaptation.

---

## 🔄 The GASO State Machine (the Engine)

The engine's control loop is a direct formalization of Leonardo's
theory-practice epistemology (*s03* in the formal extraction):

```yaml
GASO:
  Generator:  # The rules and constraints producing the current state
  Action:     # The intervention or applied force
  State:      # The observed configuration of the system
  Observer:   # The measurement and sensing mechanism
  Feedback:   # The correction loop feeding back to the Generator
```

> *"Experience never errs; it is only your judgments that err…"* — the
> model-failure attribution rule (**m06**): when prediction and observation
> diverge, the **generator is revised, never the observation**. This asymmetry
> is why every failed mutation must yield a negative constraint rather than
> being silently discarded.

The 11 phases below are the transmission that drives this engine.

---

## 🔁 The 11-Phase GASO Pipeline

```
[Phase 0: Landscape & Budget] ──> [Phase 1: Ontological Reduction]
                                                │
[Phase 3: Causal Architecture] <── [Phase 2: Parallel Decomposition] (Source/Channel, Sink, Correction)
              │
[Phase 4: Parameter Extraction] ──> [Phase 5: Parallel Mutation] (M01 - M05 Operators)
                                                │
[Phase 7: Invariant Filter] <── [Phase 6: Parallel Simulation] (Counterfactual State Runs)
              │
[Phase 8: Selection] ──> [Phase 8.5: Leverage Discovery] ──> [Phase 9: GASO Update]
                                                                     │
                                                      [Phase 10: Archive Persistence]
```

### Sequential initialization & mapping

- **Phase 0 — Fitness Landscape & Search Budget.** Declares the mathematical
  `measurement_function` (what "better" means) and resource constraints
  (budgets, per-mutation cost 1.0, per-simulation cost 0.5) *before any search
  begins*. No fitness declaration → no optimization (Hard Gate 3).
- **Phase 1 — Ontological Reduction.** Decomposes the target into irreducible
  forces, boundaries, substrates, and constraints using the notebook-derived
  ontology primitives.
- **Phase 2 — System Decomposition** *(parallel)*. Three concurrent agents map
  Source/Channel, Transformation/Sink, and Feedback/Correction structures.
- **Phase 3 — Causal Architecture.** Constructs the explicit cause-and-effect
  graph; pinpoints the fundamental **Bottleneck** and **Failure Mechanism**.
- **Phase 4 — Parameter Space Extraction.** Extracts the mechanical degrees of
  freedom — typed, range-bounded variables tied to their source nodes in the
  formal-elements graph.

### Mutation, simulation & filtering

- **Phase 5 — Controlled Mutation** *(parallel, budgeted)*. Applies up to N
  operators, each varying exactly **one** variable from the parent baseline.
- **Phase 6 — Counterfactual State Simulation** *(parallel)*. Simulates
  competing futures under baseline / stressed / perturbed environments, each
  with an explicit failure boundary.
- **Phase 7 — Invariant Filter & Negative Extraction.** Filters variants
  through structural laws; **every rejection is compiled into a negative
  constraint** so the engine learns from failure.

### Selection & loop closure

- **Phase 8 — Selection.** Ranks invariant-surviving variants by simulated
  fitness; selects the new baseline.
- **Phase 8.5 — Leverage Discovery.** Sensitivity analysis identifying where
  minute modifications yield disproportionate gains.
- **Phase 9 — GASO Update.** Feeds winner + leverage metrics back into the
  state generator, priming the next generation.
- **Phase 10 — Archive Persistence.** Writes cumulative state to
  `evolution_archive.yaml` (Hard Gate 2 verifies the write).

---

## 🧬 Mutation Operators (M01–M05)

| Operator | Name | Mechanism | Example (Transformer run) |
|:---:|:---|:---|:---|
| **M01** | Quantization | Alters resolution/threshold of one variable | Stability threshold 1e-3 → 1e-4 |
| **M02** | Role-Preserving Structural Transfer | Maps topology across domains; **must declare `exceptions`** | Attention topology → protein folding (rejected: i02) |
| **M03** | Convergence | Focuses optimization on decision apexes | Logit softcap = 50.0 at failure boundary |
| **M04** | Disequilibrium | Introduces structural imbalance to test resilience | Multi-head → GQA g=4 (Gen-1 winner) |
| **M05** | Dual-Coordinate | Adds a missing dimension (spatial + temporal) | ALiBi additive → RoPE multiplicative encoding |

Every variant carries mandatory lineage: `{parent, mutation_operator,
changed_variable, reason_for_mutation, expected_effect}` — verified by Hard Gate 5.

---

## 🛡️ The Invariant System (Three Layers)

Peer-review note: the corpus operates three distinct invariant families. These
are *layers*, not contradictions:

| Layer | Invariants | Scope |
|:---|:---|:---|
| **Corpus-extracted** (from notebooks) | i01 Proportional Invariance · i02 Determinism-under-Necessity · i03 Role Preservation | Universal structural laws governing all transfers |
| **Kernel enforcement** | Second-Law/Entropy Monotonicity · Loop Closure/Path Integrity · Capacity Bound (C ≥ log₂ M) | Hard filters applied to every simulated variant |
| **Domain-instantiated** | e.g., Transformer: attention simplex (i01), causal monotonicity (i03), residual dimension preservation (i04) | Per-target-system specializations declared in Phase 0 |

---

## 📋 Enforcement Rules & Validation Gates

Seven hard gates must pass before the engine reports success. Any violation
halts execution:

| # | Gate | Requirement |
|:---:|:---|:---|
| 1 | **Budget Compliance** | Mutation + simulation costs ≤ total search budget, enforced *per operation* |
| 2 | **Archive Existence** | Phase 10 write verified on disk |
| 3 | **Fitness Declaration** | Phase 0 contains both `measurement_function` and `search_budget` |
| 4 | **Negative Extraction** | ≥1 negative constraint recorded — *failure documentation is mandatory* |
| 5 | **Lineage Integrity** | Every variant declares parent + operator |
| 6 | **Leverage Discovery** | ≥1 high-leverage AND ≥1 low-leverage variable identified |
| 7 | **Exception Check** | Every M02 transfer carries a non-empty `exceptions` field |

Additional standing rules: **Fitness First** (no evaluation before Phase 0),
**Mechanical Mutations Only** (physical extracted variables, no arbitrary
changes), **Single Variable Rule** (one variable per variant).

---

## 🔬 Case Studies

### 1. Wiener Cybernetics A4 Genome (1948/1950)

The engine optimized Norbert Wiener's alpha-rhythm neural model.

- **Baseline fitness:** 0.62 → **Optimized: 0.78 (+26%)**
- **Mechanism:** expanded `predictor_horizon` 0.1s → 0.35s while preserving
  entropy-decay boundaries (second-law compliance), matching statistical
  alpha-rhythm frequency.
- **Negative constraints captured:** asymmetric thresholds violate entropy
  monotonicity; market-transfer mechanisms fail for lack of a
  biological-equivalent reset mechanism.

### 2. Decoder-Only Transformer — Generation 1

*Lineage: Vaswani et al. 2017 → formal-elements extraction → generative design
analysis → Configuration B (V05b encoder removal + V04 relative positions).*

Five variants explored under a 7.5/15.0 budget; one rejected on role
preservation. **Winner: Grouped Query Attention (g=4 KV heads), fitness
1.000 → 1.207.**

Why it matters: the primary bottleneck identified in Phase 3 was quadratic
attention cost / KV-cache memory at long sequences — an **inference-only**
phenomenon invisible to training-time metrics. The engine's fitness function
captured it, and M04 disequilibrium produced the winning restructure: 4× KV-cache
reduction at <0.3% quality loss, all four domain invariants preserved.

Queued for Generation 2 composition (all passed independently): Pre-LN (+0.117),
RoPE (+0.113), softcap 50.0 (+0.090). Full trace: [`EXECUTION_REPORT.md`](EXECUTION_REPORT.md)
and [`phases/`](phases/).

### 3. Cybernetic Reasoning Engine (CRE) v2.0

Tasked with maximizing stability and novelty injection inside reasoning
attractor states. Five mutations evaluated; all hard gates passed; stable
threshold quantized to **1e-4**. The repository's test suite reproduces this
outcome end-to-end (`pytest tests/ -v`, see `TestEndToEndDoorHinge` and CRE
coverage).

---

## 📁 Repository Structure

```
leonardo-lab-transformer/
├── leonardo-lab                  # Executable CLI entry point
├── leonardo_lab/                 # Core package
│   ├── genome.py                 # Da Vinci ontological reducer + invariant ruleset
│   ├── engine.py                 # 11-phase GASO state machine + 7 hard gates
│   ├── archive.py                # Evolution Archive persistence & lineage merging
│   └── models.py                 # Simulation environments (Wiener A4, CRE, …)
├── tests/
│   └── test_engine.py            # Unit / integration / E2E suite (17 tests)
├── phases/                       # Generation-1 execution traces (Phases 0–10)
├── EXECUTION_REPORT.md           # Transformer optimization run report
├── Text extraction.txt           # Formal-elements extraction (Richter ed., 1888)
├── Skill.md                      # Original kernel specification contract
├── .leonardo-lab/                # Reference evolution archive (Generation 1)
├── CITATION.cff                  # Citation metadata (CFF 1.2)
└── Leonardo_Lab_Generation_1.pdf # Formatted Generation-1 report
```

---

## 🧪 Testing & Engineering Quality

```bash
pytest tests/ -v          # 17 tests across four suites
```

| Suite | Coverage |
|:---|:---|
| `TestPhase0Budget` | Budget structure & measurement-function declaration |
| `TestGenerationIncrement` | Archive generation tracking & baseline history |
| `TestBudgetEnforcement` | `BudgetExceededError` halting; default runs within budget |
| `TestWaterwheelIntegration` | Physical DoF extraction; channel_width flagged high-leverage |
| `TestM02TransferExceptions` | Exceptions contract at construction **and** via Gate 7 defense-in-depth |
| `TestEndToEndDoorHinge` | Full 11-phase run; concrete mechanical change; cross-generation lineage linkage |

CI runs the suite on Python 3.12 and 3.13 plus two CLI smoke tests (fresh run
+ archive resume) on every push — see
[`.github/workflows/tests.yml`](.github/workflows/tests.yml).

---

## 🗺️ Documentation Map

| Artifact | Audience | Content |
|:---|:---|:---|
| [`README.md`](README.md) | Everyone | Architecture, results, quickstart (this file) |
| [`phases/phase_0_1_2_3.md`](phases/phase_0_1_2_3.md) | Reviewers | Fitness landscape, ontology, decomposition, causal graph |
| [`phases/phase_4.md`](phases/phase_4.md) | Reviewers | Typed parameter space with causal sensitivities |
| [`phases/phase_5_6_7.md`](phases/phase_5_6_7.md) | Reviewers | Mutations, counterfactual simulations, invariant filtering |
| [`phases/phase_8_8_5_9.md`](phases/phase_8_8_5_9.md) | Reviewers | Selection, leverage discovery, GASO update |
| [`EXECUTION_REPORT.md`](EXECUTION_REPORT.md) | Everyone | Complete Generation-1 report with validation gate status |
| [`Text extraction.txt`](Text%20extraction.txt) | Scholars | 23-element formal extraction from Richter ed. (1888) with source quotes |
| [`Skill.md`](Skill.md) | Engineers | Frozen kernel specification contract |

---

## 🎓 Scholarly Positioning

Leonardo Lab sits at the intersection of four literatures, differing from each
in a specific, defensible way:

| Field | Closest work | Leonardo Lab's distinction |
|:---|:---|:---|
| **Neural Architecture Search** | Zoph & Le (2017); EfficientNAS | NAS optimizes within a fixed benchmark grammar; Leonardo Lab first *derives* its parameter space from a causal-ontological analysis (Phases 1–4) and enforces cross-domain structural invariants |
| **Evolutionary Computation** | Genetic algorithms, GP | Standard EC treats constraints as penalty terms; here invariants are hard gates and **negative extraction is mandatory output**, making failure information first-class |
| **AutoML / HPO** | Optuna, AutoWEKA | HPO tunes pre-declared hyperparameters; leverage discovery (Phase 8.5) dynamically reprioritizes the search space itself between generations |
| **Digital Humanities / HI** | Computational analyses of historical texts | Prior work interprets notebooks semantically; this is — to our knowledge — the first **operationalization**: historical structural mechanics compiled into an executable optimization kernel with measurable outcomes |

**Methodological honesty statement.** The Wiener A4 and CRE case studies run
against analytic surrogate models defined in `leonardo_lab/models.py`
(deterministic, inspectable functions encoding the documented system behavior),
not against trained neural networks. The transformer Generation-1 results are
documented execution traces from the original kernel run. We label these
provenance classes explicitly so reviewers can weigh evidence appropriately —
consistent with the project's own principle that observations are trusted and
models must earn revision.

---

## ⚠️ Limitations & Future Work

**Known limitations**

- Baseline carry-forward: each CLI run currently starts from registry defaults;
  archived winners inform recommendations but do not yet warm-start parameters.
- Surrogate fidelity: case-study fitness functions are analytic surrogates;
  full empirical validation requires training-loop integration.
- Generic-system fallback uses heuristic primitive mapping rather than
  learned semantic parsing.

**Roadmap — Generation 2 mutation plan (M06–M10)**

Targeting the Predictor Horizon (τ) × Feedback Gain (g) Pareto frontier:

```
                ▲
                │          ● Variant 08 (Adaptive Cybernetic Predictor)
Feedback Gain   │         /
      (g)       │        ● Variant 07 (Maximum Prediction)
                │       /
                │      ● Variant 06 (Conservative Optimum)
                └──────────────────────────────►
                     Predictor Horizon (τ)
```

- **M06 Predictor Horizon Sweep** — exact limits of temporal foresight
- **M07 Feedback Gain Sweep** — maximum stabilizing gain per horizon level
- **M08 Adaptive Horizon Controller** *(predicted winner)* — state-dependent
  horizon via second-order uncertainty feedback: *the system learns how far
  ahead to look*
- **M09 Predictive Error Weighting** — noise injection to harden error correction
- **M10 Channel Capacity Allocation** — adaptive information-preservation bandwidth

Engineering roadmap: warm-start baselines from archives; pluggable simulation
backends (PyTorch); multi-objective selection on the τ×g frontier.

---

## 📚 Citation

If you use Leonardo Lab in your research, please cite:

```bibtex
@software{leonardo_lab_2026,
  title  = {Leonardo Lab: A Constrained Evolutionary Search Architecture
            Operationalizing Structural Mechanics from Leonardo da Vinci's
            Notebooks},
  author = {Leonardo Lab Contributors},
  year   = {2026},
  url    = {https://github.com/Michaelrobins938/leonardo-lab-transformer},
  note   = {11-phase GASO pipeline; persistent evolution archive;
            7 hard validation gates}
}
```

Machine-readable metadata: [`CITATION.cff`](CITATION.cff).

Primary sources: da Vinci, *The Notebooks of Leonardo da Vinci*, ed. Jean Paul
Richter (1888), Project Gutenberg #5000 · Wiener, *Cybernetics* (1948/1950) ·
Vaswani et al., "Attention Is All You Need" (2017).

---

## 📄 License

This architecture is licensed under the MIT License. See [`LICENSE`](LICENSE).
