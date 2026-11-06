## READ THIS FIRST — C79 INITIAL TASK (20261106T100756Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #79 now — no investigation-only work, no status-only replies. Produce heavy artifacts first.**

### C78 outcome (verified 2026-11-06T10:07Z)
- **R-A infeasible:** evidence-scanned `data/cache` (21 meta files) — no new validated nonspot real feeds with complete provenance. `real_quote_volume` remains the only validated real feed (`volume_1h_full`, 81792 rows). Substantive blocked families unchanged: `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure` (`blocked_no_real_feed`, fail-closed).
- **R-B prepared but NOT executed in this shell:** pre-stated, genuinely distinct hypothesis created — **Volume Hoover (Robin Hood) Share-Deviation Shock Mean Reversion** (`H_t=0.5*Σ|p_i-1/n|`, `p_i=x_i/Σx_i`, W=48, ZLB=168, fade shocks |d_z|>=1.25 short / <=-1.25 long, exit |d_z|<0.25/hold>=12/flip, t->t+1). Distinct from C23/C40–C77 (Hoover L1 share deviation from uniform / max vertical Lorenz gap ≠ C51 Gini pairwise L1, C76 Theil L GE(0), C74 Theil T GE(1), C75 Rényi-2 H2, C41 Shannon binned, C42/43 permutation/sample entropy, C45 CV, C66-73 quantile dispersions/asymmetries, corr/beta/lead-lag/level/ROC/ratio/cumulative/partition/imbalance transforms).
- **Environment bottleneck (REMOVE FIRST):** `/usr/bin/python3` in this session had **no numpy/pandas/scipy/scikit-learn/statsmodels/PyYAML/pytest** and no project `.venv`; runner/pytest could not execute. This is the primary blocker to C78 completion and all future R-B execution.
- **C78 artifacts (concrete):** `reports/real_feed_unblock_status_20261106T100522Z.json` (C78, prior `...095526Z`, delta no change), `reports/campaign78_execution_blocker_20261106T100522Z.json` (exact missing deps/sources/steps), `reports/strategy_edge_registry_20261106T100753Z.json` (supersedes `reports/strategy_edge_registry_20261106T095532Z.json`; `oos_edge_proven=false`; pytest rc=1 due to missing deps — **must be regenerated after real run**). Scripts added: `scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py`, `scripts/emit_campaign78_unblock_status.py`, `scripts/emit_campaign78_registry.py`.
- **Last known green infra (C76):** `928 passed, 1 skipped, 0 failed` rc=0 — treat as stale until rerun in a working env.

### Bottlenecks to remove now (mandatory)
1. **Unblock Python deps (highest priority):** create/activate a working env with `requirements.txt` + `pytest`, then execute the pending C78 runner and rerun full pytest. Do not claim edge/green tests without executed artifacts/counts.
2. **Close C78 R-B honestly:** run `scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py` → produce `reports/real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_<UTC>.json` (WF 720/168/168, cost grid 0–40 bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows, fail-closed real loader). Apply pre-stated edge rule exactly; `oos_edge_proven` only if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
3. **R-A still preferred in parallel:** if any blocked family has a discoverable real feed with complete provenance (source, schema, tz, granularity, window, checksum/ingest log), run fail-closed validation and costed OOS/feasibility **before** adding another exhausted `real_quote_volume` hypothesis. No proxies labeled real; no fabricated feeds/provenance.
4. **No zero-artifact sessions:** emit `>=3` new concrete `reports/` artifacts (or clearly versioned updates) every session.

### Execute first (copy/run; produce artifacts before summaries)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && pip install pytest
python scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py
python -m pytest tests/ -q
python -c "import sys; sys.path.insert(0,'.'); from data.real_feed_loader import generate_unblock_status_report; print(generate_unblock_status_report(campaign=79, prior_report='reports/real_feed_unblock_status_20261106T100522Z.json'))"
python scripts/emit_campaign78_registry.py  # or emit a C79 registry superseding reports/strategy_edge_registry_20261106T100753Z.json with executed OOS + real pytest counts
```

### C79 deliverables (fail-closed)
- `reports/real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_<UTC>.json` (executed, traced to `scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py`; if edge rule not met, `oos_edge_proven=false`).
- `reports/real_feed_unblock_status_<UTC>.json` with `campaign=79`, `prior_report='reports/real_feed_unblock_status_20261106T100522Z.json'`, delta vs prior explicit.
- `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T100753Z.json` with **executed** pytest counts/rc and C78/C79 OOS result.
- If C78 Hoover proves `oos_edge_proven=false` (expected given exhaustion), **immediately** run one genuinely distinct R-B on `real_quote_volume` not in C23/C40–C78 (justify distinctness mechanically), producing its runner + costed OOS artifact in the same session. If blocked, emit `reports/campaign79_execution_blocker_<UTC>.json` with concrete action taken.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C78 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Rerun `python -m pytest tests/ -q` in a working env and record actual counts; do not reuse stale C76 counts as current.
- Reference prior unblock status `reports/real_feed_unblock_status_20261106T100522Z.json` and prior registry `reports/strategy_edge_registry_20261106T100753Z.json` in outputs.

### CAMPAIGN #79 INITIAL TASK MESSAGE (EXECUTE FIRST)
PRIORITY 79 — REMOVE THE DEP BOTTLENECK, THEN EXECUTE. Install deps/pytest in a venv (or confirm a working env), run `scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py`, run full pytest, regenerate unblock status (campaign 79, prior 100522Z) and superseding registry with real counts. If Hoover shows no edge, do not stop: pre-state and run the next genuinely distinct `real_quote_volume` R-B (not in C23/C40–C78) with WF 720/168/168, 0–40bps, B&H same windows, and emit its costed OOS artifact. No status summary before >=3 new concrete `reports/` artifacts.
