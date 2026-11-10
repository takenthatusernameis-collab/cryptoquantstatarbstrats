# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-10T15:46:14Z; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid; status-only work is not.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). This is a separate research line and must not be edited to block/replace C7–C10 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-10T16:10:00Z UTC)

**MANDATORY FIRST ACTION (non-optional, heavy work):** Execute **Campaign #11 — Rolling-Stability Blocker Diagnosis & Gate-Pass Feasibility on the Wider Universe**. Status-only work is forbidden. Do not redo Campaigns #1–#10 except evidence-backed defect fixes.

**Naming collision cleared:** Campaign #11 deliverables for this handoff line are exactly: `examples/run_campaign11_rolling_stability_blocker.py`, timestamped `reports/campaign11_rolling_stability_blocker_<UTC>.json`, and deterministic tests (e.g. `tests/test_campaign11_rolling_stability_blocker.py`). Do not confuse with any pre-existing numbered artifacts.

**Objective:** On cached real data only, determine whether the `rolling_stable_ok` trailing-window insufficiency is the sole structural blocker (no bar passes all enriched gates on any wider-universe pair under unmodified thresholds) or whether any pair/slice ever achieves a causal per-bar gate pass, across trailing sample lengths and check intervals, **without weakening gate thresholds**. If no bar ever passes, confirm `no_edge` is structural and the cached-real/gate research line is exhausted; if some bar passes, evaluate cost-aware OOS net edge vs buy-and-hold for those slices.

**Minimum deliverables (all required unless concretely blocked with evidence):**
1. `examples/run_campaign11_rolling_stability_blocker.py` implementing causal per-bar enriched-gate evaluation over >=10 wider-universe pairs from cached real spot cache only, sweeping trailing-window/check-interval configurations (gates themselves unmodified), recording per-bar gate pass/fail/trade/exposure accounting.
2. Timestamped `reports/campaign11_rolling_stability_blocker_<UTC>.json` with: real-data-only provenance (cache paths + SHA256/meta hashes), per-pair and aggregate per-bar gate accounting, which gate blocks on what share of bars (emphasis `rolling_stable_ok`), cost-aware OOS/replay vs buy-and-hold only for slices where gates pass, explicit `edge`/`no_edge`/`insufficient_or_blocked` conclusion with evidence.
3. Deterministic tests validating causal per-bar fail-closed behavior, per-bar accounting recorded, artifact/provenance honesty, and that no gate threshold was weakened relative to `strategies/pairs_trading.py` / `utils/cointegration.py`.
4. Gates green: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/` (record exact outcomes).
5. Update **only** `HANDOFF.md` at checkpoint/completion with verified UTC, commands, artifact path(s)+SHA256, gate outcomes, concrete findings, and next unambiguous heavy directive.

**Constraints (non-negotiable):** No network refetch; no synthetic/fabricated data/labels/metrics/fills/IV/volume. Do not weaken gate thresholds to manufacture trades/edge. Do not modify `research_state/state.yaml` RQA line. Honest `no_edge`/`insufficient_or_blocked` with full evidence is valid only if produced via the above heavy work.

**Ready state:** env `/home/runner/work/_temp/kilo-tmp/c7-venv` (`PYTHONPATH=$PWD`), cached real spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`+`.meta.json` (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars) and volume cache present — do not refetch. C10 baseline: `pytest` 1078 passed/1 skipped, ruff clean, mypy 36 files clean.

## 0) TIMESTAMPED INITIAL TASK MESSAGE (MANDATORY FIRST ACTION)

**[2026-11-10T16:10:00Z | DURABLE INITIAL TASK | `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main`, bootstrap verified]** — **START CAMPAIGN #11 NOW.**

