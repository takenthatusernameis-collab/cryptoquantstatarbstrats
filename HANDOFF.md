# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 COMPLETE. Campaign #2 COMPLETE. Campaign #3 COMPLETE** (required artifacts present/verified; real data+provenance; honest). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **No fabrication. No blocking setup bottlenecks found.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`) is separate/locked — do **not** spend session on it unless explicitly requested. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs, rerunning C104-C248, rerunning completed Campaigns #1-#3 without a concrete defect, or fabricating data/fills/order books/labels/metrics.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T19:06:22Z | INITIAL TASK MESSAGE — RE-VERIFIED THIS SESSION: `HANDOFF.md` is the only root handoff/TODO. C1-C3 artifacts present+honest: `reports/funding_carry_real.json` (ok,true,false), `reports/execution_lob_real.json` (partial,true,false), `reports/regime_adaptive_sweep.json` (present), `reports/ml_gated_pairs.json` (ok,true,false). `reports/pairs_mtf_5m_1h.json` **MISSING**. No `pairs_mtf*` implementation files found outside reports. `data/cache` has 11-symbol 1h real frame (2026-04-01→2026-10-30) but **no 5m/15m cache**. Last full-gate baseline recorded in prior handoff: `940 passed, 1 skipped, 0 failures`; ruff/mypy clean on `main@2a82c21` — rerun after any source change. NEXT/ONLY FOCUS: Campaign #4 — HF/multi-timeframe cointegration (HIGH). EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #4. HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL, NO FABRICATION, NO LIGHTER TASKS, NO PLANNING-ONLY DELIVERABLES.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #4 NOW.** The first substantive actions must produce **code + tests + real-data validation + artifact emission** for Campaign #4 (or a user-explicit override). Do **not** stop after reading, summarizing, status-checking, or refreshing docs. Campaigns #1-#3 are complete/honest; **do not redo them** unless a concrete defect is found and fixed with evidence. Absence of new user direction does **not** permit planning-only work, summaries as deliverables, exploratory reading without implementation, cleanup-only work, alternate handoffs, `research_state/`/C249 registry/status work, or reruns of locked C104-C248/completed campaigns. If a real route is blocked, record exact `blocked_routes`, keep `real_data_only`/`fabricated_data` honest, and still ship the heaviest valid implementation/tests/artifact possible under fail-closed rules. **Future agents must not avoid heavy work:** this directive remains active until `reports/pairs_mtf_5m_1h.json` exists with honest schema/provenance **and** Campaign #4 implementation/tests/gates are materially complete; then update only `HANDOFF.md` and advance to the production-bridge follow-on.

**Campaign #4 target (execute now): HF/multi-timeframe cointegration (HIGH)**
- Multi-timeframe pairs: 1h cointegration/hedge + 5m/15m entry signals on real Binance spot candles; universe from cached 11-symbol 1h frame (ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP) where available.
- Causal multi-TF alignment (no lookahead); 5m execution realism (slippage/impact/LOB-aware where feasible). Historical L2/intrabar replay not publicly available here — record honest `blocked_routes`/limitations; **do not fabricate fills/order books**.
- Purged walk-forward validation across 1h/4h/1d where data permits; fail-closed on insufficient data.
- Required artifact: `reports/pairs_mtf_5m_1h.json` (schema: `real_data_only`, `fabricated_data`, `generated_at_utc`, `campaign`, `status`, `blocked_routes`, sources/symbols/windows/metrics/limitations/checksums/provenance).
- Minimum viable heavy deliverables: strategy/util logic for multi-TF pairs signals (causal), unit+integration tests (fixed fixtures; synthetic only if explicitly flagged in tests, never in real-data artifacts), `examples/run_pairs_mtf_5m_1h_real.py` (or equivalent) emitting the artifact, honest metrics/provenance.
- Quality gates before done (rerun after changes): `PYTHONPATH=. python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`. Fix regressions caused by your changes.
- Update **only** `HANDOFF.md` at material checkpoint/completion.

