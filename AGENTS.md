# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T13:29:19Z — **C311 COMPLETE formal negative (`20261115T125846Z`, RETRACTED, binding `multiple_testing`, convexity-dominated). C312 is the mandatory next heavy campaign and is NOT started (0 scripts/tests/artifacts on disk).** `latest_campaign_done: C311`; `oos_edge_proven: false`; `edge_claim: NONE`. Full suite last verified 2026-11-15T13:27:00Z: **1550 passed / 2 skipped / 0 failed (390.81s)**. `HANDOFF.md` absent (do not create). Economic progress means **costed out-of-sample PnL on real, provable data**; infra/status-only turns are NOT progress. No blockers remain for C312: reachability verified, templates (C311) available, env bootstrap defined, bounded-sweep rule enforced.

## INITIAL TASK MESSAGE (2026-11-15T13:20:37Z) — CAMPAIGN C312: USDT-M LINEAR-PERP WIDE-UNIVERSE NATIVE-5m CROSS-SECTIONAL OFI CARRY (mandatory heavy, NOT verification-only)

**NEXT SESSION ACTION:** Build and run C312 end-to-end over real USDT-M `aggTrades`, emit 5 `reports/campaign312_*` artifacts + 2 tests, re-run the full suite green, and sync AGENTS.md + `research_state/state.yaml`. This is the pre-registered fallback family (USDT-M aggTrades OFI cross-section) and is the only remaining reachable, genuinely-new heavy economic family after C281B–C311.

**Why this is genuinely new (not a re-skin):**
- C301 used only **3 symbols (BTC/ETH/BCH) over a 2-month window (2023-01..2023-02)** — a tiny slice, not the wide universe.
- C310 (1h) and C311 (5m) tested **COIN-M inverse-settlement** OFI carry; both were formal negatives dominated by **inverse-settlement convexity** (C310 OFI-carry share 0.088 vs convexity 0.912; C311 OFI-carry share 0.025 vs convexity 0.975).
- **C312 removes the convexity confound entirely** by using **linear-settlement USDT-M perps**: PnL is exactly `notional * (exit/entry - 1) * signed_weight`, so any surviving edge is attributable to OFI carry, not to `1/entry - 1/exit` convexity. Hypothesis: does a costed OOS OFI carry edge exist on linear perps once convexity is removed?

**Reachability VERIFIED this refresh (bottleneck removed):** USDT-M `aggTrades` `https://data.binance.vision/data/futures/um/monthly/aggTrades/{sym}/{sym}-aggTrades-YYYY-MM.zip` returns HTTP 206 (range) for 15 symbols at 2026-10 (BTC, ETH, SOL, BNB, XRP, DOGE, ADA, AVAX, LINK, LTC, BCH, DOT, TRX, ETC, XLM) and for BTC at 2020-01, 2021-06, 2023-06. `SOLUSDT 2020-08` is 404 (pre-listing) — expected, exclude pre-listing months.

