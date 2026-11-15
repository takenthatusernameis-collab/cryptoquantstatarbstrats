# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T18:04:38Z — **C312 ingest + scripts/tests COMPLETE (cache ready); runner/artifacts NOT done.** C311 remains a COMPLETE formal negative (`20261115T125846Z`, RETRACTED, binding `multiple_testing`, convexity-dominated). `latest_campaign_done: C311`; `active_campaign: C312`; `oos_edge_proven: false`; `edge_claim: NONE`. Full suite last verified 2026-11-15T13:27:00Z: **1550 passed / 2 skipped / 0 failed (390.81s)** (re-run required after C312). Economic progress = **costed out-of-sample PnL on real, provable data**; infra/status-only turns are NOT progress.

**C312 on-disk state (re-verified 2026-11-15T18:04:38Z):**
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` with 10 symbol `.npz` shards + `data/cache/campaign312_usdt_m_ofi_5m.meta.json` + `data/cache/campaign312_usdt_m_ofi_5m.provenance.json` + `months_manifest.json` (`assembled` for all 10, `months` empty, `data/cache/campaign312_usdt_m_ofi_5m/months/` empty). Meta: 10 USDT-M perps, 2023-01..2025-12, 315,648 5m grid bars, 3,156,480 total bars, total shard bytes 67,629,110 (~65 MB, <100 MB), `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, resumable scheme recorded.
- Scripts present: `scripts/ingest_c312_usdt_m_ofi_5m.py`, `scripts/preflight_c312.py`, `scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py`.
- Tests present: `tests/test_preflight_c312.py`, `tests/test_c312_usdt_m_ofi_xsec_5m_oos.py`.
- **MISSING (blocking done):** `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` — **none exist**. Do NOT re-ingest/re-download unless preflight proves cache invalid; ingest is resumable but unnecessary now.

**Bottlenecks removed / guardrails:** reachability verified (USDT-M `aggTrades` + 5m `klines` HTTP 206; pre-listing 404 = exclude). Scope bounded (10 symbols × 2023-01..2025-12, cache <100 MB). Funding unreachable in-env (fapi 451 / not in archives) → `funding_rate` NaN control-only (must not block). Runner must emit **bounded** sweep (<100 MB) and keep `*.full.json` gitignored. C287 external/decoupled (451/no creds) — never retry as economic work. C281B–C311 frozen — do not rerun/re-skin/re-probe.

**NEXT SESSION TURN CONTRACT (hard, 2026-11-15T18:04:38Z):** 1) `python scripts/bootstrap_dev_env.py` 2) run preflight: `python scripts/preflight_c312.py --json` (fail-closed on shard SHA/flags/grid/legs; fix only if invalid — do not blanket re-ingest) 3) run `python scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py` on real cache to produce the 504-config linear-settlement OFI xsec sweep 4) emit 5 `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` (SHA256-from-bytes, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, bounded sweep <100 MB; `*.full.json` gitignored) 5) `python -m pytest tests/ -q` full suite green 6) sync `AGENTS.md` + `research_state/state.yaml` with paths/SHA256/verdict. **If any C312 report artifact is absent at turn start/end, the turn is FAILED — continue running (no status-only/verification-only wrap-up, no deferral).**

## INITIAL TASK MESSAGE (2026-11-15T18:04:38Z) — CAMPAIGN C312: USDT-M LINEAR-PERP NATIVE-5m CROSS-SECTIONAL OFI CARRY (MANDATORY HEAVY — RUN TO COMPLETION)

**NEXT SESSION ACTION (do this, not a status report):** C312 data + code are already on disk. **Run preflight → runner → emit 5 `reports/campaign312_*_<ts>.json` → run full pytest green → sync `AGENTS.md`+`research_state/state.yaml`.** This is the only remaining reachable, genuinely-new heavy economic family after C281B–C311; no exploratory detour, no re-ingest unless preflight fails, no re-probe of frozen C281B–C311/C287, no status-only turn. If interrupted, resume from existing cache/state and continue in the same turn.

**Repository-name priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**; rank work by costed out-of-sample PnL on real, provable data, not infrastructure or status. C312 is the next authorized heavy campaign; no exploratory detour is authorized before its artifacts exist.

**Repository-name priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**; rank by costed out-of-sample PnL on real, provable data, not infrastructure/status.

