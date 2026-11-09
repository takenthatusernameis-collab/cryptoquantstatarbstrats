# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 (Regime-Adaptive Signal Generation) COMPLETE.** **Campaign #2 (Funding/Basis-Carry + LOB/Intrabar Feasibility) COMPLETE with required artifacts emitted (real public data/provenance, honest feasibility for LOB history).** Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **Verified 2026-11-09T16:24:13Z on `main@e6d8f31` (tree dirty only from this session's Campaign #2 implementation/artifact/handoff changes):** deps importable; quality gates PASS (`935 passed, 1 skipped`; `ruff` clean across `backtest/ data/ strategies/ utils/ tests/ examples/`; `mypy` 32 files clean on `backtest/ strategies/ utils/`). Required artifacts present: `reports/funding_carry_real.json` (`status: ok`), `reports/execution_lob_real.json` (`status: partial`, honest point-in-time feasibility). **No fabrication.** `research_state/` C249 registry/status work remains separate/locked (do not spend session on it unless explicitly requested). **Forbidden:** docs-only edits, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs, rerunning C104-C248, or fabricating data/fills/order books.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T16:24:13Z | INITIAL TASK MESSAGE — Campaign #1 COMPLETE. Campaign #2 COMPLETE (required artifacts emitted, gates PASS, HEAD `main@e6d8f31` + uncommitted Campaign #2 changes in working tree). NEXT FOCUS: Campaign #3 — ML-augmented signal filtering for cointegration persistence (HIGH), unless user explicitly requests otherwise. HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL, NO FABRICATION.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #3 NOW.** Campaign #2 required artifacts exist and are honest; do not redo Campaign #2 unless a concrete defect is found. Absence of new user direction does **not** permit lighter work. First actions must be implementation/tests/real-data validation/artifact emission for Campaign #3 (or the user-explicit request). **Never** do planning-only responses, summaries as deliverables, alternate handoffs, cleanup-only work, `research_state/`/C249 registry/status work, or reruns of locked C104-C248.

**Campaign #3 target (per follow-on plan): ML-augmented signal filtering (HIGH)**
- Classifier for cointegration persistence: rolling Engle-Granger p, Johansen trace, half-life, Hurst, spread volatility, regime features (as available/feasible with real data).
- ML-gated sizing/filtering; **purged walk-forward CV** / leakage controls; fail-closed when data insufficient.
- Real Binance/public market data only; no fabrication; record `blocked_routes` honestly.
- Required artifact: `reports/ml_gated_pairs.json` (or honest blocked/partial artifact with same schema discipline: `real_data_only`, `fabricated_data`, `generated_at_utc`, `campaign`, `status`, `blocked_routes`, sources/symbols/windows/metrics/limitations/checksums/provenance).
- Evaluation discipline: held-out validation where applicable; no lookahead; gates fail-closed; report metrics honestly even if unmet.
- Quality gates must pass before done: `python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`. Fix regressions caused by your changes.
- Update **only** `HANDOFF.md` at material checkpoint/completion.

**Bottlenecks removed:** NONE. Clean dependency/gate state; Campaign #2 public routes worked via `www.binance.com` (fapi direct 451 handled by host chain/recording). Historical L2/intrabar replay is **not** available from current public snapshot routes — honestly documented in `reports/execution_lob_real.json` (`status: partial`, `historical_l2_intrabar_replay_feasible_from_public_routes: false`), not a fake blocker.

