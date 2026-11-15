# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T09:05:00Z — **C307 EXECUTED end-to-end → EDGE_PROVEN (program's FIRST positive result), reproduced across two independent runs. `latest_campaign_done: C307`, `oos_edge_proven: true`. C308 is the active mandatory heavy campaign: RIGOROUSLY VALIDATE THE C307 EDGE (INCOMPLETE: `scripts/preflight_c308.py`, `scripts/run_c308_c307_edge_validation_oos.py`, `tests/test_preflight_c308.py`, `tests/test_c308_c307_edge_validation_oos.py`, and `reports/campaign308_*` artifacts are ABSENT; verified 2026-11-15T09:05:00Z).** C307 implementation (ingest/preflight/runner/tests) is COMPLETE and committed; the real ingest, preflight, runner, and C307 tests all executed green this session. Bootstrap `ready:true`/deps green re-verified (Python 3.12.3; pytest 9.2.0, pytest-asyncio 1.5.0, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 importable). **Full suite 2026-11-15T09:05:00Z: 1467 passed / 2 skipped / 0 failed (319.10s).** `HANDOFF.md` absent. Next session MUST implement and execute C308 end-to-end (≥1 real-data validation pass over the C307 cache, 5 SHA256 artifacts, tests+full-suite green, state synced). No planning-only, status-only, or partial-leg turn is acceptable. ANY turn that does not produce real-data validation, a passing test, or an artifact update is NOT economic progress.

## INITIAL TASK MESSAGE (2026-11-15T09:05:00Z) — NEXT FOCUS CAMPAIGN: VALIDATE THE C307 EDGE — CAMPAIGN C308 (HEAVY, MANDATORY, UNAVOIDABLE, NON-NEGOTIABLE)

