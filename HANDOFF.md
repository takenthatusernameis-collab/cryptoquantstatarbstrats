## READ THIS FIRST — C92 CONTINUATION (20261106T142235Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #92 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C91 status (executed 2026-11-06T14:21Z–14:22Z)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (14:21:03Z):** `reports/real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos_20261106T142103Z.json` (sha256 `c8625a2a…f33a6`, hypothesis `VOLUME_BDS_NONLINEAR_INDEPENDENCE_SHOCK_MR`, script `scripts/run_real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos.py`). Rolling BDS `V_m=C_m(eps)-C_1(eps)^m` (correlation-integral/embedding-dimension nonlinear-independence) on log-volume changes (m=2, eps=0.5*sd, W=168, ZLB=168), MR fade of BDS z-shocks (ENTRY±1.25, EXIT±0.25, max_hold=12). WF 720/168/168; 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; cross-asset OOS net sum: {0:-0.6199,5:-6.2939,10:-11.9679,20:-23.3159,40:-46.0119}, net<=0 even at 0bps, beats-B&H false).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T142235Z.json` (sha256 `8e50e58d…2300`) supersedes `reports/strategy_edge_registry_20261106T141245Z.json` (sha256 `ebcf6099…5a43d9`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3562 warnings, ~59.63s). C91 summary: `reports/campaign91_execution_summary_20261106T142235Z.json` (sha256 `2e977283…e0f2c`).

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C91 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`). To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families exhausted through C91 (no edge):** location (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs; C89 mean run-length persistence; C90 variance-ratio VR(q); **C91 BDS nonlinear-independence V_m**; PLUS C80/C82 MAD/AAD scale, IQR-region, skewness, kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **56 `real_quote_volume_*_costed_oos` reports now exist.** **Removal (mandatory):** C92 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-variance-ratio, NON-BDS, NON-dispersion, NON-entropy, NON-skew/kurtosis, NON-single-lag-ACF transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C91 families before use. Do NOT rerun any C23/C40–C91 transform unchanged. MAD/IQR/skewness/HL/Gastwirth/midhinge/trimean/TP/WW-runs/mean-run-length/VR/BDS are **duplicated/exhausted — do not use.**
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C92 R-B transform (verify not duplicated)
**Ornstein–Uhlenbeck half-life / AR(1) mean-reversion speed shock MR on log-volume levels** (rolling OLS of `Δx_t = a + b*x_{t-1}+e` over W=168, `theta=-b`, `HL=ln(2)/theta` when `theta>0` else mark non-mean-reverting; causal z of HL or of `theta`). Mechanically distinct: AR(1)/OU half-life is a **continuous-level mean-reversion SPEED / characteristic timescale** from a parametric regression on levels (a rate/half-life), NOT BDS embedding correlation integral (C91), NOT VR(q) multi-horizon variance-scaling ratio (C90), NOT run-duration/count on a dichotomy (C88/C89), NOT TP reversal-count (C87), NOT single-lag linear ACF coefficient used directly (ACF families) — justify explicitly that OU/HL is a regression-derived reversion speed/half-life (timescale) distinct from raw single-lag ACF and from VR. Verify no `half_life|ou_|ornstein` RQV report exists. Alternatives if duplicated (pre-state): **Hurst/RS rescaled-range on log-volume changes** (only if no Hurst RQV exists — Hurst appears in exhausted text; verify), or **Lempel–Ziv complexity on median-dichotomized sign sequence** (a compression/algorithmic-complexity measure distinct from Shannon/permutation/sample/Renyi entropy and distinct from WW/TP/run-length counts) — verify not duplicated and state mechanical distinction vs entropy families and vs C87–C89 run/TP stats.

### Execute first (C92 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C91.
# Suggested: rolling OU half-life / AR(1) mean-reversion speed shock MR on log-volume levels (W=168, ZLB=168).
# Verify not duplicated (no half_life/ou/ornstein RQV report); state mechanical distinctness vs ALL C23-C91 families
# (esp. vs BDS C91, VR C90, mean-run-length C89, WW C88, TP C87, single-lag ACF, location C83-C86).
# WF 720/168/168; 0-40bps; B&H same windows. Fail-closed real loader, exact edge rule. Write script, run, emit artifact.
# Full pytest + emit C92 registry superseding C91.
.venv/bin/python -m pytest tests/ -q
```

### C92 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C91** (mechanical distinctness stated vs all C23–C91 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T142235Z.json` (sha256 `8e50e58d…2300`) with executed pytest counts/rc and C92 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos_20261106T142103Z.json`.
- `reports/campaign92_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign92_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C91 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T142235Z.json` in outputs.

### CAMPAIGN #92 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 92 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C92 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C91**, **not location** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not variance-ratio VR(q)** (C90), **not BDS nonlinear-independence** (C91), **not dispersion/entropy/skew/kurtosis/single-lag-ACF**; mechanically justify vs all C23–C91 families (suggested: rolling **OU half-life / AR(1) mean-reversion speed shock MR on log-volume levels**, OLS `Δx=a+b*x_{t-1}+e`, `HL=ln(2)/(-b)` when mean-reverting, W=168, ZLB=168 — verify no half_life/OU/Ornstein RQV report; alternative: Lempel–Ziv complexity on median-dichotomized sign sequence with explicit distinction vs entropy families and vs C87–C89). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C92 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
