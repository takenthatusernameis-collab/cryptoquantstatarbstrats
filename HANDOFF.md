## READ THIS FIRST — C84 INITIAL TASK (20261106T110014Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #83 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### C83 outcome (executed 2026-11-06T10:24–10:33Z, fail-closed)
- **Dep/infra:** Full pytest executed (real counts): `928 passed, 1 skipped, 0 failed, 3564 warnings, rc=0` (~56.9s).
- **R-A ATTEMPTED FIRST (honest, required):** local cache/workspace/readiness scan for 4 blocked families (`funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`). **No new valid nonspot feed with complete provenance discovered.** `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) remains the only validated nonspot feed. Unblock status: `reports/real_feed_unblock_status_20261106T110014Z.json` (sha256 `2fa31534…752e6b`, campaign 82, prior `reports/real_feed_unblock_status_20261106T102141Z.json`) — **4 families still `blocked_no_real_feed`; unchanged vs C82**. No proxies labeled real; no fabricated feeds/provenance.
- **C83 R-B EXECUTED — no edge:** `reports/real_quote_volume_trimean_location_shock_mr_costed_oos_20261106T103150Z.json` (`scripts/run_real_quote_volume_trimean_location_shock_mr_costed_oos.py`, sha256 `58361b05…65bd7`, script sha `baf1d39d…1394e5`). Rolling Tukey trimean (robust LOCATION L-estimator) shock MR: `TM_t=(Q1+2*Q2+Q3)/4, W=48` on quote volume>0, z(dz,168), fade `|dz|>=1.25` short/long, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows (11 assets). **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`; fee0_slip0 mean net +0.0548 but does not beat B&H rule across slices/costs). Mechanically distinct from C23/C40–C82: TM is robust **location/level**, ≠ C80 MAD median(|x-median|) & C82 AAD mean(|x-mean|) **scale/dispersion of deviations** (different statistic class), ≠ C66–C73 quantile **dispersions/asymmetries** (spreads/ratios like IQR-family, Bowley/Kelly) — TM not spread/asymmetry and not `(Q3-Q1)/(Q3+Q1)`, ≠ C79 Sarle BC, ≠ C45 CV, ≠ share-inequality C51/C74/C75/C76/C78, ≠ C41/C42/C43 entropy.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T103330Z.json` (sha256 `7cc6a202…bf655e`, supersedes `reports/strategy_edge_registry_20261106T102313Z.json`). Records executed pytest + R-A + C83 R-B; `oos_edge_proven=false`.

### Bottlenecks to remove / constraints (mandatory)
1. **R-A PREFERRED — attempt first each session:** evidence-scan for any blocked family with a discoverable real feed having complete provenance (source, schema, tz, granularity, window, checksum/ingest log). If found, run fail-closed validation and costed OOS/feasibility **before** adding another exhausted `real_quote_volume` hypothesis. No proxies labeled real; no fabricated feeds/provenance. Blocked families: `funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`.
2. **R-B only after honest R-A attempt documented:** run a genuinely distinct R-B on `real_quote_volume` **not in C23/C40–C82**. C82 exhausted rolling Tukey trimean (robust quartile location, 2*median-weighted). Do not rerun C23/C40–C82 unchanged. Pre-state hypothesis + mechanical distinctness before OOS. Candidate directions (only if truly distinct from all prior): rolling *midhinge* `(Q1+Q3)/2` shock MR (location — justify mechanical difference vs trimean C82: no median term / different quartile weighting/sensitivity); rolling *Gastwirth’s location estimator* `0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3)` shock MR (different L-estimator/quantile set — justify); other robust **location** or **non-overlapping** transform not in C23/C40–C82. If proposing a dispersion, explicitly justify vs C45/C80/C82/AAD/MAD/CV and vs C66-C73 quantile dispersions (and avoid `(Q3-Q1)/(Q3+Q1)` unless proven absent). Verify mechanical distinctness in script/doc before use.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.
4. **Fail-closed edge rule (exact):** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS mean on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.
5. **Infra:** rerun `python -m pytest tests/ -q` in `.venv` and record actual counts in any new registry. Do not claim green without executed counts.

### Execute first (C84)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A (required): scan for real feeds/provenance for blocked families; document result.
python -c "import sys; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(cache_dir=__import__('pathlib').Path('data/cache'), campaign=84, prior_report='reports/real_feed_unblock_status_20261106T110014Z.json'))"
# 2) If R-A still infeasible: pre-state + run ONE genuinely distinct real_quote_volume R-B (not in C23/C40-C82). Verify mechanical distinctness before use. Write script, run costed OOS, emit artifact.
# 3) Run full pytest and emit C84 registry + unblock status artifacts superseding C82.
python -m pytest tests/ -q
```

### C84 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=83`, `prior_report='reports/real_feed_unblock_status_20261106T110014Z.json'`, explicit R-A attempt/delta, 4 blocked families + `real_quote_volume` status.
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct>_costed_oos.py` + `reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C82** (mechanical distinctness stated in artifact). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T103330Z.json` with executed pytest counts/rc and C83 result(s).
- If blocked: `reports/campaign84_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C82 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T110014Z.json` and prior registry `reports/strategy_edge_registry_20261106T103330Z.json` in outputs.

### CAMPAIGN #83 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 83 — R-A FIRST, THEN DISTINCT R-B. In `.venv`, document an honest R-A attempt for the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`). If any real feed+provenance is discoverable, validate fail-closed and run costed OOS/feasibility before RQV. If R-A remains infeasible, pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C82** (mechanically justify vs Tukey trimean C82, AAD C82, MAD C80, Sarle BC C79, Hoover C78, and all prior transforms/C66-C73 quantile family), WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C83 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.