**NEXT SESSION ACTION (non-optional, do not defer, do not plan, do not status-report — EXECUTE):** C307 is DONE and returned the program's FIRST `EDGE_PROVEN` result. The next session must build and run C308 to rigorously validate (or retract) that edge, reusing the C307 cache (NO re-ingest, NO new data, NO gate/cost/edge-rule weakening):
```
python scripts/bootstrap_dev_env.py
# C307 cache already on disk: data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl (SHA256 7045013e…13d3)
python scripts/preflight_c308.py            # must print ready:true and exit 0
python scripts/run_c308_c307_edge_validation_oos.py
python -m pytest tests/test_preflight_c308.py tests/test_c308_c307_edge_validation_oos.py -q
python -m pytest tests/ -q                  # must be 0 failed
```
**COMPLETION GATE (all required, no exceptions):**
1. Preflight `scripts/preflight_c308.py` prints `ready:true` and exits 0 (fail-closed if the C307 cache/artifacts are missing or the 44 edge configs are not reproducible from cache).
2. Runner `scripts/run_c308_c307_edge_validation_oos.py` executes end-to-end over the C307 cache and validates the 44 edge configs on ALL of: (a) multiple-testing correction across the 612 pre-registered configs — Holm AND Benjamini-Hochberg, reporting how many of the 44 survive; (b) DSR / minimum detectable effect given 203 splits; (c) sub-period stability (first vs second half of 2022-07..2026-06 and per-year); (d) per-asset contribution decomposition over the 11 perps; (e) inverse-convexity attribution — decompose the edge into funding carry vs inverse-settlement convexity (`1/entry − 1/exit`) using a linear-settlement shadow book; (f) execution-cost-realism overlay (COIN-M inverse taker/maker fees, native 8h funding settlement, mark slippage, turnover/rebalance).
3. 5 fresh timestamped SHA256 artifacts emitted to `reports/campaign308_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json`, each `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, SHA256-from-bytes.
4. C308 tests green (`tests/test_preflight_c308.py`, `tests/test_c308_c307_edge_validation_oos.py`).
5. Full test suite 0 failed (`python -m pytest tests/ -q`).
6. AGENTS.md + `research_state/state.yaml` synced (`latest_campaign_done: C308` if executed, cache/artifact paths/SHA256s, verdict/binding, next family).

**FAILURE TO MEET ANY GATE ITEM = INCOMPLETE SESSION. DO NOT STOP. DO NOT REPORT STATUS. EXECUTE.**

**FAIL-CLOSED VALIDATION RULE (non-negotiable):** if the C307 edge does NOT survive multiple-testing correction (Holm/BH) OR is explained by inverse-settlement convexity rather than funding carry OR fails the execution-cost-realism overlay, record a **formal negative: C307 edge RETRACTED**, with the binding constraint, and do NOT claim tradability. The prior `EDGE_PROVEN` verdict must be corrected in state/handoff to `RETRACTED`/`NOT_TRADABLE` in that case. Do NOT weaken the edge rule, cost grid, or gates to force a positive.

**C307 result being validated (executed 2026-11-15T085840Z; reproduced from 20261115T083047Z):**
- **EDGE_PROVEN: 44 of 612 costed-OOS configs.** ALL 44 are **Leg B** (cross-sectional COIN-M inverse funding carry): signals `fund_level` (16), `fund_z` (16), `fund_sign` (12); `gate=off`; lookbacks L∈{720,1440}; K∈{2,3,5}; holds {1,6,24}.
- Every cost slice `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps has net>0 for every one of the 44; each beats a **negative** equal-weight B&H benchmark (B&H mean ≈ −2.59e-5) and flat (0).
- **Leg A (term structure) = 0 edge.** BTCUSD/ETHUSD each aligned 6,489 bars (2025-03-01 → 2026-10-31, 4 contracts incl. 3 quarterlies); XRPUSD 1,464 bars (2026-09..10 only, < train+test=888) → scope-noted and excluded from WF, not a whole-campaign failure.
- **Leg B universe:** 11 perps, common funding grid 34,968 bars (2022-07-01 → 2026-06-30), 203 WF splits.
- Inverse PnL `pnl_coin = notional_usd*(1/entry − 1/exit)*signed_weight`; funding `funding_pnl = −funding_rate*signed_weight` at native 8h boundaries (causal); costs on ALL legs.
- Cache `data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl` = 16,989,995 B, SHA256 `7045013e18de42b64cf583236c90da57c30e6779ac3b58c4b86bfa87eb1373d3`; meta SHA256 `9b83353440cfd1be2fb95c51fdce0539d516aaca9aee97bc532aecfaea9a9b4d`; provenance SHA256 `b8506f3da25b008f53b57cdde978d42c34763d44c7c99c2c99d41a0b47c6309e`.
- Artifacts `reports/campaign307_{oos_sweep,tradable_edge_registry,summary,verdict}_20261115T085840Z.json` SHA256s: sweep `8b6aa194bd07bde5f995cbb4a64243c281dbc0e3cbae33d2b039e6f6b26c7974`, registry `4229ac1a472e93491648cb1aa15b9c66d5de4e929aceba8b4d394a7dc8cdbc41`, summary `ec5852c360cf354f2404ad13177aa747a8f04502c3cbebe4696e91b8ab56c3cf`, verdict `14c0a0cbb6ef7ed94f698f56b01f787b97413cfc6075cd8d8082f743ae4cf3f8` (binding_constraint null). `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.
- C307 tests: `tests/test_preflight_c307.py` + `tests/test_c307_coinm_multiasset_term_structure_carry_oos.py` = **28 passed**.

**Why C308 is necessary (not optional):** the whole prior program (C281B–C306) was formal negatives; C307 is the first positive and its edge is small (≈2–6 bps/split net at 0 bps, still positive at 40 bps) and concentrated in 44/612 configs. Before any tradable claim it MUST clear multiple-testing correction, DSR/MDE, sub-period stability, per-asset attribution, inverse-convexity vs funding-carry attribution, and execution-cost realism. This is the scientifically correct next heavy campaign.

**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics. Any turn that produces neither a real-data validation, a costed-OOS run, a passing test, or an artifact update is NOT economic progress and must not be reported as such.

**Verified state (refreshed 2026-11-15T09:05:00Z):** `HANDOFF.md` absent (correct). Deps import-verified; `python scripts/bootstrap_dev_env.py` returned `ready:true`. **Full suite 2026-11-15T09:05:00Z: 1467 passed, 2 skipped, 0 failed (319.10s).** C307 fully executed (cache + 4 artifacts + 28 tests green). The 10 historical C305 program-closure reds remain FIXED; no test is skipped, masked, or weakened. Templates present on disk to copy: C306 `scripts/ingest_c306_coinm_term_structure.py`, `scripts/preflight_c306.py`, `scripts/run_c306_coinm_term_structure_oos.py`, `tests/test_preflight_c306.py`, `tests/test_c306_coinm_term_structure_oos.py`; C307 `scripts/ingest_c307_coinm_multiasset_term_structure_carry.py`, `scripts/preflight_c307.py`, `scripts/run_c307_coinm_multiasset_term_structure_carry_oos.py`, `tests/test_preflight_c307.py`, `tests/test_c307_coinm_multiasset_term_structure_carry_oos.py`; C303/C304 cross-sectional scripts/tests. `research_state/state.yaml` parses cleanly; `latest_campaign_done: C307`.

**Corrected reachability matrix (verified; source `https://data.binance.vision/data/futures/cm/monthly/`; do NOT re-probe as unknown):**
- **Perp klines / premiumIndexKlines / markPriceKlines:** HTTP 200 for 2020-12..2026-10 for 10/11 perps; `XLMUSD_PERP` klines start **2021-04** (2021-01..03 = 404). All 11 perps HTTP 200 at both 2022-07 and 2026-06.
- **`fundingRate`:** HTTP 200 **only 2022-07..2026-06**; 2022-06 and 2026-07..2026-10 are 404. Schema: `calc_time` (ms), `funding_interval_hours` (8), `last_funding_rate`; 90 rows/month. Funding is native 8h, not 1h.
- **Dated quarterlies:** `BTCUSD_250627`, `BTCUSD_250926`, `BTCUSD_261225`, `ETHUSD_250627`, `ETHUSD_250926`, `ETHUSD_261225`, `XRPUSD_261225`. Other underlyings' `*_261225` are 404 (only BTC/ETH/XRP have dated quarterlies).
- **ETHUSD_PERP:** klines/premium/mark are HTTP 200 across 2020-12..2026-10 (the old "404 every month" note was WRONG); C306 excluded ETHUSD only because ETHUSD_261225 had <888 overlapping bars.

