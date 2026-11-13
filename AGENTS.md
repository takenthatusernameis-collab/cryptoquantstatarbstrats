# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T04:52:55Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable spot data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** Local runtime `python -m pytest tests/ -q` → **1104 passed, 2 skipped, 0 failed** (45.94s). Required cache/meta SHA256s re-verified from bytes at refresh time. **Known bottleneck (removed by Step 0 below):** the scheduled CI "Kilo General Agent Loop" worker shell has repeatedly failed with `ModuleNotFoundError: No module named 'numpy'` (108/178 diagnostics rows) because `.github/workflows/main.yml` is maintainer-owned and the agent token cannot persist workflow-file edits. Do NOT edit `main.yml`; run the Step 0 bootstrap at the start of every session instead.
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` does not exist; do not create another handoff file.

## INITIAL TASK MESSAGE (active, 2026-11-13T04:52:55Z) — execute this first, no planning/status-only turn

**Execute Campaign C284: a pre-registered, costed OOS test of Kalman-filter dynamic-hedge-ratio pairs with causal OU/cointegration gates on the refreshed real Binance spot cache.** This is the next heavy-work campaign because C281B, C282, and C283 all returned `NOT_TRADABLE` on the same 5427×11 cache; C281C identified `rolling_stable_ok` as the binding pairs gate (0.29% pass), and C283 showed turnover is also binding. C284 must test the one structurally distinct pairs construction not yet tested: a **time-varying Kalman hedge ratio** instead of rolling OLS, while keeping fail-closed gates and the exact C281B cost/edge protocol. Do **not** answer with planning, inventory, or a status update: create `scripts/run_c284_kalman_pairs_oos.py`, run it over the full universe, and emit the four C284 artifacts with SHA256-from-bytes.

### Step 0 — dependency bootstrap (removes the known CI blocker; run before anything else)
The CI worker shell may not have the repo's Python dependencies installed. Run this idempotent bootstrap first:
```bash
python -c "import numpy, pandas, scipy, statsmodels" 2>/dev/null || python -m pip install -r requirements.txt
python -c "import pytest" 2>/dev/null || python -m pip install pytest
```
If `pip` has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml` (the controller token cannot persist workflow-file changes and it will loop on persistence failure).

## C284 binding protocol

### Data and preflight (must be verified in code)
- Dataset: `data/cache/26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl`
- Expected cache SHA256: `9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df`
- Expected meta SHA256: `95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1` (use the exact file: `...meta.json`; verify from bytes)
- Required shape: 5427 hourly bars × 11 assets, 2026-04-01 → 2026-11-13T02:00Z, zero NaNs, duplicate-free index, `fetch_real_data_only=true`, `fetch_fabricated_data=false`.
- If any check fails: stop with a blocker artifact; never impute, backfill synthetically, or substitute another cache.

