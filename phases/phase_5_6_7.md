# Leonardo Lab — Phases 5–7
## System: Decoder-Only Transformer (Configuration B)
## Generation: 1

---

# PHASE 5 — Controlled Mutations (5 Variants, Budgeted)

Budget: 5 variants × 1.0 = 5.0 mutation cost consumed.
Single-variable rule: each variant changes EXACTLY ONE parameter from Phase 4.

---

## Variant A — Pre-Layer Normalization
```yaml
variant:
  name: Variant_A
  lineage:
    parent: Configuration_B_Baseline
    mutation_operator: M01  # Quantization — change resolution of structural position
    changed_variable: normalization_position
    changed_from: post_norm
    changed_to: pre_norm
    reason_for_mutation: >
      Phase 3 identified gradient scale divergence across layers as a failure
      mechanism at depth. Pre-LN equalizes gradient magnitudes by normalizing
      BEFORE the sublayer, not after. This is a categorical change to one
      structural variable with well-understood causal consequences.
    expected_effect: >
      Improved training stability for large N. Reduced gradient norm variance
      across layers. May allow training without LR warmup. Slight quality
      degradation possible at small N (pre-LN is slightly less expressive
      than post-LN when training is stable). Net: higher fitness at N>=12.
  implementation_delta: >
    Replace: LayerNorm(x + Sublayer(x))
    With:    x + Sublayer(LayerNorm(x))
    Scope:   All N layers, both attention and FFN sublayers.
```

---

## Variant B — Rotary Position Embedding (RoPE)
```yaml
variant:
  name: Variant_B
  lineage:
    parent: Configuration_B_Baseline
    mutation_operator: M05  # Dual-Coordinate — add a missing representation dimension
    changed_variable: position_encoding_type
    changed_from: alibi_linear
    changed_to: rope_rotary
    reason_for_mutation: >
      ALiBi (current V04 baseline) injects position as an additive bias to
      attention logits. RoPE instead encodes position by rotating query and key
      vectors in complex space. This adds a second representational coordinate
      (rotation angle) on top of content similarity, enabling more principled
      length extrapolation because relative positions are preserved under the
      inner product regardless of absolute position magnitude.
    expected_effect: >
      Better extrapolation beyond training length. Position-content interaction
      is richer (multiplicative via rotation, not additive via bias).
      Adds zero parameters. Compatible with flash attention implementations.
      May improve quality on tasks requiring precise relative positioning
      (code, structured data).
  implementation_delta: >
    Remove: ALiBi additive bias table b(i-j) from attention logits
    Add: Apply rotation matrix R(θ·pos) to Q and K vectors before dot product
         where θ is a fixed frequency vector (not learned)
    Formula: q_rot = R(m·θ)·q, k_rot = R(n·θ)·k
             score = (q_rot)^T(k_rot) / √d_k  [relative offset (m-n) is preserved]
```

---

## Variant C — Attention Logit Softcap
```yaml
variant:
  name: Variant_C
  lineage:
    parent: Configuration_B_Baseline
    mutation_operator: M03  # Convergence — focus on decision point (softmax apex)
    changed_variable: attention_logit_softcap
    changed_from: infinity  # no capping
    changed_to: 50.0
    reason_for_mutation: >
      Phase 3 failure mechanism: at long sequences, QK^T logits grow large →
      softmax saturates → near-uniform attention → routing degrades. The softcap
      directly addresses this by bounding logit magnitude before softmax.
      M03 (Convergence) is appropriate because this focuses optimization on
      the apex of the attention computation — the softmax decision boundary.
    expected_effect: >
      Prevents attention entropy collapse at n >> training length.
      Slight quality change at normal lengths (logits rarely exceed 50.0 for
      well-trained models). Significant quality preservation at 4–8× training
      length. Effectively extends the system's operating range.
      Adds zero parameters. One scalar hyperparameter.
  implementation_delta: >
    Replace: score = QK^T / √d_k
    With:    score = cap * tanh(QK^T / (√d_k * cap))  where cap = 50.0
    Effect:  logits bounded to [-cap, +cap] regardless of n
    Note:    At small logit values, tanh(x) ≈ x so behavior is unchanged
             in the standard operating regime.
```

