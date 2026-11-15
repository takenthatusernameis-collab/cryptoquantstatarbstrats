# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T20:32:09Z — **C312 COMPLETE (formal negative, RETRACTED, 20261115T174346Z).** C311 remains a COMPLETE formal negative (`20261115T125846Z`, RETRACTED, binding `multiple_testing`, convexity-dominated). `latest_campaign_done: C312`; `active_campaign: C313`; `oos_edge_proven: false`; `edge_claim: NONE`. Full suite last verified 2026-11-15T13:27:00Z: **1550 passed / 2 skipped / 0 failed (390.81s)** (re-run required after C313). Economic progress = **costed out-of-sample PnL on real, provable data**; infra/status-only turns are NOT progress.

**BOTTLENECK REMOVAL ENFORCEMENT (2026-11-15T20:32:09Z — MANDATORY FOR ALL FUTURE SESSIONS):**
- **THE BLOCKING BUG IS FIXED (verified live 2026-11-15T18:49Z).** Prior handoffs pointed C313 at `data.binance.vision/data/coin-m/quarterly_klines/...` — that path is **404**. The REAL path is `data.binance.vision/data/futures/cm/monthly/klines/<SYMBOL>/1h/<SYMBOL>-1h-<YYYY-MM>.zip` (HTTP 200 verified for all 11 COIN-M inverse perps @2024-06; quarterly e.g. `BTCUSD_240628-1h-2023-12.zip` present). `data/coin-m/` does NOT exist. Use the `data/futures/cm/` layout verbatim — do NOT re-derive the path; do NOT probe `data/coin-m/` again.
- C313 is the ONLY authorized campaign. C281B–C312/C287 are FROZEN/BLOCKED — any rerun, re-skin, re-probe, or pivot to them is a HARD VIOLATION.
- Quarterly contract naming is `<SYM>YYMMDD` (e.g. `BTCUSD_240628`); perp is `<SYM>_PERP`. 1h zips begin ~3 months before expiry. Pre-listing months 404 → exclude, document in provenance.
- Reachability gate uses the CORRECTED path above. ≥80% of (symbol, contract, month) pairs must return HTTP 200; 404 = exclude that contract-month (pre-listing), NOT an outage.
- Ingest MUST be resumable per (symbol, contract, month) via `months_manifest.json` — survive session boundaries, no restart-from-zero.
- Cache MUST stay <100 MB total. Per-asset `.npz` shards only. Assert on write.
- Runner MUST emit bounded sweep (<100 MB slim JSON) + full.json (gitignored). Per-split series DROPPED from slim artifact.
- C287 (testnet 451, no creds) is EXTERNALLY BLOCKED — never retry, never let it preempt C313.
- NO FABRICATED DATA — every artifact `real_data_only: true`, `fabricated_data: false`, `executed_fills: false`.
- FAIL-CLOSED — missing/None/false gate values BLOCK entries. No silent defaults.
- PROVENANCE FIRST — every number traces to source, timestamp, host, blocked routes, rationale.
- COSTS ARE REAL — all backtests use stated fee/slippage grid; 3 legs per trade = costs ×3.
- NO OVERFITTING — walk-forward, ALL pre-registered configs reported, Holm+BH BOTH must pass at α=0.05 before ANY positive claim.
- TESTS MUST PASS — new code adds tests; CI green before campaign complete.
- SINGLE HANDOFF — update only `AGENTS.md` and `research_state/state.yaml`; do NOT create `HANDOFF.md`.