### Universe and walk-forward
- All 17 pairs from `reports/portfolio_real.json`.
- Reuse the C281B protocol verbatim: `train=720, test=168, step=168`, 28 OOS splits on the full 5427-bar cache.
- Cost grid exactly: `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps.
- Edge rule exactly: `oos_edge_proven=true` iff OOS exposure > 0 AND every cost slice has OOS net sum > 0 AND mean OOS net > mean pair-matched buy-and-hold OOS net on the same WF windows. Anything else is `NOT_TRADABLE`; never relax this rule.

### C284 model (pre-registered; no post-hoc parameter search)
For each pair `(A,B)`, estimate a causal time-varying hedge ratio:
- State-space: `B_t = alpha_t + beta_t * A_t + eps_t`, `alpha_t = alpha_{t-1} + xi_t`, `beta_t = beta_{t-1} + eta_t`.
- Use a Kalman local-level filter. Fit only on the trailing TRAIN window; run the filter causally through the TEST window using the train-selected noise parameters. At every bar, use only data available up to `t-1`.
- Pre-registered Kalman noise grid: `q ∈ {1e-6, 1e-4}`, `r ∈ {1e-4, 1e-2}` (4 configs).
- Spread: `s_t = B_t - (alpha_t + beta_t * A_t)`.
- Causal z-score: trailing lookbacks `{240, 480}`, mean/std computed only from prior bars; fail closed on zero/non-finite std.
- Entries: `|z| >= {2.0, 2.5}`; exits: `|z| <= {0.5, 1.0}`; minimum holding `{1, 6}` bars.
- Position: opposing legs normalized by absolute market value from the Kalman hedge ratio; apply `weights.shift(1).fillna(0.0)`; cap gross pair exposure at 1.0. Do not use future bars or full-sample statistics.
- Full pre-registered grid: 17 pairs × 4 Kalman configs × 2 lookbacks × 2 entries × 2 exits × 2 holds = **1088 runs**. Report every run, including zero-exposure runs.

### Fail-closed gates (do not weaken)
At each candidate entry bar, require all of:
- causal Engle-Granger `p <= 0.05`;
- causal spread ADF/KPSS stationarity passes;
- OU half-life satisfies `1 < half_life < 500`;
- causal rolling hedge-ratio/spread stability gate passes (the same discipline as `rolling_stable_ok`);
- structural-break discipline passes;
- no missing/None/false gate value is treated as permissive.
If diagnostics cannot be computed, block the entry and record the reason. Do not pass `pair_diagnostics_file`/`enriched_diagnostics` static shortcuts.

### Required artifacts (exact names, timestamped)
- `reports/campaign284_oos_sweep_<ts>.json`
- `reports/campaign284_tradable_edge_registry_<ts>.json`
- `reports/campaign284_summary_<ts>.json`
- `reports/campaign284_verdict_<ts>.json`
Each must include `real_data_only: true`, `fabricated_data: false`, the cache SHA, split/cost config, all run results, and SHA256-from-bytes for the sweep/registry/summary. If `NOT_TRADABLE`, also emit `reports/campaign284_binding_constraint_<ts>.json` with gate pass shares, exposure, turnover, and the binding constraint; this is diagnosis, never an edge claim.
Then update the state fields in `research_state/state.yaml` and this file with the C284 result, artifact paths, and SHA256-from-bytes.

### Anti-avoidance rules (binding)
- No status-only, planning-only, or inventory-only turn.
- Do not rerun C281B, C281C, C282, or C283; do not edit their frozen artifacts.
- Do not weaken gates, thresholds, costs, or the edge rule; do not cherry-pick windows.
- No synthetic/fabricated data, no relabeling old caches, no quote-volume return metrics as tradable PnL.
- Use existing dependencies only (numpy/pandas/scipy/statsmodels); do not add a new framework.
- If C284 is `NOT_TRADABLE`, stop the spot-only price-only edge search and record a formal negative result. The next campaign after that is **C285 operational hardening** (testnet gateway/kill-switch), but C284 must finish first.

### Completion gate (a turn that ends without this is a failed handoff)
The next session is not done until ALL of these are true and persisted:
1. `scripts/run_c284_kalman_pairs_oos.py` exists and was executed end-to-end on the verified cache (a smoke-only run does not count).
2. All four artifacts exist with fresh timestamps and SHA256-from-bytes: `reports/campaign284_oos_sweep_<ts>.json`, `reports/campaign284_tradable_edge_registry_<ts>.json`, `reports/campaign284_summary_<ts>.json`, `reports/campaign284_verdict_<ts>.json`.
3. If `NOT_TRADABLE`, `reports/campaign284_binding_constraint_<ts>.json` exists with gate pass shares, exposure, turnover, and the binding constraint.
4. `research_state/state.yaml` and this file record the result, artifact paths, and SHA256-from-bytes.
5. `python -m pytest tests/ -q` still passes.
Ending a turn with only a plan, a status update, a partial sweep, or a smoke run does NOT satisfy the handoff and must be continued.

## Current research state (verified 2026-11-13T04:45Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evaluations | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |

Frozen evidence:
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- Global registry with zero tradable edge: `reports/tradable_edge_registry_20261112T172556Z.json` (SHA `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2`).
- Pairs universe: `reports/portfolio_real.json` (17 pairs).

## Environment / verification

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python -m pytest tests/test_cointegration_diagnostics_schema.py -q
python -m pytest tests/test_campaign8_edge_robustness.py tests/test_campaign9_causal_gate_edge_search.py -q
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels installed. Run the Step 0 bootstrap above before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not attempt to fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact records `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; zero-cost runs are labeled.
5. **NO OVERFITTING** — walk-forward with 28 splits, all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.

## Escalation

- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; current next campaign is **C284**, not 39.

**END OF HANDOFF — refreshed 2026-11-13T04:52:55Z.** The framework is research-complete but deployment-incomplete. Do not spend this session on production plumbing until C284 either proves a costed OOS edge or formally closes the spot-only edge search.