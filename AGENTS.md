# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T02:37:00Z (C303 frozen formal negative; C304 EXECUTED end-to-end — real ingest 52,426,602 B cache SHA256 56e27ec2a53b2624ab4cda1a1b4f396ffa4ebbdc9dc7f7995c88cd5153096985, preflight ready:true, costed-OOS runner 432 runs NOT_TRADABLE binding cost_sensitivity, 5 timestamped artifacts 20261115T023125Z, tests added, full suite 1394 passed/2 skipped/0 failed; C304 complete, no active heavy-work campaign)
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics. Any turn that produces neither a real-data ingest, a costed-OOS run, a passing test, or an artifact update is NOT economic progress and must not be reported as such.

**Verified state (quick recheck this refresh, 2026-11-15T01:37:39Z):** `HANDOFF.md` absent (correct). `pytest 9.2.0` and `pytest-asyncio 1.5.0` + deps (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1) import-verified. Last full-suite run recorded in state: **1376 passed, 2 skipped, 0 failed** (293.17s, 2026-11-15T01:22:44Z). C303 templates present on disk to copy: `scripts/ingest_c303_premium_index_xsec.py`, `scripts/preflight_c303.py`, `scripts/run_c303_premium_index_xsec_oos.py`, `tests/test_preflight_c303.py`, `tests/test_c303_premium_index_xsec_oos.py`; `scripts/bootstrap_dev_env.py` and `scripts/verify_env.py` present. `research_state/state.yaml` parses cleanly; `latest_campaign_done: C303`. C304 has **NO scripts / cache / reports yet** (correct — it is the active, unexecuted campaign). **C304 MANDATORY SCRIPT NAMES (do not copy C303 names):** ingest=`scripts/ingest_c304_mark_index_basis_xsec.py`, preflight=`scripts/preflight_c304.py`, runner=`scripts/run_c304_mark_index_basis_xsec_oos.py`, tests=`tests/test_preflight_c304.py` + `tests/test_c304_mark_index_basis_xsec_oos.py`, cache=`data/cache/campaign304_mark_index_basis_xsec.pkl` (+`.meta.json`, `.provenance.json`), artifacts=`reports/campaign304_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json`.

**Bottleneck removed this refresh (C304 FULL chain reachable — do NOT re-probe any of this as unknown):** re-verified 2026-11-15T01:22:44Z from this environment via `https://data.binance.vision/data/futures/um/monthly/...`:
- (a) **mark/index family** — `markPriceKlines` and `indexPriceKlines` 1h monthly zips are HTTP 200 for **all 10 assets** (BTCUSDT, ETHUSDT, XRPUSDT, ADAUSDT, LTCUSDT, BCHUSDT, LINKUSDT, TRXUSDT, ETCUSDT, XLMUSDT) at BOTH `2020-01` AND `2026-10` (**40/40 endpoints 200**) at `.../monthly/{markPriceKlines,indexPriceKlines}/<SYM>/1h/<SYM>-1h-YYYY-MM.zip`.
- (b) **execution-data chain** — perp 1h `klines` AND native 8h `fundingRate` monthly zips are HTTP 200 for all **7 assets NOT in the C299 cache** (XRPUSDT, ADAUSDT, LTCUSDT, LINKUSDT, TRXUSDT, ETCUSDT, XLMUSDT) at BOTH `2020-01` AND `2026-10` (**14/14 endpoints 200**) at `.../monthly/klines/<SYM>/1h/...` and `.../monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip`; BTCUSDT/ETHUSDT/BCHUSDT execution data is reused from the verified C299 cache.
- Archive schema is the standard 12-column kline CSV **with a header row starting `open_time`** (verified on BTCUSDT 2026-10; 745 rows = 1 header + 744 bars). Basis = mark `close` − index `close`.
- **Conclusion: C304 chain fully reachable AND now EXECUTED end-to-end (ingest → preflight ready:true → costed-OOS runner 432 runs → 5 artifacts → tests → sync). No remaining C304 blocker. C304 returned NOT_TRADABLE (binding cost_sensitivity) — formal negative; register the next genuinely-new reachable family if continuing the program.**

