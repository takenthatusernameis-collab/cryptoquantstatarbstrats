# HANDOFF (SINGLE DURABLE) — READ THIS FIRST — 2026-11-05T08:51:05Z

## READ THIS FIRST / DO THIS NOW (NO REHASH, NO INVESTIGATION-ONLY)
**You are the next session. Execute PRIORITY 6 below immediately.** This repo is `cryptoquantstatarbstrats` (crypto quant stat-arb strategies): the only acceptable progress is **heavy, fail-closed, real-data work that leaves artifacts**. **Every session leaves >=2 new concrete artifacts in `reports/`. This session requires A+B+C (>=3).** Real data only. Never fabricate. No threshold weakening. No proxies labeled as real feeds. Do not re-litigate pairs. Commit nothing unless explicitly asked.

**Bottlenecks removed (binding):**
- **Test env:** deps are at `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`, pytest at `/home/runner/work/_temp/kilo-home/.local/bin/pytest`. Run: `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` (baseline **832 passed, 1 skipped, 0 failed** full `tests/`).
- **Pairs = PROVEN BLOCKED (165/165, 0 breaches).** Do NOT re-scan/re-audit pairs and do NOT weaken gates unless a genuinely NEW real dataset is added.
- **Blocked feed families stay honest:** cross-exchange dual-venue same-asset, funding/basis/carry, term_structure/real IV-vol surface = `blocked_no_real_feed` until genuinely new real feed files with provenance exist. No fabricated candles/IV/funding/basis/dual-venue feeds.
- **No in-sample tuning to manufacture edge.** `oos_edge_proven=false` is a valid, required fail-closed outcome.

## CORE TRUTH (DO NOT RE-LITIGATE)
- **Pairs cointegration: PROVEN BLOCKED** (fail-closed). Do not touch unless NEW real dataset.
- **Momentum (0/11), mean_reversion (0/11), cross_sectional_risk_adjusted_return_rank (`oos_edge_proven=false`): NO PROVEN NET-OF-COST OOS EDGE** on real cached spot 1h 2026-04-01..2026-10-30 (11 assets, 5112 bars; rolling 30d/7d, 0–40bps, vs stated benchmarks). Do not claim edge.
- Real spot cache (ONLY real feed now): `data/cache/*_2026-04-01_2026-10-30_1h.pkl` — 11 assets (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP), 5112 bars, Binance spot klines via `www.binance.com` (per `reports/real_feed_inventory_20261105T084255Z.json`).

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (HEAVY, BINDING) — PRIORITY 6
**PRIORITY 6 — HEAVY REAL-DATA CAMPAIGN #2 (NO REHASH) + FEED UNBLOCK EXECUTION (IF REAL DATA PROVIDED).** Produce **A + B + C (>=3 artifacts in `reports/`)**.

### Required Deliverable A — `reports/spot_breakout_volfilter_costed_oos_<UTC>.json` (HEAVY, REAL SPOT ONLY, GENUINELY DIFFERENT)
Execute a **new, pre-stated** real-spot signal family **different** from momentum/mean_reversion/cross-sectional rank: e.g. **Donchian/channel breakout with a volatility-regime filter** (enter on N-bar high/low breakout only when realized vol in a specified band; exit on channel mid or stop; long/short or long-flat — state choice) **OR** an equally distinct, pre-specified variant. Use **only real cached 1h** (`data/cache/*_2026-04-01_2026-10-30_1h.pkl`, 11 assets, 5112 bars). **No new external feeds, no gate weakening, no proxies as new feed types.**
- Rigor: cost grid (>= {0,5,10,20} bps combos), rolling WF (explicit train/test/step, e.g. 720/168), IS/OOS, benchmark (asset B&H and/or EW B&H as appropriate — state), exposure/trade counts, **pre-stated `oos_edge_proven` rule**, per-asset (BTC,ETH,SOL,BNB) + aggregate over 11.
- `oos_edge_proven=false` is a valid, required fail-closed outcome — report honestly. **Do not tune parameters in-sample to manufacture edge.** Set `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true`.

### Required Deliverable B — `reports/real_feed_unblock_status_<UTC>.json` (+ ingest artifacts ONLY if real feeds added)
1) Re-check `data/cache`/repo for **any newly added real feeds** (funding, basis/spot-perp, dual-venue, real IV). If **none added**: produce an honest status artifact confirming still `blocked_no_real_feed` per family, referencing `reports/real_feed_inventory_20261105T084255Z.json` + `reports/real_feed_unblock_plan_20261105T084447Z.json` and the exact schemas still required.
2) **If and only if genuinely new real feed files are present with provenance**: ingest and run the **smallest fail-closed validation** for that family (net-of-cost/fees stated; no fabrication), producing `reports/<family>_real_validation_<UTC>.json`. **Do not fake feeds.**

### Required Deliverable C — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with Deliverable A (+ B validation if any). Keep blocked families honest/unchanged unless NEW real feed evidence is added. Rerun full `tests/` (exact command + env note) and record counts. **`supersedes: "reports/strategy_edge_registry_20261105T084647Z.json"`**.

## KEY ARTIFACTS (CANONICAL, DO NOT REDO)
- `reports/strategy_edge_registry_20261105T084647Z.json` (LATEST consolidated; supersede in P6)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B, `oos_edge_proven=false`)
- `reports/real_feed_inventory_20261105T084255Z.json` (P5A1)
- `reports/real_feed_unblock_plan_20261105T084447Z.json` (P5A2)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4, 0/11 & 0/11)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS fail-closed)
- `reports/funding_basis_blocked_20261105T075839Z.json`
- `reports/cross_exchange_real_market.json` (dual-venue blocked / single-venue only)
- `reports/portfolio_real.json`
