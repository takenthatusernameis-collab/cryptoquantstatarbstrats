# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T06:30:00Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable spot data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** After this refresh `python -m pytest tests/ -q` → **1111 passed, 2 skipped, 0 failed**. C285 is **not started**; it is the active campaign.
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (active, 2026-11-13T06:30:00Z) — EXECUTE C285 NOW; no planning/status-only turn

**C284 is COMPLETE — formal negative result.** `scripts/run_c284_kalman_pairs_oos.py` ran end-to-end on the verified real Binance spot cache (5427×11, 17 pairs, 28 WF splits, 1088 runs): **NOT_TRADABLE**, 0 runs with exposure, 0 edge. Binding constraint: `zero_exposure` (the fail-closed `rolling_stable_ok` gate blocks every entry). Frozen artifacts and SHA256-from-bytes are listed under "Frozen evidence" below. Do not rerun or edit them.

**C285 is the next focus campaign and it is ACTIVE.** It is an **economic statistical-arbitrage** campaign, not operational hardening. The previous handoff's "C285 operational hardening" placeholder is renumbered **C287** and deferred; economic work takes priority per the repository mandate. The spot-only price-only edge search is formally closed, so C285 opens the only remaining real-data economic axis on disk: the real Binance **quote-volume** cache, used as an exogenous signal while PnL is measured on real spot prices.

### C285 model (pre-registered; no post-hoc parameter search)
For each of the 11 spot assets, build a causal quote-volume signal from the real 1h klines column 5 (quote asset volume, USDT):

- `qv_t > 0` and finite; fail closed otherwise.
- `log_qv_t = ln(qv_t)`.
- Feature A — `z_logqv`: `(log_qv_t - rolling_mean(log_qv, L)) / rolling_std(log_qv, L)`, `min_periods = max(20, L // 3)`, fail closed on zero/non-finite std.
- Feature B — `qv_ratio`: `qv_t / rolling_median(qv, L)`, fail closed on non-positive/non-finite median.
- Feature C — `qv_vol`: `rolling_std(log_qv.diff(), L)`, fail closed on non-finite values.
- Lookbacks `L ∈ {168, 336, 720}` 1h bars. Use only data up to `t-1`; apply `weights.shift(1).fillna(0.0)` before PnL.

Cross-sectional portfolio at each rebalance bar:
- Rank the 11 assets by the selected feature; go long the top `K` and short the bottom `K`, `K ∈ {2, 3, 5}`.
- Equal weight `0.5 / K` per leg; gross exposure 1.0; dollar-neutral; per-asset cap 0.5.
- Holding period `H ∈ {1, 6, 24}` 1h bars; hold between rebalances; no future bars or full-sample statistics.
- Full pre-registered grid: 3 features × 3 lookbacks × 3 K × 3 holds = **81 runs**. Report every run, including zero-exposure runs.

### C285 data and preflight (must be verified in code; `scripts/preflight_c285.py` already does this)
- 1h spot cache: `data/cache/26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl` (SHA `9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df`); meta `...meta.json` (SHA `95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1`); 5427×11, 2026-04-01 → 2026-11-13T02:00Z, zero NaNs, duplicate-free.
- 1h real quote-volume cache: `data/cache/volume_1h_full.pkl` (SHA `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`); meta SHA `4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616`; provenance SHA `c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89`; 5112 bars per symbol for all 11 assets, zero NaNs, positive quote volume, `real_data_only: true`, `fabricated_data: false`.
- C285 overlap: inner join of the 1h spot and volume indexes = **5112 bars**, 2026-04-01 00:00 → 2026-10-30 23:00. The last 315 spot bars (2026-10-30 → 2026-11-13) have no volume and must be blocked, not imputed.
- 5m spot cache (C286 only): `data/cache/90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl` (SHA `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`); meta SHA `e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e`; 26208×11, 2026-08-01 → 2026-10-30T23:55Z, zero NaNs, duplicate-free.
- If any check fails: stop with a blocker artifact; never impute, backfill synthetically, relabel another cache, or substitute data.

