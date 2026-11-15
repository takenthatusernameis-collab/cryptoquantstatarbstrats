# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T10:10:05Z — **C308 EXECUTED end-to-end → C307 edge RETRACTED (program still 0 tradable costed-OOS edge). `latest_campaign_done: C308`, `oos_edge_proven: false`, `edge_claim: NONE`. C309 is the only active next step (mandatory, heavy, unavoidable): COIN-M INVERSE CROSS-SECTIONAL PREMIUM-INDEX & MARK-PERP BASIS CARRY. Build `scripts/preflight_c309.py` + `scripts/run_c309_coinm_premium_mark_basis_carry_oos.py` (+ tests), execute end-to-end over the existing C307 cache (no re-ingest), emit 5 SHA256 artifacts, pass tests + full suite, sync state.** Verified: deps green (Py3.12.3; pytest 9.2.0, pytest-asyncio 1.5.0, numpy/pandas/scipy/statsmodels/sklearn importable), full suite **2026-11-15T09:54:09Z: 1488 passed / 2 skipped / 0 failed (363.76s)**. `HANDOFF.md` absent. Any session that does not produce real-data validation, a passing test, or an artifact update is **not** economic progress.

## INITIAL TASK MESSAGE (2026-11-15T10:10:05Z) — NEXT FOCUS CAMPAIGN: COIN-M INVERSE CROSS-SECTIONAL PREMIUM-INDEX & MARK-PERP BASIS CARRY — CAMPAIGN C309 (HEAVY, MANDATORY, UNAVOIDABLE, NON-NEGOTIABLE)

**NEXT SESSION ACTION (non-optional, do not defer, do not plan, do not status-report — EXECUTE):** C308 retracted the C307 edge. The reachable COIN-M inverse space still has ONE genuinely untested economic family that is buildable from the SAME C307 cache with NO re-ingest and NO new data: the cross-sectional **premium-index carry** and **mark-perp basis** family on the 11 COIN-M inverse perps. The C307 cache already stores, per perp, `premium_close_<SYM>`, `mark_close_<SYM>`, `perp_close_<SYM>` (all finite, non-degenerate, verified this session), plus `funding_rate_<SYM>`/`funding_present_<SYM>`; `index_close_*` is NOT present (COIN-M index klines are HTTP 404 — do not depend on it). Build C309 and run it end-to-end:
```
python scripts/bootstrap_dev_env.py
# C307 cache already on disk: data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl (SHA256 7045013e…13d3)
python scripts/preflight_c309.py            # must print ready:true and exit 0
python scripts/run_c309_coinm_premium_mark_basis_carry_oos.py
python -m pytest tests/test_preflight_c309.py tests/test_c309_coinm_premium_mark_basis_carry_oos.py -q
python -m pytest tests/ -q                  # must be 0 failed
```
**COMPLETION GATE (all required, no exceptions):**
1. Preflight `scripts/preflight_c309.py` prints `ready:true` and exits 0 — fail-closed if the C307 cache is missing, the cache SHA256-from-bytes mismatches, the premium/mark/perp fields are absent or non-finite for the 11 perps, or the common grid is outside 2022-07..2026-06.
2. Runner `scripts/run_c309_coinm_premium_mark_basis_carry_oos.py` executes end-to-end over the C307 cache (NO re-ingest) over the **pre-registered 504-config grid** and validates on ALL of: (a) multiple-testing correction across the 504 pre-registered configs — Holm AND Benjamini-Hochberg, reporting how many survive BOTH; (b) DSR / minimum detectable effect given 203 splits; (c) sub-period stability (first vs second half of 2022-07..2026-06 and per-year); (d) per-asset contribution decomposition over the 11 perps; (e) inverse-convexity attribution — decompose any edge into premium/mark carry vs inverse-settlement convexity (`1/entry − 1/exit`) using a linear-settlement shadow book; (f) execution-cost-realism overlay (COIN-M inverse taker 5 bps + maker 2 bps + mark slippage 1 bps, turnover/rebalance).
3. 5 fresh timestamped SHA256 artifacts emitted to `reports/campaign309_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json`, each `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, SHA256-from-bytes.
4. C309 tests green (`tests/test_preflight_c309.py`, `tests/test_c309_coinm_premium_mark_basis_carry_oos.py`).
5. Full test suite 0 failed (`python -m pytest tests/ -q`).
6. AGENTS.md + `research_state/state.yaml` synced (`latest_campaign_done: C309` if executed, cache/artifact paths/SHA256s, verdict/binding, next family).

**PRE-REGISTERED C309 GRID (do not expand/cherry-pick):**
- **Signals (7, all NEW — NOT funding carry, NOT dated-quarterly term structure):** `premium_level`, `premium_z`, `premium_mom`, `premium_sign`, `mark_basis_level`, `mark_basis_z`, `mark_basis_sign` where `mark_basis = mark_close/perp_close − 1` and `premium` = `premium_close`.
- **Lookbacks 1h (4):** L∈{24, 168, 720, 1440}.
- **Cross-sectional K (3):** K∈{2, 3, 5}.
- **Holding periods 1h (3):** {1, 6, 24}.
- **Dispersion gates (2):** off / on.
- **Total runs:** 7×4×3×3×2 = **504** (`N_TRIALS = 504`; report all 504; never drop a config).
- **WF:** train 720, test 168, step 168 → 203 splits over the 34,968-bar common grid (2022-07-01 → 2026-06-30).
- **Inverse PnL:** `pnl_coin = notional_usd*(1/entry − 1/exit)*signed_weight`; costs on ALL legs at `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps plus the realistic overlay; native 8h funding NOT used as the C309 signal (it is a control leg only, never the carry source).

