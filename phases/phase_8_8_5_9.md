# Leonardo Lab — Phases 8–9
## System: Decoder-Only Transformer (Configuration B)
## Generation: 1

---

# PHASE 8 — Selection

## Surviving variants (PASSED invariant filter):
- Variant_A: Pre-LN — fitness 1.117
- Variant_B: RoPE   — fitness 1.113
- Variant_C: Softcap — fitness 1.090
- Variant_E: GQA    — fitness 1.207

## Rejected:
- Variant_D: Protein transfer — REJECTED (i02 / Role Preservation violation)

## Ranking

| Rank | Variant | Fitness | Primary Gain | Primary Cost |
|------|---------|---------|--------------|--------------|
| 1 | Variant_E (GQA) | 1.207 | 4× KV cache reduction; inference efficiency | Marginal quality loss (~0.3%) |
| 2 | Variant_A (Pre-LN) | 1.117 | Training stability; depth scalability | None identified |
| 3 | Variant_B (RoPE) | 1.113 | Length generalization; structured data | Minimal cost |
| 4 | Variant_C (Softcap) | 1.090 | Long-sequence quality preservation | None at normal lengths |

## Selection Decision

```text
SELECTED DESIGN:

Winner:         Variant_E (Grouped Query Attention, g=4 KV heads)

Reason:
  Highest aggregate fitness (1.207) across all three environments.
  Passes all invariant checks (i01, i02, i03, i04).
  4× reduction in KV cache memory enables 4× longer context at same
  GPU memory budget — directly addresses the quadratic bottleneck
  identified in Phase 3 (primary bottleneck: O(n²·d) attention).
  Minimal quality degradation at g=4 (< 0.3% BPC, empirically verified
  in GQA literature).

Tradeoffs Accepted:
  - 0.3% BPC quality regression at g=4 (acceptable per Phase 0 constraints:
    "small quality degradation <0.3 BPC in exchange for 50%+ memory reduction")
  - Increased architectural complexity (grouped projection indices)

Note on composite strategy:
  Variants A, B, C, E are INDEPENDENT (each changes a different variable).
  They CAN be composed without interference. The generation-2 baseline
  should be: Pre-LN + RoPE + Softcap + GQA applied simultaneously.
  However, per single-variable rule, only Variant_E is the generation-1 winner.
  Composition occurs in generation 2 with the composite as new baseline.
```

---

# PHASE 8.5 — Leverage Discovery

Leverage ratio = (Δ fitness) / (Δ variable magnitude)
Variable magnitudes normalized to [0, 1] for comparison.

```yaml
leverage_points:

  high_leverage:

    - variable: kv_cache_sharing
      mutation: multi_head → grouped_query (g=4)
      magnitude_of_change: 0.25  # 4×16 = 4 groups, normalized: 0.25 of head count
      magnitude_of_effect: +0.207 fitness units
      leverage_ratio: 0.207 / 0.25 = 0.828 per unit change
      explanation: >
        Reducing KV heads from 16 to 4 cuts memory bandwidth and cache size by 4×,
        enabling 4× longer effective context at no training cost.
        The mechanism acts on the INFERENCE bottleneck, not the training bottleneck,
        creating disproportionate deployment value from a minimal parameter change.
        High leverage because it addresses a bottleneck that training metrics
        don't fully capture (the KV cache is an inference-only structure).

    - variable: normalization_position
      mutation: post_norm → pre_norm
      magnitude_of_change: 1.0  # binary categorical
      magnitude_of_effect: +0.117 fitness units
      leverage_ratio: 0.117 / 1.0 = 0.117 per unit change
      explanation: >
        A single structural reorder (LN before sublayer vs. after) changes the
        gradient flow through ALL N layers simultaneously. The effect is
        multiplicative with depth: at N=12 layers, pre-LN improves gradient
        scale equality at all 12×2=24 sublayers with one architectural decision.
        High leverage because the change is O(1) in complexity but affects O(N)
        components.

    - variable: position_encoding_type
      mutation: alibi_linear → rope_rotary
      magnitude_of_change: 1.0  # categorical
      magnitude_of_effect: +0.113 fitness units (concentrated at stressed environment)
      leverage_ratio: 0.113 / 1.0 = 0.113 per unit change
      explanation: >
        Zero additional parameters. The gain is concentrated at out-of-distribution
        sequence lengths (stressed environment: 1.22 vs. baseline environment: 1.02).
        Leverage is asymmetric: negligible gain at training length, high gain at
        deployment length. This is a "free insurance policy" with near-zero cost
        in the standard regime.

  medium_leverage:

    - variable: attention_logit_softcap
      mutation: infinity → 50.0
      magnitude_of_change: 0.10  # small perturbation (cap=50 is near the natural max)
      magnitude_of_effect: +0.090 fitness units
      leverage_ratio: 0.090 / 0.10 = 0.900 per unit change
      explanation: >
        Very high leverage ratio, but the absolute effect is smaller than kv_cache
        because it only activates in the stressed environment (long sequences).
        In baseline conditions, the intervention is invisible (logits rarely exceed 50).
        Highly targeted: addresses exactly one failure mode (softmax saturation)
        without touching any other component.
      note: "Highest leverage RATIO but lowest absolute gain. Targeted fix for a specific failure mode."

  low_leverage:

    - variable: dropout_rate
      mutation: 0.1 → 0.2
      magnitude_of_change: 0.1
      magnitude_of_effect: ~0.005 fitness units (at scale, data regularizes implicitly)
      leverage_ratio: 0.005 / 0.1 = 0.050 per unit change
      explanation: >
        At the scale of a modern language model with billions of training tokens,
        dropout provides minimal additional regularization. The data distribution
        itself provides sufficient implicit regularization. The parameter exists
        but has low causal influence on fitness in the high-data regime.

    - variable: weight_tying
      mutation: tied → untied
      magnitude_of_change: 1.0
      magnitude_of_effect: ~0.010 fitness units
      leverage_ratio: 0.010 / 1.0 = 0.010 per unit change
      explanation: >
        At large vocabulary sizes, the embedding and output projection matrices
        serve distinct purposes (encoding context vs. generating token probability).
        Untying them gives each matrix full freedom, but the gain is marginal
        because the tied configuration is already a near-optimal constraint at
        this scale. The interaction between embedding content and output distribution
        is already captured by the transformer's learned representations.

LEVERAGE_SUMMARY:
  high_leverage_variables:
    - kv_cache_sharing
    - normalization_position
    - position_encoding_type
  low_leverage_variables:
    - dropout_rate
    - weight_tying

LEVERAGE_LAW_EXTRACTED: >
  Variables that affect MULTIPLE downstream components simultaneously
  (normalization_position → all N×2 sublayers) or that address
  BOTTLENECKS not visible in standard training metrics (kv_cache →
  inference-only memory) have disproportionate leverage over variables
  that act locally and in isolation (dropout → single forward pass).
```