---

## Variant D — Role-Preserving Transfer to Protein Sequence Modeling
```yaml
variant:
  name: Variant_D
  lineage:
    parent: Configuration_B_Baseline
    mutation_operator: M02  # Role-Preserving Structural Transfer
    changed_variable: attention_window_structure  # as a proxy for domain constraints
    reason_for_mutation: >
      Test whether the decoder-only causal architecture transfers to protein
      sequence generation, where the token vocabulary is amino acids (20 tokens)
      and the output constraint is 3D-foldable structure rather than grammaticality.
    source_structure:
      reservoir: Token embedding (50K vocabulary → R^d_model)
      channel: Causal masked self-attention (temporal sequence)
      boundary: Causal monotonicity constraint (i03)
    target_structure:
      reservoir_equivalent: Amino acid embedding (20 tokens + special tokens → R^d_model)
      channel_equivalent: Self-attention over residue sequence (no strict causality required)
      boundary_equivalent: >
        Structural validity constraint: generated sequence must fold to stable protein.
        This is NOT a causal temporal constraint but a global thermodynamic constraint.
    mapping_confidence: medium
    exceptions: >
      CRITICAL EXCEPTION 1 — Causality mismatch:
        In language, the causal constraint (i03) is natural: you cannot know
        future words when generating the next word.
        In protein generation, no such constraint exists: protein folding is
        determined by the full sequence simultaneously, not causally.
        Transfer of i03 is INVALID for native protein modeling.
        Required change: remove causal masking → bidirectional self-attention.
        This invalidates f04 (chain-rule factorization) in the target domain.

      CRITICAL EXCEPTION 2 — Vocabulary scale mismatch:
        Source: |V| = 50,000 tokens. Weight tying (m05) is efficient.
        Target: |V| = 20–30 amino acid tokens. Weight tying provides near-zero
        benefit; the embedding matrix is trivially small.
        The tied-weight efficiency argument does not transfer.

      CRITICAL EXCEPTION 3 — Position semantics mismatch:
        In language, position encodes temporal sequence order (syntactic relevance).
        In proteins, position encodes residue index along a chain, but nearby
        residues in 3D space may be far apart in sequence (long-range contacts).
        Linear relative position bias (ALiBi/RoPE) may be suboptimal for
        capturing 3D spatial relationships. MSA (multiple sequence alignment)
        features would be required, which have no equivalent in the source.

      TRANSFERS CLEANLY:
        - s01 (content-addressed retrieval) — amino acids attend by biochemical compatibility
        - s02 (parallel heads) — multiple chemical interaction types simultaneously
        - m02 (residual bypass) — depth without gradient degradation
        - m04 (position-wise FFN) — per-residue feature transformation
        - s04 (iterated refinement) — iterative representation refinement
```

---

## Variant E — Grouped Query Attention (GQA)
```yaml
variant:
  name: Variant_E
  lineage:
    parent: Configuration_B_Baseline
    mutation_operator: M04  # Disequilibrium — introduce deliberate asymmetry
    changed_variable: kv_cache_sharing
    changed_from: multi_head  # 16 KV heads
    changed_to: grouped_query  # 4 KV heads, 16 Q heads
    reason_for_mutation: >
      Multi-head attention has symmetric Q/K/V head counts. This creates
      memory pressure at inference: the KV cache scales as O(n · h · d_k · 2).
      Grouped Query Attention introduces asymmetry (M04: Disequilibrium) —
      16 query heads but only 4 KV heads. Each KV head is shared across
      4 query heads. This tests whether the KV computation is over-parameterized
      relative to the query computation.
    expected_effect: >
      KV cache size reduced by 4× (16→4 KV heads). Inference memory bandwidth
      reduced proportionally. Training quality drop: empirically < 0.5% on
      standard benchmarks (per Ainslie et al. 2023 GQA paper).
      Training FLOPs unchanged (Q projections dominate).
      High practical value for deployment at long context lengths.
  implementation_delta: >
    Current:  h=16 independent W_i^Q, W_i^K, W_i^V projections
    Variant:  h=16 W_i^Q projections, g=4 W_j^K, W_j^V projections
              Query heads i=1..4 share KV head j=1; i=5..8 share j=2; etc.
    KV cache: reduces from n×16×d_k to n×4×d_k per layer
```

