# Leonardo Lab — Phases 0–3
## System: Decoder-Only Transformer (Configuration B: V05b + V04)
## Generation: 1 (new archive)
## Input lineage: formal-elements.md → generative_design_analysis.md → this run

---

# PHASE 0 — Fitness Landscape & Search Budget

```yaml
fitness_landscape:
  objective:
    primary:
      metric: bits_per_character  # proxy for perplexity on language modeling
      direction: minimize
    secondary:
      - metric: flops_per_token
        weight: 0.35
      - metric: length_generalization_degradation  # quality drop beyond training length
        weight: 0.30
      - metric: peak_memory_per_token
        weight: 0.20
      - metric: training_stability  # divergence events per 100K steps
        weight: 0.15

  constraints:
    forbidden_states:
      - "causal_monotonicity_violated"     # i03: future tokens must not influence past
      - "attention_weights_outside_simplex" # i01: weights must sum to 1, be >= 0
      - "dimension_mismatch_at_residual"   # i04: d_model must be constant for bypass
      - "gradient_explosion_at_init"       # training must begin stably
    tradeoffs:
      accepted:
        - "small quality degradation (< 0.3 BPC) in exchange for 50%+ FLOPs reduction"
        - "increased parameter count if training stability improves"
      rejected:
        - "any change that increases max path length above O(log n)"
        - "any change that requires sequential computation across positions during encoding"

  measurement_function:
    formula: "fitness = (1 / BPC) * (1 / normalized_flops) * stability_factor"
    inputs:
      - BPC             # bits per character (lower = better)
      - normalized_flops # FLOPs relative to baseline (1.0 = same as baseline)
      - stability_factor # 1.0 if stable training, < 1.0 if divergence observed
    outputs:
      - fitness_score   # higher = better

  search_budget:
    max_variants_per_iteration: 5
    max_iterations: 10
    mutation_cost: 1.0
    simulation_cost: 0.5
    total_budget: 15.0  # 5 mutations (5.0) + 5 simulations (2.5) = 7.5 used this run
```

**Budget check:** 5 × 1.0 (mutations) + 5 × 0.5 (simulations) = **7.5 / 15.0 consumed**. ✅ WITHIN BUDGET.

---

# PHASE 1 — Ontological Reduction

**Input system:** Decoder-only Transformer (V05b + V04 from generative_design_analysis.md)
- V05b: encoder and cross-attention removed; single causal stack
- V04: sinusoidal absolute positions replaced with relative position biases

```yaml
ontology:
  primitives:
    driver: >
      Gradient signal backpropagated through the loss on next-token prediction.
      This is the primary moving force — it updates all learned parameters (o04)
      toward configurations that assign higher probability to correct tokens.
    resistance: >
      Quadratic attention cost O(n²·d) per layer. As sequence length grows,
      the cost of resolving all pairwise dependencies (p01) increases faster
      than linearly, eventually becoming the dominant computation.
    perturbation: >
      Variable sequence length; out-of-distribution token patterns;
      catastrophic forgetting when fine-tuning on new domains;
      gradient signal noise from label smoothing and dropout (m06).
    state_bias: >
      Learned parameter inertia. Weights trained on a distribution resist
      updating toward different distributions. The residual connection (m02)
      amplifies this: each layer learns a small delta, so the system
      is biased toward its initialization trajectory.

  constraints:
    deterministic_rules:
      - "Causal monotonicity: P(y_t | y_{<t}) — future tokens cannot influence past"
      - "Simplex constraint: attention weights in probability simplex at all times"
      - "Dimension invariance: every sublayer maps R^d_model → R^d_model"
      - "Chain-rule factorization: joint distribution = product of conditionals"
    substrate: >
      Real-valued parameter matrices in R^(d_model × *). All computation
      occurs in continuous vector spaces. Discrete symbols exist only at
      the input (embedding) and output (softmax projection) boundaries.
    organizing_layer: >
      The residual connection (m02) + LayerNorm structure. This is what
      maintains coherence across N layers — it prevents any single layer
      from catastrophically transforming the representation and ensures
      gradient flow through depth.

  GASO_current_state:
    generator: >
      Rules: causal decoder-only stack. N=12 layers of (masked self-attention
      + residual + LN + position-wise FFN + residual + LN). Relative position
      biases (ALiBi-style). Vocabulary projection with tied embedding weights.
      Adam optimizer with warmup-decay schedule (i05 coupling).
    action: none_yet
    state: >
      Configuration B baseline. BPC ≈ 1.12 (estimated on PTB-equivalent).
      FLOPs: O(n²·d·N). Training stable. Length generalization: degrades
      beyond 2× training length. All invariants (i01, i03, i04) preserved.
    observer: >
      Validation perplexity / BPC on held-out corpus. Attention pattern
      visualization (head specialization). Gradient norm monitoring.
    feedback: none_yet
```