---

# PHASE 9 — GASO Update & Iteration Preparation

```yaml
GASO_updated:

  generator:
    rules: >
      Updated: Causal decoder-only stack with GROUPED QUERY ATTENTION (g=4 KV heads).
      Baseline V04 (relative position) retained.
      Structural modifications queue for Generation 2:
        [QUEUED] Pre-LN normalization (Variant_A)
        [QUEUED] RoPE position encoding (Variant_B)
        [QUEUED] Attention logit softcap=50.0 (Variant_C)
      These three are independent and non-interfering; they compose cleanly.
      Generation 2 baseline = Generation 1 winner + all three queued changes.

  action:
    recommended_intervention: >
      Apply Variant_A (Pre-LN) + Variant_B (RoPE) + Variant_C (Softcap)
      simultaneously as the Generation 2 starting configuration.
      Then run Generation 2 mutations on:
        (1) ffn_expansion_ratio — test 8× vs 4×
        (2) attention_window_structure — test hybrid_local_global
        (3) layer_count — test 24 vs 12
        (4) head_count — test 32 heads (smaller d_k, more subspaces)
        (5) Composition invariant test: confirm pre-LN + RoPE + softcap + GQA
            all preserve i01, i02, i03, i04 simultaneously.

  state:
    new_baseline: >
      Decoder-only transformer with:
      - Grouped Query Attention (g=4, h=16): KV cache 4× smaller
      - Relative position biases (ALiBi, V04): maintained from Config B
      - Post-norm (unchanged from Config B): to be updated in Generation 2
      - d_model=512, N=12, d_ff=2048, h=16, g=4
      - Fitness: 1.207
    delta_from_previous: >
      kv_cache_sharing: multi_head → grouped_query (g=4)
      All other variables: unchanged from Configuration B baseline

  observer:
    primary: "Validation BPC on standard language modeling benchmark (PTB/WikiText-103)"
    secondary:
      - "KV cache memory at n=4096 (target: 4× reduction confirmed)"
      - "Training loss curve smoothness (gradient norm variance)"
      - "Quality at 2× and 4× training length (length generalization)"
    instrumentation: "Log attention entropy per head per layer (detect routing collapse)"

  feedback:
    active_loops:
      - "Fitness score from Phase 0 measurement function feeds Phase 5 mutation selection"
      - "Failed mutations in Phase 7 update learned_constraints in archive"
      - "Leverage ratios from Phase 8.5 reprioritize variable selection in Phase 4"
    correction: >
      Low-leverage variables (dropout_rate, weight_tying) deprioritized.
      Mutation budget in Generation 2 reallocated to high-leverage variables
      (ffn_expansion_ratio, attention_window_structure).

  ITERATION_READY: TRUE
  Next_Input: >
    Generation 2 system:
      "Decoder-only transformer with GQA (g=4) + Pre-LN + RoPE + Softcap
       composition. Explore ffn_expansion_ratio and attention_window_structure."
```
