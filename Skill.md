allowed-tools: Read, Write, Bash, Task, Grep, Glob

description: "Constrained evolutionary search kernel. Defines fitness landscape, extracts mechanical DOF, performs budgeted single-variable mutations with lineage, runs counterfactual simulations, filters by structural invariants, discovers leverage points, persists state to archive, and iterates GASO state machine."

argument-hint: "[target system or problem description] [optional: path to existing evolution_archive.yaml]"

---

# /leonardo-lab

## Overview

This is a **constrained evolutionary search architecture** with persistent state. It does not generate suggestions or summaries. It constructs a fitness landscape, extracts mechanical degrees of freedom, mutates variables under resource pressure, runs counterfactual simulations, filters by structural invariants, discovers high-leverage points, and preserves all evolutionary history in a persistent archive.

The YAML ruleset derived from Leonardo's notebooks acts as the **initial genome**. The GASO state machine acts as the **engine**. The Evolution Archive (Phase 10) acts as the **phenotypic memory**, enabling true cumulative adaptation across sessions.

This command operationalizes the extracted structural mechanics of Leonardo's notebooks as a **domain-agnostic evolutionary kernel** satisfying the three necessary conditions for a computational organism: heredity (archive persistence), variation (budgeted mutations), and selection (invariant filtering + fitness evaluation).

---

## The GASO State Machine (Foundation)

```yaml

GASO:

Generator: # The rules and constraints producing the current state

Action: # The intervention or applied force

State: # The observed configuration of the system

Observer: # The measurement and sensing mechanism

Feedback: # The correction loop feeding back to the Generator

```

This machine is the **engine**. The 11 phases below are the **transmission** that drives it.

---

## Variables

- **$1**: The target system, problem, or process to optimize.

- **$2 (Optional)**: Path to an existing `evolution_archive.yaml` to resume evolution. If omitted, a new archive is initialized in `./.leonardo-lab/evolution_archive.yaml`.

---

## Core Enforcement Rules

1. **Fitness First**: Optimization cannot begin without Phase 0 declaring a `measurement_function` and `search_budget`.

2. **Resource Pressure**: The engine must respect `search_budget.max_variants_per_iteration`. Mutations cost budget.

3. **State Persistence**: Every run must read the existing `evolution_archive.yaml` (if present) and write the updated archive upon completion.

4. **Mechanical Mutations Only**: Mutations must be applied to specific **mechanical degrees of freedom** extracted in Phase 4.

5. **Single Variable Rule**: A single variant changes exactly **one** variable from the parameter space.

6. **Role-Preserving Transfer**: Any structural transfer must explicitly state what **does not** transfer (the `exceptions` field).

7. **Negative Extraction**: The engine must explicitly record failed analogies and invalid mutations in the archive.

8. **Lineage Tracking**: Every variant must declare its parent and the operator used.

9. **Leverage Discovery**: The engine must identify variables with disproportionate state-transition effects and store them in the archive.

---

## Pipeline (11-Phase Evolutionary Engine)

```

PHASE 0 → Fitness Landscape + Search Budget

|

v

PHASE 1 → Ontological Reduction

|

v

PHASE 2 → System Decomposition (Parallel)

|

v

PHASE 3 → Causal Architecture

|

v

PHASE 4 → Parameter Space Extraction

|

v

PHASE 5 → Controlled Mutation (Parallel, Budgeted)

|

v

PHASE 6 → Counterfactual Simulation (Parallel)

|

v

PHASE 7 → Invariant Filter + Negative Extraction

|

v

PHASE 8 → Selection

|

v

PHASE 8.5 → Leverage Discovery

|

v

PHASE 9 → GASO Update

|

v

PHASE 10 → Evolution Archive Persistence

|

└─────────────┐

              |

              v

       Next Generation

```

---

### Phase 0: Fitness Landscape & Search Budget Definition

**Dependency:** None.

**Execution Mode:** Sequential.

**Task:** Define what "better" means and set the resource constraints for this evolutionary search.