**Handoff timestamp (UTC)**: 2026-11-09T16:24:13Z
**Repository**: `cryptoquantstatarbstrats`
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ e6d8f31` (working tree contains uncommitted Campaign #2 changes at verification time — commit/push only if user/process requests)
**Single durable handoff rule**: ONLY `HANDOFF.md`. Do not create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes.
**Campaign #1 status**: COMPLETE.
**Campaign #2 status**: COMPLETE (required artifacts emitted; honest feasibility where historical L2 unavailable).

## 1) Verified state (2026-11-09T16:24:13Z)

- **Tests**: `935 passed, 1 skipped, 0 failures` (`PYTHONPATH=. python -m pytest tests/ -q`).
- **Ruff**: `All checks passed!` across `backtest/ data/ strategies/ utils/ tests/ examples/`.
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`).
- **Dependencies**: runtime/dev deps importable in environment (numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy).
- **Real data path**: Binance public host chain works (`www.binance.com`/data-api routes used as appropriate); `api.binance.com`/`fapi.binance.com` 451 risk handled/recorded where encountered. **Never fabricate data/fills/order books.**
- **Campaign #1 artifacts**: `examples/run_regime_detection_real.py`, `reports/regime_adaptive_sweep.json` present (`real_data_only: true`, `fabricated_data: false`).
- **Campaign #2 artifacts (REQUIRED, now present):**
  - `reports/funding_carry_real.json` — **`status: ok`**, `real_data_only: true`, `fabricated_data: false`, `generated_at_utc: 2026-11-09T16:18:24.086477+00:00`, `blocked_routes: []`, `row_counts.total: 2296` (BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT, 574 rows each), window `2026-05-01T00:00:00Z`–`2026-11-08T00:00:00Z`, 8h funding intervals, checksums/provenance/attempts included. Metrics are honest funding-rate summaries/annualized carry projections only — **not an edge claim**.
  - `reports/execution_lob_real.json` — **`status: partial`** (honest), `real_data_only: true`, `fabricated_data: false`, `generated_at_utc: 2026-11-09T16:18:24.088560+00:00`, `blocked_routes: []`, point-in-time public spot depth/aggTrades snapshots captured for BTCUSDT/ETHUSDT (100 agg trades, 20 bid/ask levels each), checksums included. `historical_l2_intrabar_replay_feasible_from_public_routes: false` documented with observed limits and required schema/provenance expectations. **No fabricated fills/order books.**
- **Campaign #2 implementation/tests (uncommitted in working tree at verify time):**
  - `data/real_feed_loader.py`: added real-public helpers `fetch_binance_funding_rates`, `compute_funding_carry_metrics`, `fetch_spot_microstructure_snapshot`, `summarize_microstructure_snapshot` (host fallback, blocked-route recording, no fabrication). Existing loader family validation for `funding_basis_carry`/`intrabar_microstructure` already present and tested.
  - `examples/run_funding_carry_real.py`: emits `reports/funding_carry_real.json`.
  - `examples/run_execution_lob_real.py`: emits `reports/execution_lob_real.json`.
  - `tests/test_campaign2_funding_lob_feasibility.py`: focused mocked/network-isolated tests + artifact schema assertions.
- **Focused verification:** `tests/test_campaign2_funding_lob_feasibility.py` + `tests/test_real_feed_loader_validation.py` = `100 passed`.
- **Bottlenecks:** **NONE** blocking Campaign #3. LOB historical replay remains an honest data-availability limitation, not a code/setup blocker for this session's required feasibility artifact.

## 1.1) Parallel-track caution (do not let it block the next focus campaign)

`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`) records a locked C104-C248 RQA/volume costed-OOS artifact line with `oos_edge_proven: false`. This is real repository state but **not** the next heavy-work priority. Do **not** spend the session on C249 registry/status bookkeeping instead of Campaign #3 unless explicitly requested by the user.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Held-out accuracy proxy 0.473 (<0.65), best OOS mean return 0.0 — honest, no fabrication. |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (`ok`, 2296 real funding rows, 0 blocked routes). `reports/execution_lob_real.json` (`partial`, real point-in-time snapshots feasible; historical L2 replay not feasible from current public routes; no fabricated fills/order books). |

## 3) Next focus campaign — ML-augmented signal filtering (HIGH)

Execute immediately. See §0. Required artifact: `reports/ml_gated_pairs.json` (or honest `blocked`/`partial` with full schema/provenance). Real data only; no lookahead; purged WF/leakage controls; fail-closed on insufficient data; honest metrics regardless of outcome.

## 4) Follow-on campaigns (only after Campaign #3 is complete + artifact exists)

1. **HF/multi-timeframe (MEDIUM)** — 5m/15m, multi-TF cointegration (1h hedge, 5m signals), seasonality, realistic 5m execution. Artifact: `reports/pairs_mtf_5m_1h.json`.
2. **Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract for the executing session

- **Start with Campaign #3 immediately.** Campaign #2 artifacts exist; do not redo them unless fixing a concrete defect.
- Produce real artifacts with provenance. If a real-data path is blocked, record exact `blocked_routes` and rationale in the artifact/report — do not fabricate.
- When Campaign #3 reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, HEAD, gates, artifacts, outcomes, blockers). Keep it the single durable handoff.
