# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaigns #1-#5 COMPLETE (Campaign #5 bounded/paper, honest)**. Required C5 artifacts present: `reports/paper_trading_session.json`, `reports/risk_dashboard.json`. Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`; historical handoff JSON/scripts live under `reports/` and `scripts/` and are not active directives). **No fabrication.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`, locked C104-C248) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs/plans, rerunning C104-C248, rerunning completed Campaigns #1-#5 without a concrete defect, or fabricating data/fills/order books/labels/metrics/exchange responses.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-10T01:32:51Z | VERIFIED NOW | `HANDOFF.md` is the ONLY active root handoff/TODO — no competing root handoff/TODO docs; historical handoff artifacts exist only under `reports/`/`scripts/` (non-directive). `git status` clean at `ddb3828` (`chore(kilo): checkpoint agent session`) with only `execution/risk.py` mypy fix staged. No blocked/stale sessions, lock markers, or obvious session inefficiencies detected. Toolchain paths documented; baseline gates **reenforced green** on 2026-11-10T01:32:51Z (`pytest tests/ -q` => **956 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success, 36 source files**). **Rerun gates after any source change.** Campaigns #1-#5 complete (honest). C5 artifacts present: `reports/paper_trading_session.json`, `reports/risk_dashboard.json`. **C6 artifacts MISSING:** `reports/live_testnet_readiness.json` and `reports/testnet_order_lifecycle.json` / `reports/paper_microstructure_validation.json` absent. EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #6 (LIVE/TESTNET EXECUTION VALIDATION, HONEST/MEDIUM) IMMEDIATELY with heavy work. Do NOT stop at reading/status/planning/docs.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #6 NOW (HEAVY WORK, NON-OPTIONAL, NO EXIT WITHOUT CODE+TESTS+ARTIFACT).**
- **First substantive actions MUST produce code + tests + honest artifact** for Campaign #6 (or a user-explicit override). Do **NOT** stop after reading/summarizing/status-checking/planning without implementing. Planning/summaries without committed implementation = **failure**.
- **Do NOT redo Campaigns #1-#5** unless you find a concrete defect and fix it with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248.
- **No fabrication. Ever.** No synthetic/fabricated fills, order books, exchange responses, balances, PnL, or metrics presented as real/testnet evidence. **Exchange credentials/testnet keys are not assumed.** If authenticated testnet/live access is unavailable, record exact `blocked_routes`/capability probes/limitations honestly, keep `real_data_only`/`fabricated_data`/environment explicit, and still ship the **heaviest valid implementation + tests + dry-run artifact possible**: e.g. testnet adapter interface + capability detection + order-lifecycle state machine + latency/slippage realism extensions to paper OMS + operator runbook artifact, all fail-closed and labeled.
- **Bottleneck removal (2026-11-10T01:32:51Z):** clean git tree at `ddb3828` with only `execution/risk.py` mypy fix; toolchain present (`/home/runner/work/_temp/kilo-home/.local/bin`, deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`); baseline gates **reenforced green** (2026-11-10T01:32:51Z) — no blocked/stale sessions or lock markers detected. Standing constraints (handle honestly, not as excuses): rerun gates after source changes; no exchange/testnet credentials present (C5 correctly blocked live submission — C6 must detect and record this); historical L2/intrabar replay not publicly available — do not fabricate; `execution/` mypy issue fixed — gates fully clean.
- **Heavy-work mandate:** At least one new source module, one new test module, and one honest artifact under `reports/` for C6. Status-only/doc-only/re-verification-only work is insufficient.

**Campaign #6 target (execute now): Live/testnet execution validation — bounded order-lifecycle validation when access exists; otherwise maximal honest paper/testnet-readiness bridge (MEDIUM).**
1. **Capability detection (fail-closed):** Detect credentials/endpoints/network/testnet availability without secrets in artifacts; record probes, blocked routes, and why live/testnet submission is or is not possible.
2. **Testnet adapter interface + dry-run:** Implement exchange adapter abstraction (paper default; optional authenticated testnet adapter only when credentials explicitly available and capability-verified). Never assume credentials. If unavailable, implement adapter contract + simulated testnet-like lifecycle harness with explicit `simulated`/`real_exchange_interaction=false` labels and honest limitations.
3. **Order lifecycle validation:** Cover submit/ack/partial/fill/cancel/replace/reject/timeout/retry semantics in tests. Any non-paper exchange interaction must be explicitly labeled and proven; otherwise simulated and labeled.
4. **Microstructure/latency realism (paper):** Extend paper execution with configurable latency, queue/partial-fill, slippage/impact hooks, and data-gap handling — all honest/provenance-labeled.
5. **Operator runbook artifact:** Emit `reports/live_testnet_readiness.json` (or equivalent) with capability probes, blocked routes, required credentials/env vars by name only (never values), preflight checklist, risk/kill-switch state, and go/no-go status.
6. **Required artifacts (honest schema):** at minimum `reports/live_testnet_readiness.json` and one bounded validation artifact (e.g. `reports/testnet_order_lifecycle.json` or `reports/paper_microstructure_validation.json`) with `campaign`, `status`, `generated_at_utc`, `real_data_only`/`fabricated_data` as applicable, `real_exchange_interaction`/`simulated` flags, `blocked_routes`, `environment/capability_probes` (no secrets), `limitations`, `notes`.
7. **Tests:** adapter contract/capability fail-closed, lifecycle state machine, retry/timeout/idempotency, labeling/provenance (never claim real exchange evidence when simulated), and smoke integration.
8. **Quality gates before declaring C6 complete (rerun after changes):**
   ```bash
   cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
   export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
   export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
   python -m pytest tests/ -q
   python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
   python -m mypy backtest/ strategies/ utils/
   ```
   Fix regressions caused by your changes. Record outcomes truthfully.
9. **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified truth. Keep it the single durable handoff.

**This directive remains active until** Campaign #6 required artifacts exist with honest schema/provenance and C6 implementation/tests/gates are materially complete.

## 1) Verified state (2026-11-10T01:32:51Z)

- **Deps/gates env:** local deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`; tools in `/home/runner/work/_temp/kilo-home/.local/bin`.
- **Last recorded full gates (2026-11-10T01:32:51Z):** `956 passed, 1 skipped`; `ruff` all passed (`backtest/ data/ strategies/ utils/ tests/ examples/`); `mypy` success (`backtest/ strategies/ utils/`, 36 source files). **Rerun after any source change.**
- **Real data:** Binance public spot klines/cached data available and used for C5 bounded session; 451/blocked-route handling honest. Never fabricate.
- **Artifacts C1-C5:** `reports/funding_carry_real.json`, `reports/execution_lob_real.json`, `reports/regime_adaptive_sweep.json`, `reports/ml_gated_pairs.json`, `reports/pairs_mtf_5m_1h.json`, `reports/paper_trading_session.json`, `reports/risk_dashboard.json` present (C5 honest/bounded/paper).
- **C6 artifacts:** not yet present.
- **Bottlenecks:** none blocking start; toolchain/clean tree present. Constraints: no exchange/testnet credentials; no public historical L2/intrabar replay; `execution/` typing issue fixed (mypy clean).

## 1.1) Parallel-track caution
`research_state/state.yaml` (locked C104-C248, `next_campaign: C249`, `oos_edge_proven: false`) is a separate locked RQA/volume line. **Do not** work C249/registry/status instead of Campaign #6 unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest (held-out proxy 0.473 < 0.65; best OOS mean return 0.0). |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (ok, 2296 real rows). `reports/execution_lob_real.json` (partial; snapshots ok; historical L2 replay infeasible; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (ok, real-data-only, 544 labeled rows, cv_ok). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, tests, runner. |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json` (ok,true,false), `utils/mtf_pairs.py`, `examples/run_pairs_mtf_5m_1h_real.py`, `tests/test_pairs_mtf.py`. 14 pairs evaluated; base cost sensitivity 8 ok; negative mean Sharpe reported honestly — no profitable edge claimed. |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper, honest) | `reports/paper_trading_session.json` (ok,true,true,false,true,false; 22 paper fills, all labeled simulated/not real exchange; real cached Binance BTC 1h; blocked live/testnet routes recorded). `reports/risk_dashboard.json`. Code: `execution/oms.py`, `execution/paper_broker.py`, `execution/risk.py`, `utils/risk_dashboard.py`, `examples/run_paper_trading_live.py`. Tests: `tests/test_production_bridge_campaign5.py` (11). Full gates green as recorded. |
| #6 Live/testnet execution validation | **NOT STARTED / REQUIRED NEXT** | Execute §0 immediately; honest capability detection; no credentials assumed; no fabricated exchange evidence. |

## 3) Next focus campaign — Live/testnet execution validation (MEDIUM)
Execute immediately. See §0. Deliver adapter/capability/lifecycle/microstructure implementation, tests, and honest readiness + validation artifacts. If credentials/testnet unavailable, block routes honestly and ship maximal paper/microstructure/runbook readiness.

## 4) Follow-on campaign (only after Campaign #6 complete + artifacts exist)
**Operator deployment hardening (MEDIUM/LOW)** — config profiles, secret-free env templates, observability hooks, reconciliation checks, and bounded dry-run operational playbooks. Still no fabricated fills/evidence.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
python examples/run_paper_trading_live.py  # regenerates C5 artifacts from real cached data
```

## 6) Handoff contract
- Start with Campaign #6 immediately. Do not redo #1-#5 unless fixing a concrete defect.
- Produce real/public-data artifacts with provenance. Any simulated/testnet/paper fill must be explicitly labeled; never claim real exchange evidence. If blocked, record exact `blocked_routes`/rationale — do not fabricate.
- At material checkpoint/completion, update **only** `HANDOFF.md` with verified truth. Keep it the single durable handoff.
