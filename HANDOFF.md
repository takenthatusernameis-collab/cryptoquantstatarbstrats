# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T104057Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C148 (MANDATORY, HEAVY WORK, START NOW)

C104–C147 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_lam|entr_lam_ratio|rqa_ratio_entr_lam|ENTR_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C148 candidate (pre-selected, grep-zero verified 20261107T103803Z — re-verify at run time):** `VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` — RQA ratio `RATIO_ENTR_LAM = ENTR / %LAM` (diagonal-line Shannon entropy normalized by laminarity) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `ENTR` = -sum p(l)*ln(p(l)) over qualifying diagonal lines (natural log raw, C130/C146-consistent). `%LAM` = (sum of vertical-line points for qualifying vertical lines `l>=l_min`, main diagonal excluded) / (offdiag recurrence sum). Fail-closed NaN/no-signal if `%LAM<=0`, no qualifying vertical lines, `ENTR` undefined/non-finite (`ENTR<=0`), offdiag/recurrence degenerate, or undefined. Distinct from C125–C147 (incl C127 %LAM direct, C130 ENTR direct, C134 %LAM/%DET, C136 %LAM/%RR, C139 %RR/%LAM, C140 %RR/TT, C143 %LAM/TT, C146 %DET/ENTR, C147 %LAM/ENTR) — C148 trades `ENTR/%LAM` inverse. **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_LMAX_OVER_ENTR_RATIO_SHOCK_MR` `L_max/ENTR` fail-closed on `ENTR<=0`/no qualifying diagonal lines/`L_max` undefined; or `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` `%DET/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`%DET` undefined), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_entr_over_lam_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C147/C146 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T102339Z.json` sha `68e8d689d99c0e8a09bcd11d72a8f27e572e1f63f3b6ea14c8f35c424fcf530c` and C147 OOS sha `d5a3831eb7c876cf3b502f8670ea3cbdc933e9daf973baa2880c1143e00f899f`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 148) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T102339Z.json` (sha `68e8d689d99c0e8a09bcd11d72a8f27e572e1f63f3b6ea14c8f35c424fcf530c`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include C141–C147 context/entries and add C148 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign148_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C148`, `next_campaign: C149`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c149_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C148.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C148 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C148 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T104057Z)
- C104–C146 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T102339Z.json` (sha `68e8d689d99c0e8a09bcd11d72a8f27e572e1f63f3b6ea14c8f35c424fcf530c`).
- C147 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C147-done/C148-next.
- `numpy/scipy/pandas` were missing (blocker for running C148) — installed and importable 20261107T103803Z.
- C148 primary pre-selected and grep-zero verified (20261107T103803Z): `VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` (`ENTR/%LAM`).
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C148.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'entr_over_lam|entr_lam_ratio|rqa_ratio_entr_lam|ENTR_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C148 ENTR/%LAM (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C148-done/C149-next. **Do not stop until C148 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
