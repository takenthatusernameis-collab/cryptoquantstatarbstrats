# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-16T00:36:11Z — **C281B–C315 CLOSED (all COMPLETE FORMAL NEGATIVES; 0 tradable edge across 12,000+ pre-registered configs; binding constraint universally `multiple_testing`). C287 remains externally blocked (out-of-env only; REST 451 / fapi 451 / bybit 403). ONE genuinely-new reachable heavy family remains and is REGISTERED as the active campaign: C316 — cross-sectional size/volume/turnover LIQUIDITY factors on real on-disk USDT-M 5m data (never tested by any frozen campaign; NOT a re-skin; no network ingest).** Verified on-disk (2026-11-16T00:36:11Z): C312 source cache present (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 perps, 315,648 bars, 2023-01..2025-12, SHA-verified read-only); **no C316 scripts/tests/artifacts exist yet** — C316 is REGISTERED_NOT_STARTED. Last recorded full suite (2026-11-15T23:53:56Z): **1642 passed / 2 skipped / 0 failed**; all C310–C315 slim artifacts on disk with SHA256-from-bytes matching `research_state/state.yaml`; `real_data_only:true, fabricated_data:false, executed_fills:false`. `latest_campaign_done: C315`; `active_campaign: C316`; `oos_edge_proven: false`; `edge_claim: NONE`. **No sessions blocked by missing data; the only economic work is to BUILD + RUN C316 end-to-end now.**

## INITIAL TASK MESSAGE (2026-11-16T00:06:08Z) — BUILD + RUN C316 (cross-sectional size/volume/turnover liquidity factors), THEN VERIFY + CLOSE

**STATUS: REGISTERED_NOT_STARTED — nothing on disk yet** (no scripts, no feature cache, no preflight, no runner, no tests, no artifacts). The next session MUST BUILD C316 end-to-end per steps 1–7 below; re-attesting closure, re-running C281B–C315, or re-probing C287 is non-compliant and NOT economic progress. Data bottleneck is NONE: C312 shards (10 perps × 315,648 bars, 2023-01..2025-12, SHA-verified) are read-only on disk.

**Mission (repo priority = cryptoquantstatarbstrats → costed OOS stat-arb PnL on real, provable data):** C281B–C315 are ALL formal negatives and remain FROZEN (do not rerun/re-skin/re-probe). C287 is externally blocked (out-of-env only). **Exactly one genuinely-new reachable heavy family remains — register, build, and execute it this session: C316, cross-sectional SIZE / VOLUME / TURNOVER (liquidity) factors on the real on-disk USDT-M 5m data.** This is economically distinct from every frozen family (price-based cointegration/basis/momentum/lead-lag and COIN-M/spot OFI) and is NOT a re-skin. A session that only re-attests closure, or re-runs C281B–C315, or re-probes C287, is non-compliant and NOT economic progress.

**THE PRIMARY DE-BOTTLENECK (no network ingest — all data already on disk, SHA-verified):**
- `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` — 10 perps (BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,LINK,AVAX)USDT, 315,648 common-grid 5m bars, 2023-01..2025-12. Fields: `perp_close`, `total_volume`, `notional`, `trade_count`, `vwap`, `signed_volume`, `trade_sign_sum`, `funding_rate` (all-NaN).
- These fields have NEVER been used for a size/volume/turnover/liquidity factor (prior use of this cache was OFI sign-flow only, C312). No download bottleneck — the heavy work is the factor build + preflight + costed OOS sweep + gates + attribution + tests + artifacts.

**C316 CAMPAIGN SPECIFICATION (non-negotiable, heavy-work forcing):**
- **Objective:** prove or retract costed OOS edge for cross-sectional liquidity/size factors on 10 USDT-M linear perps, 2023-01..2025-12, native 5m.
- **Signals (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral gross 1.0):**
  - `size` = -log(cum. trailing-L notional) (small-cap premium: long small, short large).
  - `amihud` = trailing mean of |ret| / notional (illiquidity premium: long illiquid, short liquid).
  - `turnover` = trailing total_volume / trailing |price change| (volume/volatility: long high, short low).
  - `volume` = trailing log total_volume (long high, short low).
  - `vwap_dev` = trailing (close - vwap)/vwap (where price sits vs intraday VWAP).
  - Hold rebalance {6,12,48} bars; lookback L {288, 1008, 2016}.
