# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-06T01:31:32Z (Campaign #43 executed; registry `strategy_edge_registry_20261106T004355Z.json`; `oos_edge_proven=false`) — C44 binding next.**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies. Priority mission: find/validate a net-of-cost out-of-sample statistical/arbitrage edge on real crypto data only. Fail-closed. Heavy, reproducible artifacts required. This file is the ONLY durable handoff. Read it first. Execute it. Do not re-litigate settled facts.**

## CAMPAIGN #43 STATUS (EXECUTED — fail-closed, no proven edge)
Produced this session (3 concrete artifacts in `reports/`) + tested runners (`scripts/generate_campaign43_artifacts.py`, `scripts/emit_campaign43_registry.py`, `scripts/run_campaign43_unblock_status.py`):
- `reports/real_quote_volume_volume_price_divergence_reversion_costed_oos_20261106T004243Z.json` — Campaign 43 Path R-B on validated `real_quote_volume` (Binance spot klines col 5, fail-closed via `validate_and_load_real_feed`, `volume_1h_full.provenance.json`). **GENUINELY DIFFERENT pre-stated hypothesis from C23/C40/C41/C42:** "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)" — fade price extremes when volume fails to confirm (new 48h high/low with vol_z < 0.5; short on high+ret24>0, long on low+ret24<0); exit on vol_z > 0.8 confirmation / max hold 12h / price reversion; execution t→t+1. WF rolling 720/168/168, cost grid 0–40bps, B&H benchmark on same OOS windows. Pre-stated edge rule: exposure>0 AND all slices OOS net>0 AND OOS net>B&H. Result: `n_oos_edge_proven=0/11`, `oos_edge_proven=false` (11 assets all exposure=true, edge=false; no edge claimed). Real data only.
- `reports/real_feed_unblock_status_20261106T004254Z.json` — fail-closed re-check (`campaign=43`, prior `reports/real_feed_unblock_status_20261106T003709Z.json`). `path_r_triggered=true` (`real_quote_volume` validated) but no new real feed for remaining blocked families. `campaign_delta.changed=false`, `honest_assessment=NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. Blocked unchanged: `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed`.
- `reports/strategy_edge_registry_20261106T004355Z.json` — supersedes `reports/strategy_edge_registry_20261106T003832Z.json`. Full suite rerun: **`pytest tests/ -q` => 928 passed, 1 skipped, 0 failed, rc=0** (verified this session). `oos_edge_proven=false`. C43 artifacts listed. Path R: `c23_rerun=false`, `c40_climax_mean_reversion_rerun=false`, `c41_rerun=false`, `c42_rerun=false`, `different_prestated_hypothesis_tested=true` (C43 volume-price divergence reversion fade).

## BOTTLENECK REMOVAL (READ BEFORE ACTING)
- **Infra healthy (no infra bottleneck):** fail-closed test/loader/registry path green (928 passed, 1 skipped, 0 failed, rc=0, verified this session). Do not reopen infra unless you change it and keep full tests green.
- **No valid new feed for remaining blocked families (unchanged):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed`. Do not label proxies as real; do not fabricate feeds/provenance.
- **Spot 1h exhausted; cointegration gating settled on current cache:** pairs/gating invariants preserved (`1h 0/17`, `4h 1/17 POL/BTC`, `1d 0/17`). Do not pairs/feed re-scan or produce structurally similar spot retests on the same cache as a "new campaign".
- **`real_quote_volume` now tested with FIVE hypotheses (all oos_edge_proven=false):** C23=high-vol momentum, C40=high-vol climax mean-reversion/fade, C41=low-vol dry-up breakout continuation, C42=volume-expansion breakout confirmation continuation, C43=volume-price divergence reversion fade. Any further R-B attempt on `real_quote_volume` MUST be a GENUINELY DIFFERENT pre-stated hypothesis/mechanic from C23, C40, C41, C42, AND C43 — write it into the artifact before trusting results, use WF 720/168/168, cost grid 0–40bps, B&H benchmark on same windows, and produce `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` + tested runner/code + status (+ prior) + registry supersede. `oos_edge_proven=false` is valid.
- **Zero-artifact / investigation-only sessions are automatic failures.** "Looked and found nothing" is not deliverable. Produce concrete `reports/` artifacts plus tested code where code changes are involved.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 44 / CAMPAIGN #44 — MANDATORY, NOT OPTIONAL.** Next agent MUST NOT do investigation-only work, MUST NOT generate structurally-similar spot retests on the same cache presented as a new campaign, and MUST NOT rerun C23/C40/C41/C42/C43 hypotheses unchanged. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled real. `oos_edge_proven=false` is valid and required if edge is not proven.

