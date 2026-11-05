# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T12:55:03Z (Campaign #16 BINDING — execute now. No new real feed with provenance found in Campaign #15.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #15 STATUS (COMPLETE — Path C-maintain)
No new real feed with provenance was found/ingested (fail-closed scan via `data.real_feed_loader.scan_cache_for_real_nonspot_feeds` of `data/cache/`, **21 meta files, 0 valid non-spot provenance artifacts**), so Path R did not trigger. Path C-maintain executed with real, tested code + artifacts.
- Tests (full): **899 passed, 1 skipped, 0 failed** (`pytest tests/ -q`, rc=0, 40.42s). Loader tests `tests/test_real_feed_loader_validation.py`: **67 passed** (+4 scan-helper tests).
- Campaign #15 artifacts (>=3): `reports/spot_cost_regime_audit_20261105T124233Z.json` (audit-only, `oos_edge_proven=false`, not a new family/edge claim), `reports/real_feed_unblock_status_20261105T124816Z.json`, `reports/strategy_edge_registry_20261105T124816Z.json` (supersedes `20261105T114735Z.json`).
- Code (real, tested): `data/real_feed_loader.py` adds `scan_cache_for_real_nonspot_feeds` (fail-closed; counts only artifacts passing `validate_and_load_real_feed`: `real_data_only=true`, `fabricated_data=false`, sha256 verified, schema valid, no proxy admissions). `tests/test_real_feed_loader_validation.py` +4 tests (empty/missing dir blocked, spot-meta rejected as non-spot, valid funding artifact accepted).
- Real spot cache (reuse as-is, do not re-fetch): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` (sha256 in registry) — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot.
- Pairs: **PROVEN BLOCKED** (165/165). No re-scan. No gate weakening.
- Spot-only 1h families: **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge.
- Feeds: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed` (0 valid provenance artifacts found). No fabricated feeds/proxies. Fail-closed loader/scan in place for all four.
- `oos_edge_proven=false` across the registry.

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Path R is externally gated:** it requires a *genuinely new real feed with verifiable provenance ingested in-session*. Not an in-session option unless you can actually pull one. Do not spin on unverifiable feeds. This is an external blocker that cannot be removed by code changes; document honestly and fall to Path C-maintain.
- **Path C-maintain is the expected, mandatory in-session path when no new feed exists.** Do not treat "no new feed" as a license to do nothing or to re-run spot/cointegration scans on the same cache as new.
- **Zero-artifact sessions are automatic failures.** "I looked and found nothing" is not a deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.
- Tests are green (899/1/0) — no test-infrastructure bottleneck. `data/real_feed_loader.py` fail-closed scan + loader ready for reuse.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 18 / CAMPAIGN #16 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
Campaign #15 status above. `oos_edge_proven=false` across the board. No real non-spot feeds with provenance present (fail-closed scan). Pairs proven blocked. Spot 1h exhausted. Fail-closed ingestion+scan infrastructure exists for all four families. Full suite green.

## CAMPAIGN #16 (BINDING — CANNOT BE AVOIDED)
**Path R is the only productive edge path.** Follow it **only** if you can ingest a genuinely new real feed with provenance in-session (per readiness spec; validate via `data/real_feed_loader.py`). Otherwise follow **Path C-maintain** (heavy, honest) — do not churn or create fake work.

### Path R (required ONLY if new real feed with provenance is ingested this session)
Produce **>= 3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry, fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<new_feed>*.{pkl,json|meta.json}` with **immutable provenance** (source, retrieval, timestamps, symbol map, schema, sha256, `real_data_only=true`,`fabricated_data=false`). **No provenance = do not claim ingestion; treat as Path C-maintain.**
3. `reports/real_feed_unblock_status_<UTC>.json` + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T124816Z.json`, rerun tests).

Candidate families (only with real provenance): `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`.

### Path C-maintain (only if NO new real feed with provenance ingested) — EXPECTED CASE
Do **not** repeat exhaustion/readiness facts as new work. Produce **>= 3 concrete artifacts** that advance fail-closed infrastructure or audit (no fabrication), e.g.:
1. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check using fail-closed scan (still blocked; no new provenance found).
2. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T124816Z.json`, rerun tests.
3. A third concrete artifact advancing fail-closed infrastructure or audit (e.g., extend `scan_cache_for_real_nonspot_feeds`/readiness tooling, add loader/scan tests, or a clearly-labeled audit artifact with **real tested code**). Avoid structurally-similar spot retests on the same cache presented as new edge work.

If Path C-maintain, the work must be **real, tested code changes + artifact** (not just prose), and tests must still pass.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` every session (Path C-maintain also requires real code+tests if code changes). Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK
- [ ] Path R: `*_costed_oos_<UTC>.json` + real provenance in `data/cache/` + status + registry supersede; OR Path C-maintain: `real_feed_unblock_status_<UTC>.json` + `strategy_edge_registry_<UTC>.json` supersede + third concrete artifact (+ tested code if code changes)
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed scan)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T124816Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache
- [ ] >= 3 new artifacts in `reports/` (Path C-maintain also requires real code+tests)
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts in new registry

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
