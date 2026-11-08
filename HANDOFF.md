# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T025353Z, C195 COMPLETE/LOCKED, NEXT=C196 MANDATORY INITIAL TASK)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C195 LOCKED.**

## VERIFIED BASELINE (20261108T025136Z — current)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available (do not fabricate).
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C195 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_lam_over_div_ratio_shock_mr_costed_oos_20261108T025007Z.json`=a8b0d41e770bbe174f95b64c9874c902b74f2154b1ae5ff4c4a6e713097af2cd (`VOLUME_RQA_LAM_OVER_DIV_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T025136Z.json`=2529ebcb394caaa8d2480b16291d93263673ae97629f567126ab63f12321eec1. Registry `reports/strategy_edge_registry_20261108T025136Z.json`=e185079d39770b6cb8ae5b426d07f1459e585780bb513349478d5190749a2700 supersedes C194 6b2454d43d0d053426c40e25b4857f0383997fa83be2c861f3cee548f7d34c96. Script `scripts/run_real_quote_volume_rqa_lam_over_div_ratio_shock_mr_costed_oos.py`=a35fbe12cacb8289a7dc590506b2cca069f45fb000ea353b327d36cfe4476f0a. Summary `reports/campaign195_execution_summary_20261108T025136Z.json`=29e8012d68f4de59f8ac35de4261e9c202a0ab3897b0778362eb758dfce42e06. All SHAs verified from bytes 20261108T025136Z.
- Cross-asset OOS net sums (C195): fee0_slip0=-0.1235243399224849, fee5_slip5=-0.41252433992248516, fee10_slip10=-0.7015243399224853, fee20_slip20=-1.2795243399224852, fee40_slip40=-2.435524339922485 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T025136Z)
- C104–C195 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C195 LAM_OVER_DIV collision guard 0 non-self at run time. C196 ENTR_OVER_DIV grep 0 observed (20261108T025136Z); re-verify at C196 run time.

## INITIAL TASK — C196 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C196 now.** Produce **>= 3 NEW concrete C196 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_ENTR_OVER_DIV_RATIO_SHOCK_MR` — RQA ratio ENTR/DIV on delay-embedded log-volume returns. `ENTR` = Shannon entropy (nats) of the qualifying diagonal line length distribution: `p_k = n_k/sum_j n_j`, `ENTR = -sum_k p_k*ln(p_k)` over lengths `k>=l_min` with `n_k>0` (standard RQA ENTR). `DIV` = divergence = `1/L_MAX` where `L_MAX` = max qualifying diagonal line length `k>=l_min` excl LOI. `RATIO_ENTR_DIV = ENTR/DIV`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if ENTR undefined/non-finite/degenerate (<2 distinct qualifying lengths or entropy non-finite/non-positive), DIV/L_MAX invalid (no qualifying diagonal lines or `L_MAX<=0`/non-finite), ratio non-finite, or insufficient qualifying lines/points. Trailing/causal only. Pre-stated distinctness: ENTR/DIV pairing not used C125–C195; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'ENTR_OVER_DIV|entr_over_div|rqa_ratio_entr_over_div|rqa_entr_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C195, record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C196 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C195): `scripts/run_real_quote_volume_rqa_entr_over_div_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T025136Z.json` (e185079d39770b6cb8ae5b426d07f1459e585780bb513349478d5190749a2700), cite C195 OOS SHA a8b0d41e770bbe174f95b64c9874c902b74f2154b1ae5ff4c4a6e713097af2cd. Emit `reports/real_quote_volume_rqa_entr_over_div_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 196) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T025136Z.json` (e185079d39770b6cb8ae5b426d07f1459e585780bb513349478d5190749a2700). Include prior + C196 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign196_execution_summary_<UTC>.json` listing **all new C196 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C196`, `next_campaign:C197`, latest registry/OOS sha+path, `oos_edge_proven`, `c197_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C196, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C196 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'ENTR_OVER_DIV|entr_over_div|rqa_ratio_entr_over_div|rqa_entr_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C196 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml + HANDOFF.md
```

## NEXT FOCUS CAMPAIGN — C197 (MANDATORY after C196)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C196 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c197_preselected`, then **execute C197** under the same template. **No status-only replies. No stop after status.**