**Bottlenecks removed (do NOT re-litigate):** (1) C305 probe scope-limited to `futures/um`+`spot` — resolved by C306/C307 using `futures/cm`. (2) Archive host flaky — every download MUST retry with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable. (3) Recent monthly archives may carry CSV header `open_time` — skip rows whose first field is non-numeric. (4) `pytest-asyncio` present (1.5.0); if missing treat as Step 0 bootstrap. (5) Caches < 100 MB (assert). (6) C287 external-only (451/no creds) — decoupled, never retry as economic work. (7) COIN-M `fundingRate` only 2022-07..2026-06; do not attempt other months. (8) ETHUSD_PERP klines HTTP 200. (9) `XLMUSD_PERP` klines start 2021-04. (10) Dated quarterlies only for BTCUSD/ETHUSD/XRPUSD.

**Session bootstrap (Step 0, before any campaign code):** `python scripts/bootstrap_dev_env.py`; install `pytest-asyncio>=0.23` only if async tests report "async def not natively supported". Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run.

## C307 (COMPLETE — EDGE_PROVEN, reproduced; pending C308 validation)

Executed `20261115T085840Z` (and independently reproduced from `20261115T083047Z`) → **EDGE_PROVEN**, `edge_proven:true`, **44/612 costed-OOS configs**, all Leg B COIN-M inverse cross-sectional funding carry (`fund_level`/`fund_z`/`fund_sign`, gate=off, L∈{720,1440}, K∈{2,3,5}, holds{1,6,24}); every cost slice 0..40 bps net>0 and beats a negative equal-weight B&H; Leg A term structure 0 edge. Cache/artifact SHA256s and full detail recorded above and in `research_state/state.yaml` (`c307_status`). **This is a CANDIDATE edge pending C308 validation; it is NOT yet a tradable claim.** If C308 retracts it, record the formal negative.

## C306 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T050843Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/448 edge**, 448/448 with exposure, binding `cost_sensitivity`. Cache `data/cache/campaign306_coinm_term_structure.pkl` SHA256 `056066849b6b4c304cf46d48f3f3c4c1aaf87c47480fdfb01eacc17ede42bffe` (4,914 bars, 1 asset BTCUSD, 4 contracts, 2 real outage bars). Artifacts `reports/campaign306_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T050843Z.json`. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.

## RESEARCH PROGRAM STATUS (C281B–C306 frozen; C307 EDGE_PROVEN candidate; C308 validation active)

