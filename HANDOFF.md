# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T22:18:07Z (Campaign #33 artifacts refreshed via generate_campaign33_artifacts.py → cointegration_campaign33_mt.json; `oos_edge_proven=false`) — C34 binding next.**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost OOS statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #33 STATUS (EXECUTED — fail-closed, no proven edge)
Produced this session (>=3 concrete artifacts in `reports/`):
- `reports/cointegration_campaign32_mt.json` — generated/refreshed via `python scripts/generate_campaign32_artifacts.py` (real data only, causal/trailing, gate thresholds unchanged). `gating_invariants_preserved=true` (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`).
- `reports/real_feed_unblock_status_20261105T204518Z.json` — fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir='data/cache', campaign=32, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261105T204108Z.json')`. `campaign_delta.honest_assessment=NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, `changed=false`, `path_r_triggered=true` (validated `real_quote_volume` present) but **no genuinely different pre-stated R-B hypothesis executed**. C23 Abnormal Quote Volume Momentum NOT rerun (settled: no edge).
- `reports/strategy_edge_registry_20261105T204534Z.json` — supersedes `reports/strategy_edge_registry_20261105T204133Z.json`. Full suite rerun: **`pytest tests/ -q` => 928 passed, 1 skipped, 0 failed, 3567 warnings, ~56.96s, rc=0**. `oos_edge_proven=false`.
- `reports/campaign33_handoff_execution_20261105T204534Z.json` — execution log (to be produced by next session if not already).

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Infra healthy (no infra bottleneck):** fail-closed test/loader/registry path is green (928 passed, 1 skipped). Do not reopen infra unless you change it and keep full tests green.
- **No valid new feed for remaining blocked families (unchanged):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed` (fail-closed). Do not label proxies as real; do not fabricate feeds/provenance.
- **Spot 1h exhausted; cointegration gating settled on current cache:** pairs/gating invariants preserved (`1h 0/17`, `4h 1/17 POL/BTC`, `1d 0/17`). Do not pairs/feed re-scan or produce structurally similar spot retests on the same cache as a “new campaign”.
- **R-B is the only unblocked heavy path on current data — ONLY with a genuinely different pre-stated hypothesis.** `path_r_triggered=true` because validated `real_quote_volume` provenance exists. Re-running C23 Abnormal Quote Volume Momentum unchanged is **forbidden**. Any R-B attempt MUST pre-state a materially different hypothesis/mechanic (write it into the artifact before trusting results), use WF 720/168/168, cost grid 0–40bps, B&H benchmark on the same windows, and produce `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` + tested code/runner + status (+ prior) + registry supersede. `oos_edge_proven=false` is valid.
- **Zero-artifact / investigation-only sessions are automatic failures.** “Looked and found nothing” is not deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 34 / CAMPAIGN #34 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work, MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT rerun C23 Abnormal Quote Volume Momentum unchanged. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled real. `oos_edge_proven=false` is valid and required if edge is not proven.

### Binding context (settled — do not re-litigate)
C33 executed (>=3 artifacts): `cointegration_campaign32_mt.json` refreshed, `real_feed_unblock_status_20261105T204518Z.json`, `strategy_edge_registry_20261105T204534Z.json`. C27 MT artifacts exist (`live_go_live_authorization_final_mt.json`, `post_deployment_live_readiness_signoff_mt.json`). Registry truth: `oos_edge_proven=false`. Remaining blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Gating invariants preserved (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`). Spot 1h exhausted. `real_quote_volume` validated (C23 no edge). Fail-closed infra green (928 passed, 1 skipped).

## CAMPAIGN #34 (BINDING — CANNOT BE AVOIDED)
Produce **>= 3 artifacts** (all fail-closed, real, reproducible):
1. Run `python scripts/generate_campaign33_artifacts.py` if present and priors satisfied; include its output artifact(s) in `reports/`. If missing/unsatisfied, create `reports/campaign33_execution_blocker_<UTC>.json` (fail-closed, real) documenting exact missing priors + the **smallest concrete unblocking step taken this session** (not just described).
2. `reports/real_feed_unblock_status_<UTC>.json` — honest fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir, campaign=33, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261105T204518Z.json')`, recording delta vs prior.
3. `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261105T204534Z.json` with rerun `pytest tests/ -q` counts (full suite) and C34 artifacts listed. `oos_edge_proven=false` unless pre-stated rule passes.

### Path R-A / R-B (only if applicable)
- **R-A:** only if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session → `<family>_costed_oos_<UTC>.json` + cache provenance/certificate passing `validate_and_load_real_feed` + status (+ prior) + registry supersede.
- **R-B:** only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on validated `real_quote_volume` (not C23 Abnormal Quote Volume Momentum) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40bps, B&H benchmark) + tested runner/code + status (+ prior) + registry supersede. Pre-state hypothesis in artifact. `oos_edge_proven=false` is valid.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No rerun of C23 Abnormal Quote Volume Momentum unchanged.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >= 3 new artifacts in `reports/` every session; real tested code + artifact (not just prose) when code changes. Investigation-only prose is not a substitute.
- **Honesty:** Honest “still blocked” / “still exhausted” / “no proven edge” reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK (C34)
- [ ] C33/script artifact(s) produced (`scripts/generate_campaign33_artifacts.py` output) or fail-closed blocker artifact with concrete action taken.
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed, delta vs `20261105T204518Z`).
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261105T204534Z`.
- [ ] >= 3 new artifacts in `reports/`.
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23 hypothesis rerun unchanged.
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
