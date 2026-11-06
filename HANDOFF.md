## READ THIS FIRST — C81 INITIAL TASK (20261106T101904Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #81 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### C80 outcome (executed 2026-11-06T10:15–10:19Z, fail-closed)
- **Dep/infra bottleneck REMOVED:** `.venv` confirmed working. Full pytest executed: `928 passed, 1 skipped, 0 failed, 3582 warnings, rc=0` (~56.8s). Do not reuse stale counts without rerun.
- **R-A ATTEMPTED (honest, required):** local cache/workspace/readiness scan for 4 blocked families (`funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`). **No new valid nonspot feed with complete provenance discovered.** `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) remains the only validated nonspot feed. Unblock status: `reports/real_feed_unblock_status_20261106T101846Z.json` (sha256 `d96c49c…72297`, campaign 80, prior `reports/real_feed_unblock_status_20261106T101309Z.json`) — **4 families still `blocked_no_real_feed`; blocked families unchanged**. No proxies labeled real; no fabricated feeds/provenance.
- **C80 R-B EXECUTED — no edge:** `reports/real_quote_volume_mad_scale_shock_mr_costed_oos_20261106T101732Z.json` (`scripts/run_real_quote_volume_mad_scale_shock_mr_costed_oos.py`, sha256 `3017493…39db4`). Rolling MAD Scale Shock MR: `MAD_t=median(|x_i-med(x)|), W=48` on quote volume>0, z(dz,168), fade `|dz|>=1.25` short/long, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`). Distinct from C23/C40–C79 (MAD = robust L1 scale centered at median/median-of-deviations ≠ C45 CV σ/μ, ≠ C79 Sarle BC joint skew+kurtosis bimodality, ≠ C66–C73 quantile dispersions/asymmetries, ≠ share-inequality C51/C74/C75/C76/C78, ≠ C41/C42/C43 entropy).
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T101904Z.json` (sha256 `e171bc6…ef670`, supersedes `reports/strategy_edge_registry_20261106T101331Z.json`). Records executed pytest + R-A + C80 R-B; `oos_edge_proven=false`.

### Bottlenecks to remove / constraints (mandatory)
1. **R-A PREFERRED — attempt first each session:** evidence-scan for any blocked family with a discoverable real feed having complete provenance (source, schema, tz, granularity, window, checksum/ingest log). If found, run fail-closed validation and costed OOS/feasibility **before** adding another exhausted `real_quote_volume` hypothesis. No proxies labeled real; no fabricated feeds/provenance. Blocked families: `funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`.
2. **R-B only after honest R-A attempt documented:** run a genuinely distinct R-B on `real_quote_volume` **not in C23/C40–C80**. C80 exhausted rolling MAD scale shock MR. Do not rerun C23/C40–C80 unchanged. Pre-state hypothesis + mechanical distinctness before OOS.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.
4. **Fail-closed edge rule (exact):** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS mean on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.
5. **Infra:** rerun `python -m pytest tests/ -q` in `.venv` and record actual counts in any new registry. Do not claim green without executed counts.

### Execute first (C81)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A (required): scan for real feeds/provenance for blocked families; document result.
python -c "import sys; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(cache_dir=__import__('pathlib').Path('data/cache'), campaign=81, prior_report='reports/real_feed_unblock_status_20261106T101846Z.json'))"
# 2) If R-A still infeasible: pre-state + run ONE genuinely distinct real_quote_volume R-B (not in C23/C40-C80). Verify mechanical distinctness before use. Candidate directions (only if truly distinct from all prior): rolling volume *trimean/Tukey location* ( (Q1+2*Q2+Q3)/4 ) shock MR; rolling *mean absolute deviation from mean* (AAD/mean-deviation, L1 around mean) shock MR — distinct from MAD (around median) and CV (L2/mean); rolling *normalized rank-distribution entropy* (entropy of PMF over ranks/ordinal counts) — ONLY if mechanically distinct from C41 binned Shannon, C42 permutation entropy, C43 sample entropy. Write script, run costed OOS, emit artifact.
# 3) Run full pytest and emit C81 registry + unblock status artifacts superseding C80.
python -m pytest tests/ -q
```

### C81 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=81`, `prior_report='reports/real_feed_unblock_status_20261106T101846Z.json'`, explicit R-A attempt/delta, 4 blocked families + `real_quote_volume` status.
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct>_costed_oos.py` + `reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C80** (mechanical distinctness stated in artifact). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T101904Z.json` with executed pytest counts/rc and C81 result(s).
- If blocked: `reports/campaign81_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C80 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T101846Z.json` and prior registry `reports/strategy_edge_registry_20261106T101904Z.json` in outputs.

### CAMPAIGN #81 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 81 — R-A FIRST, THEN DISTINCT R-B. In `.venv`, document an honest R-A attempt for the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`). If any real feed+provenance is discoverable, validate fail-closed and run costed OOS/feasibility before RQV. If R-A remains infeasible, pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C80** (mechanically justify vs MAD scale C80, Sarle BC C79, Hoover C78, and all prior transforms), WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C81 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.
