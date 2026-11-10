# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaigns #1-#7 COMPLETE (honest/bounded/paper where stated). Campaign #7 COMPLETE (2026-11-10): lint cleanup + gates verified in-session.** Competing handoff/TODO/plan docs at repo root: **NONE** (only `HANDOFF.md`). **No fabrication.** `research_state/state.yaml` (locked RQA line C104-C248, `next_campaign: C249`, `oos_edge_proven: false`) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-10T07:41:07Z | VERIFIED NOW | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`. C7 ruff blockers cleared (E501/formatting fixes across C7 modules, C7-focused examples/tests, and `examples/run_reconciliation_audit.py`) with no intended behavior changes. Gates verified in-session with project deps + dev tools in `/home/runner/work/_temp/kilo-tmp/c7-venv` (and ruff in `/home/runner/work/_temp/kilo-home/.local/bin`): `python -m pytest tests/ -q` => **1064 passed, 1 skipped, 4042 warnings in 59.24s**; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7-focused ruff scope (`config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py`) => **All checks passed**; `python -m mypy backtest/ strategies/ utils/` => **Success: no issues found in 36 source files**. Environment note: system Python lacks deps/tools; install/use a venv with project+dev deps (`pydantic`, `aiohttp`, `pytest-asyncio` required for C7 tests). No exchange/testnet credentials, no public historical L2/intrabar replay available; never fabricate. **EXPLICIT DIRECTIONS ABSENT => CONTINUE HEAVY WORK: execute Campaign #8 below.**]**

**NEXT AGENTIC SESSION: CAMPAIGN #8 — STAT-ARB EDGE HARDENING & HONEST REAL-DATA EXTENSION (HEAVY WORK, NON-OPTIONAL).**
- **First substantive actions MUST produce code/tests/artifacts and passing verification**, not just reading/planning/status.
- **Do NOT redo Campaigns #1-#7** unless you find and fix a concrete defect with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248 RQA line.
- **No fabrication. Ever.** Use only real, fetchable/verifiable public data with full provenance (`real_data_only`, `fabricated_data`, sources/routes, timestamps, hashes/checksums where applicable). If blocked, emit honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale — never invent fills, order books, labels, metrics, or exchange responses.
- **Campaign #8 required work (prioritized by repo purpose: crypto quant stat-arb strategies):**
  1. **Out-of-sample/cost robustness extension on real Binance spot data:** Implement and run a reproducible real-data analysis (new script in `examples/` + JSON artifact in `reports/`) that extends cost/fee-slippage stress and/or regime-window comparison for the **top stat-arb pairs (BTC/ETH, ETH/SOL, BTC/SOL from `reports/pairs_real_market.json`; 14 pairs from `reports/portfolio_real.json`)** and **portfolio configs (`reports/portfolio_real.json` risk controls: max_gross_exposure=1.4, per_pair_cap=0.32, correlation_exposure_cap=0.5, CVaR_cap=0.25, drawdown_circuit_breaker=-10%)** using existing real loaders/cached data only (`data/cache/` has 12 symbols hourly 2026-04-01 to 2026-10-30). Include provenance, benchmarks (buy-and-hold), and clear pass/fail/honest findings. Do not claim edge where evidence is negative or insufficient. **Key finding to extend:** `pairs_real_market.json` shows 0 trades for all 3 pairs (cointegration gate blocked everything); `portfolio_real.json` shows BTC/EG Engle-Granger p=0.52 (fail), Johansen rank=2 (pass) — gates fail-closed. Extend analysis to answer: under what cost/regime windows (if any) does any pair/portfolio show positive OOS net after costs?
  2. **Strengthen pair/portfolio risk & diagnostics tests:** Add or tighten tests in `tests/` for:
     - Enriched cointegration gate fail-closed behavior (cached vs uncached parity, structural break hard-block, missing-gate blocks under strict mode) — see `strategies/pairs_trading.py:_evaluate_enriched_gates_strict` and `generate_signals` lines 290-420
     - Hedge-ratio/weight sanity (positivity >1e-18, clip [1e-6,1e6], opposing legs never same-direction) — see `strategies/pairs_trading.py` lines 226-240, 472-495
     - Portfolio risk controls (gross exposure cap, per-pair cap, correlation dampening, CVaR cap, drawdown circuit breaker) — see `examples/run_portfolio_real.py:PortfolioRiskController.apply` lines 109-222
     - Cost-sensitivity provenance honesty (real_data_only, fabricated_data, blocked_routes, rationale) — see `tests/test_cost_sensitivity_real.py`
     Use real/small deterministic fixtures only (no fabricated "market" claims). Cover gaps revealed by analysis in #1.
  3. **Reconciliation/ops hardening follow-through:** Ensure C7 observability (`observability/`), reconciliation (`reconciliation/`), playbook (`playbooks/`) paths remain correct under new tests; fix any regressions found. Run `examples/run_operator_deployment_readiness.py` and `examples/run_reconciliation_audit.py` to verify.
  4. **Verification:** Run and pass relevant/impacted tests plus full gates before handoff update:
     - `pytest tests/ -q`
     - `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`
     - `ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py`
     - `mypy backtest/ strategies/ utils/`
     Record exact outcomes (counts, timings, any failures with evidence).
- **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified timestamp, commands run, artifact paths/hashes if created, and the next unambiguous heavy directive.