This phase ensures the engine has an explicit objective function before any mutation occurs. Without this, selection is arbitrary.

**Required Output:**

```yaml

fitness_landscape:

objective:

primary:

  metric: \<throughput, accuracy, efficiency, cost, etc.\>

  direction: maximize | minimize | target

secondary:

  - metric: \<e.g., energy_cost\>

    weight: \<0.0 to 1.0\>

  - metric: \<e.g., maintenance_frequency\>

    weight: \<0.0 to 1.0\>

constraints:

forbidden_states:

  - \<catastrophic_failure\>

  - \<invalid_structural_state\>

tradeoffs:

accepted:

  - \<tradeoff 1\>

rejected:

  - \<tradeoff 2\>

measurement_function:

formula: \<throughput / cost\>

inputs:

  - \<variable 1\>

  - \<variable 2\>

outputs:

  - \<fitness_score\>

search_budget:

max_variants_per_iteration: 5 # Total mutations to generate per run

max_iterations: 10 # Global cap (if archive tracks generation count)

mutation_cost: 1.0 # Relative cost of generating a variant

simulation_cost: 0.5 # Relative cost of simulating a variant

total_budget: 15.0 # Total cost allowed per iteration (mutation + simulation)

```

---

### Phase 1: Ontological Reduction

**Dependency:** Phase 0.

**Execution Mode:** Sequential.

**Task:** Break down the user's `$1` using the YAML's ontology primitives (`o01`, `o02`).

This phase identifies the irreducible forces, constraints, and substrate of the system. It answers: *"What exists? What forces operate?"*

**Required Output:**

```yaml

ontology:

primitives:

driver: \<primary moving force\>

resistance: \<primary friction\>

perturbation: \<external disturbance\>

state_bias: \<inertia/momentum of the current state\>

constraints:

deterministic_rules: \<list of governing laws\>

substrate: <the physical/logical medium>

organizing_layer: <the structure maintaining coherence>

GASO_current_state:

generator: \<initial generator rules\>

action: \<none yet\>

state: \<current configuration\>

observer: \<measurement mechanism\>

feedback: \<none yet\>

```

---

### Phase 2: System Decomposition (Parallel)

**Dependency:** Phase 1.

**Execution Mode:** **Parallel**.

**Agent Strategy:** Spawn 3 parallel `Task` agents for Source/Channel, Transformation/Sink, and Feedback/Correction.

**Task:** Map the mechanistic components using `s01` (Convergent Projection), `s02` (Branching Transport), and `m01` (Causal Chain).

**Parallel Execution:**

```bash

Task: "Map Source/Channel for [System] using s01 (Convergent Projection) and s02 (Branching Transport)."

Task: "Map Transformation/Sink using m01 (Derivative Generation / Causal Chain)."

Task: "Map Feedback/Correction using m06 (Model-Failure Attribution)."

```

**Required Output:** A component graph showing:

```text

Entity A -> Role -> Connects to Entity B

Entity C -> Role -> Connects to Entity D

...

```

---

### Phase 3: Causal Architecture

**Dependency:** Aggregated output from Phase 2.

**Execution Mode:** Sequential.

**Task:** Construct the explicit cause-and-effect graph. Identify the **Bottleneck** and the **Failure Mechanism**.

**Required Output:**

```text

CAUSAL GRAPH:

[Generator] → [Substrate Action] → [State Change] → [Observation] → [Correction/Divergence]

BOTTLENECK: <Where flow constricts>

FAILURE MECHANISM: <Specific interaction causing breakage>

```

---

### Phase 4: Parameter Space Extraction

**Dependency:** Phase 3.

**Execution Mode:** Sequential.

**Task:** Extract the **mechanical degrees of freedom** from the causal architecture. This defines what can actually be varied.

**Required Output:**

