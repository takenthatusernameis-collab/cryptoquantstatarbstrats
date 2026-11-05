# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T16:42:26Z (Campaign #22 BINDING — execute now. Campaign #21 complete, Path C-maintain.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #21 STATUS (COMPLETE — Path C-maintain)
Campaign #21 executed fully; no new real non-spot feed with provenance was found/ingested (fail-closed scan of `data/cache/`, **21 meta files, 0 candidate hits, 0 valid non-spot provenance artifacts**, readiness spec `real_feed_ingestion_readiness_20261105T104640Z.json` discovered). Path R did not trigger. Path C-maintain executed with real, tested code + artifacts.
- Tests (full, rerun in-session after C21 changes): **922 passed, 1 skipped, 0 failed** (`python -m pytest tests/ -q`, rc=0, ~57.9s). Loader tests `tests/test_real_feed_loader_validation.py`: **90 passed** (+5 from C20 baseline 85). Import/CLI smoke green (status + trend).
- Campaign #21 artifacts (>=3): `reports/real_feed_unblock_status_20261105T164226Z.json` (CLI-generated, fail-closed, `path_r_triggered=false`, readiness details, **campaign_delta vs C20**: `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`), `reports/real_feed_unblock_trend_audit_20261105T164226Z.json` (fail-closed historical trend aggregation across 17 `real_feed_unblock_status` reports; observable-only transitions; `path_r_ever_triggered=false`; honest assessment `OBSERVABLE_STATE_CHANGE_IN_HISTORY_REVIEW_REQUIRED` due to historical report-shape evolution — **not an edge claim**; latest state blocked), `reports/strategy_edge_registry_20261105T164226Z.json` (supersedes `reports/strategy_edge_registry_20261105T163640Z.json`).
- Code (real, tested): `data/real_feed_loader.py` adds `build_unblock_trend_report()` (fail-closed aggregation of `real_feed_unblock_status_*.json`: transitions, path_r history, unreadable files recorded explicitly, chronological sort with campaign-int preference, latest numbered campaign) and CLI `--trend`/`--trend-limit`. +5 tests in `tests/test_real_feed_loader_validation.py`.
- Real spot cache (reuse as-is, do not re-fetch): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` (sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`) — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot.
- Pairs: **PROVEN BLOCKED** (165/165). No re-scan. No gate weakening.
- Spot-only 1h families: **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge.
- Feeds: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed` (0 valid provenance artifacts found). No fabricated feeds/proxies. Fail-closed loader/scan/audit/unblock-status/delta/trend/CLI infrastructure in place for all four.
- `oos_edge_proven=false` across the registry.

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Fail-closed unblock/audit/delta/trend/report infrastructure strengthened in Campaign #21:** `build_unblock_trend_report`/CLI `--trend`/`--trend-limit` added (+5 tests). Full suite green (**922 passed, 1 skipped, 0 failed**); loader 90 passed; import/CLI smoke green. No test-infrastructure or loader bottleneck — do not re-open.
- **Path R is externally gated:** it requires a *genuinely new real feed with verifiable provenance ingested in-session*. Not an in-session option unless you can actually pull one (and pass `validate_and_load_real_feed` + `generate_unblock_status_report`/`audit_cache_for_real_nonspot_feeds`). Do not spin on unverifiable feeds. Document honestly and fall to Path C-maintain.
- **Path C-maintain is the expected, mandatory in-session path when no new feed exists.** Do not treat "no new feed" as a license to do nothing or to re-run spot/cointegration scans on the same cache as new.
- **Zero-artifact sessions are automatic failures.** "I looked and found nothing" is not a deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 23 / CAMPAIGN #22 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
Campaign #21 status above. `oos_edge_proven=false` across the board. No real non-spot feeds with provenance present (fail-closed scan: 0 candidate hits / 0 valid artifacts, 21 meta files). Pairs proven blocked. Spot 1h exhausted. Fail-closed ingestion+scan+audit+unblock-status+delta+trend+CLI infrastructure exists for all four. Full suite green. Bottlenecks removed.

## CAMPAIGN #22 (BINDING — CANNOT BE AVOIDED)
**Path R is the only productive edge path.** Follow it **only** if you can ingest a genuinely new real feed with provenance in-session (per readiness spec; validate via `data/real_feed_loader.py`). Otherwise follow **Path C-maintain** (heavy, honest) — do not churn or create fake work.

### Path R (required ONLY if new real feed with provenance is ingested this session)
Produce **>= 3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry, fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<new_feed>*.{pkl,json|meta.json}` with **immutable provenance** (source, retrieval, timestamps, symbol map, schema, sha256, `real_data_only=true`,`fabricated_data=false`). **No provenance = do not claim ingestion; treat as Path C-maintain.**
3. `reports/real_feed_unblock_status_<UTC>.json` (include `--prior reports/real_feed_unblock_status_20261105T164226Z.json`) + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T164226Z.json`, rerun tests).

Candidate families (only with real provenance): `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`.

### Path C-maintain (only if NO new real feed with provenance ingested) — EXPECTED CASE
Do **not** repeat exhaustion/readiness facts as new work. Produce **>= 3 concrete artifacts** that advance fail-closed infrastructure or audit (no fabrication), e.g.:
1. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check using `generate_unblock_status_report`/CLI fail-closed scan **with `--prior reports/real_feed_unblock_status_20261105T164226Z.json`** (still blocked; no new provenance found).
2. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T164226Z.json`, rerun tests and record counts.
3. A third concrete artifact advancing fail-closed infrastructure or audit (e.g., extend loader/readiness/delta/trend tooling, add tests, a CLI/script/CI-audit that emits/validates the fail-closed unblock report, or a clearly-labeled audit artifact with **real tested code**). Avoid structurally-similar spot retests on the same cache presented as new edge work.

If Path C-maintain, the work must be **real, tested code changes + artifact** (not just prose), and tests must still pass.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` every session (Path C-maintain also requires real code+tests if code changes). Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK
- [ ] Path R: `*_costed_oos_<UTC>.json` + real provenance in `data/cache/` + status (+ prior delta) + registry supersede; OR Path C-maintain: `real_feed_unblock_status_<UTC>.json` (with `--prior`) + `strategy_edge_registry_<UTC>.json` supersede + third concrete artifact (+ tested code if code changes)
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed scan, includes campaign delta vs C21 when prior supplied)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T164226Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache
- [ ] >= 3 new artifacts in `reports/` (Path C-maintain also requires real code+tests)
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts in new registry

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
