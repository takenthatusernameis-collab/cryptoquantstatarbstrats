# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T121953Z, C204–C210 LOCKED — edge_claim NONE, C211 AUTO-QUEUED HEAVY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C209 LOCKED (no reruns). C210 preselected, grep-zero to be re-verified at run — execute C210 immediately, no status-first, no stop between campaigns.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T113012Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C210 NOW.** C209 complete (VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.26628127869299845, fee5=+0.06028127869299828, fee10=-0.14571872130700184, fee20=-0.5577187213070018, fee40=-1.3817187213070017 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C210 artifacts do NOT exist — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C210 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 210)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

C210 preselect: **VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR** (fallback: VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR) — must be a **distinct grep-verified** RQA-ratio candidate not used C125–C209. Metric: RQA ratio RTE/WAVG on delay-embedded log-volume returns (WAVG = mean white vertical line length / mean recurrence-time gap length, distinct from LMAX max vertical line length used C209, LAVG mean vertical line length used C208, VMAX max black vertical line used C207, TT C205, TREND C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2. Fail-closed NaN/no-signal if RTE/WAVG/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only. Run collision guard at start; pick only a grep-zero candidate; record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## VERIFIED BASELINE (20261108T113012Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C209 DONE (verified on disk, SHAs from bytes):**
  - OOS 5421892e2efe996d1af52835be9174d8b88b62cdab3cd6bd2e6e5041da5420be (`reports/real_quote_volume_rqa_rte_over_lmax_ratio_shock_mr_costed_oos_20261108T113012Z.json`, VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest 72e4ad30b77d7402f4f05a29608608d0b39eff65959a1933345cf032a81d00e0 (`reports/real_feed_ingest_attempt_20261108T113012Z.json`).
  - Registry 0b66773ab515bb51a32908e5d52caa56ef96a523f49aaf6a95e05f234ef7c5c1 (`reports/strategy_edge_registry_20261108T113012Z.json`) supersedes C208 b398c199ac0a478aa5c8814c7cc36b0f0f7002f782e205435405ba47352612e3.
  - Script 96ab74a7fe395b42bc7501c8e393887d381d68dedc5ef37e0ddc049ff92fe0e5 (`scripts/run_real_quote_volume_rqa_rte_over_lmax_ratio_shock_mr_costed_oos.py`).
  - Summary 78644f995aacf6b4eb6af18cea6cfa55df019c73084839cc24e0ae4bb9c03214 (`reports/campaign209_execution_summary_20261108T113012Z.json`).
  - C209 cross-asset OOS net sums: fee0_slip0=0.26628127869299845, fee5_slip5=0.06028127869299828, fee10_slip10=-0.14571872130700184, fee20_slip20=-0.5577187213070018, fee40_slip40=-1.3817187213070017 → **edge NOT proven** (fee10/fee20/fee40 negative); any_exposure_oos=true. Distinctness grep 0 non-self at run time.
- **C208 DONE (verified on disk, SHAs from bytes):**
  - OOS c5f181d3af540d8ff000ee77139711ed38aef9e4be5d3edea90537e9e2519ffa (`reports/real_quote_volume_rqa_rte_over_lavg_ratio_shock_mr_costed_oos_20261108T111915Z.json`, VOLUME_RQA_RTE_OVER_LAVG_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest 680c245084c9fddb3a6446b37a7d6adb1badbb05633b178beec68a2b5cee853c (`reports/real_feed_ingest_attempt_20261108T111915Z.json`).
  - Registry b398c199ac0a478aa5c8814c7cc36b0f0f7002f782e205435405ba47352612e3 (`reports/strategy_edge_registry_20261108T111915Z.json`) supersedes C207 e69a4090e7c768436049a6d880d7d16a946eb305aa651898e0a59d72a637ff45.
  - Script 6854366e8229a1d363274a2c6297648b1a27e348eb9493d20286ecb580f8b29a (`scripts/run_real_quote_volume_rqa_rte_over_lavg_ratio_shock_mr_costed_oos.py`).
  - Summary f66bb88d38347413dbae3afc4eb786f60d7f4f21caea9c864024f000e6197718 (`reports/campaign208_execution_summary_20261108T111915Z.json`).
  - C208 cross-asset OOS net sums: fee0_slip0=0.7819609868750175, fee5_slip5=0.4829609868750172, fee10_slip10=0.1839609868750172, fee20_slip20=-0.41403901312498287, fee40_slip40=-1.6100390131249827 → **edge NOT proven** (fee20/fee40 negative); any_exposure_oos=true. Distinctness grep 0 non-self at run time.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C209.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C210 now. No status-only replies. No stop between campaigns.

## C210 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO TO BE VERIFIED AT RUN)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR` — RQA ratio RTE/WAVG on delay-embedded log-volume returns (WAVG = mean white vertical line length / mean recurrence-time gap length; distinct from LMAX max vertical line length used C209, LAVG mean vertical line length used C208, VMAX max black vertical line used C207, TT used C205, TREND used C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2. Fail-closed NaN/no-signal if RTE/WAVG/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallback (verify at run):** `VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR` (grep 0 observed preflight; re-verify). Pick only a distinct grep-zero fallback not used C125–C209.
**Collision guard (RUN AT START):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_WAVG|rte_over_wavg|rqa_ratio_rte_over_wavg|rqa_rte_over_wavg_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C209 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C210 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_wavg_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C209. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T113012Z.json` (0b66773ab515bb51a32908e5d52caa56ef96a523f49aaf6a95e05f234ef7c5c1), cite C209 OOS SHA `5421892e2efe996d1af52835be9174d8b88b62cdab3cd6bd2e6e5041da5420be`. Emit `reports/real_quote_volume_rqa_rte_over_wavg_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. Avoid carryover template text: campaign/refs/denominator labels must match RTE/WAVG.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 210). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T113012Z.json` (0b66773ab515bb51a32908e5d52caa56ef96a523f49aaf6a95e05f234ef7c5c1). Include prior + all C210 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign210_execution_summary_<UTC>.json` listing **all new C210 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C210`, `next_campaign: C211`, latest registry/OOS sha+path, `oos_edge_proven`, `c211_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C210, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WAVG|rte_over_wavg|rqa_ratio_rte_over_wavg|rqa_rte_over_wavg_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self for chosen candidate
# NOW: implement+run C210 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C211 (AUTO-QUEUED, HEAVY)
After C210 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C210 (verify). Record in `state.yaml.c211_preselected` and **execute C211 immediately** under same template. No status-only replies. No stop between campaigns.
