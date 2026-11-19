# VOID — C381 execution attempt (never a result)

Archived 2026-11-19T05:29Z. These files are evidence only. Do NOT freeze, cite, re-run, or copy them.

Reason: the "C381 TURNINGPT" scripts are a clone-and-rename of C380 SEMICOV.

- Kernel is `cov(r_i, r_{i-k} | r_{i-k} < 0) - cov(r_i, r_{i-k} | r_{i-k} > 0)`, k in {1,2,4} — the SEMICOV object, not a turning-point rate.
- Emitted artifacts self-identify `campaign: 380`.
- Tests are named `test_semicov_*`; the artifact guard failed on placebo-seed mismatch.
- Four duplicate sweep sets were produced (043939Z, 044102Z, 044434Z, 044559Z).

TURNINGPT is re-queued as C383 with a corrected spec (see AGENTS.md INITIAL TASK MESSAGE).
The price-only cache `data/cache/campaign381_turningpt_5m/` is valid C312 5m data and stays in place as a template only.
Also archived here: the duplicate C380 re-run set `campaign380_*_20261119T043810Z.json` (the frozen C380 set is `20261119T023818Z`).
