# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T09:57:36Z (P9/Campaign #5 completed)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## P9/CAMPAIGN #5 COMPLETION (THIS SESSION)
- **Deliverable A:** `reports/spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json` — NEW structurally different family: pairwise spread construction (55 pairs, 11 assets) + causal rolling OLS hedge + z-score mean-reversion + IS regime filters (abs corr>=0.45, half-life [2,240], spread-vol regime) + dollar-neutral legs + per-asset attribution vs B&H. Real cached spot 1h 2026-04-01..2026-10-30 (5112 bars), rolling WF 720/168/168, cost grid 0-40bps. **`oos_edge_proven=false` (0/11)**. Named: BTC oos_0bps_sum=-0.3205 (bh 0.0569), ETH -0.1513 (0.0609), SOL -0.4982 (0.2228), BNB -0.2971 (0.1679); all negative at 40bps. Flags: `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false`.
- **Deliverable B:** `reports/real_feed_unblock_status_20261105T095713Z.json` — no new real feeds with provenance found; cross_exchange_dual_venue/funding_basis_carry/term_structure_real_iv_vol_surface remain `blocked_no_real_feed`. Honest; no fabrication.
- **Deliverable C:** `reports/strategy_edge_registry_20261105T095736Z.json` — `supersedes: reports/strategy_edge_registry_20261105T095008Z.json`. Tests rerun: **832 passed, 1 skipped, 3566 warnings, 0 failed** (40.43s) via `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q`.
- **3 new artifacts produced.** `oos_edge_proven=false` (fail-closed, honest).

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 10 / CAMPAIGN #6 — MANDATORY.** Next agent MUST NOT do investigation-only work. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

## BOTTLENECKS (REMOVED — BINDING)
- **Tests:** `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` → **832 passed, 1 skipped, 0 failed** (2026-11-05T09:57Z).
- **Real spot cache:** `data/cache/*_2026-04-01_2026-10-30_1h.pkl` + `.meta.json` — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot. **Use as-is. Do not re-fetch.**
- **Pairs:** **PROVEN BLOCKED** (165/165). No re-scan. No gate weakening.
- **Feeds:** dual-venue/funding-basis-carry/real IV-vol surface `blocked_no_real_feed`. No fabricated feeds.
- **CI/archaeology:** Not a local blocker.

## CORE TRUTH (SETTLED)
- **Pairs cointegration:** PROVEN BLOCKED (fail-closed).
- **No proven net-of-cost OOS edge** on real cached spot 1h (11 assets, 5112 bars), rolling WF (720/168/168), cost grid {0,5,10,20}bps combos:
  - momentum (0/11): `reports/momentum_mr_costed_oos_20261105T081323Z.json`
  - mean_reversion (0/11): same
  - cross_sectional_risk_adjusted_return_rank (`oos_edge_proven=false`): `reports/spot_alt_signal_costed_oos_20261105T084619Z.json`
  - donchian_breakout_volfilter (0/11): `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json`
  - range_breakout_reversion_volband (0/11): `reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json`
  - spot_zscore_regime_mean_reversion_pairs (0/11, 55 pairs): `reports/spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json` (P9)
- **Latest registry:** `reports/strategy_edge_registry_20261105T095736Z.json` — **MUST be superseded by P10**.

## CAMPAIGN #6 (BINDING — CANNOT BE AVOIDED)
All obvious single-asset spot families and pairwise OLS-spread z-score MR on this 11-asset window have failed net-of-cost OOS. Next session MUST pursue a **structurally different, pre-stated** hypothesis on the **same real cached data only** (no new feeds). Choose ONE heavy path and execute it fully:
- **Path A (recommended):** Causal **residual momentum / idiosyncratic return** (regress each asset on EW market factor using trailing IS window only; trade residual signal) — genuinely different from raw cross-sectional rank and from spread MR. State residual construction, WF, costs, benchmark.
- **Path B:** **Lead-lag / cross-asset information diffusion** with strict causal lag (train-only lag selection or fixed rolling-train-only) — fully pre-stated, no lookahead.
- **Path C:** If you can justify no remaining structurally distinct spot-only hypothesis on this window, produce a **fail-closed "spot universe exhausted" memo** as `reports/spot_universe_exhausted_memo_<UTC>.json` mapping each tested family with evidence, plus concrete **real-feed acquisition checklist** (schemas/provenance). Still produce 2 other concrete artifacts (refined feed status + registry supersede). No evasion via memo-only.

### Required artifacts (>=3)
1. `reports/<family>_costed_oos_<UTC>.json` (real data, fail-closed flags, WF 720/168/168, cost grid 0/5/10/20 bps combos, IS/OOS, benchmark, BTC/ETH/SOL/BNB+aggregate, pre-stated `oos_edge_proven` rule, structural novelty stated) **OR** `reports/spot_universe_exhausted_memo_<UTC>.json` under Path C.
2. `reports/real_feed_unblock_status_<UTC>.json` (honest re-check; no fabrication).
3. `reports/strategy_edge_registry_<UTC>.json` with `supersedes: "reports/strategy_edge_registry_20261105T095736Z.json"` and rerun test counts.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T095736Z.json` (LATEST P9 — supersede)
- `reports/spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json` (P9, oos_edge_proven=false)
- `reports/real_feed_unblock_status_20261105T095713Z.json` (P9)
- `reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json` (P7)
- `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json` (P6)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (165/165 PASS, pairs BLOCKED)

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session.
- **No edge claim:** `oos_edge_proven=true` requires all cost-grid slices OOS net>0 AND beating benchmark on same WF windows AND exposure>0 (pre-stated).
- **No weakening:** Never weaken enriched gates or fail-closed flags.
- **Heavy work mandatory:** >=3 new artifacts. Structural novelty required (not param tweaks).
- **Honesty:** `oos_edge_proven=false` is valid.

## COMPLETION CHECK
- [ ] Deliverable 1 exists (new family costed OOS or Path C memo) with real-data/fail-closed flags + novelty/justification
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest)
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261105T095736Z.json` with test counts
- [ ] `oos_edge_proven` claimed only if pre-stated rule satisfied. No fabrication/proxies/threshold weakening.
- [ ] >= 3 new artifacts in `reports/`

**START NOW. No status summary first. Produce the heavy analysis artifact first.**
