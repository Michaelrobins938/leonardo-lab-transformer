"""
Leonardo Lab — Test Suite
Unit, Integration, and End-to-End tests for the GASO State Machine Engine.

Run with:  pytest tests/ -v
"""

import os
import sys
from pathlib import Path

import pytest
import yaml

# Ensure package importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from leonardo_lab.engine import (
    GASOStateMachine,
    BudgetExceededError,
    HardGateViolation,
    InvalidMutationError,
    Variant,
)
from leonardo_lab.archive import EvolutionArchive
from leonardo_lab.genome import LeonardoGenome, DaVinciPrimitive


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_archive(tmp_path) -> str:
    """Fresh archive path per test, inside pytest tmp dir."""
    return str(tmp_path / ".leonardo-lab" / "evolution_archive.yaml")


@pytest.fixture
def waterwheel_engine(tmp_archive) -> GASOStateMachine:
    return GASOStateMachine("optimize a waterwheel", tmp_archive)


# ---------------------------------------------------------------------------
# Unit Tests (Structural Integrity)
# ---------------------------------------------------------------------------

class TestPhase0Budget:
    """Test 1: Phase 0 budget parsing and structural check."""

    def test_phase_0_declares_complete_budget(self, waterwheel_engine):
        waterwheel_engine._phase_0_fitness_landscape()
        budget = waterwheel_engine.fitness_landscape["search_budget"]

        assert "mutation_cost" in budget
        assert "simulation_cost" in budget
        assert "total_budget" in budget

        assert budget["mutation_cost"] == 1.0
        assert budget["simulation_cost"] == 0.5
        assert budget["total_budget"] == 15.0
        assert budget["max_variants_per_iteration"] == 5

    def test_phase_0_declares_measurement_function(self, waterwheel_engine):
        waterwheel_engine._phase_0_fitness_landscape()
        mf = waterwheel_engine.fitness_landscape["measurement_function"]

        assert "formula" in mf
        assert "inputs" in mf
        assert "outputs" in mf


class TestGenerationIncrement:
    """Test 2: Generation increment tracking in Phase 10."""

    def test_generation_increments_on_merge(self, tmp_archive):
        archive = EvolutionArchive(tmp_archive)
        first = archive.get_next_generation_number()
        assert first == 1  # fresh archive starts at 0

        ok = archive.merge_generation({
            "timestamp": "2026-01-01T00:00:00+00:00",
            "winner": {
                "label": "Test Winner",
                "configuration": {"x": 1},
                "fitness_score": 1.1,
                "selected_variant": "Variant_A",
            },
        })
        assert ok is True
        assert archive.data["evolution_archive"]["generation"]["number"] == 1
        assert archive.get_next_generation_number() == 2

    def test_second_merge_appends_history(self, tmp_archive):
        archive = EvolutionArchive(tmp_archive)
        for i in range(2):
            archive.merge_generation({
                "winner": {
                    "label": f"W{i}",
                    "configuration": {},
                    "fitness_score": 1.0 + i,
                    "selected_variant": f"Variant_{i}",
                },
            })
        history = archive.data["evolution_archive"]["baseline_history"]
        assert len(history) == 2
        assert [h["generation"] for h in history] == [1, 2]


class TestBudgetEnforcement:
    """Test 3: Engine halts with BudgetExceededError if search budget blown."""

    def test_budget_exceeded_raises(self, tmp_archive):
        engine = GASOStateMachine("optimize a waterwheel", tmp_archive)
        engine.budget_total = 2.5   # only fits 2 mutations + 1 simulation
        engine.max_variants_per_iteration = 5

        with pytest.raises(BudgetExceededError):
            engine.run()

    def test_default_run_stays_within_budget(self, waterwheel_engine):
        # Default config must complete without exceeding 15.0
        waterwheel_engine.run()
        assert waterwheel_engine.budget_used <= waterwheel_engine.budget_total


# ---------------------------------------------------------------------------
# Integration Tests (Causal Soundness)
# ---------------------------------------------------------------------------

class TestWaterwheelIntegration:
    """Test 4: 'Optimize a waterwheel' extracts physical variables and
    identifies channel_width as high-leverage."""

    def test_phase_4_extracts_physical_variables(self, waterwheel_engine):
        waterwheel_engine.run()
        names = {v.name for v in waterwheel_engine.parameter_space}

        assert "channel_width" in names
        assert "friction_coefficient" in names

        # Variables must be physical (typed ranges), not abstract
        cw = next(v for v in waterwheel_engine.parameter_space
                  if v.name == "channel_width")
        assert cw.unit == "meters"
        assert cw.min_value is not None and cw.max_value is not None

    def test_phase_8_5_flags_channel_width_high_leverage(self, waterwheel_engine):
        waterwheel_engine.run()
        leverage = {lp.variable: lp.classification
                    for lp in waterwheel_engine.leverage_points}

        # channel_width must be classified HIGH (widest fitness response)
        assert leverage.get("channel_width") == "HIGH"


