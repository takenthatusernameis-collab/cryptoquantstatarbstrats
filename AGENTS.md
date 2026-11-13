# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T09:54:27Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable spot data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **green (1149 passed, 2 skipped)**. C281B→C286 are **COMPLETE — formal negative results** (NOT_TRADABLE, 0 edge). **C288 (new price-derived realized-volatility / skewness cross-sectional stat-arb) is COMPLETE — formal negative result (NOT_TRADABLE, 0/81).** **C289 (OOS multiple-testing + minimum-detectable-edge closure over C286+C288, 162 configs) is COMPLETE — the economic space on this dataset is statistically CLOSED (0 configs survive Holm/BH at any cost slice incl. zero; all fee10 Sharpes negative; well-powered).** **C287 (operational hardening: testnet gateway/kill-switch) is BLOCKED by an unresolvable-in-this-environment geographic CDN block (testnet REST HTTP 451; credentials absent) and is now DECOUPLED from economic progress — it does NOT gate the next economic campaign.**
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T09:54:27Z) — C290 WIDER-UNIVERSE TRUE-5M-OHLCV CROSS-SECTIONAL STAT-ARB: HEAVY WORK REQUIRED, NO AVOIDANCE

**Focus = C290 (economic stat-arb).** The 11-asset close-price + 1h-quote-volume spot space is now statistically closed (C281B→C286 NOT_TRADABLE; C288 realized-vol/skew NOT_TRADABLE; C289 closure `economic_space_closed: true`). C287 is blocked and decoupled (see below). The ONE economic lever still reachable from THIS execution environment is **mainnet public spot klines with full 5m OHLCV (open/high/low/close/volume) on a WIDER universe** — verified reachable (`data-api.binance.vision/api/v3/klines` → HTTP 200; `/api/v3/exchangeInfo` → 200). This is a genuinely new data dimension (true-5m intrabar-range realized vol + true-5m quote volume, never used before) on a wider cross-section, and it is the correct next heavy experiment: does the C289 negative result hold for a bigger universe and finer (true-5m) data?

**Deliverable (C290):** a complete, runnable, tested, pre-registered, costed OOS economic campaign:
1. **Ingest** real mainnet public spot 5m klines (OHLCV + column-5 quote volume) for a **wider USDT spot universe** (e.g. the top ~30 USDT spot pairs by 1h quote volume, verified to exist on the exchange) over the window 2026-08-01T00:00Z → 2026-10-30T23:55Z (extend earlier if the longer 1h cache is used). Persist with **SHA256-from-bytes** + a meta/provenance JSON recording `real_data_only: true`, `fabricated_data: false`, source host/endpoint, blocked routes, and per-symbol bar counts. Use `data/loader.py::DataLoader.load_binance_data` and/or `data/real_feed_loader.py`; host chain in `data/real_feed_loader.py`. **No synthetic data, no relabeled old caches, no resampling of a derived series.**
2. **Mechanism (new):** cross-sectional stat-arb on **true-5m** features — (a) intrabar range realized vol `(high-low)/close` (and 5m close-to-close realized vol), (b) true 5m quote-volume features `z_logqv`, `qv_ratio`, `qv_vol` (computed at true 5m, not 1h→5m), (c) 5m close realized skew. Long top-K / short bottom-K, K∈{2,3,5}, equal weight 0.5/K per leg, gross 1.0, dollar-neutral, per-asset cap 0.5; hold H∈{1,6,24} 5m bars; `weights.shift(1).fillna(0.0)`; 5m cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; walk-forward train=720/test=168/step=168 (151 OOS splits); fail-closed causal gates; **identical edge rule** as C285/C286/C288 (OOS exposure>0 AND all cost slices net sum>0 AND mean per-split OOS net mean > mean per-split equal-weight B&H OOS net mean on the same WF windows). Full pre-registered grid reported (no post-hoc search, no cherry-picking).
3. **Build** `scripts/preflight_c290.py` (fail-closed: verify ingested cache SHAs, shape, window, no NaNs, positive prices, 5m spacing, WF math, feature warmup) and `scripts/run_c290_wider_universe_oohlcv_xsec_oos.py` (mirror `scripts/run_c286_5m_volume_xsec_oos.py` / `scripts/run_c288_realized_vol_xsec_oos.py`), plus tests `tests/test_preflight_c290.py` and `tests/test_c290_wider_universe_oohlcv_xsec_oos.py`.
4. **Run** preflight (must print `"ready": true`) then the full sweep; emit the five timestamped artifacts with SHA256-from-bytes (`campaign290_oos_sweep`, `campaign290_tradable_edge_registry`, `campaign290_summary`, `campaign290_verdict`, and `campaign290_binding_constraint` if NOT_TRADABLE).