---

# PHASE 6 — Counterfactual State Simulations (Parallel)

One simulation agent per variant. Three environments each: baseline, stressed (long sequences), perturbed (OOD domain).

---

## Simulation A — Variant A (Pre-LN)
```yaml
simulation:
  variant: Variant_A
  environments:
    - environment: baseline
      initial_state: "N=12 post-LN decoder, n=512, standard language modeling"
      transition_rules: "Pre-LN equalizes gradient scale across layers"
      future_state_t1: "Training loss decreases faster in first 10K steps"
      future_state_t2: "Converges to slightly lower perplexity (estimated -2% BPC)"
      failure_boundary: "No known failure mode for pre-LN at this scale"
      fitness_score: 1.08  # baseline fitness = 1.00; +8% from stability
    - environment: stressed
      initial_state: "N=12 post-LN decoder, n=4096 (8× training length)"
      transition_rules: "Pre-LN prevents gradient magnitude explosion at depth"
      future_state_t1: "Stable training continues; no gradient spike"
      future_state_t2: "Quality maintained; post-LN would show instability here"
      failure_boundary: "N > 48 layers may still show instability (known limit)"
      fitness_score: 1.15
    - environment: perturbed
      initial_state: "Fine-tuning on code domain after language pretraining"
      transition_rules: "Pre-LN allows higher LR during fine-tuning"
      future_state_t1: "Faster adaptation to new domain distribution"
      future_state_t2: "Code generation quality higher than post-LN baseline"
      failure_boundary: "None identified at this scale"
      fitness_score: 1.12
  aggregate_fitness: 1.117
```

## Simulation B — Variant B (RoPE)
```yaml
simulation:
  variant: Variant_B
  environments:
    - environment: baseline
      initial_state: "ALiBi decoder, n=512, standard language modeling"
      transition_rules: "RoPE: position encoded in Q/K rotation; no additive logit bias"
      future_state_t1: "Attention patterns similar to ALiBi at short range"
      future_state_t2: "Quality statistically identical to ALiBi at n=512"
      failure_boundary: "None at training length"
      fitness_score: 1.02
    - environment: stressed
      initial_state: "n=8192 (16× training length of n=512)"
      transition_rules: >
        RoPE: rotation angle grows with position; relative offset preserved
        ALiBi: linear bias grows unbounded → may dominate content signal
      future_state_t1: "RoPE maintains relative position information correctly"
      future_state_t2: "Quality degradation much slower than ALiBi at extreme lengths"
      failure_boundary: >
        RoPE degrades at very high frequency (position > 10× training);
        can be partially fixed by RoPE scaling (frequency interpolation)
      fitness_score: 1.22
    - environment: perturbed
      initial_state: "Structured data (code, tables) with repetitive positional patterns"
      transition_rules: "RoPE's rotary structure captures periodic patterns naturally"
      future_state_t1: "Better code indentation sensitivity (positional precision)"
      future_state_t2: "Improved F1 on structured extraction tasks"
      failure_boundary: "None identified for this domain"
      fitness_score: 1.10
  aggregate_fitness: 1.113
```