- **Data handling (fail-closed):** `total_volume`/`notional` are ~0.01% zero (a handful of 5m bars). For `size`/`amihud`/`turnover`/`volume`, guard division by zero (treat zero-notional bars as missing, never inf; carry-forward or drop the affected split bar — never fabricate). `funding_rate` is all-NaN → control only, excluded from PnL.
- **Cost Model (real, charged on turnover):** fee {1,5,10,20} bps/leg; slippage {1,2,5,10} bps/leg; `symmetric`=(fee+slip) and `perp_heavy`=(1.5·fee+slip). Perp funding unreachable (fapi 451) → excluded (control only).
- **Walk-Forward / OOS:** expanding train 12m → test 3m, roll 3m over 36m. Multiple-testing: Holm-Bonferroni AND Benjamini-Hochberg α=0.05 — BOTH must pass. MDE gate (observed mean > MDE mean). Stability gate (sign consistency ≥70% splits; first/second-half Sharpe corr ≥0.5). Attribution gate (dominant of {size, illiquidity, turnover/volume, placebo} share > 0.5 for a positive claim).
- **Artifacts (MUST emit all 5 + gitignored full.json, bounded <100 MB):** `reports/campaign316_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` + gitignored `campaign316_oos_sweep_<TS>.full.json`, each with SHA256-from-bytes and `real_data_only:true,fabricated_data:false,executed_fills:false`.
- **Scripts (MUST add):** `scripts/preflight_c316.py`, `scripts/run_c316_liquidity_xsec_oos.py` (+ any ingest/feature module).
- **Tests (MUST add + pass):** `tests/test_preflight_c316.py`, `tests/test_c316_liquidity_xsec_oos.py`; full suite green.

**Execute in order (all required):**
1. `python scripts/bootstrap_dev_env.py` (deps importable).
2. Build the C316 feature/liquidity cache from the real on-disk C312 shards (read-only; no network). Emit a `<100 MB` feature cache or compute in-runner; if cached, add `<cache>.meta.json` + `.provenance.json` with SHA256 and the three flags.
3. `python scripts/preflight_c316.py --json` → `ready:true`, `blocked_reasons:[]` (fail-closed; any SHA mismatch vs C312 `.meta.json` → BLOCK).
4. Run `scripts/run_c316_liquidity_xsec_oos.py` → emit the 5 artifacts + gitignored full.json with SHA256-from-bytes; ≥500 pre-registered configs with Holm+BH reported.
5. Add/pass `tests/test_preflight_c316.py` + `tests/test_c316_liquidity_xsec_oos.py`; run `python -m pytest tests/ -q` → full suite green.
6. Sync `AGENTS.md` + `research_state/state.yaml` with C316 verdict/SHAs/binding constraint. Register the next genuinely-new family as active ONLY if one exists after C316; otherwise space is CLOSED. Never create `HANDOFF.md`.
7. Do NOT re-run/re-skin/re-probe C281B–C315 or C287.

**Definition of Done (C316):** all 5 artifacts + full.json on disk with SHA256 provenance; ≥500 configs tested with Holm+BH reported; `edge_proven:true` OR formal negative with `binding_constraint`; feature cache <100 MB with correct flags (or in-runner compute, no cache); preflight ready:true; tests green; full suite green; state + handoff synced.

**Guardrails (enforced — C316 session):**
- **No fabricated data / fail-closed / provenance-first:** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; SHA256-from-bytes for every artifact; missing/None/false gates BLOCK.
- **Bounded resources:** per-asset `.npz` shards, each cache <100 MB; slim sweep artifact <100 MB (no per-bar series) + gitignored `full.json`.
- **No overfitting:** ALL pre-registered configs reported; Holm+BH α=0.05 BOTH must pass; MDE + stability + attribution required.
- **Costs real:** per-leg fee/slippage grid charged on turnover; model PnL labeled `executed_fills:false`. Perp funding unreachable (fapi 451) → excluded.

