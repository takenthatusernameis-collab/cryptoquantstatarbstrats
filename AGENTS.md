# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T09:28:33Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable spot data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **green** (1132 passed, 2 skipped). C281B→C286 are **COMPLETE — formal negative results** (NOT_TRADABLE, 0 edge). **C287 (operational hardening: testnet gateway/kill-switch) is the ACTIVE campaign and remains BLOCKED by an unresolvable-in-this-environment runtime blocker: Binance Spot Testnet REST (testnet.binance.vision) returns HTTP 451 "Service unavailable from a restricted location" from this environment's egress IP — a geographic CDN block (CloudFront, X-Amz-Cf-Pop IAD89-P3), not a transient fault. WS TCP/TLS reachable (TLSv1.3, 391ms). Credentials absent. This blocker CANNOT be resolved in this execution environment.** — see INITIAL TASK MESSAGE below.
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T09:28:33Z) — C287 OPERATIONAL HARDENING CAMPAIGN: HEAVY WORK REQUIRED, NO AVOIDANCE, ENV BLOCKER MAY REQUIRE EXTERNAL EXECUTION

**C287 is the only permitted focus** (C281B→C286 closed NOT_TRADABLE; no reruns/edits to frozen artifacts). Deliverable: a **working, auditable Binance Spot Testnet gateway with hard kill-switch** executing the C285/C286 signal family (11 assets, 5m bars, causal 1h-volume alignment, 5m cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`) with fail-closed gates, audit hash-chain logging, and provable zero-drift (tolerance 1e-9).

**Current verified state:** `python -m pytest tests/ -q` green; Step 0 + preflight_c285 + preflight_c286 green. Deterministic C286-aligned signal artifact present and verified (`data/cache/signal_c286_5m_aligned.pkl`, SHA `d490289e3a0d60bcdd9f0fc56f5da0e43d3b21747b1541db1a31dc6c5859f1b5`, meta/provenance SHA256-from-bytes). `scripts/preflight_c287.py` and `scripts/run_c287_testnet_gateway.py` exist and are runnable (exit 2, 4 blockers: missing `BINANCE_TESTNET_API_KEY/SECRET` env; REST ping/time/exchangeInfo HTTP 451 from `https://testnet.binance.vision` — geographic CDN block, CloudFront X-Amz-Cf-Pop IAD89-P3, not transient; WS TCP/TLS reachable TLSv1.3 391ms). Credentials absent. Formal BLOCKED C287 artifacts emitted 2026-11-13T09:28:33Z with SHA256-from-bytes (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`).

**This blocker CANNOT be resolved from this execution environment** (geographic CDN restriction). The next session must do heavy work, not narration:

**Mandatory execution path (heavy work, no status-only turn):**
1. **Step 0 (idempotent, 900000 ms):**
   ```bash
   cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
   python scripts/bootstrap_dev_env.py --json
   python scripts/verify_env.py --json
   python scripts/preflight_c285.py --json
   python scripts/preflight_c286.py --json
   python scripts/preflight_c287.py --json
   ```
   If `data/cache/signal_c286_5m_aligned.(parquet|pkl)` is missing, run `python scripts/run_c287_testnet_gateway.py --generate-signal` (deterministic from verified caches). Capture exact preflight JSON.
2. **If `ready: true`:** execute `scripts/run_c287_testnet_gateway.py --run` on **Binance Spot Testnet** for ≥72h / ≥500 rebalance cycles (smoke-only does not count). Produce all five required timestamped artifacts with SHA256-from-bytes, `drift_free: true`, all kill-switch thresholds tested/passed, update `research_state/state.yaml` + this file, and keep `python -m pytest tests/ -q` green.
3. **If `ready: false` (current):** do NOT stop at narration. (a) capture exact preflight JSON; (b) attempt concrete unblock actions possible in-session (generate/verify signal artifact — done, verify caches, rerun preflight); (c) emit fresh formal BLOCKED artifacts via `python scripts/run_c287_testnet_gateway.py --blocker-artifacts` with current blockers and SHA256-from-bytes; (d) add/update tests for any changed code/behavior; (e) update `research_state/state.yaml` + this file with current blockers/artifact paths+SHAs; (f) ensure `python -m pytest tests/ -q` green. A turn without (c)-(f) persisted is a failed handoff.

**No avoidance (binding):** no status-only/planning-only/inventory-only turn. No reruns/edits to C281B→C286 frozen artifacts. No weakened gates/thresholds/kill-switch/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data, no simulated fills presented as real. Existing deps only. No `.github/workflows/main.yml` edits. No `HANDOFF.md`. If C287 cannot achieve drift-free or kill-switch fails, record formal blocker/failure artifacts and stop without declaring success.

### C287 specification (pre-registered; no post-hoc scope creep)
- **Gateway**: Binance Spot Testnet REST + WebSocket (official endpoints only). No mainnet, no futures, no margin. API keys stored in environment variables only; never in repo, never logged.
- **Universe**: 11 spot assets (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP) — same as C285/C286.
- **Signal ingestion**: consume the C285/C286 pre-computed signal parquet (features: `z_logqv`, `qv_ratio`, `qv_vol`; lookbacks `L ∈ {168, 336, 720}` 1h bars) aligned causally to 5m execution bars — 1h volume at bar t usable only at 5m bars ≥ t+1h; signal uses data through `t-1`; weights shifted by 1 bar before execution. If no pre-computed signal parquet exists in-repo, the gateway must generate it deterministically from the verified 1h volume + 5m spot caches using the C286 causal alignment/feature definitions and persist it with SHA256-from-bytes before live/testnet operation (and record its path/hash in artifacts).
- **Execution loop**: 5m rebalance cadence. At each bar: (a) fetch 5m klines for all 11 assets; (b) verify causal 1h-volume alignment; (c) load signal for candidate lookback; (d) apply fail-closed gates (see below); (e) compute target weights (top/bottom K, K ∈ {2,3,5}, equal weight 0.5/K per leg, gross 1.0, dollar-neutral, per-asset cap 0.5); (f) place market orders with Binance testnet; (g) record fills, fees, slippage, latency.
- **Kill-switch** (hard, fail-closed): independent watchdog process monitoring (1) cumulative realized PnL vs. daily loss limit, (2) gross exposure vs. max gross, (3) per-asset position vs. cap, (4) WebSocket/REST latency > threshold, (5) consecutive failed gate evaluations > threshold, (6) manual kill signal via file/flag. On trigger: cancel all open orders, flatten all positions to zero via market orders, disable further order placement, emit audit record, require manual reset with signed confirmation.
- **Audit logging**: every decision (gate pass/fail, weight calc, order place/cancel/fill, kill-switch event) written to append-only JSONL with timestamp, bar, asset, side, qty, price, fee, slippage_bps, latency_ms, gate_reasons. SHA256 hash chain across lines for tamper evidence.
- **Zero-drift verification**: backtest replay of live signals on the same 5m cache must produce identical weights, fills (simulated), and PnL to the live run within numerical tolerance (1e-9). Any divergence blocks further live operation.
- **Cost model**: 5m execution, fee + slippage grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps (same as C285/C286). Live fills must be tagged with observed fee/slippage for post-trade cost analysis.
- **Run duration**: minimum 72 hours continuous testnet operation (or until kill-switch triggers) with at least 500 rebalance cycles completed. (A smoke-only run does not satisfy completion.)
- **Pre-registered config grid**: 3 features × 3 lookbacks × 3 K × 3 holds = **81 signal variants**. Each variant must be testable via config flag; the campaign runs ONE variant per 72h window (no simultaneous multi-variant). Variant selection is pre-committed before each window.

### C287 fail-closed gates (do not weaken)
At each 5m rebalance bar, require all of:
- Binance testnet REST + WebSocket both healthy (200 OK, WS connected, latency < 500ms p95).
- 5m klines for all 11 assets received, finite, strictly positive, no gaps > 1 bar.
- Causally aligned 1h quote-volume observation for all 11 assets finite and strictly positive.
- Selected signal finite for at least `2K` assets.
- Cross-sectional signal dispersion > 0.
- No NaN/non-finite 5m price in any selected leg.
- Kill-switch watchdog process alive and responsive (heartbeat < 5s).
- No missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, block the rebalance, record the reason, and do not place orders. The C286 gate set is the baseline; C287 adds connectivity, kill-switch health, and audit-chain integrity.

### C287 required artifacts (exact names, timestamped)
- `reports/campaign287_gateway_spec_<ts>.json` — gateway config, endpoints, auth handling, kill-switch parameters, audit schema.
- `reports/campaign287_live_run_<ts>.json` — per-bar decisions, gate results, orders, fills, fees, slippage, latency, kill-switch events (or blocker evidence in blocked mode).
- `reports/campaign287_drift_report_<ts>.json` — backtest replay vs. live comparison for the run window; max absolute weight diff, PnL diff, fill count diff; `drift_free: true` iff all diffs within tolerance (or explicit blocked/inapplicable with reason).
- `reports/campaign287_kill_switch_test_<ts>.json` — documented kill-switch trigger test (simulated breach of each threshold) with before/after state, flatten confirmation, audit chain integrity (or explicit blocked/inapplicable with reason).
- `reports/campaign287_summary_<ts>.json` — aggregate: bars run, cycles completed, total fees, total slippage, max drawdown, kill-switch activations, drift-free confirmation.
Each must include `real_data_only: true`, `fabricated_data: false`, the spot/volume/meta/provenance SHA256s, the signal variant config (or deterministic generation spec), and SHA256-from-bytes for each artifact. Then update the state fields in `research_state/state.yaml` and this file.

### C287 anti-avoidance rules (binding)
- No status-only, planning-only, or inventory-only turn.
- Do not rerun C281B, C281C, C282, C283, C284, C285, or C286; do not edit their frozen artifacts.
- Do not weaken gates, thresholds, kill-switch parameters, or the drift tolerance; do not cherry-pick windows.
- No synthetic/fabricated data, no relabeling old caches, no simulated fills without real testnet API calls.
- Use existing dependencies only (numpy/pandas/scipy/statsmodels/aiohttp/pydantic); do not add a new framework.
- C287 must execute on Binance testnet spot with real 5m market data; a paper-trading-only or simulated-gateway variant is forbidden (except fail-closed BLOCKED artifacts that explicitly report no real exchange interaction).
- If C287 cannot achieve drift-free operation or kill-switch fails any test, record a formal blocker/failure artifact and stop; do not declare success.
- **No avoidance path:** do not substitute infra/refactor/docs/status/planning work for C287. The only acceptable outcomes are (a) full C287 artifacts + state/handoff update + green tests from a real ≥72h/≥500-cycle testnet run, or (b) full fail-closed BLOCKED C287 artifacts + runnable gateway/preflight + tests + state/handoff update + green tests documenting concrete unresolvable dependency/gateway failure (no fabricated results).

### C287 completion gate (a turn that ends without this is a failed handoff)
The session is not done until ALL of these are true and persisted:
1. `scripts/preflight_c287.py` executed and its result captured; `scripts/run_c287_testnet_gateway.py` exists and is runnable.
2. Either (A) executed end-to-end on Binance testnet for ≥72h / ≥500 rebalance cycles with `drift_free: true` and all kill-switch thresholds tested/passed, OR (B) a fail-closed BLOCKED run with concrete blockers evidenced by preflight/capability probes and no fabricated fills.
3. All five artifacts exist with fresh timestamps and SHA256-from-bytes: `reports/campaign287_gateway_spec_<ts>.json`, `reports/campaign287_live_run_<ts>.json`, `reports/campaign287_drift_report_<ts>.json`, `reports/campaign287_kill_switch_test_<ts>.json`, `reports/campaign287_summary_<ts>.json`.
4. `research_state/state.yaml` and this file record the result, blocker/ready status, artifact paths, and SHA256-from-bytes.
5. `python -m pytest tests/ -q` still passes (add/update tests for any new/changed code).
Ending a turn with only a plan, a status update, a partial implementation, or a smoke test (and no BLOCKED artifacts when preflight fails) does NOT satisfy the handoff and must be continued.

### Deferred campaigns (do not start early)
- **C288+ — future economic stat-arb campaigns:** require C287 drift-free gateway as prerequisite.

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

**C287 preflight (before running the campaign):** `scripts/preflight_c287.py` (now present) verifies Binance testnet REST + WebSocket connectivity, API key presence in environment, 5m spot cache + 1h volume cache availability for signal alignment, and presence/loadability of any required pre-computed C285/C286 signal parquet (fail-closed blocker if missing). It must print `"ready": true`; any mismatch is fail-closed.

## Bottlenecks removed (so heavy work can continue)
- **Dependency bootstrap:** `scripts/bootstrap_dev_env.py` + `scripts/verify_env.py` install and verify runtime and test imports, including `hmmlearn`, `pydantic`, `aiohttp`, and `pytest-asyncio`; the old Step 0 omitted the test-only imports.
- **Signal artifact blocker:** removed — deterministic C286-aligned signal artifact `data/cache/signal_c286_5m_aligned.pkl` (SHA `d490289e3a0d60bcdd9f0fc56f5da0e43d3b21747b1541db1a31dc6c5859f1b5`, meta/provenance SHA256-from-bytes) generated from verified caches; preflight_c287 accepts parquet-or-pickle.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is explicitly forbidden. Agents that previously tried to edit a non-existent `HANDOFF.md` must ignore the missing-file error and continue.
- **Controller progress accounting:** `scripts/controller_progress.py` is restored; the scheduled workflow can now credit non-workflow commits instead of treating every session as no progress.
- **Missing controller tests:** `tests/test_controller_progress_accounting.py`, `tests/test_workflow_diagnostics_scanner.py`, `tests/test_nonfinite_result_serialization.py`, and `tests/test_campaign_resume.py` are restored so the workflow's controller-tests step is not blocked by missing files.
- **C287 gateway script:** `scripts/run_c287_testnet_gateway.py` created — runnable with `--blocker-artifacts`; emits the five formal BLOCKED C287 artifacts from real preflight/capability evidence (no fabricated fills, `real_data_only: true`, `fabricated_data: false`, `blocker: true`, SHA256-from-bytes per artifact); includes full fail-closed gate/kill-switch/audit/hash-chain/zero-drift logic behind `--run`.
- **C287 tests:** `tests/test_preflight_c287.py` and `tests/test_c287_gateway_fail_closed.py` added covering preflight SHA pinning/ready/blockers, gateway fail-closed gates (no permissive missing), kill-switch trigger/flatten/manual-reset, and audit hash-chain tamper evidence.

**Remaining unresolved blocker (external):** missing `BINANCE_TESTNET_API_KEY/SECRET` env vars + REST reachability to `testnet.binance.vision` (HTTP 451 geographic CDN block from this egress IP; WS reachable). Cannot be resolved in this environment. Next session must run from an allowed network with testnet keys in env (then `--run`), or re-emit fresh fail-closed BLOCKED artifacts with current evidence + state/handoff update + green tests.

## Current research state (verified 2026-11-13T07:30Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evaluations | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |
| C284 | Kalman dynamic-hedge-ratio pairs, 28 WF splits, 5 cost slices, fail-closed gates | 1088 | `NOT_TRADABLE`, 0 exposure, binding: zero_exposure |
| C285 | Volume-conditioned cross-sectional stat-arb, 11 assets, 26 WF splits, 5 cost slices | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C286 | 5m execution overlay of C285 signal, real 26,208-bar 5m spot cache, causal 1h-volume alignment, 5m costs, 151 WF splits, 81 runs | 81 | `NOT_TRADABLE`, 0 edge, binding constraint recorded |

Frozen evidence:
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding constraint `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (SHA `2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (SHA `23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (SHA `512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (SHA `2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding constraint `reports/campaign285_binding_constraint_20261113T065205Z.json` (SHA `15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
- C286: `reports/campaign286_oos_sweep_20261113T072725Z.json` (SHA `c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca`); registry `reports/campaign286_tradable_edge_registry_20261113T072725Z.json` (SHA `6f7eb06d56abbfde9273973f38264574f4d36443e127da8b55334b7fb6977d8f`); summary `reports/campaign286_summary_20261113T072725Z.json` (SHA `9f4d987e776b91a70efaaf6dbe472b7058a523dc481d74bf9bc3e99df67ae9da`); verdict `reports/campaign286_verdict_20261113T072725Z.json` (SHA `338e4b5dec412bcef32b0b37fd88865543ced68cfe0e94749247ce4bad7fb9fe`); binding constraint `reports/campaign286_binding_constraint_20261113T072725Z.json` (SHA `b0d7f0d9e9ac67efd501fe9ae814273ad036eaa9f2534711475003f528ddcf12`).
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
python scripts/preflight_c287.py --json
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
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285 is complete and frozen; current next campaign is **C287**.

**END OF HANDOFF — refreshed 2026-11-13T09:28:33Z.** The spot-only price-only edge search is closed (C281B→C284 all NOT_TRADABLE) and the volume-conditioned cross-sectional family is closed NOT_TRADABLE (C285 and C286 both formal negative results). **C286 is COMPLETE — frozen.** **C287 (operational hardening: testnet gateway/kill-switch) is ACTIVE/BLOCKED.** `scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` are runnable; a deterministic C286-aligned signal artifact from verified caches is now present (`data/cache/signal_c286_5m_aligned.pkl`, SHA `d490289e3a0d60bcdd9f0fc56f5da0e43d3b21747b1541db1a31dc6c5859f1b5`, meta/provenance SHA256-from-bytes). Formal BLOCKED C287 artifacts 2026-11-13T09:28:33Z exist with SHA256-from-bytes (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Remaining blockers: missing `BINANCE_TESTNET_API_KEY/SECRET` env vars and REST reachability to `testnet.binance.vision` (HTTP 451 from this environment; WS reachable TLSv1.3). **This blocker is a geographic CDN restriction (CloudFront, X-Amz-Cf-Pop IAD89-P3) that CANNOT be resolved from this execution environment.** Next session: run Step 0 + preflights; if `ready:true` execute `--run` on Binance Spot Testnet for ≥72h/≥500 cycles with `drift_free:true` and all kill-switch thresholds tested/passed; if still blocked re-emit fail-closed BLOCKED artifacts from real evidence, update `research_state/state.yaml` + AGENTS.md, keep tests green. **No avoidance:** do not substitute infra/refactor/docs/status/planning work for C287. A status-only turn is a failed handoff.
