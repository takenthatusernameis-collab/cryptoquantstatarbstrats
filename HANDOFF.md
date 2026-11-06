## READ THIS FIRST — C94 CONTINUATION (20261106T143752Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #94 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C93 status (executed 2026-11-06T14:33Z)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (14:33:58Z):** `reports/real_quote_volume_lz76_complexity_shock_mr_costed_oos_20261106T143358Z.json` (sha256 `f784dde0…7335`, hypothesis `VOLUME_LZ76_ALGORITHMIC_COMPLEXITY_SHOCK_MR`, script `scripts/run_real_quote_volume_lz76_complexity_shock_mr_costed_oos.py`). Rolling Lempel–Ziv 76 (LZ76) phrase-parsing algorithmic complexity `c(n)*log2(n)/n` on median-dichotomized log-volume change sequence (W=168, ZLB=168) — an ALGORITHMIC/COMPRESSION (dictionary-phrase parsing, Kolmogorov-complexity proxy) counting parsed distinct phrases. MR fade of complexity z-shocks (ENTRY±1.25, EXIT±0.25, max_hold=12). WF 720/168/168; 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; cross-asset OOS net sum: {0:-0.539,5:-7.066,10:-13.593,20:-26.647,40:-52.755}, net<0 at 0bps; beats-B&H false, bh_mean=1.438e-5).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T143520Z.json` (sha256 `d61a7337…35fd`) supersedes `reports/strategy_edge_registry_20261106T142846Z.json` (sha256 `f47ca60e…5279`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3561 warnings, ~57.45s). C93 summary: `reports/campaign93_execution_summary_20261106T143520Z.json` (sha256 `4d294999…cfd1`).

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C93 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`). To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families exhausted through C93 (no edge):** location (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs; C89 mean run-length persistence; C90 variance-ratio VR(q); C91 BDS nonlinear-independence V_m; C92 OU half-life / AR(1) mean-reversion speed HL; **C93 Lempel–Ziv LZ76 algorithmic/phrase-parsing complexity**; PLUS C80/C82 MAD/AAD scale, IQR-region, skewness, kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **58 `real_quote_volume_*_costed_oos` reports now exist.** **Removal (mandatory):** C94 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-variance-ratio, NON-BDS, NON-OU/HL, NON-LZ76, NON-dispersion, NON-entropy (incl. spectral-entropy-as-Shannon-over-PSD — avoid entropy-family overlap), NON-skew/kurtosis, NON-single-lag-ACF, NON-Hurst/RS transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C93 families before use. Do NOT rerun any C23/C40–C93 transform unchanged. LZ76/location/TP/WW/mean-run-length/VR/BDS/OU-HL/Hurst/RS are **duplicated/exhausted — do not use.**
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C94 R-B transform (verify not duplicated)
**Hjorth Mobility/Complexity shock MR on log-volume changes** (compute rolling Hjorth parameters over W=168: Activity `var(x)`, Mobility `sqrt(var(dx)/var(x))`, Complexity `Mobility(dx)/Mobility(x)` on log-volume or log-volume changes; causal z of Mobility or Complexity). Mechanically distinct: Hjorth parameters are **time-domain variance-of-derivative / derivative-ratio statistics** (a signal-shape/spectral-moment proxy derived from first/second differences' variances) — **NOT entropy** (no p*log p / distribution information), **NOT LZ76** (no phrase parsing), **NOT BDS/VR/OU-HL** (no embedding/correlation integral, no multi-horizon variance ratio, no AR(1) regression timescale), **NOT single-lag ACF** (uses variance ratios of derivatives, not lag-k covariance), **NOT runs/TP/mean-run-length, NOT location/dispersion magnitude alone/skew/kurtosis**. Verify no `hjorth|mobility` RQV costed_oos report exists. **Alternative if duplicated:** **Higuchi Fractal Dimension (HFD)** on log-volume changes (curve-length scaling over k) — fractal/roughness dimension from L(k)~k^{-D}, mechanically distinct (geometric curve-length scaling) — verify no `higuchi|hfd|fractal_dimension` RQV report exists.

### Execute first (C94 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C93.
# Suggested: rolling Hjorth Mobility (or Complexity) of log-volume changes (W=168, ZLB=168) — time-domain
# variance-of-derivative/derivative-ratio statistic. Verify not duplicated (no hjorth/mobility RQV report);
# state mechanical distinctness vs ALL C23-C93 families (esp. vs entropy [no distribution info], vs LZ76 C93
# [no phrase parsing], vs BDS C91/VR C90/OU-HL C92, vs single-lag ACF [derivative variance ratios != lag-k cov],
# vs runs/TP/mean-run-length C87-C89, vs Hurst/RS [exhausted], vs location C83-C86/dispersion/skew/kurtosis).
# WF 720/168/168; 0-40bps; B&H same windows. Fail-closed real loader, exact edge rule. Write script, run, emit artifact.
.venv/bin/python -m pytest tests/ -q
```

### C94 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C93** (mechanical distinctness stated vs all C23–C93 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T143520Z.json` (sha256 `d61a7337…35fd`) with executed pytest counts/rc and C94 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_lz76_complexity_shock_mr_costed_oos_20261106T143358Z.json`.
- `reports/campaign94_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign94_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C93 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T143520Z.json` in outputs.

### CAMPAIGN #94 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 94 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C94 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C93**, **not location** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not variance-ratio VR(q)** (C90), **not BDS nonlinear-independence** (C91), **not OU half-life/AR(1) mean-reversion speed** (C92), **not Lempel–Ziv LZ76 algorithmic complexity** (C93), **not Hurst/RS, not dispersion/entropy (incl. spectral-entropy-as-Shannon-over-PSD)/skew/kurtosis/single-lag-ACF**; mechanically justify vs all C23–C93 families (suggested: rolling **Hjorth Mobility or Complexity shock MR on log-volume changes** — time-domain variance-of-derivative/derivative-ratio statistic, W=168, ZLB=168 — verify no hjorth/mobility RQV report; justify distinctness vs entropy [no distribution info], vs LZ76 [no phrase parsing], vs BDS/VR/OU-HL, vs single-lag ACF [derivative variance ratios != lag-k cov], vs C87–C89 runs/TP; alternative **Higuchi Fractal Dimension** if Hjorth duplicated). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C94 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
