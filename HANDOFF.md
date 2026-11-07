# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T214600Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T214345Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C175 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos_20261107T214159Z.json`=497b4e0ed839d3d92c9d9fe75d6ea124fa3811a593da7acc00db53cdaf7f72af (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.080213502570049, fee5=-0.3982135025700493, fee10=-0.7162135025700493, fee20=-1.3522135025700492, fee40=-2.6242135025700493; provenance reconciliation: script refactored post-213708Z, OOS re-run 214159Z confirmed identical numeric results), ingest `reports/real_feed_ingest_attempt_20261107T214345Z.json`=2c4f26c906fea7ad894939b84a2d19367f3a365bdb00958830e8eefbf62c7a09 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T214345Z.json`=f8fae5c72ff3d3a9f6740e61bcbf8662b1bd498cd676a47f9485d5fc0b1ab528 (supersedes C174 registry cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5), summary `reports/campaign175_execution_summary_20261107T214345Z.json`=dc96f7bd1d87cb31e0818a248f33a8b114568a21832141556939585201006fa1, script `scripts/run_real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos.py`=4cf42383ef08f04cde54f87ad758c8275b603a0569ad6efef2e77a8dbace8133. `state.yaml` synced C175-done/C176-next.
- **Collision guards:** C175 `ENTR_OVER_VMAX` completed with recorded pre-distinctness grep 0 at 20261107T214159Z (primary candidate used). **C176 preselected `VOLUME_RQA_LAM_OVER_VMAX_RATIO_SHOCK_MR` => 0 non-self** (`grep -rEIn 'lam_over_vmax|LAM_OVER_VMAX|rqa_ratio_lam_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1`, verified 20261107T214345Z / re-checked now). Fallback `LMAX_OVER_VMAX` also grep 0 (20261107T214345Z). **Re-verify at C176 run time (0 non-self) before implementation.**
- **No C176 artifacts exist yet** (`reports/*c176*`/`*campaign176*`/`*lam_over_vmax*` absent at handoff time). Prior C104–C175 remain locked.

## C104–C175 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T214345Z.json` (f8fae5c72ff3d3a9f6740e61bcbf8662b1bd498cd676a47f9485d5fc0b1ab528). Use it as `PRIOR_REGISTRY`; cite C175 OOS SHA 497b4e0ed839d3d92c9d9fe75d6ea124fa3811a593da7acc00db53cdaf7f72af in pre-stated refs.

## INITIAL TASK — C176 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T214600Z
**Execute C176 now. NO status-only replies. NO status summary before >= 3 NEW concrete C176 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LAM_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio **LAM/V_max** (laminarity `LAM` = fraction of recurrence points forming vertical lines of length >= `l_min`, normalized by max vertical line length `V_max`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `V_max==0` or undefined/non-finite (no qualifying vertical lines), `LAM` undefined/non-finite/degenerate (no qualifying vertical line distribution or `sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LAM` numerator with `V_max` denominator — pairing not used in C125–C175 (C173 used `DET/V_max`, C175 used `ENTR/V_max`). `LAM_OVER_VMAX` tokens absent in scripts/strategies/backtest/utils at selection (grep 0).

Fallback if primary collides at run time (re-grep both): `VOLUME_RQA_LMAX_OVER_VMAX_RATIO_SHOCK_MR` (`grep -rEIn 'lmax_over_vmax|LMAX_OVER_VMAX|rqa_ratio_lmax_over_vmax' ...` == 0 now).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'lam_over_vmax|LAM_OVER_VMAX|rqa_ratio_lam_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick grep-zero fallback (`LMAX_OVER_VMAX`), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C176 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C175): `scripts/run_real_quote_volume_rqa_lam_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T214345Z.json` (f8fae5c72ff3d3a9f6740e61bcbf8662b1bd498cd676a47f9485d5fc0b1ab528), cite C175 OOS SHA 497b4e0ed839d3d92c9d9fe75d6ea124fa3811a593da7acc00db53cdaf7f72af. Emit `reports/real_quote_volume_rqa_lam_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 176) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T214345Z.json` (f8fae5c72ff3d3a9f6740e61bcbf8662b1bd498cd676a47f9485d5fc0b1ab528). Structurally consistent; include prior + C176 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign176_execution_summary_<UTC>.json` listing **all new C176 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C176`, `next_campaign:C177`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c177_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C176, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C176 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T214600Z)
- C104–C175 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C175 `ENTR_OVER_VMAX` completed/verified; provenance reconciliation recorded (post-refactor re-run matched numerics).
- C176 `LAM_OVER_VMAX` preselect grep verified 0 non-self (fallback `LMAX_OVER_VMAX` also 0) — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C176 artifacts exist; start implementation/run immediately from the C175 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'lam_over_vmax|LAM_OVER_VMAX|rqa_ratio_lam_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C176 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C176-done/C177-next with grep-verified C177 preselection
```

## NEXT FOCUS CAMPAIGN — C177 (preselect at end of C176; HEAVY WORK MANDATORY)
After C176 completes, **C177 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C176 (consider `LMAX_OVER_VMAX` fallback if unused, or other distinct RQA-ratio pairs), record grep cmd/hits/evidence in `state.yaml.c177_preselected`, then execute C177 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file)