---

# PHASE 2 — System Decomposition (Parallel)

*Three parallel agent tasks executed:*

## Agent 1: Source/Channel (s01 Convergent Projection, s02 Branching Transport)

```
Source: Token vocabulary (discrete symbols, |V| ≈ 50K)
  → Embedding matrix (m05 inverse): discrete → R^d_model    [CONVERGENT PROJECTION]
  → Positional bias injection (V04/o02): ordinal → additive logit bias
  → Input representation: R^(n × d_model)

Channel (s02 — Branching Transport):
  Input representation
    → h=16 parallel query projections (W_i^Q)               [BRANCHING]
    → h=16 parallel key projections (W_i^K)
    → h=16 parallel value projections (W_i^V)
  Each head: independent content-addressed retrieval (s01)
  Merge: Concat(head_1,...,head_h) · W^O                    [RECONVERGENCE]
```

## Agent 2: Transformation/Sink (m01 Causal Chain)

```
Transformation chain per layer (m01 — Causal Chain):
  Step 1: Masked self-attention
    Input X → Q=XW^Q, K=XW^K, V=XW^V
    Score = mask(QK^T / √d_k) → softmax → weights ∈ Δ^n    [i01 enforced]
    Causal mask zeros all j > i positions                    [i03 enforced]
    Output = weights · V

  Step 2: Residual + LayerNorm
    X' = LayerNorm(X + Attn(X))                             [m02: identity bypass]

  Step 3: Position-wise FFN
    FFN(x) = max(0, xW_1 + b_1)W_2 + b_2  ∀ positions     [m04: local, no coupling]
    Expansion ratio: d_ff = 4 · d_model

  Step 4: Residual + LayerNorm
    X'' = LayerNorm(X' + FFN(X'))                           [m02]

Sink: Final layer representation → Linear(d_model, |V|) → softmax → P(next token)
```

## Agent 3: Feedback/Correction (m06 Model-Failure Attribution)

```
Feedback loop:
  Forward pass → logits → cross-entropy loss against target tokens
  Loss → backpropagation through N layers via residual highways (m02)
  Gradient → Adam optimizer (s05) → parameter update (o04)
  Correction mechanisms:
    - Dropout (m06): stochastic suppression during forward pass
    - Label smoothing: softens target distribution → prevents overconfidence
    - Gradient clipping: prevents explosion through deep residuals
    - LR warmup-decay (i05): curriculum on gradient trust
```

**Component graph:**
```
[Vocabulary] →[Embedding]→ [Input Repr]
                               │
                    ┌──────────┼──────────┐
               [Q proj×h]  [K proj×h]  [V proj×h]    ← s02 branching
                    └──────────┼──────────┘
                         [Masked Attn]                ← s01 + i01 + i03
                               │
                        [Residual+LN]                 ← m02
                               │
                        [Position FFN]                ← m04
                               │
                        [Residual+LN]                 ← m02
                               │ ×N layers            ← s04 iteration
                               │
                    [Linear + Softmax]                ← m05 observer
                               │
                    [Cross-entropy Loss]
                               │
                    [Backprop via Adam]               ← s05 + m06
                               │
                         [Θ update]                   ← o04 memory
```

---

# PHASE 3 — Causal Architecture

```
CAUSAL GRAPH:

[Token Embedding (o01)] → [Position Bias Injection (V04/o02)] →
[Masked Self-Attention (s01/s02/i01/i03)] →
[Residual Bypass (m02/i04)] →
[Position-wise FFN (m04)] →
[Residual Bypass (m02/i04)] →
[×N layers (s04)] →
[Vocabulary Projection (m05)] →
[Softmax Distribution (i01 analog)] →
[Cross-entropy Loss] →
[Gradient Signal] →
[Adam Update (s05/i05)] →
[Parameter Memory (o04)] →
[feeds back to all projection matrices]

BOTTLENECK:
  Primary:   Masked self-attention (s01) — O(n²·d) cost per layer.
             At n=2048, n² = 4,194,304. At n=8192, n² = 67,108,864.
             The quadratic scaling is the binding constraint on context length.
  Secondary: Sequential decoding at inference (s03 + f04). Each new token
             requires a full forward pass; cannot parallelize token generation.

FAILURE MECHANISM:
  As sequence length n grows beyond training distribution:
    (1) Attention logits QK^T/√d_k become large → softmax saturates
    (2) Near-uniform attention → routing signal degrades → effective
        path length increases beyond O(1)
    (3) Position biases (V04) are not defined for offsets beyond training
        range → relative bias table lookup fails or extrapolates poorly
    (4) System fails gracefully (soft degradation) not catastrophically,
        but quality drops measurably beyond 2× training length.
```