```yaml

parameter_space:

variable:

name: <e.g., friction_coefficient>

type: resistance # (resistance, transport_capacity, projection_geometry, state_bias, etc.)

range:

min: \<numerical or logical minimum\>

max: \<numerical or logical maximum\>

unit: <if applicable>

variable:

name: <e.g., channel_width>

type: transport_capacity

range:

min: \<numerical\>

max: \<numerical\>

variable:

name: <e.g., convergence_distance>

type: projection_geometry

range:

min: \<numerical\>

max: \<numerical\>

```

---

### Phase 5: Controlled Mutation (Parallel, Budgeted)

**Dependency:** Phase 4.

**Execution Mode:** **Parallel**, subject to `search_budget.max_variants_per_iteration`.

**Agent Strategy:** Spawn up to N `Task` agents, where N = `max_variants_per_iteration` (default 5). Each agent applies a distinct mutation operator (M01–M05) strictly bound to a variable from Phase 4.

**Mutation Operators (M01–M05):**

- **M01 (Quantization):** Change the resolution/threshold of a specific variable (e.g., price points, timeout thresholds).

- **M02 (Role-Preserving Structural Transfer):** Transfer the topology to another domain. **Must explicitly state exceptions.**

- **M03 (Convergence):** Focus optimization on the apex/decision point.

- **M04 (Disequilibrium):** Introduce a deliberate imbalance to test resilience.

- **M05 (Dual-Coordinate):** Add a missing dimension (e.g., temporal + spatial).

**Parallel Execution:**

```bash

Task: "Apply M01 (Quantization) to variable [X]. Produce Variant 01."

Task: "Apply M02 (Role-Preserving Transfer) to variable [Y]. Produce Variant 02."

Task: "Apply M04 (Disequilibrium) to variable [Z]. Produce Variant 03."

```

**Required Output (including Lineage):**

```yaml

variant:

name: Variant 01

lineage:

parent: \<Baseline | Archive last winner\>

mutation_operator: \<M01\>

changed_variable: \<exact variable name\>

reason_for_mutation: \<Why this operator was chosen\>

expected_effect: \<Hypothesis\>

# For M02, strictly enforce this structure:

source_structure:

reservoir: \<source element\>

channel: \<propagation element\>

boundary: \<constraint element\>

target_structure:

reservoir_equivalent: \<mapped element\>

channel_equivalent: \<mapped element\>

boundary_equivalent: \<mapped element\>

mapping_confidence: <high/medium/low>

exceptions: <EXPLICITLY STATE what does NOT transfer and why>

```

---

### Phase 6: Counterfactual State Simulation (Parallel)

**Dependency:** Phase 5.

**Execution Mode:** **Parallel**.

**Agent Strategy:** Spawn 1 `Task` agent per variant generated in Phase 5.

**Task:** Simulate competing futures under different environmental conditions.

**Required Output:**

```yaml

simulation:

variant: <Variant #>

environment: <baseline | stressed | perturbed>

initial_state: <state before action>

transition_rules: <how variables interact>

future_state_t1: <predicted state at time 1>

future_state_t2: <predicted state at time 2>

failure_boundary: <The exact threshold where this configuration breaks>

fitness_score: <Calculated using Phase 0 measurement_function>

```

---

### Phase 7: Invariant Filter & Negative Extraction

**Dependency:** Phase 6.

**Execution Mode:** Sequential.

**Task:** Filter all simulated variants through the YAML's formal invariants (`i01`: Proportionality, `i02`: Causal Order, `i03`: Role Preservation). Explicitly record why configurations are rejected.

**Required Output:**

```yaml

invariant_validation:

variant: Variant 01

status: REJECTED

violated_invariant: i02 (Causal Order)

reason: "Action occurred before Generator state was established."

variant: Variant 02

status: PASSED

reason: "Proportional relationships preserved."

negative_constraints:

failed_transfer:

source: <source structure>

target: <target structure>

reason: "Structural homomorphism does not hold due to [exception]."

invalid_mutation:

variable: <variable name>

reason: "Mutation caused violation of [invariant]."

```

---

### Phase 8: Selection

**Dependency:** Phase 7.

**Execution Mode:** Sequential.

**Task:** Rank the surviving (PASSED) variants by their counterfactual performance (fitness_score from Phase 6). Select the new baseline.

