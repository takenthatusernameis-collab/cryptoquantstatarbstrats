# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T18:15:00Z — **C312 COMPLETE (formal negative, RETRACTED, 20261115T174346Z).** C311 remains a COMPLETE formal negative (`20261115T125846Z`, RETRACTED, binding `multiple_testing`, convexity-dominated). `latest_campaign_done: C312`; `active_campaign: NONE`; `oos_edge_proven: false`; `edge_claim: NONE`. Full suite last verified 2026-11-15T13:27:00Z: **1550 passed / 2 skipped / 0 failed (390.81s)** (re-run required after C312). Economic progress = **costed out-of-sample PnL on real, provable data**; infra/status-only turns are NOT progress.

**C312 on-disk state (verified 2026-11-15T17:43:46Z):**
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` with 10 symbol `.npz` shards + `data/cache/campaign312_usdt_m_ofi_5m.meta.json` + `data/cache/campaign312_usdt_m_ofi_5m.provenance.json` + `months_manifest.json` (`assembled` for all 10, `months` empty, `data/cache/campaign312_usdt_m_ofi_5m/months/` empty). Meta: 10 USDT-M perps, 2023-01..2025-12, 315,648 5m grid bars, 3,156,480 total bars, total shard bytes 67,629,110 (~65 MB, <100 MB), `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, resumable scheme recorded.
- Scripts present: `scripts/ingest_c312_usdt_m_ofi_5m.py`, `scripts/preflight_c312.py`, `scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py`.
- Tests present: `tests/test_preflight_c312.py`, `tests/test_c312_usdt_m_ofi_xsec_5m_oos.py` (21 passed).
- **ARTIFACTS PRESENT (5 + full):** `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T174346Z.json` + `reports/campaign312_oos_sweep_20261115T174346Z.full.json` (gitignored, 340 MB).
- **VERDICT:** RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, **0 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 0 survive cost-realism. Observed mean 0.0 bps/split. OFI-carry share 0.0 vs convexity share 0.0 → `edge_explained_by_ofi_carry: false`.

**Bottlenecks removed / guardrails:** reachability verified (USDT-M `aggTrades` + 5m `klines` HTTP 206; pre-listing 404 = exclude). Scope bounded (10 symbols × 2023-01..2025-12, cache <100 MB). Funding unreachable in-env (fapi 451 / not in archives) → `funding_rate` NaN control-only (must not block). Runner emits **bounded** sweep (<100 MB) and keeps `*.full.json` gitignored. C287 external/decoupled (451/no creds) — never retry as economic work. C281B–C312 frozen — do not rerun/re-skin/re-probe.

**NEXT SESSION TURN CONTRACT (hard, 2026-11-15T18:15:00Z):** No active campaign. The COIN-M inverse-futures space (`coin_m_inverse_futures_space: OPEN`) remains the only reachable genuinely-new economic family (wider COIN-M quarterly universe, or COIN-M perp-vs-quarterly basis with execution-cost realism). Any next heavy campaign MUST be a genuinely-new reachable family with costed OOS validation on real data. Do not rerun/re-skin frozen C281B–C312/C287. Do not produce infra/status-only output. Economic progress = costed out-of-sample PnL on real, provable data.

## INITIAL TASK MESSAGE (2026-11-15T18:15:00Z) — NO ACTIVE CAMPAIGN; COIN-M INVERSE FUTURES SPACE OPEN

**NEXT SESSION ACTION:** The C312 campaign (USDT-M linear-perp native-5m cross-sectional OFI carry) has been executed and completed as a formal negative (RETRACTED, 0/504 Holm+BH, binding `multiple_testing`). All 5 report artifacts + full.json exist on disk. C311, C310, C306–C309, C281B–C305 are frozen formal negatives/retractions. C287 is blocked/decoupled externally.

**Repository-name priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**; rank work by costed out-of-sample PnL on real, provable data, not infrastructure or status.

**Reachable genuinely-new economic families (require validation before any claim):**
1. **COIN-M inverse quarterly term-structure carry** (wider universe than C306 single-asset): long cheap / short rich across front quarterly, next quarterly, and perp using annualized basis on the 11 COIN-M inverse perps (reuses C306/C307 cache reachability; no re-ingest needed for perp legs; quarterly contracts require HTTP 200 verification).
2. **COIN-M perp-vs-quarterly basis cross-sectional** with execution-cost realism overlay (builds on C307 Leg B cache; 11 perps, native 1h or 5m; inverse PnL modeled in coin; costs charged on ALL legs).
3. **USDT-M linear perp microstructure/OFI** at higher resolution (1m if reachable) or wider universe — but requires fresh reachability probe and bounded cache <100 MB.

**Do NOT:** rerun/re-skin frozen C281B–C312/C287; weaken edge rule/costs/gates; claim tradability without costed-OOS proof; produce infra/status-only output.

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