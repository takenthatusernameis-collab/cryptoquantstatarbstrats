# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaigns #1-#4 COMPLETE** (required artifacts present/verified; real data+provenance; honest). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **No fabrication.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`, locked C104-C248) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs/plans, rerunning C104-C248, rerunning completed Campaigns #1-#4 without a concrete defect, or fabricating data/fills/order books/labels/metrics.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T21:14:26Z | VERIFIED NOW | `HANDOFF.md` is the ONLY root handoff/TODO. C1-C4 artifacts present+honest: `reports/funding_carry_real.json` (ok,true,false), `reports/execution_lob_real.json` (partial,true,false; historical L2 replay infeasible), `reports/regime_adaptive_sweep.json` (present), `reports/ml_gated_pairs.json` (ok,true,false), `reports/pairs_mtf_5m_1h.json` (ok,true,false; campaign "Campaign #4 - HF/multi-timeframe cointegration"; 14 pairs, 14 ok; base cost-sensitivity 8/8 ok; mean_sharpe_ok negative — reported honestly, no edge claimed). Implementation/tests present: `utils/mtf_pairs.py`, `examples/run_pairs_mtf_5m_1h_real.py`, `tests/test_pairs_mtf.py` (5 passed). Fresh gates (2026-11-09): `945 passed, 1 skipped`; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` all passed; `mypy backtest/ strategies/ utils/` success (35 source files). 5m+1h real data provenance recorded (Binance public spot klines via loader/cache; 5m fetch succeeded 26208 rows; 1h cache hit). EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #5 (PRODUCTION BRIDGE) IMMEDIATELY.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #5 NOW (HEAVY WORK, NON-OPTIONAL).**
- **First substantive actions MUST produce code + tests + honest real/public/testnet-validated deliverable/artifact** for Campaign #5 (or a user-explicit override). Do **NOT** stop after reading, summarizing, status-checking, planning, or refreshing docs. Planning/summaries/exploratory reading without implementation = **failure**.
- **Do NOT redo Campaigns #1-#4** unless you find a concrete defect and fix it with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248.
- **No fabrication. Ever.** No synthetic/fabricated fills, order books, exchange responses, balances, PnL, or metrics presented as real/testnet evidence. If testnet/live routes are unavailable or credentials absent, record exact `blocked_routes`/limitations, keep `real_data_only`/`fabricated_data`/environment honest, and still ship the **heaviest valid paper-trading/OMS/risk implementation + tests + dry-run artifact possible** under fail-closed rules.
- **Bottlenecks removed (2026-11-09T21:14:26Z): NONE blocking start.** Competing handoffs/TODOs: none. Deps OK. C4 artifact/impl/tests present. Known constraints (not excuses): historical L2/intrabar replay not publicly available — do not fabricate; exchange credentials/testnet keys are not assumed — record honestly; build against public/testnet/paper modes with explicit capability detection and fail-closed order submission.

