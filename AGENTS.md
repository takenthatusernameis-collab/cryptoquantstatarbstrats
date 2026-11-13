# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T07:09:16Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable spot data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **1121 passed, 2 skipped, 0 failed** (verified 2026-11-13T07:09:16Z). C285 is **COMPLETE — formal negative result**: `scripts/run_c285_volume_xsec_oos.py` ran end-to-end on the verified real Binance 1h spot + quote-volume caches (5112-bar overlap, 26 OOS splits, 81 pre-registered runs): **NOT_TRADABLE**, 81 runs with exposure, 0 edge, binding constraint `cost_sensitivity` (zero-exposure rate 0.0). All five C285 artifacts exist with fresh timestamps and SHA256-from-bytes. **C286 (5m execution overlay) is ACTIVE and not started**: `scripts/preflight_c286.py` now exists and passes (`ready: true`, all dataset SHAs verified, 151 WF splits confirmed, causal alignment warm for L ∈ {168,336,720}); `scripts/run_c286_5m_volume_xsec_oos.py` and `reports/campaign286_*` are absent as of this refresh — the next session must create and execute the campaign script. C287 (operational hardening) remains deferred until C286 is complete.
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (active, 2026-11-13T07:09:16Z) — EXECUTE C286 NEXT; no planning/status-only turn

**Your first actions this session, in order (do not deviate, do not ask for confirmation):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json
python scripts/verify_env.py --json
python scripts/preflight_c286.py --json     # must print "ready": true; any mismatch is a fail-closed blocker, not a research result
```
Then **create `scripts/run_c286_5m_volume_xsec_oos.py` and execute it end-to-end** (81 pre-registered runs × 151 OOS splits × 5 cost slices on the 26,208-bar 5m cache — a smoke run does not count). Reuse the C285 implementation (`scripts/run_c285_volume_xsec_oos.py`) as the base: same features (z_logqv, qv_ratio, qv_vol), same causal `shift(1)` rule, same fail-closed gates, same strict edge rule, same per-split aggregation; only the execution grid changes to 5m.

**C285 is COMPLETE — formal negative result.** `scripts/run_c285_volume_xsec_oos.py` ran end-to-end on the verified real Binance 1h spot cache + real 1h quote-volume cache (5112-bar overlap, 26 OOS splits, 81 pre-registered runs: 3 features × 3 lookbacks × 3 K × 3 holds): **NOT_TRADABLE**, 81 runs with exposure, 0 edge. Binding constraint: `cost_sensitivity` (zero-exposure rate 0.0). Frozen artifacts and SHA256-from-bytes are listed under "Frozen evidence" below. Do not rerun or edit them. Per the anti-avoidance rules, the volume-conditioned cross-sectional family is recorded NOT_TRADABLE and the search stops here; do not start a new parameter search in this session.

**C286 is the next focus campaign and it is now ACTIVE** (it was deferred until C285 complete; that precondition is satisfied). It is an **economic statistical-arbitrage** campaign, not operational hardening: the C285 volume-conditioned signal re-run with **5m execution** on the real 26,208-bar 5m spot cache, with **causal 1h-volume alignment**, 5m costs, and the same strict edge rule. **C287 (operational hardening: testnet gateway/kill-switch) remains deferred until C286 is complete.**

### C286 model (pre-registered; no post-hoc parameter search)
- Signal: the C285 causal quote-volume signal (z_logqv, qv_ratio, qv_vol; lookbacks `L ∈ {168, 336, 720}` 1h bars) computed from the real 1h quote-volume cache and aligned causally to 5m execution bars — 1h volume at bar t is available at 5m bars at/after `t+1h`; use only data up to `t-1` for the signal; apply `weights.shift(1).fillna(0.0)` before PnL.
- Universe: the same 11 spot assets (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP). 5m spot cache: `data/cache/90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl` (SHA `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`; meta SHA `e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e`; 26208×11, 2026-08-01 → 2026-10-30T23:55Z, zero NaNs, duplicate-free, `real_data_only: true`, `fabricated_data: false`). The 1h volume cache (SHA `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`; meta SHA `4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616`; provenance SHA `c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89`) is already preflight-verified.
- Cross-sectional portfolio at each 5m rebalance bar: rank the 11 assets by the selected feature; go long the top `K` and short the bottom `K`, `K ∈ {2, 3, 5}`. Equal weight `0.5 / K` per leg; gross exposure 1.0; dollar-neutral; per-asset cap 0.5. Holding period `H ∈ {1, 6, 24}` 5m bars; hold between rebalances; no future bars or full-sample statistics.
- Full pre-registered grid: 3 features × 3 lookbacks × 3 K × 3 holds = **81 runs**. Report every run, including zero-exposure runs.
- Walk-forward: `train=720, test=168, step=168` in 5m bars on the 26,208-bar cache → **151 OOS splits**.
- Cost grid exactly: `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps (5m execution, same bps grid as C285).
- Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows; no rebalance.
- Edge rule exactly: `oos_edge_proven=true` iff OOS exposure > 0 AND every cost slice has OOS net sum > 0 AND the mean of the per-split OOS net means is greater than the mean of the per-split equal-weight buy-and-hold OOS net means on the same WF windows. Use the same per-split aggregation for both legs; never compare a strategy mean to a benchmark sum. Anything else is `NOT_TRADABLE`; never relax this rule.

