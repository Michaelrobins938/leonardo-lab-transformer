# Leonardo Lab — Constrained Evolutionary Search Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

**Leonardo Lab** is a high-fidelity, resource-constrained evolutionary search engine designed for the optimization of complex systems. The system operationalizes the structural mechanics extracted from Leonardo da Vinci’s scientific notebooks, recasting his mechanical insights into a domain-agnostic evolutionary kernel.

The architecture integrates a **ruleset derived from Leonardo's notebooks** as the initial system genome, uses the **GASO State Machine** as the evolutionary engine, and persists a continuous lineage of mutations in the **Evolution Archive** to enable phenotypic memory and cumulative adaptation across execution sessions.

---

## 🛠️ System Architecture

Leonardo Lab runs on a structured, three-part cybernetic foundation:

1. **The Initial Genome**: A formal ruleset extracted from Leonardo da Vinci’s historical notebooks (e.g., Richter ed., 1888), removing domain-specific terminology (like "eye," "blood," "water") and mapping physical and functional entities to abstract primitives: `{source, sink, channel, apex, gradient, role}`.
2. **The GASO State Machine (The Engine)**: A formal state machine executing an immutable, 11-phase optimization pipeline that drives the transition from a target problem to a highly optimized, physically grounded architecture.
3. **The Evolution Archive (`evolution_archive.yaml`)**: The phenotypic memory of the system. By persisting lineage, parameters, search budgets, and negative constraints across runs, the lab behaves like a true computational organism capable of cumulative adaptation.

---

## 🔄 The 11-Phase GASO Pipeline

Every evolutionary cycle is governed sequentially and in parallel through 11 rigorous phases:

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

### 1. Sequential Initialization & Mapping
*   **Phase 0: Fitness Landscape & Search Budget Definition**  
    Declares the mathematical `measurement_function` (what "better" means) and defines resource constraints (total search budget, mutation costs, and simulation costs) before any search or optimization can begin.
*   **Phase 1: Ontological Reduction**  
    Breaks down the target system using formal YAML ontology primitives to define irreducible physical forces, boundaries, substrates, and constraints.
*   **Phase 2: System Decomposition (Parallel Execution)**  
    Spawns three parallel task agents to map the system's structural channels:
    *   *Agent 1 (Source/Channel Mapping)*
    *   *Agent 2 (Transformation/Sink Mapping)*
    *   *Agent 3 (Feedback/Correction Mapping)*
*   **Phase 3: Causal Architecture**  
    Establishes the explicit cause-and-effect pathways of the system, pinpointing the fundamental **Bottleneck** and **Failure Mechanism**.
*   **Phase 4: Parameter Space Extraction**  
    Extracts the **mechanical degrees of freedom** (DoF) from the causal graph. These are the physical variables that can be modified.

### 2. Mutation, Simulation & Filtering
*   **Phase 5: Controlled Mutation (Parallel & Budgeted)**  
    Applies up to $N$ mutation operators (limited by the iteration variant budget) to vary exactly **one** variable at a time from the extracted parameter space. The primary operators are:
    *   `M01 (Quantization)`: Alters the resolution or threshold of a variable (e.g., stability thresholds).
    *   `M02 (Role-Preserving Structural Transfer)`: Maps structural topology to another domain, requiring an explicit `exceptions` field for non-transferable characteristics.
    *   `M03 (Convergence)`: Focuses optimization on decision-making apexes or attractors.
    *   `M04 (Disequilibrium)`: Introduces structural instability to test system resilience.
    *   `M05 (Dual-Coordinate)`: Introduces a missing dimension (e.g., spatial + temporal).
*   **Phase 6: Counterfactual State Simulation (Parallel Execution)**  
    Simulates competing futures for each mutated variant under diverse, stressful environment conditions.
*   **Phase 7: Invariant Filter & Negative Extraction**  
    Filters simulated variants through strict physical and structural laws:
    *   `i01 (Second-Law Compliance / Entropy Monotonicity)`: Prevents thermodynamic violations.
    *   `i02 (Loop Closure / Path Integrity)`: Ensures all feedback paths form a closed, complete loop.
    *   `i03 (Capacity Bound)`: Ensures total communication channel capacity matches or exceeds message variety.
    
    *Failed mutations are compiled into negative constraints so the engine learns from its failures.*

### 3. Selection & Loop Closure
*   **Phase 8: Selection**  
    Ranks surviving variants that passed all invariants and selects the optimal configuration based on their simulated fitness score.
*   **Phase 8.5: Leverage Discovery**  
    Analyzes the sensitivity of variables to identify where minute modifications yield disproportionate state-transition gains, extracting the "physics of improvement."
*   **Phase 9: GASO State Machine Update**  
    Feeds the selected configuration and leverage metrics back to update the state generator, priming the system for the next generation.
*   **Phase 10: Evolution Archive Persistence**  
    Writes the cumulative state, lineages, and negative constraints to the central `evolution_archive.yaml`.

---

## 📋 Core Enforcement Rules & Validation Gates

