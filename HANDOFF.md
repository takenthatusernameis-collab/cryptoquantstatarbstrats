# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo purpose (name-inferred): `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Campaigns #1-#7 COMPLETE (honest/bounded/paper where stated). Competing handoff/TODO/plan docs at repo root: **NONE** (verified 2026-11-10T08:49:52Z, only `HANDOFF.md`). **No fabrication. Ever.**
> **Separate locked line — DO NOT WORK/MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (C104-C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Unrelated to Campaign #8 and must not block it.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-10T09:38:12Z | DURABLE INITIAL TASK | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main` | last verified baseline 2026-11-10T09:38:12Z in `/home/runner/work/_temp/kilo-tmp/c7-venv` with `PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH`: `pytest tests/ -q` => 1064 passed, 1 skipped, 4032 warnings in 58.90s; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => All checks passed; C7-focused `ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py` => All checks passed; `mypy backtest/ strategies/ utils/` => Success (36 source files).]**

**Bottlenecks cleared for immediate progress (verified 2026-11-10T08:49:52Z):**
- Env ready: `/home/runner/work/_temp/kilo-tmp/c7-venv` with project+dev deps present (`numpy`, `pandas`, `scipy`, `pydantic`, `aiohttp`, `pytest 9.2.0`, `ruff 0.17.4` in PATH, `mypy`); `PYTHONPATH` must be repo root.
- Cached real data available (SHA256-verified per `research_state/state.yaml`): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (spot, 12 symbols ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP, hourly 2026-04-01..2026-10-30, ~123k bars), `volume_1h_full.pkl` + meta/provenance. 14-pair universe and diagnostics in `reports/portfolio_real.json`.
- Known workflow diagnostics (`research_state/workflow_run_diagnostics.jsonl`, recent runs 2026-11-08..10) show external loop failures (e.g. missing numpy / invalid tool args) — **not a blocker in this workspace** when using `c7-venv`.
- Constraints: no exchange/testnet credentials; no public historical L2/intrabar replay. **Never fabricate data/fills/order books/labels/metrics/exchange responses.** If blocked, emit honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale.

### ACTIVE CAMPAIGN #8 — STAT-ARB EDGE HARDENING & HONEST REAL-DATA EXTENSION (HEAVY, MANDATORY, NON-DEFERRABLE)

**FIRST substantive actions this session MUST produce code/tests/artifacts and passing verification** (not reading, not planning, not status). Start implementing/running immediately.

**Repo-priority focus (name-inferred):** crypto quant stat-arb strategies. Answer with evidence, not narrative: **under which real-data cost/regime/window/gate conditions (if any) do pairs/portfolio show positive OOS net after costs vs buy-and-hold, and what do enriched gates/risk controls do to that result?** Negative/insufficient findings are valid only if honest, reproducible, and fully evidenced.

**Key baseline evidence to extend (real, do not hand-wave):**
- `reports/pairs_real_market.json` (2026-11-05, real Binance spot, BTC/ETH,ETH/SOL,BTC/SOL, 5064 bars 2026-04-01..2026-10-28, wf train=500/test=100/n_splits=4 rolling, fee=0.001 slip=0.0005, diagnostics from `reports/portfolio_real.json`): **OOS mean return 0.0 and replay total_return 0.0 for all 3 pairs** (enriched gates fail-closed, 0 trades), benchmarks +15.50%/+17.60%/+21.59%. `real_data_only: true`, `fabricated_data: false`.
- `reports/portfolio_real.json` (real-only, 14 pairs/12 symbols, 1h/4h/1d wf>=12, risk controls per_pair_cap/correlation/CVaR/gross/drawdown circuit breaker, volume-aware execution, cost-stress, regime-conditioned/tail risk): e.g. BTC/ETH Engle-Granger p=0.52 (fail) while Johansen rank=2 (pass) — strict fail-closed dominates. `real_data_only: true`, `fabricated_data: false`.
- `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`: existing cost/regime stress artifacts (extend, do not blindly trust without provenance checks).

**Do NOT:** redo Campaigns #1-#7 unless fixing a concrete defect with evidence; touch `research_state/state.yaml` or locked RQA C104-C249 line; fabricate anything; defer with status-only updates.

#### Required heavy work (complete in priority order)

1. **Reproducible real-data OOS/cost/regime robustness artifact (primary):**
   - Add `examples/run_campaign8_edge_robustness.py` (or equivalent) + timestamped JSON report in `reports/` (e.g. `reports/campaign8_edge_robustness_<UTC>.json`).
   - Using cached real loaders/data only, extend analysis for top pairs (BTC/ETH, ETH/SOL, BTC/SOL) and portfolio configs/risk controls consistent with `reports/portfolio_real.json` (`max_gross_exposure=1.4`, `per_pair_cap=0.32`, `correlation_exposure_cap=0.5`, `CVaR_cap=0.25`, `drawdown_circuit_breaker=-10%`).
   - Include: full provenance (`real_data_only`, `fabricated_data`, data sources/cache refs, timestamps, hashes where applicable), walk-forward/OOS windows, fee×slippage grid, regime slices and buy-and-hold benchmarks, enriched gate pass/fail/trade accounting, and clear honest findings (edge/no-edge/insufficient + why). Do not claim edge without evidence.
2. **Strengthen stat-arb risk/diagnostic tests (evidence-driven):**
   - Add/tighten tests in `tests/` for: fail-closed enriched gate behavior and cached-vs-uncached parity/structural-break hard-block (`strategies/pairs_trading.py` `_evaluate_enriched_gates_strict`, `generate_signals`), hedge-ratio/weight sanity (positive clip [1e-6,1e6], opposing legs, abs-market-value normalization), portfolio risk controls (`examples/run_portfolio_real.py:PortfolioRiskController.apply` gross/per-pair/correlation/CVaR/circuit breaker), and cost/provenance honesty invariants (`tests/test_cost_sensitivity_real.py` style). Deterministic real/small fixtures only.
3. **Reconciliation/ops hardening follow-through:** keep C7 `config/`, `observability/`, `playbooks/`, `reconciliation/` correct; fix any regressions. Verify `examples/run_operator_deployment_readiness.py` and `examples/run_reconciliation_audit.py` run successfully (record outcomes).
4. **Gates (must pass before completion/update):**
   - `pytest tests/ -q`
   - `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`
   - `ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py`
   - `mypy backtest/ strategies/ utils/`
   - Record exact outcomes and any failures with evidence.

#### Immediate bootstrap commands (run first, then execute #1-#4)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### Session completion contract
- **Not complete** until Campaign #8 produces verified real-data artifacts/tests/code improvements with gates green, **or** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials.
- Update **only** `HANDOFF.md` at material checkpoint/completion with: verified timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (edge/no-edge/blocked), and the next unambiguous heavy directive (C9 or remaining evidenced C8 blockers). No status-only completion. No deferral.

## 1) Verified state snapshot (2026-11-10T09:38:12Z)

- **Repo:** `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats` (`main`, git). Single durable handoff: `HANDOFF.md` only.
- **Baseline gates (last full run 2026-11-10T09:38:12Z, c7-venv):** pytest 1064 passed, 1 skipped; ruff (main scopes + C7 scope) all passed; mypy 36 files success.
- **C7 modules present:** `config/`, `observability/`, `playbooks/`, `reconciliation/` with examples/tests; lint cleaned (E501) in prior session, no intended behavior change.
- **Real data (cached, verified):** 12 symbols hourly spot 2026-04-01..2026-10-30 + full 1h quote-volume series; see `research_state/state.yaml` cache SHA256s and `reports/portfolio_real.json`.
- **Locked/separate track:** `research_state/state.yaml` RQA C104-C248/C249 preselected, `oos_edge_proven: false` — do not modify.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-adaptive signal generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py` |
| #2 Funding/basis-carry + LOB/intrabar feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py` |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py` |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json` |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json` |
| #7 Operator deployment hardening | COMPLETE (verified 2026-11-10) | config/observability/playbooks/reconciliation + artifacts; gates green |
| **#8 Stat-arb edge hardening & honest real-data extension** | **ACTIVE — NEXT HEAVY WORK** | See §0; produce real-data artifacts/tests/code + gates |

## 3) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m ruff check config/ observability/ playbooks/ reconciliation/ \
  examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py \
  tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py
$PY -m mypy backtest/ strategies/ utils/
```

## 4) Key files for Campaign #8

- **Examples/analysis:** `examples/run_pairs_multi.py`, `examples/run_portfolio_real.py`, `examples/run_cost_sensitivity_real.py`, `examples/run_cost_sensitivity_real_portfolio.py`
- **Core strategy/gates:** `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, `_evaluate_enriched_gates_strict`, fail-closed enriched gates, hedge-ratio clipping/opposing legs)
- **Portfolio/risk:** `examples/run_portfolio_real.py` (`PortfolioRiskController.apply`), `backtest/engine.py` (`run_portfolio`)
- **Tests:** `tests/test_pairs_real_market.py`, `tests/test_cost_sensitivity_real.py`, `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_reconciliation.py`, `tests/test_config.py`, `tests/test_observability.py`, `tests/test_playbooks.py`
- **Key reports (real, honest):** `reports/pairs_real_market.json` (0 trades/gates blocked, all 3 pairs), `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`

(End of durable handoff)
