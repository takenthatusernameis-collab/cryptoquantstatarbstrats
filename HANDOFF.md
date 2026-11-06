## READ THIS FIRST — C84 INITIAL TASK (20261106T111700Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #84 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### C83 outcome (executed 2026-11-06T10:24–10:33Z, fail-closed)
- **R-A executed:** local cache/workspace/readiness scan for 4 blocked families (`funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`). **No new valid nonspot feed with complete provenance discovered.** `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) remains the only validated nonspot feed. `reports/real_feed_unblock_status_20261106T110014Z.json` (sha256 `2fa31534…752e6b`, campaign 83, prior `reports/real_feed_unblock_status_20261106T102141Z.json`) — **4 families still `blocked_no_real_feed`; unchanged vs C82**. No proxies labeled real; no fabricated feeds/provenance.
- **C83 R-B executed — no edge:** `reports/real_quote_volume_trimean_location_shock_mr_costed_oos_20261106T103150Z.json` (script sha `baf1d39d…1394e5`). Rolling Tukey trimean shock MR `(Q1+2*Q2+Q3)/4, W=48`, z(dz,168), fade `|dz|>=1.25`, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps, B&H same OOS windows (11 assets). **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`; fee0_slip0 mean net +0.0548 but does not beat B&H rule). Mechanically distinct from C23/C40–C82, C66–C73 quantile family, C79 Sarle BC, C45 CV, C51/C74/C75/C76/C78, C41–C43 entropy.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T103330Z.json` (sha256 `7cc6a202…bf655e`, supersedes `...102313Z.json`). Records pytest + R-A + C83 R-B; `oos_edge_proven=false`.
- **pytest:** `928 passed, 1 skipped, 0 failed, rc=0` (~56.9s).

### Bottlenecks — status and removal
1. **Cache is stale for R-A:** all `data/cache/*.pkl`/`.meta.json` mtime 2026-11-06 09:58; no new cache since C83. Re-run R-A anyway (required each session) and document explicit delta vs `reports/real_feed_unblock_status_20261106T110014Z.json`. If still `blocked_no_real_feed` for all 4 families, proceed to R-B without delay — do not re-scan the same cache as a "new campaign".
2. **RQV location transforms exhausted:** C82 (trimean/C82? actually C82 AAD, C80 MAD) and C83 (Tukey trimean) done. Do not rerun C23/C40–C82 unchanged. Next R-B must be a genuinely distinct location estimator on `real_quote_volume` (midhinge `(Q1+Q3)/2` primary; Gastwirth `0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3)` alternate), with mechanical distinctness stated vs trimean `(Q1+2*Q2+Q3)/4` (no median term, different quartile weighting), MAD C80, AAD C82, Sarle BC C79, Hoover C78, C66–C73 quantile family.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.

### Execute first (C84)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A (required): rescan blocked families vs prior report; document delta.
python -c "import sys, pathlib; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(cache_dir=pathlib.Path('data/cache'), campaign=84, prior_report='reports/real_feed_unblock_status_20261106T110014Z.json'))"
# 2) If R-A infeasible: pre-state + run ONE genuinely distinct real_quote_volume R-B (midhinge or Gastwirth; not in C23/C40-C82). Verify mechanical distinctness before use. Write script, run costed OOS, emit artifact.
# 3) Full pytest and emit C84 registry + unblock status artifacts superseding C83.
python -m pytest tests/ -q
```

### C84 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=84`, `prior_report='reports/real_feed_unblock_status_20261106T110014Z.json'`, explicit R-A attempt/delta, 4 blocked families + `real_quote_volume` status.
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct>_costed_oos.py` + `reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C82** (mechanical distinctness stated in artifact). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T103330Z.json` with executed pytest counts/rc and C84 result(s).
- If blocked: `reports/campaign84_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C82 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T110014Z.json` and prior registry `reports/strategy_edge_registry_20261106T103330Z.json` in outputs.

### CAMPAIGN #84 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 84 — R-A FIRST, THEN DISTINCT R-B. In `.venv`, document an honest R-A attempt for the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`) vs `reports/real_feed_unblock_status_20261106T110014Z.json`. If any real feed+provenance is discoverable, validate fail-closed and run costed OOS/feasibility before RQV. If R-A remains infeasible, pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C82** (mechanically justify vs Tukey trimean C83, AAD C82, MAD C80, Sarle BC C79, Hoover C78, C66-C73 quantile family), WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C84 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.
