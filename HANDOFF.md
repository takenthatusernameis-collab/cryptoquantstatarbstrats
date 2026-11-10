# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-10T15:46:14Z; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid; status-only work is not.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). This is a separate research line and must not be edited to block/replace C7–C10 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-10T15:46:14Z UTC)

**MANDATORY FIRST ACTION (non-optional, heavy work):** Execute **Campaign #10 — Wider-Universe Causal Per-Bar Gate Validation**. Status-only work is forbidden. Do not redo Campaigns #1–#9.

**Naming collision cleared:** `scripts/generate_campaign10_artifacts.py` (RQA-era paper-bridge artifacts) and `examples/run_pairs_real_wider_universe*.py`/`reports/pairs_real_market_wider_universe.json` are **different, pre-existing artifacts** — do not confuse or overwrite. C10 deliverables for this handoff line are exactly: `examples/run_campaign10_wider_universe_causal_gates.py`, timestamped `reports/campaign10_wider_universe_causal_gates_<UTC>.json`, and deterministic tests (e.g. `tests/test_campaign10_wider_universe_causal_gates.py`).

**Objective:** On cached real data only, replicate causal per-bar enriched-gate evaluation across the wider `reports/portfolio_real.json` universe (>=10 pairs from: ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC, plus baseline BTC/ETH, ETH/SOL, BTC/SOL as applicable) and determine whether the `rolling_stable_ok` trailing-window insufficiency is a structural blocker or whether any pair/portfolio slice yields reproducible cost-aware OOS net edge vs buy-and-hold **without weakening gate thresholds**.

**Minimum deliverables (all required unless concretely blocked with evidence):**
1. `examples/run_campaign10_wider_universe_causal_gates.py` implementing causal per-bar trailing enriched-gate evaluation (reuse/follow C9 `examples/run_campaign9_causal_gate_edge_search.py` semantics) over >=10 wider-universe pairs from cached real spot cache only.
2. Timestamped `reports/campaign10_wider_universe_causal_gates_<UTC>.json` with: real-data-only provenance (cache paths + SHA256/meta hashes), WF/OOS splits, fee×slippage grid, per-pair and aggregate per-bar gate pass/fail/trade/exposure accounting, B&H benchmarks, path comparison where relevant, and explicit `edge`/`no_edge`/`insufficient_or_blocked` conclusion with evidence.
3. Deterministic tests validating causal per-bar fail-closed behavior, per-bar accounting recorded, and artifact/provenance honesty on real-data subsets/no-fabrication invariants.
4. Gates green: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/` (record exact outcomes).
5. Update **only** `HANDOFF.md` at checkpoint/completion with verified UTC, commands, artifact path(s)+SHA256, gate outcomes, concrete findings, and next unambiguous heavy directive.

**Constraints (non-negotiable):** No network refetch; no synthetic/fabricated data/labels/metrics/fills/IV/volume. Do not weaken gate thresholds to manufacture trades/edge. Do not modify `research_state/state.yaml` RQA line. Honest `no_edge`/`insufficient_or_blocked` with full evidence is valid only if produced via the above heavy work.

**Ready state:** env `/home/runner/work/_temp/kilo-tmp/c7-venv` (`PYTHONPATH=$PWD`), cached real spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`+`.meta.json` (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars) and volume cache present — do not refetch. C9 baseline: 1074 passed/1 skipped, ruff clean, mypy 36 files clean.

## 0) TIMESTAMPED INITIAL TASK MESSAGE (MANDATORY FIRST ACTION)

