# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 COMPLETE. Campaign #2 COMPLETE. Campaign #3 COMPLETE** (required artifacts emitted; real public data/provenance; honest). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **Verified 2026-11-09T18:13:07Z on `main@2a82c21` (working tree clean; this in-place handoff refresh is the only change):** deps importable (numpy/pandas/scipy/sklearn/statsmodels/hmmlearn/pytest/ruff/mypy). Required artifacts present & spot-checked: `reports/funding_carry_real.json` (`status: ok`), `reports/execution_lob_real.json` (`status: partial`, honest LOB feasibility), `reports/regime_adaptive_sweep.json` present, `reports/ml_gated_pairs.json` present (`status: ok`, `real_data_only: true`, `fabricated_data: false`, 544 labeled rows, cv_ok true, 0 blocked routes, 0 errors). Gates re-run fresh this check: `940 passed, 1 skipped, 0 failures`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` → All checks passed; `python -m mypy backtest/ strategies/ utils/` → Success: no issues found in 34 source files. **No fabrication. No blocking setup bottlenecks found.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`) is separate/locked — do **not** spend session on it unless explicitly requested. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs, rerunning C104-C248, rerunning completed Campaigns #1-#3 without a concrete defect, or fabricating data/fills/order books/labels/metrics.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T18:13:07Z | INITIAL TASK MESSAGE — VERIFIED STATE: Campaigns #1-#3 COMPLETE. Campaign #3 artifact `reports/ml_gated_pairs.json` present and verified (`status: ok`, real-data-only, gates pass). NEXT/ONLY FOCUS: Campaign #4 — HF/multi-timeframe cointegration (HIGH). EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #4. HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL, NO FABRICATION, NO LIGHTER TASKS.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #4 NOW.** First actions in the session must be **code+tests+real-data validation+artifact emission** for Campaign #4 (or a user-explicit override). Campaigns #1-#3 artifacts exist and are honest; **do not redo them** unless a concrete defect is found and fixed with evidence. The absence of new user direction does **not** permit planning-only work, summaries as deliverables, exploratory reading without implementation, cleanup-only work, alternate handoffs, `research_state/`/C249 registry/status work, or reruns of locked C104-C248 or completed campaigns. If a real route is blocked, record exact `blocked_routes`, keep `real_data_only`/`fabricated_data` honest, and still ship the heaviest valid implementation/tests/artifact possible under fail-closed rules. **Future agents must not avoid heavy work:** this directive remains active until `reports/pairs_mtf_5m_1h.json` exists with honest schema/provenance **and** Campaign #4 implementation/tests/gates are materially complete, at which point update only `HANDOFF.md` and advance to the production-bridge follow-on.

**Campaign #4 target (next focus): HF/multi-timeframe cointegration (HIGH)**
- Multi-timeframe pairs: 1h cointegration hedge + 5m/15m entry signals on real Binance spot candles; universe from the 11-symbol cached frame (ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP).
- Causal multi-TF alignment (no lookahead); 5m execution realism (slippage/impact/LOB-aware where feasible, honest `blocked_routes` where historical L2 unavailable).
- Purged walk-forward validation across 1h/4h/1d where data permits; fail-closed on insufficient data.
- Required artifact: `reports/pairs_mtf_5m_1h.json` (schema: `real_data_only`, `fabricated_data`, `generated_at_utc`, `campaign`, `status`, `blocked_routes`, sources/symbols/windows/metrics/limitations/checksums/provenance).
- Implementation expectations (minimum viable, heavy): add/extend strategy logic for multi-TF pairs signals; include tests (unit + integration with fixed fixtures); add `examples/run_pairs_mtf_5m_1h_real.py` (or equivalent) that emits the artifact.
- Evaluation discipline: held-out validation where applicable; no lookahead; gates fail-closed; report metrics honestly even if unmet.
- Quality gates must pass before done: `PYTHONPATH=. python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`. Fix regressions caused by your changes.
- Update **only** `HANDOFF.md` at material checkpoint/completion.

