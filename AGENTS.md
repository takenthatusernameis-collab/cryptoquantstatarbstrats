# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T12:35:56Z — **C310 COMPLETE formal negative (`20261115T111243Z`, RETRACTED, binding `multiple_testing`, convexity-dominated).** `latest_campaign_done: C310`; `oos_edge_proven: false`; `edge_claim: NONE`. Full suite last verified 2026-11-15T11:14:00Z: 1528 passed / 2 skipped / 0 failed (375.60s). `HANDOFF.md` absent (do not create). Economic progress means **costed out-of-sample PnL on real, provable data**; infra/status-only turns are NOT progress.

## INITIAL TASK MESSAGE (2026-11-15T12:35:56Z) — CAMPAIGN C311 RUNNER EXECUTION (mandatory heavy, NOT verification-only)

**NEXT SESSION ACTION:** Execute the C311 runner end-to-end over the real COIN-M aggTrades 5m grid and emit the 5 artifacts, then re-run the full suite green and sync AGENTS.md + `research_state/state.yaml`.

**State of C311 (verified on disk):**
- Scripts exist: `scripts/ingest_c311_coinm_ofi_5m.py`, `scripts/preflight_c311.py`, `scripts/run_c311_coinm_ofi_xsec_5m_oos.py`
- Tests exist: `tests/test_preflight_c311.py`, `tests/test_c311_coinm_ofi_xsec_5m_oos.py`
- Ingest EXECUTED (`20261115T122009Z`): `data/cache/campaign311_coinm_ofi_5m/` has 11 per-persp float32 npz shards (~91.6 MB total, under the 100 MB GitHub blob limit) + `meta.json` + `provenance.json`, all `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. Window 2022-07..2026-06, BAR_MS=300000, 419,616 common-grid 5m bars, execution price from 5m klines close, native 8h funding from C307 1h `funding_rate_<SYM>` (control leg only). COIN-M `indexPriceKlines` is HTTP 404 — never used.
- **NOT yet done:** `run_c311_coinm_ofi_xsec_5m_oos.py` has not been run — **no `reports/campaign311_*.json` exist yet.** This is the remaining heavy work.

**Runner requirements (pre-registered 504 grid, report all):** 7 OFI signals {ofi_z, ofi_mom, buy_ratio, ofi_per_trade_z, ofi_sign_autocorr, trade_intensity_z, amihud_z} × 4 lookbacks {288,1008,2016,4032} 5m bars × K{2,3,5} × holds{1,6,24} × gates{off,on} = 504 runs. WF train720/test168/step168 (~2500 splits). Inverse PnL `pnl_coin = notional*(1/entry - 1/exit)*signed_weight`; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps + COIN-M realistic overlay (taker5+maker2+mark slip1); native 8h funding excluded (control leg only).

**Validate on ALL of:** (a) Holm AND BH over 504 (report how many survive BOTH); (b) DSR/MDE given the splits; (c) sub-period + per-year stability; (d) per-asset attribution over 11 perps; (e) inverse-convexity vs OFI-carry decomposition (linear-settlement shadow book); (f) execution-cost-realism overlay.

**Emit 5 fresh** `reports/campaign311_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` SHA256-from-bytes, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. **FAIL-CLOSED:** if 0 survive Holm+BH OR any positive is explained by inverse convexity OR fails cost-realism → record a formal negative with binding constraint; do NOT claim tradability. Do not weaken edge rule/costs/gates; do not re-probe reachability; do not re-skin frozen C281B–C310. Full suite must be 0 failed; sync AGENTS.md + `research_state/state.yaml`.

**Definition of done (hard gate):** 5 C311 artifacts on disk with the exact names above + the 3 scripts + 2 tests present, all 504 configs reported (including non-edge), and the full suite re-run green. Anything short is NOT completion.

**Fallback gate:** USDT-M 24-perp aggTrades cross-sectional OFI carry is permitted ONLY after writing `reports/campaign311_5m_infeasibility_probe_<ts>.json` with per-symbol/per-month HTTP status + row counts + concrete blocking evidence (sustained 5xx/404 after 6 linear-backoff retries, or <80% grid-bar coverage), `real_data_only:true`, `fabricated_data:false`. Jumping to the fallback without that artifact is forbidden.

## Bottlenecks removed (do NOT re-litigate)

1. C310 cache is **1h-aggregated only** (`BAR_MS = 3_600_000`; raw trades discarded per month; no raw zips retained) so it CANNOT be re-aggregated to 5m — C311 re-downloaded the COIN-M `aggTrades` window once (~6.2 GB, ~10 min streaming, 3 workers); ingest cache is now on disk. 5m klines (~335 KB/mo) fetched too.
2. Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable.
3. Recent monthly archives may carry CSV header `open_time`/`agg_trade_id` — detect header vs headerless.
4. `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
5. Caches < 100 MB (assert). C311 shards are per-asset npz (~8 MB each), total ~91.6 MB.
6. C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
7. COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — all HTTP 404 on data.binance.vision; never depend on them.
8. COIN-M `fundingRate` HTTP 200 only 2022-07..2026-06 (native 8h). `XLMUSD_PERP` klines start 2021-04. Dated quarterlies only BTCUSD/ETHUSD/XRPUSD `*_261225`.

## C310 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T111243Z` over a NEW real COIN-M aggTrades ingest → RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, 30 deterministic edge, **0 survive Holm AND BH** over 504 (0 Holm, 0 BH, 0 both); 30 survive cost-realism overlay but fail multiple-testing. DSR/MDE: n_splits 203, `n_dsr_ge_0.95: 0`, MDE mean 1.166 bps vs observed -0.179 bps/split. Attribution: OFI-carry share 0.088 vs inverse-convexity share 0.912 → `edge_explained_by_ofi_carry: false`. Cache `data/cache/campaign310_coinm_aggtrades_ofi.pkl` (28.34 MB, SHA256 `393173923815a0e7bc1f06fff439089d50a54e665a7ce1f19f5ba5b5e1d876e8`) is a reusable real-data asset but cannot be re-aggregated to 5m. Artifacts `reports/campaign310_{*}_20261115T111243Z.json` exist (sweep/registry/summary/verdict/binding_constraint SHA256s recorded in prior handoff).

## Repository priority

`cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress = costed out-of-sample PnL on real, provable data. Any turn producing neither a real-data validation, a costed-OOS run, a passing test, or an artifact update is NOT economic progress.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; model PnL labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward, all pre-registered configs reported, multiple-testing correction before any positive claim.
6. **TESTS MUST PASS** — new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and `research_state/state.yaml`; do not create `HANDOFF.md`.
8. **ECONOMIC PRIORITY** — C287 is blocked externally and decoupled; do not retry as economic work.

## Environment / verification

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

## Escalation

- **ACTIVE — C311 runner execution:** run `scripts/run_c311_coinm_ofi_xsec_5m_oos.py` end-to-end over the real 5m grid, emit 5 `reports/campaign311_*` artifacts + tests, full suite green, sync AGENTS.md + state.yaml. If nothing survives Holm+BH → formal negative with binding constraint; do NOT claim tradability.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 20 tests green. Cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only; record, do not retry.
