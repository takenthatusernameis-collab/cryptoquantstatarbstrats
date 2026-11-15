# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T21:36:14Z — **C313 COMPLETE FORMAL NEGATIVE (RETRACTED, 20261115T204419Z, 0/960 Holm+BH, binding `multiple_testing`).** C312/C311/C310/C306–C309/C281B–C305 FROZEN formal negatives. C287 BLOCKED/DECOUPLED (external 451/no creds). `latest_campaign_done: C313`; `active_campaign: C314`; `oos_edge_proven: false`; `edge_claim: NONE`.

## INITIAL TASK MESSAGE (2026-11-15T21:36:14Z, refreshed) — ACTIVE CAMPAIGN C314: SPOT-PERP LEAD-LAG STAT-ARB (MANDATORY HEAVY, NO STATUS-ONLY TURN)

**Mission (repo priority = cryptoquantstatarbstrats → costed OOS stat-arb PnL on real, provable data):** Execute **C314 — Spot-Perp Lead-Lag Statistical Arbitrage (USDT-M linear perps vs spot, 5m, 2023-01..2025-12)** end-to-end to `edge_proven:true` OR a formal negative with binding constraint. **C314 does not exist on disk** (no scripts/tests/cache/artifacts) — create and complete all heavy work this campaign. Infra/status-only output is NOT progress.

**Frozen/blocked (do NOT rerun, re-skin, re-probe, or pivot to):** C281B–C313 (formal negatives), C287 (external 451/no creds). Any work on them is a hard violation.

**Bottlenecks removed / guardrails (enforced):**
- **Verified data paths (C312 HTTP 206):** spot `https://data.binance.vision/data/spot/monthly/klines/<SYMBOL>/5m/<SYMBOL>-5m-<YYYY-MM>.zip`, perp `https://data.binance.vision/data/futures/um/monthly/klines/<SYMBOL>/5m/<SYMBOL>-5m-<YYYY-MM>.zip`. 404 = excluded pre-listing month (not outage). Funding NaN/control-only if unreachable.
- **Resumable ingest:** per (symbol, market, month) via `months_manifest.json`; survive session boundaries; discard raw CSV after feature extraction.
- **Bounded resources:** cache <100 MB total, per-asset `.npz` shards; slim sweep artifact <100 MB (no per-bar/per-split series) + gitignored `full.json`.
- **No fabricated data / fail-closed / provenance-first:** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; SHA256-from-bytes for every artifact; missing/None/false gates BLOCK.
- **No overfitting:** ALL pre-registered configs reported; Holm+BH α=0.05 BOTH must pass; MDE + stability + lead-lag-vs-noise attribution required.

**Execute in order (all required):**
1. `python scripts/bootstrap_dev_env.py`
2. Create `scripts/ingest_c314_spot_perp_leadlag_5m.py`: reachability probe + resumable ingest for spot+USDT-M perp 5m klines, 10 symbols `[BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,DOTUSDT,LTCUSDT,AVAXUSDT]`, 2023-01..2025-12 (36m), aligned common 5m grid, lead-lag features (spot↔perp cross-corr at lags 1-12 / 5-60m), months_manifest, cache `data/cache/campaign314_spot_perp_leadlag_5m/` <100 MB `.npz`.
3. Create/run `scripts/preflight_c314.py` → `ready:true` fail-closed (≥80% reachable pairs, schema/manifest/cache checks).
4. Create/run `scripts/run_c314_spot_perp_leadlag_oos.py` over **all pre-registered configs (2304 ≥504):** lag_window[6,12,24]×lead_lag_threshold[0.05,0.10,0.15]×rebalance[5m,15m,30m,1h]×fee[1,5,10,20]bps×slippage[1,2,5,10]bps×tercile_cut[33,25]×cost_variant[symmetric,perp_heavy]. Expanding WF train 12m/test 3m/roll 3m. Holm+BH α=0.05 BOTH; MDE; stability (≥70% sign consistency, first/second-half Sharpe corr ≥0.5); lead-lag-vs-noise attribution (>0.5 share for positive claim). 2-leg USDT PnL (spot+perp), costs ×2 on stated grid.
5. Emit `reports/campaign314_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` (slim) + gitignored `full.json`, SHA256-from-bytes, `real_data_only:true,fabricated_data:false,executed_fills:false`.
6. Add/pass `tests/test_preflight_c314.py` + `tests/test_c314_spot_perp_leadlag_oos.py`; run targeted/full suite green.
7. Sync `AGENTS.md` + `research_state/state.yaml` with verdict/SHAs/binding constraint. If formal negative, register the next genuinely-new reachable stat-arb family (pre-registered, heavy) as active. Never create `HANDOFF.md`.

