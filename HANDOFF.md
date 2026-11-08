# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T102842Z, C204 DONE, C205 DONE, C206 DONE — edge_claim NONE, C207 AUTO-QUEUED HEAVY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C206 LOCKED (no reruns). C207 preselected, grep-zero observed 20261108T045258Z (re-verify at run) — execute C207 immediately, no status-first, no stop between campaigns.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T102842Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C207 NOW.** C206 complete (VOLUME_RQA_RTE_OVER_TREND_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+1.0930684191547377, fee5=+0.7580684191547373, fee10=+0.42306841915473725, fee20=-0.24693158084526265, fee40=-1.5869315808452626 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C207 artifacts do NOT yet exist on disk — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C207 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 207)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

C207 preselect: **VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR** (fallback: VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR) — must be a **distinct grep-verified** RQA-ratio candidate not used C125–C206. Run collision guard at start; pick only a grep-zero candidate; record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## VERIFIED BASELINE (20261108T102842Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C204 LOCKED (verified on disk, SHAs from bytes):**
  - OOS e0dd9dc9012b2c75ec8e9b6c0b903bc7445e9b0d1932f2e43969acd75faf032c (`reports/real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos_20261108T091806Z.json`, VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR, edge_claim NONE).
  - Script b2643c015809a2815f299e71cfa1d7ae64ec958b91a7b85d9db4bcb5401eb675 (`scripts/run_real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos.py`).
  - C204 cross-asset OOS net sums: fee0=0.72458166, fee5=0.35858166, fee10=-0.00741834, fee20=-0.73941834, fee40=-2.20341834 → **edge NOT proven**.
- **C205 DONE (verified on disk, SHAs from bytes):**
  - OOS 75cafee2308e6c2f37e2f96f08753ac59a2f88e9c0704b27acccd6f243f3fb44 (`reports/real_quote_volume_rqa_rte_over_tt_ratio_shock_mr_costed_oos_20261108T101655Z.json`, VOLUME_RQA_RTE_OVER_TT_RATIO_SHOCK_MR, edge_claim NONE).
  - Script f63db56228c792de7e72f84d817976021bfc2f3f22d2935cb4e699325545e5b5 (`scripts/run_real_quote_volume_rqa_rte_over_tt_ratio_shock_mr_costed_oos.py`).
  - C205 cross-asset OOS net sums: fee0_slip0=0.7819609868750175, fee5_slip5=0.4829609868750172, fee10_slip10=0.1839609868750172, fee20_slip20=-0.41403901312498287, fee40_slip40=-1.6100390131249827 → **edge NOT proven**.
- **C206 DONE (verified on disk, SHAs from bytes):**
  - OOS 03d77e679c417b128d5d793f86961a45f820ae38840547910eda655ec5aa7058 (`reports/real_quote_volume_rqa_rte_over_trend_ratio_shock_mr_costed_oos_20261108T102523Z.json`, VOLUME_RQA_RTE_OVER_TREND_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest 3296884ee715193f235f1e84b2a162a5017e44b2af754abcbb8c867f947a7823 (`reports/real_feed_ingest_attempt_20261108T102523Z.json`).
  - Registry d061ab66a0126c1ef248959c1ff6e1d86b07b88e5562b366d52a5829ed38b75a (`reports/strategy_edge_registry_20261108T102523Z.json`) supersedes C205 0ac163a703bddc32c1681c1fe7d33cb59a15bb306ebbba9ccdd7235f32492832.
  - Script df54a9bc92fa9f8956492615c3aad0f98bb5ff27debc7ee9c4492802357711cb (`scripts/run_real_quote_volume_rqa_rte_over_trend_ratio_shock_mr_costed_oos.py`).
  - Summary 46eac8b62b2317ef60991f8cce5013cd2133fe350bcf45d4e352010144609d1d (`reports/campaign206_execution_summary_20261108T102523Z.json`).
  - C206 cross-asset OOS net sums: fee0_slip0=1.0930684191547377, fee5_slip5=0.7580684191547373, fee10_slip10=0.42306841915473725, fee20_slip20=-0.24693158084526265, fee40_slip40=-1.5869315808452626 → **edge NOT proven**; any_exposure_oos=true. Distinctness grep 0 non-self at run time.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C206.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C207 now. No status-only replies. No stop between campaigns.

## C207 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO OBSERVED 20261108T045258Z; RUN-TIME RE-VERIFY REQUIRED)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio RTE/VMAX on delay-embedded log-volume returns (VMAX denominator distinct from TT used C205 and TREND used C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1. Fail-closed NaN/no-signal if RTE/VMAX/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallback (verify at run):** `VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR` (grep 0 observed 20261108T045258Z; re-verify). Pick only a distinct grep-zero RQA-ratio candidate not used C125–C206.
**Collision guard (RUN AT START):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_VMAX|rte_over_vmax|rqa_ratio_rte_over_vmax|rqa_rte_over_vmax_ratio|RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C206 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C207 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C206. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T102523Z.json` (d061ab66a0126c1ef248959c1ff6e1d86b07b88e5562b366d52a5829ed38b75a), cite C206 OOS SHA `03d77e679c417b128d5d793f86961a45f820ae38840547910eda655ec5aa7058`. Emit `reports/real_quote_volume_rqa_rte_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. Avoid carryover template text: campaign/refs/denominator labels must match RTE/VMAX.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 207). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T102523Z.json` (d061ab66a0126c1ef248959c1ff6e1d86b07b88e5562b366d52a5829ed38b75a). Include prior + all C207 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign207_execution_summary_<UTC>.json` listing **all new C207 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C207`, `next_campaign: C208`, latest registry/OOS sha+path, `oos_edge_proven`, `c208_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C207, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_VMAX|rte_over_vmax|rqa_ratio_rte_over_vmax|rqa_rte_over_vmax_ratio|RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self for chosen candidate
# NOW: implement+run C207 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C208 (AUTO-QUEUED, HEAVY)
After C207 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C207 (verify). Record in `state.yaml.c208_preselected` and **execute C208 immediately** under same template. No status-only replies. No stop between campaigns.