**Bottlenecks removed (verified 2026-11-09T18:13:07Z):** **NONE**. No competing handoffs/TODOs. Deps import OK. Working state clean. Stale-handoff inconsistency resolved (Campaign #3 was implemented at HEAD but `HANDOFF.md` had not been refreshed — now corrected). Historical L2/intrabar replay **not** available from current public snapshot routes — honestly documented in `reports/execution_lob_real.json` (`status: partial`), not a fake blocker. Do not create setup/blocker artifacts as a substitute for Campaign #4 heavy work.

**Handoff timestamp (UTC)**: 2026-11-09T18:13:07Z
**Repository**: `cryptoquantstatarbstrats`
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ 2a82c21`
**Single durable handoff rule**: ONLY `HANDOFF.md`. Do not create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes.
**Campaign #1 status**: COMPLETE.
**Campaign #2 status**: COMPLETE (required artifacts emitted; honest feasibility where historical L2 unavailable).
**Campaign #3 status**: COMPLETE (`reports/ml_gated_pairs.json` present, verified `status: ok`, real-data-only).

## 1) Verified state (2026-11-09T18:13:07Z)

- **Deps**: runtime/dev deps importable (numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy).
- **Gates (re-run fresh 2026-11-09T18:13:07Z)**: `PYTHONPATH=. python -m pytest tests/ -q` → `940 passed, 1 skipped, 0 failures`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` → All checks passed; `python -m mypy backtest/ strategies/ utils/` → Success: no issues found in 34 source files. **Rerun after any source change and before declaring Campaign #4 complete.**
- **Real data path**: Binance public host chain works (`www.binance.com`/data-api routes as appropriate); `api.binance.com`/`fapi.binance.com` 451 risk handled/recorded where encountered. **Never fabricate data/fills/order books.**
- **Campaign #1 artifact**: `reports/regime_adaptive_sweep.json` present.
- **Campaign #2 artifacts (REQUIRED, present):**
  - `reports/funding_carry_real.json` — **`status: ok`**, `real_data_only: true`, `fabricated_data: false`, `row_counts.total: 2296` (BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT, 574 rows each), window `2026-05-01T00:00:00Z`–`2026-11-08T00:00:00Z`, 8h funding intervals, checksums/provenance/attempts included.
  - `reports/execution_lob_real.json` — **`status: partial`** (honest), `real_data_only: true`, `fabricated_data: false`, point-in-time public spot depth/aggTrades snapshots captured for BTCUSDT/ETHUSDT. `historical_l2_intrabar_replay_feasible_from_public_routes: false` documented with observed limits and required schema/provenance expectations. **No fabricated fills/order books.**
- **Campaign #3 artifact**: `reports/ml_gated_pairs.json` — **`status: ok`**, `real_data_only: true`, `fabricated_data: false`, 544 labeled rows across 8 pairs, `cv_ok: true`, 0 blocked routes, 0 errors. Regenerated end-to-end via `examples/run_ml_gated_pairs_real.py` from cached real Binance spot data.
- **Bottlenecks:** **NONE** blocking Campaign #4.
- **Real cached data available for Campaign #4 (verified 2026-11-09T18:13:07Z):** `data/cache/` holds real Binance spot pickle artifacts including a full 11-symbol frame `2026-04-01 → 2026-10-30` 1h (`0bab5d6a...pkl`, 5112 rows × 11 cols: ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP), a 2-symbol frame `2026-04-01 → 2026-10-28` 1h (BTC/ETH, 5064 rows), and a 3-symbol frame `2026-10-01 → 2026-11-09` 1h (BTC/ETH/SOL, 944 rows). All carry `fetch_real_data_only: true`, `fetch_fabricated_data: false` provenance. Campaign #4 may load these via `DataLoader.fetch_with_provenance(..., use_cache=True)` without network access; record `blocked_routes` honestly if any route is unavailable.

## 1.1) Parallel-track caution (do not let it block the next focus campaign)

`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`) records a locked C104-C248 RQA/volume costed-OOS artifact line with `oos_edge_proven: false`. This is real repository state but **not** the next heavy-work priority. Do **not** spend the session on C249 registry/status bookkeeping instead of Campaign #4 unless explicitly requested by the user.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Held-out accuracy proxy 0.473 (<0.65), best OOS mean return 0.0 — honest, no fabrication. |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (`ok`, 2296 real funding rows, 0 blocked routes). `reports/execution_lob_real.json` (`partial`, real point-in-time snapshots feasible; historical L2 replay not feasible from current public routes; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (`ok`, real-data-only, 544 labeled rows, cv_ok true, 0 blocked routes). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, `tests/test_ml_gated_pairs.py`, `examples/run_ml_gated_pairs_real.py`. |
| #4 HF/multi-timeframe cointegration | **NOT STARTED / REQUIRED NEXT** | `reports/pairs_mtf_5m_1h.json` missing. Execute §0 immediately. |

## 3) Next focus campaign — HF/multi-timeframe cointegration (HIGH)

Execute immediately. See §0. Required artifact: `reports/pairs_mtf_5m_1h.json` (or honest `blocked`/`partial` with full schema/provenance). Real data only; no lookahead; purged WF/leakage controls; fail-closed on insufficient data; honest metrics regardless of outcome.

## 4) Follow-on campaign (only after Campaign #4 is complete + artifact exists)

**Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract for the executing session

- **Start with Campaign #4 immediately.** Campaigns #1-#3 artifacts exist; do not redo them unless fixing a concrete defect.
- Produce real artifacts with provenance. If a real-data path is blocked, record exact `blocked_routes` and rationale in the artifact/report — do not fabricate.
- When Campaign #4 reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, HEAD, gates, artifacts, outcomes, blockers). Keep it the single durable handoff.