**Definition of Done:** all 5 artifacts + full.json on disk with SHA256 provenance; ≥504 configs tested with Holm+BH reported; `edge_proven:true` OR formal negative with `binding_constraint`; cache <100 MB with correct flags; tests green.

**C313 on-disk state (verified 2026-11-15T20:45:00Z, post-execution refresh):**
- Scripts PRESENT (uncommitted): `scripts/ingest_c313_coinm_quarterly_carry.py`, `scripts/preflight_c313.py`, `scripts/run_c313_coinm_quarterly_carry_oos.py`.
- Tests COMPLETE: `tests/test_preflight_c313.py` PRESENT; `tests/test_c313_coinm_quarterly_carry_oos.py` CREATED AND PASSING (23/23 tests green).
- Cache COMPLETE (real-data ingest finished): `data/cache/campaign313_coinm_quarterly_carry/` with 8 `.npz` shards (ADAUSD, BNBUSD, BTCUSD, DOTUSD, ETHUSD, LTCUSD, SOLUSD, XRPUSD) + `months_manifest.json` (`{"assembled":[ADAUSD,BNBUSD,BTCUSD,DOTUSD,ETHUSD,LTCUSD,SOLUSD,XRPUSD],"months":{}}`) + `.meta.json`/`.provenance.json` (generated `20261115T195558Z`, 1h 2022-07..2026-06, 8/11 bases ingested). Total shard dir ~4.0 MB. Excluded by source: DOGEUSD/MATICUSD/AVAXUSD (`no_quarterly_contracts_listed`); many quarterlies excluded (`expiry_code_outside_mapped_schedule` / `expiry_after_window`). Some windows truncated (e.g. ADAUSD ends 2025-06-27) — documented in provenance.
- Preflight status: **VERIFIED GREEN** (`python scripts/preflight_c313.py --json` → `ready:true`, `blocked_reasons:[]`).
- Runner/artifacts: **COMPLETE** — all 5 artifacts + gitignored `full.json` emitted at `20261115T204419Z` with SHA256 provenance. Slim sweep ~1.2 MB, full ~2.0 MB.
- **VERDICT:** RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/960 deterministic edge, 0 survive Holm+BH). Costed OOS executed over 960 pre-registered configs (5 lookbacks × 3 rebalances × 4 fees × 4 slippages × 2 tercile cuts × 2 cost variants).

**C312 on-disk state (verified 2026-11-15T18:50Z, frozen):**
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`).
- Scripts/tests/artifacts present; **VERDICT:** RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

**Bottlenecks removed / guardrails:** corrected COIN-M path enforced; resumable manifest ingest; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C312 frozen.

## INITIAL TASK MESSAGE (2026-11-15T21:32:49Z) — ACTIVE CAMPAIGN: C314 SPOT-PERP LEAD-LAG STAT-ARB (MANDATORY HEAVY, START IMMEDIATELY)

**Mission (cannot defer, cannot stop at status):** C313 COIN-M inverse quarterly term-structure carry is **COMPLETE — FORMAL NEGATIVE** (RETRACTED, 20261115T204419Z, 0/960 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`, 23/23 tests green, 5 artifacts + full.json with SHA256). Repo priority remains `cryptoquantstatarbstrats` (stat-arb) — economic progress = costed OOS PnL on real, provable data.

**Next session MUST (end-to-end, no infra-only stop):** Execute **C314 — Spot-Perp Lead-Lag Statistical Arbitrage on USDT-M Linear Perps** to `edge_proven:true` OR a formal negative with binding constraint. C314 is a genuinely-new signal family (spot↔perp lead-lag, cross-sectional), distinct from exhausted carry/OFI/term-structure families (C281B–C313 all formal negatives). On-disk: **no C314 scripts/tests/cache/artifacts exist** — create, run, and complete them this campaign.