class TestM02TransferExceptions:
    """Test 5: M02 transfer without explicit exceptions must fail loudly."""

    def test_validate_m02_rejects_empty_exceptions(self, waterwheel_engine):
        """validate_m02 raises InvalidMutationError on empty exceptions."""
        waterwheel_engine._phase_4_parameter_extraction()
        var = waterwheel_engine.parameter_space[0]
        bad = Variant(
            name="Variant_X", parent="baseline", mutation_operator="M02",
            changed_variable=var.name, new_value="transferred:test-domain",
            reason_for_mutation="test", expected_effect="test",
            exceptions="")
        with pytest.raises(InvalidMutationError):
            waterwheel_engine.validate_m02(bad)

    def test_gate7_catches_post_hoc_tampering(self, waterwheel_engine):
        """A valid M02 whose exceptions field is later emptied is caught by
        the hard-gate validation (defense in depth)."""
        waterwheel_engine._phase_4_parameter_extraction()
        var = waterwheel_engine.parameter_space[0]
        variant = waterwheel_engine._mutate_structural_transfer(var)
        assert variant.exceptions and variant.exceptions.strip()  # born valid

        variant.exceptions = ""   # tamper
        waterwheel_engine.variants.append(variant)
        with pytest.raises(HardGateViolation, match="Exception Check"):
            waterwheel_engine._gate_7_exception_check()

    def test_m02_generated_transfers_declare_exceptions(self, waterwheel_engine):
        """Every M02 variant produced by the engine carries non-empty exceptions."""
        waterwheel_engine.run()
        m02s = [v for v in waterwheel_engine.variants
                if v.mutation_operator == "M02"]
        assert len(m02s) >= 1
        for v in m02s:
            assert v.exceptions and v.exceptions.strip()
            # Waterwheel -> blood circulation transfer must flag inventory gap
            if "blood" in (v.new_value or ""):
                assert "inventory" in v.exceptions.lower() or \
                       "biological equivalent" in v.exceptions.lower()


# ---------------------------------------------------------------------------
# End-to-End Evolution Test
# ---------------------------------------------------------------------------

class TestEndToEndDoorHinge:
    """Test 6: Full 11-phase run on 'improve a door hinge'; verify concrete
    mechanical change and cross-generation lineage linkage."""

    def test_full_run_produces_concrete_mechanical_change(self, tmp_archive):
        engine = GASOStateMachine("improve a door hinge", tmp_archive)
        report = engine.run()

        # Final generator must specify a concrete mechanical change
        generator = engine.gaso_updated["generator"]
        assert any(
            token in generator
            for token in ("pivot_diameter", "friction_coefficient")
        ), f"Generator lacks concrete mechanical change: {generator}"

        # Report must contain the mandatory sections
        assert "EVOLUTION REPORT" in report
        assert "ALL 7 HARD GATES PASSED" in report
        assert "WINNER:" in report

    def test_second_generation_links_lineage(self, tmp_archive):
        # Generation 1
        e1 = GASOStateMachine("improve a door hinge", tmp_archive)
        e1.run()

        # Generation 2 resumes from same archive
        e2 = GASOStateMachine("improve a door hinge", tmp_archive)
        e2.run()

        with open(tmp_archive) as f:
            data = yaml.safe_load(f)["evolution_archive"]

        # Two generations recorded
        assert data["generation"]["number"] == 2
        assert len(data["baseline_history"]) == 2

        # Parent-child lineage: gen-2 winner declares a parent lineage entry
        gen2_mutations = [m for m in data["successful_mutations"]
                          if m.get("generation") == 2]
        assert gen2_mutations, "no generation-2 mutations recorded"
        for m in gen2_mutations:
            lin = m.get("lineage", {})
            assert lin.get("parent"), "gen-2 mutation missing parent"
            assert lin.get("mutation_operator"), \
                "gen-2 mutation missing operator"

    def test_hard_gates_all_pass(self, tmp_archive):
        engine = GASOStateMachine("Cybernetic Reasoning Engine", tmp_archive)
        engine.run()
        # _validate_hard_gates raises on failure; reaching here means all passed
        engine._validate_hard_gates()


# ---------------------------------------------------------------------------
# Genome unit checks (supporting)
# ---------------------------------------------------------------------------

class TestGenome:
    def test_domain_terms_stripped(self):
        g = LeonardoGenome()
        cleaned = g.strip_domain_terminology("the eye sees blood flow in water")
        assert "eye" not in cleaned
        assert "blood" not in cleaned
        assert "water" not in cleaned

    def test_primitive_mapping_returns_all_six(self):
        g = LeonardoGenome()
        mapping = g.map_to_primitives("input source flows through channel to sink")
        assert set(mapping.keys()) == set(DaVinciPrimitive)

    def test_constraints_present(self):
        g = LeonardoGenome()
        constraints = g.get_all_constraints()
        assert {"i01", "i02", "i03"} <= set(constraints.keys())