**[2026-11-10T12:40:45Z | DURABLE INITIAL TASK | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`, bootstrap verified]** — **EXECUTED & COMPLETE 2026-11-10T12:50:28Z**.

**SUBSTANTIVE ACTION DONE (all three deliverables produced):**
1. Created `examples/run_campaign9_causal_gate_edge_search.py`.
2. Ran it with `c7-venv`; produced `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`) from **cached real data only** (no refetch, no synthetic/fabricated inputs).
3. Added deterministic tests `tests/test_campaign9_causal_gate_edge_search.py` (causal per-bar gate breakdown recorded + fail-closed; cached-vs-causal parity fail-closed; artifact provenance honesty).

Artifact includes real-data provenance (cache paths/hashes/meta), WF/OOS splits, fee×slippage grid, regime slices, B&H benchmarks, causal per-bar gate pass/fail/trade/exposure accounting, cached-aggregate reference path, path comparison vs Campaign #8 baseline, and explicit conclusion.

Creating this code+artifact is the definition of progress. **Campaigns #1–#8 are COMPLETE** — do not redo them except evidence-backed defect fixes. **Campaign #9 is COMPLETE.**

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
- **Campaign #9:** COMPLETE — `examples/run_campaign9_causal_gate_edge_search.py` + `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865e...ad43b0`) produced; deterministic tests added; gates green.
- **Baseline gates (C9, 2026-11-10T12:50Z, c7-venv):** `pytest tests/ -q` => **1074 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7-focused ruff => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
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
| **#9 Enriched-gate causal/per-bar edge discovery & robustness** | **COMPLETE** | `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`), `tests/test_campaign9_causal_gate_edge_search.py`; conclusion `no_edge` |

## 3) CAMPAIGN #9 — EXECUTION RECORD (COMPLETE)

**Objective:** Close the causal-vs-cached enriched-gate evidence gap and determine if any reproducible, cost-aware OOS net edge exists for BTC/ETH, ETH/SOL, BTC/SOL or portfolio configs when gates are evaluated **causally/per-bar on trailing windows** (not via static aggregate fail-closed shortcut), while preserving fail-closed safety for unassessable/missing/failed gates and structural breaks.

**Constraints honored:** No network refetch, no synthetic/fabricated data/labels/metrics/fills/IV/volume. Did not weaken gate thresholds to manufacture trades/edge. Did not touch `research_state/state.yaml` RQA C104–C249 line. Did not redo Campaigns #1–#8.

**Done (all four items):**
1. **Causal enriched-gate implementation + evidence:** `examples/run_campaign9_causal_gate_edge_search.py` exercises both paths per pair: (a) cached-aggregate fail-closed (Campaign #8 reference) and (b) causal per-bar trailing diagnostics recomputed every `cointegration_check_interval` bars, forward-filled, fail-closed under strict. Produced timestamped `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` with real-data-only provenance (cache hashes/meta), WF/OOS splits (train=500/test=100, 4 splits, rolling), fee×slippage grid, regime slices, B&H benchmarks, per-bar gate pass/fail/trade/exposure accounting, path comparison vs C8 baseline, explicit conclusion.
2. **Deterministic tests:** `tests/test_campaign9_causal_gate_edge_search.py` — causal per-bar gate breakdown recorded + fail-closed (no exposure) on real subset; cached-vs-causal parity fail-closed; artifact provenance honesty; portfolio risk controller controls.
3. **Gates:** `pytest tests/ -q` => **1074 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; C7 ruff scope => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
4. **Handoff update:** this section (verified UTC, commands, artifact path+SHA256, gate outcomes, concrete findings, next directive below).

**Concrete findings (honest, reproducible, never fabricated):**
- **Conclusion: `no_edge`** (edge_claim: false). Across tested cached-real-data pairs/portfolio, walk-forward OOS cost slices and replay cost slices under causal per-bar enriched gates (with cached-aggregate fail-closed reference), no positive OOS net edge and no replay outperformance vs buy-and-hold were observed under stated costs/windows. Buy-and-hold benchmark +11.66% (portfolio); strategy returns 0.0% on all cost slices for all pairs.
- **Causal per-bar gates fail-closed on 100% of bars** for all three pairs (pass_rate 0.0, fail_rate 1.0, 5112 bars each). Dominant blocker: `rolling_stable_ok` fails all bars (720-bar rolling-stability window is insufficient on trailing samples); `leg_stationarity_ok` 4872/5112, `eg_pass` 4752/5112, `johansen_pass` 3912/5112, `spread_mr_pass` 3839/5112, `no_structural_break` 1799/5112 fail. Zero trades, zero exposure under all cost slices.
- **Cached-aggregate and causal-per-bar paths agree** (`no_edge` both), closing the causal-vs-cached evidence gap from Campaign #8.

## 3b) CAMPAIGN #10 — ACTIVE DIRECTIVE (START HERE; NOT YET EXECUTED)

**Timestamped handoff directive (2026-11-10T15:46:14Z UTC):** Execute Campaign #10 now — wider-universe causal per-bar gate validation on cached real data only. This is the required heavy-work continuation (see §0 for full scope/deliverables/constraints).

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
- **C9 deliverables (complete):** `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`), `tests/test_campaign9_causal_gate_edge_search.py`; conclusion `no_edge`.
- **C10 deliverables (ACTIVE — not yet executed):** `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_<UTC>.json`, deterministic tests (e.g. `tests/test_campaign10_wider_universe_causal_gates.py`); conclusion must be evidence-backed `edge`/`no_edge`/`insufficient_or_blocked`. (Do not confuse with unrelated `scripts/generate_campaign10_artifacts.py` RQA-era artifact generator or `reports/pairs_real_market_wider_universe.json`.)
- **Strategy/gates:** `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, `_evaluate_enriched_gates_strict`, `generate_signals`)
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`
- **Key real reports:** `reports/pairs_real_market.json`, `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`

---

**END OF DURABLE HANDOFF — CAMPAIGN #9 COMPLETE (`no_edge`, gates green). NEXT SESSION STARTS WITH CAMPAIGN #10 WIDER-UNIVERSE CAUSAL PER-BAR GATE VALIDATION (§3 directive). NO STATUS-ONLY WORK.**
