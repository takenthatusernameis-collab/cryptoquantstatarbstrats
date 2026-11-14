# Program Closure Final — cryptoquantstatarbstrats

Generated at: `20261114T205712Z`

## Closure verdict

- `reachable_real_data_cross_sectional_stat_arb_space`: **CLOSED**
- `real_data_only`: true
- `fabricated_data`: false
- `executed_fills`: false
- `edge_claim`: NONE
- `oos_edge_proven`: false
- `zero_tradable_edge_registry_confirmed`: true
- `no_new_data_sources`: true
- `total_costed_oos_edge_proven`: 0

## Program closure

- `status`: recorded
- `as_of_utc`: 20261114T205712Z
- `C281B_to_C300`: COMPLETE_NOT_TRADABLE_zero_costed_OOS_edge_frozen
- `C301`: COMPLETE_NOT_TRADABLE_0_648_edge_binding_mean_beats_benchmark_fail
- `n_campaigns`: 21

## Campaign summary (all frozen)

| Campaign | Verdict | n_runs | n_edge_proven | Binding constraint |
|---|---|---|---|---|
| C281B | NOT_TRADABLE | 663 | 0 | cost_sensitivity |
| C281C | GATE_DIAGNOSTICS | - | - | rolling_stable_ok (pass_share 0.00294) |
| C282 | NOT_TRADABLE | 128 | 0 | cost_sensitivity |
| C283 | NOT_TRADABLE | 17 | 0 | zero_exposure |
| C284 | NOT_TRADABLE | 1088 | 0 | zero_exposure |
| C285 | NOT_TRADABLE | 81 | 0 | cost_sensitivity |
| C286 | NOT_TRADABLE | 81 | 0 | cost_sensitivity |
| C287 | BLOCKED_EXTERNAL_EXECUTION | - | - | decoupled_from_economic_progress |
| C288 | NOT_TRADABLE | 81 | 0 | cost_sensitivity |
| C289 | ECONOMIC_SPACE_CLOSED | - | - | max DSR 0.0; MDE 0.106 bps |
| C290 | NOT_TRADABLE | 162 | 0 | cost_sensitivity (26 assets) |
| C291 | NOT_TRADABLE | 162 | 0 | cost_sensitivity (24 assets) |
| C292 | NOT_TRADABLE | 81 | 0 | cost_sensitivity (25 assets) |
| C293 | NOT_TRADABLE | 81 | 0 | cost_sensitivity |
| C294 | NOT_TRADABLE | 27 | 0 | cost_sensitivity |
| C295 | NOT_TRADABLE | 162 | 0 | cost_sensitivity (92/162 gross-positive at 0bps, 0/162 net at >=5bps) |
| C296 | DATA_BLOCKED | - | - | no per-strike mark IV historical time series |
| C297 | NOT_TRADABLE | 135 | 0 | mean_beats_benchmark_fail (81/135 gross-positive at 0bps max +2.152) |
| C298 | NOT_TRADABLE | 162 | 0 | zero_exposure (162/162 zero-exposure) |
| C299 | NOT_TRADABLE | 486 | 0 | mean_beats_benchmark_fail |
| C300 | NOT_TRADABLE | 648 | 0 | mean_beats_benchmark_fail (621 with exposure) |
| C301 | NOT_TRADABLE | 648 | 0 | mean_beats_benchmark_fail (545 with exposure / 103 zero-exposure) |

## C287 external execution blocker (external-only, decoupled)

- `status`: BLOCKED
- `decoupled_from_economic_progress`: true
- `as_of_utc`: 20261114T205712Z
- Blocked reasons: binance_testnet_rest_ping:451, binance_testnet_rest_time:451, binance_testnet_rest_exchangeInfo:451, fapi_ping:451, api_bybit_v5_time:403, missing_env_credentials:BINANCE_TESTNET_API_KEY_and_or_SECRET
- Evidence: Binance testnet REST HTTP 451 (CloudFront geographic block, not transient) from this egress IP; fapi 451; bybit 403; no BINANCE_TESTNET_API_KEY/SECRET in env. Mainnet reachable but forbidden for C287 (spec requires testnet only).
- External action required: valid Binance Spot Testnet credentials + network egress not subject to the testnet 451 geographic block — outside this environment.
- Do NOT: re-probe C287 blocked routes as economic work; edit .github/workflows/main.yml; create/read/edit HANDOFF.md; fabricate data/fills/credentials; weaken gates/costs/edge rule; relabel data; claim tradable edge without costed-OOS proof; rerun/edit frozen C281B-C301 artifacts/cache; re-skin the closed family.

## Verification

- `pytest tests/ -q`: 1339 passed, 2 skipped, 0 failed (446.23s), as_of 20261114T205712Z
- Integrity audit: `reports/program_closure_integrity_audit_20261114T085109Z.json` (SHA256 `84174b99be9cce2229a061989dfcddc990f5972c9485d716c4779c8c6184b96d`) + `.md` (SHA256 `ec763ed5428479a78277099962e1149e02ad070eaebf82cba93bc15f4bcada8a`); integrity_ok true, n_references 95, n_issues 0, scope C281B-C297.
- Deps: python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified).
- Cache SHA256-from-bytes: campaign301_aggtrades_ofi.pkl `4ce779531636d833c285cbfd87fe1f46b91bc3d8447c92853be8550973f1b9cf` (3,676,412 B); campaign300_multianual_perp_funding_basis_ts_5m.pkl `2c86accda2f32b466d32c6d520f3424b24952f10e93ea1da9bf803f154cfb873` (69,011,342 B).

## Edge rule (never relaxed)

`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean of per-split OOS net means > mean of per-split equal-weight B&H OOS net means on same WF windows (same aggregation for both legs; never compare a strategy mean to a benchmark sum). Real data only.

## Provenance

- Host: agent-loop execution environment (github runner, linux)
- Message time UTC: 2026-11-14T20:48:53Z
- Generated at UTC: 20261114T205712Z
- C287 blocked by geography/credentials; decoupled from economic progress and external to this environment.
- Never: fabricate data/fills/credentials, weaken gates/costs/edge rule, relabel data, claim tradable edge without costed-OOS proof.
