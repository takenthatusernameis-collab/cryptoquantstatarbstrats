# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T20:39:07Z (Campaign #31 IN PROGRESS — C31 cointegration artifact produced; unblock status + registry next.)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #30 STATUS (COMPLETE — fail-closed, no proven edge)
Executed 2026-11-05 (this session). Produced (>=3 artifacts):
- `reports/cointegration_campaign30_mt.json` — phase-2 real-data cointegration rigor (17 pairs × 1h/4h/1d, causal trailing OOS/rolling). `real_data_only=true`, `fabricated_data=false`, `causal_only=true`, `trailing_windows_only=true`, `fail_closed=true`, `gating_invariants_preserved=true` (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`). Gate thresholds unchanged; no auto-lift.
- `reports/real_feed_unblock_status_20261105T200500Z.json` — fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir='data/cache', campaign=30, reports_dir='reports', prior_report=reports/real_feed_unblock_status_20261105T195831Z.json)`. `campaign_delta.changed=false`, `honest_assessment=NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. `path_r_triggered=true` (validated `real_quote_volume` present) but **no genuinely different pre-stated R-B hypothesis executed**; C23 NOT rerun. Remaining blocked (unchanged): `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. No proxies labeled real.
- `reports/strategy_edge_registry_20261105T200600Z.json` supersedes `reports/strategy_edge_registry_20261105T195956Z.json` (C29). Pytest **928 passed / 1 skipped / 0 failed / 3572 warnings, ~56.85s, rc=0, full `tests/`**. `oos_edge_proven=false`.

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Fail-closed infra healthy (no infra bottleneck):** full suite **928 passed, 1 skipped, 0 failed**. Do not re-open test/loader infra unless you change it and keep tests green.
- **No valid new feed for remaining blocked families.** `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure = blocked_no_real_feed` (unchanged, fail-closed). `real_quote_volume` validated but C23 hypothesis failed (`oos_edge_proven=false`, 0/11). Spot-only 1h families exhausted; pairs/gating blocked (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Do not spin on unverifiable feeds/proxies.
- **R-B is the only unblocked heavy path on current data — but ONLY with a genuinely different pre-stated hypothesis.** `path_r_triggered=true` because `real_quote_volume` has validated provenance. Re-running C23 (Abnormal Quote Volume Momentum) is **forbidden** (settled: no edge). Any R-B attempt MUST pre-state a materially different hypothesis/mechanic, use WF 720/168/168, cost grid 0–40bps, B&H benchmark on same windows, and produce `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` + tested code + status+registry. `oos_edge_proven=false` is valid.
- **Zero-artifact sessions are automatic failures.** "I looked and found nothing" is not a deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 31 / CAMPAIGN #31 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work and MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT re-run C23 Abnormal Quote Volume Momentum unchanged. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven.

### Binding context (settled — do not re-litigate)
C30 complete (>=3 artifacts: `cointegration_campaign30_mt.json`, `real_feed_unblock_status_20261105T200500Z.json`, `strategy_edge_registry_20261105T200600Z.json`). C27 MT artifacts exist (`live_go_live_authorization_final_mt.json`, `post_deployment_live_readiness_signoff_mt.json`). `oos_edge_proven=false` across registry. Remaining blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Gating invariants preserved (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`). Spot 1h exhausted. `real_quote_volume` validated (C23 no edge). Fail-closed infra green (928 passed, 1 skipped).

## CAMPAIGN #31 (BINDING — CANNOT BE AVOIDED)
Produce **>= 3 artifacts** (all fail-closed, real, reproducible):
1. Run `python scripts/generate_campaign31_artifacts.py` if present and priors satisfied; include its output artifact(s) in `reports/`. If missing/unsatisfied, create `reports/campaign31_execution_blocker_<UTC>.json` (fail-closed, real) documenting exact missing priors + the **smallest concrete unblocking step taken this session** (not just described).
2. `reports/real_feed_unblock_status_<UTC>.json` — honest fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir, campaign=31, reports_dir=..., prior_report=reports/real_feed_unblock_status_20261105T200500Z.json)`, recording delta vs C30.
3. `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261105T200600Z.json` with rerun `pytest tests/ -q` counts (full suite) and C31 artifacts listed. `oos_edge_proven=false` unless pre-stated rule passes.

### Path R-A / R-B (only if applicable)
- **R-A:** only if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session → `<family>_costed_oos_<UTC>.json` + cache provenance/certificate passing `validate_and_load_real_feed` + status (+ prior) + registry supersede.
- **R-B:** only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on validated `real_quote_volume` (not C23 Abnormal Quote Volume Momentum) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40bps, B&H benchmark) + tested runner/code + status (+ prior) + registry supersede. Pre-state the hypothesis in the artifact. `oos_edge_proven=false` is valid.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No re-run of C23 Abnormal Quote Volume Momentum unchanged.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >= 3 new artifacts in `reports/` every session; real tested code + artifact (not just prose) when code changes. Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" / "no proven edge" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK (C31)
- [ ] C31 MT/script artifact(s) produced (or fail-closed blocker artifact with concrete action taken).
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed, includes campaign delta vs C30 prior `20261105T200500Z`).
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261105T200600Z` with rerun test counts.
- [ ] >= 3 new artifacts in `reports/`.
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23 hypothesis rerun unchanged.
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
