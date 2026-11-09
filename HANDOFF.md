# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 COMPLETE. Campaign #2 COMPLETE** (required artifacts emitted; real public data/provenance; honest LOB historical feasibility). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **Verified 2026-11-09T17:13:22Z on `main@58af8fd` (working tree clean; this in-place handoff refresh is the only change):** deps importable (numpy/pandas/scipy/sklearn/statsmodels/hmmlearn/pytest). Required artifacts present & spot-checked: `reports/funding_carry_real.json` (`status: ok`, `real_data_only: true`, `fabricated_data: false`), `reports/execution_lob_real.json` (`status: partial`, honest point-in-time feasibility, historical L2/intrabar replay not feasible from current public routes), `reports/regime_adaptive_sweep.json` present. `reports/ml_gated_pairs.json` **NOT present** — Campaign #3 work remains. Gates re-run fresh this check: `935 passed, 1 skipped, 0 failures` (59.19s); `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` → All checks passed; `mypy backtest/ strategies/ utils/` → Success: no issues found in 32 source files. **No fabrication. No blocking setup bottlenecks found.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`) is separate/locked — do **not** spend session on it unless explicitly requested. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs, rerunning C104-C248, or fabricating data/fills/order books/labels/metrics.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T17:13:22Z | INITIAL TASK MESSAGE — VERIFIED STATE: Campaigns #1-#2 COMPLETE; Campaign #3 NOT STARTED (`reports/ml_gated_pairs.json` MISSING). NEXT/ONLY FOCUS: Campaign #3 — ML-augmented signal filtering for cointegration persistence (HIGH). EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #3. HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL, NO FABRICATION, NO LIGHTER TASKS.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #3 NOW.** First actions in the session must be **code+tests+real-data validation+artifact emission** for Campaign #3 (or a user-explicit override). Campaign #2 artifacts exist and are honest; **do not redo Campaign #2** unless a concrete defect is found and fixed with evidence. The absence of new user direction does **not** permit planning-only work, summaries as deliverables, exploratory reading without implementation, cleanup-only work, alternate handoffs, `research_state/`/C249 registry/status work, or reruns of locked C104-C248. If a real route is blocked, record exact `blocked_routes`, keep `real_data_only`/`fabricated_data` honest, and still ship the heaviest valid implementation/tests/artifact possible under fail-closed rules. **Future agents must not avoid heavy work:** this directive remains active until `reports/ml_gated_pairs.json` exists with honest schema/provenance **and** Campaign #3 implementation/tests/gates are materially complete, at which point update only `HANDOFF.md` and advance to §4 follow-ons.

**Campaign #3 target (per follow-on plan): ML-augmented signal filtering (HIGH)**
- Classifier for cointegration persistence: rolling Engle-Granger p, Johansen trace, half-life, Hurst, spread volatility, regime features (as available/feasible with real data).
- ML-gated sizing/filtering; **purged walk-forward CV** / leakage controls; fail-closed when data insufficient.
- Real Binance/public market data only; no fabrication; record `blocked_routes` honestly.
- Required artifact: `reports/ml_gated_pairs.json` (or honest `blocked`/`partial` artifact with same schema discipline: `real_data_only`, `fabricated_data`, `generated_at_utc`, `campaign`, `status`, `blocked_routes`, sources/symbols/windows/metrics/limitations/checksums/provenance).
- Implementation expectations (minimum viable, heavy): add/extend strategy logic for ML gating of pairs/stat-arb signals; include tests (unit + small integration with synthetic/fixed fixtures for determinism, plus real-data path exercised where feasible); add `examples/run_ml_gated_pairs_real.py` (or equivalent) that emits the artifact.
- Evaluation discipline: held-out validation where applicable; no lookahead; gates fail-closed; report metrics honestly even if unmet.
- Quality gates must pass before done: `PYTHONPATH=. python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`. Fix regressions caused by your changes.
- Update **only** `HANDOFF.md` at material checkpoint/completion.

**Bottlenecks removed (verified 2026-11-09T17:13:22Z):** **NONE**. No competing handoffs/TODOs. Deps import OK. Working state clean. Campaign #2 public routes previously verified. Historical L2/intrabar replay **not** available from current public snapshot routes — honestly documented in `reports/execution_lob_real.json` (`status: partial`), not a fake blocker. Do not create setup/blocker artifacts as a substitute for Campaign #3 heavy work.