The laboratory enforces severe operational safeguards to prevent "p-hacking" or ungrounded optimizations:

| Rule/Gate | Requirement |
| :--- | :--- |
| **Fitness First** | No mutations or evaluations may occur without defining Phase 0 objectives. |
| **Resource Pressure** | System halting occurs immediately if simulation/mutation costs exceed the search budget. |
| **Mechanical Mutations** | Variations must only target physical, extracted variables (no abstract or arbitrary changes). |
| **Single Variable Rule** | A mutated variant can modify exactly one variable from the parent baseline. |
| **Role Preservation (M02)**| Any cross-domain structural transfer must explicitly declare its limits (the `exceptions` field). |
| **Negative Extraction** | Every run must record and document why invalid mutations failed (preventing cyclic errors). |
| **Lineage Tracking** | Every variant must maintain a traceable parent identifier and a declared mutation operator. |

---

## 🔬 Target Optimization Case Studies

### 1. Cybernetics A4 Genome (Wiener, 1948/1950)
The evolutionary engine was tasked with optimizing Norbert Wiener's cybernetic alpha-rhythm neural model.
*   **Baseline Fitness**: `0.62`
*   **Optimized Winner (Variant 03)**: Successfully achieved a **fitness score of 0.78** (a 26% improvement).
*   **Mechanism of Optimization**: The engine expanded the `predictor_horizon` parameter from $0.1$ to $0.35$ seconds while preserving entropy decay boundaries (second-law compliance), matching the statistical frequency of neurological alpha rhythms.
*   **Negative Constraints Captured**:
    *   *Asymmetric thresholds* violated second-law monotonicity (Entropy violation).
    *   *Market transfer mechanisms* failed due to the absence of a biological-equivalent reset mechanism.

### 2. Cybernetic Reasoning Engine (CRE) / Generative Eigen-Engine v2.0
Tasked with maximizing stability and novelty injections inside the system's reasoning attractor states. 
*   **Variants Evaluated**: 5 distinct mutations (M01 Coarser Stability Threshold, M02 Neural Transfer, M03 Attractor Count Reduction, M04 Novelty Injection, M05 History Compression Rate).
*   **Outcome**: Successfully passed all hard gates, updated the GASO machine, and quantized the stable threshold to $1 \times 10^{-4}$.

---

## 🔮 Roadmap: Generation 2 Mutation Plan

The upcoming iteration (Generation 2) targets the optimization of the **Predictor Horizon ($\tau$) × Feedback Coefficient ($g$) Pareto Frontier** to enhance robustness during system state transitions:

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

*   **M06: Predictor Horizon Sweep** — Identifies the exact limits of temporal foresight.
*   **M07: Feedback Gain Sweep** — Establishes maximum stabilizing feedback gains for each horizon level.
*   **M08: Adaptive Horizon Controller (Predicted Winner)** — Replaces the static predictor horizon with a state-dependent horizon managed by a second-order uncertainty feedback loop. *The system learns to adaptively decide how far into the future it should look.*
*   **M09: Predictive Error Weighting** — Integrates noise injection to harden loop error corrections.
*   **M10: Channel Capacity Allocation** — Deploys dynamic, adaptive information-preservation bandwidth channels.

---

## 💻 Installation & CLI Usage

```bash
# Install dependencies (Python 3.12+)
pip install -r requirements.txt

# Initialize a new evolutionary search for a target system
./leonardo-lab "optimize a waterwheel"

# Resume an existing evolutionary search from a saved archive
./leonardo-lab "Cybernetic Reasoning Engine" ./.leonardo-lab/evolution_archive.yaml
```

Registered target systems include `Wiener A4` (cybernetic alpha-rhythm model), `CRE` (Cybernetic Reasoning Engine), `waterwheel`, and `door hinge`. Unregistered systems fall back to a generic ontology-driven parameter extraction.

### 📁 Repository Structure

```
leonardo-lab-transformer/
├── leonardo-lab                  # Executable CLI entry point
├── leonardo_lab/                 # Core package
│   ├── genome.py                 # Da Vinci ontological reducer + invariant ruleset (i01–i03)
│   ├── engine.py                 # 11-phase GASO state machine + 7 hard validation gates
│   ├── archive.py                # Evolution Archive persistence & lineage merging
│   └── models.py                 # Simulation environments (Wiener A4, CRE, waterwheel, hinge)
├── tests/
│   └── test_engine.py            # Unit / integration / E2E suite (17 tests)
├── phases/                       # Generation-1 execution traces (Phases 0–10)
├── EXECUTION_REPORT.md           # Transformer optimization run report
├── Text extraction.txt           # Formal-elements extraction from Richter ed. (1888)
├── Skill.md                      # Original kernel specification contract
└── CITATION.cff                  # Academic citation metadata
```

### Development & Testing
Run the test suite to verify structural and causal engine integrity:
```bash
# Execute unit and integration tests (Structural checks, M02 transfers, E2E evolution loops)
pytest tests/ -v
```

---

## 📄 License
This architecture is licensed under the MIT License. See `LICENSE` for details.