**FAIL-CLOSED VALIDATION RULE (non-negotiable):** if 0 of the 504 configs survive Holm AND BH, OR any positive is explained by inverse-settlement convexity rather than premium/mark carry, OR the positive fails the execution-cost-realism overlay, record a **formal negative** with the binding constraint and do NOT claim tradability. Do NOT weaken the edge rule, cost grid, or gates to force a positive.

**Why C309 is necessary (not optional):** C307/C308 exhausted the COIN-M inverse **funding-carry** and **dated-quarterly term-structure** families (both formal negatives / RETRACTED). The premium-index and mark-perp basis cross-section is the last reachable, genuinely untested COIN-M inverse economic family on real data already on disk. It is the scientifically correct next heavy campaign and it cannot be avoided by claiming "data missing" — the cache provably contains the required fields.

**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics. Any turn that produces neither a real-data validation, a costed-OOS run, a passing test, or an artifact update is NOT economic progress and must not be reported as such.

**Verified state (refreshed 2026-11-15T09:54:09Z):** `HANDOFF.md` absent (correct). Deps import-verified; `python scripts/bootstrap_dev_env.py` returned `ready:true`. **Full suite 2026-11-15T09:54:09Z: 1488 passed, 2 skipped, 0 failed (363.76s).** C308 fully executed this session (preflight ready + runner + 5 artifacts + 21 tests green); the C308 completion gate is met and C308 is FROZEN as a formal negative. The 10 historical C305 program-closure reds remain FIXED; no test is skipped, masked, or weakened. Templates present on disk to copy: C306 `scripts/ingest_c306_coinm_term_structure.py`, `scripts/preflight_c306.py`, `scripts/run_c306_coinm_term_structure_oos.py`, `tests/test_preflight_c306.py`, `tests/test_c306_coinm_term_structure_oos.py`; C307 `scripts/ingest_c307_coinm_multiasset_term_structure_carry.py`, `scripts/preflight_c307.py`, `scripts/run_c307_coinm_multiasset_term_structure_carry_oos.py`, `tests/test_preflight_c307.py`, `tests/test_c307_coinm_multiasset_term_structure_carry_oos.py`; **C308 `scripts/preflight_c308.py`, `scripts/run_c308_c307_edge_validation_oos.py`, `tests/test_preflight_c308.py`, `tests/test_c308_c307_edge_validation_oos.py`**; C303/C304 cross-sectional scripts/tests. `research_state/state.yaml` parses cleanly; `latest_campaign_done: C308`.

**Corrected reachability matrix (verified; source `https://data.binance.vision/data/futures/cm/monthly/`; do NOT re-probe as unknown):**
- **Perp klines / premiumIndexKlines / markPriceKlines:** HTTP 200 for 2020-12..2026-10 for 10/11 perps; `XLMUSD_PERP` klines start **2021-04** (2021-01..03 = 404). All 11 perps HTTP 200 at both 2022-07 and 2026-06.
- **`fundingRate`:** HTTP 200 **only 2022-07..2026-06**; 2022-06 and 2026-07..2026-10 are 404. Schema: `calc_time` (ms), `funding_interval_hours` (8), `last_funding_rate`; 90 rows/month. Funding is native 8h, not 1h.
- **Dated quarterlies:** `BTCUSD_250627`, `BTCUSD_250926`, `BTCUSD_261225`, `ETHUSD_250627`, `ETHUSD_250926`, `ETHUSD_261225`, `XRPUSD_261225`. Other underlyings' `*_261225` are 404 (only BTC/ETH/XRP have dated quarterlies).
- **ETHUSD_PERP:** klines/premium/mark are HTTP 200 across 2020-12..2026-10 (the old "404 every month" note was WRONG); C306 excluded ETHUSD only because ETHUSD_261225 had <888 overlapping bars.
- **COIN-M `indexPriceKlines`:** HTTP 404 — do NOT depend on it; use `premium_close` (premium index) and `mark_close` from the C307 cache for C309.

