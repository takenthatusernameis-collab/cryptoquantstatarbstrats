# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T09:45:43Z**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.** Mission: find/validate statistical-arbitrage edge on **real crypto data only**, fail-closed, with **heavy reproducible artifacts**. This file is the **only** durable handoff. Read it first; execute it; do not re-litigate settled facts.

## READ THIS FIRST / DO THIS NOW (NO REHASH, NO INVESTIGATION-ONLY)
**Execute PRIORITY 7 / CAMPAIGN #3 immediately.** Only acceptable progress is **heavy, fail-closed, real-data work that leaves artifacts**. **This session MUST leave >= 3 new concrete artifacts in `reports/`** (A, B, C below). Real data only. Never fabricate. No threshold weakening. No proxies labeled as real feeds. No in-sample tuning to manufacture edge. `oos_edge_proven=false` is valid/required fail-closed. **Zero-artifact, investigation-only, or "summarize status" sessions are failures.** Commit nothing unless explicitly asked.

## BOTTLENECKS REMOVED (BINDING; VERIFIED 2026-11-05T09:45Z)
- **Test env OK (not a blocker):** deps `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`, pytest `/home/runner/work/_temp/kilo-home/.local/bin/pytest` (9.2.0). Run: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` → **832 passed, 1 skipped, 0 failed** (`tests/`, ~40s, verified this session). Warnings present but non-failing.
- **Real spot cache VALID (use as-is):** `data/cache/*_2026-04-01_2026-10-30_1h.pkl` — 11 assets (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP), 5112 bars each, 2026-04-01..2026-10-30 1h, source `www.binance.com` public spot klines, `real_data_only=true, fabricated_data=false`. `data/cache/summary.json` present/all ok. **Do not re-fetch.**
- **Pairs = PROVEN BLOCKED (165/165, 0 breaches).** Do **NOT** re-scan/re-audit pairs; do **NOT** weaken gates unless a **genuinely NEW real dataset** is added + a new fail-closed audit artifact is produced.
- **Blocked feed families (honest, still blocked):** cross-exchange dual-venue same-asset, funding/basis/carry, term_structure/real IV-vol surface = `blocked_no_real_feed` until genuinely new real feed files with provenance exist. **No fabricated candles/IV/funding/basis/dual-venue feeds.**
- **Workflow/CI noise is NOT a local research blocker:** `research_state/workflow_run_diagnostics.jsonl` shows historical CI agent-loop failures. Do not spend the session on CI archaeology.

## CORE TRUTH (DO NOT RE-LITIGATE)
- **Pairs cointegration: PROVEN BLOCKED** (fail-closed).
- **No proven net-of-cost OOS edge** on real cached spot 1h 2026-04-01..2026-10-30 (11 assets, 5112 bars): momentum (0/11), mean_reversion (0/11), cross_sectional_risk_adjusted_return_rank (`oos_edge_proven=false`), donchian_breakout_volfilter (`oos_edge_proven=false`, P6 `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json`). **Do not claim edge.**
- Latest registry: `reports/strategy_edge_registry_20261105T093702Z.json` (P6). **P7 MUST supersede it.**

## CAMPAIGN #3 (BINDING FOCUS — FUTURE AGENTS MAY NOT AVOID HEAVY WORK)
**Repo-name priority:** stat-arb edge on real spot is the only open, unproven family executable **now** with available real data. **You must execute Campaign #3 first.** You may not substitute pairs/feed re-scans, status summaries, refactors, or CI archaeology for Campaign #3. Only escape hatch: a **genuinely NEW real dataset/feed with provenance** is added to the repo *in this session* — then still produce Deliverable B validation artifacts for it AND complete A+C.

### Deliverable A (HEAVY, REQUIRED) — `reports/spot_range_breakout_reversion_volband_costed_oos_<UTC>.json`
Implement and run a **new, pre-stated** real-spot family **genuinely different from all prior** (momentum, mean-reversion, cross-sectional rank, Donchian breakout+volfilter). **Required concept:** *range-bound breakout-reversion with a volatility band* — define range (Bollinger/ATR or local rolling range), enter breakout **only** in a specific vol band **OR** fade a failed breakout (reversion leg). State rules explicitly (long/short or long-flat). **Data:** only `data/cache/*_2026-04-01_2026-10-30_1h.pkl` (11 assets). No new external feeds, no proxies, no gate weakening.
- **Rigor (pre-stated, fail-closed):** cost grid >= {0,5,10,20} bps combos; rolling walk-forward (train/test/step explicit); IS/OOS; benchmark stated (e.g., buy-and-hold or equal-weight); exposure/trade counts; pre-stated `oos_edge_proven` rule; per-asset (BTC,ETH,SOL,BNB) + aggregate over 11.
- `oos_edge_proven=false` valid/required fail-closed. **Do not tune in-sample.** Set `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false`.
- **Rejected/evasion:** re-labeling P6 Donchian volfilter as “range breakout-reversion”.

### Deliverable B (REQUIRED) — `reports/real_feed_unblock_status_<UTC>.json` (+ ingest/validation artifacts ONLY if real feeds added)
1) Re-check `data/cache/` and repo for **any newly added real feeds** (funding, basis/spot-perp, dual-venue, real IV). If none: produce **honest** status confirming still `blocked_no_real_feed` per family, referencing `reports/real_feed_inventory_20261105T084255Z.json`, `reports/real_feed_unblock_plan_20261105T084447Z.json`, `reports/real_feed_unblock_status_20261105T093642Z.json`, and exact schemas still required.
2) **If and only if genuinely new real feed files with provenance are present:** ingest and run the smallest fail-closed validation for that family (net-of-cost/fees stated; no fabrication), producing `reports/<family>_real_validation_<UTC>.json`. **Do not fake feeds.**

### Deliverable C (REQUIRED) — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with Deliverable A (+ B validation if any). Keep blocked families honest/unchanged unless NEW real feed evidence added. Rerun full `tests/` with exact command + env note and record counts. Set **`supersedes: "reports/strategy_edge_registry_20261105T093702Z.json"`**.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T093702Z.json` (LATEST; supersede in P7)
- `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json` (P6A Donchian volfilter, `oos_edge_proven=false` — **NOT** Deliverable A)
- `reports/real_feed_unblock_status_20261105T093642Z.json` (P6B)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B)
- `reports/real_feed_inventory_20261105T084255Z.json` (P5A1), `reports/real_feed_unblock_plan_20261105T084447Z.json` (P5A2)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS fail-closed)

## ANTI-EVASION (ENFORCED)
- No pairs/feed re-scans for Campaign #3 without a genuinely new real dataset + new fail-closed audit artifact.
- No `oos_edge_proven=true` without: all cost-grid slices OOS net > 0 **AND** beating benchmark on same WF windows **AND** exposure > 0 (all pre-stated).
- Never weaken `use_enriched_gates=True, strict_enriched_gates=True`, `real_data_only=true`, `fabricated_data=false`, `no_threshold_weakening=true`.
- Every session leaves >=2 (P7 requires >=3) new concrete artifacts in `reports/`.
- Deliverable A must be genuinely different from P6 Donchian breakout volfilter.

## COMPLETION CHECK (self-audit before ending session)
- [ ] `reports/spot_range_breakout_reversion_volband_costed_oos_<UTC>.json` exists, real-data/fail-closed flags set, cost grid+WF+benchmark present.
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest or with real validation if feeds added).
- [ ] `reports/strategy_edge_registry_<UTC>.json` exists with `supersedes` set and test counts recorded.
- [ ] `oos_edge_proven` claimed only if pre-stated rule satisfied (likely false). No fabrication/proxies/threshold weakening.
