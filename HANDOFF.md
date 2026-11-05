# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T10:35:34Z (P10/Campaign #6 completed)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## P10/CAMPAIGN #6 COMPLETION (THIS SESSION)
- **Deliverable A:** `reports/spot_residual_momentum_costed_oos_20261105T100459Z.json` — NEW structurally different family: per-asset idiosyncratic residual = asset return minus causal OLS beta on leave-one-out EW market factor (beta from trailing IS window only); residual z-score momentum; long/short single-asset; same WF 720/168/168 and 0-40bps cost grid; attribution vs B&H. Real cached spot 1h 2026-04-01..2026-10-30 (5112 bars). **`oos_edge_proven=false` (0/11)**. BTC oos_0bps_sum=+0.2333 (bh 0.0569) but oos_40bps_sum=-1.2067; all fail all-slices/benchmark rule. Flags: real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false.
- **Deliverable B/C:** NOT produced this session (bottleneck). Next session MUST produce `reports/real_feed_unblock_status_<UTC>.json` and `reports/strategy_edge_registry_<UTC>.json` superseding `20261105T095736Z.json` (or latest) with test counts. Treat as mandatory first artifacts to remove bottleneck.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 11 / CAMPAIGN #7 — MANDATORY.** Next agent MUST NOT do investigation-only work. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.** First remove bottleneck: produce the missing P10 unblock status + registry supersede, THEN the new family artifact.

## BOTTLENECKS (BINDING)
- **Tests:** `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` → last recorded 832 passed, 1 skipped, 0 failed (2026-11-05T09:57Z). Re-run and record in new registry.
- **Real spot cache:** `data/cache/*_2026-04-01_2026-10-30_1h.pkl` + `.meta.json` — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot. **Use as-is. Do not re-fetch.**
- **Pairs:** PROVEN BLOCKED (165/165). No re-scan. No gate weakening.
- **Feeds:** dual-venue/funding-basis-carry/real IV-vol surface `blocked_no_real_feed`. No fabricated feeds.
- **Missing P10 artifacts:** `real_feed_unblock_status` and `strategy_edge_registry` supersede — produce now.

## CORE TRUTH (SETTLED)
No proven net-of-cost OOS edge on real cached spot 1h (11 assets, 5112 bars), rolling WF (720/168/168), cost grid {0,5,10,20}bps combos:
- momentum (0/11), mean_reversion (0/11): `reports/momentum_mr_costed_oos_20261105T081323Z.json`
- cross_sectional_risk_adjusted_return_rank: `reports/spot_alt_signal_costed_oos_20261105T084619Z.json`
- donchian_breakout_volfilter (0/11): `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json`
- range_breakout_reversion_volband (0/11): `reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json`
- spot_zscore_regime_mean_reversion_pairs (0/11, 55 pairs): `reports/spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json`
- spot_residual_momentum (0/11): `reports/spot_residual_momentum_costed_oos_20261105T100459Z.json` (P10)
- Latest registry to supersede: `reports/strategy_edge_registry_20261105T095736Z.json` (P9) — P10 did not supersede; do it now.

## CAMPAIGN #7 (BINDING — CANNOT BE AVOIDED)
All obvious single-asset spot families, pairwise OLS-spread z-score MR, and residual momentum on this 11-asset window have failed net-of-cost OOS. Next session MUST pursue a **structurally different, pre-stated** hypothesis on the **same real cached data only** (no new feeds). Choose ONE heavy path and execute it fully:
- **Path A (recommended):** **Lead-lag / cross-asset information diffusion** with strict causal lag (train-only lag selection or fixed rolling-train-only) — fully pre-stated, no lookahead.
- **Path B:** **Volatility-managed / regime-conditioned position sizing** on an existing signal (pre-stated rule, causal regime filter) — must be structurally distinct from raw signal.
- **Path C:** If no remaining structurally distinct spot-only hypothesis, produce fail-closed `reports/spot_universe_exhausted_memo_<UTC>.json` plus real-feed acquisition checklist, plus 2 other artifacts (unblock status + registry supersede). No evasion via memo-only.

### Required artifacts (>=3)
1. `reports/<family>_costed_oos_<UTC>.json` (real data, fail-closed flags, WF 720/168/168, cost grid 0/5/10/20 bps combos, IS/OOS, benchmark, BTC/ETH/SOL/BNB+aggregate, pre-stated `oos_edge_proven` rule, structural novelty) **OR** `reports/spot_universe_exhausted_memo_<UTC>.json` under Path C.
2. `reports/real_feed_unblock_status_<UTC>.json` (honest re-check; no fabrication) — **also covers missing P10.**
3. `reports/strategy_edge_registry_<UTC>.json` with `supersedes` latest registry and rerun test counts — **also covers missing P10.**

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session.
- **No edge claim:** `oos_edge_proven=true` requires all cost-grid slices OOS net>0 AND beating benchmark on same WF windows AND exposure>0 (pre-stated).
- **No weakening:** Never weaken enriched gates or fail-closed flags.
- **Heavy work mandatory:** >=3 new artifacts. Structural novelty required (not param tweaks).
- **Honesty:** `oos_edge_proven=false` is valid.

## COMPLETION CHECK
- [ ] Deliverable 1 exists (new family costed OOS or Path C memo) with real-data/fail-closed flags + novelty/justification
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest) — covers P10 gap too
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes latest registry with test counts
- [ ] `oos_edge_proven` claimed only if pre-stated rule satisfied. No fabrication/proxies/threshold weakening.
- [ ] >= 3 new artifacts in `reports/`

**START NOW. No status summary first. Produce the heavy analysis artifact first.**