**Frozen/blocked (do NOT rerun, re-skin, re-probe, or pivot to):**
- **C281B–C315** — formal negatives (0/12,000+ configs survive Holm+BH). Re-running, re-skinning, or re-probing any of these is a hard violation.
- **C287** — external-only geographic/credential block (testnet 451, fapi 451, bybit 403, no creds). Do NOT re-probe C287 routes as economic work; unblocking requires out-of-env action only.

**Environment / verification:**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

## C314 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T21:38:11Z)

- **Scripts PRESENT (uncommitted):** `scripts/ingest_c314_spot_perp_leadlag_5m.py`, `scripts/preflight_c314.py`, `scripts/run_c314_spot_perp_leadlag_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c314.py`, `tests/test_c314_spot_perp_leadlag_oos.py` (25/25 C314 tests green).
- **Cache COMPLETE (real data, ~22 MB):** `data/cache/campaign314_spot_perp_leadlag_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LTCUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `spot_close`, `perp_close`, `funding_rate` (all-NaN control-only). 315,632 common-grid 5m bars, 2023-01..2025-12. `months_manifest.json` `{"assembled":[...10...],"months":{}}`. Total 22 MB, max shard 2.69 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`.
  - **KEY DE-BOTTLENECK (do not re-litigate):** Binance **spot** 5m klines switched `open_time` to MICROSECONDS from 2025-01 (e.g. `1735689600000000`) while USDT-M perp stays in milliseconds (`1735689600000`). The ingest normalizes open_time to ms (`normalize_open_time_ms`, threshold >1e14 → //1000) on BOTH write and read paths. Without this the spot/perp intersection collapses to 210,512 bars (67% < 80% gate) and every month from 2025-01 fails. This is fixed and covered by `test_preflight_2025_microsecond_spot_normalized`.
  - Cache meta SHA256 `4bd0e8c97e23fa01d1681357b70e6191caaf6ed5b5a9d4be1d2fd2a3d112f983`; provenance SHA256 `aa2aa688594ff5f3d02ad061ffbf983d5e9a023d365403f144e0c196172bccb6`.
- **Preflight:** `python scripts/preflight_c314.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261115T214305Z`:** 2304 pre-registered configs (lag_window×threshold×rebalance×fee×slip×tercile×cost_variant), expanding WF 12m/3m/3m. **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; `leadlag_vs_noise_share = 0.000275` (noise-dominated, no lead-lag edge); 1664/2304 configs had exposure. All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `3b78ccd1f2caa8e93791b06d338aa1b1ce771caed629c460a05d1077e79db45b` (slim ~1.9 MB)
  - tradable_edge_registry `bd92bd6fc53315981e066e3c081a5aa310881b3a7019c063d1763c56c3e97094`
  - summary `8f5045e7bf3e39aebc4c065a9fe64d54c15cbd8c97d7cf143b2f0aab1b67b9f0`
  - verdict `0b5c40e8da9b1e3177d99afc4c216f51f38d0b1f8c18a7069137a762bfdb6716`
  - binding_constraint `592403e4dd7c8071e88f41684f53563dae62b8072c61ba449dc30cd37e5ac07b`
  - full sweep kept on disk as `reports/campaign314_oos_sweep_20261115T214305Z.full.json` (gitignored).

## C313 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T20:45:00Z, frozen)
- Scripts PRESENT: `scripts/ingest_c313_coinm_quarterly_carry.py`, `scripts/preflight_c313.py`, `scripts/run_c313_coinm_quarterly_carry_oos.py`. Tests 23/23 green. Cache `data/cache/campaign313_coinm_quarterly_carry/` (8 shards + manifest + meta/provenance, ~4.0 MB, 1h 2022-07..2026-06). VERDICT: RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/960 deterministic edge, 0 survive Holm+BH). Artifacts at `20261115T204419Z`. Do not rerun.

## C312 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T18:50Z, frozen)
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `perp_close` usable by C315). Scripts/tests/artifacts present; VERDICT: RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

