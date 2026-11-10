# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-10T12:40Z; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid; status-only work is not.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Must not block Campaign #9.

## 0) TIMESTAMPED INITIAL TASK MESSAGE (MANDATORY FIRST ACTION)

**[2026-11-10T12:40:45Z | DURABLE INITIAL TASK | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`, bootstrap verified]**

**NON-NEGOTIABLE FIRST SUBSTANTIVE ACTION (before any other non-trivial work):**
1. Create `examples/run_campaign9_causal_gate_edge_search.py`.
2. Run it with `c7-venv` and produce `reports/campaign9_causal_gate_edge_search_<UTC>.json` from **cached real data only** (no refetch, no synthetic/fabricated inputs).
3. The artifact must include real-data provenance (cache paths/hashes/meta), WF/OOS splits, fee×slippage grid, regime slices, B&H benchmarks, **causal/per-bar enriched-gate** pass/fail/trade/exposure accounting, and explicit conclusion `edge` / `no_edge` / `insufficient_or_blocked`.

Creating this code+artifact is the definition of progress. Re-planning, re-reading, or status-only updates without it is failure. **Campaigns #1–#8 are COMPLETE** — do not redo them except evidence-backed defect fixes. **Campaign #9 is ACTIVE and not started.**

### MISSION (evidence-first, repo-priority)

Determine with reproducible real-data evidence whether any cost-aware OOS net edge exists for BTC/ETH, ETH/SOL, BTC/SOL and portfolio slices consistent with `reports/portfolio_real.json` when enriched gates are evaluated **causally/per-bar on trailing windows** (not via static aggregate fail-closed shortcut), and how causal per-bar gates affect trade/exposure accounting vs Campaign #8 `no_edge` baseline. Negative/insufficient findings are valid only if honest, reproducible, fully evidenced, and never fabricated.

### BOTTLENECKS CLEARED / READY STATE (2026-11-10T12:40Z)

- **Env ready:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (`python`, `pytest` present; numpy/pandas/scipy/pydantic/aiohttp/pytest/ruff/mypy available per prior verification). Use `PYTHONPATH=$PWD`.
- **Cached real data (SHA256-verified, do not refetch/fabricate):** spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars) and volume `data/cache/volume_1h_full.pkl` + `.meta.json` + `.provenance.json` — hashes recorded in `research_state/state.yaml`.
- **No in-workspace env/data/credential blockers.** No exchange/testnet creds and no public historical L2/intrabar replay; if genuinely blocked, emit honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale — never fabricate.
- **Ops artifacts pass:** `reports/reconciliation_audit.json`, `reports/operator_deployment_readiness.json`.

#### IMMEDIATE BOOTSTRAP

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### SESSION COMPLETION CONTRACT (NON-NEGOTIABLE)

- **NOT COMPLETE** until Campaign #9 produces verified real-data artifacts/tests/code improvements with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

## 1) VERIFIED BASELINE SNAPSHOT

- **Repo state:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#8:** COMPLETE (honest/evidence-first). C8 conclusion `no_edge` (fail-closed enriched gates on tested cached-real BTC/ETH,ETH/SOL,BTC/SOL + portfolio slices/costs/windows).
- **Campaign #9:** ACTIVE — **NOT STARTED** (`examples/run_campaign9_causal_gate_edge_search.py` and `reports/campaign9_causal_gate_edge_search_*.json` absent).
- **Baseline gates (C8, 2026-11-10T12:00Z, c7-venv):** `pytest tests/ -q` => **1070 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7-focused ruff => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
- **Key real artifacts:** `reports/campaign8_edge_robustness_20261110T115802Z.json` (SHA256 `5064aea1688751d063b01349743ef8d3997299bced107f91217c1b35b3c95d42`, cached-real, `no_edge`), `reports/pairs_real_market.json` (BTC/ETH,ETH/SOL,BTC/SOL 0 trades/OOS mean 0/replay 0; B&H +15.50%/+17.60%/+21.59%), `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`.
- **C7 modules:** `config/`, `observability/`, `playbooks/`, `reconciliation/` with examples/tests; ops artifacts pass.

## 2) CAMPAIGN OUTCOMES (REFERENCE)

| Campaign | State | Notes / key artifacts |
|---|---|---|
| #1 Regime-adaptive signal generation | COMPLETE | `reports/regime_adaptive_sweep.json` |
| #2 Funding/basis-carry + LOB/intrabar feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py` |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py` |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json` |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json` |
| #7 Operator deployment hardening | COMPLETE | config/observability/playbooks/reconciliation + artifacts; gates green |
| #8 Stat-arb edge hardening & honest real-data extension | COMPLETE (`no_edge`) | `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py` |
| **#9 Enriched-gate causal/per-bar edge discovery & robustness** | **ACTIVE — NOT STARTED** | Execute §0/§3 now |

## 3) ACTIVE CAMPAIGN #9 — REQUIRED HEAVY WORK (NO DEFERRAL)

**Objective:** Close the causal-vs-cached enriched-gate evidence gap and determine if any reproducible, cost-aware OOS net edge exists for BTC/ETH, ETH/SOL, BTC/SOL or portfolio configs when gates are evaluated **causally/per-bar on trailing windows** (not via static aggregate fail-closed shortcut), while preserving fail-closed safety for unassessable/missing/failed gates and structural breaks.

**Constraints:** No network refetch, no synthetic/fabricated data/labels/metrics/fills/IV/volume. Do not weaken gate thresholds to manufacture trades/edge. Do not touch `research_state/state.yaml` RQA C104–C249 line. Do not redo Campaigns #1–#8 except evidence-backed defect fixes.

1. **Causal enriched-gate parity implementation + evidence (deliver first):** implement/adjust strategy path so cached diagnostics are not misused as causal per-bar passes and per-bar trailing diagnostics (interval-cached/causal) are the enforceable path for signal generation where feasible; document behavior. Produce `examples/run_campaign9_causal_gate_edge_search.py` and timestamped `reports/campaign9_causal_gate_edge_search_<UTC>.json` with real-data-only provenance (cache hashes/meta), WF/OOS splits, fee×slippage grid, regime slices, B&H benchmarks, per-bar gate pass/fail/trade/exposure accounting, and explicit conclusion `edge`/`no_edge`/`insufficient_or_blocked`.
2. **Deterministic tests:** add/tighten tests proving causal/per-bar gate enforcement parity and fail-closed behavior for missing/unassessable/failed gates and structural breaks on cached-real subsets (avoid synthetic; if unavoidable, flag explicitly).
3. **Gates:** pass `$PT tests/ -q`, `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, C7 ruff scope, `$PY -m mypy backtest/ strategies/ utils/` and record exact outcomes.
4. **Handoff update:** update only `HANDOFF.md` with verified UTC, commands, artifact paths+SHA256, gate outcomes, concrete findings, and next unambiguous heavy directive (Campaign #10 or evidenced blockers).

## 4) REPRODUCTION / GATE COMMANDS

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

## 5) KEY FILES

- **C8 baseline:** `examples/run_campaign8_edge_robustness.py`, `tests/test_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`
- **C9 deliverables (required):** `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_<UTC>.json`, deterministic causal-gate parity tests
- **Strategy/gates:** `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, `_evaluate_enriched_gates_strict`, `generate_signals`)
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`
- **Key real reports:** `reports/pairs_real_market.json`, `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`

---

**END OF DURABLE HANDOFF — START WITH §0 BOOTSTRAP, THEN EXECUTE CAMPAIGN #9 ITEM 1 (CODE + TIMESTAMPED CACHED-REAL ARTIFACT) IMMEDIATELY. NO STATUS-ONLY WORK.**
