## READ THIS FIRST — C88 CONTINUATION (20261106T130431Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #88 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

Repo prioritization (from name `cryptoquantstatarbstrats`): **fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`.

### C88 status (as of 2026-11-06T13:04Z)
- **C87 executed (12:16–12:22Z):** R-A `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED` vs C86; 4 families still blocked_no_real_feed (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`); `real_quote_volume` only validated nonspot feed. R-B Turning-Point Rate done → `oos_edge_proven=false`. Registry superseded (sha256 `94539613…d89f69f`). pytest `928 passed, 1 skipped, 0 failed, rc=0`.
- **C88 R-A DONE (13:02:43Z):** `reports/real_feed_unblock_status_20261106T130243Z.json` (campaign=88). Delta vs C87 report (`reports/real_feed_unblock_status_20261106T122116Z.json`): `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED` (changed=false; `scan_differences` empty). 4 families still blocked. `real_quote_volume` validated-only. **No new validated nonspot feed discoverable — path_r infeasible on stale cache.** R-A is complete; do NOT re-run R-A on the same stale cache as campaign work.

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C88.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json`. To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families tested through C87 (no edge):** location family exhausted (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); path-oscillation C87 TP done. **Removal (mandatory):** C88 R-B must be a **genuinely distinct NON-location, NON-TP** transform on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs C86/C85/C84/C83 (location) AND vs C87 TP, ACF/autocorr, and C41–C43 entropy/permutation entropy before use. Do NOT rerun any C23/C40–C87 transform unchanged.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Execute first (C88 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C87 and NOT a location estimator and NOT Turning-Point Rate. Mechanically justify vs C86 HL, C85 Gastwirth, C84 midhinge, C83 trimean, C87 TP, ACF/autocorr, and C41-C43 entropy. Suggested concrete candidate (verify not duplicated, then implement): rolling Wald–Wolfowitz RUNS statistic/runs-ratio on volume relative to its rolling median (count runs of values above/below median; dichotomized-sequence clustering/randomness — distinct from TP local peak/trough reversals and from ACF linear correlation). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Write script, run, emit artifact.
# Full pytest + emit C88 registry superseding C87.
.venv/bin/python -m pytest tests/ -q
```

### C88 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_nonlocation_nonTP>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C87** (mechanical distinctness stated vs C83/C84/C85/C86 location, C87 TP, ACF/autocorr, C41–C43 entropy). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T122237Z.json` (sha256 `94539613…d89f69f`) with executed pytest counts/rc and C88 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` (C88 R-A) and `reports/real_feed_unblock_status_20261106T122116Z.json` (C87 R-A).
- If blocked: `reports/campaign88_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C87 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T122237Z.json` in outputs.

### CAMPAIGN #88 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 88 — R-A COMPLETE (13:02:43Z, `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only). Now execute **C88 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C87**, **not a location estimator** (C83/C84/C85/C86), and **not Turning-Point Rate** (C87); mechanically justify vs C83–C87, ACF/autocorr, and C41–C43 entropy (suggested: Wald–Wolfowitz runs statistic/runs-ratio on volume vs rolling median — dichotomized clustering/randomness, distinct from TP local reversals and from linear ACF — verify not duplicated). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C88 superseding registry. **No status summary before >=3 new concrete `reports/` artifacts.**
