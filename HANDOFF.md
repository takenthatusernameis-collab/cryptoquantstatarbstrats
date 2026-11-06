## READ THIS FIRST — C89 CONTINUATION (20261106T131012Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #89 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

Repo prioritization (from name `cryptoquantstatarbstrats`): **fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`.

### C88 status (executed 2026-11-06T13:02Z–13:09Z)
- **R-A (ref, 13:02:43Z):** `reports/real_feed_unblock_status_20261106T130243Z.json` — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED` vs C87 (`reports/real_feed_unblock_status_20261106T122116Z.json`; changed=false). 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`). `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (13:08Z):** `reports/real_quote_volume_wald_wolfowitz_runs_shock_mr_costed_oos_20261106T130804Z.json` (sha256 `c51d6651…cc44`, script `scripts/run_real_quote_volume_wald_wolfowitz_runs_shock_mr_costed_oos.py`). Hypothesis: `VOLUME_WALD_WOLFOWITZ_RUNS_SHOCK_MR` — fade Wald–Wolfowitz runs statistic `Z_WW=(R-mu_R)/sqrt(var_R)` (W=48, median-dichotomized contiguous same-side runs count = dichotomized-sequence randomness/clustering, **NON-location, NON-TP**); causal z(dz,168), fade `|dz|>=1.25`, exit `|dz|<0.25`/hold>=12/flip; `t->t+1`; WF 720/168/168; 0–40bps; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; all cost slices NOT net>0, NOT beating B&H).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T130830Z.json` (sha256 `3a97d20f…c4f3f`) supersedes `reports/strategy_edge_registry_20261106T122237Z.json` (sha256 `94539613…d89f69f`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3561 warnings, ~58s). C88 summary: `reports/campaign88_execution_summary_20261106T130839Z.json`.

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C89 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json`. To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families tested through C88 (no edge):** location family exhausted (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs. **Removal (mandatory):** C89 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs** transform on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs C83/C84/C85/C86 (location), C87 TP, C88 WW runs, ACF/autocorr, and C41–C43 entropy/permutation entropy before use. Do NOT rerun any C23/C40–C88 transform unchanged.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Execute first (C89 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C88, NOT a location estimator, NOT Turning-Point Rate, NOT Wald–Wolfowitz runs. Mechanically justify vs C83-C88, ACF/autocorr, and C41-C43 entropy. Suggested concrete candidate (verify not duplicated, then implement): rolling ABOVE/BELOW-MEDIAN RUN-LENGTH PERSISTENCE = mean length of contiguous same-side runs in the median-dichotomized window (or longest-run ratio) — uses run lengths (persistence/duration) rather than WW’s standardized total-run-count randomness test and rather than TP’s raw-difference reversal frequency. WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Write script, run, emit artifact.
# Full pytest + emit C89 registry superseding C88.
.venv/bin/python -m pytest tests/ -q
```

### C89 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_nonlocation_nonTP_nonWWruns>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C88** (mechanical distinctness stated vs C83–C88 location/TP/WW-runs, ACF/autocorr, C41–C43 entropy). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T130830Z.json` (sha256 `3a97d20f…c4f3f`) with executed pytest counts/rc and C89 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_wald_wolfowitz_runs_shock_mr_costed_oos_20261106T130804Z.json`.
- `reports/campaign89_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign89_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C88 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T130830Z.json` in outputs.

### CAMPAIGN #89 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 89 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C89 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C88**, **not a location estimator** (C83–C86), **not Turning-Point Rate** (C87), and **not Wald–Wolfowitz runs** (C88); mechanically justify vs C83–C88, ACF/autocorr, and C41–C43 entropy (suggested: rolling **mean/longest contiguous above/below-median run length** — run-length persistence/duration, distinct from WW standardized total-run-count randomness test and from TP raw-difference reversal frequency; verify not duplicated). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C89 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