**Verified this handoff (2026-11-15T00:40:03Z):** C303 **EXECUTED** (scripts/*c303*, tests/*c303*, data/cache/*campaign303*, reports/*campaign303* all present). Premium-index common intersection grid re-confirmed: 58,959 bars, 2020-01-31 08:00Z → 2026-10-31 23:00Z, all 10 assets present on-grid. C303 result: **NOT_TRADABLE**, `edge_proven:false`, **0/432 edge**, **432/432 with exposure / 0 zero-exposure** (cross-sectional grid solved C298's zero_exposure), binding `cost_sensitivity`. All artifacts carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.

**C303 executed this refresh (2026-11-15T00:26:48Z):** cross-sectional premium-index carry across 10 real assets on the 58,959-bar common premium grid → **NOT_TRADABLE**, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. Cache `data/cache/campaign303_premium_index_xsec.pkl` = 28,776,516 B, SHA256 `a827bfd7350b85c45b63135376776e90dcd91c6f15161e6564e2044fe97e5067`. Artifacts `reports/campaign303_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T002648Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. FROZEN.

**C304 executed this refresh (20261115T023125Z):** cross-sectional mark/index basis carry across 10 real assets on the 59,031-bar common mark/index grid (2020-01-19 09:00Z → 2026-10-31 23:00Z), basis = mark close − index close, K∈{2,3,5} → **NOT_TRADABLE**, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. Cache `data/cache/campaign304_mark_index_basis_xsec.pkl` = 52,426,602 B, SHA256 `56e27ec2a53b2624ab4cda1a1b4f396ffa4ebbdc9dc7f7995c88cd5153096985`. Artifacts `reports/campaign304_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T023125Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. FROZEN.

**C303 is FROZEN (formal negative); C304 is now FROZEN (formal negative).** C304 returned NOT_TRADABLE (binding cost_sensitivity) — the cross-sectional mark/index basis family is closed as a formal negative. No active heavy-work campaign remains; register the next genuinely-new reachable family if continuing the program.

- **C302 (NEW real family: USDT-M perp `premiumIndexKlines` / continuous fair-value premium, native 1h, 2020-01..2026-10, 486 runs):** executed end-to-end at `20261114T215720Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/486 edge**, 446 with exposure / 40 zero-exposure, binding `mean_beats_benchmark_fail`. Distinct real family from C291/C293/C298/C299/C300 (funding/basis) and C301 (OFI). Cache `data/cache/campaign302_premium_index_basis.pkl` = 7,192,198 B, SHA256 `2f0b45cff41baecf1ab4ddb52de68664ad91f3a4a6f95086f0fc468f7cd86063`. Artifacts `reports/campaign302_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261114T215720Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. FROZEN.
- **C303 (cross-sectional premium-index carry, 10 real assets, 58,959-bar common premium grid, K∈{2,3,5}):** executed end-to-end at `20261115T002648Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/432 edge**, 432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. Cache `data/cache/campaign303_premium_index_xsec.pkl` = 28,776,516 B, SHA256 `a827bfd7350b85c45b63135376776e90dcd91c6f15161e6564e2044fe97e5067`. Artifacts `reports/campaign303_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T002648Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. FROZEN. Next: register a genuinely-new reachable family (e.g. `markPriceKlines`/`indexPriceKlines` basis cross-sectional, or `bookTicker` quote-side).
- **C281B→C301:** all **COMPLETE formal negative results** (0 costed-OOS edge, frozen). Binding constraints: `cost_sensitivity` / `zero_exposure` / `mean_beats_benchmark_fail`.
- **C287 (external execution / testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient), `fapi` 451, bybit 403, no credentials. **Cannot be resolved from this execution environment.** Do not re-probe as economic work.

**Measured real premium-index coverage (this refresh; source of truth for C303):** the 10-asset USDT-M perp `premiumIndexKlines` 1h archives are all reachable at `https://data.binance.vision/data/futures/um/monthly/premiumIndexKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip` (2020-01..2026-10 HTTP 200). Their **common intersection grid (a bar present in ALL 10 premium archives) = 58,959 bars, 2020-01-31 08:00:00Z → 2026-10-31 23:00:00Z**, each asset present 58,959/58,959. Real outages are carried as NaN and NEVER imputed: 2020-01 (16 common bars), 2020-12 (743/744), 2021-07 (624/744), 2022-10 (720/744), 2023-02 (648/672), 2023-04 (696/720), 2026-06 (696/720). So **K∈{2,3,5} is reachable (10 assets ≥ 2K=10 for K=5)** — the old "full coverage from 2020-01" wording was WRONG and is superseded.

**Bottlenecks removed this refresh:** (1) The false "10 assets full coverage from 2020-01" premise → replaced with the measured 58,959-bar common intersection grid (from 2020-01-31 08:00Z). (2) The "reuse C299 perp close + funding for execution" instruction → **C299 cache holds only 3 assets (BTCUSDT, ETHUSDT, BCHUSDT)**, so the C303 ingest MUST fetch real perp 1h klines + native 8h funding for the other 7 assets (endpoints verified HTTP 200 for 2020-01 and 2026-10); reusing C299 for 10 assets would have failed closed. (3) `pytest-asyncio` **present** (1.5.0); if missing elsewhere treat as Step 0 bootstrap (`pip install "pytest-asyncio>=0.23"`), not a research result. (4) GitHub 100 MB push limit resolved (compact ndarray caches < 100 MB; assert on disk). (5) C287 is an **external-only blocker** (testnet 451 / no credentials) — recorded/decoupled, not economic work. (6) **Archive host is flaky under rapid sequential access — the C303 ingest MUST retry:** this refresh re-probed `premiumIndexKlines`/`klines`/`fundingRate` and saw **transient 200↔404 flip-flops** on the same URL within seconds (they stabilized at 200 only after retry/backoff). So the ingest must issue each download with retry-with-backoff (e.g. 6 attempts, linear 1 s×k), treat a lone 404/5xx as retryable, and only fail-closed after all retries are exhausted — a single spurious 404 must NOT abort a session. (7) **Recent monthly archives carry a CSV header row starting `open_time`** (verified: 10 header rows per asset for 2026-09 and 2026-10). The parser MUST skip any row whose first field is non-numeric (`open_time`) rather than `int()`-ing it — otherwise the ingest crashes on the newest months.

**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-15T01:37:39Z, re-affirmed) — EXECUTE C304: CROSS-SECTIONAL MARK/INDEX BASIS STAT-ARB (HEAVY WORK, MANDATORY, UNAVOIDABLE) — **COMPLETE**

All completion gates (a)–(e) met in one session (20261115T023125Z):

- (a) **Ingest:** `scripts/ingest_c304_mark_index_basis_xsec.py` → `data/cache/campaign304_mark_index_basis_xsec.pkl` = 52,426,602 B (< 100 MB), SHA256 `56e27ec2a53b2624ab4cda1a1b4f396ffa4ebbdc9dc7f7995c88cd5153096985`, meta + provenance written, flags `real_data_only:true`/`fabricated_data:false`/`executed_fills:false`. 10 assets, 59,031-bar common mark/index grid (2020-01-19 09:00Z → 2026-10-31 23:00Z), basis = mark close − index close, real outages as NaN never imputed.
- (b) **Preflight:** `scripts/preflight_c304.py` exit 0, `ready:true` on real cache (meta/SHA/size/format/coverage/WF/warmup/provenance all pass).
- (c) **Runner:** `scripts/run_c304_mark_index_basis_xsec_oos.py` costed OOS, **432 runs (≥ 400)**, grid frozen pre-OOS, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps, 5 timestamped artifacts `reports/campaign304_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T023125Z.json` all with real-data flags + SHA256-from-bytes. Verdict **NOT_TRADABLE**, `edge_proven:false`, **0/432 edge**, 432/432 exposure / 0 zero-exposure, binding `cost_sensitivity`.
- (d) **Tests:** `tests/test_preflight_c304.py` + `tests/test_c304_mark_index_basis_xsec_oos.py` added; full suite **1394 passed / 2 skipped / 0 failed**.
- (e) **Sync:** `AGENTS.md` + `research_state/state.yaml` synced with real paths + SHA256-from-bytes (no zeros).

**MANDATORY SCRIPT NAMES:** ingest=`scripts/ingest_c304_mark_index_basis_xsec.py`, preflight=`scripts/preflight_c304.py`, runner=`scripts/run_c304_mark_index_basis_xsec_oos.py`, tests=`tests/test_preflight_c304.py` + `tests/test_c304_mark_index_basis_xsec_oos.py`, cache=`data/cache/campaign304_mark_index_basis_xsec.pkl` (+`.meta.json`, `.provenance.json`), artifacts=`reports/campaign304_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json`.

**ACTIVE CAMPAIGN = C304 — now FROZEN formal negative.** Cross-sectional `markPriceKlines`/`indexPriceKlines` basis stat-arb (mark−index basis, dollar-neutral long cheap/short rich). Distinct real family from funding/basis (C291/C293/C298/C299/C300), OFI (C301), premium-index (C302/C303). CLOSED: `edge_proven:false`, binding `cost_sensitivity`. Register the next genuinely-new reachable family if continuing the program.

**Anti-deferral note:** C304 heavy work executed end-to-end in ONE session. No C304 blocker remains (data 40/40 + execution 14/14 endpoints HTTP 200; templates cloned from C303; pytest-asyncio present). C287 (external execution/testnet 451) stays blocked/decoupled and must not be retried as economic work. Never claim a tradable edge without a passed costed-OOS rule; never fabricate data/fills/credentials; never weaken gates/costs/edge rule; never relabel data; never edit `.github/workflows/main.yml`; never create/read/edit `HANDOFF.md`.

## RESEARCH PROGRAM STATUS (C281B–C304 frozen)

**Status:** C281B→C304 (all COMPLETE formal negatives, frozen) returned **0 costed OOS edge** on the formulations/windows tested. The real-archive funding-carry / spot-perp basis family, the OFI/trade-sign autocorrelation family, the **per-asset premium-index** family, the **cross-sectional premium-index** family, and the **cross-sectional mark/index basis** family are CLOSED.

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
- **C303 cross-sectional premium-index carry** (10 real assets, 58,959-bar common premium grid, K∈{2,3,5}): **COMPLETE formal negative** — executed `20261115T002648Z`, NOT_TRADABLE, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. FROZEN.
- **C304 cross-sectional mark/index basis carry** (10 real assets, 59,031-bar common mark/index grid, K∈{2,3,5}): **COMPLETE formal negative** — executed `20261115T023125Z`, NOT_TRADABLE, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. FROZEN.

**C289 multiple-testing closure:** `economic_space_closed: true` over C286+C288 configs (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps). Does not subsume C299/C300/C301/C302 (different formulation/window).

**C287 (testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient) + no credentials. Cannot be resolved from this execution environment. External execution capability is the only remaining path to a tradable claim, but it is blocked by geography/credentials and decoupled from economic progress.

**Program closure status (this refresh):** C281B→C304 all COMPLETE formal negatives, frozen. `reachable_real_data_cross_sectional_stat_arb_space` is **NOT** closed as a source of tradable edge — every reachable real family tested (funding/basis C291-C300, OFI C301, premium-index C302/C303, mark/index basis C304) returned NOT_TRADABLE with 0 costed-OOS edge. `edge_claim: NONE`, `oos_edge_proven: false`, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false` for all frozen campaigns. Register the next genuinely-new reachable family if continuing the program.

**Environment / verification**

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python scripts/verify_env.py --json
python scripts/bootstrap_dev_env.py
python -m pip install "pytest-asyncio>=0.23"   # only if test_playbooks async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified; suite 1394 passed / 2 skipped / 0 failed, 300s, with `pytest-asyncio` installed). `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

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

- **C303 (COMPLETE formal negative, frozen):** cross-sectional premium-index carry, 10 real assets, 58,959-bar common premium grid, K∈{2,3,5}, ≥400 runs. Executed `20261115T002648Z` → NOT_TRADABLE, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`.
- **C304 (COMPLETE formal negative, frozen):** cross-sectional `markPriceKlines`/`indexPriceKlines` basis stat-arb (mark−index basis, dollar-neutral long cheap/short rich), 10 real assets, 59,031-bar common mark/index grid, K∈{2,3,5}, ≥400 runs. Executed `20261115T023125Z` → NOT_TRADABLE, `edge_proven:false`, **0/432 edge**, 432/432 with exposure / 0 zero-exposure, binding `cost_sensitivity`. CLOSED.
- **C302 (COMPLETE formal negative, frozen):** real premium-index per-asset time-series NOT_TRADABLE, 486 runs, 446 with exposure / 40 zero-exposure, 0/486 edge, binding `mean_beats_benchmark_fail`. New real family (continuous fair-value premium).
- **C301 (COMPLETE formal negative, frozen):** real OFI / trade-sign autocorrelation per-asset time-series NOT_TRADABLE, 648 runs, 545 with exposure / 103 zero-exposure, 0/648 edge, binding `mean_beats_benchmark_fail`. Closes the microstructure family.
- **C300 / C299 / C298 (COMPLETE formal negative, frozen):** perp funding/basis per-asset time-series (1h & 5m) and cross-sectional — all NOT_TRADABLE, 0 edge.
- **C297 (COMPLETE formal negative):** daily multi-year cross-sectional stat-arb NOT_TRADABLE (0/135 costed OOS edge, binding mean_beats_benchmark_fail).
- **C296 (COMPLETE data-blocked closure):** Deribit options term-structure/skew — no deep historical per-strike mark IV feed reachable.
- C295 (frozen, NOT_TRADABLE): three-venue 5m spot, 0/162 edge, binding cost_sensitivity.
- C294 (frozen): Deribit DVOL + Binance VRP, closed NOT_TRADABLE.
- C293 (frozen): OKX funding + Binance funding (C291 cache).
- C292 (frozen): Binance+OKX 5m spot cross-venue basis.
- C291 (frozen): `data.binance.vision` USDT-M 5m klines + fundingRate archives. `fapi.binance.com` remains HTTP 451.
- Binance API/host changes → `data/real_feed_loader.py` host chain. Statsmodels warnings → `utils/coinestion.py` (`result_object=True` where applicable). Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C281B–C303 complete and frozen; **C304 is the active campaign**; C287 (external execution) remains BLOCKED/decoupled and external to this environment.