**Mandatory execution path (heavy work, no status-only turn):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json          # 900000 ms shell timeout
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json              # must print ready:true (build it if missing)
python scripts/run_c290_wider_universe_oohlcv_xsec_oos.py   # full sweep -> 5 artifacts
python -m pytest tests/ -q                            # must stay green
```
Then update `research_state/state.yaml` + this file with artifact paths + SHA256-from-bytes, and record the verdict.

**If C290 endpoints become unreachable (HTTP 451) or any cache check fails:** do NOT fabricate. Emit fail-closed BLOCKED C290 artifacts (capability probes: exact host/status/blocked route) with SHA256-from-bytes, add tests, update state + this handoff, keep `pytest` green. A turn without persisted artifacts + state/handoff update + green tests is a failed handoff.

**If C290 also closes (likely, given C289):** that is a **definitive result** — record it (binding-constraint artifact + `economic_space_closed: true` at wider universe) and **escalate**: the only remaining economic levers are (i) **new derivatives data** — `data/real_feed_loader.py::fetch_binance_funding_rates` + `compute_funding_carry_metrics` exist but `fapi.binance.com` is **HTTP 451 blocked from this egress** (geographic CDN), and (ii) **live/testnet execution** (C287) — both require execution from an **allowed network**. State this explicitly; do NOT loop on another 11-asset spot signal family.

**No avoidance (binding):** no status-only/planning-only/inventory-only turn. No reruns/edits to frozen artifacts C281B→C286, C288, C289. No weakened gates/thresholds/cost grid/edge rule/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data, no simulated fills presented as real. Existing deps only (numpy/pandas/scipy/statsmodels/scikit-learn/aiohttp/pydantic). No `.github/workflows/main.yml` edits. No `HANDOFF.md`.

### C287 status — BLOCKED, DECOUPLED (do not let it block economic work)
`scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` exist and are runnable (fail-closed BLOCKED artifacts already emitted 2026-11-13T09:28:33Z: gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Blockers: missing `BINANCE_TESTNET_API_KEY/SECRET`; REST ping/time/exchangeInfo **HTTP 451** from `testnet.binance.vision` (CloudFront, X-Amz-Cf-Pop IAD89-P3, geographic, not transient); WS TCP/TLS reachable (TLSv1.3, ~346 ms). **Cannot be resolved from this execution environment.** The prior handoff's self-imposed rule "C288+ requires the C287 drift-free gateway" is **REMOVED** — economic research proceeds on reachable real data (mainnet public klines are sanctioned backtest data per README); C287 requires execution from an allowed network with testnet keys. Do not re-emit C287 BLOCKED artifacts every session (already done); only re-run `--blocker-artifacts` if new capability evidence changes.

### C290 specification (pre-registered; no post-hoc scope creep)
- **Data**: real mainnet public spot 5m klines (OHLCV + quote volume), wider USDT spot universe (top ~30 by 1h quote volume, verified to exist), window 2026-08-01T00:00Z → 2026-10-30T23:55Z (or longer). SHA256-from-bytes + meta/provenance; `real_data_only: true`, `fabricated_data: false`.
- **Features (true-5m)**: `rv_range = rolling_std/mean of (high-low)/close`; `rv_close = rolling std of 5m log-returns`; `z_logqv`, `qv_ratio`, `qv_vol` from true-5m quote volume; `skew` = rolling skew of 5m log-returns. Lookbacks L ∈ {288, 1008, 2016} 5m bars.
- **Portfolio**: long top-K / short bottom-K by score, K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; hold H∈{1,6,24}; `shift(1)`; 5m cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; WF 720/168/168 = 151 splits.
- **Gates (fail-closed)**: feature finite for ≥2K assets; cross-sectional dispersion>0; no NaN/non-finite 5m price in selected legs; block & record reason otherwise; no missing/None/false treated as permissive.
- **Edge rule**: identical to C285/C286/C288 (never relaxed).
- **Required artifacts**: `reports/campaign290_oos_sweep_<ts>.json`, `reports/campaign290_tradable_edge_registry_<ts>.json`, `reports/campaign290_summary_<ts>.json`, `reports/campaign290_verdict_<ts>.json` (+ `campaign290_binding_constraint_<ts>.json` if NOT_TRADABLE), each with `real_data_only: true`, `fabricated_data: false`, dataset SHAs, config, all run results, and SHA256-from-bytes.

### C290 completion gate (a turn that ends without this is a failed handoff)
1. `scripts/preflight_c290.py` exists, executed, `ready: true` (or fail-closed BLOCKED with capability probes if endpoints unreachable); `scripts/run_c290_wider_universe_oohlcv_xsec_oos.py` exists and is runnable.
2. Full sweep executed end-to-end (not smoke-only) with all five artifacts fresh + SHA256-from-bytes.
3. `research_state/state.yaml` and this file record the result, artifact paths, and SHA256-from-bytes.
4. `python -m pytest tests/ -q` green (add/update tests for new code).

## Step 0 — dependency bootstrap and preflight (run before anything else)
The scheduled Kilo worker shell may start without the repo's Python dependencies. Run this idempotent bootstrap first, with a **900000 ms shell timeout**:
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml` (the controller token cannot persist workflow-file changes and it will loop on persistence failure).