### C285 walk-forward, costs, and edge rule
- Walk-forward: `train=720, test=168, step=168` on the 5112-bar overlap → **26 OOS splits**.
- Cost grid exactly: `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps.
- Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows; no rebalance.
- Edge rule exactly: `oos_edge_proven=true` iff OOS exposure > 0 AND every cost slice has OOS net sum > 0 AND the mean of the per-split OOS net means is greater than the mean of the per-split equal-weight buy-and-hold OOS net means on the same WF windows. Use the same per-split aggregation for both legs; never compare a strategy mean to a benchmark sum. Anything else is `NOT_TRADABLE`; never relax this rule.

### C285 fail-closed gates (do not weaken)
At each candidate rebalance bar, require all of:
- all 11 quote-volume observations finite and strictly positive;
- the selected signal finite for at least `2K` assets;
- cross-sectional signal dispersion > 0;
- no NaN/non-finite price in any selected leg;
- no missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, block the rebalance and record the reason. C285 uses this separate cross-sectional gate set; the C281B-C284 pairs gates remain unchanged and must not be used as a static shortcut or weakened.

### C285 required artifacts (exact names, timestamped)
- `reports/campaign285_oos_sweep_<ts>.json`
- `reports/campaign285_tradable_edge_registry_<ts>.json`
- `reports/campaign285_summary_<ts>.json`
- `reports/campaign285_verdict_<ts>.json`
Each must include `real_data_only: true`, `fabricated_data: false`, the spot/volume/meta/provenance SHA256s, the split/cost config, all 81 run results, and SHA256-from-bytes for the sweep/registry/summary. If `NOT_TRADABLE`, also emit `reports/campaign285_binding_constraint_<ts>.json` with signal pass shares, exposure, turnover, and the binding constraint; this is diagnosis, never an edge claim. Then update the state fields in `research_state/state.yaml` and this file.

### C285 anti-avoidance rules (binding)
- No status-only, planning-only, or inventory-only turn.
- Do not rerun C281B, C281C, C282, C283, or C284; do not edit their frozen artifacts.
- Do not weaken gates, thresholds, costs, or the edge rule; do not cherry-pick windows.
- No synthetic/fabricated data, no relabeling old caches, no quote-volume return metrics as tradable PnL. Quote volume is a **signal only**; PnL is real spot price PnL.
- Use existing dependencies only (numpy/pandas/scipy/statsmodels); do not add a new framework.
- C285 must use a volume-derived signal; a price-only C285 variant is forbidden.
- If C285 is `NOT_TRADABLE`, record a formal negative result for the volume-conditioned cross-sectional family and stop; do not start a new parameter search in the same session. C286/C287 are the next campaigns.

### C285 completion gate (a turn that ends without this is a failed handoff)
The next session is not done until ALL of these are true and persisted:
1. `scripts/preflight_c285.py` exists and exits 0 with `ready: true`.
2. `scripts/run_c285_volume_xsec_oos.py` exists and was executed end-to-end on the verified caches (a smoke-only run does not count).
3. All four artifacts exist with fresh timestamps and SHA256-from-bytes: `reports/campaign285_oos_sweep_<ts>.json`, `reports/campaign285_tradable_edge_registry_<ts>.json`, `reports/campaign285_summary_<ts>.json`, `reports/campaign285_verdict_<ts>.json`.
4. If `NOT_TRADABLE`, `reports/campaign285_binding_constraint_<ts>.json` exists with signal pass shares, exposure, turnover, and the binding constraint.
5. `research_state/state.yaml` and this file record the result, artifact paths, and SHA256-from-bytes.
6. `python -m pytest tests/ -q` still passes.
Ending a turn with only a plan, a status update, a partial sweep, or a smoke run does NOT satisfy the handoff and must be continued.

### Deferred campaigns (do not start early)
- **C286 — 5m execution overlay:** rerun the C285 signal with 5m execution on the real 26,208-bar 5m spot cache, causal 1h-volume alignment, 5m costs, and the same strict edge rule. Do not start until C285 is complete.
- **C287 — operational hardening:** testnet gateway/kill-switch. Do not start until C285 and C286 are complete.

## Step 0 — dependency bootstrap (removes the known CI blocker; run before anything else)
The scheduled Kilo worker shell may start without the repo's Python dependencies. Run this idempotent bootstrap first, with a **900000 ms shell timeout**:
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml` (the controller token cannot persist workflow-file changes and it will loop on persistence failure).

## Bottlenecks removed in this refresh
- **Dependency bootstrap:** `scripts/bootstrap_dev_env.py` + `scripts/verify_env.py` install and verify runtime and test imports, including `hmmlearn`, `pydantic`, `aiohttp`, and `pytest-asyncio`; the old Step 0 omitted the test-only imports.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is explicitly forbidden. Agents that previously tried to edit a non-existent `HANDOFF.md` must ignore the missing-file error and continue.
- **Controller progress accounting:** `scripts/controller_progress.py` is restored; the scheduled workflow can now credit non-workflow commits instead of treating every session as no progress.
- **Missing controller tests:** `tests/test_controller_progress_accounting.py`, `tests/test_workflow_diagnostics_scanner.py`, `tests/test_nonfinite_result_serialization.py`, and `tests/test_campaign_resume.py` are restored so the workflow's controller-tests step is not blocked by missing files.
- **C285 preflight:** `scripts/preflight_c285.py` verifies every dataset SHA, shape, NaN/duplicate status, real/fabricated flag, and the 5112-bar causal overlap before any campaign code runs.

## Current research state (verified 2026-11-13T06:30Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evaluations | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |
| C284 | Kalman dynamic-hedge-ratio pairs, 28 WF splits, 5 cost slices, fail-closed gates | 1088 | `NOT_TRADABLE`, 0 exposure, binding: zero_exposure |
| C285 | Volume-conditioned cross-sectional stat-arb, 11 assets, 26 WF splits, 5 cost slices | 81 planned | **ACTIVE — not started** |

Frozen evidence:
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding constraint `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- Global registry with zero tradable edge: `reports/tradable_edge_registry_20261112T172556Z.json` (SHA `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2`).
- Pairs universe: `reports/portfolio_real.json` (17 pairs).

## Environment / verification

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python -m pytest tests/test_cointegration_diagnostics_schema.py -q
python -m pytest tests/test_campaign8_edge_robustness.py tests/test_campaign9_causal_gate_edge_search.py -q
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap above before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not attempt to fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact records `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; zero-cost runs are labeled.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — C285 is economic stat-arb; operational hardening is C287 and must not preempt it.

## Escalation

- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; current next campaign is **C285**, not C284.

**END OF HANDOFF — refreshed 2026-11-13T06:30:00Z.** The spot-only price-only edge search is closed (C281B→C284 all NOT_TRADABLE). C285 volume-conditioned cross-sectional stat-arb is active; C286 (5m overlay) and C287 (operational hardening) are deferred.