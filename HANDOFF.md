# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo: `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Campaigns #1–#7 COMPLETE (honest/bounded/paper where stated). Competing handoff/TODO/NEXT/plan docs at repo root: **NONE** (re-verified 2026-11-10T11:33Z, only `HANDOFF.md`; historical handoff-named JSON/scripts in `reports/` and `scripts/` are artifacts, not competing directives). **No fabrication. Ever.**
> **Separate locked line — DO NOT WORK/MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Unrelated to Campaign #8 and must not block it.
> **BOTTLENECK STATUS (2026-11-10T11:33Z):** No in-workspace env/data/credential blockers. `c7-venv` present, cached real spot/volume data present, baseline state per prior verified run, ops examples previously passing. External CI/workflow log failures in `research_state/workflow_run_diagnostics.jsonl` are **not blockers here** — use `c7-venv`. **The only remaining blocker to meaningful progress is the missing Campaign #8 primary deliverable; remove it by creating code + artifact + tests and passing gates this session.**

## 0) TIMESTAMPED INITIAL TASK MESSAGE (SINGLE DURABLE DIRECTIVE FOR NEXT SESSION)

**[2026-11-10T11:33:58Z | DURABLE INITIAL TASK | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`]**

**NON-NEGOTIABLE FIRST SUBSTANTIVE ACTION (do before any other non-trivial work):** create `examples/run_campaign8_edge_robustness.py` and execute it with `c7-venv` to produce a timestamped `reports/campaign8_edge_robustness_<UTC>.json` generated from **cached real data only** (no refetch, no synthetic/fabricated prices/IV/volume/fills/order books/labels/metrics). Status-only updates, re-planning, or re-reading without producing this code+artifact is **failure**.

**MISSION (repo-priority, evidence-first):** Determine with reproducible real-data evidence **under which real-data cost, regime, window, and enriched-gate conditions (if any) do pairs/portfolio strategies show positive OOS net after costs vs buy-and-hold, and how do enriched gates and portfolio risk controls affect that result?** Negative or insufficient findings are valid **only** if honest, reproducible, fully evidenced, and never fabricated. Negative/insufficient outcomes do **not** excuse skipping heavy implementation, tests, or artifact generation.

### BOTTLENECKS CLEARED / READY STATE (re-verified 2026-11-10T11:31Z)

- **Env ready:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (numpy/pandas/scipy/pydantic/aiohttp/pytest 9.2.0, ruff 0.17.4, mypy available). Use `PYTHONPATH` = repo root.
- **Cached real data (SHA256-verified, do not refetch/fabricate):**
  - Spot cache: `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (11 symbols: ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; hourly 2026-04-01..2026-10-30 UTC; 5112 bars) — hashes recorded in `research_state/state.yaml`.
  - Volume: `data/cache/volume_1h_full.pkl` + `.meta.json` + `.provenance.json` (hashes in `research_state/state.yaml`).
- **Key real baseline artifacts:** `reports/pairs_real_market.json` (BTC/ETH,ETH/SOL,BTC/SOL, 5064 bars, wf train=500/test=100/n_splits=4 rolling, fee=0.001 slip=0.0005: **0 trades, OOS mean 0, replay total 0** for all 3; B&H +15.50%/+17.60%/+21.59%; fail-closed enriched gates), `reports/portfolio_real.json` (14 pairs/12 symbols, risk controls gross=1.4/per-pair=0.32/corr=0.5/CVaR=0.25/DD breaker=-10%), `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json` — all real-data-only, no fabrication.
- **Baseline gates (re-verified 2026-11-10T11:31Z, c7-venv):** `pytest tests/ -q` => **1064 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7-focused ruff => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
- **Ops examples (re-verified 2026-11-10T11:31Z):** `examples/run_reconciliation_audit.py` => `reports/reconciliation_audit.json` **pass**; `examples/run_operator_deployment_readiness.py` => `reports/operator_deployment_readiness.json` **pass**.
- **Known non-blockers:** no exchange/testnet creds, no public historical L2/intrabar replay. If genuinely blocked, emit honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale; **never fabricate**.

### ACTIVE CAMPAIGN #8 — STAT-ARB EDGE HARDENING & HONEST REAL-DATA EXTENSION (MANDATORY)

**Constraints:** Do NOT redo Campaigns #1–#7 unless fixing a concrete defect with evidence. Do NOT touch `research_state/state.yaml` or the locked RQA C104–C249 line. Do NOT defer with status-only updates.

#### REQUIRED HEAVY WORK (COMPLETE IN PRIORITY ORDER — NO EXCEPTIONS)

1. **Reproducible real-data OOS/cost/regime robustness artifact (PRIMARY):**
   - Implement `examples/run_campaign8_edge_robustness.py` and run it to produce `reports/campaign8_edge_robustness_<UTC>.json` (timestamped).
   - **Data:** cached real loaders/data only (`data/cache/*` / loader cache path). Cover BTC/ETH, ETH/SOL, BTC/SOL and portfolio configs/risk controls consistent with `reports/portfolio_real.json` (`max_gross_exposure=1.4`, `per_pair_cap=0.32`, `max_correlation_exposure=0.5`, `max_cvar_allocation=0.25`, `drawdown_circuit_breaker=-0.10`) and walk-forward/OOS splits.
   - **Report must include:** `real_data_only: true`, `fabricated_data: false`, full provenance (sources/cache refs, timestamps, SHA256 hashes where applicable), symbols/pairs/windows/freq/splits, fee×slippage grid and OOS net per slice, regime slices, buy-and-hold benchmarks, enriched gate pass/fail and trade/exposure accounting, portfolio/risk-control outcomes, and an explicit honest conclusion (`edge` / `no_edge` / `insufficient_or_blocked` + why). **No edge claim without evidence.**
2. **Strengthen stat-arb risk/diagnostic tests (evidence-driven):**
   - Add/tighten deterministic `tests/` for: fail-closed enriched gate behavior and cached-vs-uncached/structural-break hard-block parity (`strategies/pairs_trading.py`: `_evaluate_enriched_gates_strict`, `generate_signals`), hedge-ratio/weight sanity (positive clip [1e-6,1e6], opposing legs, abs-market-value normalization), portfolio risk controls (`examples/run_portfolio_real.py:PortfolioRiskController.apply` gross/per-pair/correlation/CVaR/circuit breaker), and cost/provenance honesty invariants (cf. `tests/test_cost_sensitivity_real.py`).
3. **Reconciliation/ops hardening follow-through:**
   - Keep `config/`, `observability/`, `playbooks/`, `reconciliation/` correct; fix any regressions. Re-run `examples/run_operator_deployment_readiness.py` and `examples/run_reconciliation_audit.py` if code changes and record outcomes.
4. **GATES (MUST PASS BEFORE COMPLETION/UPDATE):**
   - `$PT tests/ -q`
   - `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`
   - `$PY -m ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py`
   - `$PY -m mypy backtest/ strategies/ utils/`
   - Record exact outcomes and any failures with evidence.

#### IMMEDIATE BOOTSTRAP COMMANDS

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
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (edge/no-edge/blocked), and the next unambiguous heavy directive (Campaign #9 or remaining evidenced C8 blockers). **No status-only completion. No deferral.**

---

## 1) VERIFIED STATE SNAPSHOT

- **Repo:** `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats` (`main`). Single durable handoff: `HANDOFF.md` only.
- **Baseline gates (2026-11-10T11:31Z, c7-venv):** pytest 1064 passed, 1 skipped; ruff (main + C7 scopes) all passed; mypy 36 files success.
- **C7 modules:** `config/`, `observability/`, `playbooks/`, `reconciliation/` with examples/tests; ops artifacts pass.
- **Real data (cached, verified):** 11-symbol hourly spot 2026-04-01..2026-10-30 + full 1h quote-volume series; see `research_state/state.yaml` cache SHA256s and `reports/portfolio_real.json`.
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
| **#8 Stat-arb edge hardening & honest real-data extension** | **ACTIVE — NEXT HEAVY WORK** | §0: produce `examples/run_campaign8_edge_robustness.py` + timestamped `reports/campaign8_edge_robustness_<UTC>.json` from cached real data, tests, gates |

### SESSION 2026-11-10T11:31Z — VERIFIED OUTCOMES (baseline checkpoint)

- Gates green (pytest 1064/1 skipped, ruff main+C7 clean, mypy 36 files success).
- Ops examples pass (`reconciliation_audit.json`, `operator_deployment_readiness.json`).
- **Campaign #8 not started:** `examples/run_campaign8_edge_robustness.py` and `reports/campaign8_edge_robustness_<UTC>.json` do not exist. This is the only remaining bottleneck; all prerequisites are ready.

### SESSION 2026-11-10T11:33Z — HANDOFF REFRESH (no competing directives)

- Re-verified: `HANDOFF.md` is the only competing handoff/TODO/NEXT/plan doc at repo root; `c7-venv` present; C8 deliverable still absent. No env/data/credential bottlenecks identified in-workspace. **Next agent must execute §0 immediately and produce Campaign #8 item 1 (code + timestamped real-data artifact) before any status-only work.**

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
- **Core strategy/gates:** `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, `_evaluate_enriched_gates_strict`, `generate_signals`)
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`
- **Tests:** `tests/test_pairs_real_market.py`, `tests/test_cost_sensitivity_real.py`, `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_reconciliation.py`, C7 tests
- **Key real reports:** `reports/pairs_real_market.json` (0 trades/fail-closed), `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`

---

**END OF DURABLE HANDOFF — NEXT AGENT MUST START WITH §0 BOOTSTRAP, THEN IMMEDIATELY PRODUCE CAMPAIGN #8 ITEM 1 CODE+ARTIFACT, THEN ITEMS 2–4.**