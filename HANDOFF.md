# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T11:37:02Z (Campaign #11 binding; handoff re-stamped for next agentic session; no new real feed found — Path C-maintain)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## P14/CAMPAIGN #10 COMPLETION (THIS SESSION — 3 ARTIFACTS + CODE/TESTS, Path C-maintain)
- **A (heavy, real code+tests):** `data/real_feed_loader.py` + `tests/test_real_feed_loader_validation.py` — fail-closed real-feed loader/validator for `funding_basis_carry` (conforms to `reports/real_feed_ingestion_readiness_20261105T104640Z.json`). Validates provenance keys, `real_data_only=true`/`fabricated_data=false`, sha256_pkl integrity, schema/row/column/timestamp, and refuses missing metadata, mismatches, fabricated/proxy-as-real flags, undocumented sentinels, unknown families. **15 targeted tests pass.** Synthetic fixtures used only in tests (never labeled real).
- **B:** `reports/funding_basis_carry_loader_validation_20261105T105258Z.json` — refusal-proof cases (11 cases: valid passes + 10 refusals incl. missing metadata, sha256 mismatch, fabricated flag, proxy-labeled-real notes, missing provenance/columns/data file, unknown family). Verdict `PASS_FAIL_CLOSED`.
- **C:** `reports/real_feed_unblock_status_20261105T105258Z.json` — honest re-check; **no new real feeds with provenance** found (`cache_keyword_hits=[]`). `cross_exchange_dual_venue_same_asset|funding_basis_carry|term_structure_real_iv_vol_surface|intrabar_microstructure=blocked_no_real_feed`. Pairs PROVEN BLOCKED (165/165; no re-scan). Spot-only cached 1h = EXHAUSTED.
- **D (registry):** `reports/strategy_edge_registry_20261105T105258Z.json` — supersedes `reports/strategy_edge_registry_20261105T104640Z.json`. Rerun tests: **847 passed, 1 skipped, 0 failed, 3569 warnings, 40.37s** (`PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q`, rc=0).

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 15 / CAMPAIGN #11 — MANDATORY.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
- **Tests (P14):** 847 passed, 1 skipped, 0 failed. Re-run and record in new registry.
- **Real spot cache (reuse as-is):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` — 11 assets (`ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP`), 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot. **Do not re-fetch.**
- **Pairs:** PROVEN BLOCKED (165/165). No re-scan. No gate weakening.
- **Spot-only 1h families:** **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge.
- **Feeds:** `dual-venue|funding-basis-carry|real-IV/vol-surface|intrabar-microstructure = blocked_no_real_feed` (no provenance found). No fabricated feeds.
- **Readiness spec:** `reports/real_feed_ingestion_readiness_20261105T104640Z.json`.
- **Fail-closed loader (new, funding_basis_carry):** `data/real_feed_loader.py` + tests `tests/test_real_feed_loader_validation.py` + validation proof `reports/funding_basis_carry_loader_validation_20261105T105258Z.json`.

### Core truth
No proven net-of-cost OOS edge on real cached spot 1h (WF 720/168/168, cost grid 0/5/10/20 bps, B&H benchmark). No real non-spot feeds with provenance are present. Spot 1h is exhausted. Fail-closed ingestion infrastructure exists for `funding_basis_carry` and must be used if a real feed arrives.

## CAMPAIGN #11 (BINDING — CANNOT BE AVOIDED)
**Path R is the only productive path.** Follow it if you can ingest a genuinely new real feed with provenance in-session. If not, follow Path C-maintain (heavy, honest) — do **not** churn or create fake work.

### Path R (required if new real feed with provenance is ingested this session)
Produce **>=3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry, fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<new_feed>*.{pkl,json|meta.json}` with **immutable provenance** (source, retrieval, timestamps, symbol map, schema, sha256, `real_data_only=true`,`fabricated_data=false`). **No provenance = do not claim ingestion; treat as Path C-maintain.** Validate via `data/real_feed_loader.py` where applicable / per readiness spec.
3. `reports/real_feed_unblock_status_<UTC>.json` + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T105258Z.json`, rerun tests).

Candidate families (only with real provenance): `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`.

### Path C-maintain (only if NO new real feed with provenance ingested)
Do **not** repeat exhaustion/readiness facts as new work. Produce **>=3 concrete artifacts** that advance fail-closed infrastructure or audit (no fabrication), e.g.:
1. Extend `data/real_feed_loader.py` with a **fail-closed spec+tests** for another blocked family (`cross_exchange_dual_venue_same_asset` OR `term_structure_real_iv_vol_surface` OR `intrabar_microstructure`) per readiness spec, plus `reports/<family>_loader_validation_<UTC>.json` proving it refuses missing/fabricated/proxy inputs (synthetic fixtures only in tests, never labeled real).
2. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check (still blocked; no new provenance found).
3. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T105258Z.json`, rerun tests, restates exhausted/blocked truth.

If Path C-maintain, the loader/validator work must be **real, tested code changes + artifact** (not just prose), and tests must still pass.

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` (Path R also needs provenance in `data/cache/`; Path C-maintain needs real code+tests).
- **Honesty:** `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.

## COMPLETION CHECK
- [ ] Path R: `*_costed_oos_<UTC>.json` + real provenance in `data/cache/` + status + registry supersede; OR Path C-maintain: tested fail-closed loader/validator for another family + `*_loader_validation_<UTC>.json` + status + registry supersede
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T105258Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache
- [ ] >= 3 new artifacts in `reports/` (Path C-maintain also requires real code+tests)

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