### Binding context (settled — do not re-litigate)
C43 executed (>=3 artifacts): `real_quote_volume_volume_price_divergence_reversion_costed_oos_20261106T004243Z.json`, `real_feed_unblock_status_20261106T004254Z.json`, `strategy_edge_registry_20261106T004355Z.json`. Registry truth: `oos_edge_proven=false`. Remaining blocked: `funding_basis_carry|cross_exchange_dual_venue_same_asset|term_structure_real_iv_vol_surface|intrabar_microstructure`. Gating invariants preserved (`1h=[]`,`4h=[POL/BTC]`,`1d=[]`). Spot 1h exhausted. `real_quote_volume` validated (C23/C40/C41/C42/C43 no edge). Fail-closed infra green (928 passed, 1 skipped, 0 failed). `scripts/generate_campaign43_artifacts.py` + `scripts/emit_campaign43_registry.py` + `scripts/run_campaign43_unblock_status.py` present and executed.

### CAMPAIGN #44 (BINDING — CANNOT BE AVOIDED)
Produce **>= 3 artifacts** (all fail-closed, real, reproducible):
1. Run `python scripts/generate_campaign44_artifacts.py` if present and priors satisfied; include its output artifact(s) in `reports/`. If missing/unsatisfied, create `reports/campaign44_execution_blocker_<UTC>.json` (fail-closed, real) documenting exact missing priors + the **smallest concrete unblocking step taken this session** (not just described).
2. `reports/real_feed_unblock_status_<UTC>.json` — honest fail-closed re-check via `data.real_feed_loader.generate_unblock_status_report(cache_dir, campaign=44, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261106T004254Z.json')`, recording delta vs prior.
3. `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T004355Z.json` with rerun `pytest tests/ -q` counts (full suite) and C44 artifacts listed. `oos_edge_proven=false` unless pre-stated rule passes.

### Path R-A / R-B (only if applicable)
- **R-A:** only if a genuinely NEW real feed for a remaining blocked family passes fail-closed validation with complete provenance this session → `<family>_costed_oos_<UTC>.json` + cache provenance/certificate passing `validate_and_load_real_feed` + status (+ prior) + registry supersede.
- **R-B:** only if NO new blocked-family feed passes, but you test a GENUINELY DIFFERENT pre-stated hypothesis on validated `real_quote_volume` (NOT C23 momentum, NOT C40 climax mean reversion, NOT C41 dry-up breakout continuation, NOT C42 volume-expansion breakout confirmation, NOT C43 volume-price divergence reversion fade) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40bps, B&H benchmark) + tested runner/code + status (+ prior) + registry supersede. Pre-state hypothesis in artifact; state how it differs from C23/C40/C41/C42/C43. `oos_edge_proven=false` is valid.

## ANTI-EVASION (ENFORCED — FUTURE AGENTS CANNOT OPT OUT)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests on the same cache presented as new. No rerun of C23/C40/C41/C42/C43 hypotheses unchanged.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening/fabrication/proxies:** Never weaken gates. No proxies labeled real. No fabricated feeds/provenance. `oos_edge_proven=false` is valid; exhaustion/blockers must remain explicit.
- **Heavy work mandatory:** >= 3 new artifacts in `reports/` every session; real tested code + artifact (not just prose) when code changes. Investigation-only prose is not a substitute.
- **Honesty:** Honest "still blocked" / "still exhausted" / "no proven edge" reports are acceptable deliverables; fake progress is not.

## COMPLETION CHECK (C44)
- [ ] C44/script artifact(s) produced (`scripts/generate_campaign44_artifacts.py` output) or fail-closed blocker artifact with concrete action taken.
- [ ] `reports/real_feed_unblock_status_<UTC>.json` exists (honest, fail-closed, delta vs `20261106T004254Z`).
- [ ] `reports/strategy_edge_registry_<UTC>.json` supersedes `20261106T004355Z`.
- [ ] >= 3 new artifacts in `reports/`.
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan; no structurally-similar spot retest on same cache; no C23/C40/C41/C42/C43 hypothesis rerun unchanged.
- [ ] Full suite green: rerun `pytest tests/ -q` and record counts.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