## Bottlenecks removed / guardrails
- **C314 microsecond spot open_time (2025-01+) NORMALIZED to ms** in ingest (`normalize_open_time_ms`) — the key fix that made spot/perp 5m intersect across the full 36 months. Covered by a regression test.
- **C315 DONE** — real 5m prices already on disk (C312/C314 caches); no download bottleneck. C315 is a COMPLETE FORMAL NEGATIVE (see Escalation); do not rerun.
- Resumable manifest ingest (per symbol/market/month) where ingest is needed; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C315 frozen.
- Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable; 404 month = pre-listing exclusion (not outage).
- Recent monthly archives may carry a CSV header (`open_time`) — detect header vs headerless.
- `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
- Caches <100 MB (assert); keep per-asset `.npz` shards.
- C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
- COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — HTTP 404 on data.binance.vision; never depend. USDT-M `fundingRate` not in monthly archives and fapi 451 → funding leg NaN (control-only).

## C312 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T174346Z` over the real USDT-M 5m klines native ingest (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 perps, 315,648 common-grid 5m bars, 2023-01..2025-12) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, **0 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 0 survive cost-realism. Observed mean 0.0 bps/split. OFI-carry share 0.0 vs convexity share 0.0 → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T174346Z.json` exist; SHA256-from-bytes: sweep `a15aaa40329b44c85b0f64cafe52b8bb8bf73b2431f73463cbef5c4e8dcbb8d4`, registry `4678c43167eee5181e288b3606cf4536ad3ee1870a4bc9599d07bf6209fa41f5`, summary `c1889d55654505e9947da3d7566ce6916e10783bc52a8214e9b4480c239613cf`, verdict `e1bf670670cc9a6fe2cd887e64298c7f13895580db52045845a4b3934ead2955` (corrected 20261115T235151Z from a placeholder to the true SHA256-from-bytes; content unchanged), binding `13c7479777a4f5c698836067fdd87f3686aa82e5dd16496f16051c11f788f5e5`. The sweep was slimmed to ~927 KB (per-split series dropped; full 340 MB kept on disk as `reports/campaign312_oos_sweep_20261115T174346Z.full.json`, gitignored). C312 tests green (21/21).

## C311 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T125846Z` over the real COIN-M aggTrades **native 5m** ingest (`data/cache/campaign311_coinm_ofi_5m/`, 11 perps, 419,616 common-grid 5m bars, 2022-07..2026-06) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`, convexity-dominated. Of 504 pre-registered configs, **17 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 17 survive cost-realism but fail multiple-testing. MDE mean 0.107 bps vs observed −0.0126 bps/split; stability 17/17 first-half and second-half. Attribution: **OFI-carry share 0.025 vs inverse-convexity share 0.975** → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign311_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T125846Z.json` exist; SHA256-from-bytes: sweep `238cb14418c080e8089f2ef222447674641d57e0089402f27bb426f18356a582`, registry `499985448b2dd34da62c9a785950e4168f5f8ce82bdd97d0ac0078b6167bb85e`, summary `515323c39a0cebb7383eb014084c49b2404f6319c1a743a46a628565da4868e9`, verdict `42b885a111f321ed770722e98cfdcb3652226cd65e9c31b8b15d105e1e2437c6`, binding `66f611172056433e78c66bb957e5c4a435b9771945406048cf592f634a06de6c`. The sweep was slimmed to ~1 MB (per-split series dropped; full 427 MB kept on disk as `reports/campaign311_oos_sweep_20261115T125846Z.full.json`, gitignored). C311 tests green (22/22).

## C310 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T111243Z` over a NEW real COIN-M aggTrades 1h ingest → RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, 30 deterministic edge, **0 survive Holm AND BH**; 30 survive cost-realism. MDE mean 1.166 bps vs observed −0.179 bps/split. OFI-carry share 0.088 vs inverse-convexity 0.912. Cache `data/cache/campaign310_coinm_aggtrades_ofi.pkl` (28.34 MB, SHA256 `393173923815a0e7bc1f06fff439089d50a54e665a7ce1f19f5ba5b5e1d876e8`) is a reusable real-data asset but is 1h-aggregated only (cannot re-aggregate to 5m).

