## READ THIS FIRST — C93 CONTINUATION (20261106T142846Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #93 R-B now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C92 status (executed 2026-11-06T14:28Z)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** R-A complete — do NOT re-run R-A on the same stale cache as campaign work.
- **R-B (14:28:46Z):** `reports/real_quote_volume_ou_halflife_shock_mr_costed_oos_20261106T142846Z.json` (sha256 `d7237f29…cb8ad`, hypothesis `VOLUME_OU_HALFLIFE_MEAN_REVERSION_SPEED_SHOCK_MR`, script `scripts/run_real_quote_volume_ou_halflife_shock_mr_costed_oos.py`). Rolling OU half-life `HL=ln(2)/(-b)` from parametric AR(1) regression `Δx=a+b*x_{t-1}+e` on log-volume LEVELS (theta=-b>0 => mean-reverting, else NaN fail-closed; W=168, ZLB=168) — a regression-derived mean-reversion SPEED/characteristic timescale. MR fade of HL z-shocks (ENTRY±1.25, EXIT±0.25, max_hold=12). WF 720/168/168; 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows. **oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED** (11 assets, exposure true; cross-asset OOS net sum: {0:+2.062,5:-2.343,10:-6.748,20:-15.558,40:-33.178}, net>0 only at 0bps — fails from 5bps; beats-B&H false, bh_mean=1.438e-5).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T142846Z.json` (sha256 `f47ca60e…5279`) supersedes `reports/strategy_edge_registry_20261106T142235Z.json` (sha256 `8e50e58d…2300`). pytest `928 passed, 1 skipped, 0 failed, rc=0` (3586 warnings, ~57.31s). C92 summary: `reports/campaign92_execution_summary_20261106T142846Z.json` (sha256 `af8a9731…3a6b`).

### Bottlenecks — status and removal (hard)
1. **Cache stale + R-A NO_CHANGE across C84–C92 refs.** **Removal (mandatory):** do NOT re-run R-A on the same stale cache as "new campaign work". Reference only against `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`). To unblock path_r, **discover/ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta — not a rescan.
2. **RQV transform families exhausted through C92 (no edge):** location (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann); C87 Turning-Point Rate; C88 Wald–Wolfowitz runs; C89 mean run-length persistence; C90 variance-ratio VR(q); **C91 BDS nonlinear-independence V_m**; **C92 OU half-life / AR(1) mean-reversion speed HL**; PLUS C80/C82 MAD/AAD scale, IQR-region, skewness, kurtosis, Shannon/permutation/sample/Renyi2 entropy, Bowley/Kelly skew, Hurst, Gini/Theil/CV/IDR/quartile/semi-var/range/meanad L1 dispersion, volume breakout/dryup, volume-price/OBV divergence, autocorr, abnormal/vov/illiq/climax momentum, bimodality. **57 `real_quote_volume_*_costed_oos` reports now exist.** **Removal (mandatory):** C93 R-B must be a **genuinely distinct NON-location, NON-TP, NON-Wald–Wolfowitz-runs, NON-mean-run-length-persistence, NON-variance-ratio, NON-BDS, NON-OU/HL, NON-dispersion, NON-entropy, NON-skew/kurtosis, NON-single-lag-ACF transform** on `real_quote_volume` (or a newly validated nonspot feed first). Pre-state mechanical distinctness vs ALL C23/C40–C92 families before use. Do NOT rerun any C23/C40–C92 transform unchanged. Location/TP/WW/mean-run-length/VR/BDS/OU-HL are **duplicated/exhausted — do not use.**
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C93 R-B transform (verify not duplicated)
**Lempel–Ziv complexity (LZ76 / LZC) shock MR on median-dichotomized log-volume change sign sequence** (binarize `r_t=ln(v_t)-ln(v_{t-1})` by trailing-median sign `s_t∈{0,1}`, compute normalized LZ76 complexity `c(n)/[n/log2(n)]` or raw count `c(n)` over rolling W=168, causal z of complexity). Mechanically distinct: Lempel–Ziv is an **algorithmic/compression (dictionary-phrase parsing) complexity** of a binary sequence — it counts the number of distinct phrases in a Lempel–Ziv parsing (Kolmogorov-complexity proxy). **NOT entropy** (C-scope: Shannon/permutation/sample/Renyi2 are symbol-probability/ordinal-pattern information measures on distributions, not phrase-parsing compression counts), **NOT WW-runs/TP/mean-run-length** (C87–C89 are reversal/run-count/duration dichotomy statistics — LZC counts parsed dictionary phrases, a different combinatorial object). **NOT single-lag ACF, NOT VR/BDS/OU-HL, NOT location/dispersion/skew/kurtosis.** Verify no `lempel|lz_|lzc|lz76` RQV report exists. Alternative if duplicated (pre-state): **Approximate Entropy (ApEn) or a *new* ApEn variant only if absent** — but ApEn/SampEn/PermEn families appear in exhausted entropy list; verify carefully and justify distinctness, or prefer **Hurst/RS rescaled-range on log-volume changes** ONLY if no Hurst RQV costed_oos exists (Hurst listed as exhausted in C92 text — verify by filename) — prefer LZ76 as safest mechanically-justified choice.

### Execute first (C93 R-B) — heavy work, no avoidance
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# R-B (required): pre-state + run ONE genuinely distinct real_quote_volume transform NOT in C23/C40-C92.
# Suggested: rolling Lempel–Ziv (LZ76) complexity on median-dichotomized log-volume change sequence (W=168, ZLB=168).
# Verify not duplicated (no lempel/lz/lzc RQV report); state mechanical distinctness vs ALL C23-C92 families
# (esp. vs entropy Shannon/perm/sample/Renyi2 [distribution info vs phrase-parsing compression], vs WW C88 / mean-run-length C89 / TP C87 [run/count/duration vs dictionary phrases], vs BDS C91, VR C90, OU-HL C92, single-lag ACF, location C83-C86, dispersion/skew/kurtosis).
# WF 720/168/168; 0-40bps; B&H same windows. Fail-closed real loader, exact edge rule. Write script, run, emit artifact.
.venv/bin/python -m pytest tests/ -q
```