**Build (Step 0 first):** `python scripts/bootstrap_dev_env.py`, then create:
- `scripts/ingest_c312_usdt_m_ofi_5m.py` — BAR_MS=300000; stream per-month aggTrades (retry 6× linear backoff, lone 404/5xx retryable, skip CSV header row), per-bar legs {signed_volume, total_volume, trade_count, trade_sign_sum, notional, vwap}; execution price from USDT-M 5m klines close; native 8h funding control-only (never the carry source); per-asset float32 `.npz` shards, total cache **< 100 MB** (assert), + `meta.json` + `provenance.json`, all `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. Reuse the C311 ingest script as the template.
- `scripts/preflight_c312.py` — fail-closed: shard SHAs match manifest, interval 5m, flags intact, common grid non-empty, every symbol finite positive close + finite OFI legs, gaps recorded never imputed.
- `scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py` — pre-registered **504 configs**: 7 signals {ofi_z, ofi_mom, buy_ratio, ofi_per_trade_z, ofi_sign_autocorr, trade_intensity_z, amihud_z} × 4 lookbacks {288,1008,2016,4032} 5m × K{2,3,5} × holds{1,6,24} × gates{off,on}. WF train720/test168/step168. **Linear** PnL `sum(pos*(close/close_prev - 1))*notional`; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps + USDT-M realism overlay (taker 5 + slippage 1 = 6 bps one-way on turnover; maker 2 bps reported separately). **Emit a bounded oos_sweep (<100 MB)**: drop per-split series (`oos_net_mean_per_split`, `bh_oos_net_mean_per_split`), keep full on disk as `*.full.json` (gitignored). Copy the C311 runner as the template.
- `tests/test_preflight_c312.py`, `tests/test_c312_usdt_m_ofi_xsec_5m_oos.py` (pure helpers + fail-closed cache + artifact flags + SHA256-from-bytes + edge-rule-never-relaxed + verdict/registry/summary consistency, mirroring the C311 tests).

**Validate on ALL of:** (a) Holm AND BH over 504 (report how many survive BOTH); (b) DSR/MDE given the splits; (c) sub-period + per-year stability; (d) per-asset attribution over the universe; (e) OFI-carry vs equal-weight B&H decomposition (linear, no convexity term); (f) execution-cost-realism overlay.

**Emit 5 fresh** `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` SHA256-from-bytes, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. **FAIL-CLOSED:** if 0 survive Holm+BH OR any positive fails cost-realism → record a formal negative with binding constraint; do NOT claim tradability. Do not weaken edge rule/costs/gates; do not re-probe C311; do not re-skin frozen C281B–C311.

**Definition of done (hard gate):** 5 C312 artifacts on disk with the exact names above + 3 scripts + 2 tests present, all 504 configs reported (including non-edge), and the full suite re-run green. Anything short is NOT completion.

## C311 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T125846Z` over the real COIN-M aggTrades **native 5m** ingest (`data/cache/campaign311_coinm_ofi_5m/`, 11 perps, 419,616 common-grid 5m bars, 2022-07..2026-06) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`, convexity-dominated. Of 504 pre-registered configs, **17 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 17 survive cost-realism but fail multiple-testing. MDE mean 0.107 bps vs observed −0.0126 bps/split; stability 17/17 first-half and second-half. Attribution: **OFI-carry share 0.025 vs inverse-convexity share 0.975** → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign311_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T125846Z.json` exist; SHA256-from-bytes: sweep `238cb14418c080e8089f2ef222447674641d57e0089402f27bb426f18356a582`, registry `499985448b2dd34da62c9a785950e4168f5f8ce82bdd97d0ac0078b6167bb85e`, summary `515323c39a0cebb7383eb014084c49b2404f6319c1a743a46a628565da4868e9`, verdict `42b885a111f321ed770722e98cfdcb3652226cd65e9c31b8b15d105e1e2437c6`, binding `66f611172056433e78c66bb957e5c4a435b9771945406048cf592f634a06de6c`. The sweep was slimmed to ~1 MB (per-split series dropped; full 427 MB kept on disk as `reports/campaign311_oos_sweep_20261115T125846Z.full.json`, gitignored). C311 tests green (22/22).

## C310 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T111243Z` over a NEW real COIN-M aggTrades 1h ingest → RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, 30 deterministic edge, **0 survive Holm AND BH**; 30 survive cost-realism. MDE mean 1.166 bps vs observed −0.179 bps/split. OFI-carry share 0.088 vs inverse-convexity 0.912. Cache `data/cache/campaign310_coinm_aggtrades_ofi.pkl` (28.34 MB, SHA256 `393173923815a0e7bc1f06fff439089d50a54e665a7ce1f19f5ba5b5e1d876e8`) is a reusable real-data asset but is 1h-aggregated only (cannot re-aggregate to 5m).

## Bottlenecks removed (do NOT re-litigate)

1. **C311 runner was the blocked item — now EXECUTED** (`20261115T125846Z`); all 5 artifacts + 22 tests green. Nothing about C311 remains to run.
2. **C311 oos_sweep was 446 MB (>100 MB GitHub push limit) → slimmed to ~1 MB** on disk; the runner now drops per-split series on write; the full blob is kept as `reports/*.full.json` (gitignored) for audit. Any future campaign MUST emit a bounded sweep.
3. **C312 reachability verified** (USDT-M aggTrades HTTP 206 for 15 symbols @2026-10 and BTC @2020-01/2021-06/2023-06). Pre-listing months 404 (e.g. SOL 2020-08) — exclude, do not treat as outage.
4. C310 cache is 1h-aggregated only; C311 re-downloaded the COIN-M aggTrades window once (~6.2 GB, streaming); C312 needs its own USDT-M aggTrades ingest (per-month streaming, discard raw).
5. Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable.
6. Recent monthly archives may carry CSV header `open_time`/`agg_trade_id` — detect header vs headerless.
7. `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
8. Caches < 100 MB (assert). Keep per-asset `.npz` shards; total < 100 MB.
9. C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
10. COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — all HTTP 404 on data.binance.vision; never depend on them.

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

- **ACTIVE — C312 build+run:** ingest real USDT-M aggTrades at 5m, preflight, run the 504-config linear-settlement cross-sectional OFI carry sweep, emit 5 `reports/campaign312_*` artifacts + 2 tests, full suite green, sync AGENTS.md + state.yaml. If nothing survives Holm+BH → formal negative with binding constraint; do NOT claim tradability.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only; record, do not retry.