# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T115330Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C155 (MANDATORY, HEAVY WORK, START NOW)

C104–C154 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_lmax|entr_lmax_ratio|rqa_ratio_entr_lmax|ENTR_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C155 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_ENTR_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio `RATIO_ENTR_LMAX = ENTR / L_max` (diagonal-line Shannon entropy normalized by max diagonal line length) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `ENTR` = Shannon entropy (natural log) over qualifying diagonal-line length distribution (`k!=0`, main diagonal excluded), `p(l)=n(l)/N`. `L_max` = max qualifying diagonal-line length. Fail-closed NaN/no-signal if `L_max<=0`, no qualifying diagonal lines, `ENTR` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C154 (incl C154 L_max/TT, C153 ENTR/TT, C151 TT/L_max). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_LAM_OVER_TT_RATIO_SHOCK_MR` `LAM/TT_mean`, fail-closed on `TT_mean<=0`/no qualifying vertical lines/`LAM` undefined-non-finite/offdiag-degenerate/undefined — verify grep; or `VOLUME_RQA_DET_OVER_LMAX_RATIO_SHOCK_MR` `%DET/L_max`, fail-closed on `L_max<=0`/no qualifying diagonal lines/`%DET` undefined-non-finite/offdiag-degenerate/undefined — verify grep), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_entr_over_lmax_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C154/C153 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T115330Z.json` sha `8060af8a85ddbdda1fbb51a3bcd19018f87cf8c231c72f81fbadbdc95c8a3fa6` and C154 OOS sha `613b4624747be15c65473ece35fc10bac19d39877cfff5b6b12a197f36ee7c67`). Run it to emit `reports/real_quote_volume_rqa_entr_over_lmax_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 155) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T115330Z.json` (sha `8060af8a85ddbdda1fbb51a3bcd19018f87cf8c231c72f81fbadbdc95c8a3fa6`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C155 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign155_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C155`, `next_campaign: C156`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c156_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C155.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C155 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C155 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T115330Z)
- C104–C153 locked; no reruns unchanged.
- C154 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C154-done/C155-next.
- `numpy/scipy/pandas` importable.
- C155 primary pre-selected: `VOLUME_RQA_ENTR_OVER_LMAX_RATIO_SHOCK_MR` (`ENTR/L_max`) — grep pre-verified 0 hits at C154 wrap-up; re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C155.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C154 result (locked, do not rerun)
- `VOLUME_RQA_LMAX_OVER_TT_RATIO_SHOCK_MR` (L_max/TT_mean), campaign 154, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_lmax_over_tt_ratio_shock_mr_costed_oos_20261107T115254Z.json` (sha `613b4624747be15c65473ece35fc10bac19d39877cfff5b6b12a197f36ee7c67`). `any_exposure_oos:true`; cross-asset net sums `fee0=0.3296176378356719, fee5=0.03261763783567165, fee10=-0.2643823621643284, fee20=-0.8583823621643284, fee40=-2.0463823621643282`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T115330Z.json` (sha `7b67e6ad4d81bc5bdef5929ec0c3d05cab8232c297a2e5b5868145ee8a3b94a0`).
- Registry: `reports/strategy_edge_registry_20261107T115330Z.json` (sha `8060af8a85ddbdda1fbb51a3bcd19018f87cf8c231c72f81fbadbdc95c8a3fa6`, supersedes C153 `98aa65897fac28b12f62c315627211242955eae82509923b1dc58a63ab39e606`).
- Summary: `reports/campaign154_execution_summary_20261107T115330Z.json` (sha `30c3b7e3c2b630563861da6564baf7bd5dba94e5e7eb620fe6254595d816a199`).
- Script: `scripts/run_real_quote_volume_rqa_lmax_over_tt_ratio_shock_mr_costed_oos.py` (sha `b2134436bdbd7c1db8b6d6dc784c023edc24f5dc8a998824b3cf84c9e6f19f2a`). Distinctness grep hits pre=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'entr_over_lmax|entr_lmax_ratio|rqa_ratio_entr_lmax|ENTR_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C155 `ENTR/L_max` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C155-done/C156-next. **Do not stop until C155 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