**Campaign #5 target (execute now): Production bridge — paper trading/testnet path, OMS primitives, risk dashboard (MEDIUM→HIGH)**
1. **OMS/primitives (code, fail-closed):** Add production-oriented primitives (e.g. `execution/oms.py`, `execution/paper_broker.py`, `execution/risk.py`, and/or `utils/oms.py`/`utils/risk_dashboard.py` — choose idiomatic paths consistent with repo) covering: order intents (market/limit where feasible), idempotency/client-order IDs, position/cash accounting, fee/slippage model hooks, cancel/replace semantics where supported, and strict validation (no negative/NaN/oversized orders, no fill fabrication).
2. **Paper trading/testnet path (honest):** Implement a paper broker that consumes real/public market data (or recorded real candles with provenance) and simulates fills **only as paper/simulated** with explicit `simulated_fills: true`, never claimed as real exchange fills. If Binance testnet/public WS/REST access is feasible without secrets, support a clearly-labeled testnet/public-data mode with provenance; if blocked/missing credentials, fail closed and record `blocked_routes`.
3. **Risk dashboard / controls:** Pre-trade and runtime risk checks: max notional/position, gross/net exposure, per-symbol concentration, turnover/cost budget, drawdown/kill-switch, stale-data/data-gap guard, and fail-closed behavior on missing inputs. Emit a machine-readable risk state/report.
4. **Integration:** Wire at least one real-data strategy path (prefer Campaign #4 MTF pairs or C1-C3 validated components, honest) into the paper OMS runner: `examples/run_paper_trading_live.py` (or equivalent) that runs a bounded paper session from real data/provenance and emits artifacts.
5. **Required artifacts (honest schema):**
   - `reports/paper_trading_session.json` (or equivalent) with at minimum: `real_data_only` (for market data inputs), `fabricated_data` (false for market data; paper fills explicitly labeled), `simulated_fills` (true/false, honest), `generated_at_utc`, `campaign` (`Campaign #5 - Production bridge`), `status` (`ok`/`partial`/`blocked`), `blocked_routes`, `environment` (paper/testnet/public-data; no secrets), `data_sources`/provenance, `oms_config`, `risk_config`/risk events, `orders`/`fills` (paper, labeled), `positions`/`pnl_summary` (paper, labeled), `limitations`, `notes`.
   - `reports/risk_dashboard.json` (or embedded equivalent) with current/terminal risk state and any breaches/actions.
6. **Tests (all required):**
   - OMS/order validation/idempotency/accounting tests.
   - Risk guard tests (fail-closed, kill-switch, stale data, limits).
   - Paper fill labeling/provenance tests — **paper fills must never be marked as real exchange fills**.
   - Runner smoke/integration test using real cached/fetched public data or clearly-flagged test fixtures (never presented as real evidence).
7. **Quality gates before declaring C5 complete (rerun after changes):**
   ```bash
   cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
   PYTHONPATH=. python -m pytest tests/ -q
   python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
   python -m mypy backtest/ strategies/ utils/
   ```
   Fix regressions caused by your changes. Record outcomes truthfully.
8. **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified truth (timestamp, artifact paths/status, gate results, honest blocked routes/limitations, next focus). Keep this file the **single durable handoff**.

**This directive remains active until** `reports/paper_trading_session.json` and `reports/risk_dashboard.json` (or honest equivalents) exist with honest schema/provenance **and** Campaign #5 implementation/tests/gates are materially complete. Then advance to the follow-on.

## 1) Verified state (2026-11-09T21:14:26Z)

- **Deps**: numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy importable.
- **Gates (fresh full baseline):** `945 passed, 1 skipped, 0 failures`; `ruff` all passed; `mypy` success (35 source files). **Rerun after any source change.**
- **Real data**: Binance public spot klines work via loader/cache; 451/blocked routes handled honestly. **5m fetch verified (26208 rows, 11 symbols, 2026-08-01→2026-10-30).** 1h cache available (2026-04-01→2026-10-30). Never fabricate.
- **Artifacts (C1-C4):** `reports/funding_carry_real.json` ok/true/false; `reports/execution_lob_real.json` partial/true/false (historical L2 replay infeasible); `reports/regime_adaptive_sweep.json` present; `reports/ml_gated_pairs.json` ok/true/false; `reports/pairs_mtf_5m_1h.json` ok/true/false (C4, 14 pairs, negative mean Sharpe reported honestly).
- **Bottlenecks:** **NONE** blocking Campaign #5 start.
- **Gates re-verified (2026-11-09T21:14:26Z):** `945 passed, 1 skipped, 0 failures`; `ruff` all passed; `mypy` success (35 source files). Baseline unchanged.

## 1.1) Parallel-track caution
`research_state/state.yaml` (locked C104-C248, `next_campaign: C249`, `oos_edge_proven: false`) is a separate locked line. **Do not** work C249/registry/status instead of Campaign #5 unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest (held-out proxy 0.473 < 0.65; best OOS mean return 0.0). |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (ok, 2296 real rows). `reports/execution_lob_real.json` (partial; snapshots ok; historical L2 replay infeasible; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (ok, real-data-only, 544 labeled rows, cv_ok). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, tests, runner. |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json` (ok,true,false), `utils/mtf_pairs.py`, `examples/run_pairs_mtf_5m_1h_real.py`, `tests/test_pairs_mtf.py`. 14 pairs evaluated; base cost sensitivity 8 ok; negative mean Sharpe reported honestly — no profitable edge claimed. |
| #5 Production bridge (paper/testnet OMS + risk) | **NOT STARTED / REQUIRED NEXT** | Execute §0 immediately. |

## 3) Next focus campaign — Production bridge (HIGH after C4)
Execute immediately. See §0. Deliver paper OMS/risk primitives, tests, and honest `reports/paper_trading_session.json` + `reports/risk_dashboard.json`. Real/public market data only; paper/testnet fills explicitly labeled/simulated; no fabricated exchange evidence.

## 4) Follow-on campaign (only after Campaign #5 complete + artifacts exist)
**Live/testnet execution validation (MEDIUM)** — If credentials/testnet access become available, run bounded testnet order lifecycle with honest provenance; otherwise extend paper OMS with richer microstructure/latency realism and operator runbooks (still no fabricated fills).

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract
- Start with Campaign #5 immediately. Do not redo #1-#4 unless fixing a concrete defect.
- Produce real/public-data artifacts with provenance. Paper fills must be explicitly simulated/labeled. If blocked, record exact `blocked_routes`/rationale — do not fabricate.
- At material checkpoint/completion, update **only** `HANDOFF.md` with verified truth. Keep it the single durable handoff.