**Why genuinely new (not a re-skin):** C301 was 3 symbols/2 months. C310 (1h) and C311 (5m) tested COIN-M inverse-settlement OFI carry and were formal negatives dominated by inverse-settlement convexity (OFI-carry share 0.088 vs 0.912; 0.025 vs 0.975). **C312 removes the convexity confound** via **linear-settlement USDT-M perps** (`notional*(exit/entry - 1)*signed_weight`) — any edge is attributable to OFI carry. Hypothesis: costed OOS OFI carry edge on linear perps once convexity is removed?

**BOUNDED SCOPE (fixed, satisfied by current cache):** 10 USDT-M linear perps `BTCUSDT ETHUSDT BNBUSDT SOLUSDT XRPUSDT ADAUSDT DOGEUSDT AVAXUSDT LINKUSDT DOTUSDT`, `2023-01..2025-12` (36 months; per-year 2023/2024/2025 + half stability). Cache 67.6 MB (<100 MB). `funding_rate` all-NaN control-only (unreachable in-env; must not block). Execution price from 5m klines close; OFI legs from taker buy/sell split.

**Pipeline to complete (build already done):**
1. `python scripts/bootstrap_dev_env.py`
2. `python scripts/preflight_c312.py --json` — fail-closed: shard SHAs/manifest, interval 5m, flags, grid non-empty in window, finite positive close + finite OFI legs, gaps recorded never imputed, funding NaN control-only. **Do not re-ingest if ready.**
3. `python scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py` — 504 configs: 7 signals {ofi_z,ofi_mom,buy_ratio,ofi_per_trade_z,ofi_sign_autocorr,trade_intensity_z,amihud_z} × 4 lookbacks {288,1008,2016,4032} × K{2,3,5} × holds{1,6,24} × gates{off,on}; WF train720/test168/step168; **linear** PnL `sum(pos*(close/close_prev - 1))*notional`; costs [[0,0],[5,5],[10,10],[20,20],[40,40]] bps + realism overlay (taker 5 + slippage 1 = 6 bps one-way on turnover; maker 2 bps reported separately).
4. Emit 5 fresh `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` (SHA256-from-bytes, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`). **Bounded sweep <100 MB** (drop per-split series; keep full as `*.full.json` gitignored).
5. `python -m pytest tests/ -q` (full suite green).

**Validate on ALL of:** (a) Holm AND BH over 504 (report counts surviving BOTH); (b) DSR/MDE; (c) sub-period + per-year stability (2023/2024/2025); (d) per-asset attribution (10 symbols); (e) OFI-carry vs EW B&H (linear, no convexity term); (f) execution-cost-realism overlay.

**FAIL-CLOSED verdict rule:** if 0 survive Holm+BH OR any positive fails cost-realism → formal negative with binding constraint; **never claim tradability**. Do not weaken edge rule/costs/gates. Do not rerun/re-skin C281B–C311/C287.

**Definition of done (hard gate):** 5 C312 report artifacts on disk + all 504 configs reported (including non-edge) + full suite green + AGENTS/state synced with paths+SHA256. Anything short is NOT completion. If interrupted, resume from existing cache and continue (no restart, no deferral, no status-only wrap-up).

**Anti-avoidance gate (hard):** if any C312 artifact is missing at the end of a turn, the turn is a **failed turn** — do not write a completion summary, do not write a "blocked"/"verification-only"/"status" wrap-up, do not defer to a later session. Continue building/running until the 5 artifacts + 3 scripts + 2 tests exist and the suite is green. Ranked by repo name (`cryptoquantstatarbstrats` = stat-arb), only costed out-of-sample PnL on real provable data counts as progress; re-probing C310/C311/C287, re-skinning frozen C281B–C311, or producing infra/status-only output is explicitly NOT progress and does not satisfy this campaign. If the download is interrupted, **resume** from `months_manifest.json` in the same turn — do not restart and do not stop.

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

- **ACTIVE (2026-11-15T16:45:20Z) — C312 build+run (mandatory heavy):** execute full pipeline (bootstrap → build 3 scripts + 2 tests → ingest real USDT-M aggTrades 5m + 5m klines exec price, resumable per symbol-month → preflight → 504-config linear-settlement OFI xsec sweep → 5 `reports/campaign312_*` artifacts → full pytest green → sync AGENTS/state). If nothing survives Holm+BH or fails cost-realism → formal negative with binding constraint; do NOT claim tradability. Status-only turns while C312 artifacts absent are failed turns.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only geographic/credential issue (testnet 451, no creds). Do not retry, do not probe, do not let it preempt economic work. Unblocking requires out-of-env action only.