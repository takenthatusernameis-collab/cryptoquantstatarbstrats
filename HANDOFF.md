# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaigns #1-#6 COMPLETE (Campaign #6 honest/paper, bounded)**. Required C6 artifacts present: `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json`. **Campaign #7 IN PROGRESS (PARTIAL)**: prior session reported C7 code/test fixes and `pytest tests/ -q` => **1064 passed, 1 skipped**, `mypy backtest/ strategies/ utils/` => **Success**, but **ruff failing** (standard scope 35 errors; C7-focused scope 78 errors, mostly E501). Competing handoff/TODO/plan docs at repo root: **NONE** (only `HANDOFF.md`). **No fabrication.** `research_state/state.yaml` (locked RQA line C104-C248, `next_campaign: C249`, `oos_edge_proven: false`) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-10T07:29:25Z | VERIFIED NOW | Repo at `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`, branch `main` (git present), clean competing root handoffs: only `HANDOFF.md`. C7 module dirs present: `config/`, `observability/`, `playbooks/`, `reconciliation/` (+ related examples/tests exist per prior handoff). Environment/tooling in this session: system `python` lacked `ruff`/`pytest`/`mypy`; local tool bins under `/home/runner/work/_temp/kilo-home/.local/bin` and `/home/runner/work/_temp/kilo-tmp` not found — **quality gates could not be re-verified now**. Prior verified baseline (2026-11-10T05:40:54Z, per previous handoff): `pytest` 1064 passed/1 skipped, `mypy` success, `ruff` red (35 std, 78 C7-focused, mostly E501). Workflow diagnostics show recurring CI/loop failures and historical numpy/tooling friction; do not fabricate results. **EXPLICIT DIRECTIONS ABSENT => CONTINUE HEAVY WORK: complete Campaign #7 by making ruff clean (C7 scope first, then full standard scope as feasible) without behavior regressions, then rerun and pass gates.**]**

**NEXT AGENTIC SESSION: FINISH C7 LINT CLEANUP AND RE-VERIFY GATES (HEAVY WORK, NON-OPTIONAL).**
- **First substantive actions MUST produce code fixes + passing lint/tests.** Do **NOT** stop after reading/summarizing/status-checking/planning.
- **Do NOT redo Campaigns #1-#6** unless you find a concrete defect and fix it with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248.
- **No fabrication. Ever.** No fake test/lint outputs, no invented credentials/testnet fills/order books/labels/metrics/exchange responses.
- **Primary focus:** resolve ruff errors without changing behavior or weakening tests. Prior hotspots (verify in current tree): `config/schemas.py` (long Field descriptions), `observability/{health,logging,metrics}.py`, `playbooks/{__init__,dry_run,incident,state}.py`, `reconciliation/{fill_audit,lifecycle_audit}.py`, C7 example runners (`examples/run_operator_deployment_readiness.py`, `examples/run_reconciliation_audit.py`), and touched tests (`tests/test_config.py`, `tests/test_observability.py`, `tests/test_playbooks.py`, `tests/test_reconciliation.py`). Prefer safe wrapping/line breaks/refactors; preserve semantics.
- **Quality gates before declaring C7 complete (install/locate deps/tools as needed, rerun after changes):**
  ```bash
  cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
  # ensure project + dev deps available in the active Python env; if using prior local env:
  # export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
  # export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
  python -m pytest tests/ -q
  python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
  python -m ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py
  python -m mypy backtest/ strategies/ utils/
  ```
  Fix regressions caused by your changes. Record outcomes truthfully.
- **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified truth (timestamp, commands run, counts, remaining blockers if any). Keep it the single durable handoff.

**This directive remains active until** C7 lint/tests/mypy gates are green and verified in-session (or any remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials).

## 1) Verified state (2026-11-10T07:29:25Z)

- **Repo:** `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats` (git repo, recent commits are checkpoint/workflow diagnostics).
- **Single durable handoff:** `HANDOFF.md` only at root (no other `*todo*/*handoff*/next*/plan*` files found).
- **C7 code present:** `config/` (`__init__.py, env.py, profiles.py, schemas.py`), `observability/` (`__init__.py, health.py, logging.py, metrics.py`), `playbooks/` (`__init__.py, dry_run.py, incident.py, preflight.py, state.py`), `reconciliation/` (`__init__.py, cash.py, equity.py, fill_audit.py, lifecycle_audit.py, orchestrator.py, position.py`).
- **Gate tooling (this session):** `python -m ruff/pytest/mypy` unavailable in system env; no local bin/tools located under `/home/runner/work/_temp/kilo-home/.local/bin` or `_temp` search hits — **gates not rerun now**.
- **Prior verified baseline (2026-11-10T05:40:54Z):** `pytest tests/ -q` => 1064 passed, 1 skipped, 4033 warnings in 59.26s. `mypy backtest/ strategies/ utils/` => Success (36 source files). `ruff` red: standard dirs 35 errors; C7-focused 78 errors (E501 dominant). C7 behavioral fixes previously applied (fill audit unmatched handling, config profile validation return, metrics ad-hoc key/auto-create helpers, observability test import, playbook default injection/status semantics, pytest asyncio_mode=auto).
- **Constraints unchanged:** no exchange/testnet credentials; no public historical L2/intrabar replay; never fabricate data/fills/order books/labels/metrics/exchange responses. `research_state/state.yaml` RQA line (C104-C248 locked, C249 preselected, `oos_edge_proven: false`) is separate — do not modify/work unless explicitly requested.

## 1.1) Parallel-track caution
`research_state/state.yaml` (locked C104-C248, `next_campaign: C249`) is a separate locked RQA/volume line. **Do not** work C249/registry/status instead of C7 completion unless explicitly requested.

## 2) Remaining C7 work (fix now)

| Area | State (last verified 2026-11-10T05:40:54Z; not rerun 2026-11-10T07:29:25Z) | Notes |
|---|---|---|
| Tests (C7) | GREEN (prior) | Preserve 1064 passed, 1 skipped; fix any regressions. |
| Mypy | GREEN (prior) | Keep `backtest/ strategies/ utils/` clean. |
| Ruff | RED (prior) | Clear 78 C7-focused + 35 standard-scope errors (mostly E501) without semantic changes. |

## 3) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest. |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required. |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`. |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py`. |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper, honest) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json`. |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json`. |
| #7 Operator deployment hardening | **IN PROGRESS (lint cleanup + gate re-verification required)** | Modules/artifacts present; complete ruff cleanup and verify tests/mypy/ruff green. |

## 4) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
# set env to one with project deps + dev tools (pytest/ruff/mypy/pytest-asyncio) installed
python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m ruff check config/ observability/ playbooks/ reconciliation/ examples/run_operator_deployment_readiness.py examples/run_reconciliation_audit.py tests/test_config.py tests/test_observability.py tests/test_playbooks.py tests/test_reconciliation.py
python -m mypy backtest/ strategies/ utils/
```

## 5) Handoff contract
- Continue with heavy implementation: clear ruff, keep tests/mypy green, no behavior regressions, no fabrication.
- Do not redo #1-#6 unless fixing a concrete defect. Do not touch locked C104-C248/state RQA line.
- Update **only** `HANDOFF.md` at next material checkpoint/completion with verified truth.

(End of file)