**SUBSTANTIVE ACTION REQUIRED (all deliverables must be produced):**
1. Create `examples/run_campaign11_rolling_stability_blocker.py` (pattern from C10 `run_campaign10_wider_universe_causal_gates.py`, gate logic unmodified).
2. Run it with `c7-venv`; produce `reports/campaign11_rolling_stability_blocker_<UTC>.json` (SHA256) from **cached real data only** (no refetch, no synthetic/fabricated inputs).
3. Add deterministic tests `tests/test_campaign11_rolling_stability_blocker.py` (causal per-bar gate breakdown recorded + fail-closed; artifact provenance honesty; no gate-threshold weakening).
4. Verify gates: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/`.
5. Update **only** `HANDOFF.md` with verified UTC, commands, artifact path(s)+SHA256, gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and next unambiguous heavy directive.

Creating this code+artifact is the definition of progress. **Campaigns #1–#10 are COMPLETE** — do not redo them except evidence-backed defect fixes. **Campaign #11 is ACTIVE — EXECUTE NOW.**

### MISSION (evidence-first, repo-priority)

Determine with reproducible real-data evidence whether any cost-aware OOS net edge exists for the wider universe (>=10 pairs from `reports/portfolio_real.json`) and portfolio slices when enriched gates are evaluated **causally/per-bar on trailing windows** (not via static aggregate fail-closed shortcut), and how causal per-bar gates affect trade/exposure accounting vs Campaign #9 `no_edge` baseline. Negative/insufficient findings are valid only if honest, reproducible, fully evidenced, and never fabricated.

### BOTTLENECKS CLEARED / READY STATE (2026-11-10T15:49Z)

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

- **NOT COMPLETE** until Campaign #10 produces verified real-data artifacts/tests/code improvements with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

## 1) VERIFIED BASELINE SNAPSHOT

- **Repo state:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#8:** COMPLETE (honest/evidence-first). C8 conclusion `no_edge` (fail-closed enriched gates on tested cached-real BTC/ETH,ETH/SOL,BTC/SOL + portfolio slices/costs/windows).
- **Campaign #9:** COMPLETE — `examples/run_campaign9_causal_gate_edge_search.py` + `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865e...ad43b0`) produced; deterministic tests added; gates green; conclusion `no_edge` (causal per-bar gates fail-closed on 100% of bars; dominant blocker `rolling_stable_ok` fails all bars due to 720-bar rolling-stability window insufficiency).
- **Campaign #10:** COMPLETE — `examples/run_campaign10_wider_universe_causal_gates.py` + `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json` (SHA256 `8c3c5d5785c0d7bd33c805f939528771809494dba400e6f990d269dd3369b895`) produced over the full 17-pair `reports/portfolio_real.json` wider universe (ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC, BTC/ETH, ETH/SOL, BTC/SOL) on cached real data only; deterministic tests added; gates green; conclusion `insufficient_or_blocked` (zero trades on every pair under causal per-bar gates; fail_rate 1.0 / `rolling_stable_ok` fails 5112/5112 bars on every pair; no positive OOS net edge vs buy-and-hold; replay 0.0 cash merely exceeds *negative* buy-and-hold on down-market pairs — not an edge; gate thresholds not weakened).
- **Campaign #11:** ACTIVE — NOT YET EXECUTED (rolling-stability blocker diagnosis & gate-pass feasibility).
- **Baseline gates (2026-11-10T16:10Z, c7-venv):** `pytest tests/ -q` => **1078 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
- **Key real artifacts:** `reports/campaign8_edge_robustness_20261110T115802Z.json` (SHA256 `5064aea1...c95d42`, cached-real, `no_edge`), `reports/pairs_real_market.json` (BTC/ETH,ETH/SOL,BTC/SOL 0 trades/OOS mean 0/replay 0; B&H +15.50%/+17.60%/+21.59%), `reports/portfolio_real.json`, `reports/cost_sensitivity_real.json`, `reports/cost_sensitivity_real_portfolio.json`, `reports/regime_cost_stress_extended.json`.
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
| **#10 Wider-universe causal per-bar gate validation** | **COMPLETE** | `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json` (SHA256 `8c3c5d5785c0d7bd33c805f939528771809494dba400e6f990d269dd3369b895`), `tests/test_campaign10_wider_universe_causal_gates.py`; conclusion `insufficient_or_blocked` |
| **#11 Rolling-stability blocker diagnosis & gate-pass feasibility** | **ACTIVE — NOT YET EXECUTED** | **Deliverables: `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_<UTC>.json`, `tests/test_campaign11_rolling_stability_blocker.py`** |

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

## 3b) CAMPAIGN #10 — EXECUTION RECORD (COMPLETE)

**Timestamped handoff directive (2026-11-10T15:49:19Z UTC):** Execute Campaign #10 now — wider-universe causal per-bar gate validation on cached real data only. (see §0 for full scope/deliverables/constraints).

**Done (all five items):**
1. **Wider-universe causal per-bar implementation + evidence:** `examples/run_campaign10_wider_universe_causal_gates.py` exercises both causal per-bar and cached-aggregate fail-closed paths over all 17 `reports/portfolio_real.json` pairs on cached real spot (5112 bars, 1h, 2026-04-01..2026-10-30), with WF/OOS (train=500/test=100, 4 splits, rolling), fee×slippage grid, per-bar gate pass/fail/trade/exposure accounting, B&H benchmarks, path comparison vs C9 baseline, explicit conclusion. Produced `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json`.
2. **Deterministic tests:** `tests/test_campaign10_wider_universe_causal_gates.py` — cached-symbols coverage; causal per-bar gate breakdown recorded + fail-closed on real subset; cached-vs-causal parity fail-closed; artifact provenance honesty (>=10 pairs present).
3. **Gates:** `pytest tests/ -q` => **1078 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
4. **Handoff update:** this section + §0/§1/§2 (verified UTC, commands, artifact path+SHA256, gate outcomes, concrete findings, next directive below).
5. **No network refetch, no synthetic/fabricated inputs, gate thresholds not weakened, `research_state/state.yaml` RQA line untouched.**

**Concrete findings (honest, reproducible, never fabricated):**
- **Conclusion: `insufficient_or_blocked`** (edge_claim: false). Across all 17 cached-real-data wider-universe pairs and the portfolio slice, walk-forward OOS cost slices and replay cost slices under causal per-bar enriched gates (with cached-aggregate fail-closed reference) show no positive OOS net edge vs buy-and-hold. Every pair: zero trades, zero exposure under all cost slices, fail_rate 1.0, `rolling_stable_ok` fails 5112/5112 bars. Replay returns 0.0 (cash) which merely exceeds *negative* buy-and-hold on down-market pairs (e.g. ADA/ETH -7.01%, ADA/BTC -3.48%, DOT/BTC -4.57%, DOT/ETH -8.09%) — cash avoiding losses is not a reproducible edge.
- **Structural blocker confirmed:** `rolling_stable_ok` (720-bar rolling-stability window) is insufficient on every trailing sample across every pair; gate thresholds were not weakened to manufacture trades/edge.
- **Cached-aggregate and causal-per-bar paths agree** (both fail-closed), consistent with Campaign #9.

## 3c) CAMPAIGN #11 — ACTIVE DIRECTIVE (START HERE; NOT YET EXECUTED)

**Timestamped handoff directive (2026-11-10T16:10:00Z UTC):** Execute Campaign #11 now — rolling-stability blocker diagnosis & gate-pass feasibility on the wider universe (see §0 for full scope/deliverables/constraints).

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

**END OF DURABLE HANDOFF — CAMPAIGN #10 COMPLETE (`insufficient_or_blocked`, gates green: 1078 passed/1 skipped). NEXT SESSION STARTS WITH CAMPAIGN #11 ROLLING-STABILITY BLOCKER DIAGNOSIS & GATE-PASS FEASIBILITY (§0/§3c directive). NO STATUS-ONLY WORK.**