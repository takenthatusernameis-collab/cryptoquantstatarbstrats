# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T10:45:00Z (P12/Campaign #8 Path C completed; handoff re-stamped for next session)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## P12/CAMPAIGN #8 COMPLETION (THIS SESSION — 3 ARTIFACTS, Path C)
- **A (heavy):** `reports/spot_universe_exhausted_memo_20261105T104319Z.json` — fail-closed exhaustion memo. Enumerates tested families (P4-P11, 8 structurally distinct) + artifacts; rules out remaining pre-stated micro-hypotheses on same cached spot (sizing/regime overlays = not new structure; intrabar/microstructure, funding-basis, dual-venue, real IV/vol surface, on-chain/alt, sub-hour resampling = `blocked_no_real_feed`/not cached). Conclusion: **EXHAUSTED** on 11-asset 2026-04-01..2026-10-30 1h Binance spot cache (5112 bars) under pre-stated WF 720/168/168, cost grid 0/5/10/20 bps, B&H benchmark. `oos_edge_proven=false`. Includes concrete **real-feed acquisition checklist** (funding/basis, dual-venue, real IV/vol surface) with provenance/validation requirements. Flags: `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false`.
- **B:** `reports/real_feed_unblock_status_20261105T104319Z.json` — honest re-check; **no new real feeds with provenance**. `cross_exchange_dual_venue_same_asset|funding_basis_carry|term_structure_real_iv_vol_surface|intrabar_microstructure=blocked_no_real_feed`. Pairs PROVEN BLOCKED (no re-scan). Spot-only cached 1h = EXHAUSTED.
- **C:** `reports/strategy_edge_registry_20261105T104319Z.json` — supersedes `reports/strategy_edge_registry_20261105T104010Z.json`. Rerun tests: **832 passed, 1 skipped, 0 failed, 3561 warnings, 40.30s** (`PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q`, rc=0).

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 13 / CAMPAIGN #9 — MANDATORY.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
- **Tests (P12):** 832 passed, 1 skipped, 0 failed. Re-run and record in new registry.
- **Real spot cache:** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` — 11 assets (`ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP`), 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot. **Use as-is. Do not re-fetch.**
- **Pairs:** PROVEN BLOCKED (165/165). No re-scan. No gate weakening.
- **Spot-only 1h families:** **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge on real cached data. Memo: `reports/spot_universe_exhausted_memo_20261105T104319Z.json`.
- **Feeds:** `dual-venue|funding-basis-carry|real-IV/vol-surface|intrabar-microstructure = blocked_no_real_feed`. No fabricated feeds.

### Core truth
No proven net-of-cost OOS edge on real cached spot 1h (WF 720/168/168, cost grid 0/5/10/20 bps combos, B&H benchmark). No real non-spot feeds with provenance are present.

## CAMPAIGN #9 (BINDING — CANNOT BE AVOIDED)
**Path R is the only productive path.** Follow it if you can ingest a genuinely new real feed with provenance in-session. If not, follow Path C-maintain (heavy, honest) — do **not** churn or create fake work.

### Path R (required if new real feed with provenance is ingested this session)
Produce **>=3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry, fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<new_feed>*.{pkl,json|meta.json}` or equivalent **immutable provenance** recorded in-repo (source, retrieval, timestamps, symbol map, schema, checksum/hash). **No provenance = do not claim ingestion; treat as Path C-maintain.**
3. `reports/real_feed_unblock_status_<UTC>.json` + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T104319Z.json`, rerun tests).

Candidate families (only with real provenance): `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure` (if real tick/trade/book obtained). Use acquisition checklist in `spot_universe_exhausted_memo_20261105T104319Z.json`.

### Path C-maintain (only if NO new real feed with provenance ingested)
Do **not** produce another exhaustion memo that repeats the same facts. Produce **>=3 concrete artifacts** that advance real-feed unblock readiness without fabrication:
1. `reports/real_feed_ingestion_readiness_<UTC>.json` — concrete, executable readiness spec: for each candidate feed (funding/basis, dual-venue, real IV/vol), list exact target schemas/fields, validation checks, fail-closed loader requirements, cost/carry model inputs, provenance metadata schema, and a **step-by-step ingestion runbook** a human/operator can execute to place verifiable files into `data/cache/` (include expected filenames/meta keys). Must be specific enough to execute; no vague advice.
2. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check (still blocked; no new provenance found).
3. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T104319Z.json`, rerun tests, restates exhausted/blocked truth.

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` (and provenance files in `data/cache/` if Path R).
- **Honesty:** `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.

## COMPLETION CHECK
- [ ] Path R: `*_costed_oos_<UTC>.json` + real provenance in `data/cache/` + status + registry supersede; OR Path C-maintain: `real_feed_ingestion_readiness_<UTC>.json` + status + registry supersede
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T104319Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache
- [ ] >= 3 new artifacts in `reports/`

**START NOW. No status summary first. Produce the heavy analysis/spec artifact first.**