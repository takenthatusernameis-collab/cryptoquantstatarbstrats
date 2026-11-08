# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T103205Z, C204 DONE, C205 DONE, C206 DONE, C207 DONE — edge_claim NONE, C208 AUTO-QUEUED HEAVY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C207 LOCKED (no reruns). C208 preselected, grep-zero to be re-verified at run — execute C208 immediately, no status-first, no stop between campaigns.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T103205Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C208 NOW.** C207 complete (VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.26628127869299845, fee5=+0.06028127869299828, fee10=-0.14571872130700184, fee20=-0.5577187213070018, fee40=-1.3817187213070017 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C208 artifacts do NOT yet exist on disk — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C208 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 208)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

C208 preselect: **VOLUME_RQA_RTE_OVER_LAVG_RATIO_SHOCK_MR** (fallback: VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR) — must be a **distinct grep-verified** RQA-ratio candidate not used C125–C207. Run collision guard at start; pick only a grep-zero candidate; record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

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
- **C207 DONE (verified on disk, SHAs from bytes):**
  - OOS 41890be468f48f1fe71cf8c9e758cfb8a7afa7d8b32a669740ccacee626c09c8 (`reports/real_quote_volume_rqa_rte_over_vmax_ratio_shock_mr_costed_oos_20261108T103205Z.json`, VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest 8e3c95120b71ba34f379a11d3d61958579e49782d6f1c3f1a8a64ed337d240ec (`reports/real_feed_ingest_attempt_20261108T103205Z.json`).
  - Registry e69a4090e7c768436049a6d880d7d16a946eb305aa651898e0a59d72a637ff45 (`reports/strategy_edge_registry_20261108T103205Z.json`) supersedes C206 d061ab66a0126c1ef248959c1ff6e1d86b07b88e5562b366d52a5829ed38b75a.
  - Script 7cf8c85c6c99725472f3560aa9b2c2ac9255612a9beb2c8b92bfe3e845588aeb (`scripts/run_real_quote_volume_rqa_rte_over_vmax_ratio_shock_mr_costed_oos.py`).
  - Summary eaa4a7d4c96df43a0b81ff6a744496db4577a06959207836f00eb07e913df5e7 (`reports/campaign207_execution_summary_20261108T103205Z.json`).
  - C207 cross-asset OOS net sums: fee0_slip0=0.26628127869299845, fee5_slip5=0.06028127869299828, fee10_slip10=-0.14571872130700184, fee20_slip20=-0.5577187213070018, fee40_slip40=-1.3817187213070017 → **edge NOT proven**; any_exposure_oos=true. Distinctness grep 0 non-self at run time.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C207.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C208 now. No status-only replies. No stop between campaigns.

## C208 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO TO BE VERIFIED AT RUN)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio RTE/LAVG on delay-embedded log-volume returns (LAVG denominator distinct from VMAX used C207, TT used C205, TREND used C206). Params: m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2. Fail-closed NaN/no-signal if RTE/LAVG/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallback (verify at run):** `VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR` (grep 0 observed at selection; re-verify). Pick only a distinct grep-zero fallback not used C125–C207.
**Collision guard (RUN AT START):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_LAVG|rte_over_lavg|rqa_ratio_rte_over_lavg|rqa_rte_over_lavg_ratio|RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C207 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C208 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C207. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T103205Z.json` (e69a4090e7c768436049a6d880d7d16a946eb305aa651898e0a59d72a637ff45), cite C207 OOS SHA `41890be468f48f1fe71cf8c9e758cfb8a7afa7d8b32a669740ccacee626c09c8`. Emit `reports/real_quote_volume_rqa_rte_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. Avoid carryover template text: campaign/refs/denominator labels must match RTE/LAVG.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 208). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T103205Z.json` (e69a4090e7c768436049a6d880d7d16a946eb305aa651898e0a59d72a637ff45). Include prior + all C208 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign208_execution_summary_<UTC>.json` listing **all new C208 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C208`, `next_campaign: C209`, latest registry/OOS sha+path, `oos_edge_proven`, `c209_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C208, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_LAVG|rte_over_lavg|rqa_ratio_rte_over_lavg|rqa_rte_over_lavg_ratio|RTE_OVER_LMAX|rte_over_lmax|rqa_ratio_rte_over_lmax|rqa_rte_over_lmax_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self for chosen candidate
# NOW: implement+run C208 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C209 (AUTO-QUEUED, HEAVY)
After C208 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C208 (verify). Record in `state.yaml.c209_preselected` and **execute C209 immediately** under same template. No status-only replies. No stop between campaigns.
