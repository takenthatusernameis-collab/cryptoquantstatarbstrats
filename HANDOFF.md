# READ THIS FIRST — SINGLE DURABLE HANDOFF (NEXT AGENT START: 2026-11-08T00:52:30Z)
**Repo:** `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Priority (inferred from repo name): fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. **Claim edge ONLY if the exact fail-closed edge rule holds.** R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest. **C104–C188 are LOCKED — do not rerun unchanged.**

## VERIFIED BASELINE (2026-11-08T00:52:30Z) — no reruns
- `deps_ok`: numpy 2.5.4 / scipy 1.18.1 / pandas 3.1.1 importable. `pytest 9.2.0` available.
- Caches present: `data/cache/volume_1h_full.pkl`, `volume_1h_full.meta.json`, `volume_1h_full.provenance.json`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C187 COMPLETE/LOCKED** (SHAs from bytes): OOS `reports/real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos_20261108T004708Z.json`=0f5b82f91352ab34741936164e6d1888e93b4865342ab1f7975c017ee896cd63 (`VOLUME_RQA_LAVG_OVER_ENTR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`, exposure true, all-cost-positive false, beats-BH-mean false; cross fee0_slip0=0.5562567597620807 → fee40_slip40=-2.7557432402379196). Ingest `reports/real_feed_ingest_attempt_20261108T004812Z.json`=4fdf046ce1e35322f62ee5902e09da083a78e1bc11de9ded2f58774c08d4aaf6 (nonspot blocked fail-closed, `rb_unblocked:true`). Registry `reports/strategy_edge_registry_20261108T004812Z.json`=1aca1a556e00763cec77945c6c48085b2ba77b1c486932444510d8221124eeb9 supersedes C186 32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61. Script `scripts/run_real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos.py`=4785c5b3d8e872ecf073d18dbf40a50b76726303d9754e7a396ddcb8d914725a. Summary `reports/campaign187_execution_summary_20261108T004812Z.json`=61cac13022c7636b0551ba7205cdfc3b4de6627e4cc9f6ea4cfa310c0eb54844.
- **C188 COMPLETE/LOCKED** (SHAs from bytes): OOS `reports/real_quote_volume_rqa_trend_over_det_ratio_shock_mr_costed_oos_20261108T005102Z.json`=efe782e49e1fa6219f05e424d1d9901a12e2cb020cd6d8d6f13d39cc7269ec4e (`VOLUME_RQA_TREND_OVER_DET_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`, exposure true, all-cost-positive false, beats-BH-mean false). Ingest `reports/real_feed_ingest_attempt_20261108T005205Z.json`=512c4cd75525e519bd72aef01f9b825d569f7af3575c8c14b1f2e5acd821bac6. Registry `reports/strategy_edge_registry_20261108T005205Z.json`=aadd225ddaf2bcc83cff6a1c41bb35105c7b8e651e994f152cedb2bb2a04d640 supersedes C187 1aca1a556e00763cec77945c6c48085b2ba77b1c486932444510d8221124eeb9. Script `scripts/run_real_quote_volume_rqa_trend_over_det_ratio_shock_mr_costed_oos.py`=7f83353fa022dbce8e3dd41bf9e9a4dfeac6ed27b5a5ddc758fde09b1ded97dd. Summary `reports/campaign188_execution_summary_20261108T005205Z.json`=8de537217997a3ff773579fc6661b8c6ad198892e8052f2f1dc60c6028865bc0.
- C189 collision note (resolved, recorded): `LAM_OVER_DET` family collided with existing repo script(s) (10 hits observed 2026-11-08T00:52:30Z); **do not use**. `LAVG_OVER_RR` grep returned **0 non-self hits** (2026-11-08T00:52:30Z) and is preselected. **Re-verify 0 non-self at C189 run time before implementation.**

## BOTTLENECKS REMOVED / NO EXCUSES (2026-11-08T00:52:30Z)
- C104–C188 locked; artifact SHAs verified; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready; pytest available. Nonspot ingest blocker does **not** block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. No other TODO/NEXT/SESSION files.
- **No status-only replies. No “summarize then stop”. No waiting.** Work starts by running prereq/grep commands and implementing C189.

## INITIAL TASK — C189 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C189 now.** You must produce **>= 3 NEW concrete C189 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus the OOS script and synced `research_state/state.yaml`. A status summary is allowed **only after** these artifacts exist.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_LAVG_OVER_RR_RATIO_SHOCK_MR` — RQA ratio **LAVG/RR** on delay-embedded log-volume returns. `LAVG` = mean diagonal line length over qualifying diagonal lines (k>=1, l>=`l_min`, excluding LOI) on the recurrence matrix. `RR` = recurrence rate = number of recurrent pairs / `M_pts^2` on the full recurrence matrix (pre-stated). `RATIO_LAVG_RR = LAVG / RR`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `RR==0` or RR undefined/non-finite/degenerate, LAVG undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only. Pre-stated distinctness: LAVG/RR pairing not used C125–C188; grep 0 at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAVG_OVER_RR|lavg_over_rr|rqa_ratio_lavg_over_rr|rqa_lavg_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C189 (e.g., `LMAX_OVER_LAVG`, `TT_OVER_RR` — **verify 0 non-self at run time**), record chosen feature + grep cmd/hits/evidence in artifacts/state. Do **not** pick `LAM_OVER_DET` (known collision).

### Required C189 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C187–C188): `scripts/run_real_quote_volume_rqa_lavg_over_rr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T005205Z.json` (aadd225ddaf2bcc83cff6a1c41bb35105c7b8e651e994f152cedb2bb2a04d640), cite C188 OOS SHA efe782e49e1fa6219f05e424d1d9901a12e2cb020cd6d8d6f13d39cc7269ec4e. Emit `reports/real_quote_volume_rqa_lavg_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence). `strategy_id` must match family.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 189) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T005205Z.json` (aadd225ddaf2bcc83cff6a1c41bb35105c7b8e651e994f152cedb2bb2a04d640). Include prior + C189 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign189_execution_summary_<UTC>.json` listing **all new C189 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C189`, `next_campaign:C190`, latest registry/OOS sha+path, `oos_edge_proven` from emitted report, `c190_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C189, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C189 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAVG_OVER_RR|lavg_over_rr|rqa_ratio_lavg_over_rr|rqa_lavg_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C189 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C190 (MANDATORY after C189; HEAVY WORK)
C190 is not optional. After C189 artifacts/state are synced, preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C189 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c190_preselected`, then **execute C190** under the same deliverable/edge-rule template. **No status-only replies. No stop after status.** If C189 is blocked only by a collision, switch to a grep-zero fallback and continue — do not stall.