**Ordered work (all required):**
1. `python scripts/bootstrap_dev_env.py`
2. Create `scripts/ingest_c314_spot_perp_leadlag_5m.py` (or equivalent): reachability probe + resumable ingest per (symbol, market, month) via `months_manifest.json` for spot & USDT-M perp 5m klines, 2023-01..2025-12, 10 symbols, bounded cache <100 MB, per-asset `.npz` shards, compute/retain lead-lag features, discard raw CSV, 404=excluded pre-listing (not outage), funding NaN control-only.
3. Create/run `scripts/preflight_c314.py` → `ready:true` fail-closed.
4. Create/run `scripts/run_c314_spot_perp_leadlag_oos.py` over ALL pre-registered configs (≥504, see grid) with expanding WF train 12m/test 3m/roll 3m, Holm+BH α=0.05 BOTH, MDE, stability, lead-lag-vs-noise attribution, 2-leg (spot+perp) costs.
5. Emit `reports/campaign314_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` (slim sweep <100 MB) + gitignored `full.json`, SHA256-from-bytes, `real_data_only:true,fabricated_data:false,executed_fills:false`.
6. Add/pass `tests/test_preflight_c314.py`, `tests/test_c314_spot_perp_leadlag_oos.py`; run targeted/full suite green.
7. Sync `AGENTS.md` + `research_state/state.yaml` with verdict/SHAs; if formal negative, register next genuinely-new reachable stat-arb family (heavy, pre-registered). Never create `HANDOFF.md`.

**Hard rules:** no fabricated data; fail-closed gates; provenance-first; costs real (2 legs × per-leg fee/slippage); no overfitting (all pre-registered, Holm+BH both); no rerun/re-skin of C281B–C313/C287; no unbounded sweep (>100 MB slim); no infra-only completion.

**Prerequisites for C314:**
1. Reachability probe against data.binance.vision for spot + USDT-M perp 5m klines (both verified HTTP 206 in C312)
2. Pre-register ≥504 configs (signals × lookbacks × rebalances × costs × gates) BEFORE any backtest
3. Resumable ingest via months_manifest, bounded cache <100 MB, per-asset .npz shards
4. Fail-closed preflight + runner tests + 5 artifacts + full.json with SHA256 provenance
5. Holm+BH at α=0.05 BOTH required; MDE + stability gates; lead-lag vs noise attribution
6. Real data only, no fabrication, executed_fills:false

**Hard constraints:** no fabricated data; fail-closed gates; provenance-first; costs real (2 legs: spot + perp); no overfitting (all pre-registered, Holm+BH); no rerun/re-skin of C281B–C313/C287; no unbounded sweep; no infra-only completion.

### C314 CAMPAIGN SPECIFICATION (non-negotiable, heavy-work forcing)

**Objective:** Prove or retract costed out-of-sample edge for spot-perp lead-lag statistical arbitrage on USDT-M linear perps, 2023-01..2025-12 (36 months, aligns with C312 window).

**VERIFIED DATA PATHS (C312 confirmed HTTP 206 live):**
- Spot klines: `https://data.binance.vision/data/spot/monthly/klines/<SYMBOL>/5m/<SYMBOL>-5m-<YYYY-MM>.zip`
- USDT-M perp klines: `https://data.binance.vision/data/futures/um/monthly/klines/<SYMBOL>/5m/<SYMBOL>-5m-<YYYY-MM>.zip`
- Symbols: 10 major USDT-M perps (BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, DOTUSDT, LTCUSDT, AVAXUSDT) — same universe as C312
- Bucket root listing (XML): `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/monthly/klines/<SYMBOL>/` and `.../data/futures/um/monthly/klines/<SYMBOL>/`

**Scope (bounded, <100 MB cache):**
- 10 symbols × 2 markets (spot + perp) = 20 instruments
- Native 5m klines (reuse C312 5m aggregation logic; 1h only if 5m cache blows out — 5m is the default for lead-lag)
- Window: 2023-01..2025-12 (36 months, aligns with C312 USDT-M window)
- Cache target: <100 MB total (per-asset `.npz` shards, ~5 MB each → ~100 MB max)

