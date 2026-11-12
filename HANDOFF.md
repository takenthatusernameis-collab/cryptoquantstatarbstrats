# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T17:18:47Z UTC (AUTHORITATIVE)

**Repo-prioritized focus:** `cryptoquantstatarbstrats` means crypto quant stat-arb strategies. The only economically relevant question is whether a signal produces costed out-of-sample PnL from real spot prices. The prior handoff's C273 "edge" is not tradable: it computes PnL from log quote-volume changes, not price. The next session must stop hardening volume-return PnL and run the price-PnL tradability gate below.

### BOTTLENECK REMOVED — C273 IS A VOLUME-RETURN METRIC, NOT A TRADABLE PnL
- `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py:199`: `r = np.log(vv).diff().dropna()` where `vv` is quote volume.
- Same file `:225`: `rets = r.loc[feat.index].shift(-1).dropna()`; `:271-277`: `npn = rets`, `strat = ppn * npn - trades * tc`.
- `spot_df` is loaded at `:181` but used only for symbol intersection at `:184`; no spot price return enters PnL.
- Therefore C273's `oos_edge_proven:true` and `bh_oos_net_mean` are volume-return metrics. The prior C277 "hardening suite" would polish a non-tradable number. Do not run that plan.
- C273 artifacts remain frozen and preserved; no edits. Their status is `METRIC_VALID_BUT_NOT_TRADABLE_UNTIL_PRICE_PNL_GATE`.
- The 7 "pool" families are already `oos_edge_proven:false`; the prior "unrun pool" claim remains false. Do not re-run them.
- The prior handoff's Hurst path was wrong. Correct path: `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`.
- No active heavy process. Working tree clean at `main`, HEAD `b36e3cd`, up to date with `origin/main`.

### IMMEDIATE MANDATORY CAMPAIGN — C277 = C273 PRICE-PnL TRADABILITY GATE

**C277A (required first):**
1. Create `scripts/run_c277_price_pnl_revalidation.py`.
2. Reuse the C273 feature/params/spec exactly: W_RR=168, ALB=336, m=2, tau=1, eps_scale=0.5, w_min=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24; WF train=720/test=168/step=168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps. Import the feature and helpers from the C273 runner/split script; do not re-derive the feature.
3. Compute the feature from real quote volume exactly as C273; compute PnL from spot log-price returns: `r_price = np.log(spot_df[sym]).diff().dropna()`, align to feature timestamps, shift(-1), then use the same positions, max-hold carry, cost grid, and OOS mask.
4. Preflight: reproduce the C273 volume-return baseline on one asset (e.g., ADA) within 1e-9 before running all 11. If runtime is excessive, optimize the recurrence-matrix math with identical results and re-verify that one-asset baseline. Do not change the feature.
5. Emit `reports/campaign277_c273_price_pnl_revalidation_<ts>.json` with per-asset and cross-asset OOS net sum/mean at 0/5/10/20/40 bps, exposure, turnover, break-even total cost bps, B&H spot-price mean, original volume-return values for comparison, and `price_pnl_edge_proven` using the same rule (exposure>0, all cost slices net >0, and mean net strategy > mean B&H spot-price return on the same WF windows; use net-of-cost, not gross).
6. Emit `reports/campaign273_metric_validity_finding_<ts>.json` with the exact file:line evidence and verdict `NON_TRADABLE_METRIC_UNTIL_PRICE_PNL_GATE`.
7. Fail-closed on missing cache, hash mismatch, non-finite values, or spec mismatch. No network, no synthetic data, no threshold weakening.

**C277B (only if `price_pnl_edge_proven=true`):** harden the price-PnL edge, not volume PnL. Emit:
- `reports/campaign277_price_cost_breakeven_<ts>.json`
- `reports/campaign277_price_bootstrap_<ts>.json`
- `reports/campaign277_price_regime_<ts>.json`
- `reports/campaign277_price_loo_<ts>.json`
- `reports/campaign277_verdict_<ts>.json`

