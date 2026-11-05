# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T18:32:00Z (Campaign #24 BINDING — execute now. Campaign #23 complete, Path R executed: real_quote_volume feed validated fail-closed, pre-stated costed OOS showed NO proven edge.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #23 STATUS (COMPLETE — Path R executed, NO proven edge)
Campaign #23 executed Path R because a valid real non-spot feed with verifiable provenance was present and passed fail-closed validation: `data/cache/volume_1h_full.meta.json` + `data/cache/volume_1h_full.pkl` + `data/cache/volume_1h_full.provenance.json` (real Binance public spot klines column 5 = quote asset volume, not fabricated, not a proxy) validated via `validate_and_load_real_feed(..., 'real_quote_volume', provenance=...)` as `passed_all_fail_closed_checks` (81792 rows, 16 symbols, 1h UTC 2026-04-01..2026-10-30). A **pre-stated** hypothesis ("Abnormal Quote Volume Momentum", params fixed before OOS) was tested WF 720/168/168, cost grid 0–40 bps, B&H benchmark on same OOS windows (fail-closed edge rule). **Result: 0/11 assets `oos_edge_proven`; no asset met all-slice net>0 AND beat B&H. `oos_edge_proven=false`.** Honest negative result, not progress.
- Tests (full, rerun in-session): **925 passed, 1 skipped, 0 failed** (`python -m pytest tests/ -q`, rc=0, ~57.1s). No loader/test code changes required in C23.
- Campaign #23 artifacts (>=3): `reports/real_quote_volume_abnormal_momentum_costed_oos_20261105T183142Z.json` (sha256 `cb188bfa7b4c039d8648b227a59f1c00ef845b9f09838a57813885eda9cfde71`, pre-stated WF/costs/B&H, fail-closed, `oos_edge_proven=false` 0/11), `reports/real_feed_unblock_status_20261105T182936Z.json` (CLI-generated, fail-closed, `path_r_triggered=true`, `--prior reports/real_feed_unblock_status_20261105T173236Z.json`, delta `UNBLOCK_STATE_CHANGED_REVIEW_REQUIRED`), `reports/cache_provenance_gap_audit_20261105T182936Z.json` (CLI-generated, fail-closed; 21 metas, 1 candidate, 1 valid, 0 refused, `PATH_R_ELIGIBLE_REVIEW_REQUIRED`), `reports/strategy_edge_registry_20261105T183200Z.json` (supersedes `reports/strategy_edge_registry_20261105T173236Z.json`).
- Runner (real, reproducible): `_run_p23_real_quote_volume_costed_oos.py`.
- Real spot cache (reuse as-is, do not re-fetch): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` (sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`) — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot.
- Real non-spot feed now validated (reuse as-is): `real_quote_volume` = **`real_feed_with_provenance_present`** (fail-closed validated). C23 hypothesis tested, **no proven edge** (`oos_edge_proven=false`). Feed remains available for *new, genuinely different, pre-stated* hypotheses only — do not repackage the same hypothesis as new.
- Still blocked (0 valid provenance artifacts): `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed`. No fabricated feeds/proxies.
- Pairs: **PROVEN BLOCKED** (165/165). No re-scan. No gate weakening.
- Spot-only 1h families: **EXHAUSTED** (P4 mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion) — 0 proven net-of-cost OOS edge.
- `oos_edge_proven=false` across the registry.

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Fail-closed unblock/audit/delta/trend/cache-provenance-audit/report infrastructure is in place and healthy:** full suite **925 passed, 1 skipped, 0 failed**; loader/CLI smoke green. No test-infrastructure or loader bottleneck — do not re-open.
- **`real_quote_volume` is now a validated real feed.** Path R for the *remaining* blocked families still requires a *genuinely new real feed with verifiable provenance ingested in-session* (or a complete provenance certificate satisfying loader schema) that passes `validate_and_load_real_feed` + unblock-status/audit. Not an in-session option unless you can actually produce a passing valid artifact. Do not spin on unverifiable feeds. Document honestly and fall to Path C-maintain or a new pre-stated hypothesis on the validated `real_quote_volume` feed (if genuinely different).
- **Path C-maintain / new-prestated-volume-hypothesis is the expected, mandatory in-session path when no new valid feed for a remaining blocked family exists.** Do not treat "no new feed" as a license to do nothing or to re-run spot/cointegration scans on the same cache as new. Do not re-run the C23 Abnormal Quote Volume Momentum hypothesis unchanged.
- **Zero-artifact sessions are automatic failures.** "I looked and found nothing" is not a deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 24 / CAMPAIGN #24 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT repackage the C23 Abnormal Quote Volume Momentum hypothesis unchanged. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled — do not re-litigate)
Campaign #23 status above. `oos_edge_proven=false` across the board. `real_quote_volume` is a validated real feed (present, passing provenance) but C23 hypothesis found no edge. Remaining families blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Pairs proven blocked. Spot 1h exhausted. Fail-closed ingestion+scan+audit+unblock-status+delta+trend+cache-provenance-audit+CLI infrastructure exists. Full suite green. Bottlenecks removed.

