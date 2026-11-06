## READ THIS FIRST — C80 INITIAL TASK (20261106T101400Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #80 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment is READY (`.venv` has numpy/pandas/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### C79 outcome (executed 2026-11-06T10:13Z, fail-closed)
- **Dep bottleneck REMOVED:** `.venv` confirmed working (`/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats/.venv/bin/python`, pandas 3.1.1). No dep install needed unless `.venv` is broken.
- **Full pytest (executed this session):** `928 passed, 1 skipped, 0 failed, 3565 warnings, rc=0` (~60s). Do not reuse stale counts without rerun.
- **C78 R-B EXECUTED — no edge:** `reports/real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_20261106T101025Z.json` (`scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py`, sha256 `21d0796…017ea`). Volume Hoover/Robin Hood share-deviation shock MR: `H_t=0.5*Σ|p_i-1/n|, p_i=x_i/Σx_i`, W=48, ZLB=168, fade `|d_z|>=1.25` (short conc. shock / long uniformity shock), exit `|d_z|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`). Distinct from C23/C40–C77 (Hoover L1 share deviation from uniform / max vertical Lorenz gap ≠ C51 Gini, C76 Theil L GE(0), C74 Theil T GE(1), C75 Rényi-2 H2, C41 Shannon binned, C42/43 perm/sample entropy, C45 CV, C66-73 quantile dispersions/asymmetries).
- **C79 R-B EXECUTED — no edge:** `reports/real_quote_volume_bimodality_coeff_shock_mr_costed_oos_20261106T101306Z.json` (`scripts/run_real_quote_volume_bimodality_coeff_shock_mr_costed_oos.py`, sha256 `f2f2c79…e4a8a`). Volume Sarle's Bimodality Coefficient shock MR: `BC=(g^2+1)/(k_ex + 3*(n-1)^2/((n-2)*(n-3)))` (g=skew, k_ex=excess kurtosis), W=48, ZLB=168, fade `|dz|>=1.25` short / `<=-1.25` long, exit `|dz|<0.25/hold>=12/flip`, t->t+1, WF 720/168/168, 0–40bps, B&H same OOS windows. **`oos_edge_proven=false`** (`any_exposure=true, all_costs_positive=false, beats_bh_rule=false`). Distinct from C23/C40–C78 (composite nonlinear shape/bimodality jointly mapping skewness(3rd)+excess kurtosis(4th) with sample-size correction ≠ raw CV C45/kurtosis, ≠ share-inequality C51/C74/C75/C76/C78, ≠ C41/C42/C43 entropy, ≠ C66-73 quantile transforms).
- **Unblock status (C79):** `reports/real_feed_unblock_status_20261106T101309Z.json` (sha256 `83d26cd…c89e0`, campaign 79, prior `reports/real_feed_unblock_status_20261106T100522Z.json`). `path_r_triggered=true` but **4 families remain `blocked_no_real_feed`**: `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure`. Only validated real feed: `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present). No new nonspot real feeds found in `data/cache` (21 meta). Delta vs C78: conclusion/path_r fields changed per loader logic; **blocked families unchanged**. `oos_edge_proven=false`.
- **Registry (superseding):** `reports/strategy_edge_registry_20261106T101331Z.json` (sha256 `e3e9b06…7dc9`, supersedes `reports/strategy_edge_registry_20261106T100753Z.json`). Records executed C78+C79 OOS + real pytest counts; `oos_edge_proven=false`; `EXECUTED_C78_AND_C79_RB_DEPS_UNBLOCKED`.

### Bottlenecks to remove / constraints (mandatory)
1. **R-A is PREFERRED and must be attempted first each session:** evidence-scan for any blocked family with a discoverable real feed having complete provenance (source, schema, tz, granularity, window, checksum/ingest log). If found, run fail-closed validation and costed OOS/feasibility **before** adding another exhausted `real_quote_volume` hypothesis. No proxies labeled real; no fabricated feeds/provenance. Blocked families: `funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure`.
2. **R-B only after honest R-A attempt documented:** run a genuinely distinct R-B on `real_quote_volume` **not in C23/C40–C79**. C79 exhausted Hoover/Robin Hood (share L1 vs uniform) and Sarle BC (skew+kurtosis bimodality). Do not rerun C23/C40–C79 unchanged. Pre-state hypothesis+distinctness mechanically before OOS.
3. **No status-only work:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session. Produce artifacts before summaries.
4. **Fail-closed / edge rule (exact):** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS mean on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows unless pre-stated with strong justification.
5. **Infra:** rerun `python -m pytest tests/ -q` in `.venv` and record actual counts in any new registry. Do not claim green without executed counts.

### Execute first (C80)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate
# 1) R-A (required attempt): scan for real feeds/provenance for blocked families in data/cache and any discoverable local paths; document result.
python -c "import sys; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(cache_dir=__import__('pathlib').Path('data/cache'), campaign=80, prior_report='reports/real_feed_unblock_status_20261106T101309Z.json'))"
# 2) If R-A still infeasible: pre-state + run ONE genuinely distinct real_quote_volume R-B (not in C23/C40-C79). Suggested unexplored directions (verify distinctness before use): rolling volume *trimean/Tukey location* shock MR; rolling *mean absolute deviation from median (MAD)* shock MR; rolling *entropy of normalized rank distribution* (distinct from binned histogram C41 / permutation C42) — ONLY if mechanically distinct from prior campaigns; write script, run costed OOS, emit artifact.
# 3) Run full pytest and emit C80 registry + unblock status artifacts superseding C79.
python -m pytest tests/ -q
```

### C80 deliverables (fail-closed)
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=80`, `prior_report='reports/real_feed_unblock_status_20261106T101309Z.json'`, explicit R-A attempt/delta, 4 blocked families + real_quote_volume status.
- If R-A yields a validated nonspot feed: fail-closed validation + costed OOS/feasibility artifact for that family (before any new RQV R-B).
- If R-A infeasible: `scripts/run_real_quote_volume_<distinct>_costed_oos.py` + `reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json` for a hypothesis **not in C23/C40–C79** (mechanical distinctness stated in artifact). Apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T101331Z.json` with executed pytest counts/rc and C80 result(s).
- If blocked: `reports/campaign80_execution_blocker_<UTC>.json` with concrete action taken, exact missing priors/feeds, smallest unblocking steps.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C79 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference prior unblock `reports/real_feed_unblock_status_20261106T101309Z.json` and prior registry `reports/strategy_edge_registry_20261106T101331Z.json` in outputs.

### CAMPAIGN #80 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 80 — R-A FIRST, THEN DISTINCT R-B. In `.venv`, document an honest R-A attempt for the 4 blocked nonspot families (`funding_basis_carry,cross_exchange_dual_venue_same_asset,term_structure_real_iv_vol_surface,intrabar_microstructure`). If any real feed+provenance is discoverable, validate fail-closed and run costed OOS/feasibility before RQV. If R-A remains infeasible, pre-state and run one genuinely distinct `real_quote_volume` R-B **not in C23/C40–C79** (mechanically justify vs Hoover C78 and Sarle BC C79 and all prior transforms), WF 720/168/168, 0–40bps, B&H same windows, fail-closed real loader, exact edge rule. Rerun full pytest (record real counts) and emit C80 unblock status + superseding registry. No status summary before >=3 new concrete `reports/` artifacts.
