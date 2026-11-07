# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T124720Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C157 (MANDATORY, HEAVY WORK, START NOW)

C104–C156 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'rr_over_entr|rr_entr_ratio|rqa_ratio_rr_entr|RR_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C157 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_RR_OVER_ENTR_RATIO_SHOCK_MR` — RQA ratio `RATIO_RR_ENTR = RR / ENTR` (recurrence rate normalized by diagonal-line Shannon entropy) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `RR` = recurrence rate = off-diagonal qualifying recurrence fraction `offdiag_sum/(M_pts*(M_pts-1))`; `ENTR` = Shannon entropy (natural log) over qualifying diagonal-line length distribution (`k!=0`, main diagonal excluded, `l>=l_min=2`), `p(l)=n(l)/N`. Fail-closed NaN/no-signal if `ENTR<=0` or undefined/non-finite, no qualifying diagonal lines/distribution, `RR` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C156 (incl C156 RR/L_max, C155 ENTR/L_max, C154 L_max/TT, C153 ENTR/TT, C151 TT/L_max). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_LAM_OVER_LMAX_RATIO_SHOCK_MR` `%LAM/L_max`, fail-closed on `L_max<=0`/no qualifying diagonal lines/`%LAM` undefined-non-finite/offdiag-degenerate/undefined — grep observed 0 hits 20261107T124230Z, re-verify; or `VOLUME_RQA_TT_OVER_ENTR_RATIO_SHOCK_MR` `TT_mean/ENTR`, fail-closed on `ENTR<=0`/undefined/`TT_mean` undefined-no qualifying vertical lines/recurrence degenerate — verify grep), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_rr_over_entr_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C155/C156 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T124230Z.json` sha `c6248481e3b747d0b2e864c442fcd092a8ed669e364e30a9a9796451a984d8c9` and C156 OOS sha `ac68a83d7cf852b54c8046114efded6e376fd96aed34c6c8d1ed6b408c28b7a2`). Run it to emit `reports/real_quote_volume_rqa_rr_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 157) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T124230Z.json` (sha `c6248481e3b747d0b2e864c442fcd092a8ed669e364e30a9a9796451a984d8c9`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C157 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign157_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C157`, `next_campaign: C158`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c158_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C157.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C157 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C157 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T124230Z)
- C104–C155 locked; no reruns unchanged.
- C156 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C156-done/C157-next.
- `numpy/scipy/pandas` importable.
- C156 collision guard pre-verified 0 hits for RR/L_max; C157 primary (RR/ENTR) grep observed 0 hits at preselect — re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C157.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C156 result (locked, do not rerun)
- `VOLUME_RQA_RR_OVER_LMAX_RATIO_SHOCK_MR` (RR/L_max), campaign 156, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_rr_over_lmax_ratio_shock_mr_costed_oos_20261107T124142Z.json` (sha `ac68a83d7cf852b54c8046114efded6e376fd96aed34c6c8d1ed6b408c28b7a2`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.5333821003688645, fee5=-0.9003821003688648, fee10=-1.267382100368865, fee20=-2.0013821003688648, fee40=-3.4693821003688643`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T124230Z.json` (sha `503b73dda8c282c48f6fc1dd42a5642da54e7d8ba99a961415e23aed6d0f3e8c`).
- Registry: `reports/strategy_edge_registry_20261107T124230Z.json` (sha `c6248481e3b747d0b2e864c442fcd092a8ed669e364e30a9a9796451a984d8c9`, supersedes C155 `a36c8f4e40b9e9b35f5a2c24c9338362c641bea42dab0baa0576dcc9ce91717c`).
- Summary: `reports/campaign156_execution_summary_20261107T124230Z.json` (sha `99efc47fc674d5c5d8a36a78436a5b855da5f4e251e2cbc5bbd69f58362db7bc`).
- Script: `scripts/run_real_quote_volume_rqa_rr_over_lmax_ratio_shock_mr_costed_oos.py` (sha `4efd84306703e83f4efec3ba7085edfa2e8649d191a58f0699f6ab6a8fa3801c`). Distinctness grep hits pre (non-self)=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'rr_over_entr|rr_entr_ratio|rqa_ratio_rr_entr|RR_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C157 `RR/ENTR` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C157-done/C158-next. **Do not stop until C157 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