## Simulation C — Variant C (Softcap)
```yaml
simulation:
  variant: Variant_C
  environments:
    - environment: baseline
      initial_state: "No softcap, n=512"
      transition_rules: "cap=50.0 applied; logits at n=512 typically < 20.0"
      future_state_t1: "Behavior identical to baseline (tanh(x) ≈ x for |x| << cap)"
      future_state_t2: "No measurable quality change at normal lengths"
      failure_boundary: "None"
      fitness_score: 1.00
    - environment: stressed
      initial_state: "n=4096 without softcap; logits can reach 100+"
      transition_rules: "Softcap clips logits to [-50, +50] → prevents saturation"
      future_state_t1: "Attention distributions remain informative (not uniform)"
      future_state_t2: "BPC degradation from n=512 to n=4096 reduced by ~40%"
      failure_boundary: "cap too low (< 10) would clip even normal-length logits"
      fitness_score: 1.18
    - environment: perturbed
      initial_state: "Domain with high token repetition (legal text)"
      transition_rules: "Repetition causes high-magnitude logits; softcap stabilizes"
      future_state_t1: "Attention does not collapse to trivial copy patterns"
      future_state_t2: "Quality preserved on repetitive domains"
      failure_boundary: "None identified"
      fitness_score: 1.09
  aggregate_fitness: 1.090
```

## Simulation D — Variant D (Protein Transfer)
```yaml
simulation:
  variant: Variant_D
  environments:
    - environment: baseline
      initial_state: "Causal decoder applied to amino acid sequence generation"
      transition_rules: >
        Causal masking retained (incorrect for proteins — see exceptions in Phase 5)
      future_state_t1: "Model generates valid amino acid sequences"
      future_state_t2: "But sequences may not fold correctly — global constraint violated"
      failure_boundary: "Causal factorization incompatible with protein thermodynamics"
      fitness_score: 0.61  # structure validity penalty dominates
    - environment: stressed
      initial_state: "Long protein (n=1000 residues)"
      transition_rules: "Quadratic cost still present; long-range contacts missed by causal mask"
      future_state_t1: "Critical disulfide bonds between residue 50 and 800 missed"
      future_state_t2: "Protein unfoldable — fitness collapses"
      failure_boundary: "Causal masking creates fatal information asymmetry for proteins"
      fitness_score: 0.32
    - environment: perturbed
      initial_state: "Without causal mask (corrected per exception clause)"
      transition_rules: "Bidirectional attention allowed; exceptions applied"
      future_state_t1: "Long-range contacts can be captured"
      future_state_t2: "Model approaches ESM/ProtTrans quality"
      failure_boundary: "Missing MSA features limits co-evolutionary signal capture"
      fitness_score: 0.85
  aggregate_fitness: 0.593  # Low due to invalid causal transfer
```

## Simulation E — Variant E (GQA)
```yaml
simulation:
  variant: Variant_E
  environments:
    - environment: baseline
      initial_state: "16 KV heads → 4 KV heads, n=512"
      transition_rules: "Q diversity maintained; KV shared within groups"
      future_state_t1: "Training loss virtually identical to baseline"
      future_state_t2: "Quality within 0.3% BPC of multi-head baseline"
      failure_boundary: "g=1 (MQA) shows measurable degradation; g=4 is safe"
      fitness_score: 0.99
    - environment: stressed
      initial_state: "n=8192, 16-bit inference on 80GB GPU"
      transition_rules: "KV cache: 4×d_k per layer vs 16×d_k; 4× memory saving"
      future_state_t1: "Fits in memory at 4× longer context without quality loss"
      future_state_t2: "Enables batch size increase → higher training throughput"
      failure_boundary: "None identified at g=4"
      fitness_score: 1.35  # high inference efficiency gain
    - environment: perturbed
      initial_state: "High-throughput serving (1000 concurrent requests)"
      transition_rules: "KV cache bandwidth reduced 4× per request"
      future_state_t1: "4× more requests servable per GPU"
      future_state_t2: "Inference cost per token reduced ~40% in memory-bound regime"
      failure_boundary: "g < 2 shows degradation on attention-heavy tasks"
      fitness_score: 1.28
  aggregate_fitness: 1.207
```

---

# PHASE 7 — Invariant Filter & Negative Extraction

Invariants checked:
- **i01**: Simplex constraint — attention weights must remain in probability simplex
- **i02**: Causal order — no structural change may create future-to-past information flow
- **i03**: Role preservation — transferred mechanisms must preserve their functional role
- **i04**: Dimension invariance — d_model must be constant throughout

