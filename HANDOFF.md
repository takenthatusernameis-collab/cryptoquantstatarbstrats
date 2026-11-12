# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T17:26:17Z UTC (AUTHORITATIVE)

**Repo-prioritized focus:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. The only economically relevant question is whether a signal produces **costed out-of-sample PnL from real spot prices**. Anything measured in quote-volume return units is not a PnL and is not tradable.

**This session already removed the two hard bottlenecks. Do not redo them:**
1. **C273 volume-return "edge" is dead as a tradable claim.** C277A re-ran the exact C273 feature / positions / WF / cost grid but computed PnL from real spot log-price returns. Result: `price_pnl_edge_proven=false`; cross-asset price PnL is **negative at every cost slice** (fee0 **−1.7524**, fee5 −3.0134, fee10 −4.2744, fee20 −6.7964, fee40 −11.8404). The volume-return baseline reproduced to **max_abs_diff 0.0** (tolerance 1e-9), so the negative price result is real, not a feature regression. C273 remains frozen; its volume-return numbers are evidence only.
2. **The single-config price-only baseline is exhausted.** C278 attempted `CointegrationPairsStrategy` on the real 11-asset spot cache with strict fail-closed gates: all three canonical pairs (BTC/ETH, ETH/SOL, BTC/SOL) produced **0 OOS exposure** (gates fail closed). It then ran the mandated single-asset `MeanReversionStrategy` fallback (lookback 30, entry 2.0, exit 0.5) on the same 11 assets: **no edge**, cross-asset price PnL **−40.2291** at fee0 (fee40 −78.1091). Every one of 16 registry candidates is `NOT_TRADABLE`.

**Bottom line:** no existing candidate has a costed spot-price edge. Do not re-run C1–C278, the 7 pool families, or the C273 volume families. The next session must run the **C279 broad price-only strategy sweep** below, on real spot prices only.

### C279 — MANDATORY HEAVY FOCUS CAMPAIGN (price-only strategy sweep, 11-asset real spot cache)

**C279A (required first):** create `scripts/run_c279_price_only_sweep.py`. Load the real spot cache `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, 11 assets, 5112 hourly bars). Do **not** fetch network, do **not** fabricate data.

Sweep all three price-only families on the **same** WF 720/168/168 and cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]] bps`, with an equal-weight B&H spot-price benchmark:
- `MeanReversionStrategy` (existing `strategies/mean_reversion.py`): lookback ∈ {24, 48, 96, 120} × entry_threshold ∈ {1.5, 2.0, 2.5} × exit_threshold ∈ {0.25, 0.5}.
- `MomentumStrategy` (existing `strategies/momentum.py`): n ∈ {10, 20, 40} × m ∈ {20, 40, 80} × entry_threshold ∈ {0.005, 0.01, 0.02}.
- `CointegrationPairsStrategy` (existing `strategies/pairs_trading.py`): **all 17 pairs** in `reports/portfolio_real.json` `cointegration_diagnostics` (not just the 3 canonical), strict enriched gates, cached diagnostics only; record per-pair OOS exposure and gate-block reason.

Evaluation must match C277/C278 exactly: causal positions, `trades=|diff(pos)|`, `strat = pos*ret − trades*tc`, OOS slice per WF window, exposure>0, all cost slices OOS net sum > 0, and mean OOS net > mean B&H spot-price mean. Use net-of-cost.

Emit `reports/campaign279_price_only_sweep_<ts>.json` (per-config, per-asset and cross-asset OOS net sum/mean at 0/5/10/20/40 bps, exposure, turnover, break-even total cost bps, B&H spot mean, and `price_only_edge_proven` per config) and refresh `reports/tradable_edge_registry_<ts>.json` recording `return_basis` (`spot_price` vs `quote_volume`), `price_pnl_edge_proven`, `tradable`, and `status` for every candidate. Volume-only candidates stay `NOT_TRADABLE`.

**C279B (only if ≥1 config has `price_only_edge_proven=true`):** harden that config only — break-even total cost bps, ≥3 chronological subperiods all non-negative at fee0, leave-one-asset-out never flips cross-asset PnL negative at fee0/fee20. Emit `reports/campaign279_verdict_<ts>.json`. Verdict `PROMOTE_READY` only if break-even ≥20 bps AND all ≥3 subperiods non-negative at fee0 AND LOO never flips negative at fee0/fee20; otherwise `NOT_PROMOTED` with the exact failing condition. Do not harden a volume-return metric.

**C279C (only if C279A finds zero tradable configs):** stop the single-config search. Emit a definitive negative finding `reports/campaign279_negative_result_<ts>.json` stating no spot-price strategy config in the repo produces costed OOS PnL on the real 11-asset cache, and list the exact grids tried. Do not invent a new statistic, lower thresholds, or fabricate gates.

### SESSION COMPLETION RULE
The session is NOT complete until:
- `reports/campaign279_price_only_sweep_<ts>.json` and a refreshed `reports/tradable_edge_registry_<ts>.json` exist as valid JSON with SHA256 computed from file bytes.
- C279B or C279C is completed and its artifact exists on disk.
- This handoff is updated with exact paths, SHA256s, and a new UTC timestamp.
- No planning-only or status-only turn is acceptable.

