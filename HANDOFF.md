# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T111915Z, C204–C208 LOCKED — edge_claim NONE, C209 AUTO-QUEUED HEAVY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C208 LOCKED (no reruns). C209 preselected, grep-zero to be re-verified at run — execute C209 immediately, no status-first, no stop between campaigns.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T111915Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C209 NOW.** C208 complete (VOLUME_RQA_RTE_OVER_LAVG_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.7819609868750175, fee5=+0.4829609868750172, fee10=+0.1839609868750172, fee20=-0.41403901312498287, fee40=-1.6100390131249827 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C209 artifacts do NOT exist — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C209 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 209)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

C209 preselect: **VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR** (fallbacks: VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR, VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR) — must be a **distinct grep-verified** RQA-ratio candidate not used C125–C208. Metric: RQA ratio RTE/LMAX on delay-embedded log-volume returns (LMAX = max white vertical line / recurrence-time gap length, distinct from LAVG mean used C208, VMAX max black vertical line used C207, TT C205, TREND C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2. Fail-closed NaN/no-signal if RTE/LMAX/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only. Run collision guard at start; pick only a grep-zero candidate; record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## VERIFIED BASELINE (20261108T111915Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
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
- **No reruns of locked campaigns C104–C208.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C209 now. No status-only replies. No stop between campaigns.

## C209 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO TO BE VERIFIED AT RUN)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio RTE/LMAX on delay-embedded log-volume returns (LMAX = max white vertical line / recurrence-time gap length; distinct from LAVG mean used C208, VMAX max black vertical line used C207, TT used C205, TREND used C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2. Fail-closed NaN/no-signal if RTE/LMAX/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallbacks (verify at run):** `VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR` (grep 0 observed preflight for LMAX; re-verify). Pick only a distinct grep-zero fallback not used C125–C208.
**Collision guard (RUN AT START):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C208 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C209 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_lmax_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C208. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T111915Z.json` (b398c199ac0a478aa5c8814c7cc36b0f0f7002f782e205435405ba47352612e3), cite C208 OOS SHA `c5f181d3af540d8ff000ee77139711ed38aef9e4be5d3edea90537e9e2519ffa`. Emit `reports/real_quote_volume_rqa_rte_over_lmax_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. Avoid carryover template text: campaign/refs/denominator labels must match RTE/LMAX.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 209). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T111915Z.json` (b398c199ac0a478aa5c8814c7cc36b0f0f7002f782e205435405ba47352612e3). Include prior + all C209 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign209_execution_summary_<UTC>.json` listing **all new C209 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C209`, `next_campaign: C210`, latest registry/OOS sha+path, `oos_edge_proven`, `c210_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C209, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self for chosen candidate
# NOW: implement+run C209 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C210 (AUTO-QUEUED, HEAVY)
After C209 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C209 (verify). Record in `state.yaml.c210_preselected` and **execute C210 immediately** under same template. No status-only replies. No stop between campaigns.