**Bottlenecks removed (do NOT re-litigate):** (1) C305 probe scope-limited to `futures/um`+`spot` — resolved by C306/C307 using `futures/cm`. (2) Archive host flaky — every download MUST retry with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable. (3) Recent monthly archives may carry CSV header `open_time` — skip rows whose first field is non-numeric. (4) `pytest-asyncio` present (1.5.0); if missing treat as Step 0 bootstrap. (5) Caches < 100 MB (assert). (6) C287 external-only (451/no creds) — decoupled, never retry as economic work. (7) COIN-M `fundingRate` only 2022-07..2026-06; do not attempt other months. (8) ETHUSD_PERP klines HTTP 200. (9) `XLMUSD_PERP` klines start 2021-04. (10) Dated quarterlies only for BTCUSD/ETHUSD/XRPUSD. (11) C307 cache already holds finite non-degenerate `premium_close`/`mark_close`/`perp_close` for all 11 perps — C309 needs NO new ingest.

**Session bootstrap (Step 0, before any campaign code):** `python scripts/bootstrap_dev_env.py`; install `pytest-asyncio>=0.23` only if async tests report "async def not natively supported". Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run.

## C308 (COMPLETE — C307 edge RETRACTED, FROZEN formal negative — do not rerun)

Executed `20261115T093148Z` over the C307 cache (no re-ingest) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`. Of **53 deterministic edge configs** (C307's 44 Leg B + 9 others), **0 survive Holm AND BH** over 612 configs (0 Holm, 18 BH, 0 both); 44 survive the execution-cost-realism overlay but fail multiple-testing. DSR/MDE: n_splits 203, `n_dsr_ge_0.95: 0`, `n_dsr_ge_0.90: 0`, MDE mean 0.339 bps vs observed 0.401 bps/split (MDE not cleared). Stability: first-half 44 / second-half 44 stable, per-year 2022:44 2023:14 2024:44 2025:44 2026:35. Attribution: aggregate funding share 0.324 vs inverse-convexity share 0.607 → `edge_explained_by_funding: false` (convexity dominates). All 612 runs (180 Leg A + 432 Leg B) had exposure (0 zero-exposure); the edge rule was never relaxed (0/612 mismatches). Cache SHA256 `7045013e18de42b64cf583236c90da57c30e6779ac3b58c4b86bfa87eb1373d3`. Artifacts `reports/campaign308_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T093148Z.json` SHA256s: sweep `e1e0c14866d262adbe157289ca3d1011f82133e592de17fd56ceceba42badffe`, registry `c81e1c747e879f6918a6dbbd7fb5af3da2c1fc5101dc0724e040d5cbccfdff2b`, summary `7c310454c68fb60e3d4342ee3b5243bfedc44449e0d3947de8ad6b59ec41fd40`, verdict `1a7f7a927db5de4935239b964b72d169f7000f32c3283d6df60533752a78a65c`, binding_constraint `5293ed8dfaaa2ceccccc8b792862735c0694404746129d5a809b92076535d18c`. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`. C308 tests: `tests/test_preflight_c308.py` + `tests/test_c308_c307_edge_validation_oos.py` = **21 passed**.

## C307 (RETRACTED by C308 — formal negative, FROZEN — do not rerun)