### HARD BANS
- No status-only or planning-only turns.
- No re-running C1–C278, the 7 pool families, or C273 volume-return families; evidence already exists.
- No network refetch; no synthetic/fabricated data; no threshold weakening; no gate coercion.
- No edits to frozen C273 artifacts (C277/C278 read them, never rewrite).
- No edits to `research_state/state.yaml` unless explicitly requested.
- Record all new/updated artifact SHA256s from file bytes.

## COMPLETED THIS SESSION — EVIDENCE (2026-11-12T17:22–17:26Z UTC)
- C277A price-PnL revalidation: `reports/campaign277_c273_price_pnl_revalidation_20261112T172258Z.json` sha256 `3b5bf3094ccd46d6afa985022232c245424a9634711a5a49df71c09f62e12f1b`
  - preflight ADA volume-return vs frozen C273: max_abs_diff **0.0** (tol 1e-9) PASS
  - `price_pnl_edge_proven=false`; cross-asset price PnL: fee0 −1.7524246012241438, fee5 −3.013424601224145, fee10 −4.274424601224145, fee20 −6.796424601224145, fee40 −11.840424601224145
  - frozen C273 volume-return cross reproduced exactly: fee0 +80.68391844301627 … fee40 +70.59591844301625
  - worst price assets: POL −0.609, ADA −0.606, ETH −0.498; best: DOT +0.329, AVAX +0.312, LTC +0.155 (all still negative after cost)
- C273 metric-validity finding: `reports/campaign273_metric_validity_finding_20261112T172258Z.json` sha256 `7a595cfadd330ffb5616cf23b041aa2fcc745ca2446eb7cfb92c03b5b170e231`
- C278 price-only baseline: `reports/campaign278_price_only_baseline_20261112T172556Z.json` sha256 `f484a0978bb9572779598a3d8b82779d70eed6638a7182a1724e8e90ceb8ffe2`
  - pairs blocked: BTC/ETH, ETH/SOL, BTC/SOL all 0 OOS exposure (strict gates fail closed)
  - mean-reversion fallback (lookback 30, entry 2.0, exit 0.5): `price_only_edge_proven=false`, cross-asset fee0 **−40.22912642021079**, fee40 **−78.1091264202108**; all 11 assets negative at fee0 (worst ADA −4.610, DOT −4.810)
- Tradable edge registry: `reports/tradable_edge_registry_20261112T172556Z.json` sha256 `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2` (16 candidates, 0 tradable, 16 not tradable)
- New scripts (uncommitted working tree): `scripts/run_c277_price_pnl_revalidation.py` sha256 `9f2fb2f441548d40c689df756c63cb8def3c46c9f25bad97f7bdca4cdfe669db`; `scripts/run_c278_price_only_baseline.py` sha256 `4156dba3b068694dd3f62f31a6de7332cb82526f7456dbef8a7eb1c1e2163c87`

## FROZEN C273 VOLUME-RETURN BASELINE (EVIDENCE ONLY — DO NOT HARDEN)
- OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`
- Robustness `reports/campaign273_robustness_dossier_20261112T051659Z.json` sha256 `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`
- Sensitivity `reports/campaign273_param_sensitivity_20261112T052846Z.json` sha256 `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`
- Promotion JSON `reports/campaign273_promotion_evidence_package_20261112T054614Z.json` sha256 `7aff2e6031d5ca0aa9a00c05d1320800b13cc767328df4c5664b9b5964c0975c`
- Split `reports/campaign273_split_decomposition_20261112T052106Z.json` sha256 `2b4da1e65cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`
- Volume-return cross-asset OOS net sums: fee0 +80.68, fee5 +79.42, fee10 +78.16, fee20 +75.64, fee40 +70.60. These are **not** spot-price PnL.
- Fragility: only 9/11 assets positive (DOT −2.18, SOL −2.22 at fee0); top1 (BNB) = 23.9% and top3 = 64.7% of positive fee0 net.
- Sensitivity: 21/27 edge-positive; all 6 failures are W_RR=192. Baseline W_RR=168 reproduces.

## STATE SNAPSHOT (verified 2026-11-12T17:26Z UTC)
- **Env:** `python3 3.12.3`; `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `statsmodels 0.15.0`. Ruff/mypy not installed here; skip lint/typecheck until available. Note `research_state/state.yaml` records a venv path (`/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`) that does not exist; use `/usr/bin/python3` with the deps above.
- **Data:** `data/cache/` = 68 real files. Spot cache sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b` (11 assets, 5112 hourly bars, 2026-04-01→2026-10-30). Volume pkl sha256 `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`. No network refetch. No synthetic data.
- **Git:** HEAD `a7ee8ce09dfce897a78721bae51a8285cf7e5961` on `main`. New artifacts and the two C277/C278 scripts are untracked (not committed). No active heavy process.
- **Canonical handoff:** this file only.
- **C273:** frozen; volume-return metric; **not tradable** (C277A price-PnL negative at all cost slices).
- **C274/C275/C276:** NO EDGE. No action needed.
- **C277:** DONE (`price_pnl_edge_proven=false`).
- **C278:** DONE (`price_only_edge_proven=false`; pairs blocked; mean reversion no edge).
- **C279:** PENDING. `scripts/run_c279_price_only_sweep.py` does not exist yet; C279A is the sole immediate deliverable.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T17:27:00Z UTC (verified current; C279 is sole mandatory next action).**