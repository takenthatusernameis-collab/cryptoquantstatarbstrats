## READ THIS FIRST — C95 INITIAL TASK (20261106T150449Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #95 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C94 status (executed 2026-11-06T150449Z)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`). `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **C94 R-B (15:04:49Z):** `reports/real_quote_volume_hjorth_mobility_shock_mr_costed_oos_20261106T150449Z.json` (sha256 `35aec052…97546`, hypothesis `VOLUME_HJORTH_MOBILITY_SHOCK_MR`, script `scripts/run_real_quote_volume_hjorth_mobility_shock_mr_costed_oos.py`). Rolling Hjorth Mobility `sqrt(var(dx)/var(x))` — time-domain variance-of-derivative / derivative-ratio signal-shape statistic on log-volume changes (W=168, ZLB=168) — mechanically distinct vs all C23/C40–C93 (NON-entropy [variance ratios, not p*log p], NON-LZ76 C93 [no phrase parsing], NON-WW/mean-run-length/TP C87–89, NON-BDS C91, NON-VR C90, NON-OU/HL C92, NON-single-lag-ACF, NON-Hurst/RS, NON-location C83–C86, NON-dispersion/skew/kurtosis). MR fade of Mobility z-shocks (ENTRY±1.25, EXIT±0.25, max_hold=12). WF 720/168/168; 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; cross-asset OOS net sum: {0:-1.509,5:-5.981,10:-10.453,20:-19.397,40:-37.285}, net<0 at 0bps; beats-B&H false, bh_mean=1.438e-5).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T150449Z.json` (sha256 `d4e35f01…add444b5`) supersedes `reports/strategy_edge_registry_20261106T143520Z.json` (sha256 `d61a7337…35fd`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3559 warnings, ~56.37s). C94 summary: `reports/campaign94_execution_summary_20261106T150449Z.json`.
- **RQV transform families now exhausted through C94:** location C83–C86; C87 TP; C88 WW runs; C89 mean run-length; C90 VR(q); C91 BDS; C92 OU/HL; C93 LZ76; C94 Hjorth Mobility; PLUS C80/C82 MAD/AAD scale, IQR-region, skewness, kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **59 `real_quote_volume_*_costed_oos` reports now exist.**

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C94 refs. PRIMARY BLOCKER.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`). To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan. The 4 blocked families need a real feed: `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`. Until a new validated nonspot feed lands, path_r stays blocked and C95+ must run on `real_quote_volume` only.
2. **RQV transform families exhausted through C94 (no edge proven).** **Removal (mandatory):** C95 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-variance-ratio, NON-BDS, NON-OU/HL, NON-LZ76, NON-Hjorth-Mobility/Complexity, NON-dispersion, NON-entropy (incl. spectral-entropy-as-Shannon-over-PSD), NON-skew/kurtosis, NON-single-lag-ACF, NON-Hurst/RS transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C94 families before use. Do NOT rerun any C23/C40–C94 transform unchanged. **Suggested last genuinely-distinct option: Higuchi Fractal Dimension (HFD)** on log-volume changes (curve-length scaling L(k)~k^{-D}, geometric roughness/fractal dimension) — verify no `higuchi|hfd|fractal_dimension` RQV report exists. If HFD is also deemed exhausted/duplicated, the ONLY remaining path to new edge is a NEW real nonspot feed (see bottleneck #1).
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C95 R-B transform (verify not duplicated)
**Higuchi Fractal Dimension (HFD) shock MR on log-volume changes** (compute rolling HFD over W=168: curve-length scaling L(k)~k^{-D} over k=1..kmax, fractal dimension D; causal z of D). Mechanically distinct: HFD is a **geometric curve-length scaling / fractal-roughness dimension** — **NOT entropy** (no p*log p / distribution information), **NOT LZ76/Hjorth** (no phrase parsing, no variance-of-derivative ratio), **NOT BDS/VR/OU-HL** (no embedding/correlation integral, no multi-horizon variance ratio, no AR(1) regression timescale), **NOT single-lag ACF** (uses curve-length scaling over multiple k, not lag-k covariance), **NOT runs/TP/mean-run-length, NOT location/dispersion magnitude alone/skew/kurtosis**, **NOT Hurst/RS** (not rescaled-range). Verify no `higuchi|hfd|fractal_dimension` RQV costed_oos report exists.

### Execute first (C95 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40–C94.
# Suggested: rolling Higuchi Fractal Dimension (HFD) of log-volume changes (W=168, ZLB=168) — geometric
# curve-length scaling / fractal dimension. Verify not duplicated (no higuchi/hfd/fractal_dimension RQV report);
# state mechanical distinctness vs ALL C23–C94 families (esp. vs entropy [no distribution info], vs LZ76/Hjorth
# [no phrase parsing / no variance-of-derivative ratio], vs BDS C91/VR C90/OU-HL C92, vs single-lag ACF
# [curve-length scaling != lag-k cov], vs C87–C89 runs/TP/mean-run-length, vs Hurst/RS [not R/S], vs location
# C83–C86/dispersion/skew/kurtosis). WF 720/168/168; 0-40bps; B&H same windows. Fail-closed real loader,
# exact edge rule. Write script, run, emit artifact.
.venv/bin/python -m pytest tests/ -q
```

### C95 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C94** (mechanical distinctness stated vs all C23–C94 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T150449Z.json` (sha256 `d4e35f01…add444b5`) with executed pytest counts/rc and C95 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_hjorth_mobility_shock_mr_costed_oos_20261106T150449Z.json`.
- `reports/campaign95_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign95_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.
- **Bottleneck removal attempt (if possible):** document any attempt to discover/ingest a NEW real nonspot feed into `data/cache/` for one of the 4 blocked families; emit `reports/real_feed_ingest_attempt_<UTC>.json` if attempted.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C94 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T150449Z.json` in outputs.

### CAMPAIGN #95 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 95 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C95 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C94**, **not location** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not variance-ratio VR(q)** (C90), **not BDS nonlinear-independence** (C91), **not OU half-life/AR(1) mean-reversion speed** (C92), **not Lempel–Ziv LZ76 algorithmic complexity** (C93), **not Hjorth Mobility/Complexity** (C94), **not Hurst/RS, not dispersion/entropy (incl. spectral-entropy-as-Shannon-over-PSD)/skew/kurtosis/single-lag-ACF**; mechanically justify vs all C23–C94 families (suggested: rolling **Higuchi Fractal Dimension (HFD)** on log-volume changes — geometric curve-length scaling L(k)~k^{-D}, fractal roughness dimension, W=168, ZLB=168 — verify no higuchi/hfd/fractal_dimension RQV report; justify distinctness vs entropy [no distribution info], vs LZ76/Hjorth [no phrase parsing / no variance-of-derivative ratio], vs BDS/VR/OU-HL, vs single-lag ACF [curve-length scaling != lag-k cov], vs C87–C89 runs/TP/mean-run-length, vs Hurst/RS [not R/S]). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C95 superseding registry + execution summary. **Attempt bottleneck removal:** document any attempt to ingest a NEW real nonspot feed into `data/cache/` for one of the 4 blocked families. **No status summary before >=3 new concrete `reports/` artifacts.**
