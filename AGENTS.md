# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-14T20:43:43Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.

**Verified state (this refresh, 2026-11-14T20:43:43Z):** `python -m pytest tests/ -q` → **1339 passed, 2 skipped, 0 failed** (456.27s). Deps import-verified: numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. The economic stat-arb program is **COMPLETE — all reachable real-data formulations closed NOT_TRADABLE, 0 costed-OOS edge**:

- **C301 (real OFI / trade-sign autocorrelation, Binance USDT-M perp aggTrades, 2023-01..02, 648 runs):** executed end-to-end at `20261114T193801Z` → **NOT_TRADABLE**, `edge_proven:false`, **0/648 edge**, binding `mean_beats_benchmark_fail`. Cache `data/cache/campaign301_aggtrades_ofi.pkl` = 3,676,412 B, SHA256 `4ce779531636d833c285cbfd87fe1f46b91bc3d8447c92853be8550973f1b9cf`. Artifacts `reports/campaign301_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261114T193801Z.json` all carry `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`.
- **C281B→C300:** all **COMPLETE formal negative results** (0 costed-OOS edge, frozen). Binding constraints: `cost_sensitivity` / `zero_exposure` / `mean_beats_benchmark_fail`.
- **C287 (external execution / testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient), `fapi` 451, bybit 403, no credentials. **Cannot be resolved from this execution environment.** External execution is the only remaining path to a tradable claim, but it is blocked by geography/credentials and **decoupled from economic progress**; do not re-probe as economic work.

**Bottleneck status this refresh:** no data/compute bottleneck remains. The GitHub 100 MB push limit is resolved (compact ndarray caches < 100 MB). C287 is an **external-only blocker** — record it as blocked/decoupled and proceed to program closure; it must not preempt or be mistaken for economic work.

**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-14T20:43:43Z) — PROGRAM CLOSURE VERIFIED: NO FURTHER ECONOMIC WORK POSSIBLE WITHOUT GENUINELY NEW REACHABLE DATA

**Program closure is COMPLETE and VERIFIED.** All campaigns C281B–C301 executed NOT_TRADABLE (0/648+ costed-OOS edge across the program). The entire **reachable real-data stat-arb space is CLOSED** at every tested resolution (single-venue 5m spot; perp funding/basis single-venue, cross-venue, per-asset time-series, cross-sectional; options IV; daily cross-sectional; real OFI/trade-sign autocorrelation; 2020-01..2026-10). C287 external execution remains BLOCKED/DECOUPLED by external constraints (testnet REST 451, fapi 451, bybit 403, missing credentials, geography) that cannot be resolved from this environment.

**No further economic campaign is registered.** Do not re-plan, re-probe, or re-skin the closed family (no lookback/hold/threshold variants of C299/C300, no re-probe of excluded candidates, no microstructure re-skin without a genuinely new reachable data source). The only path to a tradable claim is external execution (C287), which requires credentials/network egress outside this environment.

**MANDATORY verification work for next session (heavy work — no status-only turns):**
1. **Verify closure artifacts exist and are consistent:** confirm `reports/program_closure_final_*.json` + `.md` exist with `reachable_real_data_cross_sectional_stat_arb_space: CLOSED`, all campaigns `NOT_TRADABLE`, `edge_claim: NONE`, `oos_edge_proven: false`, C287 `BLOCKED`/`decoupled_from_economic_progress: true`, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; full provenance (source, timestamp, host, blocked routes, rationale) for every number.
2. **Integrity audit:** run `python -m pytest tests/ -q` → MUST be 0 failed; verify zero mismatches across all campaign cache/meta/provenance/artifact references; confirm `zero_tradable_edge_registry_confirmed: true`.
3. **Sync state:** update `AGENTS.md` (`updated_at_utc`, `active_initial_task`, `next_campaign`, frozen records retained) and `research_state/state.yaml` with current timestamp and all closure artifact paths+SHA256 (no zeros, no nesting regression).
4. **Re-verify:** run `python -m pytest tests/ -q` green after state/handoff sync.

**Acceptance gate:** closure artifacts present with real-data flags + SHA256-from-bytes; integrity audit clean (0 issues); pytest green (0 failed); `AGENTS.md` timestamp/evidence match `research_state/state.yaml`; C287 recorded as blocked/decoupled (not retried as economic work). **Any claim of tradable edge without costed OOS proof is a hard failure.**

**Never** fabricate data/fills/credentials, weaken gates/costs/edge rule, relabel data, claim tradable edge, edit `.github/workflows/main.yml`, or create/read/edit `HANDOFF.md`. C287 is external-only and must not preempt or be mistaken for economic work.

## RESEARCH PROGRAM STATUS (C281B–C301 frozen)

**Status:** C281B→C297 (17 campaigns, ~1,400+ WF configs), **C298**, **C299**, **C300**, and **C301** all returned **0 costed OOS edge** on the formulations/windows tested. The entire real-archive funding-carry / spot-perp basis family plus the OFI/trade-sign autocorrelation family is CLOSED; `reachable_real_data_cross_sectional_stat_arb_space: CLOSED`.

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

**C289 multiple-testing closure:** `economic_space_closed: true` over C286+C288 configs (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps). Does not subsume C299/C300 (different formulation/window).

**C287 (testnet gateway):** **BLOCKED/DECOUPLED** — Binance testnet REST HTTP 451 (CloudFront geographic block, not transient) + no credentials. Cannot be resolved from this execution environment. External execution capability is the only remaining path to a tradable claim, but it is blocked by geography/credentials and decoupled from economic progress.

**Program closure (this refresh):** COMPLETE — record explicit closure verified; no further economic campaign is registered; the only remaining path (C287) requires external credentials/network egress outside this environment.

**Environment / verification**

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python scripts/verify_env.py --json
python scripts/bootstrap_dev_env.py
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1 (import-verified; suite 1339 passed / 2 skipped / 0 failed). `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

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

- **C301 (COMPLETE formal negative, frozen):** real OFI / trade-sign autocorrelation per-asset time-series stat-arb NOT_TRADABLE, 648 runs, 545 with exposure / 103 zero-exposure, 0/648 edge, binding `mean_beats_benchmark_fail`. Closes the microstructure family.
- **C300 / C299 / C298 (COMPLETE formal negative, frozen):** perp funding/basis per-asset time-series (1h & 5m) and cross-sectional — all NOT_TRADABLE, 0 edge.
- **C297 (COMPLETE formal negative):** daily multi-year cross-sectional stat-arb NOT_TRADABLE (0/135 costed OOS edge, binding mean_beats_benchmark_fail).
- **C296 (COMPLETE data-blocked closure):** Deribit options term-structure/skew — no deep historical per-strike mark IV feed reachable.
- C295 (frozen, NOT_TRADABLE): three-venue 5m spot, 0/162 edge, binding cost_sensitivity.
- C294 (frozen): Deribit DVOL + Binance VRP, closed NOT_TRADABLE.
- C293 (frozen): OKX funding + Binance funding (C291 cache).
- C292 (frozen): Binance+OKX 5m cross-venue spot basis.
- C291 (frozen): `data.binance.vision` USDT-M 5m klines + fundingRate archives. `fapi.binance.com` remains HTTP 451.
- Binance API/host changes → `data/real_feed_loader.py` host chain. Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable). Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C281B–C301 complete and frozen; **program closure is the active task**; C287 (external execution) remains BLOCKED/decoupled and external to this environment.
