# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo: `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Campaigns #1–#7 COMPLETE (honest/bounded/paper where stated). Competing handoff/TODO/NEXT/plan docs at repo root: **NONE** (re-verified 2026-11-10T10:46Z, only `HANDOFF.md`). **No fabrication. Ever.**
> **Separate locked line — DO NOT WORK/MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Unrelated to Campaign #8 and must not block it.
> **BOTTLENECK STATUS (2026-11-10T10:46Z):** No env/data/credential blockers in-workspace. `c7-venv`, cached real spot/volume data, baseline gates, and ops examples are ready. **Only remaining blocker to progress is missing Campaign #8 primary deliverable** — you must remove it by creating code+artifact+tests this session.

## 0) TIMESTAMPED INITIAL TASK MESSAGE (SINGLE DURABLE DIRECTIVE FOR NEXT SESSION)

**[2026-11-10T10:46:11Z | DURABLE INITIAL TASK (REFRESHED) | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`]**

**NON-NEGOTIABLE FIRST ACTION:** in this session, **create `examples/run_campaign8_edge_robustness.py` and execute it to produce a timestamped `reports/campaign8_edge_robustness_<UTC>.json` from cached real data only** (no refetch, no fabrication). Do this before any other non-trivial work. Status-only updates, re-planning, or re-reading without producing this artifact/test/code progress is failure.

**YOUR FIRST SUBSTANTIVE ACTIONS THIS SESSION MUST PRODUCE CODE/TESTS/ARTIFACTS AND PASSING VERIFICATION** (not reading, not planning, not status-only narration). Begin implementation immediately.

**MISSION (repo-priority, evidence-first):** Answer with reproducible real-data evidence: **under which real-data cost/regime/window/enriched-gate conditions (if any) do pairs/portfolio strategies show positive OOS net after costs vs buy-and-hold, and how do enriched gates and portfolio risk controls affect that result?** Negative or insufficient findings are valid only if honest, reproducible, fully evidenced, and never fabricated. Negative/insufficient outcomes do **not** excuse skipping heavy implementation, tests, or artifact generation.

### BOTTLENECKS CLEARED / READY STATE (re-verified 2026-11-10T10:35Z)

- **Env ready:** `/home/runner/work/_temp/kilo-tmp/c7-venv` with deps present (numpy/pandas/scipy/pydantic/aiohttp/pytest 9.2.0, ruff 0.17.4, mypy available in env/tooling). Use `PYTHONPATH` = repo root.
- **Cached real data available (SHA256-verified, do not refetch/fabricate):**
  - `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (spot, 12 symbols ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP, hourly 2026-04-01..2026-10-30) with `.meta.json`
  - `data/cache/volume_1h_full.pkl` + `.meta.json` + `.provenance.json` (hashes recorded in `research_state/state.yaml`)
- **Key real artifacts present:** `reports/pairs_real_market.json`, `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`
- **Baseline gates (re-verified 2026-11-10T10:35Z, c7-venv):** `pytest tests/ -q` => **1064 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7-focused ruff => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
- **Ops examples (re-verified 2026-11-10T10:35Z):** `examples/run_reconciliation_audit.py` => `reports/reconciliation_audit.json` overall status **pass**; `examples/run_operator_deployment_readiness.py` => `reports/operator_deployment_readiness.json` overall status **pass**. No regressions.
- **Known non-blockers here:** `research_state/workflow_run_diagnostics.jsonl` shows external workflow failures (missing numpy / invalid tool args in CI loops) — irrelevant in this workspace when using `c7-venv`. No exchange/testnet credentials; no public historical L2/intrabar replay. **If blocked, emit honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale; never fabricate data/fills/order books/labels/metrics/exchange responses.**

### ACTIVE CAMPAIGN #8 — STAT-ARB EDGE HARDENING & HONEST REAL-DATA EXTENSION (MANDATORY)

**Constraints:** Do NOT redo Campaigns #1–#7 unless fixing a concrete defect with evidence. Do NOT touch `research_state/state.yaml` or the locked RQA C104–C249 line. Do NOT defer with status-only updates.

**Baseline evidence to extend (real, do not hand-wave):**
- `reports/pairs_real_market.json` (real Binance spot, BTC/ETH,ETH/SOL,BTC/SOL, 5064 bars 2026-04-01..2026-10-28, wf train=500/test=100/n_splits=4 rolling, fee=0.001 slip=0.0005, diagnostics from `reports/portfolio_real.json`): **OOS mean return 0.0 and replay total_return 0.0 for all 3 pairs** (enriched gates fail-closed, 0 trades) vs B&H +15.50%/+17.60%/+21.59%. `real_data_only: true`, `fabricated_data: false`.
- `reports/portfolio_real.json` (real-only, 14 pairs/12 symbols, 1h/4h/1d wf>=12, risk controls per_pair_cap/corr/CVaR/gross/drawdown circuit breaker, volume-aware execution, cost-stress, regime/tail): e.g. BTC/ETH Engle-Granger p=0.52 (fail) while Johansen rank=2 (pass) — strict fail-closed dominates. `real_data_only: true`, `fabricated_data: false`.
- `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`: existing cost/regime stress (extend with provenance checks, do not blindly trust).

#### REQUIRED HEAVY WORK (COMPLETE IN PRIORITY ORDER — NO EXCEPTIONS)

1. **Reproducible real-data OOS/cost/regime robustness artifact (PRIMARY, HIGHEST PRIORITY):**
   - Create `examples/run_campaign8_edge_robustness.py` and produce a timestamped JSON report in `reports/` (e.g. `reports/campaign8_edge_robustness_<UTC>.json`).
   - Use cached real loaders/data only. Extend analysis for BTC/ETH, ETH/SOL, BTC/SOL and portfolio configs/risk controls consistent with `reports/portfolio_real.json` (`max_gross_exposure=1.4`, `per_pair_cap=0.32`, `correlation_exposure_cap=0.5`, `CVaR_cap=0.25`, `drawdown_circuit_breaker=-10%`).
   - Include: full provenance (`real_data_only`, `fabricated_data`, data sources/cache refs, timestamps, hashes where applicable), walk-forward/OOS windows and splits, fee×slippage grid, regime slices, buy-and-hold benchmarks, enriched gate pass/fail and trade accounting, and clear honest findings (edge/no-edge/insufficient + why). **Do not claim edge without evidence.**

2. **Strengthen stat-arb risk/diagnostic tests (evidence-driven):**
   - Add/tighten tests in `tests/` for: fail-closed enriched gate behavior and cached-vs-uncached parity/structural-break hard-block (`strategies/pairs_trading.py`: `_evaluate_enriched_gates_strict`, `generate_signals`), hedge-ratio/weight sanity (positive clip [1e-6,1e6], opposing legs, abs-market-value normalization), portfolio risk controls (`examples/run_portfolio_real.py:PortfolioRiskController.apply` gross/per-pair/correlation/CVaR/circuit breaker), and cost/provenance honesty invariants (cf. `tests/test_cost_sensitivity_real.py`). Deterministic real/small fixtures only.

3. **Reconciliation/ops hardening follow-through:**
   - Keep C7 `config/`, `observability/`, `playbooks/`, `reconciliation/` correct; fix any regressions. Verify `examples/run_operator_deployment_readiness.py` and `examples/run_reconciliation_audit.py` run successfully and record outcomes.

4. **GATES (MUST PASS BEFORE COMPLETION/UPDATE):**
   - `$PT tests/ -q`
   - `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`
   - `$PY -m ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py`
   - `$PY -m mypy backtest/ strategies/ utils/`
   - Record exact outcomes and any failures with evidence.

#### IMMEDIATE BOOTSTRAP COMMANDS (RUN FIRST — NO EXCEPTIONS)

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### SESSION COMPLETION CONTRACT (NON-NEGOTIABLE)

- **NOT COMPLETE** until Campaign #8 produces verified real-data artifacts/tests/code improvements with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (edge/no-edge/blocked), and the next unambiguous heavy directive (C9 or remaining evidenced C8 blockers). **No status-only completion. No deferral.**

---

## 1) VERIFIED STATE SNAPSHOT

- **Repo:** `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats` (`main`, git). Single durable handoff: `HANDOFF.md` only.
- **Baseline gates (2026-11-10T09:38:12Z, c7-venv):** pytest 1064 passed, 1 skipped; ruff (main + C7 scopes) all passed; mypy 36 files success.
- **C7 modules present:** `config/`, `observability/`, `playbooks/`, `reconciliation/` with examples/tests; previously lint-cleaned, no intended behavior change.
- **Real data (cached, verified):** 12 symbols hourly spot 2026-04-01..2026-10-30 + full 1h quote-volume series; see `research_state/state.yaml` cache SHA256s and `reports/portfolio_real.json`.
- **Locked/separate track:** `research_state/state.yaml` RQA C104–C248/C249 preselected, `oos_edge_proven: false` — do not modify.

## 2) CAMPAIGN OUTCOMES SUMMARY

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

### SESSION 2026-11-10T10:35Z — VERIFIED OUTCOMES (this checkpoint)

- **Gates re-verified (all green):** `pytest tests/ -q` => 1064 passed, 1 skipped; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => All checks passed; C7 ruff scope => All checks passed; `mypy backtest/ strategies/ utils/` => Success (36 source files).
- **Ops examples re-verified:** `examples/run_reconciliation_audit.py` => `reports/reconciliation_audit.json` status `pass`; `examples/run_operator_deployment_readiness.py` => `reports/operator_deployment_readiness.json` status `pass`. No regressions in C7 `config/`, `observability/`, `playbooks/`, `reconciliation/`.
- **Campaign #8 status: NOT YET STARTED.** `examples/run_campaign8_edge_robustness.py` does NOT exist; no `reports/campaign8_*.json` artifact exists. This is the single remaining bottleneck: the primary heavy-work item (§0.1) has zero code, zero tests, zero artifact. Nothing blocks it — env, cached real data, baseline gates, and all supporting examples (`run_pairs_multi.py`, `run_cost_sensitivity_real.py`, `run_cost_sensitivity_real_portfolio.py`, `run_portfolio_real.py`) are present and green.
- **No fabrication risk identified:** all existing artifacts (`pairs_real_market.json`, `portfolio_real.json`, `cost_sensitivity_real*.json`, `regime_cost_stress_extended.json`) carry `real_data_only: true`, `fabricated_data: false`, `blocked_routes`, and `rationale`. The cached-vs-uncached parity and structural-break hard-block are enforced in `strategies/pairs_trading.py:_evaluate_enriched_gates_strict`.
- **Next unambiguous heavy directive:** implement Campaign #8 item 1 (`examples/run_campaign8_edge_robustness.py` + timestamped `reports/campaign8_edge_robustness_<UTC>.json`) using ONLY cached real loaders/data, then items 2 (evidence-driven stat-arb risk/diagnostic tests in `tests/`) and 3 (ops follow-through, already verified this session — re-run only if code changes). Then re-run all four gates and record exact outcomes.

## 3) REPRODUCTION / GATE COMMANDS

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

## 4) KEY FILES FOR CAMPAIGN #8

- **Examples/analysis:** `examples/run_pairs_multi.py`, `examples/run_portfolio_real.py`, `examples/run_cost_sensitivity_real.py`, `examples/run_cost_sensitivity_real_portfolio.py`
- **Core strategy/gates:** `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, `_evaluate_enriched_gates_strict`, `generate_signals`, hedge-ratio clipping [1e-6,1e6], opposing legs, abs-market-value normalization)
- **Portfolio/risk:** `examples/run_portfolio_real.py` (`PortfolioRiskController.apply` gross/per-pair/correlation/CVaR/circuit breaker), `backtest/engine.py` (`run_portfolio`)
- **Tests:** `tests/test_pairs_real_market.py`, `tests/test_cost_sensitivity_real.py`, `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_reconciliation.py`, `tests/test_config.py`, `tests/test_observability.py`, `tests/test_playbooks.py`
- **Key reports (real, honest):** `reports/pairs_real_market.json` (0 trades/gates blocked), `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`

---

**END OF DURABLE HANDOFF — NEXT AGENT MUST START WITH §0 BOOTSTRAP AND PRODUCE HEAVY WORK IMMEDIATELY. SINGLE REMAINING BOTTLENECK: Campaign #8 item 1 has zero code/artifact — create `examples/run_campaign8_edge_robustness.py` and its timestamped `reports/campaign8_edge_robustness_<UTC>.json` artifact first, then items 2 and 3, then re-run all four gates.**