# HANDOFF (SINGLE DURABLE) — READ THIS FIRST — 2026-11-05T09:38:21Z

## READ THIS FIRST / DO THIS NOW (NO REHASH, NO INVESTIGATION-ONLY)
**You are the next session. Execute INITIAL TASK MESSAGE / PRIORITY 7 below immediately.** Repo `cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. Repo-name inference: the core mission is statistical-arbitrage edge research on crypto, on **real data only**, fail-closed, leaving **heavy artifacts**. Only acceptable progress: **heavy, fail-closed, real-data work that leaves artifacts**. **Every session leaves >=2 new concrete artifacts in `reports/`.** Real data only. Never fabricate. No threshold weakening. No proxies labeled as real feeds. Do not re-litigate pairs. Commit nothing unless explicitly asked.

## Bottlenecks removed (binding; verified this session)
- **Test env:** deps at `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`, pytest at `/home/runner/work/_temp/kilo-home/.local/bin/pytest`. Run: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` (**832 passed, 1 skipped, 0 failed**, full `tests/`, ~40s). Env is NOT a blocker.
- **Pairs = PROVEN BLOCKED (165/165, 0 breaches).** Do NOT re-scan/re-audit pairs; do NOT weaken gates unless genuinely NEW real dataset added.
- **Blocked feed families stay honest:** cross-exchange dual-venue same-asset, funding/basis/carry, term_structure/real IV-vol surface = `blocked_no_real_feed` until genuinely new real feed files with provenance exist. No fabricated candles/IV/funding/basis/dual-venue feeds.
- **No in-sample tuning to manufacture edge.** `oos_edge_proven=false` is valid/required fail-closed.

## CORE TRUTH (DO NOT RE-LITIGATE)
- **Pairs cointegration: PROVEN BLOCKED** (fail-closed).
- **Momentum (0/11), mean_reversion (0/11), cross_sectional_risk_adjusted_return_rank (oos_edge_proven=false), donchian_breakout_volfilter (oos_edge_proven=false): NO PROVEN NET-OF-COST OOS EDGE** on real cached spot 1h 2026-04-01..2026-10-30 (11 assets, 5112 bars). Do not claim edge.
- Real spot cache only real feed now: `data/cache/*_2026-04-01_2026-10-30_1h.pkl` (11 assets).

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (HEAVY, BINDING) — PRIORITY 7 / CAMPAIGN #3
**PRIORITY 7 — HEAVY REAL-DATA CAMPAIGN #3 (NO REHASH) + FEED UNBLOCK EXECUTION (IF REAL DATA PROVIDED). Produce A + B + C (>=3 artifacts in `reports/`).** Repo-name priority: stat-arb edge on real spot is the only open, unproven family; this campaign is the required focus. A future session may not skip to pairs/feeds without new real data; it must execute Campaign #3 first.

### Required Deliverable A — `reports/spot_range_breakout_reversion_volband_costed_oos_<UTC>.json` (HEAVY, REAL SPOT ONLY, GENUINELY DIFFERENT)
Execute a **new, pre-stated** real-spot family different from all prior (momentum/mean-reversion/cross-sectional rank/Donchian+volfilter). **Range-bound breakout-reversion:** define range by Bollinger/ATR or local range; enter breakout only in a specific vol band OR fade failed breakout; long/short or long-flat — state explicitly. Use only `data/cache/*_2026-04-01_2026-10-30_1h.pkl` (11 assets). No new external feeds, no proxies, no gate weakening.
- Rigor: cost grid >= {0,5,10,20} bps combos, rolling WF (train/test/step explicit), IS/OOS, benchmark stated, exposure/trade counts, pre-stated `oos_edge_proven` rule, per-asset (BTC,ETH,SOL,BNB)+aggregate over 11.
- `oos_edge_proven=false` valid/required fail-closed. Do not tune in-sample. Set `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true`.

### Required Deliverable B — `reports/real_feed_unblock_status_<UTC>.json` (+ ingest artifacts ONLY if real feeds added)
1) Re-check `data/cache/` and repo for **any newly added real feeds** (funding, basis/spot-perp, dual-venue, real IV). If none: produce honest status confirming still `blocked_no_real_feed` per family, referencing `reports/real_feed_inventory_20261105T084255Z.json`, `reports/real_feed_unblock_plan_20261105T084447Z.json`, and exact schemas still required.
2) **If and only if genuinely new real feed files are present with provenance**: ingest and run smallest fail-closed validation for that family (net-of-cost/fees stated; no fabrication), producing `reports/<family>_real_validation_<UTC>.json`. Do not fake feeds.

### Required Deliverable C — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with Deliverable A (+ B validation if any). Keep blocked families honest/unchanged unless NEW real feed evidence added. Rerun full `tests/` with exact command + env note and record counts. **`supersedes: "reports/strategy_edge_registry_20261105T093702Z.json"`**.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T093702Z.json` (LATEST; supersede in P7)
- `reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json` (P6A, oos_edge_proven=false)
- `reports/real_feed_unblock_status_20261105T093642Z.json` (P6B)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B)
- `reports/real_feed_inventory_20261105T084255Z.json` (P5A1)
- `reports/real_feed_unblock_plan_20261105T084447Z.json` (P5A2)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS fail-closed)

## ANTI-EVASION (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
- Do not substitute pairs/feed re-scans for Campaign #3 without a genuinely new real dataset + new fail-closed audit artifact.
- Do not claim `oos_edge_proven=true` without all cost-grid slices OOS net > 0 AND beating benchmark on same WF windows AND exposure > 0.
- Do not weaken `use_enriched_gates=True, strict_enriched_gates=True`, `real_data_only=true`, `fabricated_data=false`, `no_threshold_weakening=true`.
- Every session leaves >=2 new concrete artifacts in `reports/`; zero-artifact sessions are not acceptable.