### C286 fail-closed gates (do not weaken)
At each candidate 5m rebalance bar, require all of:
- the causally aligned 1h quote-volume observation for all 11 assets finite and strictly positive;
- the selected signal finite for at least `2K` assets;
- cross-sectional signal dispersion > 0;
- no NaN/non-finite 5m price in any selected leg;
- no missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, block the rebalance and record the reason. C286 uses this gate set; the C281B-C284 pairs gates must not be used as a shortcut or weakened.

### C286 required artifacts (exact names, timestamped)
- `reports/campaign286_oos_sweep_<ts>.json`
- `reports/campaign286_tradable_edge_registry_<ts>.json`
- `reports/campaign286_summary_<ts>.json`
- `reports/campaign286_verdict_<ts>.json`
Each must include `real_data_only: true`, `fabricated_data: false`, the spot/volume/meta/provenance SHA256s, the split/cost config, all 81 run results, and SHA256-from-bytes for the sweep/registry/summary. If `NOT_TRADABLE`, also emit `reports/campaign286_binding_constraint_<ts>.json` with signal pass shares, exposure, turnover, and the binding constraint; this is diagnosis, never an edge claim. Then update the state fields in `research_state/state.yaml` and this file.

### C286 anti-avoidance rules (binding)
- No status-only, planning-only, or inventory-only turn.
- Do not rerun C281B, C281C, C282, C283, C284, or C285; do not edit their frozen artifacts.
- Do not weaken gates, thresholds, costs, or the edge rule; do not cherry-pick windows.
- No synthetic/fabricated data, no relabeling old caches, no quote-volume return metrics as tradable PnL. Quote volume is a **signal only**; PnL is real spot price PnL.
- Use existing dependencies only (numpy/pandas/scipy/statsmodels); do not add a new framework.
- C286 must use the volume-derived signal aligned causally to 5m execution; a price-only C286 variant is forbidden.
- If C286 is `NOT_TRADABLE`, record a formal negative result and stop; C287 is the next campaign.
- **No avoidance path:** do not substitute infra/refactor/docs/status/planning work for C286. The only acceptable outcomes are (a) full C286 artifacts + state/handoff update + green tests, or (b) a fail-closed blocker artifact documenting a concrete unresolvable dependency/data gate failure (no fabricated results).

### C286 completion gate (a turn that ends without this is a failed handoff)
The session is not done until ALL of these are true and persisted:
1. `scripts/run_c286_5m_volume_xsec_oos.py` exists and was executed end-to-end on the verified 5m cache (a smoke-only run does not count).
2. All four artifacts exist with fresh timestamps and SHA256-from-bytes: `reports/campaign286_oos_sweep_<ts>.json`, `reports/campaign286_tradable_edge_registry_<ts>.json`, `reports/campaign286_summary_<ts>.json`, `reports/campaign286_verdict_<ts>.json`.
3. If `NOT_TRADABLE`, `reports/campaign286_binding_constraint_<ts>.json` exists with signal pass shares, exposure, turnover, and the binding constraint.
4. `research_state/state.yaml` and this file record the result, artifact paths, and SHA256-from-bytes.
5. `python -m pytest tests/ -q` still passes.
Ending a turn with only a plan, a status update, a partial sweep, or a smoke run does NOT satisfy the handoff and must be continued.

### Deferred campaigns (do not start early)
- **C287 — operational hardening:** testnet gateway/kill-switch. Do not start until C286 is complete.