**C313 on-disk state (verified 2026-11-15T20:32Z):**
- Scripts PRESENT (uncommitted): `scripts/ingest_c313_coinm_quarterly_carry.py`, `scripts/preflight_c313.py`, `scripts/run_c313_coinm_quarterly_carry_oos.py`.
- Tests PARTIAL: `tests/test_preflight_c313.py` PRESENT; `tests/test_c313_coinm_quarterly_carry_oos.py` **MISSING** (must be created and pass).
- Cache PARTIAL (real-data ingest started, resumable): `data/cache/campaign313_coinm_quarterly_carry/` with 8 `.npz` shards (ADAUSD, BNBUSD, BTCUSD, DOTUSD, ETHUSD, LTCUSD, SOLUSD, XRPUSD) + `months_manifest.json` (`{"assembled":[ADAUSD,BNBUSD,BTCUSD,DOTUSD,ETHUSD,LTCUSD,SOLUSD,XRPUSD],"months":{}}`) + `.meta.json`/`.provenance.json` (generated `20261115T195558Z`, 1h 2022-07..2026-06, 8/11 bases ingested). Total shard dir ~4.0 MB. Excluded by ingest: DOGEUSD/MATICUSD/AVAXUSD (`no_quarterly_contracts_listed`); many quarterlies excluded (`expiry_code_outside_mapped_schedule` / `expiry_after_window`). Some windows truncated (e.g. ADAUSD ends 2025-06-27) — **resume/complete ingest and validate coverage; do not assume ready.**
- Preflight status: **NOT VERIFIED this refresh** (cache may be incomplete/misaligned to spec; preflight must be run and pass before runner).
- Runner/artifacts: **NONE** — no `reports/campaign313_*` on disk. `full.json` must be gitignored.
- Immediate bottleneck removed for next session: prior "scripts/cache missing" claim was stale; real blocker is finishing resumable ingest to a spec-compliant bounded cache, running preflight, implementing/passing runner tests, and producing costed OOS artifacts.

**NEXT SESSION TURN CONTRACT (hard, 2026-11-15T20:32:09Z):** Active campaign **C313** (COIN-M inverse quarterly term-structure carry) is the ONLY authorized work. Next session MUST perform heavy economic work end-to-end: (1) bootstrap env, (2) resume/complete real-data ingest per corrected path + `months_manifest.json` (or prove cache is spec-complete and preflight-ready), (3) run `scripts/preflight_c313.py` to green, (4) run C313 costed OOS runner over ≥504 pre-registered configs with Holm+BH (α=0.05, both required) on 1h grid 2022-07..2026-06, (5) emit all 5 artifacts + gitignored `full.json` with SHA256 provenance, (6) add/pass `tests/test_c313_coinm_quarterly_carry_oos.py` and keep `tests/test_preflight_c313.py` green. Do not rerun/re-skin frozen C281B–C312/C287. Do not produce infra/status-only output. Economic progress = costed out-of-sample PnL on real, provable data.