Verdict `PROMOTE_READY` only if break-even total cost >=20 bps AND all >=3 chronological subperiods have non-negative cross-asset price PnL at fee0 AND leave-one-asset-out never flips cross-asset price PnL negative at fee0/fee20. Otherwise `NOT_PROMOTED` with the precise failing condition.

**C278 (mandatory same-session continuation if `price_pnl_edge_proven=false`):**
- Do not stop at the negative result. Run a price-only baseline using the existing `CointegrationPairsStrategy` / `examples/run_pairs_multi.py` on the 11-asset spot cache, same WF/cost grid, with an equal-weight B&H benchmark. Emit `reports/campaign278_price_only_baseline_<ts>.json` and `reports/tradable_edge_registry_<ts>.json`.
- If the pairs strategy is blocked by missing gates, fail closed and run the existing single-asset `MeanReversionStrategy` / `examples/run_mean_reversion_real.py` on the same 11 assets, with the same WF/cost grid and B&H benchmark. Do not fabricate gates or invent a new feature.
- The registry must record `return_basis` (`spot_price` vs `quote_volume`) and `price_pnl_edge_proven` for every candidate; volume-only candidates are `NOT_TRADABLE`.

### SESSION COMPLETION RULE
The session is NOT complete until:
- C277A artifact and metric-validity finding exist as valid JSON, with SHA256 recorded from file bytes.
- C277B or C278 is completed and its artifact exists on disk.
- This handoff is updated with the exact paths, SHA256s, and a new UTC timestamp.
- No planning-only or status-only turn is acceptable.

### HARD BANS
- No status-only work. No planning-only turns. No additional single-feature "try the next statistic" search.
- No re-running C1-C276 or the 7 pool families; evidence already exists.
- No network refetch; no synthetic or fabricated data; no threshold weakening.
- No edits to frozen C273 artifacts. C277 reads them; it does not rewrite them.
- No edits to `research_state/state.yaml` unless explicitly requested.
- Record all new/updated artifact SHA256s from file bytes.

## FROZEN C273 VOLUME-RETURN BASELINE (EVIDENCE ONLY — DO NOT HARDEN)
- OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`
- Robustness `reports/campaign273_robustness_dossier_20261112T051659Z.json` sha256 `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`
- Sensitivity `reports/campaign273_param_sensitivity_20261112T052846Z.json` sha256 `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`
- Promotion JSON `reports/campaign273_promotion_evidence_package_20261112T054614Z.json` sha256 `7aff2e6031d5ca0aa9a00c05d1320800b13cc767328df4c5664b9b5964c0975c`
- Split `reports/campaign273_split_decomposition_20261112T052106Z.json` sha256 `2b4da1e65cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`
- Volume-return cross-asset OOS net sums: fee0 +80.68, fee5 +79.42, fee10 +78.16, fee20 +75.64, fee40 +70.60. These are not spot-price PnL.
- Fragility: only 9/11 assets positive (DOT -2.18, SOL -2.22 at fee0); top1 (BNB) = 23.9% and top3 = 64.7% of positive fee0 net.
- Sensitivity: 21/27 edge-positive; all 6 failures are W_RR=192. Baseline W_RR=168 reproduces.

## STATE SNAPSHOT (verified 2026-11-12T17:18Z UTC)
- **Env:** `python3 3.12.3`; `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`. Ruff/mypy not installed here; skip lint/typecheck until available.
- **Data:** `data/cache/` = 68 real files. Spot cache `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`; volume pkl sha256 `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`; volume meta sha256 `4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616`; provenance sha256 `c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89`. No network refetch. No synthetic data.
- **Git:** clean at `main`, HEAD `b36e3cd`, up to date with `origin/main`.
- **Canonical handoff:** this file only.
- **C273:** frozen; volume-return metric; conditional volume-return edge only. Not tradable until C277A price-PnL gate.
- **C274/C275/C276:** NO EDGE. No action needed.
- **C277:** PENDING. No C277 artifacts exist yet; C277A is the sole immediate deliverable.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T17:18:47Z UTC.**