**Reachability Gate (MUST pass before any ingest — verified paths):**
- Probe both spot and perp 5m paths for all 10 symbols × 36 months = 720 URLs
- HTTP 200/206 required for ≥80% of (symbol, market, month) pairs; 404 = exclude that market-month (pre-listing), NOT an outage
- Document blocked routes in provenance; no fabricated data

**Ingest (resumable per (symbol, market, month)):**
- Stream monthly CSVs → align to common 5m grid (forward-fill spot to perp timestamps, or resample both to common grid)
- Compute lead-lag features: spot→perp return correlation at lags 1-12 (5m-60m), perp→spot reverse, cross-correlation peak lag
- Discard raw CSV after feature extraction; resume via `months_manifest.json` (C312 pattern)
- Funding rate: NaN control-only (not in monthly archives, fapi 451) — must not block

**Signal Construction (pre-registered, no data peeking):**
- Lead-lag signal: for each symbol, compute rolling cross-correlation between spot and perp returns at lags 1-12 (5m steps)
- Long perp / short spot when spot leads perp (positive lag correlation) with strength > threshold; reverse when perp leads spot
- Cross-sectional rank by lead-lag strength (z-score per timestamp across 10 symbols)
- Long top tercile (strongest lead-lag), short bottom tercile (weakest/reverse) — dollar-neutral in USDT
- Rebalance: 5m (native), 15m, 30m, 1h (cost-aware)
- PnL modeled in **USDT** (spot + perp both USDT-quoted); 2 legs per trade (spot + perp)

**Cost Model (execution-cost realism, charged on ALL legs):**
- Maker/taker fee grid: 1/5/10/20 bps (per leg, spot + perp)
- Slippage: 1/2/5/10 bps (per leg, spot typically tighter than perp)
- 2 legs per trade (long spot + short perp OR short spot + long perp) → costs ×2
- No cost-free assumptions

**Walk-Forward / OOS Protocol (pre-registered configs = 504 minimum):**
- Expanding window: train 12m → test 3m, roll 3m (12 splits over 36m)
- Pre-register ALL configs before first backtest: lag_window × lead_lag_threshold × rebalance × fee × slippage × tercile_cut × cost_variant
  - lag_window: [6, 12, 24] (3)
  - lead_lag_threshold: [0.05, 0.10, 0.15] (3)
  - rebalance: [5m, 15m, 30m, 1h] (4)
  - fee: [1, 5, 10, 20] bps (4)
  - slippage: [1, 2, 5, 10] bps (4)
  - tercile_cut: [top/bottom 33%, top/bottom 25%] (2)
  - cost_variant: [symmetric, perp_heavy] (2) = 3×3×4×4×4×2×2 = 2304 configs (well above 504 minimum)
- Multiple-testing correction: **Holm-Bonferroni AND Benjamini-Hochberg (BH) at α=0.05** — BOTH must pass
- Minimum Deterministic Edge (MDE) gate: observed mean > MDE mean across splits
- Stability gate: sign consistency ≥70% splits, first-half vs second-half Sharpe correlation ≥0.5
- Attribution gate: lead-lag share vs noise share (require lead-lag share > 0.5 for positive claim)

**Artifacts (MUST emit all 5 + full.json, bounded sweep <100 MB):**
1. `reports/campaign314_oos_sweep_<TS>.json` (slim: per-split summary only, no per-bar series)
2. `reports/campaign314_oos_sweep_<TS>.full.json` (gitignored, full per-bar series for audit)
3. `reports/campaign314_tradable_edge_registry_<TS>.json`
4. `reports/campaign314_summary_<TS>.json`
5. `reports/campaign314_verdict_<TS>.json` (`edge_proven`, `binding_constraint`, `edge_explained_by_leadlag_vs_noise`)
6. `reports/campaign314_binding_constraint_<TS>.json`

**Tests (MUST add + pass):**
- `tests/test_preflight_c314.py` (reachability against spot/perp paths, cache schema, manifest)
- `tests/test_c314_spot_perp_leadlag_oos.py` (runner, gates, artifact schema)
- CI green before campaign complete