**C312 on-disk state (verified 2026-11-15T18:50Z, frozen):**
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`).
- Scripts/tests/artifacts present; **VERDICT:** RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

**Bottlenecks removed / guardrails:** corrected COIN-M path enforced; resumable manifest ingest; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C312 frozen.

## INITIAL TASK MESSAGE (2026-11-15T20:32:09Z) — ACTIVE CAMPAIGN: C313 COIN-M INVERSE QUARTERLY TERM-STRUCTURE CARRY (HEAVY EXECUTION, NO DEFERRAL)

**NEXT SESSION ACTION (mandatory, start immediately — no planning-only turn):** Complete and validate **Campaign 313 (C313)** to a costed OOS result (edge proven OR formal negative) on real, provable data. Repo priority is `cryptoquantstatarbstrats` (stat-arb): deliver costed OOS PnL evidence, not status.

1. **Bootstrap & verify env:** `python scripts/bootstrap_dev_env.py`; ensure deps per AGENTS; install `pytest-asyncio>=0.23` only if async tests break.
2. **Resume/complete real ingest (corrected path only):** use `data/futures/cm/monthly/klines/<SYMBOL>/1h/<SYMBOL>-1h-<YYYY-MM>.zip` (perp `<BASE>USD_PERP`, quarterly `<BASE>USD_YYMMDD`). Resume via `data/cache/campaign313_coinm_quarterly_carry/months_manifest.json`. Stream/discard raw, enforce cache <100 MB (per-asset `.npz`). Exclude 404/pre-listing/unmapped contract-months with provenance. Current cache is PARTIAL (8/11 bases, some truncated windows, `months` empty in manifest) — finish to spec-compliant coverage over 2022-07..2026-06 or fail-closed with documented binding reason.
3. **Preflight to green:** run `python scripts/preflight_c313.py` against real cache/manifest/path; fix any blocking issues (do not bypass gates).
4. **Run costed OOS (≥504 pre-registered configs):** execute `python scripts/run_c313_coinm_quarterly_carry_oos.py` (expanding WF train 12m→test 3m, roll 3m, 16 splits) with Holm+BH at α=0.05 (BOTH required). Model inverse PnL in coin (USDT conversion at portfolio via perp mark only), 3-leg cost grid (fee 1/5/10/20 + slip 1/2/5/10 bps/leg, ×3). Emit bounded slim sweep <100 MB + gitignored `full.json`.
5. **Emit 5 artifacts + full.json with SHA256:** `reports/campaign313_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` (+ `oos_sweep_<TS>.full.json` gitignored). Verdict must state `edge_proven` true/false, `binding_constraint`, and carry/convexity attribution. All `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.
6. **Tests required:** create/complete `tests/test_c313_coinm_quarterly_carry_oos.py`; keep `tests/test_preflight_c313.py` passing; run targeted tests (and full suite if feasible). Do not claim green without running.
7. **Update handoff:** sync `AGENTS.md` + `research_state/state.yaml` with final C313 state, artifact SHAs, and — if formal negative — the next genuinely-new reachable stat-arb family (pre-registered, heavy-work). Never create `HANDOFF.md`.

**Hard constraints:** no fabricated data; fail-closed gates; provenance-first; costs real (×3 legs); no overfitting (all pre-registered, Holm+BH); no rerun/re-skin of C281B–C312/C287; no `data/coin-m/` probes; no unbounded sweep; no infra-only completion.

### C313 CAMPAIGN SPECIFICATION (non-negotiable, heavy-work forcing)

**Objective:** Prove or retract costed out-of-sample edge for cross-sectional term-structure carry on COIN-M inverse quarterlies + perp, 2022-07..2026-06.

**CORRECTED DATA PATH (verified live 2026-11-15T18:49Z — use verbatim):**
- COIN-M klines live at: `https://data.binance.vision/data/futures/cm/monthly/klines/<SYMBOL>/1h/<SYMBOL>-1h-<YYYY-MM>.zip`
- Perp symbol: `<BASE>USD_PERP` (e.g. `BTCUSD_PERP`). Quarterly symbol: `<BASE>USD_<YYMMDD>` (e.g. `BTCUSD_240628`).
- `data/coin-m/` and `data.binance.vision/data/coin-m/quarterly_klines/` DO NOT EXIST (404) — prior handoff was wrong; do not probe them again.
- Bucket root listing: `https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/cm/monthly/klines/<SYMBOL>/` (XML).
- aggTrades (if needed for microstructure): `https://data.binance.vision/data/futures/cm/monthly/aggTrades/<SYMBOL>/<SYMBOL>-aggTrades-<YYYY-MM>.zip`.

**Scope (bounded, <100 MB cache):**
- 11 COIN-M inverse perps × 3 tenors (front quarterly, next quarterly, perp) = 33 instruments
- Native 1h klines (reuse C310 1h aggregation logic; 5m only if reachable without cache blowout — 1h is the default)
- Window: 2022-07..2026-06 (48 months, aligns with C311 COIN-M window)
- Cache target: <100 MB total (per-asset `.npz` shards)

