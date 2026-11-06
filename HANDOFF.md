## READ THIS FIRST — C87 INITIAL TASK (20261106T120400Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #87 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

Repo prioritization (from name `cryptoquantstatarbstrats`): the mission is **fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (volume_1h_full, 81792 rows) is a validated nonspot feed; the other 4 nonspot families remain `blocked_no_real_feed`.

### C86 outcome (executed 2026-11-06T12:01–12:03Z, fail-closed)
- **R-A executed (required):** `generate_unblock_status_report(cache_dir='data/cache', campaign=86, prior_report='reports/real_feed_unblock_status_20261106T112342Z.json')` → `reports/real_feed_unblock_status_20261106T120340Z.json` (sha256 `77dac2a9…3da3a7`). **Delta vs C85 prior: `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`** (changed=false; blocked families unchanged; path_r unchanged; `scan_differences` empty). **4 families still blocked_no_real_feed:** `funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`. `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) remains the only validated nonspot feed. Cache stale (`data/cache/*.pkl` mtimes 2026-11-06 09:58 UTC). No proxies labeled real; no fabricated feeds/provenance. **No new validated nonspot feed discoverable — R-A infeasible for a new path_r feed.**
- **C86 R-B executed — no edge:** `scripts/run_real_quote_volume_hodges_lehmann_location_shock_mr_costed_oos.py` → `reports/real_quote_volume_hodges_lehmann_location_shock_mr_costed_oos_20261106T120214Z.json` (sha256 `f580d18e…ff7da`). Rolling Hodges–Lehmann location `HL_t=median{(x_i+x_j)/2:1<=i<=j<=n}`, W=48 (Walsh-average-median **rank-based robust LOCATION**, O(W^2) ~1176 pairs/window, feasible), z(dz,168), fade `|dz|>=1.25`, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps, B&H same OOS windows (11 assets). **`oos_edge_proven=false`** (`any_exposure=true, all_cost_slices_positive=false, beats_bh_rule=false`; fee0_slip0 net sum +0.00951 but all nonzero cost slices negative/lose to B&H rule, bh_mean 1.44e-05). **Mechanically distinct** from C85 Gastwirth (tercile+median order-stat L-estimator weights 0.3/0.4/0.3), C84 midhinge `(Q1+Q3)/2` (quartiles Q1/Q3, excludes median, weights 0.5/0/0.5), C83 Tukey trimean `(Q1+2*Q2+Q3)/4` (quartiles, weights 0.25/0.5/0.25), C82 AAD/C80 MAD (scale/dispersion), C66–C73 quantile dispersions/asymmetries (spread/asymmetry not location), C79 Sarle BC/C45 CV/C51C74C75C76C78 inequality (shape/scale/concentration), C41–C43 entropy, C23/C40–C84 other RQV transforms. HL is NOT an L-estimator (no fixed order-statistic weights) — median of all pairwise Walsh averages.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T120340Z.json` (sha256 `eb10abbd…dd2f3`, campaign 86) supersedes `reports/strategy_edge_registry_20261106T112634Z.json` (sha256 `185ca894…56fec421`). Records pytest + R-A + C86 R-B; `oos_edge_proven=false`.
- **pytest:** `928 passed, 1 skipped, 0 failed, rc=0` (~56.8s).

### Bottlenecks — status and removal
1. **Cache stale + R-A re-scan returns NO_CHANGE across C84/C85/C86.** Re-running R-A on the same stale cache as a "new campaign" is inefficient and violates the no-rescan rule. **Removal:** do NOT re-run R-A on the same cache as campaign work. Document the delta once against `reports/real_feed_unblock_status_20261106T120340Z.json` (C86) and proceed directly to R-B. To unblock path_r, a **new real nonspot feed artifact must be discovered/ingested** (none present in cache) — not a cache rescan.
2. **RQV robust-location estimator family exhausted:** C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann — all no edge, all location-family transforms on the same validated feed. **Removal:** the next R-B must be a genuinely distinct **non-location** transform on `real_quote_volume` (or a newly validated nonspot feed via path_r), with mechanical distinctness verified vs C23/C40–C86 before use. Do not rerun any C23/C40–C86 location estimator unchanged.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.

### Execute first (C87)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A reference only (document delta vs C86 report; do NOT treat stale-cache rescan as new campaign work).
python -c "import sys, pathlib, json; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; r=generate_unblock_status_report(cache_dir=pathlib.Path('data/cache'), campaign=87, prior_report='reports/real_feed_unblock_status_20261106T120340Z.json'); print(json.dumps(r.get('campaign_delta'), indent=2))"
# 2) R-B (required): one genuinely distinct NON-location real_quote_volume transform NOT in C23/C40-C86 (verify mechanical distinctness vs C86 HL, C85 Gastwirth, C84 midhinge, C83 trimean before use). Pre-state hypothesis, write script, run costed OOS, emit artifact. Apply exact edge rule. If a new validated nonspot feed appears via path_r, validate fail-closed and run costed OOS/feasibility for that family first.
# 3) Full pytest and emit C87 registry + unblock status artifacts superseding C86.
python -m pytest tests/ -q
```

### C87 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=87`, `prior_report='reports/real_feed_unblock_status_20261106T120340Z.json'`, explicit R-A delta vs C86, 4 blocked families + `real_quote_volume` status. (Do not re-scan same cache as new campaign; document delta only.)
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct_nonlocation>_costed_oos.py` + `reports/real_quote_volume_<distinct_nonlocation>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C86** (mechanical distinctness stated, esp. vs C86 Hodges–Lehmann, C85 Gastwirth, C84 midhinge, C83 Tukey trimean). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T120340Z.json` (sha256 `eb10abbd…dd2f3`) with executed pytest counts/rc and C87 result(s).
- If blocked: `reports/campaign87_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C86 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T120340Z.json` and prior registry `reports/strategy_edge_registry_20261106T120340Z.json` in outputs.

### CAMPAIGN #87 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 87 — R-A REFERENCE (delta vs C86, no stale-cache rescan as new campaign), THEN DISTINCT NON-LOCATION R-B. In `.venv`, document an honest R-A delta against `reports/real_feed_unblock_status_20261106T120340Z.json` confirming the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`) remain blocked and `real_quote_volume` remains the only validated feed. Do not re-run R-A on the same stale cache as campaign work; if pursuing path_r, discover/ingest a new real nonspot feed artifact. Then pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C86** and **not a location estimator** (C83 trimean, C84 midhinge, C85 Gastwirth, C86 Hodges–Lehmann all exhausted the location family); mechanically justify vs all of them, WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C87 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.

---
*(Prior campaign history retained in git history and prior `reports/strategy_edge_registry_*` / `reports/real_feed_unblock_status_*` artifacts.)*
