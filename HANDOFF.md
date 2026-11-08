# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T132919Z, C104–C214 LOCKED — edge_claim NONE, C215 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C214 LOCKED (no reruns). C215 preselected and grep-zero — execute C215 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T132919Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C215.** C214 is complete on disk (VOLUME_RQA_RTE_OVER_MAXDIAGLINE_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=-0.4032316542058335, fee5=-0.6602316542058337, fee10=-0.9172316542058339, fee20=-1.4312316542058339, fee40=-2.4592316542058335 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C215 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T132919Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C212 DONE (verified on disk, SHAs from bytes):** OOS bd8b0f0f... (`reports/real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos_20261108T123534Z.json`, VOLUME_RQA_RTE_OVER_VAVG_RATIO_SHOCK_MR, edge_claim NONE). Registry 6ba3d270... (`reports/strategy_edge_registry_20261108T123534Z.json`).
- **C213 DONE (verified on disk, SHAs from bytes):** OOS a19284df... (`reports/real_quote_volume_rqa_rte_over_wmax_ratio_shock_mr_costed_oos_20261108T131955Z.json`, VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR, edge_claim NONE, oos_edge_proven false). Registry e27c5e46... (`reports/strategy_edge_registry_20261108T131955Z.json`). Script f22df79b... Summary 25293103...
- **C214 DONE (verified on disk, SHAs from bytes):**
  - OOS aa9b3e65dff9dbe1db3cde3ba1ce6885523ffbea1e0fcb664752f99364f7af6a (`reports/real_quote_volume_rqa_rte_over_maxdiagline_divergence_shock_mr_costed_oos_20261108T132919Z.json`, VOLUME_RQA_RTE_OVER_MAXDIAGLINE_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest ba6345035fcc0254402fd3e2b1b2fb3815a040c72d0e4396b4c7647955dfb8bb (`reports/real_feed_ingest_attempt_20261108T132919Z.json`).
  - Registry 684475cd6fec8116479f7436697ff09b5c01dea9a94632c89f4eaeb206a90ec8 (`reports/strategy_edge_registry_20261108T132919Z.json`) supersedes `reports/strategy_edge_registry_20261108T131955Z.json` (e27c5e46...).
  - Script 9c85f22aa445987e19984ea2cae41996663af3922aa5dfbc434a05004a98c903 (`scripts/run_real_quote_volume_rqa_rte_over_maxdiagline_divergence_shock_mr_costed_oos.py`).
  - Summary a4b12da3dd46b1626fc747f572730e25125665ba9b79bea1937a16b6f151bace (`reports/campaign214_execution_summary_20261108T132919Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_MAXDIAGLINE_DIVERGENCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T132919Z.json` (684475cd...). Latest OOS = C214 `aa9b3e65...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C214.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C215 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T132919Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_MAXVERTLINE_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / MAXVERTLINE_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy; MAXVERTLINE_DIVERGENCE = max vertical line length minus mean vertical line length over qualifying vertical runs l>=l_min, LOI/self excluded; fail-closed if denominator <=0/non-finite/undefined or insufficient vertical lines). Distinct from MAXDIAGLINE_DIVERGENCE(C214), WMAX(C213), VAVG(C212), diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168` (denominator divergence defined explicitly at run; fail-closed NaN/no-signal if RTE/MAXVERTLINE_DIVERGENCE/ratio undefined/non-finite/degenerate). Trailing/causal only.
**Fallback (grep-zero 20261108T132919Z):** `VOLUME_RQA_RTE_OVER_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` (0 hits). Pick only a distinct grep-zero candidate not used C125–C214.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_MAXVERTLINE_DIVERGENCE|rte_over_maxvertline_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C214 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C215 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_maxvertline_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C214. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T132919Z.json` (684475cd...), cite C214 OOS SHA `aa9b3e65dff9dbe1db3cde3ba1ce6885523ffbea1e0fcb664752f99364f7af6a`. Emit `reports/real_quote_volume_rqa_rte_over_maxvertline_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/MAXVERTLINE_DIVERGENCE.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 215). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T132919Z.json` (684475cd...). Include prior + all C215 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign215_execution_summary_<UTC>.json` listing **all new C215 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C215`, `next_campaign: C216`, latest registry/OOS sha+path, `oos_edge_proven`, `c216_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C215, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_MAXVERTLINE_DIVERGENCE|rte_over_maxvertline_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C215 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C216 (AUTO-QUEUED, HEAVY)
After C215 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C215, record in `state.yaml.c216_preselected`, and **execute C216 immediately** under same template. No status-only replies. No stop between campaigns.