## Step 0 — dependency bootstrap and preflight (removes known blockers; run before anything else)
The scheduled Kilo worker shell may start without the repo's Python dependencies. Run this idempotent bootstrap first, with a **900000 ms shell timeout**:
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml` (the controller token cannot persist workflow-file changes and it will loop on persistence failure).

**C286 preflight (before running the campaign):** `scripts/preflight_c286.py` verifies the 5m spot cache/meta and the 1h volume cache/meta/provenance against the recorded SHA256s, the meta real/fabricated flags, the exact 5m window (26208×11, 2026-08-01T00:00Z → 2026-10-30T23:55Z, zero NaNs, duplicate-free, 5m spacing), per-asset 1h volume coverage (5112 finite positive bars), the causal 1h→5m alignment (1h volume at bar t usable only at 5m bars ≥ t+1h; signal warm before the window for L ∈ {168,336,720}), and the WF split math (151 splits, last test window fits). It must print `"ready": true`; any mismatch is fail-closed — do not relabel or fabricate data.

## Bottlenecks removed in this refresh
- **Dependency bootstrap:** `scripts/bootstrap_dev_env.py` + `scripts/verify_env.py` install and verify runtime and test imports, including `hmmlearn`, `pydantic`, `aiohttp`, and `pytest-asyncio`; the old Step 0 omitted the test-only imports.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is explicitly forbidden. Agents that previously tried to edit a non-existent `HANDOFF.md` must ignore the missing-file error and continue.
- **Controller progress accounting:** `scripts/controller_progress.py` is restored; the scheduled workflow can now credit non-workflow commits instead of treating every session as no progress.
- **Missing controller tests:** `tests/test_controller_progress_accounting.py`, `tests/test_workflow_diagnostics_scanner.py`, `tests/test_nonfinite_result_serialization.py`, and `tests/test_campaign_resume.py` are restored so the workflow's controller-tests step is not blocked by missing files.
- **C285 preflight:** `scripts/preflight_c285.py` verifies every dataset SHA, shape, NaN/duplicate status, real/fabricated flag, and the 5112-bar causal overlap before any campaign code runs.
- **C285 campaign script:** `scripts/run_c285_volume_xsec_oos.py` created and executed end-to-end on the verified caches; all five artifacts written with SHA256-from-bytes.
- **C286 preflight (this refresh):** `scripts/preflight_c286.py` now exists and passes — it verifies all five C286 dataset SHAs, meta flags, the exact 26,208×11 5m window with 5m spacing, per-asset 1h volume coverage, causal 1h→5m alignment for L ∈ {168,336,720} (signal warm before the window), and the 151-split WF math. The next session's first blocker check is therefore a single command.
- **Stale resume test (this refresh):** `tests/test_campaign_resume.py` was failing because it hard-coded C284 as the latest completed campaign; it is now generic — it parses `latest_campaign_done` from `research_state/state.yaml` and verifies the referenced artifacts exist on disk. The green baseline is restored at 1121 passed / 2 skipped.

## Current research state (verified 2026-11-13T06:30Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evaluations | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |
| C284 | Kalman dynamic-hedge-ratio pairs, 28 WF splits, 5 cost slices, fail-closed gates | 1088 | `NOT_TRADABLE`, 0 exposure, binding: zero_exposure |
| C285 | Volume-conditioned cross-sectional stat-arb, 11 assets, 26 WF splits, 5 cost slices | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C286 | 5m execution overlay of C285 signal, real 26,208-bar 5m spot cache, causal 1h-volume alignment, 5m costs, 151 WF splits, 81 runs | planned | ACTIVE — preflight ready, campaign script not yet created/executed |

Frozen evidence:
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding constraint `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (SHA `2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (SHA `23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (SHA `512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (SHA `2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding constraint `reports/campaign285_binding_constraint_20261113T065205Z.json` (SHA `15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
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
python scripts/preflight_c286.py --json
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
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285 is complete and frozen; current next campaign is **C286**.

**END OF HANDOFF — refreshed 2026-11-13T07:09:16Z.** The spot-only price-only edge search is closed (C281B→C284 all NOT_TRADABLE) and the volume-conditioned cross-sectional family is closed NOT_TRADABLE (C285). **C286 (5m execution overlay, script `scripts/run_c286_5m_volume_xsec_oos.py`) is the active next campaign — execute it end-to-end and satisfy the completion gate.** C287 (operational hardening) remains deferred until C286 is complete.