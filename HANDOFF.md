# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T09:51:17Z (Enforced by next session)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## INITIAL TASK MESSAGE (EXECUTE FIRST - NO DELAY)
**PRIORITY 9 / CAMPAIGN #5 — MANDATORY.** The next agent MUST not do investigation-only work. You must produce **>= 3 new concrete artifacts in `reports/`** this session. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

## BOTTLENECKS (REMOVED - BINDING)
- **Tests:** `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` → **832 passed, 1 skipped, 0 failed** (verified 2026-11-05T09:50Z). Warnings non-blocking.
- **Real spot cache:** `data/cache/*_2026-04-01_2026-10-30_1h.pkl` + `.meta.json` — 11 assets (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP), 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot klines. **Use as-is. Do not re-fetch.**
- **Pairs:** **PROVEN BLOCKED** (165/165, 0 breaches). No re-scan. No gate weakening.
- **Feeds:** Cross-exchange dual-venue, funding/basis/carry, term-structure/real IV-vol surface remain `blocked_no_real_feed`. No fabricated feeds. Verified no new real feeds with provenance as of 2026-11-05T09:50:08Z.
- **CI/archaeology:** Not a local research blocker. Do not spend time here.

## CORE TRUTH (SETTLED)
- **Pairs cointegration:** PROVEN BLOCKED (fail-closed).
- **No proven net-of-cost OOS edge** on real cached spot 1h (11 assets, 5112 bars), rolling WF (train 720 / test 168 / step 168), cost grid {0,5,10,20}bps:
  - momentum (0/11): `reports/momentum_mr_costed_oos_20261105T081323Z.json`
  - mean_reversion (0/11): same
  - cross_sectional_risk_adjusted_return_rank (`oos_edge_proven=false`): `reports/spot_alt_signal_costed_oos_20261105T084619Z.json`
  - donchian_breakout_volfilter (`oos_edge_proven=false`, 0/11): `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json` (P6)
  - range_breakout_reversion_volband (`oos_edge_proven=false`, 0/11): `reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json` (P7)
- **Latest registry:** `reports/strategy_edge_registry_20261105T095008Z.json` (P7) — **MUST be superseded by P9**.

## CAMPAIGN #5 (BINDING — CANNOT BE AVOIDED)
**Repo-name priority:** On `cryptoquantstatarbstrats`, the highest ROI for finding any real edge is **pairwise spread/cointegration-adjacent mean-reversion on the SAME 11-asset spot set with regime-adaptive, fail-closed construction**. Prior families failed. You must do something **structurally different**.

### Deliverable A (HEAVY, REQUIRED) — `reports/spot_zscore_regime_mean_reversion_costed_oos_<UTC>.json`
Implement and run a **new, pre-stated family** genuinely different from P4-P7:
- **Concept:** Regime-adaptive z-score mean-reversion on rolling spreads/pairs constructed from the **same 11-asset universe** (use existing pair logic only to inform, but do NOT re-run full pairs audit; you may test top hypotheses from `reports/pairs_failclosed_audit_20261105T075431Z.json` but must not weaken gates).
- **Structural difference required:** Must differ from pure cross-sectional rank (P5) and from breakout families (P6/P7). Explicitly state what makes it different in `methodology`/`notes`.
- **Data:** Only `data/cache/*_2026-04-01_2026-10-30_1h.pkl`. No new external feeds.
- **Rigor (fail-closed):**
  - Cost grid >= {0,5,10,20} bps combos
  - Rolling WF: train 720 / test 168 / step 168 (explicit)
  - IS/OOS split, benchmark stated (B&H per asset or EW, consistent)
  - Exposure/trade counts, per-asset (BTC,ETH,SOL,BNB) + aggregate over 11
  - Pre-stated `oos_edge_proven` rule
- **Flags:** `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false`
- **No tuning in-sample to manufacture edge.** `oos_edge_proven=false` is valid.

### Deliverable B (REQUIRED) — `reports/real_feed_unblock_status_<UTC>.json`
Re-check `data/cache/` and repo for **any newly added real feeds** with provenance (funding/basis/spot-perp/dual-venue/real IV).
- If **none:** produce honest status citing `reports/real_feed_inventory_20261105T084255Z.json`, `reports/real_feed_unblock_plan_20261105T084447Z.json`, `reports/real_feed_unblock_status_20261105T095008Z.json`. List required schemas still missing.
- If **present:** ingest only with provenance, run smallest fail-closed validation, emit `reports/<family>_real_validation_<UTC>.json`. **Never fabricate.**

### Deliverable C (REQUIRED) — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with A (+B if any). Keep blocked families honest. Rerun full tests with exact command and env note, record counts. Set `supersedes: "reports/strategy_edge_registry_20261105T095008Z.json"`.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T095008Z.json` (LATEST P7 — supersede in P9)
- `reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json` (P7, oos_edge_proven=false)
- `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json` (P6)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B)
- `reports/real_feed_unblock_status_20261105T095008Z.json` (P7B)
- `reports/real_feed_inventory_20261105T084255Z.json`, `reports/real_feed_unblock_plan_20261105T084447Z.json`
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (165/165 PASS)

## ANTI-EVASION (ENFORCED)
- **No escape:** Pairs/feed re-scans are forbidden unless a genuinely new real dataset + new fail-closed audit artifact is added this session.
- **No edge claim:** `oos_edge_proven=true` requires all cost-grid slices OOS net>0 AND beating benchmark on same WF windows AND exposure>0 (all pre-stated).
- **No weakening:** Never weaken `use_enriched_gates=True, strict_enriched_gates=True`, `real_data_only=true`, `fabricated_data=false`, `no_threshold_weakening=true`.
- **Heavy work mandatory:** >=3 new artifacts. Every session must leave concrete artifacts.
- **Structural novelty:** Deliverable A must be genuinely different from P4-P7 (not param tweaks).

## COMPLETION CHECK (SELF-AUDIT BEFORE ENDING)
- [ ] `reports/spot_zscore_regime_mean_reversion_costed_oos_<UTC>.json` exists with real-data/fail-closed flags, cost grid+WF+benchmark, structurally distinct from P6/P7
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest or with real validation if feeds added)
- [ ] `reports/strategy_edge_registry_<UTC>.json` exists with `supersedes: "reports/strategy_edge_registry_20261105T095008Z.json"` and test counts recorded
- [ ] `oos_edge_proven` claimed only if pre-stated rule satisfied. No fabrication/proxies/threshold weakening.
- [ ] >= 3 new artifacts total in `reports/`

**START NOW. No status summary first. Produce Deliverable A first with heavy computation.**
