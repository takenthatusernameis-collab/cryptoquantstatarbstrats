# Program Closure Integrity Audit — 20261114T015802Z

- real_data_only: True
- fabricated_data: False
- scope: C281B-C297 frozen artifacts and datasets referenced in research_state/state.yaml and AGENTS.md
- integrity_ok: False
- n_references: 77 (ok=76, issues=1)
- zero_tradable_edge_registry_confirmed: True
- reachable_real_data_cross_sectional_stat_arb_space: CLOSED

## Generated artifacts

- json: `program_closure_integrity_audit_20261114T015802Z.json` (SHA256-from-bytes `7c6d1b1f65e6102d7a6cc4a61c177771b59d0600101a2cd1af3be80b31a19598`)
- md: `program_closure_integrity_audit_20261114T015802Z.md` (SHA256-from-bytes `92a82d5b030a84f0ad8d4c027861fd1e8c801c8fb32c6aaa61a641733a41aa8c`)

| Campaign | Items | Hashes OK | Exists | Errors | Verdicts | Bindings | n_runs | n_edge |
|---|---:|:---:|:---:|:---:|---|---|---|---|
| C281B | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C281C | 1 | True | True | False | - | - | None | None |
| C282 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C283 | 1 | True | True | False | NOT_TRADABLE | - | None | None |
| C284 | 2 | True | True | False | NOT_TRADABLE | zero_exposure | None | None |
| C285 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C286 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C287 | 8 | False | True | True | - | - | None | None |
| C288 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C289 | 3 | True | True | False | - | - | None | None |
| C290 | 6 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C291 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | None | None |
| C292 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C293 | 5 | True | True | False | NOT_TRADABLE | cost_sensitivity | 81 | 0 |
| C294 | 6 | True | True | False | NOT_TRADABLE | cost_sensitivity | 27 | 0 |
| C295 | 6 | True | True | False | NOT_TRADABLE | cost_sensitivity | 162 | 0 |
| C296 | 5 | True | True | False | DATA_BLOCKED | - | 24 | 0 |
| C297 | 6 | True | True | False | NOT_TRADABLE | mean_beats_benchmark_fail | None | None |
| UNCATEGORIZED | 1 | True | True | False | - | - | None | None |

## Issues
- `reports/c287_external_unblock_status_20261114T015431Z.json` expected=993fa792ead2ab32ed813ddbd34513b13d7855136c762f9bbafc6470b172c3e5 actual=9fc3afaebf9aa22050c499ce334859cc424de682da968528d8edb8ad3f85a568 errors=['sha256_mismatch']