Executed `20261115T085840Z` (reproduced from `20261115T083047Z`) → the then-recorded `EDGE_PROVEN` (44/612, all Leg B COIN-M inverse cross-sectional funding carry: `fund_level`/`fund_z`/`fund_sign`, gate=off, L∈{720,1440}, K∈{2,3,5}, holds{1,6,24}) was **RETRACTED by C308**: 0 of the edge configs survive Holm+BH multiple-testing correction over 612 configs, and the effect is dominated by inverse-settlement convexity (0.607) rather than funding carry (0.324). The `EDGE_PROVEN`/`oos_edge_proven:true` claim is CORRECTED to `RETRACTED`/`oos_edge_proven:false` in this handoff and in `research_state/state.yaml` (`c307_status`, `c308_status`). Cache `data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl` (16,989,995 B, SHA256 `7045013e18de42b64cf583236c90da57c30e6779ac3b58c4b86bfa87eb1373d3`; meta `9b83353440cfd1be2fb95c51fdce0539d516aaca9aee97bc532aecfaea9a9b4d`; provenance `b8506f3da25b008f53b57cdde978d42c34763d44c7c99c2c99d41a0b47c6309e`) remains valid and is REUSED by C308 (validation) and C309 (next family). C307 artifacts `reports/campaign307_{oos_sweep,tradable_edge_registry,summary,verdict}_20261115T085840Z.json` are frozen historical records of the superseded candidate.

## C306 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T050843Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/448 edge**, 448/448 with exposure, binding `cost_sensitivity`. Cache `data/cache/campaign306_coinm_term_structure.pkl` SHA256 `056066849b6b4c304cf46d48f3f3c4c1aaf87c47480fdfb01eacc17ede42bffe` (4,914 bars, 1 asset BTCUSD, 4 contracts, 2 real outage bars). Artifacts `reports/campaign306_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T050843Z.json`. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.

## RESEARCH PROGRAM STATUS (C281B–C306 frozen formal negatives; C307 RETRACTED; C308 RETRACTED; C309 active)

**Status:** C281B→C306 returned **0 costed OOS edge** on the formulations/windows tested (all COMPLETE formal negatives, frozen). USDT-M/spot/options families CLOSED (C305). C306 (COIN-M inverse dated-quarterly term-structure, BTC-only grid) FROZEN as formal negative. **C307 (COIN-M inverse multi-asset term-structure + cross-sectional funding carry) was EXECUTED → candidate EDGE_PROVEN (44/612) but RETRACTED by C308 (0 survive Holm+BH over 612; convexity-dominated).** **C308 (C307-edge validation) EXECUTED → RETRACTED, binding `multiple_testing`.** `oos_edge_proven: false`, `edge_claim: NONE`. **C309 (COIN-M inverse cross-sectional premium-index & mark-perp basis carry, 504 configs, same cache) is the active mandatory heavy campaign.**

**Verified closure (fail-closed, no fabricated data, full provenance):**
- **Single-venue 5m spot** (Binance): C281B, C282, C283, C284, C285, C286, C288, C289, C290 — **CLOSED** (NOT_TRADABLE, binding: cost_sensitivity / zero_exposure)
- **Real USDT-M perp funding/basis** (Binance data-api): C291 — **CLOSED** (cost_sensitivity)
- **Cross-venue real-spot basis/lead-lag** (Binance+OKX): C292 — **CLOSED** (cost_sensitivity)
- **Cross-venue perp funding-carry** (OKX+Binance): C293 — **CLOSED** (cost_sensitivity)
- **Real implied-vol VRP / BTC-ETH relative value** (Deribit DVOL + Binance): C294 — **CLOSED** (cost_sensitivity)
- **Three-venue real 5m spot cross-venue basis/dispersion/lead-lag** (Binance+OKX+Coinbase): C295 — **CLOSED** (cost_sensitivity)
- **Deribit options term-structure/skew**: C296 — **DATA_BLOCKED**
- **Daily multi-year cross-sectional stat-arb** (Binance spot 1d, 24 assets, 2021-01-01..2026-11-13): C297 — **CLOSED** (mean_beats_benchmark_fail)
- **Multi-year perp funding/basis cross-sectional** (USDT-M+spot, 1h, 3 assets): C298 — **CLOSED** (zero_exposure)
- **Multi-year perp funding/basis per-asset TS** (USDT-M+spot, 1h, 3 assets): C299 — **CLOSED** (mean_beats_benchmark_fail; 0/486)
- **Multi-year perp funding/basis per-asset TS, NATIVE 5m + execution overlay**: C300 — **CLOSED** (mean_beats_benchmark_fail; 0/648)
- **Real OFI / trade-sign autocorrelation per-asset TS** (USDT-M perp aggTrades): C301 — **CLOSED** (mean_beats_benchmark_fail; 0/648)
- **Real premium-index per-asset TS** (USDT-M perp premiumIndexKlines, 1h): C302 — **CLOSED** (mean_beats_benchmark_fail; 0/486)
- **C303 cross-sectional premium-index carry** (USDT-M, 10 assets, 58,959-bar grid, K∈{2,3,5}): **COMPLETE formal negative** (`20261115T002648Z`, 0/432, cost_sensitivity). FROZEN.
- **C304 cross-sectional mark/index basis carry** (USDT-M, 10 assets, 59,031-bar grid, K∈{2,3,5}): **COMPLETE formal negative** (`20261115T023125Z`, 0/432, cost_sensitivity). FROZEN.
- **C305 reachability-exhaustion + program closure** (scope: `futures/um`+`spot/monthly`): **COMPLETE** (`20261115T032416Z`, audit 0 mismatches). Did not sweep `futures/cm`; superseded for COIN-M by C306/C307/C308/C309.
- **C306 COIN-M inverse dated-quarterly term structure** (BTC-only grid): **COMPLETE formal negative** (`20261115T050843Z`, 0/448, cost_sensitivity). FROZEN.
- **C307 COIN-M inverse multi-asset term-structure + cross-sectional funding carry** (11-perp Leg B, 3-asset Leg A): candidate `EDGE_PROVEN` (44/612) **RETRACTED by C308** (0 survive Holm+BH over 612; convexity-dominated). FROZEN as formal negative.
- **C308 C307-edge validation** (same cache, no re-ingest): **RETRACTED** (`20261115T093148Z`, 0/53 survive Holm+BH, binding `multiple_testing`, convexity share 0.607 > funding 0.324). FROZEN.
- **C309 COIN-M inverse cross-sectional premium-index & mark-perp basis carry** (11 perps, 504 pre-registered configs): **ACTIVE — build + execute.**