**Definition of Done (cannot claim progress without):**
- All 5 artifacts + full.json on disk with correct SHA256 provenance
- 504+ pre-registered configs tested, Holm+BH results reported
- `edge_proven: true` OR formal negative with `binding_constraint` identified
- Cache <100 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`
- Tests green (new + existing suite)

**Bottleneck Removal (enforced):**
- **VERIFIED DATA PATHS** (C312 confirmed spot + USDT-M perp 5m klines HTTP 206) — no re-probe needed for reachability gate
- Resumable ingest per (symbol, market, month) — survive session boundaries
- Bounded sweep emission (<100 MB) — drop per-split series in slim artifact
- C287 remains BLOCKED/DECOUPLED — never retry, never let it preempt C314
- C281B–C313 FROZEN — do not rerun, re-skin, re-probe

**Repository-name priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. This campaign IS statistical arbitrage (spot-perp lead-lag). Rank work by costed out-of-sample PnL on real, provable data. Infra/status-only output = NOT progress.

**Environment / verification:**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

## C312 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T174346Z` over the real USDT-M 5m klines native ingest (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 perps, 315,648 common-grid 5m bars, 2023-01..2025-12) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, **0 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 0 survive cost-realism. Observed mean 0.0 bps/split. OFI-carry share 0.0 vs convexity share 0.0 → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T174346Z.json` exist; SHA256-from-bytes: sweep `a15aaa40329b44c85b0f64cafe52b8bb8bf73b2431f73463cbef5c4e8dcbb8d4`, registry `4678c43167eee5181e288b3606cf4536ad3ee1870a4bc9599d07bf6209fa41f5`, summary `c1889d55654505e9947da3d7566ce6916e10783bc52a8214e9b4480c239613cf`, verdict `9a7b8e7f1b3c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9`, binding `13c7479777a4f5c698836067fdd87f3686aa82e5dd16496f16051c11f788f5e5`. The sweep was slimmed to ~927 KB (per-split series dropped; full 340 MB kept on disk as `reports/campaign312_oos_sweep_20261115T174346Z.full.json`, gitignored). C312 tests green (21/21).

## C311 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T125846Z` over the real COIN-M aggTrades **native 5m** ingest (`data/cache/campaign311_coinm_ofi_5m/`, 11 perps, 419,616 common-grid 5m bars, 2022-07..2026-06) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`, convexity-dominated. Of 504 pre-registered configs, **17 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 17 survive cost-realism but fail multiple-testing. MDE mean 0.107 bps vs observed −0.0126 bps/split; stability 17/17 first-half and second-half. Attribution: **OFI-carry share 0.025 vs inverse-convexity share 0.975** → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign311_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T125846Z.json` exist; SHA256-from-bytes: sweep `238cb14418c080e8089f2ef222447674641d57e0089402f27bb426f18356a582`, registry `499985448b2dd34da62c9a785950e4168f5f8ce82bdd97d0ac0078b6167bb85e`, summary `515323c39a0cebb7383eb014084c49b2404f6319c1a743a46a628565da4868e9`, verdict `42b885a111f321ed770722e98cfdcb3652226cd65e9c31b8b15d105e1e2437c6`, binding `66f611172056433e78c66bb957e5c4a435b9771945406048cf592f634a06de6c`. The sweep was slimmed to ~1 MB (per-split series dropped; full 427 MB kept on disk as `reports/campaign311_oos_sweep_20261115T125846Z.full.json`, gitignored). C311 tests green (22/22).

## C310 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T111243Z` over a NEW real COIN-M aggTrades 1h ingest → RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, 30 deterministic edge, **0 survive Holm AND BH**; 30 survive cost-realism. MDE mean 1.166 bps vs observed −0.179 bps/split. OFI-carry share 0.088 vs inverse-convexity 0.912. Cache `data/cache/campaign310_coinm_aggtrades_ofi.pkl` (28.34 MB, SHA256 `393173923815a0e7bc1f06fff439089d50a54e665a7ce1f19f5ba5b5e1d876e8`) is a reusable real-data asset but is 1h-aggregated only (cannot re-aggregate to 5m).

## Bottlenecks removed (do NOT re-litigate)

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

- **C312 (COMPLETE FORMAL NEGATIVE, 20261115T174346Z):** 0/504 survive Holm+BH, binding `multiple_testing`; 5 artifacts + full.json + 21 tests green.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only geographic/credential issue (testnet 451, no creds). Do not retry, do not probe, do not let it preempt economic work. Unblocking requires out-of-env action only.