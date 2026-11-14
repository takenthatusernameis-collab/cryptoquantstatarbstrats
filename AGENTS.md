# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-14T22:24:22Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.

**Verified state (as of 2026-11-14T22:24:22Z, handoff checked 2026-11-14T22:24:22Z):** `python -m pytest tests/ -q` → **1358 passed, 2 skipped, 0 failed** (284.5s; includes 19 new C302 tests). Deps import-verified: numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. **Dependency note:** `pytest-asyncio` (declared in `[project.optional-dependencies].dev` but may be absent from runtime) is required for `tests/test_playbooks.py` (16 async tests); install via `python -m pip install "pytest-asyncio>=0.23"` if missing — a bootstrap gap, NOT a research result. The economic stat-arb program is **NOT closed — a new real data family (premium index) was reachable and has been added**:

- **C302 (NEW real family: USDT-M perp `premiumIndexKlines` / continuous fair-value premium, native 1h, 2020-01..2026-10, 486 runs):** executed end-to-end at `20261114T215720Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/486 edge**, 446 with exposure / 40 zero-exposure, binding `mean_beats_benchmark_fail`. This is a genuinely new real signal family (the real-time premium index that drives funding) distinct from C291/C293/C298/C299/C300 (funding/basis) and C301 (OFI). Cache `data/cache/campaign302_premium_index_basis.pkl` = 7,192,198 B, SHA256 `2f0b45cff41baecf1ab4ddb52de68664ad91f3a4a6f95086f0fc468f7cd86063`. Artifacts `reports/campaign302_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261114T215720Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.
- **C281B→C301:** all **COMPLETE formal negative results** (0 costed-OOS edge, frozen). Binding constraints: `cost_sensitivity` / `zero_exposure` / `mean_beats_benchmark_fail`.
- **C287 (external execution / testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient), `fapi` 451, bybit 403, no credentials. **Cannot be resolved from this execution environment.** External execution is the only remaining path to a tradable claim, but it is blocked by geography/credentials and **decoupled from economic progress**; do not re-probe as economic work.

**Bottleneck status this refresh:** (1) The prior "VERIFY & MONITOR ONLY / no further campaign" stance was the main progress bottleneck — it told future agents NOT to do heavy economic work. It is **removed**: a concrete, heavy, reachable next campaign (C303) is now registered. (2) `pytest-asyncio` runtime gap fixed (see above). (3) The GitHub 100 MB push limit is resolved (compact ndarray caches < 100 MB; C302 cache 7.19 MB). (4) C287 is an **external-only blocker** — record it as blocked/decoupled; it must not preempt or be mistaken for economic work.

**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-14T22:24:22Z) — EXECUTE C303: CROSS-SECTIONAL PREMIUM-INDEX CARRY (HEAVY WORK, MANDATORY)

**C302 is a COMPLETE formal negative (0/486 costed-OOS edge, binding `mean_beats_benchmark_fail`) and is FROZEN.** The program is **not** closed: a new real data family (`premiumIndexKlines`) is reachable and only its per-asset time-series form has been tested. **Do NOT re-run C302 or re-skin the closed funding/basis/OFI families.**

**ACTIVE NEXT CAMPAIGN = C303 — cross-sectional premium-index carry across a large real perp universe.** This directly attacks the binding constraint (`zero_exposure`) that closed C298: C298 had only 3 full-coverage assets (< 2K for every K), so every cross-sectional rebalance was blocked. Verified this refresh: **10 real USDT-M perps have full `premiumIndexKlines` coverage from 2020-01** (BTCUSDT, ETHUSDT, XRPUSDT, ADAUSDT, LTCUSDT, BCHUSDT, LINKUSDT, TRXUSDT, ETCUSDT, XLMUSDT), so K ∈ {2,3,5} is now reachable and every rebalance can have real exposure. That is the heavy work: a genuinely new formulation (cross-sectional premium-index carry/dispersion), not a re-skin.