## CAMPAIGN #24 (BINDING — CANNOT BE AVOIDED)
Choose exactly one path and produce **>= 3 artifacts**:

### Path R-A (required ONLY if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session)
Target a remaining blocked family (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, or `intrabar_microstructure`). Produce **>= 3 artifacts**:
1. `reports/<family>_costed_oos_<UTC>.json` — pre-stated WF/costs/carry (as applicable), fail-closed, net-of-cost/carry OOS, benchmark. `oos_edge_proven=true` only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
2. `data/cache/<feed>*` + complete immutable provenance/certificate (source, retrieval, timestamps, symbol map, schema, sha256, `real_data_only=true`,`fabricated_data=false`) **passing `validate_and_load_real_feed`**. **No passing provenance = do not claim ingestion; treat as Path R-B or C-maintain.**
3. `reports/real_feed_unblock_status_<UTC>.json` (include `--prior reports/real_feed_unblock_status_20261105T182936Z.json`) + `reports/strategy_edge_registry_<UTC>.json` (supersedes `20261105T183200Z.json`, rerun tests).

### Path R-B (only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on the validated `real_quote_volume` feed)
The hypothesis must be **structurally/pre-stated different** from C23 Abnormal Quote Volume Momentum (state exactly how). Produce **>= 3 artifacts**:
1. `reports/real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` — pre-stated (params fixed before OOS), WF 720/168/168, cost grid 0–40bps, B&H benchmark on same OOS windows, fail-closed edge rule. `oos_edge_proven=false` is valid.
2. Real, tested runner/script used (or tested code changes) + `reports/real_feed_unblock_status_<UTC>.json` (with `--prior reports/real_feed_unblock_status_20261105T182936Z.json`, still honest).
3. `reports/strategy_edge_registry_<UTC>.json` superseding `20261105T183200Z.json` with rerun test counts.

### Path C-maintain (only if NO real feed passes fail-closed validation for a remaining blocked family AND no genuinely different pre-stated volume hypothesis is credibly/testably implemented this session) — EXPECTED CASE
Do **not** repeat exhaustion/readiness facts as new work. Produce **>= 3 concrete artifacts** that advance fail-closed infrastructure or audit (no fabrication), e.g.:
1. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check using `generate_unblock_status_report`/CLI fail-closed scan **with `--prior reports/real_feed_unblock_status_20261105T182936Z.json`**.
2. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T183200Z.json`, rerun tests and record counts.
3. A third concrete artifact advancing fail-closed infrastructure or audit (e.g., extend loader/readiness/delta/trend/gap-audit tooling, add tests, a CLI/script/CI-audit that emits/validates the fail-closed unblock/gap report, or a clearly-labeled audit artifact with **real tested code**). Avoid structurally-similar spot retests on the same cache and avoid re-running C23 volume hypothesis unchanged.

If Path C-maintain, the work must be **real, tested code changes + artifact** (not just prose), and tests must still pass.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No re-run of C23 Abnormal Quote Volume Momentum unchanged.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >=3 new artifacts in `reports/` every session (Path C-maintain/Path R-B also requires real code+tests where code changes). Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" / "no proven edge" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK
- [ ] Path R-A: `<family>_costed_oos_<UTC>.json` + real passing provenance/certificate in `data/cache/` + status (+ prior delta) + registry supersede; OR Path R-B: genuinely different pre-stated `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` + tested runner/code + status (+ prior delta) + registry supersede; OR Path C-maintain: `real_feed_unblock_status_<UTC>.json` (with `--prior 20261105T182936Z`) + `strategy_edge_registry_<UTC>.json` supersede + third concrete artifact (+ tested code if code changes)
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed scan, includes campaign delta vs C23 when prior supplied)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T183200Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23 hypothesis re-run unchanged
- [ ] >= 3 new artifacts in `reports/`
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts in new registry

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
