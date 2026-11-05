# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T19:37:05Z (Campaign #26 BINDING — execute now. Campaign #25 complete: cointegration_recertification_audit_mt.json + drift_triggered_regating_mt.json regenerated fail-closed, tests 928 passed/1 skipped/0 failed. C25 outputs are now priors for C26, unblocking the C27+ MT chain. Next session: execute C26 per below; >= 3 artifacts; no investigation-only.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #25 STATUS (COMPLETE — fail-closed, no proven edge)
Campaign #25 executed `scripts/generate_campaign25_artifacts.py`. Produced: `reports/cointegration_recertification_audit_mt.json` and `reports/drift_triggered_regating_mt.json` (fail-closed, `real_data_only: true`, `fabricated_data: false`, `no_auto_lift`, thresholds unchanged). These are now the C26 prior artifacts and unblock the C27+ MT chain — bottleneck removed. Tests (full, rerun in-session): **928 passed, 1 skipped, 0 failed** (`python -m pytest tests/ -q`, rc=0, ~57.11s). `oos_edge_proven=false` across the registry; unchanged vs C24/C25.

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Fail-closed infra healthy (no infra bottleneck):** full suite **928 passed, 1 skipped, 0 failed**; loader/CLI/status/audit/delta/trend/cache-provenance-audit green. Do not re-open test/loader infrastructure unless you change it and keep tests green.
- **C26 is now runnable:** `scripts/generate_campaign26_artifacts.py` requires `reports/portfolio_gating_mt.json` (present) and C25 priors `cointegration_recertification_audit_mt.json` + `drift_triggered_regating_mt.json` (just regenerated). Run it first — this unblocks C27+.
- **No valid new feed for remaining blocked families is present.** `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed`. `real_quote_volume` validated but C23 hypothesis failed (`oos_edge_proven=false`). Spot-only 1h families exhausted; pairs proven blocked (165/165). Do not spin on unverifiable feeds or proxies.
- **Zero-artifact sessions are automatic failures.** "I looked and found nothing" is not a deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 26 / CAMPAIGN #26 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT re-run C23 Abnormal Quote Volume Momentum unchanged. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven.

### Binding context (settled — do not re-litigate)
Campaign #25 complete (2 artifacts, tests green). `oos_edge_proven=false`. C25 priors present. Remaining blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Pairs proven blocked. Spot 1h exhausted. Fail-closed infra exists. Full suite green. `real_quote_volume` validated (C23 no edge).

## CAMPAIGN #26 (BINDING — CANNOT BE AVOIDED)
Produce **>= 3 artifacts**:

1. `reports/end_to_end_pairs_execution_validation_mt.json` — run `python scripts/generate_campaign26_artifacts.py` (fail-closed end-to-end pairs execution validation over 1h/4h/1d, zero capital/orders/fills for blocked pairs).
2. `reports/live_operational_readiness_signoff_mt.json` — same script (fail-closed live operational readiness signoff).
3. `reports/real_feed_unblock_status_<UTC>.json` — honest fail-closed re-check using `generate_unblock_status_report`/CLI scan **with `--prior reports/real_feed_unblock_status_20261105T193230Z.json`**, recording campaign delta vs C25. Plus `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261105T193213Z.json` with rerun test counts.

### Path R-A / R-B (only if applicable)
- **R-A:** only if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session → `<family>_costed_oos_<UTC>.json` + cache provenance/certificate passing `validate_and_load_real_feed` + status (+ prior) + registry supersede.
- **R-B:** only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on validated `real_quote_volume` → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40bps, B&H benchmark) + tested runner/code + status (+ prior) + registry supersede. `oos_edge_proven=false` is valid.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No re-run of C23 Abnormal Quote Volume Momentum unchanged.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >= 3 new artifacts in `reports/` every session; real tested code + artifact (not just prose) when code changes. Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" / "no proven edge" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK
- [ ] `reports/end_to_end_pairs_execution_validation_mt.json` and `reports/live_operational_readiness_signoff_mt.json` generated via `scripts/generate_campaign26_artifacts.py`.
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed scan, includes campaign delta vs C25 when prior supplied).
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261105T193213Z.json` with test counts.
- [ ] >= 3 new artifacts in `reports/`.
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23 hypothesis re-run unchanged.
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts in new registry.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
