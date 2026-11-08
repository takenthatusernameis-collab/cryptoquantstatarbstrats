# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T024607Z, C194 COMPLETE/LOCKED, NEXT=C195 MANDATORY INITIAL TASK)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C194 LOCKED.**

## VERIFIED BASELINE (20261108T024607Z — current)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available (928 passed, 1 skipped observed earlier; do not fabricate).
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C194 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_rte_over_rr_ratio_shock_mr_costed_oos_20261108T024453Z.json`=d648afa35d9626670a2f133f326a5c266da0b5458c1537567652ebdd7760fdab (`VOLUME_RQA_RTE_OVER_RR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T024607Z.json`=314d9e27fe7a3b8c4accec8fc75d51367a29a4f6af9b7396c5ae1c383e6212b2. Registry `reports/strategy_edge_registry_20261108T024607Z.json`=6b2454d43d0d053426c40e25b4857f0383997fa83be2c861f3cee548f7d34c96 supersedes C193 7471b609d6fcab19362eb051e70e42e438021ab5b14dab23b59b0e530c970f4a. Script `scripts/run_real_quote_volume_rqa_rte_over_rr_ratio_shock_mr_costed_oos.py`=a5d553f4abd1369600fefc7f2ae43062de0a2a4dd702fc7033a3d5e47690beb2. Summary `reports/campaign194_execution_summary_20261108T024607Z.json`=728366a3229d63433ed3149e8c26ba06284c363800046a21bba46d335dd3302c. All SHAs verified from bytes 20261108T024607Z.
- Cross-asset OOS net sums (C194): fee0_slip0=0.5095580790225089, fee5_slip5=0.10055807902250857, fee10_slip10=-0.30844192097749146, fee20_slip20=-1.1264419209774912, fee40_slip40=-2.762441920977491 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T024607Z)
- C104–C194 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C194 RTE_OVER_RR collision guard 0 non-self at run time (20261108T024207Z). C195 LAM_OVER_DIV grep 0 observed (20261108T024607Z); re-verify at C195 run time.

## INITIAL TASK — C195 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C195 now.** Produce **>= 3 NEW concrete C195 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_LAM_OVER_DIV_RATIO_SHOCK_MR` — RQA ratio LAM/DIV on delay-embedded log-volume returns. `LAM` = laminarity = fraction of recurrence points forming vertical lines of length >= v_min (pre-stated `v_min=2`), excluding trivial points. `DIV` = divergence = `1/L_MAX` where `L_MAX` = max qualifying diagonal line length `k>=l_min` excl LOI. `RATIO_LAM_DIV = LAM/DIV`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,v_min=2`. **Fail-closed NaN/no-signal** if `LAM` undefined/non-finite/degenerate, `DIV/L_MAX` invalid (L_MAX<=0/non-finite), ratio non-finite, or insufficient qualifying lines/points. Trailing/causal only. Pre-stated distinctness: LAM/DIV pairing not used C125–C194; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAM_OVER_DIV|lam_over_div|rqa_ratio_lam_over_div|rqa_lam_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C195, record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C195 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C194): `scripts/run_real_quote_volume_rqa_lam_over_div_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T024607Z.json` (6b2454d43d0d053426c40e25b4857f0383997fa83be2c861f3cee548f7d34c96), cite C194 OOS SHA d648afa35d9626670a2f133f326a5c266da0b5458c1537567652ebdd7760fdab. Emit `reports/real_quote_volume_rqa_lam_over_div_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 195) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T024607Z.json` (6b2454d43d0d053426c40e25b4857f0383997fa83be2c861f3cee548f7d34c96). Include prior + C195 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign195_execution_summary_<UTC>.json` listing **all new C195 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C195`, `next_campaign:C196`, latest registry/OOS sha+path, `oos_edge_proven`, `c196_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C195, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C195 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAM_OVER_DIV|lam_over_div|rqa_ratio_lam_over_div|rqa_lam_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C195 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml + HANDOFF.md
```

## NEXT FOCUS CAMPAIGN — C196 (MANDATORY after C195)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C195 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c196_preselected`, then **execute C196** under the same template. **No status-only replies. No stop after status.**