**Handoff timestamp (UTC)**: 2026-11-09T17:13:22Z
**Repository**: `cryptoquantstatarbstrats`
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ 58af8fd`
**Single durable handoff rule**: ONLY `HANDOFF.md`. Do not create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes.
**Campaign #1 status**: COMPLETE.
**Campaign #2 status**: COMPLETE (required artifacts emitted; honest feasibility where historical L2 unavailable).

## 1) Verified state (2026-11-09T17:13:22Z)

- **Deps**: runtime/dev deps importable (numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy). **Re-verified fresh this check: all importable.**
- **Gates (re-run fresh 2026-11-09T17:13:22Z)**: `PYTHONPATH=. python -m pytest tests/ -q` → `935 passed, 1 skipped, 0 failures` (59.19s); `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` → All checks passed; `python -m mypy backtest/ strategies/ utils/` → Success: no issues found in 32 source files. **Rerun after any source change and before declaring Campaign #3 complete.**
- **Real data path**: Binance public host chain works (`www.binance.com`/data-api routes as appropriate); `api.binance.com`/`fapi.binance.com` 451 risk handled/recorded where encountered. **Never fabricate data/fills/order books.**
- **Campaign #1 artifact**: `reports/regime_adaptive_sweep.json` present.
- **Campaign #2 artifacts (REQUIRED, present):**
  - `reports/funding_carry_real.json` — **`status: ok`**, `real_data_only: true`, `fabricated_data: false`, `row_counts.total: 2296` (BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT, 574 rows each), window `2026-05-01T00:00:00Z`–`2026-11-08T00:00:00Z`, 8h funding intervals, checksums/provenance/attempts included. Metrics are honest funding-rate summaries/annualized carry projections only — **not an edge claim**.
  - `reports/execution_lob_real.json` — **`status: partial`** (honest), `real_data_only: true`, `fabricated_data: false`, point-in-time public spot depth/aggTrades snapshots captured for BTCUSDT/ETHUSDT. `historical_l2_intrabar_replay_feasible_from_public_routes: false` documented with observed limits and required schema/provenance expectations. **No fabricated fills/order books.**
- **Campaign #3 artifact**: `reports/ml_gated_pairs.json` **MISSING** — this is the active heavy-work target.
- **Bottlenecks:** **NONE** blocking Campaign #3.
- **Real cached data available for Campaign #3 (verified 2026-11-09T17:13:22Z):** `data/cache/` holds real Binance spot pickle artifacts including a full 11-symbol frame `2026-04-01 → 2026-10-30` 1h (`0bab5d6a...pkl`, 5112 rows × 11 cols: ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP), a 2-symbol frame `2026-04-01 → 2026-10-28` 1h (BTC/ETH, 5064 rows), and a 3-symbol frame `2026-10-01 → 2026-11-09` 1h (BTC/ETH/SOL, 944 rows). All carry `fetch_real_data_only: true`, `fetch_fabricated_data: false` provenance. Campaign #3 may load these via `DataLoader.fetch_with_provenance(..., use_cache=True)` without network access; record `blocked_routes` honestly if any route is unavailable.

## 1.1) Parallel-track caution (do not let it block the next focus campaign)

`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`) records a locked C104-C248 RQA/volume costed-OOS artifact line with `oos_edge_proven: false`. This is real repository state but **not** the next heavy-work priority. Do **not** spend the session on C249 registry/status bookkeeping instead of Campaign #3 unless explicitly requested by the user.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Held-out accuracy proxy 0.473 (<0.65), best OOS mean return 0.0 — honest, no fabrication. |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (`ok`, 2296 real funding rows, 0 blocked routes). `reports/execution_lob_real.json` (`partial`, real point-in-time snapshots feasible; historical L2 replay not feasible from current public routes; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | **NOT STARTED / REQUIRED NEXT** | `reports/ml_gated_pairs.json` missing. Execute §0 immediately. |

## 3) Next focus campaign — ML-augmented signal filtering (HIGH)

Execute immediately. See §0. Required artifact: `reports/ml_gated_pairs.json` (or honest `blocked`/`partial` with full schema/provenance). Real data only; no lookahead; purged WF/leakage controls; fail-closed on insufficient data; honest metrics regardless of outcome.

**Real cached data for Campaign #3 (verified this check):** `data/cache/` has real Binance spot frames — full 11-symbol `2026-04-01→2026-10-30` 1h (5112 rows: ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP), BTC/ETH 1h `2026-04-01→2026-10-28` (5064 rows), BTC/ETH/SOL 1h `2026-10-01→2026-11-09` (944 rows). All carry `fetch_real_data_only: true` / `fetch_fabricated_data: false`. Load via `DataLoader().fetch_with_provenance([...], start, end, interval="1h", use_cache=True)`; record `blocked_routes` honestly if any route is unavailable. The 17-pair universe used by Campaigns #34-#37 (BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC) is fully covered by the 11-symbol frame.

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