**MANDATORY heavy work — do this in one session (no status-only / planning-only turns):**
1. **Step 0 bootstrap:** `python scripts/bootstrap_dev_env.py` then `python -m pytest tests/ -q` green (0 failed). If `pytest-asyncio` is missing, `python -m pip install "pytest-asyncio>=0.23"` (bootstrap gap, not a research result).
2. **Ingest (real, fail-closed):** build `scripts/ingest_c303_premium_index_xsec.py` that downloads the 10 verified assets' `premiumIndexKlines` 1h archives (`https://data.binance.vision/data/futures/um/monthly/premiumIndexKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip`, 2020-01..2026-10), aligns to a common real 1h grid, and reuses C299/C302 real perp close + native 8h funding for execution/PnL. Reuse the C302 ingest patterns (`read_premium_zip` header/no-header generic, per-asset contiguous window, NaN gap bars never imputed). Persist `data/cache/campaign303_premium_index_xsec.pkl` (+ `.meta.json`, `.provenance.json`) as compact ndarrays < 100 MB, SHA256-from-bytes, `real_data_only:true fabricated_data:false executed_fills:false`. Assert < 100 MB before success.
3. **Preflight:** `scripts/preflight_c303.py` fail-closed (mirror `preflight_c302.py`): meta flags/interval/window/host/SHA/size, per-asset premium OHLC present-finite + NaN gaps never imputed, funding boundary/staleness, common-grid cross-sectional coverage ≥ 2K for K∈{2,3,5}, WF fit, warmup, provenance.
4. **Runner (costed OOS):** `scripts/run_c303_premium_index_xsec_oos.py` — cross-sectional premium-index carry. Pre-register the grid BEFORE OOS and freeze it: signals (e.g. premium level, premium z, premium dispersion/momentum) × lookbacks × K ∈ {2,3,5} × holds; **≥ 400 runs total** to be unmistakably heavy. Each rebalance: rank the real cross-section by the causal premium signal, long top-K / short bottom-K (dollar-neutral, gross 1.0), apply from the next bar (shift(1)); real funding cashflow `-rate*signed_weight` at each native boundary (causal); cost grid exactly `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps on turnover. Benchmarks on the SAME WF windows: flat and equal-weight B&H-with-funding. **Edge rule identical to C285–C302, never relaxed:** `oos_edge_proven=true` IFF OOS exposure > 0 AND every cost slice OOS net sum > 0 AND mean of per-split OOS net means > mean of per-split equal-weight B&H-with-funding OOS net means AND > flat. Emit the 5 timestamped artifacts (`campaign303_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json`) with real-data flags + SHA256-from-bytes.
5. **Tests:** `tests/test_preflight_c303.py` + `tests/test_c303_premium_index_xsec_oos.py` (mirror C302 tests: causal/no-lookahead, dollar-neutral top-K/bottom-K, NaN-gap flat, edge rule re-derivation, artifact flags+SHA, no-edge-claimed). Full suite green (0 failed).
6. **Sync:** update `AGENTS.md` (`updated_at_utc`, `active_initial_task`, `next_campaign`, C302/C303 records) and `research_state/state.yaml` with all paths + SHA256-from-bytes (no zeros, no nesting regression). Re-verify pytest green.

**Interpret the outcome honestly:** if C303 is NOT_TRADABLE, record the formal negative (binding constraint) and register the next genuinely-new reachable family (e.g. `markPriceKlines`/`indexPriceKlines` basis, or `bookTicker` quote-side). **Never** claim a tradable edge without a passed costed-OOS rule, never fabricate data/fills/credentials, never weaken gates/costs/edge rule, never relabel data, never edit `.github/workflows/main.yml`, never create/read/edit `HANDOFF.md`. C287 (external execution) stays blocked/decoupled and must not be retried as economic work.

## RESEARCH PROGRAM STATUS (C281B–C302 frozen; C303 active)

**Status:** C281B→C301 (all COMPLETE formal negatives, frozen) plus **C302** (new premium-index per-asset family, COMPLETE formal negative, frozen) returned **0 costed OOS edge** on the formulations/windows tested. The real-archive funding-carry / spot-perp basis family, the OFI/trade-sign autocorrelation family, and the **per-asset premium-index** family are CLOSED. **C303 (cross-sectional premium-index carry) is the ACTIVE heavy next campaign** and directly attacks C298's `zero_exposure` bottleneck (10 real full-coverage assets now vs 3).

**Verified closure (fail-closed, no fabricated data, full provenance):**
- **Single-venue 5m spot** (Binance): C281B, C282, C283, C284, C285, C286, C288, C289, C290 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity / zero_exposure)
- **Real USDT-M perp funding/basis** (Binance data-api): C291 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity)
- **Cross-venue real-spot basis/lead-lag** (Binance+OKX): C292 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity)
- **Cross-venue perp funding-carry** (OKX+Binance): C293 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity)
- **Real implied-vol VRP / BTC-ETH relative value** (Deribit DVOL + Binance): C294 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity; variance-swap proxy wrong-way 0/27)
- **Three-venue real 5m spot cross-venue basis/dispersion/lead-lag** (Binance+OKX+Coinbase): C295 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity; 92/162 gross-positive at 0bps, 0/162 net-positive at ≥5bps)
- **Deribit options term-structure/skew** (deep per-strike mark IV): C296 — **DATA_BLOCKED** (no endpoint yields historical per-strike IV time series)
- **Daily multi-year cross-sectional stat-arb** (real mainnet Binance spot 1d OHLCV, 24 assets, 2021-01-01..2026-11-13): C297 — **CLOSED** (NOT_TRADABLE, binding: mean_beats_benchmark_fail; 81/135 gross-positive at 0bps max +2.152, 0/135 beat equal-weight B&H after costs)
- **Multi-year perp funding/basis, cross-sectional** (real USDT-M + spot, 1h, 3 full-coverage assets): C298 — **CLOSED** (NOT_TRADABLE, binding: zero_exposure; 162/162 zero-exposure, 2K universe gate never met)
- **Multi-year perp funding/basis, per-asset time-series** (real USDT-M + spot, 1h, 3 full-coverage assets): C299 — **CLOSED** (NOT_TRADABLE, binding: mean_beats_benchmark_fail; 486 runs, 0/486 edge)
- **Multi-year perp funding/basis, per-asset time-series, NATIVE 5m + execution overlay** (real USDT-M + spot + native 8h funding, 3 full-coverage assets): C300 — **CLOSED** (NOT_TRADABLE, binding: mean_beats_benchmark_fail; 648 runs, 621 with exposure, 0/648 edge)
- **Real OFI / trade-sign autocorrelation per-asset time-series** (Binance USDT-M perp aggTrades, 2023-01..02): C301 — **CLOSED** (NOT_TRADABLE, binding: mean_beats_benchmark_fail; 648 runs, 545 with exposure / 103 zero-exposure, 0/648 edge)
- **Real premium-index (continuous fair-value premium) per-asset time-series** (Binance USDT-M perp premiumIndexKlines, 1h, 2020-01..2026-10, 3 full-coverage assets): C302 — **CLOSED** (NOT_TRADABLE, binding: mean_beats_benchmark_fail; 486 runs, 446 with exposure / 40 zero-exposure, 0/486 edge)
- **C303 cross-sectional premium-index carry** (10 real full-coverage assets, K∈{2,3,5}): **ACTIVE — NEXT HEAVY CAMPAIGN** (see INITIAL TASK MESSAGE above)

**C289 multiple-testing closure:** `economic_space_closed: true` over C286+C288 configs (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps). Does not subsume C299/C300/C301/C302 (different formulation/window).

**C287 (testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient) + no credentials. Cannot be resolved from this execution environment. External execution capability is the only remaining path to a tradable claim, but it is blocked by geography/credentials and decoupled from economic progress.

**Program closure status (this refresh):** SUPERSEDED — the prior "program closure / verify & monitor only" record is replaced by the C303 active campaign. `reachable_real_data_cross_sectional_stat_arb_space` is **NOT** closed: the premium-index family (C302 per-asset) is a new reachable real source, and its cross-sectional form (C303) is registered as heavy work. `edge_claim: NONE`, `oos_edge_proven: false`, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false` for all frozen campaigns.

