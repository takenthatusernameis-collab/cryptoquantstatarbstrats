# READ THIS FIRST — C146 COMPLETED / C147 NEXT (20261107T101900Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute C147 NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness (C146 completion, 20261107T101900Z):** `numpy,scipy,pandas` importable; required caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`). `pytest` unavailable (honest: `/usr/bin/python3: No module named pytest`). C147 primary grep-zero verified at C146 completion: `lam_over_entr|lam_entr_ratio|rqa_ratio_lam_entr|LAM_OVER_ENTR` → 0 hits in `scripts/ strategies/ backtest/ utils/`. **Re-verify grep at C147 run time (collision guard).**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C146 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** `edge_claim: NONE` throughout.
- **C146 COMPLETED (20261107T101900Z):** `VOLUME_RQA_DET_OVER_ENTR_RATIO_SHOCK_MR` (RQA ratio `RATIO_DET_ENTR = %DET / ENTR`, determinism normalized by diagonal-line Shannon entropy, on delay-embedded log-volume returns; `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`; fail-closed on `ENTR<=0`/no qualifying diagonal lines/`%DET` undefined/non-finite/offdiag-degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_det_over_entr_ratio_shock_mr_costed_oos_20261107T101900Z.json` (sha `ccbb1b34621e899f9f598c3241f9a1e6f3da23ade5e82aeaf53115d08df2d3d4`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.23281776095722806`, `fee5_slip5=-0.21018223904277233`, `fee10_slip10=-0.6531822390427724`, `fee20_slip20=-1.539182239042772`, `fee40_slip40=-3.3111822390427723`). Refs C145 registry sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20` / C145 OOS sha `5d38cc6eb608083cd13c57fadfdab73e75e4e66d61af6ae56d9b93ec2782a263`; grep-zero `det_over_entr|det_entr_ratio|rqa_ratio_det_entr|DET_OVER_ENTR` verified before implementation/run.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T101900Z.json` (sha `9a50c0d1220c8479db8c4e8bf50db1a970693abb1535f396f584c99bcfaa9bea`, campaign 146, nonspot blocked fail-closed, `rb_unblocked=true`).
  - Script: `scripts/run_real_quote_volume_rqa_det_over_entr_ratio_shock_mr_costed_oos.py` (sha `67d9111de0af7e1e90117018c47e082fb226f133e9e2e6f6d16eed9c5802890f`).
  - Registry superseding C145: `reports/strategy_edge_registry_20261107T101900Z.json` (sha `0dc859e3cdd77da6f177a2ec993f877d3410b3edcecf59b4532a9712323afb8c`, supersedes `reports/strategy_edge_registry_20261107T101205Z.json` sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20`).
  - Summary: `reports/campaign146_execution_summary_20261107T101900Z.json` (sha `f204695e58b6f98f17202bbaa1e8d618c768b836c6cbb4597f5305164c4a1c19`).
  - `research_state/state.yaml` synced: `latest_campaign_done: C146`, `next_campaign: C147`.

## Bottlenecks removed (this handoff)
- C104–C146 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T101900Z.json` (sha `0dc859e3cdd77da6f177a2ec993f877d3410b3edcecf59b4532a9712323afb8c`).
- C146 completed heavy: DET/ENTR grep-zero distinctness verified pre-run; OOS/ingest/registry/summary emitted with disk-verified SHAs; state synced.
- C147 primary pre-selected and grep-zero verified (20261107T101900Z): `VOLUME_RQA_LAM_OVER_ENTR_RATIO_SHOCK_MR` (`%LAM/ENTR`).
- "No status before >=3 new artifacts" + mandatory run — forces heavy work for C147.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C147 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C146 done — do NOT rerun.

### Step 0 — Readiness + distinctness grep + implement/run (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_entr\|lam_entr_ratio\|rqa_ratio_lam_entr\|LAM_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Primary C147 candidate (pre-selected, grep-zero verified 20261107T101900Z): **`VOLUME_RQA_LAM_OVER_ENTR_RATIO_SHOCK_MR`** — RQA ratio `RATIO_LAM_ENTR = %LAM / ENTR` (laminarity normalized by diagonal-line Shannon entropy) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `%LAM` = (sum of vertical-line points for qualifying vertical lines `l>=l_min`, main diagonal excluded) / (offdiag recurrence sum). `ENTR` = -sum p(l)*ln(p(l)) over qualifying diagonal lines (natural log raw, C130-consistent). Fail-closed NaN/no-signal if `ENTR<=0`, no qualifying diagonal lines, `%LAM` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C146 (incl C127 %LAM direct, C130 ENTR direct, C134 %LAM/%DET, C136 %LAM/%RR, C139 %RR/%LAM, C140 %RR/TT, C143 %LAM/TT, C146 %DET/ENTR) — C147 trades `%LAM/ENTR`. **Re-verify grep at run time (must still be zero non-self). If collision, pick next distinct alternative (`VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` `ENTR/%LAM` fail-closed on `%LAM<=0`/no qualifying vertical lines; or `VOLUME_RQA_LMAX_OVER_ENTR_RATIO_SHOCK_MR` `L_max/ENTR` fail-closed on `ENTR<=0`/no qualifying diagonal lines/`L_max` undefined), re-grep, and record chosen feature + grep evidence.**

Implement script `scripts/run_real_quote_volume_rqa_lam_over_entr_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on the C146/C145 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, and `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T101900Z.json` sha `0dc859e3cdd77da6f177a2ec993f877d3410b3edcecf59b4532a9712323afb8c` and C146 OOS sha `ccbb1b34621e899f9f598c3241f9a1e6f3da23ade5e82aeaf53115d08df2d3d4`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 147) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T101900Z.json` (sha `0dc859e3cdd77da6f177a2ec993f877d3410b3edcecf59b4532a9712323afb8c`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include C140–C146 context/entries and add C147 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign147_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C147`, `next_campaign: C148`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c148_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C147.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C147 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C147 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'lam_over_entr\|lam_entr_ratio\|rqa_ratio_lam_entr\|LAM_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C147 %LAM/ENTR (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C147-done/C148-next. **Do not stop until C147 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
