## READ THIS FIRST — C91 CONTINUATION (20261106T141245Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #91 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C90 status (executed 2026-11-06T14:10Z–14:12Z)
- **R-A (ref, 13:02:43Z):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (14:10:32Z):** `reports/real_quote_volume_variance_ratio_shock_mr_costed_oos_20261106T141032Z.json` (sha256 `e192f01f…b0e0e5`, hypothesis `VOLUME_VARIANCE_RATIO_SHOCK_MR`, script `scripts/run_real_quote_volume_variance_ratio_shock_mr_costed_oos.py`). Rolling Lo/Craig–MacKinlay `VR(q)=Var(r^(q))/(q*Var(r))` on log-volume changes (q=24, W_VR=168, ZLB=168), MR fade of VR z-shocks (ENTRY±1.25, EXIT±0.25, max_hold=12). WF 720/168/168; 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; net>0 fails at >=5bps, beats-B&H false). Cross-asset OOS net sum: {0:1.1067,5:-3.3513,10:-7.8093,20:-16.7253,40:-34.5573}.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T141245Z.json` (sha256 `ebcf6099…5a43d9`) supersedes `reports/strategy_edge_registry_20261106T131733Z.json` (sha256 `b7f2ee34…713661`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3560 warnings, ~57.32s). C90 summary: `reports/campaign90_execution_summary_20261106T141245Z.json` (sha256 `80b807b3…beee79`).

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C90 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`). To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families exhausted through C90 (no edge):** location (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs; C89 mean run-length persistence; **C90 variance-ratio VR(q)**; PLUS C80/C82 MAD/AAD scale, C82-region IQR (051843Z), skewness (023830Z/023835Z), kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **55 `real_quote_volume_*_costed_oos` reports now exist.** **Removal (mandatory):** C91 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-variance-ratio, NON-dispersion, NON-entropy, NON-skew/kurtosis, NON-autocorr transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C90 families before use. Do NOT rerun any C23/C40–C90 transform unchanged. MAD/IQR/skewness/HL/Gastwirth/midhinge/trimean/TP/WW-runs/mean-run-length/VR are **duplicated/exhausted — do not use.**
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C91 R-B transform (verify not duplicated)
**BDS (Brock–Dechert–Scheinkman) nonlinear-independence statistic on log-volume changes (m=2, eps=0.5*sd, W=168) — MR shock on BDS z.** NOT in C23/C40–C90 (no BDS report). BDS tests i.i.d./independence via correlation-integral embedding-dimension scaling: under independence BDS≈0; significant BDS indicates nonlinear serial dependence/structure. Compute causal rolling BDS W-stat z over ZLB=168; fade extreme BDS z as structure/persistence shock MR (ENTRY±1.25, EXIT±0.25, max_hold=12); t->t+1; WF 720/168/168; 0–40bps; B&H same windows. Fail-closed real loader, exact edge rule. Mechanical distinctness: BDS is a correlation-integral/embedding-dimension nonlinear-independence test (joint higher-order dependence) — distinct from VR(q) multi-horizon variance-scaling ratio, location, TP reversal-count, WW total-run-count randomness, mean run-length persistence/duration, dispersion, entropy, skew/kurtosis, and single-lag linear ACF. Alternatives if BDS duplicated/too slow (pre-state): **sign-change/crossing-rate shock MR on log-volume** (`CR = (1/(n-1))*sum I[r_t*r_{t-1}<0]`, a zero-crossing oscillation rate — distinct from TP which counts local peak/troughs of consecutive diffs on the raw series, and distinct from dichotomized median-runs), or **Ljung–Box Q joint autocorr-portmanteau statistic** (multi-lag joint test) — note ACF family exists so justify portmanteau vs single-lag ACF if used.

### Execute first (C91 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C90.
# Suggested: rolling BDS nonlinear-independence shock MR on log-volume (m=2, eps=0.5*sd, W=168, ZLB=168).
# Verify not duplicated; state mechanical distinctness vs all C23-C90 families (esp. vs VR C90, vs TP C87, vs WW/C89 runs, vs ACF). WF 720/168/168; 0-40bps; B&H same windows.
# Fail-closed real loader, exact edge rule. Write script, run, emit artifact.
# Full pytest + emit C91 registry superseding C90.
.venv/bin/python -m pytest tests/ -q
```

### C91 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C90** (mechanical distinctness stated vs all C23–C90 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T141245Z.json` (sha256 `ebcf6099…5a43d9`) with executed pytest counts/rc and C91 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_variance_ratio_shock_mr_costed_oos_20261106T141032Z.json`.
- `reports/campaign91_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign91_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C90 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T141245Z.json` in outputs.

### CAMPAIGN #91 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 91 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C91 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C90**, **not location** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not variance-ratio VR(q)** (C90), **not dispersion/entropy/skew/kurtosis/autocorr**; mechanically justify vs all C23–C90 families (suggested: rolling **BDS nonlinear-independence shock MR on log-volume changes**, m=2, eps=0.5*sd, W=168, ZLB=168 — verify no BDS report; alternatives: sign-change/crossing-rate shock MR on log-volume with distinction vs TP stated, or Ljung–Box portmanteau with distinction vs single-lag ACF stated). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C91 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