**Environment / verification**

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python scripts/verify_env.py --json
python scripts/bootstrap_dev_env.py
python -m pip install "pytest-asyncio>=0.23"   # only if test_playbooks async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified; suite 1358 passed / 2 skipped / 0 failed with `pytest-asyncio` installed). `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact/closure record `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid plus real cashflow legs; zero-cost runs are labeled; any model PnL is explicitly labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — economic stat-arb (costed OOS PnL) is the priority; operational hardening (C287) must not preempt or block it. C287 is blocked externally and decoupled; record it, do not retry it as economic work.

## Escalation

- **C302 (COMPLETE formal negative, frozen):** real premium-index per-asset time-series NOT_TRADABLE, 486 runs, 446 with exposure / 40 zero-exposure, 0/486 edge, binding `mean_beats_benchmark_fail`. New real family (continuous fair-value premium).
- **C301 (COMPLETE formal negative, frozen):** real OFI / trade-sign autocorrelation per-asset time-series NOT_TRADABLE, 648 runs, 545 with exposure / 103 zero-exposure, 0/648 edge, binding `mean_beats_benchmark_fail`. Closes the microstructure family.
- **C300 / C299 / C298 (COMPLETE formal negative, frozen):** perp funding/basis per-asset time-series (1h & 5m) and cross-sectional — all NOT_TRADABLE, 0 edge.
- **C297 (COMPLETE formal negative):** daily multi-year cross-sectional stat-arb NOT_TRADABLE (0/135 costed OOS edge, binding mean_beats_benchmark_fail).
- **C296 (COMPLETE data-blocked closure):** Deribit options term-structure/skew — no deep historical per-strike mark IV feed reachable.
- C295 (frozen, NOT_TRADABLE): three-venue 5m spot, 0/162 edge, binding cost_sensitivity.
- C294 (frozen): Deribit DVOL + Binance VRP, closed NOT_TRADABLE.
- C293 (frozen): OKX funding + Binance funding (C291 cache).
- C292 (frozen): Binance+OKX 5m cross-venue spot basis.
- C291 (frozen): `data.binance.vision` USDT-M 5m klines + fundingRate archives. `fapi.binance.com` remains HTTP 451.
- Binance API/host changes → `data/real_feed_loader.py` host chain. Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable). Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C281B–C302 complete and frozen; **C303 is the active campaign**; C287 (external execution) remains BLOCKED/decoupled and external to this environment.
