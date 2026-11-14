# Program Closure Integrity Audit — 20261114T000415Z

- real_data_only: True
- fabricated_data: False
- scope: C281B-C296 frozen artifacts and datasets referenced in research_state/state.yaml and AGENTS.md
- integrity_ok: False
- n_references: 95 (ok=88, issues=7)
- zero_tradable_edge_registry_confirmed: True
- reachable_real_data_cross_sectional_stat_arb_space: CLOSED

| Campaign | Items | Hashes OK | Exists | Errors | Verdicts | Bindings | n_runs | n_edge |
|---|---:|:---:|:---:|:---:|---|---|---|---|
| C282 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C283 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C284 | 2 | True | True | False | NOT_TRADABLE | zero_exposure | None | None |
| C285 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C286 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C287 | 5 | True | True | False | - | - | None | None |
| C288 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C289 | 3 | True | True | False | - | - | None | None |
| C290 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C291 | 6 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C292 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C293 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C294 | 11 | False | True | True | NOT_TRADABLE | cost_sensitivity | 27 | 0 |
| C295 | 11 | False | True | True | NOT_TRADABLE | cost_sensitivity | 162 | 0 |
| C296 | 5 | True | True | False | DATA_BLOCKED | - | 24 | 0 |
| 281C | 1 | True | True | False | - | - | None | None |
| C281 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| UNCATEGORIZED | 12 | False | True | True | - | - | None | None |

## Issues
- `reports/campaign294_oos_sweep_20261113T210906Z.json` expected=6b5d184506aa5f7c06e718828ee4a3bc95001752deed7bfbb8a46999db36d080 actual=9fd19f763a5d1f5f264baf02123414a1caa3bd1935c7fa7c7239f6897f572537 errors=['sha256_mismatch']
- `reports/campaign294_tradable_edge_registry_20261113T210906Z.json` expected=31baa147afb75a782e3a00d04d99340a28b46581b93ad02f50c64f0c3dd4e3f9 actual=b3171c1198c433269e3492d5f8786f758c5879961300468412f56c499ba64fa4 errors=['sha256_mismatch']
- `reports/campaign294_summary_20261113T210906Z.json` expected=dc21804a717f7571bda1f0f50df106b455a3150b7f1b7e67dc775e03c2a96ec8 actual=5960389029f03587fc5b5c43c68e9a6f9ae50258da2cb894b7a42b056bbedabf errors=['sha256_mismatch']
- `reports/campaign295_oos_sweep_20261113T215725Z.json` expected=2fe7e08286fb6a055667941292bf2cdcaed069ff7ffebe6d8baa9c8b6859e3f7 actual=fd1762fa820b38cf05ccdada8c89a4da161dd174beb207ad8006f571d72595bc errors=['sha256_mismatch']
- `reports/campaign295_tradable_edge_registry_20261113T215725Z.json` expected=de894a7ba13c78d089101baaf49d1da995f59645552c953dba8b27da9367d1ab actual=e898b0cbcfcbc053af91b2edf9b5cec1c02e861d00a3d6c1546f60e8ed5c671a errors=['sha256_mismatch']
- `reports/campaign295_summary_20261113T215725Z.json` expected=570fb29c497376e6332e97556aa5a17dbdcab68f1088dc9218090a2a617a936d actual=036c01500706137e1098d98639f341aa36231321c7b5e4b0f2e35f2d745e4893 errors=['sha256_mismatch']
- `reports/program_closure_integrity_audit_20261113T234735Z.md` expected=88ea3de73f0f1c7ba12954131763c2532cb2ce7bbedec1aabd9b42f292f6d0b0 actual=9aa562902d13a31f92420ad1c73124bc4f162ddc460e3e7812442b6f48e4ff33 errors=['sha256_mismatch']