**Required Output:**

```text

SELECTED DESIGN:

Winner: [Variant #]

Reason: [Passed all invariants. Highest fitness_score.]

Tradeoffs Accepted: [List of secondary effects tolerated]

```

---

### Phase 8.5: Leverage Discovery

**Dependency:** Phase 8.

**Execution Mode:** Sequential.

**Task:** Identify variables where small changes produced disproportionate state transitions. This extracts the "physics of improvement."

**Required Output:**

```yaml

leverage_points:

variable: <name>

magnitude_of_change: <delta>

magnitude_of_effect: <delta in fitness/state>

leverage_ratio: <effect / change>

explanation: <Why this variable has high leverage>

variable: <name>

magnitude_of_change: <delta>

magnitude_of_effect: <delta in fitness/state>

leverage_ratio: <effect / change>

explanation: <Why this variable has low leverage or is inert>

```

---

### Phase 9: GASO Update & Iteration Preparation

**Dependency:** Phase 8.5.

**Execution Mode:** Sequential.

**Task:** Feed the selected configuration and discovered leverage points back into the `GASO` state machine. The `Generator` is updated with the new rules, and the `State` is redefined.

**Required Output:**

```yaml

GASO_updated:

generator: <Updated rules incorporating the Winner's mechanism>

action: <Recommended next intervention based on leverage>

state: <New baseline state configuration>

observer: <Existing/Updated measurement>

feedback: <Active correction loop enabled>

ITERATION_READY: TRUE

Next_Input: <Ready to feed back into Phase 0 with new baseline>

```

---

### Phase 10: Evolution Archive Persistence (CRITICAL)

**Dependency:** Phase 9.

**Execution Mode:** Sequential.

**Task:** Persist the entire evolutionary history to `./.leonardo-lab/evolution_archive.yaml`. If the archive exists (via $2 or default location), merge the new generation. If not, create it.

This phase ensures the engine accumulates knowledge across sessions, functioning as a true evolutionary system rather than a stateless optimizer.

**Required Output (Written to Disk):**

```yaml

# ./.leonardo-lab/evolution_archive.yaml

evolution_archive:

system_identity:

name: \<target system\>

domain: \<category\>

generation:

number: \<increment from existing archive + 1\>

baseline_history:

- generation: 1

  configuration: \<baseline config\>

  fitness_score: \<score\>

  selected_variant: \<winner name\>

- generation: 2

  configuration: \<updated config\>

  fitness_score: \<score\>

  selected_variant: \<winner name\>

successful_mutations:

- mutation_operator: \<M01\>

  variable: \<name\>

  magnitude: \<delta\>

  effect: \<delta fitness\>

  leverage_ratio: \<effect/change\>

- mutation_operator: \<M03\>

  variable: \<name\>

  magnitude: \<delta\>

  effect: \<delta fitness\>

  leverage_ratio: \<effect/change\>

failed_mutations:

- variable: \<name\>

  mutation_operator: \<op\>

  failure_reason: \<why\>

  violated_invariant: \<invariant\>

- variable: \<name\>

  mutation_operator: \<op\>

  failure_reason: \<why\>

  violated_invariant: \<invariant\>

learned_constraints:

- rule: \<new constraint derived from failures\>

- rule: \<another constraint\>

parameter_sensitivity:

high_leverage:

  - variable: \<name\>

  - variable: \<name\>

low_leverage:

  - variable: \<name\>

current_genome:

GASO:

  generator: \<updated\>

  action: \<recommended\>

  state: \<new baseline\>

  observer: \<current\>

  feedback: \<enabled\>

search_budget_remaining:

max_iterations: \<remaining\>

```

---

## Validation & Quality Assurance (Hard Gates)

The following hard gates must pass before the engine reports success. If any gate fails, the engine halts and reports the violation.

1. **Budget Compliance**: Total cost (mutations * mutation_cost + simulations * simulation_cost) must not exceed `search_budget.total_budget`. If exceeded, halt.