**Status:** C281B→C306 returned **0 costed OOS edge** on the formulations/windows tested (all COMPLETE formal negatives, frozen). USDT-M/spot/options families CLOSED (C305). C306 (COIN-M inverse dated-quarterly term-structure, BTC-only grid) FROZEN as formal negative. **C307 (COIN-M inverse multi-asset term-structure + cross-sectional funding carry) EXECUTED → EDGE_PROVEN (44/612, all Leg B funding carry), reproduced twice; this is a CANDIDATE edge pending C308 rigorous validation.** `oos_edge_proven: true` (program-level, C307 candidate), `edge_claim: C307_LEG_B_COIN_M_INVERSE_FUNDING_CARRY_CANDIDATE_PENDING_C308_VALIDATION`.

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
- **C303 cross-sectional premium-index carry** (10 assets, 58,959-bar grid, K∈{2,3,5}): **COMPLETE formal negative** (`20261115T002648Z`, 0/432, cost_sensitivity). FROZEN.
- **C304 cross-sectional mark/index basis carry** (10 assets, 59,031-bar grid, K∈{2,3,5}): **COMPLETE formal negative** (`20261115T023125Z`, 0/432, cost_sensitivity). FROZEN.
- **C305 reachability-exhaustion + program closure** (scope: `futures/um`+`spot/monthly`): **COMPLETE** (`20261115T032416Z`, audit 0 mismatches). Did not sweep `futures/cm`; superseded for COIN-M by C306/C307.
- **C306 COIN-M inverse dated-quarterly term structure** (BTC-only grid): **COMPLETE formal negative** (`20261115T050843Z`, 0/448, cost_sensitivity). FROZEN.
- **C307 COIN-M inverse multi-asset term-structure + cross-sectional funding carry** (11-perp Leg B, 3-asset Leg A): **EDGE_PROVEN (44/612), reproduced twice, CANDIDATE pending C308.**

**C289 multiple-testing closure:** `economic_space_closed: true` over C286+C288 configs (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps). Does not subsume later families.

**C287 (testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 + no credentials. Cannot be resolved from this execution environment; decoupled from economic progress.

**Program status (2026-11-15T09:05:00Z):** USDT-M/spot/options space C281B–C305 CLOSED (formal negatives). COIN-M inverse futures space: C306 FROZEN (negative); **C307 EDGE_PROVEN (44/612, all Leg B funding carry) — CANDIDATE; C308 validation is the active mandatory heavy campaign.** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false` for all campaigns.

**Environment / verification**

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified; full suite 1467 passed / 2 skipped / 0 failed, 319.10s at 2026-11-15T09:05:00Z). `ruff`/`mypy` may not be installed; do not claim they passed unless actually run.

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

- **ACTIVE — C308 (mandatory heavy, validate-or-retract):** rigorously validate the C307 Leg B COIN-M inverse funding-carry edge (44/612 configs) on the SAME C307 cache — multiple-testing correction (Holm + BH over 612 configs), DSR/MDE, sub-period + per-year stability, per-asset attribution over 11 perps, inverse-convexity vs funding-carry decomposition, and COIN-M execution-cost-realism overlay. Emit 5 `reports/campaign308_*` artifacts + tests; sync state/handoff. If the edge does not survive, record **C307 edge RETRACTED** formal negative with binding constraint; do NOT claim tradability.
- **C307 (EDGE_PROVEN candidate, reproduced):** executed `20261115T085840Z`, 44/612 costed-OOS edge, all Leg B COIN-M inverse funding carry; pending C308 validation. Cache/artifact SHA256s recorded above and in state.yaml.
- **C306 (FROZEN, formal negative):** executed `20261115T050843Z`, NOT_TRADABLE, 0/448 edge, binding `cost_sensitivity`, BTC-only grid.
- **C305 (COMPLETE):** USDT-M/spot/options closure `20261115T032416Z`, audit 0 mismatches. Scope did not sweep `futures/cm`; superseded for COIN-M by C306/C307.
- **C281B–C304 (FROZEN, formal negatives):** 0 costed-OOS edge on tested formulations; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** Binance testnet REST 451, fapi 451, bybit 403, no creds — external-only; do not retry as economic work.
- Campaign numbering conflict → highest campaign JSON in `reports/`. Never fabricate data/fills; never weaken gates/costs/edge rules. Do not create HANDOFF.md.