# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T11:45:12Z (Campaign #12 complete, Path C-maintain; handoff re-stamped for next agentic session. No new real feed found.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## CAMPAIGN #12 STATUS (COMPLETE — Path C-maintain)
No new real feed with provenance was found/ingested (honest re-scan of `data/cache/*`), so Path R did not trigger. Path C-maintain executed with tested code + artifacts.
- Tests: **877 passed, 1 skipped, 0 failed** (`pytest tests/ -q`, rc=0, 40.26s). Loader tests `tests/test_real_feed_loader_validation.py`: **45 passed** (15 added for `term_structure_real_iv_vol_surface`).
- New/updated code (Campaign #12): `data/real_feed_loader.py` adds fail-closed `TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC` + realized/historical-vol-proxy-as-IV refusals, registered in `FAMILY_SPECS`. `tests/test_real_feed_loader_validation.py` adds 15 targeted tests (synthetic fixtures only, never labeled real).
- Campaign #12 artifacts: `reports/term_structure_real_iv_vol_surface_loader_validation_20261105T114512Z.json`, `reports/real_feed_unblock_status_20261105T114512Z.json`, `reports/strategy_edge_registry_20261105T114512Z.json` (supersedes `20261105T105940Z`).
- Real spot cache (reuse as-is, do not re-fetch): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot.
- Pairs: PROVEN BLOCKED (165/165). No re-scan. No gate weakening.
- Spot-only 1h families: **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge.
- Feeds: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed` (no provenance found). No fabricated feeds/proxies.
- Fail-closed loader `data/real_feed_loader.py` has specs+tests for: `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`. **Missing spec:** `intrabar_microstructure`. Readiness spec: `reports/real_feed_ingestion_readiness_20261105T104640Z.json`.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 16 / CAMPAIGN #13 — MANDATORY.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
See Campaign #12 status above. `oos_edge_proven=false` across the board. No real non-spot feeds with provenance are present. Spot 1h is exhausted. Fail-closed ingestion infrastructure exists for `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface` and must be extended for `intrabar_microstructure` if no real feed arrives.

## CAMPAIGN #13 (BINDING — CANNOT BE AVOIDED)
**Path R is the only productive path.** Follow it if you can ingest a genuinely new real feed with provenance in-session (per readiness spec; validate via `data/real_feed_loader.py`). Otherwise follow **Path C-maintain** (heavy, honest) — do not churn or create fake work.

### Path R (required if new real feed with provenance is ingested this session)
Produce **>= 3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry, fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<new_feed>*.{pkl,json|meta.json}` with **immutable provenance** (source, retrieval, timestamps, symbol map, schema, sha256, `real_data_only=true`,`fabricated_data=false`). **No provenance = do not claim ingestion; treat as Path C-maintain.**
3. `reports/real_feed_unblock_status_<UTC>.json` + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T114512Z.json`, rerun tests).

Candidate families (only with real provenance): `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`.

### Path C-maintain (only if NO new real feed with provenance ingested) — EXPECTED CASE
Do **not** repeat exhaustion/readiness facts as new work. Produce **>= 3 concrete artifacts** that advance fail-closed infrastructure or audit (no fabrication), e.g.:
1. Extend `data/real_feed_loader.py` with a **fail-closed spec+tests** for `intrabar_microstructure` (the only uncovered family per readiness spec), plus `reports/intrabar_microstructure_loader_validation_<UTC>.json` proving it refuses missing/fabricated/proxy inputs (synthetic fixtures only in tests, never labeled real). Per readiness spec: support `kind` `trades` (cols `timestamp_utc`,`symbol`,`price`,`qty`; optional `side_or_is_buyer_maker`) and/or `book` (cols `timestamp_utc`,`symbol`,`bid_px_levels`,`ask_px_levels`,`bid_sz_levels`,`ask_sz_levels`,`depth`); provenance keys `source_provider`,`endpoints_or_files`,`retrieved_at_utc`,`symbol_map`,`kind`,`row_count`,`sha256_pkl`,`real_data_only`,`fabricated_data` (+ `compression_if_any` optional). Refuse missing meta/sha256, fabricated flags, missing required cols, missing/invalid `kind`, and resampled-to-1h-presented-as-microstructure proxies admitted in notes. Register in `FAMILY_SPECS`.
2. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check (still blocked; no new provenance found).
3. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T114512Z.json`, rerun tests.

If Path C-maintain, the loader/validator work must be **real, tested code changes + artifact** (not just prose), and tests must still pass.

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` (Path C-maintain also requires real code+tests).
- **Honesty:** `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.

## COMPLETION CHECK
- [ ] Path R: `*_costed_oos_<UTC>.json` + real provenance in `data/cache/` + status + registry supersede; OR Path C-maintain: tested fail-closed loader/validator for `intrabar_microstructure` + `*_loader_validation_<UTC>.json` + status + registry supersede
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T114512Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache
- [ ] >= 3 new artifacts in `reports/` (Path C-maintain also requires real code+tests)
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts in new registry

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
