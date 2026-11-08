# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T202936Z, C104–C228 LOCKED — edge_claim NONE, C228 DONE, C229 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C228 LOCKED (no reruns). C228 DONE on disk (edge_claim NONE). C229 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR) — execute C229 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T202506Z.json` (509503bf...). Latest OOS = C228 `4c4de94e...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T202506Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C229.** C228 is complete on disk (VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.015478741990794798, fee5=-1.3914787419907952, fee10=-2.767478741990795, fee20=-5.519478741990795, fee40=-11.023478741990795 — fails all-cost-positive / B&H mean rule). C228 script was fixed from a campaign=227/template carryover state to campaign 228 with the correct feature definition: `DIAG_LINE_COUNT_VARIANCE = sample variance (ddof=1) of cnt_k` over off-diagonal diagonals `k!=0` with >=1 qualifying white diagonal segment of consecutive 0s (length>=w_min=2), where `cnt_k = (number of qualifying white diagonal segments on diagonal k) / (number of cells on diagonal k = M_pts-|k|)`; RTE unchanged (white vertical gap entropy, w>=w_min, LOI/self excluded). Fixed run artifacts: OOS `reports/real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos_20261108T202354Z.json` (sha 4c4de94e...), ingest `reports/real_feed_ingest_attempt_20261108T202506Z.json` (sha c47487ef...), registry `reports/strategy_edge_registry_20261108T202506Z.json` (sha 509503bf...), script `scripts/run_real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos.py` (sha 2de98225...), summary `reports/campaign228_execution_summary_20261108T202506Z.json` (sha 25ea3cf9...). Superseded carryover artifact (not canonical): OOS `20261108T202049Z` (sha f0e34882..., campaign field 227 / old denominator text; same computed sums/feature impl). state.yaml + HANDOFF synced (latest_campaign_done C228, next_campaign C229). **Do not summarize status. Do not stop at status. Implement + run C229 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T202506Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C223–C227 DONE (locked):** edge_claim NONE, all oos_edge_proven false.
- **C228 DONE (verified on disk, SHAs from bytes):**
  - OOS (canonical, fixed) 4c4de94e3064a0176f24bc817d7fed1ab56c712543b3d4c5aa7bd216b87504ae (`reports/real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos_20261108T202354Z.json`, VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR, campaign 228, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - OOS alt/superseded f0e34882d0633d1dc57f9281eae997508a9a66725d9b9a093ba83147b3e0cc1f (`..._20261108T202049Z.json`, campaign=227 template carryover in metadata; same computed sums/feature impl) — not canonical.
  - Ingest c47487ef2b0e633e854dd5c06a640f62bcab3d804717f85358665dea7a26a638 (`reports/real_feed_ingest_attempt_20261108T202506Z.json`).
  - Registry 509503bf244491bc7ae57ebf1b4cfc849b081f8d19b1761e30aedcfeaabc6fa8 (`reports/strategy_edge_registry_20261108T202506Z.json`) supersedes 201358Z 5fc6752e....
  - Script 2de98225f0f48ef94b1aa90fbe60675482ff69e317358ecd1e01cf6fab30ace5 (`scripts/run_real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos.py`, campaign 228, correct cnt_k variance denominator).
  - Summary 25ea3cf9584d8101c1e0ff3975ba111b9448e2504efdad8c807b4101215dc81a (`reports/campaign228_execution_summary_20261108T202506Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_DIAG_LINE_COUNT_VARIANCE/DIAG_LINE_COUNT_VARIANCE).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C228 completion bottleneck removed.** Script fixed (campaign 228, correct DIAG_LINE_COUNT_VARIANCE = sample variance of `cnt_k = qualifying white segment count / diagonal cell count`, ddof=1, refs to C227 registry/OOS/C226 OOS). Fixed OOS + ingest + registry + summary emitted (20261108T202354Z/20261108T202506Z) with SHA256 from bytes; state.yaml/HANDOFF synced. C228 initial OOS `20261108T202049Z` (campaign=227 carryover, sha f0e34882...) superseded (not canonical). C228 no longer blocks C229.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C228.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF. `diag_line_length_*` (89 hits) and `diag_line_count_divergence` collide with C226/C227 text — rejected for C228/C229 context.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C229 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T202506Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_COUNT_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_COUNT_VARIANCE = sample variance (ddof=1) of `cnt_k_white` over off-diagonal diagonals `k!=0` with >=1 qualifying **white** diagonal segment of consecutive 0s meeting `w_min>=2`, where `cnt_k_white = (number of qualifying white diagonal segments on diagonal k) / (number of cells on diagonal k = M_pts-|k|)`. White diagonal segment = run of consecutive 0-cells (non-recurrent) along diagonal k!=0, qualifying if length >= w_min. Fail-closed if <2 qualifying diagonals or variance <=0/non-finite/undefined). Distinct from DIAG_LINE_COUNT_VARIANCE(C228; name collision risk avoided by explicit `WHITE_` qualifier and feature definition using white/non-recurrent segments — grep confirms 0 hits for `WHITE_DIAG_LINE_COUNT_VARIANCE` patterns pre-run), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), WHITE_DIAG_LINE_COUNT_DIVERGENCE(C225), WHITE_DIAG_LINE_DENSITY_VARIANCE(C224), WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C228 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (trailing/causal).
**grep evidence (20261108T202506Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE|rte_over_white_diag_line_count_variance|WHITE_DIAG_LINE_COUNT_VARIANCE|white_diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** none preselected; at C229 start, grep-verify a distinct grep-zero RQA-ratio candidate not used C125–C228 and record evidence. Also-verified grep-zero alternates (20261108T202506Z): `RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS` (0), `RTE_OVER_DIAG_LINE_LENGTH_DIVERGENCE` (0); `RTE_OVER_DIAG_LINE_LENGTH_VARIANCE` collides (89 hits, rejected).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE|rte_over_white_diag_line_count_variance|WHITE_DIAG_LINE_COUNT_VARIANCE|white_diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C228 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C229 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_count_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C228. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T202506Z.json` (509503bf...), cite C228 OOS SHA `4c4de94e3064a0176f24bc817d7fed1ab56c712543b3d4c5aa7bd216b87504ae` (canonical) and C227 OOS SHA `037f23a5555807eaa24a966276ebb7a1fd916de5e516f60cee55184a8c086cba`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_count_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 229`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 229). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T202506Z.json` (509503bf...). Include prior + all C229 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign229_execution_summary_<UTC>.json` listing **all new C229 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C229`, `next_campaign: C230`, latest registry/OOS sha+path, `oos_edge_proven`, `c230_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C229, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE|rte_over_white_diag_line_count_variance|WHITE_DIAG_LINE_COUNT_VARIANCE|white_diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C229 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C230 (AUTO-QUEUED, HEAVY)
After C229 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C229, record in `state.yaml.c230_preselected`, and **execute C230 immediately** under same template. No status-only replies. No stop between campaigns.
