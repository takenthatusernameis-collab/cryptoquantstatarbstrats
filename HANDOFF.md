## READ THIS FIRST — C85 INITIAL TASK (20261106T112155Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #85 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### C84 outcome (executed 2026-11-06T11:18–11:21Z, fail-closed)
- **R-A executed (required):** `data.real_feed_loader.generate_unblock_status_report(cache_dir='data/cache', campaign=84, prior_report='reports/real_feed_unblock_status_20261106T110014Z.json')` → `reports/real_feed_unblock_status_20261106T111852Z.json` (sha256 `44949e29…27b9ba`). **Delta vs C83 prior: `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`** (changed=false; blocked families unchanged; path_r unchanged; `scan_differences` empty). **4 families still blocked_no_real_feed:** `funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`. `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) remains the only validated nonspot feed. Cache still stale (`data/cache/*.pkl` mtimes 2026-11-06 09:58). No proxies labeled real; no fabricated feeds/provenance.
- **C84 R-B executed — no edge:** `scripts/run_real_quote_volume_midhinge_location_shock_mr_costed_oos.py` (sha256 `070e0b17…468f20`) → `reports/real_quote_volume_midhinge_location_shock_mr_costed_oos_20261106T112108Z.json` (sha256 `96d965e1…6135b`). Rolling midhinge location shock MR `MH_t=(Q1+Q3)/2, W=48` (outer-quartile midpoint, **excludes median Q2**), z(dz,168), fade `|dz|>=1.25`, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps, B&H same OOS windows (11 assets). **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`; fee0_slip0 mean net −0.001375, all cost slices negative/lose to B&H rule). **Mechanically distinct** from C83 Tukey trimean `(Q1+2*Q2+Q3)/4` (TM includes Q2 with double weight; MH excludes Q2, different L-estimator), C80 MAD, C82 AAD, C66–C73 quantile family, C79 Sarle BC, C45 CV, C51/C74/C75/C76/C78, C41–C43 entropy, C23/C40–C83.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T112155Z.json` (sha256 `957f1f1c…089d67`, campaign 84) supersedes `reports/strategy_edge_registry_20261106T103330Z.json` (sha256 `7cc6a202…bf655e`). Records pytest + R-A + C84 R-B; `oos_edge_proven=false`.
- **pytest:** `928 passed, 1 skipped, 0 failed, rc=0` (~56.2s).

### Bottlenecks — status and removal
1. **Cache is stale for R-A:** all `data/cache/*.pkl`/`.meta.json` mtimes 2026-11-06 09:58; no new cache since C84. **Re-run R-A every session anyway** and document explicit delta vs `reports/real_feed_unblock_status_20261106T111852Z.json`. If still `blocked_no_real_feed` for all 4 families, proceed to R-B without delay — do not re-scan the same cache as a "new campaign".
2. **RQV robust-location set partially exhausted:** C83 (Tukey trimean `(Q1+2Q2+Q3)/4`) and C84 (midhinge `(Q1+Q3)/2`) done. **Do not rerun C23/C40–C84 unchanged.** Next R-B must be a genuinely distinct location/robust estimator on `real_quote_volume` with mechanical distinctness stated, e.g. **Gastwirth location `0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3)`** (tercile+median L-estimator, different quantiles/weights from quartile-based TM/MH) or another pre-stated estimator not in C23/C40–C84 (e.g. Hodges–Lehmann median of Walsh averages — only if computationally feasible on W=48; pre-state window/complexity). Verify distinctness vs TM/MH/MAD/AAD/Sarle BC/Hoover/C66–C73 quantile family before use.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.

### Execute first (C85)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A (required): rescan blocked families vs prior report; document delta.
python -c "import sys, pathlib; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(cache_dir=pathlib.Path('data/cache'), campaign=85, prior_report='reports/real_feed_unblock_status_20261106T111852Z.json'))"
# 2) If R-A infeasible: pre-state + run ONE genuinely distinct real_quote_volume R-B (Gastwirth or other mechanically distinct estimator; not in C23/C40-C84). Verify mechanical distinctness before use. Write script, run costed OOS, emit artifact.
# 3) Full pytest and emit C85 registry + unblock status artifacts superseding C84.
python -m pytest tests/ -q
```

### C85 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=85`, `prior_report='reports/real_feed_unblock_status_20261106T111852Z.json'`, explicit R-A attempt/delta, 4 blocked families + `real_quote_volume` status.
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct>_costed_oos.py` + `reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C84** (mechanical distinctness stated in artifact, esp. vs C83 trimean & C84 midhinge). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T112155Z.json` (sha256 `957f1f1c…089d67`) with executed pytest counts/rc and C85 result(s).
- If blocked: `reports/campaign85_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C84 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T111852Z.json` and prior registry `reports/strategy_edge_registry_20261106T112155Z.json` in outputs.

### CAMPAIGN #85 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 85 — R-A FIRST, THEN DISTINCT R-B. In `.venv`, document an honest R-A attempt for the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`) vs `reports/real_feed_unblock_status_20261106T111852Z.json`. If any real feed+provenance is discoverable, validate fail-closed and run costed OOS/feasibility before RQV. If R-A remains infeasible, pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C84** (mechanically justify vs C84 midhinge, C83 Tukey trimean, C82 AAD, C80 MAD, C79 Sarle BC, C78 Hoover, C66-C73 quantile family), WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C85 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.

---
*(Prior campaign history retained in git history and prior `reports/strategy_edge_registry_*` / `reports/real_feed_unblock_status_*` artifacts.)*
