# VOID — defective C398 LMOM clone-and-rename (quarantined read-only, 2026-11-20T05:18:46Z)

These five files were named `c398_lmom_*` but were unmodified clones of the FROZEN C397 SPECFM
campaign. They are the exact prohibited C381 defect: rename-only shipping.

Evidence (recorded before quarantine):

- `scripts/build_c398_lmom_features.py`: `DST_DIR = .../campaign397_specfm_5m`, `campaign: 397`,
  `specfm_params`, docstring "C397 feature build ... SPECFM: SPECTRAL FLATNESS / SPECTRAL ENTROPY".
- `scripts/preflight_c398.py`: `CACHE_DIR = .../campaign397_specfm_5m`, validates `specfm_params`,
  prints `campaign: 397`. It would have printed `ready:true` for the C397 cache.
- `scripts/run_c398_lmom_xsec_oos.py`: `CACHE_DIR = .../campaign397_specfm_5m`,
  `PLACEBO_SEED = 20261261` (spec requires 20261262), SPECFM mandate string — it would have
  emitted a duplicate SPECFM sweep labelled `campaign398_*`.
- `tests/test_preflight_c398.py`, `tests/test_c398_lmom_xsec_oos.py`: SPECFM tests.

Action: never copy, import, fix, cite, freeze or run anything in this directory. C398 LMOM must be
created fresh by copying the C397 scripts/tests and FULLY re-specifying the kernel, cache paths,
campaign integer, mandate strings, placebo seed and brute-force reference. The grep self-check in
`AGENTS.md` (`grep -n 397 specfm SPECFM` over `scripts/*c398* tests/*c398*` must return nothing)
enforces this.
