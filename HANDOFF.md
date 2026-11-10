# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaigns #1-#6 COMPLETE (Campaign #6 honest/paper, bounded)**. Required C6 artifacts present: `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json`. Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`; historical handoff JSON/scripts live under `reports/` and `scripts/` and are not active directives). **No fabrication.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`, locked C104-C248) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs/plans, rerunning C104-C248, rerunning completed Campaigns #1-#6 without a concrete defect, or fabricating data/fills/order books/labels/metrics/exchange responses.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-10T03:26:31Z | VERIFIED NOW | `HANDOFF.md` is the ONLY active root handoff/TODO — no competing root handoff/TODO docs; historical handoff artifacts exist only under `reports/`/`scripts/` (non-directive). `git status` clean at inspection time, working tree clean, nothing staged. No blocked/stale sessions, lock markers, or obvious session inefficiencies detected. Toolchain paths documented; last recorded baseline gates **green** (2026-11-10T03:24:50Z: `pytest tests/ -q` => **997 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success, 36 source files**). **Rerun gates after any source change.** Campaigns #1-#6 complete (honest). C6 artifacts present: `reports/live_testnet_readiness.json` (capability probes, blocked routes, preflight checklist, go/no-go), `reports/testnet_order_lifecycle.json` (9/9 lifecycle scenarios passed), `reports/paper_microstructure_validation.json` (8 fills with latency/slippage/impact/queue/partial-fill stats). EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #7 (OPERATOR DEPLOYMENT HARDENING, MEDIUM/LOW) IMMEDIATELY with heavy work. Do NOT stop at reading/status/planning/docs.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #7 NOW (HEAVY WORK, NON-OPTIONAL, NO EXIT WITHOUT CODE+TESTS+ARTIFACT).**
- **First substantive actions MUST produce code + tests + honest artifact** for Campaign #7 (or a user-explicit override). Do **NOT** stop after reading/summarizing/status-checking/planning without implementing. Planning/summaries without committed implementation = **failure**.
- **Do NOT redo Campaigns #1-#6** unless you find a concrete defect and fix it with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248.
- **No fabrication. Ever.** No synthetic/fabricated fills, order books, exchange responses, balances, PnL, or metrics presented as real/testnet evidence. Exchange credentials/testnet keys are not assumed.
- **Bottleneck removal (2026-11-10T03:26:31Z):** clean git tree; toolchain present (`/home/runner/work/_temp/kilo-home/.local/bin`, deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`); baseline gates last green (2026-11-10T03:24:50Z) — no blocked/stale sessions or lock markers detected. Standing constraints (handle honestly, not as excuses): rerun gates after source changes; no exchange/testnet credentials present; historical L2/intrabar replay not publicly available — do not fabricate.
- **Heavy-work mandate:** At least one new source module, one new test module, and one honest artifact under `reports/` for C7. Status-only/doc-only/re-verification-only work is insufficient.

**Campaign #7 target (execute now): Operator deployment hardening — config profiles, secret-free env templates, observability hooks, reconciliation checks, bounded dry-run operational playbooks (MEDIUM/LOW).**
1. **Config profiles & secret-free env templates:** Define dev/staging/prod config schemas (YAML/TOML/JSON) with strict validation; secret-free `.env.example` templates listing required vars by name only (never values); environment detection and profile switching.
2. **Observability hooks:** Structured logging (JSON lines) for order lifecycle, risk decisions, adapter probes, microstructure events; metrics emission (Prometheus-compatible counters/histograms/gauges) for fills, latency, slippage, rejections, risk breaches; health-check endpoints (liveness/readiness) with dependency status.
3. **Reconciliation checks:** End-of-session position/cash/equity reconciliation against exchange (or paper ledger) with tolerance thresholds; fill audit trail with client_order_id ↔ exchange_order_id linkage; order lifecycle state machine audit (no invalid transitions, no orphan orders).
4. **Bounded dry-run operational playbooks:** Preflight checklist automation (capability probes, credential presence, network reachability, risk config validation); start/stop/pause/resume procedures with state persistence; incident response runbook (kill-switch activation, position flattening, alert escalation); dry-run validation script that exercises full stack without live capital.
5. **Required artifacts (honest schema):** at minimum `reports/operator_deployment_readiness.json` and `reports/reconciliation_audit.json` with `campaign`, `status`, `generated_at_utc`, `real_data_only`/`fabricated_data` as applicable, `simulated`/`real_exchange_interaction` flags, `blocked_routes`, `environment/capability_probes` (no secrets), `limitations`, `notes`.
6. **Tests:** config schema validation, secret-free template rendering, observability emission correctness, reconciliation logic with tolerance thresholds, playbook dry-run smoke test, fail-closed behavior under missing config/credentials.
7. **Quality gates before declaring C7 complete (rerun after changes):**
   ```bash
   cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
   export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
   export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
   python -m pytest tests/ -q
   python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
   python -m mypy backtest/ strategies/ utils/
   ```
   Fix regressions caused by your changes. Record outcomes truthfully.
8. **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified truth. Keep it the single durable handoff.

**This directive remains active until** Campaign #7 required artifacts exist with honest schema/provenance and C7 implementation/tests/gates are materially complete.

## 1) Verified state (2026-11-10T03:26:31Z)

- **Deps/gates env:** local deps in `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages`; tools in `/home/runner/work/_temp/kilo-home/.local/bin`.
- **Last recorded full gates (2026-11-10T03:24:50Z):** `997 passed, 1 skipped`; `ruff` all passed (`backtest/ data/ strategies/ utils/ tests/ examples/`); `mypy` success (`backtest/ strategies/ utils/`, 36 source files). **Rerun after any source change.**
- **Real data:** Binance public spot klines/cached data available and used for C5/C6 bounded sessions; 451/blocked-route handling honest. Never fabricate.
- **Artifacts C1-C6:** `reports/funding_carry_real.json`, `reports/execution_lob_real.json`, `reports/regime_adaptive_sweep.json`, `reports/ml_gated_pairs.json`, `reports/pairs_mtf_5m_1h.json`, `reports/paper_trading_session.json`, `reports/risk_dashboard.json`, `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json` present (C6 honest/paper/bounded).
- **C7 artifacts:** not yet present.
- **Bottlenecks:** none blocking start; toolchain/clean tree present. Constraints: no exchange/testnet credentials; no public historical L2/intrabar replay.

## 1.1) Parallel-track caution
`research_state/state.yaml` (locked C104-C248, `next_campaign: C249`, `oos_edge_proven: false`) is a separate locked RQA/volume line. **Do not** work C249/registry/status instead of Campaign #7 unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest (held-out proxy 0.473 < 0.65; best OOS mean return 0.0). |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (ok, 2296 real rows). `reports/execution_lob_real.json` (partial; snapshots ok; historical L2 replay infeasible; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (ok, real-data-only, 544 labeled rows, cv_ok). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, tests, runner. |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json` (ok,true,false), `utils/mtf_pairs.py`, `examples/run_pairs_mtf_5m_1h_real.py`, `tests/test_pairs_mtf.py`. 14 pairs evaluated; base cost sensitivity 8 ok; negative mean Sharpe reported honestly — no profitable edge claimed. |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper, honest) | `reports/paper_trading_session.json` (ok,true,true,false,true,false; 22 paper fills, all labeled simulated/not real exchange; real cached Binance BTC 1h; blocked live/testnet routes recorded). `reports/risk_dashboard.json`. Code: `execution/oms.py`, `execution/paper_broker.py`, `execution/risk.py`, `utils/risk_dashboard.py`, `examples/run_paper_trading_live.py`. Tests: `tests/test_production_bridge_campaign5.py` (11). Full gates green as recorded. |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json` (capability probes, blocked routes, preflight, go/no-go), `reports/testnet_order_lifecycle.json` (9/9 lifecycle scenarios passed), `reports/paper_microstructure_validation.json` (8 fills with latency/slippage/impact/queue/partial-fill stats). Code: `execution/adapter.py`, `execution/lifecycle.py`, `execution/microstructure.py`, `examples/run_live_testnet_readiness.py`. Tests: `tests/test_live_testnet_execution_campaign6.py` (41). Full gates green as recorded. |
| #7 Operator deployment hardening | **NOT STARTED / REQUIRED NEXT** | Execute §0 immediately; config profiles, secret-free env templates, observability hooks, reconciliation checks, bounded dry-run operational playbooks. |

## 3) Next focus campaign — Operator deployment hardening (MEDIUM/LOW)
Execute immediately. See §0. Deliver config/observability/reconciliation/playbook implementation, tests, and honest readiness + audit artifacts. Still no fabricated fills/evidence.

## 4) Follow-on campaign (only after Campaign #7 complete + artifacts exist)
**Continuous monitoring & incident response hardening (LOW)** — automated drift detection, alert escalation, rollback procedures, and post-incident audit trail. Still no fabricated fills/evidence.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats:/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
python examples/run_paper_trading_live.py  # regenerates C5 artifacts from real cached data
python examples/run_live_testnet_readiness.py  # regenerates C6 artifacts
```

## 6) Handoff contract
- Start with Campaign #7 immediately. Do not redo #1-#6 unless fixing a concrete defect.
- Produce real/public-data artifacts with provenance. Any simulated/testnet/paper fill must be explicitly labeled; never claim real exchange evidence. If blocked, record exact `blocked_routes`/rationale — do not fabricate.
- At material checkpoint/completion, update **only** `HANDOFF.md` with verified truth. Keep it the single durable handoff.
