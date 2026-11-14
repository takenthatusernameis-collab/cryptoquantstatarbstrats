# Program Closure Integrity Audit — 20261114T025732Z

- real_data_only: True
- fabricated_data: False
- scope: C281B-C297 frozen artifacts and datasets referenced in research_state/state.yaml and AGENTS.md
- integrity_ok: False
- n_references: 102 (ok=100, issues=2)
- zero_tradable_edge_registry_confirmed: True
- reachable_real_data_cross_sectional_stat_arb_space: CLOSED

## Generated artifacts

- json: `program_closure_integrity_audit_20261114T025732Z.json` (SHA256-from-bytes `b13dc8b85fc1ccca99320332cd90c6af0156281f55d03ab97717100fcd858cfc`)
- md: `program_closure_integrity_audit_20261114T025732Z.md` (SHA256-from-bytes `10db63256a01fdf62396d36ec8cddeafde8e781c46226f62ce2980ea87a6fde5`)

| Campaign | Items | Hashes OK | Exists | Errors | Verdicts | Bindings | n_runs | n_edge |
|---|---:|:---:|:---:|:---:|---|---|---|---|
| C281B | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C281C | 1 | True | True | False | - | - | None | None |
| C282 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C283 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C284 | 2 | True | True | False | NOT_TRADABLE | zero_exposure | None | None |
| C285 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C286 | 6 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C287 | 14 | False | True | True | - | - | None | None |
| C288 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C289 | 3 | True | True | False | - | - | None | None |
| C290 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C291 | 7 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C292 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C293 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C294 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | 27 | 0 |
| C295 | 8 | True | True | False | NOT_TRADABLE | cost_sensitivity | 162 | 0 |
| C296 | 5 | True | True | False | DATA_BLOCKED | - | 24 | 0 |
| C297 | 6 | True | True | False | NOT_TRADABLE | mean_beats_benchmark_fail | None | None |
| UNCATEGORIZED | 8 | True | True | False | - | - | None | None |

## Issues
- `reports/c287_external_unblock_status_20261114T014957Z.json` expected=5e8795745fc7fd591a9ebd5196255d4340f4b2aa58129bd05542ec9919c78b90 actual=72d1e5ff5c4b465fcd089d6b1dc648df01ce47414bdbcd5da944bbe257d615ae errors=['sha256_mismatch']
- `reports/c287_external_unblock_status_20261114T024344Z.json` expected=9fc3afaebf9aa22050c499ce334859cc424de682da968528d8edb8ad3f85a568 actual=dcf1e8e3a01dd54512183b77fa3f088cca0e0fdf43e235117cc3356c0420c005 errors=['sha256_mismatch']
