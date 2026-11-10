# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (verified 2026-11-10T17:05:10Z; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid; status-only work is not.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). This is a separate research line and must not be edited to block/replace C1–C11 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-10T17:05:10Z UTC)

**STATE:** Campaigns #1–#11 COMPLETE on the cached-real enriched-gate line. Campaign #11 (rolling-stability blocker diagnosis & gate-pass feasibility) is executed and evidenced: conclusion `no_edge` (`edge_claim: false`), **no bar passes all enriched gates on any wider-universe pair under any swept trailing config with thresholds unmodified**. `rolling_stable_ok` blocks **5112/5112 bars on every pair** across sweeps (structural blocker confirmed); cached-aggregate and causal-per-bar paths agree (fail-closed). Cost-aware OOS/replay edge evaluation was infeasible because zero gate-pass slices exist. **Cached-real/gate research line is exhausted** under current gate schema/thresholds without fabricating data/trades/edge.

**MANDATORY HEAVY ACTION (do not do status-only work):** Only proceed if you can produce **new, real-data, evidence-backed progress** without weakening gate thresholds and without fabrication/refetch. Prioritize in order:
1. **New real cached data / materially different window or asset coverage** already present locally (search `data/cache/`, `reports/` for additional real spot/volume caches not yet evaluated on this gate line) — if found, run a timestamped causal per-bar campaign (script + `reports/campaign12_*_<UTC>.json` + deterministic tests) and report honest `edge`/`no_edge`/`insufficient_or_blocked`.
2. **Orthogonal, real-data-only strategy research** in-repo (not re-running C1–C11) that does not rely on weakening enriched pair gates to manufacture trades (e.g. evidence-backed use of existing real artifacts/modules with strict provenance) — produce code + timestamped artifact + tests.
3. **If (1)-(2) are concretely impossible with available local real data/assets:** record an evidence-backed `insufficient_or_blocked` closeout note in this handoff (what was searched, why blocked, no refetch/credentials/synthetic) and stop; do **not** invent work, do **not** weaken thresholds, do **not** modify `research_state/state.yaml`.

Do not redo Campaigns #1–#11 except evidence-backed defect fixes. Any continuation must create new timestamped deliverables and keep gates green.

### READY STATE (verified context)

- **Env:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (python/pytest/ruff/mypy). Use `PYTHONPATH=$PWD`.
- **Cached real spot (do not refetch):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (SHA256 `56075733...f5f8c9b` / `d03556ba...d2d80d`; ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars). Volume cache present.
- **No exchange/testnet creds and no public historical L2/intrabar replay.** Honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale only — never fabricate.

#### BOOTSTRAP

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### SESSION COMPLETION CONTRACT (NON-NEGOTIABLE)

- **NOT COMPLETE** until you produce verified real-data artifacts/tests/code with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials/threshold-weakening.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

## 1) VERIFIED BASELINE SNAPSHOT (2026-11-10T17:05:10Z)

- **Repo:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#11:** COMPLETE (honest/evidence-first). C11 confirms structural blocker on cached-real enriched-gate line.
- **Gates (C11 recorded):** `pytest tests/ -q` => **1080 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => passed on touched scope (new files clean) at checkpoint; `mypy backtest/ strategies/ utils/` => **Success (36 source files)**.
- **RQA locked (separate, untouched):** `research_state/state.yaml` C104–C248, `next_campaign: C249`, `oos_edge_proven: false`.

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
| #9 Enriched-gate causal/per-bar edge discovery & robustness | COMPLETE (`no_edge`) | `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`), `tests/test_campaign9_causal_gate_edge_search.py` |
| #10 Wider-universe causal per-bar gate validation | COMPLETE (`insufficient_or_blocked`) | `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json` (SHA256 `8c3c5d5785c0d7bd33c805f939528771809494dba400e6f990d269dd3369b895`), `tests/test_campaign10_wider_universe_causal_gates.py` |
| **#11 Rolling-stability blocker diagnosis & gate-pass feasibility** | **COMPLETE (`no_edge`)** | `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py` |

## 3) CAMPAIGN #11 — EXECUTION RECORD (COMPLETE)

**Objective:** On cached real data only, determine whether `rolling_stable_ok` trailing-window insufficiency is the sole structural blocker (no bar passes all enriched gates on any wider-universe pair under unmodified thresholds) or whether any pair/slice ever achieves a causal per-bar gate pass, across trailing sample lengths/check intervals, **without weakening gate thresholds**.

**Constraints honored:** No network refetch, no synthetic/fabricated data/labels/metrics/fills/IV/volume. Gate thresholds unmodified. `research_state/state.yaml` RQA line untouched. Campaigns #1–#10 not redone.

**Deliverables:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`.

**Findings (honest, reproducible):** conclusion `no_edge` (edge_claim false). No bar passes all enriched gates on any wider-universe pair under swept configs with unmodified thresholds. `rolling_stable_ok` blocks **5112/5112 bars** across pairs/sweeps (structural blocker confirmed). Cached-aggregate and causal-per-bar paths agree (fail-closed). No positive OOS/replay edge; zero gate-pass slices => cost-aware evaluation not possible. Cached-real/gate research line exhausted under current gate schema/thresholds without fabricating data/trades/edge.

## 4) REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/
```

## 5) KEY FILES

- **C11:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`
- **C10:** `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json`, `tests/test_campaign10_wider_universe_causal_gates.py`
- **C9:** `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json`, `tests/test_campaign9_causal_gate_edge_search.py`
- **C8:** `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`

---

**END OF DURABLE HANDOFF — CAMPAIGNS #1–#11 COMPLETE (`no_edge` on cached-real enriched-gate line; exhausted under current gates/thresholds). NEXT SESSION: execute §0 (new real cached data or orthogonal real-data-only work without threshold-weakening/fabrication, else evidence-backed closeout). NO STATUS-ONLY WORK.**