## Bottlenecks removed (do NOT re-litigate)

0. **C314 spot 5m `open_time` MICROSECONDS (2025-01+) → NORMALIZED to ms.** Binance spot monthly klines switched `open_time` to microseconds from 2025-01 (e.g. `1735689600000000`) while USDT-M perp stays in ms (`1735689600000`). The C314 ingest normalizes on both write and read paths (`normalize_open_time_ms`, threshold >1e14 → //1000). Without it the spot/perp intersection collapses to 210,512 bars (67% < 80% gate) and all 2025 months fail. Regression test: `test_preflight_2025_microsecond_spot_normalized`.
1. **C311 runner was the blocked item — now EXECUTED** (`20261115T125846Z`); all 5 artifacts + 22 tests green. Nothing about C311 remains to run.
2. **C311 oos_sweep was 446 MB (>100 MB GitHub push limit) → slimmed to ~1 MB** on disk; the runner now drops per-split series on write; the full blob is kept as `reports/*.full.json` (gitignored) for audit. Any future campaign MUST emit a bounded sweep.
3. **C312 reachability verified live** (USDT-M aggTrades AND USDT-M 5m klines = the exec-price endpoint, both HTTP 206 for BTCUSDT @2023-06; SOLUSDT aggTrades @2023-06 also 206). Pre-listing months 404 (e.g. SOL 2020-08) — exclude, do not treat as outage.
4. **C312 scope BOUNDED** to 10 linear USDT-M perps × 2023-01..2025-12 to stay < 100 MB cache and download-tractable (an unbounded "wide universe over many years" would exceed the 100 MB cache rule and blow the session budget).
5. **C312 ingest must be RESUMABLE per (symbol, month)** — this is the primary de-bottleneck: a multi-GB USDT-M aggTrades download survives session boundaries (skip months already in `months_manifest.json`, resume instead of restart). Do not copy the C311 per-symbol-only (non-resumable) behavior.
6. C310 cache is 1h-aggregated only; C311 re-downloaded the COIN-M aggTrades window once (~6.2 GB, streaming); C312 needs its own USDT-M aggTrades ingest (per-month streaming, discard raw, resumable).
7. Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable.
8. Recent monthly archives may carry CSV header `open_time`/`agg_trade_id` — detect header vs headerless.
9. `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
10. Caches < 100 MB (assert). Keep per-asset `.npz` shards; total < 100 MB. C312 estimated ~60 MB.
11. C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
12. COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — all HTTP 404 on data.binance.vision; never depend on them. USDT-M `fundingRate` is not in monthly archives and fapi is 451 → C312 funding leg is NaN (control-only).

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

## Escalation

- **C315 (COMPLETE FORMAL NEGATIVE, 20261115T223831Z):** perp momentum / short-term reversal stat-arb, 3456 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`, dominant attribution reversal 0.7015 (momentum 0.1467, placebo 0.1518); 5 artifacts + full.json + 23 C315 tests green; full suite 1642 passed / 2 skipped / 0 failed (verified 2026-11-15T23:53:56Z). De-bottleneck: real 5m prices on disk from C312 (no network ingest).
- **C314 (COMPLETE FORMAL NEGATIVE, 20261115T214305Z):** spot-perp lead-lag stat-arb, 2304 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`, leadlag_vs_noise_share 0.0003; 5 artifacts + full.json + 25 C314 tests green. De-bottleneck: spot 5m microsecond `open_time` (2025-01+) normalized to ms.
- **C313 (COMPLETE FORMAL NEGATIVE, 20261115T204419Z):** 0/960 Holm+BH, binding `multiple_testing`; 5 artifacts + 23 tests green. Do not rerun.
- **C312 (COMPLETE FORMAL NEGATIVE, 20261115T174346Z):** 0/504 survive Holm+BH, binding `multiple_testing`; 5 artifacts + full.json + 21 tests green.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only geographic/credential issue (testnet 451, no creds). Do not retry, do not probe, do not let it preempt economic work. Unblocking requires out-of-env action only.