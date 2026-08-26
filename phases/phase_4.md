# Leonardo Lab — Phase 4: Parameter Space Extraction
## System: Decoder-Only Transformer (Configuration B)

---

# PHASE 4 — Parameter Space Extraction

Extracted from the causal architecture (Phase 3). Each variable is typed,
range-bounded, and tied to its source node in the formal-elements graph.

```yaml
parameter_space:

  - variable:
      name: normalization_position
      source_node: m02  # residual bypass
      type: structural_topology
      description: >
        Whether LayerNorm is applied AFTER the residual addition (Post-LN, original)
        or BEFORE the sublayer (Pre-LN). This governs gradient scaling at depth.
      range:
        values: [post_norm, pre_norm, sandwich_norm]
        current: post_norm
      unit: categorical
      causal_sensitivity: >
        High. Post-LN creates gradient scale differences across layers.
        Pre-LN equalizes gradient magnitudes, improving training stability
        for deep models. Changes gradient flow through ALL N layers simultaneously.

  - variable:
      name: position_encoding_type
      source_node: o02  # position injection
      type: projection_geometry
      description: >
        The mathematical form of the relative position signal injected into
        attention. Current: ALiBi-style linear bias. Alternatives include
        RoPE (rotary), T5-style learned buckets, no encoding.
      range:
        values: [alibi_linear, rope_rotary, t5_relative_learned, no_position]
        current: alibi_linear
      unit: categorical
      causal_sensitivity: >
        High. Governs length generalization (i06). RoPE embeds position into
        query/key vectors directly, enabling more principled extrapolation.

  - variable:
      name: ffn_expansion_ratio
      source_node: m04  # position-wise FFN
      type: transport_capacity
      description: >
        The multiplier applied to d_model to get d_ff (FFN hidden dimension).
        d_ff = ratio × d_model. Controls local processing capacity per token.
      range:
        min: 2
        max: 16
        current: 4
        typical_values: [2, 4, 8, 16]
      unit: dimensionless_multiplier
      causal_sensitivity: >
        Medium. Increasing ratio expands per-token capacity but increases
        FLOPs quadratically relative to d_model. Most critical for tasks
        requiring strong local feature extraction.

  - variable:
      name: head_count
      source_node: s02  # parallel multi-subspace projection
      type: projection_geometry
      description: >
        Number of parallel attention heads h. Per i02 (cost conservation),
        d_k = d_model / h. More heads = smaller per-head subspace.
      range:
        min: 1
        max: 128
        current: 16
        constraint: "d_k = d_model / h must be >= 16 for stable attention"
      unit: count
      causal_sensitivity: >
        Medium-Low. Paper shows quality peaks at moderate h, drops with too few
        or too many. i02 keeps cost constant so this is a free architectural
        parameter within the d_k >= 16 constraint.

  - variable:
      name: attention_logit_softcap
      source_node: m01  # inner-product routing gate
      type: resistance
      description: >
        A tanh-based logit clipping applied before softmax:
        logit_capped = cap * tanh(logit / cap). Prevents attention entropy
        collapse at large sequence lengths by bounding logit magnitude.
        If cap = infinity, no capping (current baseline).
      range:
        min: 10.0
        max: infinity
        current: infinity  # no capping in baseline
        recommended: 50.0
      unit: logit_scale
      causal_sensitivity: >
        High for long sequences. Prevents softmax saturation (the primary
        failure mechanism identified in Phase 3). Low cost — one scalar.

  - variable:
      name: layer_count
      source_node: s04  # iterated layer stack
      type: transport_capacity
      description: >
        Number of transformer layers N. Governs depth of the discrete
        dynamical system (f03). More layers = more refinement iterations.
      range:
        min: 2
        max: 96
        current: 12
      unit: count
      causal_sensitivity: >
        High. Strongly correlated with quality and FLOPs. But returns
        diminishing after ~24 layers. Each layer adds O(n²·d + n·d_ff) FLOPs.

  - variable:
      name: dropout_rate
      source_node: m06  # stochastic unit suppression
      type: resistance
      description: >
        Fraction of activations zeroed during training. Controls overfitting
        pressure. Higher rate = stronger regularization but slower convergence.
      range:
        min: 0.0
        max: 0.5
        current: 0.1
      unit: probability
      causal_sensitivity: >
        Low-Medium. At scale (large data), dropout has diminishing effect
        because data diversity provides implicit regularization.

  - variable:
      name: weight_tying
      source_node: m05  # vocabulary projection
      type: structural_topology
      description: >
        Whether the input embedding matrix and the pre-softmax projection
        matrix are the same tensor (tied) or independent (untied).
      range:
        values: [tied, untied]
        current: tied
      unit: categorical
      causal_sensitivity: >
        Medium. Tied weights reduce parameters by |V| × d_model (~25M params
        for d_model=512, |V|=50K). May slightly reduce quality at very large
        scale where the two roles diverge.

  - variable:
      name: attention_window_structure
      source_node: s01  # content-addressed retrieval
      type: projection_geometry
      description: >
        Whether all layers use full global attention, or a mixture of
        local-window and global attention layers. Controls the O(n²) bottleneck.
      range:
        values:
          - all_global               # baseline: every layer is full attention
          - sliding_window_all       # every layer uses window of size r
          - hybrid_local_global      # first N-k layers local, last k global
          - alternating              # alternate local and global
        current: all_global
      unit: categorical
      causal_sensitivity: >
        Very High for long sequences. Switching from all_global to
        hybrid_local_global reduces total FLOPs from O(n²·N·d) to
        O(n·r·(N-k)·d + n²·k·d). Critical for n >> training length.

  - variable:
      name: kv_cache_sharing
      source_node: s02  # parallel heads
      type: transport_capacity
      description: >
        Whether key and value projections are shared across query heads
        (Multi-Query Attention: 1 KV head, h Q heads) or grouped
        (Grouped Query Attention: g KV heads, h Q heads where g < h).
        Controls inference memory bandwidth and KV cache size.
      range:
        values:
          - multi_head    # h KV heads (baseline, i02 conserves cost)
          - grouped_query # g KV heads where 1 < g < h
          - multi_query   # 1 KV head, maximum sharing
        current: multi_head
      unit: categorical
      causal_sensitivity: >
        High for inference efficiency. Minimal quality loss at grouped_query (g=8).
        Multi-query can degrade quality measurably. Does not affect training FLOPs.
```

**Total variables extracted: 10**
**High-sensitivity variables: normalization_position, position_encoding_type, attention_logit_softcap, attention_window_structure**
**Medium-sensitivity: ffn_expansion_ratio, layer_count, kv_cache_sharing**
**Low-sensitivity: head_count (within constraints), dropout_rate, weight_tying**
