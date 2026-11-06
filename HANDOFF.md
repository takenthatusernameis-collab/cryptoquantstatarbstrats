## READ THIS FIRST — C90 CONTINUATION (20261106T140458Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #90 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C89 status (executed 2026-11-06T13:16Z–13:17Z)
- **R-A (ref, 13:02:43Z):** `reports/real_feed_unblock_status_20261106T130243Z.json` — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (13:16Z):** `reports/real_quote_volume_mean_run_length_persistence_shock_mr_costed_oos_20261106T131620Z.json` (sha256 `1f84d36b…3de20c`, hypothesis `VOLUME_MEAN_RUN_LENGTH_PERSISTENCE_SHOCK_MR`). WF 720/168/168; 0–40bps; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; all cost slices NOT net>0, NOT beating B&H). Cross-asset OOS net sum (0bps)=-2.2159.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T131733Z.json` (sha256 `b7f2ee34…713661`) supersedes `reports/strategy_edge_registry_20261106T130830Z.json`. pytest `928 passed, 1 skipped, 0 failed, rc=0` (3582 warnings, ~56.65s). C89 summary: `reports/campaign89_execution_summary_20261106T131733Z.json`.

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C89 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json`. To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families exhausted through C89 (no edge):** location family (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs; C89 mean run-length persistence; PLUS C80/C82 MAD/AAD scale, C82-region IQR (051843Z), skewness (023830Z/023835Z), kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **54 `real_quote_volume_*_costed_oos` reports already exist.** **Removal (mandatory):** C90 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-dispersion, NON-entropy, NON-skew/kurtosis, NON-autocorr transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C89 families (location/TP/WW-runs/mean-run-length/dispersion/entropy/skew/kurtosis/autocorr/volume-divergence) before use. Do NOT rerun any C23/C40–C89 transform unchanged. MAD/IQR/skewness are **duplicated — do not use.**
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C90 R-B transform (verify not duplicated)
**Rolling Variance-Ratio (Lo/Craig–MacKinlay) mean-reversion shock on log-volume** — NOT in C23/C40–C89 (no variance-ratio report exists). Compute per-asset log-volume returns `r_t = ln(v_t) - ln(v_{t-1})`; causal variance ratio `VR(q) = Var_k(r_t aggregated over q=24h) / (q * Var_1(r_t))` over a trailing lookback (e.g., 168h); under random walk VR=1, VR<1 signals mean reversion. Trade as MR: fade when causal z of VR is significantly < 1 (go LONG expecting reversion) / significantly > 1 (go SHORT); exit when |z|<0.25 or hold>=12 or flip; t->t+1; WF 720/168/168; 0–40bps; B&H same windows. Fail-closed real loader, exact edge rule. Mechanical distinctness: VR is a spectral/random-walk variance test across aggregation horizons — distinct from location, TP reversal-count, WW total-run-count randomness, mean run-length persistence, dispersion, entropy, skew/kurtosis, and linear autocorr. Alternative if VR duplicated: BDS nonlinear-independence test on log-volume, or sign-change/crossing-rate shock MR on log-volume.

### Execute first (C90 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C89.
# Suggested: rolling Variance-Ratio mean-reversion shock MR on log-volume (q=24, lookback 168h).
# Verify not duplicated; state mechanical distinctness vs all C23-C89 families. WF 720/168/168; 0-40bps; B&H same windows.
# Fail-closed real loader, exact edge rule. Write script, run, emit artifact.
# Full pytest + emit C90 registry superseding C89.
.venv/bin/python -m pytest tests/ -q
```

### C90 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C89** (mechanical distinctness stated vs all C23–C89 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T131733Z.json` (sha256 `b7f2ee34…713661`) with executed pytest counts/rc and C90 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_mean_run_length_persistence_shock_mr_costed_oos_20261106T131620Z.json`.
- `reports/campaign90_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign90_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C89 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T131733Z.json` in outputs.

### CAMPAIGN #90 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 90 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C90 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C89**, **not a location estimator** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not dispersion/entropy/skew/kurtosis/autocorr** (C80–C89 region); mechanically justify vs all C23–C89 families (suggested: rolling **Variance-Ratio (Lo/Craig–MacKinlay) mean-reversion shock MR on log-volume**, q=24, causal lookback 168h — verify no variance-ratio report exists; alternatives: BDS nonlinear-independence, or sign-change/crossing-rate shock MR on log-volume). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C90 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
