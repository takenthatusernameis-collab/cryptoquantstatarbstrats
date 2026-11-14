# Program Closure Integrity Audit — 20261114T015733Z

- real_data_only: True
- fabricated_data: False
- scope: C281B-C297 frozen artifacts and datasets referenced in research_state/state.yaml and AGENTS.md
- integrity_ok: False
- n_references: 77 (ok=76, issues=1)
- zero_tradable_edge_registry_confirmed: True
- reachable_real_data_cross_sectional_stat_arb_space: CLOSED

## Generated artifacts

- json: `program_closure_integrity_audit_20261114T015733Z.json` (SHA256-from-bytes `2b780e926523ea7f4c89ba88839d5931f6cacd763181e3dc8b139f73f8816bf6`)
- md: `program_closure_integrity_audit_20261114T015733Z.md` (SHA256-from-bytes `91b6a0b42be2075b428cf41a14ea7527d8b683aae9600f2ef96f16ab6891f7c2`)

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
