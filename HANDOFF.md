# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T23:37:00Z (Campaign #40 executed; registry `strategy_edge_registry_20261105T233646Z.json`; `oos_edge_proven=false`) — C41 binding next.**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost out-of-sample statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #40 STATUS (EXECUTED — fail-closed, no proven edge)
Produced/confirmed this session (>=3 concrete artifacts in `reports/`; 4 total):
- `reports/real_quote_volume_climax_mean_reversion_costed_oos_20261105T233410Z.json` — Campaign 40 Path R-B on validated `real_quote_volume` (Binance spot klines col 5, fail-closed via `validate_and_load_real_feed`, `volume_1h_full.provenance.json`). **GENUINELY DIFFERENT hypothesis from C23 "Abnormal Quote Volume Momentum": quote-volume climax mean reversion / FADE (vol_z>1.5 → OPPOSITE of 24h return direction; exit on vol normalization / max hold / flip; execution t→t+1), not momentum/trend.** WF rolling 720/168/168, cost grid 0–40bps (fee+slip pairs), B&H benchmark on same OOS windows, pre-stated edge rule (exposure>0 AND all slices OOS net>0 AND OOS net>B&H → true, else false). Result: `n_oos_edge_proven=0/11`, `oos_edge_proven=false` for all assets (valid/honest; no edge claimed). Script: `scripts/generate_campaign40_artifacts.py` (created + run, priors satisfied = C39 artifacts present).
- `reports/real_feed_unblock_status_20261105T233410Z.json` — fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir='data/cache', campaign=40, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261105T224120Z.json')`. `path_r_triggered=true` (`real_quote_volume` validated) but **no genuinely different pre-stated R-B hypothesis executed this session beyond C40 climax mean reversion**. Remaining blocked families unchanged: `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed`. `campaign_delta` vs 224120Z: `changed=false`, honest assessment `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`.
- `reports/campaign40_execution_20261105T233656Z.json` — C40 execution record (honest, fail-closed).
- `reports/strategy_edge_registry_20261105T233646Z.json` — supersedes `reports/strategy_edge_registry_20261105T232053Z.json`. Full suite rerun: **`pytest tests/ -q` => 928 passed, 1 skipped, 0 failed, ~32.4s, rc=0 (verified 2026-11-05)**. `oos_edge_proven=false`. C40 artifacts listed. Path R: `c23_rerun=false`, `different_prestated_hypothesis_tested=true` (C40 climax mean reversion).

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Infra healthy (no infra bottleneck):** fail-closed test/loader/registry path green (928 passed, 1 skipped, 0 failed, verified). Do not reopen infra unless you change it and keep full tests green.
- **No valid new feed for remaining blocked families (unchanged):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed` (fail-closed). Unblock recheck shows no new validated feeds for these families. Do not label proxies as real; do not fabricate feeds/provenance.
- **Spot 1h exhausted; cointegration gating settled on current cache:** pairs/gating invariants preserved (`1h 0/17`, `4h 1/17 POL/BTC`, `1d 0/17`). Do not pairs/feed re-scan or produce structurally similar spot retests on the same cache as a "new campaign".
- **real_quote_volume is validated but C23 momentum AND C40 climax mean reversion are now both tested (oos_edge_proven=false).** Any further R-B attempt on `real_quote_volume` MUST be a GENUINELY DIFFERENT pre-stated hypothesis/mechanic from BOTH C23 (momentum) and C40 (climax mean reversion/fade) — write it into the artifact before trusting results, use WF 720/168/168, cost grid 0–40bps, B&H benchmark on same windows, and produce `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` + tested code/runner + status (+ prior) + registry supersede. `oos_edge_proven=false` is valid.
- **Zero-artifact / investigation-only sessions are automatic failures.** "Looked and found nothing" is not deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 41 / CAMPAIGN #41 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work, MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT rerun C23 Abnormal Quote Volume Momentum unchanged (nor reuse C40's climax mean reversion unchanged as "new"). Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled real. `oos_edge_proven=false` is valid and required if edge is not proven.

### Binding context (settled — do not re-litigate)
C40 executed (>=3 artifacts): `real_quote_volume_climax_mean_reversion_costed_oos_20261105T233410Z.json`, `real_feed_unblock_status_20261105T233410Z.json`, `campaign40_execution_20261105T233656Z.json`, `strategy_edge_registry_20261105T233646Z.json`. Registry truth: `oos_edge_proven=false`. Remaining blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Gating invariants preserved (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`). Spot 1h exhausted. `real_quote_volume` validated (C23 no edge; C40 climax mean reversion no edge). Fail-closed infra green (928 passed, 1 skipped, 0 failed).

### CAMPAIGN #41 (BINDING — CANNOT BE AVOIDED)
Produce **>= 3 artifacts** (all fail-closed, real, reproducible):
1. Run `python scripts/generate_campaign41_artifacts.py` if present and priors satisfied; include its output artifact(s) in `reports/`. If missing/unsatisfied, create `reports/campaign41_execution_blocker_<UTC>.json` (fail-closed, real) documenting exact missing priors + the **smallest concrete unblocking step taken this session** (not just described).
2. `reports/real_feed_unblock_status_<UTC>.json` — honest fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir, campaign=41, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261105T233410Z.json')`, recording delta vs prior.
3. `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261105T233646Z.json` with rerun `pytest tests/ -q` counts (full suite) and C41 artifacts listed. `oos_edge_proven=false` unless pre-stated rule passes.

### Path R-A / R-B (only if applicable)
- **R-A:** only if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session → `<family>_costed_oos_<UTC>.json` + cache provenance/certificate passing `validate_and_load_real_feed` + status (+ prior) + registry supersede.
- **R-B:** only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on validated `real_quote_volume` (NOT C23 Abnormal Quote Volume Momentum, NOT C40 Quote Volume Climax Mean Reversion) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40bps, B&H benchmark) + tested runner/code + status (+ prior) + registry supersede. Pre-state hypothesis in artifact; state how it differs from C23 and C40. `oos_edge_proven=false` is valid.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No rerun of C23 Abnormal Quote Volume Momentum unchanged. No reuse of C40 climax mean reversion unchanged as a "new" campaign.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >= 3 new artifacts in `reports/` every session; real tested code + artifact (not just prose) when code changes. Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" / "no proven edge" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK (C41)
- [ ] C41/script artifact(s) produced (`scripts/generate_campaign41_artifacts.py` output) or fail-closed blocker artifact with concrete action taken.
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed, delta vs `20261105T233410Z`).
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261105T233646Z`.
- [ ] >= 3 new artifacts in `reports/`.
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23 hypothesis rerun unchanged; no C40 climax-mean-reversion reuse unchanged.
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
