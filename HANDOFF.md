# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T195750Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T195750Z) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C171 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_rr_over_vmax_ratio_shock_mr_costed_oos_20261107T195511Z.json`=04e05bcd56a38c6c47147ae30a0c4c456addc6f494dc356138e1a9436b449342 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true, cross-asset nets: fee0=-0.090227, fee5=-0.356227, fee10=-0.622227, fee20=-1.154227, fee40=-2.218227), ingest `reports/real_feed_ingest_attempt_20261107T195645Z.json`=348a3229f8596dc974b1724a9a9a64681ff757ae3256d8e20e2c23f9fd343691, registry `reports/strategy_edge_registry_20261107T195645Z.json`=00fa95eb87598fd107f861766c0ce193ce24d32c06cb3db4ef30835adb16812d (supersedes C170 c89757fe...), summary `reports/campaign171_execution_summary_20261107T195645Z.json`=e2c018956a795a80bd18ff05755de1e0a960f5579a7b4fbb86c7fa360a7b0c40, script `scripts/run_real_quote_volume_rqa_rr_over_vmax_ratio_shock_mr_costed_oos.py`=5c2e0cdce0fcd970ea73c24fc0c38529d65e6a09b49881d754fe832349c779e0. state.yaml synced C171-done/C172-next.
- **Collision guards verified:** C170 `LMAX_OVER_DET` locked. C171 `RR_OVER_VMAX` verified **0** non-self before implementation/run. C172 preselected `VOLUME_RQA_TT_OVER_VMAX_RATIO_SHOCK_MR` => **0** non-self (grep -rEIn 'tt_over_vmax|vmax_over_tt|TT_OVER_VMAX|RQA_TT_OVER_VMAX|rqa_ratio_tt_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1, observed 20261107T195645Z, post-C171). Re-verify at run time (0 non-self) before implementation.
- **No C172 artifacts exist yet** (`reports/*c172*`/`*campaign172*` absent). Prior C104–C171 remain locked. Re-verified at 20261107T195750Z: `tt_over_vmax`/`vmax_over_tt` collision guard = 0 non-self, C172 unstarted.

## C104–C171 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T195645Z.json` (00fa95eb87598fd107f861766c0ce193ce24d32c06cb3db4ef30835adb16812d). Use it as `PRIOR_REGISTRY`; cite C171 OOS SHA 04e05bcd56a38c6c47147ae30a0c4c456addc6f494dc356138e1a9436b449342 in pre-stated refs.

## INITIAL TASK — C172 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T195750Z
**Execute C172 now. NO status-only replies. NO status summary before >= 3 NEW concrete C172 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C171; run-time grep required)
`VOLUME_RQA_TT_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio **TT/V_max** (trapping time `TT` = average length of vertical lines with `l>=l_min` normalized by max vertical line length `V_max`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `V_max==0` or undefined/non-finite (no qualifying vertical lines), `TT` undefined/non-finite/degenerate, recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM`, C166 `V_max/%LAM`, C167 `TT/TREND`, C168 `RR/TREND`, C169 `V_max/TREND`, C170 `Lmax/DET`, C171 `RR/V_max`. C167 uses TT numerator with TREND denominator; C172 uses TT numerator with V_max denominator — distinct denominator token family. Explicit `TT_OVER_VMAX`/`VMAX_OVER_TT` tokens absent (verified 0 at 20261107T195645Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'tt_over_vmax|vmax_over_tt|TT_OVER_VMAX|RQA_TT_OVER_VMAX|rqa_ratio_tt_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (e.g. `DET_OVER_VMAX` or `RR_OVER_LMAX` — verify 0 at run time; any distinct RQA-ratio candidate not used in C125–C172), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C172 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C171): `scripts/run_real_quote_volume_rqa_tt_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T195645Z.json` (00fa95eb87598fd107f861766c0ce193ce24d32c06cb3db4ef30835adb16812d), cite C171 OOS SHA 04e05bcd56a38c6c47147ae30a0c4c456addc6f494dc356138e1a9436b449342. Emit `reports/real_quote_volume_rqa_tt_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 172) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T195645Z.json` (00fa95eb87598fd107f861766c0ce193ce24d32c06cb3db4ef30835adb16812d). Structurally consistent; include prior + C172 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign172_execution_summary_<UTC>.json` listing **all new C172 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C172`, `next_campaign:C173`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c173_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C172, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C172 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T195750Z)
- C104–C171 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C171 `RR_OVER_VMAX` collision guard verified 0 non-self; C172 `TT_OVER_VMAX`/`VMAX_OVER_TT` grep verified 0 — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C172 artifacts exist; start implementation/run immediately from the C171 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'tt_over_vmax|vmax_over_tt|TT_OVER_VMAX|RQA_TT_OVER_VMAX|rqa_ratio_tt_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C172 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C172-done/C173-next with grep-verified C173 preselection
```

## NEXT FOCUS CAMPAIGN — C173 (preselect at end of C172; HEAVY WORK MANDATORY)
After C172 completes, **C173 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C172, record grep cmd/hits/evidence in `state.yaml.c173_preselected`, then execute C173 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