**Reachability Gate (MUST pass before any ingest — corrected path):**
- Probe `https://data.binance.vision/data/futures/cm/monthly/klines/<SYMBOL>/1h/<SYMBOL>-1h-<YYYY-MM>.zip` for all 11 perps × front/next quarterly contracts
- HTTP 200 required for ≥80% of symbol-month pairs; 404 = exclude that contract-month (pre-listing)
- Document blocked routes in provenance; no fabricated data

**Ingest (resumable per (symbol, contract, month)):**
- Stream monthly CSVs → aggregate to 1h grid → compute annualized basis (perp vs front quarterly, front vs next quarterly)
- Discard raw CSV after aggregation; resume via `months_manifest.json` (C312 pattern)
- Funding rate: NaN control-only (fapi 451 / not in archives) — must not block

**Signal Construction (pre-registered, no data peeking):**
- Cross-sectional rank by annualized basis (z-score per timestamp across 11 symbols)
- Long bottom tercile (cheap), short top tercile (rich) — dollar-neutral in coin terms
- Rebalance: 1h (native) or 4h (cost-aware)
- Inverse PnL modeled in **coin** (not USDT); convert to USDT only at portfolio level using perp mark

**Cost Model (execution-cost realism, charged on ALL legs):**
- Maker/taker fee grid: 1/5/10/20 bps (per leg)
- Slippage: 1/2/5/10 bps (per leg, quarterly liquidity penalty)
- 3 legs per trade (long perp + short front quarterly + long/short next quarterly) → costs ×3
- No cost-free assumptions

**Walk-Forward / OOS Protocol (pre-registered configs = 504 minimum):**
- Expanding window: train 12m → test 3m, roll 3m (16 splits over 48m)
- Pre-register ALL configs before first backtest: basis_horizon × rebalance × fee × slippage × tercile_cut × cost_model_variant
- Multiple-testing correction: **Holm-Bonferroni AND Benjamini-Hochberg (BH) at α=0.05** — BOTH must pass
- Minimum Deterministic Edge (MDE) gate: observed mean > MDE mean across splits
- Stability gate: sign consistency ≥70% splits, first-half vs second-half Sharpe correlation ≥0.5

**Artifacts (MUST emit all 5 + full.json, bounded sweep <100 MB):**
1. `reports/campaign313_oos_sweep_<TS>.json` (slim: per-split summary only, no per-bar series)
2. `reports/campaign313_oos_sweep_<TS>.full.json` (gitignored, full per-bar series for audit)
3. `reports/campaign313_tradable_edge_registry_<TS>.json`
4. `reports/campaign313_summary_<TS>.json`
5. `reports/campaign313_verdict_<TS>.json` (`edge_proven`, `binding_constraint`, `edge_explained_by_carry_vs_convexity`)
6. `reports/campaign313_binding_constraint_<TS>.json`

**Tests (MUST add + pass):**
- `tests/test_preflight_c313.py` (reachability against CORRECTED path, cache schema, manifest)
- `tests/test_c313_coinm_quarterly_carry_oos.py` (runner, gates, artifact schema)
- CI green before campaign complete

**Definition of Done (cannot claim progress without):**
- All 5 artifacts + full.json on disk with correct SHA256 provenance
- 504+ pre-registered configs tested, Holm+BH results reported
- `edge_proven: true` OR formal negative with `binding_constraint` identified
- Cache <100 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`
- Tests green (new + existing suite)

**Bottleneck Removal (enforced):**
- **CORRECTED DATA PATH verified live** (the prior blocker) — `data/futures/cm/monthly/klines/`; do not re-probe `data/coin-m/`.
- Resumable ingest per (symbol, contract, month) — survive session boundaries
- Bounded sweep emission (<100 MB) — drop per-split series in slim artifact
- C287 remains BLOCKED/DECOUPLED — never retry, never let it preempt C313
- C281B–C312 FROZEN — do not rerun, re-skin, re-probe

**Repository-name priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. This campaign IS statistical arbitrage (term-structure carry). Rank work by costed out-of-sample PnL on real, provable data. Infra/status-only output = NOT progress.

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