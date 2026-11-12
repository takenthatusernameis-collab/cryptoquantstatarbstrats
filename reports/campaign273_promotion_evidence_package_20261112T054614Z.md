# C273 Promotion Evidence Package (20261112T054614Z)

- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR`
- Edge claim: **CONDITIONAL_EDGE_PROVEN** | `oos_edge_proven=True` | Readiness: **READY_FOR_REVIEW**
- Edge rule: oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same OOS windows.

## Baseline (real cached data, WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]])
- Cross-asset OOS net sums: {"fee0_slip0": 80.68391844301627, "fee5_slip5": 79.42291844301636, "fee10_slip10": 78.16191844301629, "fee20_slip20": 75.63991844301627, "fee40_slip40": 70.59591844301625}
- Distinctness grep hits (non-self): 0
- Compliance flags: {"oos_edge_proven": true, "any_exposure_oos": true, "all_cost_slices_positive_oos_net_sum": true, "all_cost_slices_beat_bh_mean_rule": true, "compliant_with_saved_flags": true}

## Verification / Replication
- Deterministic verification passed: **True** (`reports/campaign273_verification_20261112T051659Z.json`, sha256 `42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229`)
- Split-decomposition replication matches C273: **True** (diffs: {"fee0_slip0": 0.0, "fee5_slip5": 0.0, "fee10_slip10": 1.4210854715202004e-14, "fee20_slip20": 1.4210854715202004e-14, "fee40_slip40": 1.4210854715202004e-14}, `reports/campaign273_split_decomposition_20261112T052106Z.json`, sha256 `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`)

## Stability / Sensitivity
- Robustness dossier: CONDITIONAL_EDGE_VERIFIED_BUT_REQUIRES_HARDENING_REVIEW | flags: ["some_assets_nonpositive_at_fee0", "not_all_assets_positive_in_every_cost_slice"]
- Split stats (fee0): positive 16/24 (0.6666666666666666), assets positive net fee0 9/11, cross-asset positive all cost slices recomputed=True
- Parameter sensitivity: **robust_neighborhood** — edge-positive 21/27 (0.7777777777777778), all-cost-positive 21/27, baseline reproduced=True
- Failing combos (6), all at W_RR=192: [{"params": {"W_RR": 192, "ENTRY_Z": 1.25, "EXIT_Z": 0.25}, "fee40_slip40": -23.068169522391372, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}, {"params": {"W_RR": 192, "ENTRY_Z": 1.25, "EXIT_Z": 0.5}, "fee40_slip40": -23.068169522391372, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}, {"params": {"W_RR": 192, "ENTRY_Z": 1.25, "EXIT_Z": 0.75}, "fee40_slip40": -23.068169522391372, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}, {"params": {"W_RR": 192, "ENTRY_Z": 1.5, "EXIT_Z": 0.25}, "fee40_slip40": -44.7833781134085, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}, {"params": {"W_RR": 192, "ENTRY_Z": 1.5, "EXIT_Z": 0.5}, "fee40_slip40": -44.7833781134085, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}, {"params": {"W_RR": 192, "ENTRY_Z": 1.5, "EXIT_Z": 0.75}, "fee40_slip40": -44.7833781134085, "all_cost_slices_positive_oos_net_sum": false, "all_cost_slices_beat_bh_mean_rule": false}]

## Risks and Caveats
- Fragility flags from robustness dossier: some_assets_nonpositive_at_fee0; not_all_assets_positive_in_every_cost_slice (cross-asset edge positive but not uniform across all assets/cost slices).
- Split stability: fee0 cross-asset positive splits 16/24 (66.67%), 8/24 negative splits (min -12.116630665422184, max 27.10148575154885, mean 3.361829935125678); assets positive net at fee0 9/11.
- Parameter sensitivity: 21/27 combos edge-positive overall, but 6/27 fail edge rule — all failures at W_RR=192 (ENTRY_Z 1.25 with EXIT_Z 0.25/0.5/0.75 and ENTRY_Z 1.5 with EXIT_Z 0.25/0.5/0.75) due to fee40/high-cost negativity and BH-beat failure (e.g. fee40 nets -23.068169522391372 and -44.7833781134085). Baseline W_RR=168/ENTRY_Z=1.5/EXIT_Z=0.5 reproduced.
- Evidence is real-cached-data OOS on fixed WF/cost framework; no live/refetched/synthetic validation and no out-of-sample beyond cached history.

## Artifact Manifest (SHA256 from bytes)
- `oos`: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` — sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf` (expected `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`, ok=True)
- `script`: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py` — sha256 `4d91581133c6ca5a8613c644f137f2c24bf5fefa0d1086d2d735d85d813a117e` (expected `4d91581133c6ca5a8613c644f137f2c24bf5fefa0d1086d2d735d85d813a117e`, ok=True)
- `ingest`: `reports/real_feed_ingest_attempt_20261112T051504Z.json` — sha256 `dd704efab8d6c3650e5c872f0b8b3462185e960b136382ea260e139370d70446` (expected `dd704efab8d6c3650e5c872f0b8b3462185e960b136382ea260e139370d70446`, ok=True)
- `registry`: `reports/strategy_edge_registry_20261112T051504Z.json` — sha256 `7fb2ceeaccbb2c8499e5d8203479c7c9c309f41acd57ccc2c5e5685308b7c6b6` (expected `7fb2ceeaccbb2c8499e5d8203479c7c9c309f41acd57ccc2c5e5685308b7c6b6`, ok=True)
- `summary`: `reports/campaign273_execution_summary_20261112T051504Z.json` — sha256 `d2694387c152b6659a041dd946fda79de415d9d1747bac447418c090cae153dd` (expected `d2694387c152b6659a041dd946fda79de415d9d1747bac447418c090cae153dd`, ok=True)
- `verification_script`: `scripts/verify_c273_percentile_spread_edge.py` — sha256 `fde5d4fe45f1d3ac5c316a640b11d4f03e352765141bb28aeaad99794bc9e1e0` (expected `None`, ok=True)
- `verification`: `reports/campaign273_verification_20261112T051659Z.json` — sha256 `42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229` (expected `42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229`, ok=True)
- `robustness`: `reports/campaign273_robustness_dossier_20261112T051659Z.json` — sha256 `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6` (expected `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`, ok=True)
- `split_script`: `scripts/run_c273_percentile_spread_split_decomposition.py` — sha256 `21059d45026d8ba09362526f9ec6b5fe810fc5a7c70d7d64f98efc695a9f5d11` (expected `None`, ok=True)
- `split_decomposition`: `reports/campaign273_split_decomposition_20261112T052106Z.json` — sha256 `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d` (expected `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`, ok=True)
- `sensitivity_script`: `scripts/run_c273_percentile_spread_param_sensitivity.py` — sha256 `73832091f61282a3e1d2199284ba5af3fd79d1df66a1a512e9ea65a2c2252d98` (expected `73832091f61282a3e1d2199284ba5af3fd79d1df66a1a512e9ea65a2c2252d98`, ok=True)
- `sensitivity`: `reports/campaign273_param_sensitivity_20261112T052846Z.json` — sha256 `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d` (expected `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`, ok=True)

## Promotion Readiness
- **READY_FOR_REVIEW**
- All required artifacts present with matching/pinned hashes (where expected), verification passed, replication matched, and parameter sensitivity shows robust neighborhood (21/27 = 77.78%) with baseline reproduced. Risks/non-uniformities and W_RR=192 failures are explicitly documented for reviewer judgment.

## Reproduction (real cached data only, no refetch)
- Core run: `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py`
- Verification: `python3 scripts/verify_c273_percentile_spread_edge.py`
- Split decomposition: `python3 scripts/run_c273_percentile_spread_split_decomposition.py`
- Param sensitivity: `python3 scripts/run_c273_percentile_spread_param_sensitivity.py`
- Package build: `python3 scripts/build_c273_promotion_evidence_package.py`