## Bottlenecks removed (so heavy work can continue)
- **C287 economic gate removed:** the prior "C288+ requires the C287 drift-free gateway" prerequisite is deleted. Economic campaigns run on reachable real data (mainnet public klines); C287 is a separate, external-execution-only operational track.
- **C288 campaign:** `scripts/preflight_c288.py` + `scripts/run_c288_realized_vol_xsec_oos.py` created and executed end-to-end (new price-derived realized-vol/skew cross-sectional family); five artifacts with SHA256-from-bytes; tests added (`tests/test_preflight_c288.py`, `tests/test_c288_realized_vol_xsec_oos.py`).
- **C289 closure:** `scripts/preflight_c289.py` + `scripts/run_c289_closure.py` created and executed (block-bootstrap p-values, Holm FWER, BH FDR, deflated Sharpe, minimum-detectable-edge over the 162 5m configs); three artifacts with SHA256-from-bytes; tests added (`tests/test_c289_closure.py`). Conclusion: `economic_space_closed: true`.
- **New-data reachability probed:** funding/basis futures API (`fapi.binance.com`) is **HTTP 451** (geographic) — new derivatives data blocked here; mainnet public spot klines (`data-api.binance.vision/api/v3/klines`) are **HTTP 200** — the C290 data source.
- **Dependency bootstrap:** `scripts/bootstrap_dev_env.py` + `scripts/verify_env.py` install and verify runtime + test imports (`hmmlearn`, `pydantic`, `aiohttp`, `pytest-asyncio`).
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is forbidden; ignore missing-file errors for it.
- **Controller progress accounting / missing controller tests:** restored (`scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, `tests/test_workflow_diagnostics_scanner.py`, `tests/test_nonfinite_result_serialization.py`, `tests/test_campaign_resume.py`).

## Current research state (verified 2026-11-13T09:54Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evals | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |
| C284 | Kalman dynamic-hedge-ratio pairs, 28 WF splits, 5 cost slices | 1088 | `NOT_TRADABLE`, 0 exposure, binding: zero_exposure |
| C285 | Volume-conditioned cross-sectional stat-arb, 11 assets, 26 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C286 | 5m execution overlay of C285 signal, 26,208-bar 5m cache, causal 1h-vol, 151 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C287 | Operational hardening: Binance Spot Testnet gateway + kill-switch | — | **BLOCKED** (env: testnet REST HTTP 451 + no creds) |
| C288 | NEW realized-vol / vol-reversal / low-skew cross-sectional stat-arb, 5m close-only, 151 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C289 | OOS multiple-testing + MDE closure over C286+C288 (162 configs) | 810 tests | **`economic_space_closed: true`** (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps) |

Frozen evidence (C281B→C286, C288, C289):
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding constraint `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (SHA `2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (SHA `23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (SHA `512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (SHA `2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding constraint `reports/campaign285_binding_constraint_20261113T065205Z.json` (SHA `15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
- C286: `reports/campaign286_oos_sweep_20261113T072725Z.json` (SHA `c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca`); registry `reports/campaign286_tradable_edge_registry_20261113T072725Z.json` (SHA `6f7eb06d56abbfde9273973f38264574f4d36443e127da8b55334b7fb6977d8f`); summary `reports/campaign286_summary_20261113T072725Z.json` (SHA `9f4d987e776b91a70efaaf6dbe472b7058a523dc481d74bf9bc3e99df67ae9da`); verdict `reports/campaign286_verdict_20261113T072725Z.json` (SHA `338e4b5dec412bcef32b0b37fd88865543ced68cfe0e94749247ce4bad7fb9fe`); binding constraint `reports/campaign286_binding_constraint_20261113T072725Z.json` (SHA `b0d7f0d9e9ac67efd501fe9ae814273ad036eaa9f2534711475003f528ddcf12`).
- C288: `reports/campaign288_oos_sweep_20261113T094728Z.json` (SHA `75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d`); registry `reports/campaign288_tradable_edge_registry_20261113T094728Z.json` (SHA `8c35996e5675d151a5f3b80f4e8f4545a7cb99923adc41e0ad4fa03ef5a7c7d8`); summary `reports/campaign288_summary_20261113T094728Z.json` (SHA `fc236ad1ad51d53fe909444d02648909188b80fab8013e299140e7f292ec8eb5`); verdict `reports/campaign288_verdict_20261113T094728Z.json` (SHA `cb7f80a755a0ce84c8c2bb83ec51a7576d436fea0026303688a5aa596b94419a`); binding constraint `reports/campaign288_binding_constraint_20261113T094728Z.json` (SHA `46248de8b9441b3c3fdcf402d8b0bba2de8bda1c25ef6f66bee085269013c763`). Verdict `NOT_TRADABLE`, 0/81 edge.
- C289: `reports/campaign289_closure_20261113T095308Z.json` (SHA `1abf68af6f9e9d96f158b41b9a0694ed7bc9feba5afed387483bc6069d0f1b77`); summary `reports/campaign289_summary_20261113T095308Z.json` (SHA `7ed5717296df3b146fe1b87747182cc9e2e6f3cf1282e817fac9dfe8ecf09e92`); verdict `reports/campaign289_verdict_20261113T095308Z.json` (SHA `d1a7894e0c38e077d34e24a156bb1c1cfaadab0469729b1cdf1d7236243f52b5`). `economic_space_closed: true`.
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
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c287.py --json
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact records `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; zero-cost runs are labeled.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — economic stat-arb (costed OOS PnL) is the priority; operational hardening (C287) must not preempt or block it.

## Escalation

- New spot data (C290): `data-api.binance.vision/api/v3/klines` (HTTP 200) + `data/loader.py::DataLoader.load_binance_data` + `data/real_feed_loader.py` host chain. Persist with SHA256-from-bytes.
- New derivatives/funding data (economic): `data/real_feed_loader.py::fetch_binance_funding_rates` + `compute_funding_carry_metrics` exist but `fapi.binance.com` is **HTTP 451** here — requires an allowed network.
- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285/C286/C288/C289 are complete and frozen; current next campaign is **C290**.

**END OF HANDOFF — refreshed 2026-11-13T09:54:27Z.** Economic status: the 11-asset close + 1h-quote-volume spot stat-arb space is **closed** (C281B→C286, C288 all NOT_TRADABLE; C289 closure `economic_space_closed: true`). **C288 and C289 are COMPLETE and frozen** (real artifacts + SHA256-from-bytes). **C287 is BLOCKED and decoupled** (testnet REST HTTP 451 + no creds; requires external execution). The only economic lever reachable from this environment is **C290: wider-universe true-5m-OHLCV cross-sectional stat-arb on freshly ingested real mainnet public spot klines** (mainnet klines HTTP 200; funding/basis HTTP 451). Next session MUST build + run C290 end-to-end (heavy work), update state + this file, keep tests green; if C290 also closes, record the definitive wider-universe closure and escalate to external execution (derivatives data or testnet). **No avoidance: a status-only/planning-only turn, or substituting infra/refactor/docs for C290, is a failed handoff.**