**This directive remains active until** Campaign #8 produces verified real-data artifacts/tests/code improvements with gates green (or every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials).

## 1) Verified state (2026-11-10T07:41:07Z)

- **Repo:** `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats` (git repo, `main`).
- **Single durable handoff:** `HANDOFF.md` only at root.
- **C7 modules present:** `config/`, `observability/`, `playbooks/`, `reconciliation/` (+ examples/tests).
- **C7 lint/test fixes applied this session (no intended behavior change):** E501/line-wrap cleanup in `config/env.py`, `config/schemas.py`, `observability/health.py`, `observability/logging.py`, `observability/metrics.py`, `playbooks/__init__.py`, `playbooks/dry_run.py`, `playbooks/incident.py`, `playbooks/state.py`, `reconciliation/fill_audit.py`, `reconciliation/lifecycle_audit.py`, `examples/run_operator_deployment_readiness.py`, `examples/run_reconciliation_audit.py`, `tests/test_observability.py`, `tests/test_playbooks.py`.
- **Quality gates (verified 2026-11-10T07:35:00Z, c7-venv):**
  - `pytest tests/ -q` => **1064 passed, 1 skipped, 4042 warnings in 59.24s**
  - `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**
  - C7-focused ruff scope => **All checks passed**
  - `mypy backtest/ strategies/ utils/` => **Success: no issues found in 36 source files**
- **Env/tooling:** created `/home/runner/work/_temp/kilo-tmp/c7-venv` and installed project deps + dev deps including `pydantic`, `aiohttp`, `pytest-asyncio` (required for C7 config/observability/async playbook tests). Ruff also installed to `/home/runner/work/_temp/kilo-home/.local/bin`.
- **Real data available (cached, verified SHA256 in `research_state/state.yaml`):**
  - Spot: 12 symbols (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP) hourly 2026-04-01 to 2026-10-30 (~123k bars each)
  - Quote volume: full 1h series for all 12 symbols (`data/cache/volume_1h_full.pkl`)
  - Portfolio universe: 14 pairs across 12 symbols (see `reports/portfolio_real.json`)
  - Top pairs from prior campaigns: BTC/ETH, ETH/SOL, BTC/SOL (see `reports/pairs_real_market.json`)
- **Constraints:** no exchange/testnet credentials; no public historical L2/intrabar replay; never fabricate data/fills/order books/labels/metrics/exchange responses. `research_state/state.yaml` RQA line (C104-C248 locked, C249 preselected, `oos_edge_proven: false`) is separate — do not modify/work unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest. |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required. |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`. |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py`. |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper, honest) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json`. |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json`. |
| #7 Operator deployment hardening | **COMPLETE (2026-11-10, verified)** | Config/observability/playbooks/reconciliation modules and artifacts present; lint cleaned; tests/mypy/ruff green in-session. |
| #8 Stat-arb edge hardening & honest real-data extension | **NOT STARTED (next, heavy)** | See §0 directive. |

## 3) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
# use env with project + dev deps (pydantic, aiohttp, pytest-asyncio, ruff, mypy, pytest)
# example (this session): /home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats

python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m ruff check config/ observability/ playbooks/ reconciliation/ \
  examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py \
  tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py
python -m mypy backtest/ strategies/ utils/
```

## 4) Key files for Campaign #8 work

**Analysis scripts to extend/model after:**
- `examples/run_pairs_multi.py` — multi-pair walk-forward + replay
- `examples/run_portfolio_real.py` — portfolio construction with risk controls, cost-stress, regime-conditioned
- `examples/run_cost_sensitivity_real.py` — fee×slippage grid on pairs
- `examples/run_cost_sensitivity_real_portfolio.py` — fee×slippage grid on portfolio

**Core strategy (enriched gates, fail-closed):**
- `strategies/pairs_trading.py` — `CointegrationPairsStrategy` with `_evaluate_enriched_gates_strict`, cached vs uncached parity, hedge ratio clipping, opposing legs

**Tests to strengthen:**
- `tests/test_pairs_real_market.py` — cointegration gate, hedge ratio, opposing legs, real-data smoke, multi-pair orchestration
- `tests/test_cost_sensitivity_real.py` — provenance honesty (real_data_only, blocked_routes, rationale)
- `tests/test_portfolio_real.py` / `tests/test_portfolio_real_hardened.py` — portfolio risk controls, walk-forward, bootstrap CI
- `tests/test_reconciliation.py` — fill audit, lifecycle audit

**Reports to extend (cost/regime stress):**
- `reports/pairs_real_market.json` — 3 pairs, walk-forward, replay, benchmark (shows 0 trades, gates blocked)
- `reports/portfolio_real.json` — 14 pairs, 12 symbols, risk controls, parameter stability, tail risk, cost-stress, volume-aware execution
- `reports/cost_sensitivity_real.json` — ETH/SOL fee×slippage grid
- `reports/cost_sensitivity_real_portfolio.json` — portfolio fee×slippage grid
- `reports/regime_cost_stress_extended.json` — regime/cost slices across wider universe

## 5) Handoff contract

- Continue with heavy implementation: C8 real-data artifacts/analysis, tests, and any needed code hardening; keep gates green; no behavior regressions; no fabrication.
- Do not redo #1-#7 unless fixing a concrete defect. Do not touch locked C104-C248/state RQA line.
- Update **only** `HANDOFF.md` at next material checkpoint/completion with verified truth.

(End of file)