### C93 deliverables (fail-closed)
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C92** (mechanical distinctness stated vs all C23–C92 families). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T142846Z.json` (sha256 `f47ca60e…5279`) with executed pytest counts/rc and C93 R-B result(s). Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_ou_halflife_shock_mr_costed_oos_20261106T142846Z.json`.
- `reports/campaign93_execution_summary_<UTC>.json` (>=3 concrete artifacts total this session).
- If blocked: `reports/campaign93_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C92 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T130243Z.json` and prior registry `reports/strategy_edge_registry_20261106T142846Z.json` in outputs.

### CAMPAIGN #93 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 93 — R-A remains complete/reference-only (`NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`, 4 blocked families, `real_quote_volume` validated-only; do not stale-cache rescan). Execute **C93 R-B**: pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C92**, **not location** (C83–C86), **not Turning-Point Rate** (C87), **not Wald–Wolfowitz runs** (C88), **not mean run-length persistence** (C89), **not variance-ratio VR(q)** (C90), **not BDS nonlinear-independence** (C91), **not OU half-life/AR(1) mean-reversion speed** (C92), **not dispersion/entropy/skew/kurtosis/single-lag-ACF**; mechanically justify vs all C23–C92 families (suggested: rolling **Lempel–Ziv LZ76 complexity shock MR on median-dichotomized log-volume change sequence** — algorithmic/phrase-parsing compression count, W=168, ZLB=168 — verify no lempel/lz/lzc RQV report; justify distinctness vs entropy families [distribution info vs compression phrases] and vs C87–C89 [reversal/run-count/duration vs dictionary phrases]). WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C93 superseding registry + execution summary. **No status summary before >=3 new concrete `reports/` artifacts.**