```yaml
invariant_validation:

  - variant: Variant_A
    status: PASSED
    checks:
      i01: "softmax still applied to logits; simplex preserved"
      i02: "normalization position before sublayer; no causal order change"
      i03: "LayerNorm is a per-position operation; role unchanged"
      i04: "output dimension unchanged; residual addition valid"
    reason: "Pre-LN is a structural reorder, not a functional change. All invariants preserved."

  - variant: Variant_B
    status: PASSED
    checks:
      i01: "softmax applied to rotated logits; simplex preserved"
      i02: "rotation applied independently to Q and K; no cross-position contamination"
      i03: "RoPE encodes relative position, not absolute future position"
      i04: "Q and K dimensions unchanged; rotation is dimension-preserving"
    reason: "RoPE modifies query/key vectors via rotation in d_k space. All invariants preserved."

  - variant: Variant_C
    status: PASSED
    checks:
      i01: "softmax applied after softcap; output still in simplex"
      i02: "logit bounding is applied symmetrically; no causal leakage"
      i03: "softcap is a monotonic function; relative ordering of logits preserved"
      i04: "no dimensional change"
    reason: "Softcap is a logit preprocessing step. Simplex constraint still holds post-softmax."

  - variant: Variant_D
    status: REJECTED
    violated_invariant: i02  # Causal Order (repurposed as Role Preservation)
    reason: >
      The transfer retains the causal masking (i03/s03) in a domain where
      temporal causality is not a valid organizing constraint. For proteins,
      the constraint governing valid states is thermodynamic, not temporal.
      The causal mask forces an invalid factorization: P(aa_t | aa_{<t}) where
      aa_{>t} residues may be critical for determining aa_t's folding state.
      The transferred architecture generates structurally invalid proteins.
    negative_constraints:
      failed_transfer:
        source: Causal decoder self-attention (s03)
        target: Protein residue self-attention
        reason: >
          Causal temporal ordering has no valid analog in protein folding.
          Structural homomorphism fails because the constraint domains
          (time-series vs. thermodynamic energy landscape) are incompatible.
        resolution: "Must remove causal mask before transfer is valid."
      invalid_mutation:
        variable: kv_cache_sharing (not changed — but relevant)
        reason: >
          If protein model uses bidirectional attention, the KV cache structure
          of the causal decoder is irrelevant at inference (no autoregressive
          generation in the same sense). KV cache optimization would need
          redesign for iterative refinement inference.

  - variant: Variant_E
    status: PASSED
    checks:
      i01: "attention computation per head unchanged; simplex preserved"
      i02: "KV sharing within query groups; no cross-temporal leakage"
      i03: "Q diversity maintained; roles of Q (query) and KV (memory) preserved"
      i04: "output dimensions unchanged; W^O projection still valid"
    reason: "GQA reduces KV parameter count but preserves all functional roles and invariants."

negative_constraints:
  failed_transfer:
    - source: "Causal decoder temporal ordering (s03)"
      target: "Protein folding sequence modeling"
      reason: "Temporal causality is not isomorphic to thermodynamic validity. Transfer creates invalid protein structures."
    - source: "Weight tying efficiency argument (m05) — large vocabulary"
      target: "Protein amino acid vocabulary (20 tokens)"
      reason: "Parameter count argument does not transfer; 20-token embedding is trivially small."

  invalid_mutations:
    - variable: normalization_position
      attempted_value: "no_normalization"
      reason: "Removing LayerNorm entirely causes unbounded activation growth in pre-LN variant at depth; training diverges."
      violated_invariant: "training_stability (derived from i04 + m02)"
    - variable: head_count
      attempted_value: "h=128"
      reason: "d_k = d_model/h = 512/128 = 4 dimensions per head. Inner-product similarity in 4D is degenerate; heads fail to learn distinct patterns."
      violated_invariant: "i02 (cost conservation holds but practical limit on d_k >= 16 is violated)"
```