**C289 multiple-testing closure:** `economic_space_closed: true` over C286+C288 configs (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps). Does not subsume later families.

**C287 (testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 + no credentials. Cannot be resolved from this execution environment; decoupled from economic progress.

**Program status (2026-11-15T09:54:09Z):** USDT-M/spot/options space C281B–C305 CLOSED (formal negatives). COIN-M inverse futures space: C306 FROZEN (negative); C307 RETRACTED by C308; C308 FROZEN (RETRACTED); **C309 (COIN-M inverse cross-sectional premium-index & mark-perp basis carry) is the active mandatory heavy campaign.** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false` for all campaigns.

**Environment / verification**

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified; full suite 1488 passed / 2 skipped / 0 failed, 363.76s at 2026-11-15T09:54:09Z). `ruff`/`mypy` may not be installed; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact/closure record `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid plus real cashflow legs; zero-cost runs are labeled; any model PnL is explicitly labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked; multiple-testing correction required before any positive claim.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — economic stat-arb (costed OOS PnL) is the priority; operational hardening (C287) must not preempt or block it. C287 is blocked externally and decoupled; record it, do not retry it as economic work.

## Escalation

- **ACTIVE — C309 (mandatory heavy, new economic family):** build `scripts/preflight_c309.py` + `scripts/run_c309_coinm_premium_mark_basis_carry_oos.py` (+ tests) and execute end-to-end over the SAME C307 cache (NO re-ingest) to test the COIN-M inverse cross-sectional **premium-index & mark-perp basis carry** family (504 pre-registered configs; Holm+BH over 504; DSR/MDE; sub-period + per-year stability; per-asset attribution; inverse-convexity vs premium-carry decomposition; COIN-M cost-realism overlay). Emit 5 `reports/campaign309_*` artifacts + tests; sync state/handoff. If nothing survives, record a formal negative with binding constraint; do NOT claim tradability.
- **C308 (RETRACTED, FROZEN):** executed `20261115T093148Z`, C307 edge 0/53 survive Holm+BH, binding `multiple_testing`, convexity-dominated; 5 artifacts + 21 tests green.
- **C307 (RETRACTED by C308, FROZEN):** candidate `EDGE_PROVEN` (44/612, all Leg B COIN-M inverse funding carry) retracted; cache reused by C308/C309.
- **C306 (FROZEN, formal negative):** executed `20261115T050843Z`, NOT_TRADABLE, 0/448 edge, binding `cost_sensitivity`, BTC-only grid.
- **C305 (COMPLETE):** USDT-M/spot/options closure `20261115T032416Z`, audit 0 mismatches. Scope did not sweep `futures/cm`; superseded for COIN-M by C306/C307/C308/C309.
- **C281B–C304 (FROZEN, formal negatives):** 0 costed-OOS edge on tested formulations; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** Binance testnet REST 451, fapi 451, bybit 403, no creds — external-only; do not retry as economic work.
- Campaign numbering conflict → highest campaign JSON in `reports/`. Never fabricate data/fills; never weaken gates/costs/edge rules. Do not create HANDOFF.md.