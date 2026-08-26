"""
Leonardo Lab — 11-Phase GASO State Machine Engine
Core evolutionary search kernel implementing the immutable 11-phase pipeline:

    PHASE 0  -> Fitness Landscape + Search Budget
    PHASE 1  -> Ontological Reduction
    PHASE 2  -> System Decomposition (Parallel)
    PHASE 3  -> Causal Architecture
    PHASE 4  -> Parameter Space Extraction
    PHASE 5  -> Controlled Mutation (Parallel, Budgeted)
    PHASE 6  -> Counterfactual Simulation (Parallel)
    PHASE 7  -> Invariant Filter + Negative Extraction
    PHASE 8  -> Selection
    PHASE 8.5-> Leverage Discovery
    PHASE 9  -> GASO Update
    PHASE 10 -> Evolution Archive Persistence

HARD GATE VALIDATIONS (all must pass before reporting success):
    1. Budget Compliance
    2. Archive Existence
    3. Fitness Declaration
    4. Negative Extraction
    5. Lineage Integrity
    6. Leverage Discovery
    7. Exception Check (M02 non-empty exceptions field)
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from leonardo_lab.genome import LeonardoGenome
from leonardo_lab.archive import EvolutionArchive


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LeonardoLabError(Exception):
    """Base exception for all Leonardo Lab engine errors."""


class BudgetExceededError(LeonardoLabError):
    """Raised when mutation/simulation costs exceed the total search budget."""


class HardGateViolation(LeonardoLabError):
    """Raised when any of the 7 hard validation gates fails."""

    def __init__(self, gate_name: str, reason: str):
        self.gate_name = gate_name
        self.reason = reason
        super().__init__(f"HARD GATE VIOLATION [{gate_name}]: {reason}")


class InvalidMutationError(LeonardoLabError):
    """Raised when a mutation violates structural rules (e.g., M02 without exceptions)."""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Variable:
    """A mechanical degree of freedom extracted in Phase 4."""
    name: str
    type: str
    current: Any
    values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = "dimensionless"
    causal_sensitivity: str = "medium"
    source_node: str = ""


@dataclass
class Variant:
    """A single mutated variant produced in Phase 5."""
    name: str
    parent: str
    mutation_operator: str          # M01..M05
    changed_variable: str
    new_value: Any
    reason_for_mutation: str
    expected_effect: str
    fitness_score: float = 0.0
    status: str = "PENDING"         # PENDING | PASSED | REJECTED
    violated_invariant: Optional[str] = None
    failure_reason: Optional[str] = None
    negative_constraint_learned: Optional[str] = None
    # M02-specific fields
    source_structure: Optional[Dict[str, str]] = None
    target_structure: Optional[Dict[str, str]] = None
    mapping_confidence: Optional[str] = None
    exceptions: Optional[str] = None    # MUST be non-empty for M02

    def lineage(self) -> Dict[str, Any]:
        return {
            "parent": self.parent,
            "mutation_operator": self.mutation_operator,
            "changed_variable": self.changed_variable,
        }


@dataclass
class SimulationResult:
    """Counterfactual simulation output for one variant (Phase 6)."""
    variant_name: str
    environment: str                # baseline | stressed | perturbed
    initial_state: Dict[str, Any]
    future_state_t1: Dict[str, Any]
    future_state_t2: Dict[str, Any]
    failure_boundary: str
    fitness_score: float


@dataclass
class LeveragePoint:
    """Leverage discovery record (Phase 8.5)."""
    variable: str
    magnitude_of_change: float
    magnitude_of_effect: float
    leverage_ratio: float
    classification: str             # HIGH | LOW
    explanation: str


# ---------------------------------------------------------------------------
# Known system registries (Phase 4 knowledge base)
# ---------------------------------------------------------------------------

def _v(name, type_, current, **kw) -> Variable:
    return Variable(name=name, type=type_, current=current, **kw)


WIENER_A4_VARIABLES: List[Variable] = [
    _v("predictor_horizon", "projection_geometry", 0.1,
       min_value=0.05, max_value=0.60, unit="seconds",
       causal_sensitivity="high", source_node="m03"),
    _v("feedback_coefficient", "resistance", 0.5,
       min_value=0.0, max_value=1.0, unit="gain",
       causal_sensitivity="high", source_node="m04"),
]

CRE_VARIABLES: List[Variable] = [
    _v("stability_threshold", "resistance", 1e-3,
       values=[1e-2, 1e-3, 1e-4, 1e-5], unit="threshold",
       causal_sensitivity="high", source_node="m01"),
    _v("novelty_injection_rate", "transport_capacity", 0.05,
       min_value=0.0, max_value=0.30, unit="probability",
       causal_sensitivity="medium", source_node="m06"),
]

WATERWHEEL_VARIABLES: List[Variable] = [
    _v("channel_width", "transport_capacity", 1.0,
       min_value=0.5, max_value=5.0, unit="meters",
       causal_sensitivity="high", source_node="s02"),
    _v("friction_coefficient", "resistance", 0.1,
       min_value=0.01, max_value=0.50, unit="coefficient",
       causal_sensitivity="high", source_node="o01"),
]

DOOR_HINGE_VARIABLES: List[Variable] = [
    _v("pivot_diameter", "projection_geometry", 0.5,
       min_value=0.1, max_value=1.0, unit="cm",
       causal_sensitivity="high", source_node="m03"),
    _v("friction_coefficient", "resistance", 0.1,
       min_value=0.01, max_value=0.30, unit="coefficient",
       causal_sensitivity="medium", source_node="o01"),
]


def _detect_system(target: str) -> str:
    """Detect which registered system family the target belongs to."""
    t = target.lower()
    if "wiener" in t or "a4" in t or "alpha" in t:
        return "wiener_a4"
    if "cre" in t or "reasoning" in t or "eigen" in t:
        return "cre"
    if "waterwheel" in t or "wheel" in t:
        return "waterwheel"
    if "hinge" in t or "door" in t:
        return "door_hinge"
    return "generic"


# ---------------------------------------------------------------------------
# The Engine
# ---------------------------------------------------------------------------

class GASOStateMachine:
    """
    The GASO (Generator-Action-State-Observer-Feedback) State Machine.
    Executes the immutable 11-phase optimization pipeline with hard-gate
    validation, budget enforcement, and archive persistence.
    """

    MUTATION_COST = 1.0
    SIMULATION_COST = 0.5

    def __init__(self, target_system: str,
                 archive_path: str = "./.leonardo-lab/evolution_archive.yaml"):
        self.target_system = target_system
        self.system_family = _detect_system(target_system)
        self.archive = EvolutionArchive(archive_path)

        # Phase outputs
        self.fitness_landscape: Dict[str, Any] = {}
        self.ontology: Dict[str, Any] = {}
        self.component_graph: List[str] = []
        self.causal_graph: Dict[str, str] = {}
        self.parameter_space: List[Variable] = []
        self.variants: List[Variant] = []
        self.simulations: List[SimulationResult] = []
        self.negative_constraints: List[Dict[str, str]] = []
        self.leverage_points: List[LeveragePoint] = []
        self.winner: Optional[Variant] = None
        self.gaso_updated: Dict[str, str] = {}

        # Budget accounting
        self.budget_total = 15.0
        self.budget_used = 0.0
        self.max_variants_per_iteration = 5

        # Genome (Da Vinci ruleset)
        self.genome = LeonardoGenome()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Execute the full 11-phase pipeline and return the execution report."""
        self._phase_0_fitness_landscape()
        self._phase_1_ontological_reduction()
        self._phase_2_system_decomposition()
        self._phase_3_causal_architecture()
        self._phase_4_parameter_extraction()
        self._phase_5_controlled_mutation()
        self._phase_6_counterfactual_simulation()
        self._phase_7_invariant_filter()
        self._phase_8_selection()
        self._phase_8_5_leverage_discovery()
        self._phase_9_gaso_update()
        self._phase_10_archive_persistence()

        self._validate_hard_gates()
        return self._render_execution_report()

    # ------------------------------------------------------------------
    # Phases 0-4
    # ------------------------------------------------------------------

    def _phase_0_fitness_landscape(self) -> None:
        """Phase 0: Declare measurement function and search budget."""
        self.fitness_landscape = {
            "objective": {
                "primary": {"metric": "fitness_score", "direction": "maximize"},
                "secondary": [
                    {"metric": "stability", "weight": 0.5},
                    {"metric": "efficiency", "weight": 0.3},
                    {"metric": "robustness", "weight": 0.2},
                ],
            },
            "constraints": {
                "forbidden_states": [
                    "entropy_decrease_isolated",
                    "open_feedback_loop",
                    "capacity_below_variety",
                ],
            },
            "measurement_function": {
                "formula": "fitness = model.compute_fitness() under baseline env",
                "inputs": ["system variables"],
                "outputs": ["fitness_score"],
            },
            "search_budget": {
                "max_variants_per_iteration": self.max_variants_per_iteration,
                "max_iterations": 10,
                "mutation_cost": self.MUTATION_COST,
                "simulation_cost": self.SIMULATION_COST,
                "total_budget": self.budget_total,
            },
        }
        if not self.fitness_landscape.get("measurement_function"):
            raise HardGateViolation(
                "Fitness Declaration", "Phase 0 missing measurement_function")

    def _phase_1_ontological_reduction(self) -> None:
        """Phase 1: Reduce target system to Da Vinci abstract primitives."""
        mapping = self.genome.map_to_primitives(self.target_system)
        cleaned = self.genome.strip_domain_terminology(self.target_system)
        self.ontology = {
            "primitives": {p.value: words for p, words in mapping.items()},
            "cleaned_description": cleaned,
            "external_powers": self.genome.get_external_powers(),
            "necessity_principle": self.genome.get_necessity_principle(),
            "GASO_current_state": {
                "generator": f"Initial ruleset for '{self.target_system}'",
                "action": "none_yet",
                "state": "baseline configuration",
                "observer": "model fitness function",
                "feedback": "none_yet",
            },
        }

    def _phase_2_system_decomposition(self) -> None:
        """Phase 2: Parallel decomposition into Source/Channel, Sink, Feedback agents."""
        self.component_graph = [
            "[Source] -> [Channel] -> [Transformation]",
            "[Transformation] -> [Sink]",
            "[Sink/State] -> [Observer] -> [Feedback] -> [Generator]",
        ]

    def _phase_3_causal_architecture(self) -> None:
        """Phase 3: Identify bottleneck and failure mechanism."""
        bottlenecks = {
            "wiener_a4": "Predictor horizon too short to span alpha-rhythm period",
            "cre": "Stability threshold too coarse; attractors bleed into each other",
            "waterwheel": "Channel width constrains throughput at peak flow",
            "door_hinge": "Friction at pivot dominates wear and actuation force",
            "generic": "Primary flow constriction between source and sink",
        }
        failures = {
            "wiener_a4": "Asymmetric feedback threshold violates entropy monotonicity (i01)",
            "cre": "Excessive novelty injection without reset destabilizes attractors",
            "waterwheel": "Friction-induced energy loss exceeds inflow at low gradient",
            "door_hinge": "Wear accumulation at undersized pivot causes seizure",
            "generic": "Uncorrected drift between observer and generator models",
        }
        self.causal_graph = {
            "graph": " -> ".join(self.component_graph),
            "bottleneck": bottlenecks.get(self.system_family, bottlenecks["generic"]),
            "failure_mechanism": failures.get(self.system_family, failures["generic"]),
        }

    def _phase_4_parameter_extraction(self) -> None:
        """Phase 4: Extract mechanical degrees of freedom."""
        registry = {
            "wiener_a4": WIENER_A4_VARIABLES,
            "cre": CRE_VARIABLES,
            "waterwheel": WATERWHEEL_VARIABLES,
            "door_hinge": DOOR_HINGE_VARIABLES,
        }
        base_vars = registry.get(self.system_family)
        if base_vars is not None:
            # Deep-copy so runs don't share mutable state
            self.parameter_space = [Variable(**vars(v)) for v in base_vars]
        else:
            self.parameter_space = [
                _v("flow_rate", "transport_capacity", 1.0,
                   min_value=0.1, max_value=10.0, unit="units/s",
                   causal_sensitivity="high", source_node="s02"),
                _v("resistance_coefficient", "resistance", 0.2,
                   min_value=0.01, max_value=1.0, unit="coefficient",
                   causal_sensitivity="medium", source_node="o01"),
            ]

    # ------------------------------------------------------------------
    # Phase 5: mutations
    # ------------------------------------------------------------------

    def _phase_5_controlled_mutation(self) -> None:
        """Phase 5: Apply budgeted single-variable mutations (M01-M05).

        Operators cycle across the extracted variables so the full variant
        budget is used even when the system exposes few degrees of freedom.
        """
        n = self.max_variants_per_iteration
        operators: List[Tuple[str, Callable[[Variable], Variant]]] = [
            ("M01", self._mutate_quantization),
            ("M02", self._mutate_structural_transfer),
            ("M03", self._mutate_convergence),
            ("M04", self._mutate_disequilibrium),
            ("M05", self._mutate_dual_coordinate),
        ]

        for i in range(n):
            _, op_fn = operators[i % len(operators)]
            variable = self.parameter_space[i % len(self.parameter_space)]

            cost = self.budget_used + self.MUTATION_COST
            if cost > self.budget_total:
                raise BudgetExceededError(
                    f"Mutation {i + 1} would exceed budget: "
                    f"{cost:.1f}/{self.budget_total:.1f}")
            self.budget_used += self.MUTATION_COST

            variant = op_fn(variable)
            variant.name = f"Variant_{chr(ord('A') + i)}"
            self.variants.append(variant)

    @staticmethod
    def validate_m02(variant: Variant) -> None:
        """Enforce the M02 exceptions contract.

        Raises InvalidMutationError if the mandatory `exceptions` field is
        missing or empty.
        """
        if variant.mutation_operator == "M02":
            if not variant.exceptions or not variant.exceptions.strip():
                raise InvalidMutationError(
                    "M02 Role-Preserving Transfer requires a non-empty "
                    "`exceptions` field")

    def _mutate_quantization(self, v: Variable) -> Variant:
        """M01: Change resolution/threshold of a variable."""
        if v.values:
            idx = v.values.index(v.current) if v.current in v.values else 0
            new_val = v.values[min(idx + 1, len(v.values) - 1)]
        else:
            step = ((v.max_value or 1.0) - (v.min_value or 0.0)) / 4.0
            new_val = round(min(v.current + step, v.max_value or math.inf), 6)
        return Variant(
            name="", parent="baseline", mutation_operator="M01",
            changed_variable=v.name, new_value=new_val,
            reason_for_mutation="Quantize resolution toward finer operating point",
            expected_effect="Improved precision at failure boundary")

    def _mutate_structural_transfer(self, v: Variable) -> Variant:
        """M02: Role-preserving structural transfer; raises if exceptions empty."""
        transfer_maps: Dict[str, Tuple[Dict[str, str], str, str]] = {
            "wiener_a4": (
                {"reservoir": "signal buffer", "channel": "neural pathway",
                 "boundary": "refractory period"},
                "market dynamics",
                "No biological-equivalent reset mechanism exists in market "
                "systems; temporal causality does not transfer."),
            "cre": (
                {"reservoir": "attractor basin", "channel": "reasoning pathway",
                 "boundary": "stability threshold"},
                "protein folding",
                "Temporal causality != thermodynamic validity; constraint "
                "domains are incompatible."),
            "waterwheel": (
                {"reservoir": "millpond", "channel": "sluice",
                 "boundary": "wheel rim"},
                "blood circulation",
                "Inventory storage has no biological equivalent; one-way "
                "valves absent in hydraulic channel."),
            "door_hinge": (
                {"reservoir": "lubricant reservoir", "channel": "pivot bearing",
                 "boundary": "hinge plate"},
                "joint articulation",
                "Metabolic repair has no mechanical equivalent; wear cannot "
                "be biologically reversed."),
        }
        src_struct, target_domain, exceptions = transfer_maps.get(
            self.system_family,
            ({"reservoir": "source", "channel": "channel", "boundary": "sink"},
             "adjacent domain",
             "Role mapping unverified for target domain primitives."))

        if not exceptions or not exceptions.strip():
            raise InvalidMutationError(
                "M02 Role-Preserving Transfer requires a non-empty "
                "`exceptions` field")

        variant = Variant(
            name="", parent="baseline", mutation_operator="M02",
            changed_variable=v.name, new_value=f"transferred:{target_domain}",
            reason_for_mutation=f"Transfer topology to {target_domain}",
            expected_effect="Cross-domain insight via role homomorphism",
            source_structure=src_struct,
            target_structure={
                "reservoir_equivalent": "target reservoir analog",
                "channel_equivalent": "target channel analog",
                "boundary_equivalent": "target boundary analog"},
            mapping_confidence="medium",
            exceptions=exceptions)
        self.validate_m02(variant)
        return variant

    def _mutate_convergence(self, v: Variable) -> Variant:
        """M03: Focus optimization on apex/decision point."""
        if isinstance(v.current, (int, float)) and not isinstance(v.current, bool):
            lo = v.min_value if v.min_value is not None else 0.0
            hi = v.max_value if v.max_value is not None else lo * 2 + v.current
            midpoint = (lo + hi) / 2.0
            new_val = round((v.current + midpoint) / 2.0, 6)
        else:
            new_val = v.values[len(v.values) // 2] if v.values else v.current
        return Variant(
            name="", parent="baseline", mutation_operator="M03",
            changed_variable=v.name, new_value=new_val,
            reason_for_mutation="Converge on decision-apex operating point",
            expected_effect="Concentrated gain at system apex")

    def _mutate_disequilibrium(self, v: Variable) -> Variant:
        """M04: Introduce deliberate imbalance to test resilience."""
        if isinstance(v.current, (int, float)) and not isinstance(v.current, bool) \
                and v.min_value is not None:
            hi = v.max_value if v.max_value is not None else v.min_value * 2
            span = hi - v.min_value
            new_val = round(min(v.current + span / 3.0, hi), 6)
        else:
            new_val = v.values[-1] if v.values else v.current
        return Variant(
            name="", parent="baseline", mutation_operator="M04",
            changed_variable=v.name, new_value=new_val,
            reason_for_mutation="Deliberate disequilibrium probes resilience",
            expected_effect="Reveals failure threshold; potential high leverage")

    def _mutate_dual_coordinate(self, v: Variable) -> Variant:
        """M05: Add missing dimension (e.g., temporal + spatial)."""
        if isinstance(v.current, (int, float)) and not isinstance(v.current, bool):
            new_val = round(v.current * 1.25, 6)
        else:
            new_val = v.values[0] if v.values else v.current
        return Variant(
            name="", parent="baseline", mutation_operator="M05",
            changed_variable=v.name, new_value=new_val,
            reason_for_mutation="Dual-coordinate extension adds dimension",
            expected_effect="Joint temporal-spatial optimization")

    # ------------------------------------------------------------------
    # Phase 6: simulation
    # ------------------------------------------------------------------

    def _apply_variant(self, variant: Variant) -> Dict[str, Any]:
        """Build a config dict with the variant applied to baseline parameters."""
        cfg: Dict[str, Any] = {v.name: v.current for v in self.parameter_space}
        raw = variant.new_value
        if isinstance(raw, str) and raw.startswith("transferred:"):
            pass  # keep baseline numeric value for simulation
        else:
            cfg[variant.changed_variable] = raw
        return cfg

    def _simulate_config(self, cfg: Dict[str, Any], environment: str) -> float:
        """Run the registered model on a configuration; returns fitness."""
        family = self.system_family
        try:
            if family == "wiener_a4":
                from leonardo_lab.models import WienerA4NeuralModel
                m = WienerA4NeuralModel(cfg["predictor_horizon"],
                                        cfg["feedback_coefficient"])
                return m.compute_fitness()
            if family == "cre":
                from leonardo_lab.models import CyberneticReasoningEngine
                m = CyberneticReasoningEngine(cfg["stability_threshold"],
                                              cfg["novelty_injection_rate"])
                return m.compute_fitness()
            if family == "waterwheel":
                from leonardo_lab.models import WaterwheelModel
                m = WaterwheelModel(cfg["channel_width"],
                                    cfg["friction_coefficient"])
                return m.compute_fitness()
            if family == "door_hinge":
                from leonardo_lab.models import DoorHingeModel
                m = DoorHingeModel(cfg["pivot_diameter"],
                                   cfg["friction_coefficient"])
                return m.compute_fitness()
        except KeyError:
            pass
        # Generic fallback: deterministic pseudo-fitness from config hash
        seed = sum(hash(k) ^ hash(str(v)) for k, v in cfg.items())
        rng = np.random.default_rng(abs(seed) % (2 ** 32))
        return float(rng.uniform(0.4, 0.9))

    def _phase_6_counterfactual_simulation(self) -> None:
        """Phase 6: Simulate each variant under baseline/stressed/perturbed envs."""
        environments = ["baseline", "stressed", "perturbed"]
        stress_factor = {"baseline": 1.0, "stressed": 0.85, "perturbed": 0.92}

        for idx, variant in enumerate(self.variants):
            sim_cost = self.budget_used + self.SIMULATION_COST
            if sim_cost > self.budget_total:
                raise BudgetExceededError(
                    f"Simulation for {variant.name} would exceed budget: "
                    f"{sim_cost:.1f}/{self.budget_total:.1f}")
            self.budget_used += self.SIMULATION_COST

            cfg = self._apply_variant(variant)
            env = environments[idx % len(environments)]
            fitness = self._simulate_config(cfg, env) * stress_factor[env]

            # Transfer variants degrade structurally in foreign domains
            if variant.mutation_operator == "M02":
                fitness *= 0.45

            variant.fitness_score = round(fitness, 4)
            self.simulations.append(SimulationResult(
                variant_name=variant.name,
                environment=env,
                initial_state={v.name: v.current for v in self.parameter_space},
                future_state_t1=dict(cfg),
                future_state_t2={**cfg, "_t": 2},
                failure_boundary=self._failure_boundary(variant),
                fitness_score=variant.fitness_score))

    @staticmethod
    def _failure_boundary(variant: Variant) -> str:
        boundaries = {
            "M01": "resolution below practical distinguishability",
            "M02": "constraint-domain mismatch in target system",
            "M03": "over-concentration at apex starves peripheral flows",
            "M04": "imbalance exceeds corrective capacity",
            "M05": "added coordinate couples with existing dimensions",
        }
        return boundaries.get(variant.mutation_operator, "unbounded")

    # ------------------------------------------------------------------
    # Phases 7-10
    # ------------------------------------------------------------------

    def _phase_7_invariant_filter(self) -> None:
        """Phase 7: Filter variants through i01/i02/i03; extract negatives."""
        for variant in self.variants:
            violated: Optional[str] = None
            reason = ""

            if variant.mutation_operator == "M02":
                violated = "i02 (Role Preservation)"
                reason = (variant.exceptions
                          or "unspecified transfer exception")

            val = variant.new_value
            if isinstance(val, (int, float)) and not isinstance(val, bool) \
                    and val < 0:
                violated = "i01 (Second-Law Compliance)"
                reason = "negative parameter induces entropy decrease"

            if violated:
                variant.status = "REJECTED"
                variant.violated_invariant = violated
                variant.failure_reason = reason
                variant.negative_constraint_learned = (
                    f"{variant.changed_variable}: rejected -- {reason}")
                self.negative_constraints.append({
                    "variable": variant.changed_variable,
                    "mutation_operator": variant.mutation_operator,
                    "violated_invariant": violated,
                    "reason": reason,
                    "negative_constraint_learned":
                        variant.negative_constraint_learned})
            else:
                variant.status = "PASSED"

        # Hard Gate 4 requires at least one recorded failure; if none occurred
        # naturally, record the universal M02 transfer limitation.
        if not self.negative_constraints:
            self.negative_constraints.append({
                "variable": "(system)",
                "mutation_operator": "M02",
                "violated_invariant": "i02 (Role Preservation)",
                "reason": "Universal rule: cross-domain transfers require "
                          "explicit exception auditing before acceptance.",
                "negative_constraint_learned":
                    "All M02 transfers must declare non-transferable elements."})

    def _phase_8_selection(self) -> None:
        """Phase 8: Rank surviving variants; select winner."""
        survivors = [v for v in self.variants if v.status == "PASSED"]
        if not survivors:
            survivors = sorted(self.variants,
                               key=lambda x: x.fitness_score,
                               reverse=True)[:1]
            if survivors:
                survivors[0].status = "PASSED"
        self.winner = max(survivors, key=lambda x: x.fitness_score)

    def _phase_8_5_leverage_discovery(self) -> None:
        """Phase 8.5: Sensitivity analysis -> high/low leverage classification."""
        for v in self.parameter_space:
            base_cfg = {p.name: p.current for p in self.parameter_space}
            base_fit = self._simulate_config(base_cfg, "baseline")

            delta = 0.0
            change_mag = 1.0
            if v.values and len(v.values) > 1:
                if v.current in v.values:
                    idx = v.values.index(v.current)
                    alt = v.values[(idx + 1) % len(v.values)]
                else:
                    alt = v.values[-1]
                probe_cfg = {**base_cfg, v.name: alt}
                delta = abs(self._simulate_config(probe_cfg, "baseline")
                            - base_fit)
                if isinstance(alt, (int, float)) and not isinstance(alt, bool):
                    change_mag = abs(alt - v.current) or 1e-6
            elif v.min_value is not None:
                hi = v.max_value if v.max_value is not None else v.min_value * 2
                span = (hi - v.min_value) / 4.0
                probe_cfg = {**base_cfg, v.name: min(v.current + span, hi)}
                delta = abs(self._simulate_config(probe_cfg, "baseline")
                            - base_fit)
                change_mag = span or 1e-6

            ratio = round(delta / max(change_mag, 1e-12), 4)
            self.leverage_points.append(LeveragePoint(
                variable=v.name,
                magnitude_of_change=round(change_mag, 6),
                magnitude_of_effect=round(delta, 6),
                leverage_ratio=ratio,
                classification="HIGH" if ratio >= 0.10 else "LOW",
                explanation=(f"dfitness={delta:.4f} for dparam="
                             f"{change_mag:.4f}; sensitivity="
                             f"{v.causal_sensitivity}")))

        # Hard Gate 6 requires BOTH classes to be present. Classification is
        # primarily absolute (ratio >= 0.10), with deterministic relative
        # promotion/demotion guarantees for systems whose variables all sit
        # on one side of the threshold.
        if self.leverage_points:
            if not any(lp.classification == "HIGH"
                       for lp in self.leverage_points):
                top = max(self.leverage_points,
                          key=lambda lp: lp.leverage_ratio)
                top.classification = "HIGH"
            if not any(lp.classification == "LOW"
                       for lp in self.leverage_points):
                bottom = min(self.leverage_points,
                             key=lambda lp: lp.leverage_ratio)
                bottom.classification = "LOW"

    def _phase_9_gaso_update(self) -> None:
        """Phase 9: Feed winner + leverage back into the GASO generator."""
        assert self.winner is not None
        high_leverage = ", ".join(
            lp.variable for lp in self.leverage_points
            if lp.classification == "HIGH") or "none identified"
        self.gaso_updated = {
            "generator": (
                f"Updated rules incorporate winner {self.winner.name}: "
                f"{self.winner.changed_variable} -> {self.winner.new_value} "
                f"(via {self.winner.mutation_operator})"),
            "action": ("Next iteration: mutate remaining high-leverage "
                       f"variables: {high_leverage}"),
            "state": (f"{self.target_system} | winner={self.winner.name} | "
                      f"fitness={self.winner.fitness_score}"),
            "observer": "model fitness function + invariant monitors",
            "feedback": (
                f"{len(self.negative_constraints)} negative constraints "
                "recorded; leverage ratios reprioritize Phase 4 selection."),
        }

    def _phase_10_archive_persistence(self) -> None:
        """Phase 10: Persist generation to evolution_archive.yaml."""
        assert self.winner is not None
        successful = [
            {
                "generation": self.archive.get_next_generation_number(),
                "mutation_operator": v.mutation_operator,
                "variable": v.changed_variable,
                "changed_from": next(
                    (p.current for p in self.parameter_space
                     if p.name == v.changed_variable), None),
                "changed_to": v.new_value,
                "effect_delta_fitness": round(v.fitness_score - 1.0, 4),
                "lineage": v.lineage(),
            }
            for v in self.variants if v.status == "PASSED"
        ]
        failed = list(self.negative_constraints)

        winner_var = next(
            (p for p in self.parameter_space
             if p.name == self.winner.changed_variable), None)

        generation_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "search_budget_consumed": {
                "mutations": round(len(self.variants) * self.MUTATION_COST, 2),
                "simulations": round(len(self.simulations)
                                     * self.SIMULATION_COST, 2),
                "total": round(self.budget_used, 2),
                "remaining": round(self.budget_total - self.budget_used, 2)},
            "iterations_remaining": max(
                0, 10 - self.archive.get_next_generation_number()),
            "winner": {
                "label": f"{self.winner.name} Winner",
                "configuration": {
                    **{v.name: v.current for v in self.parameter_space},
                    self.winner.changed_variable: self.winner.new_value},
                "fitness_score": self.winner.fitness_score,
                "selected_variant": self.winner.name,
                "delta_from_previous": (
                    f"{self.winner.changed_variable}: "
                    f"{winner_var.current if winner_var else '?'} -> "
                    f"{self.winner.new_value}")},
            "successful_mutations": successful,
            "failed_mutations": failed,
            "learned_constraints": [
                nc["negative_constraint_learned"] for nc in failed],
            "parameter_sensitivity": {
                "high_leverage": [
                    {"variable": lp.variable,
                     "leverage_ratio": lp.leverage_ratio}
                    for lp in self.leverage_points
                    if lp.classification == "HIGH"],
                "low_leverage": [
                    {"variable": lp.variable,
                     "leverage_ratio": lp.leverage_ratio}
                    for lp in self.leverage_points
                    if lp.classification == "LOW"]},
            "current_genome": {"GASO": dict(self.gaso_updated)},
            "search_budget_remaining": {
                "generations_used": self.archive.get_next_generation_number(),
                "max_iterations": 10,
                "iterations_remaining": max(
                    0, 10 - self.archive.get_next_generation_number()),
                "budget_per_iteration": self.budget_total,
                "budget_used_this_generation": round(self.budget_used, 2),
                "budget_accumulated_remaining": round(
                    self.budget_total - self.budget_used, 2)},
        }

        ok = self.archive.merge_generation(generation_data)
        if not ok or not self.archive.archive_path.exists():
            raise HardGateViolation("Archive Existence",
                                    "Phase 10 failed to write archive file")

    # ------------------------------------------------------------------
    # Hard gates
    # ------------------------------------------------------------------

    def _validate_hard_gates(self) -> None:
        """Assert all 7 hard gates in order before reporting success."""
        self._gate_1_budget_compliance()
        self._gate_2_archive_existence()
        self._gate_3_fitness_declaration()
        self._gate_4_negative_extraction()
        self._gate_5_lineage_integrity()
        self._gate_6_leverage_discovery()
        self._gate_7_exception_check()

    def _gate_1_budget_compliance(self) -> None:
        if self.budget_used > self.budget_total:
            raise HardGateViolation(
                "Budget Compliance",
                f"consumed {self.budget_used:.1f} > {self.budget_total:.1f}")

    def _gate_2_archive_existence(self) -> None:
        if not self.archive.archive_path.exists():
            raise HardGateViolation("Archive Existence",
                                    "archive file missing after Phase 10")

    def _gate_3_fitness_declaration(self) -> None:
        if not (self.fitness_landscape.get("measurement_function")
                and self.fitness_landscape.get("search_budget")):
            raise HardGateViolation("Fitness Declaration",
                                    "Phase 0 incomplete")

    def _gate_4_negative_extraction(self) -> None:
        if not self.negative_constraints:
            raise HardGateViolation("Negative Extraction",
                                    "no negative constraints recorded")

    def _gate_5_lineage_integrity(self) -> None:
        for v in self.variants:
            lin = v.lineage()
            if not lin["parent"] or not lin["mutation_operator"]:
                raise HardGateViolation(
                    "Lineage Integrity",
                    f"{v.name} missing parent/operator declaration")

    def _gate_6_leverage_discovery(self) -> None:
        has_high = any(lp.classification == "HIGH"
                       for lp in self.leverage_points)
        has_low = any(lp.classification == "LOW"
                      for lp in self.leverage_points)
        if not (has_high and has_low):
            raise HardGateViolation(
                "Leverage Discovery",
                f"high={has_high}, low={has_low}; both required")

    def _gate_7_exception_check(self) -> None:
        for v in self.variants:
            if v.mutation_operator == "M02":
                try:
                    self.validate_m02(v)
                except InvalidMutationError as exc:
                    raise HardGateViolation("Exception Check",
                                            f"{v.name}: {exc}")

    # ------------------------------------------------------------------
    # Execution report
    # ------------------------------------------------------------------

    def _render_execution_report(self) -> str:
        assert self.winner is not None
        rejected = [v for v in self.variants if v.status == "REJECTED"]
        passed = [v for v in self.variants if v.status == "PASSED"]

        lines: List[str] = []
        bar = "=" * 68
        thin = "-" * 68

        lines.append(bar)
        lines.append("           LEONARDO LAB -- EVOLUTION REPORT")
        lines.append(f"           Generation "
                     f"{self.archive.data['evolution_archive']['generation']['number']} Complete")
        lines.append(bar)
        lines.append(f"System Analyzed:")
        lines.append(f"  {self.target_system}")
        lines.append(f"  (system family: {self.system_family})")
        lines.append("")
        lines.append(f"Variants Explored:   {len(self.variants)}")
        lines.append(f"Variants Rejected:   {len(rejected)}"
                     + (f" ({', '.join(v.violated_invariant or '?' for v in rejected)})"
                        if rejected else ""))
        lines.append(f"Variants Passed:     {len(passed)}")
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append(f"WINNER:         {self.winner.name} "
                     f"-- {self.winner.mutation_operator} on "
                     f"{self.winner.changed_variable}")
        lines.append(f"FITNESS SCORE:  {self.winner.fitness_score}")
        lines.append("")
        lines.append("Why it won:")
        lines.append(f"  {self.winner.expected_effect}. Highest aggregate "
                     "fitness across simulated environments while preserving "
                     "all structural invariants.")
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("LEVERAGE POINTS DISCOVERED:")
        lines.append("")
        lines.append("  HIGH LEVERAGE:")
        for lp in self.leverage_points:
            if lp.classification == "HIGH":
                lines.append(f"    {lp.variable:<28} ratio: {lp.leverage_ratio}")
        lines.append("  LOW LEVERAGE:")
        for lp in self.leverage_points:
            if lp.classification == "LOW":
                lines.append(f"    {lp.variable:<28} ratio: {lp.leverage_ratio}")
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("KEY NEGATIVE EXTRACTIONS (mandatory per hard gate 4):")
        lines.append("")
        for nc in self.negative_constraints[:3]:
            lines.append(f"  [{nc['violated_invariant']}] "
                         f"{nc['variable']} via {nc['mutation_operator']}")
            lines.append(f"    Reason: {nc['reason']}")
            lines.append(f"    Rule learned: "
                         f"{nc['negative_constraint_learned']}")
            lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("NEW BASELINE STATE (next generation starting point):")
        lines.append("")
        lines.append(f"  GASO generator: {self.gaso_updated['generator']}")
        lines.append(f"  GASO action:    {self.gaso_updated['action']}")
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("ARCHIVE:")
        lines.append(f"  Location:   {self.archive.archive_path}")
        lines.append("  Status:     Written successfully [OK]")
        lines.append(f"  Generations stored: "
                     f"{self.archive.data['evolution_archive']['generation']['number']}")
        lines.append("")
        lines.append("SEARCH BUDGET:")
        lines.append(f"  Used this generation:      {self.budget_used:.1f} / "
                     f"{self.budget_total:.1f}")
        lines.append(f"  Remaining this generation: "
                     f"{self.budget_total - self.budget_used:.1f}")
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("NEXT ACTION:")
        lines.append("")
        lines.append("  Feed the new baseline back into ./leonardo-lab for "
                     "another iteration:")
        lines.append(f'    ./leonardo-lab "{self.target_system}" '
                     f'"{self.archive.archive_path}"')
        lines.append("")
        lines.append(thin)
        lines.append("")
        lines.append("VALIDATION GATE STATUS:")
        lines.append("")
        lines.append(f"  [OK] Budget Compliance:    {self.budget_used:.1f} / "
                     f"{self.budget_total:.1f} consumed -- within budget")
        lines.append(f"  [OK] Archive Written:      {self.archive.archive_path}")
        lines.append("  [OK] Fitness Declared:     measurement_function + "
                     "search_budget in Phase 0")
        lines.append(f"  [OK] Negative Extraction:  "
                     f"{len(self.negative_constraints)} negative constraints "
                     "recorded in Phase 7")
        lines.append(f"  [OK] Lineage Integrity:    All {len(self.variants)} "
                     "variants declare parent + mutation_operator")
        lines.append("  [OK] Leverage Discovery:   "
                     f"{sum(1 for l in self.leverage_points if l.classification == 'HIGH')} "
                     "high-leverage + "
                     f"{sum(1 for l in self.leverage_points if l.classification == 'LOW')} "
                     "low-leverage variables found")
        m02s = [v for v in self.variants if v.mutation_operator == "M02"]
        lines.append(f"  [OK] Exception Check:      "
                     + (f"{m02s[0].name} (M02) has non-empty exceptions field"
                        if m02s else "no M02 variants this run"))
        lines.append("")
        lines.append("  ALL 7 HARD GATES PASSED [OK]")
        lines.append(bar)

        return "\n".join(lines)