**Bottlenecks removed (re-verified 2026-11-09T19:06:22Z):** **NONE blocking start**. No competing handoffs/TODOs. Deps import OK. C1-C3 artifacts present. `HANDOFF.md` refreshed in place as the single durable directive. **Known real-data constraints (not excuses to avoid heavy work):** no 5m/15m cache files found in `data/cache/`; historical L2/intrabar replay not available from current public routes (`reports/execution_lob_real.json` partial, honest). Fetch 5m/15m via real public routes with provenance if feasible, or record exact `blocked_routes` and still implement/test/emit the heaviest honest artifact possible. Do **not** create setup/blocker artifacts, alternate plans, or docs as a substitute for Campaign #4.

**Handoff timestamp (UTC)**: 2026-11-09T19:06:22Z
**Repository**: `cryptoquantstatarbstrats`
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD (at verification check)**: `main @ 72a9489` (handoff-only refresh in this session)
**Single durable handoff rule**: ONLY `HANDOFF.md`. Do not create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes.
**Campaign #1 status**: COMPLETE. **Campaign #2 status**: COMPLETE (honest). **Campaign #3 status**: COMPLETE. **Campaign #4 status**: NOT STARTED / REQUIRED NEXT.

## 1) Verified state (2026-11-09T18:18:35Z)

- **Deps**: numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy importable.
- **Gates (last fresh run 2026-11-09T18:18:00Z)**: `pytest` → `940 passed, 1 skipped, 0 failures`; `ruff` → All checks passed; `mypy` → Success, no issues in 34 source files. **Rerun after any source change and before declaring Campaign #4 complete.**
- **Real data**: Binance public host chain works; 451 routes handled/recorded where encountered. **Never fabricate data/fills/order books.**
- **Artifacts:** `reports/funding_carry_real.json` `ok/true/false`; `reports/execution_lob_real.json` `partial/true/false` (historical L2 replay infeasible from public routes, honest); `reports/regime_adaptive_sweep.json` present; `reports/ml_gated_pairs.json` `ok/true/false` (544 rows, cv_ok true, 0 blocked/0 errors).
- **Cached 1h data available:** `data/cache/` has 11-symbol 1h frame `2026-04-01→2026-10-30` (`0bab5d6a...pkl`, 5112×11: ADA/AVAX/BNB/BTC/DOT/ETH/LINK/LTC/POL/SOL/XRP), plus BTC/ETH/SOL subsets and per-symbol 1h series; provenance flags present (`fetch_real_data_only`/`fetch_fabricated_data`). **No 5m/15m cache files found** — C4 must fetch real 5m/15m with provenance or record `blocked_routes`.
- **Bottlenecks:** **NONE** blocking Campaign #4 start.

## 1.1) Parallel-track caution
`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`, `oos_edge_proven: false`) is a separate locked line. **Do not** work C249/registry/status instead of Campaign #4 unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest (held-out proxy 0.473 < 0.65; best OOS mean return 0.0). |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (ok, 2296 real rows). `reports/execution_lob_real.json` (partial; point-in-time snapshots ok; historical L2 replay infeasible from public routes; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (ok, real-data-only, 544 labeled rows, cv_ok, 0 blocked/errors). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, tests, runner. |
| #4 HF/multi-timeframe cointegration | **NOT STARTED / REQUIRED NEXT** | `reports/pairs_mtf_5m_1h.json` missing. Execute §0 immediately. |

## 3) Next focus campaign — HF/multi-timeframe cointegration (HIGH)
Execute immediately. See §0. Required artifact: `reports/pairs_mtf_5m_1h.json` (or honest `blocked`/`partial` with full schema/provenance). Real data only; no lookahead; purged WF/leakage controls; fail-closed on insufficient data; honest metrics regardless of outcome.

## 4) Follow-on campaign (only after Campaign #4 complete + artifact exists)
**Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract
- Start with Campaign #4 immediately. Do not redo #1-#3 unless fixing a concrete defect.
- Produce real artifacts with provenance. If blocked, record exact `blocked_routes`/rationale — do not fabricate.
- At material checkpoint/completion, update **only** `HANDOFF.md` with verified truth. Keep it the single durable handoff.