2. **Archive Existence**: Phase 10 must successfully write the archive. If write fails, halt.

3. **Fitness Declaration**: Phase 0 must contain both `measurement_function` and `search_budget`. If missing, halt.

4. **Negative Extraction**: Phase 7 must contain at least one `negative_constraints` entry (failure is expected; documenting it is mandatory). If none, halt.

5. **Lineage Integrity**: Every variant in Phase 5 must declare a `parent` and `mutation_operator`. If any missing, halt.

6. **Leverage Discovery**: Phase 8.5 must output at least one high-leverage and one low-leverage variable. If missing, halt.

7. **Exception Check**: Any M02 (Role-Preserving Transfer) variant must have a non-empty `exceptions` field. If empty, halt.

---

## Test Suite

### Unit Tests (Structural Integrity)

- [ ] **Test 1**: Does Phase 0 include `search_budget` with `mutation_cost`, `simulation_cost`, and `total_budget`?

- [ ] **Test 2**: Does Phase 10 correctly increment `generation` when an archive already exists?

- [ ] **Test 3**: Does the engine halt if `total_budget` is exceeded before Phase 5 completes?

### Integration Tests (Causal Soundness)

- [ ] **Test 4**: Run on "optimize a waterwheel." Does Phase 4 extract `channel_width` and `friction_coefficient` as variables (physical), and does Phase 8.5 correctly identify `channel_width` as high-leverage?

- [ ] **Test 5**: Run M02 on "supply chain" transferring to "blood circulation." Does the `exceptions` field correctly flag that "inventory storage" has no biological equivalent?

### End-to-End Evolution Test

- [ ] **Test 6**: Provide a simple system (e.g., "improve a door hinge"). Run the full 11 phases. Verify that the final `GASO_updated.generator` specifies a specific mechanical change (e.g., "increase pivot diameter" or "reduce friction coefficient") rather than a vague process improvement. Then run a second iteration and verify that the archive contains a traceable lineage and that `parameter_sensitivity` updates.

---

## Final Output Checklist

Before reporting success, the engine must confirm all items are complete:

- [ ] Phase 0: Fitness Landscape + Search Budget declared.

- [ ] Phase 1: Ontology + GASO initial state declared.

- [ ] Phase 2: Parallel component decomposition complete.

- [ ] Phase 3: Causal map + Bottleneck identified.

- [ ] Phase 4: Parameter space with typed ranges extracted.

- [ ] Phase 5: Budget-respecting, lineage-tracked, single-variable mutations generated.

- [ ] Phase 6: Counterfactual simulations with failure boundaries run.

- [ ] Phase 7: Invariant filtering + Negative constraints recorded.

- [ ] Phase 8: Winner selected based on structural validity and fitness.

- [ ] Phase 8.5: Leverage ratios discovered and documented.

- [ ] Phase 9: GASO engine updated and iteration loop primed.

- [ ] Phase 10: `evolution_archive.yaml` written/updated successfully.

---

## Execution Report (To be returned to user)

Upon successful completion of all phases and validation gates, return a summary report:

```text

LEONARDO LAB — EVOLUTION REPORT

System Analyzed: <$1>

Generation: <generation number>

Variants Explored: <number>

Variants Rejected (Invariant Violation): <number>

Winner: <Variant #>

Fitness Score: <value>

Why it won: <reason>

Leverage Points Discovered:

High Leverage: <variable> (ratio: <value>)

Low Leverage: <variable> (ratio: <value>)

New Baseline State:

<brief description>

Archive Location: ./.leonardo-lab/evolution_archive.yaml

Search Budget Remaining:

Iterations: <remaining>

Total Budget: <remaining>

Next Action:

Feed the new baseline back into /leonardo-lab for another iteration.

```

---

## End of Command Definition

```

---

This is the frozen, complete, and final slash command. It operationalizes the extracted Leonardo YAML as a domain-agnostic evolutionary kernel with persistent memory, budget constraints, and full lineage tracking.

Save it to `.claude/commands/leonardo-lab.md`. The engine is ready to evolve.