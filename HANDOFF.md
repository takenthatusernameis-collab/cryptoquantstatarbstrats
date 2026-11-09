# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. DO HEAVY WORK NOW.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 — Regime-Adaptive Signal Generation is COMPLETE** (verified 2026-11-09T10:43:00Z). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **Verified 2026-11-09T11:47:42Z on `main@e76bc79` (clean): deps OK (`numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `hmmlearn 0.3.3`, `GaussianHMM` importable); `reports/regime_adaptive_sweep.json` + `examples/run_regime_detection_real.py` present.** Last recorded gates (2026-11-09T10:54:21Z, `main@fc32a87`, substantively unchanged): `928 passed, 1 skipped, 0 failures`, `ruff check` clean, `mypy` clean (32 source files). **Next-campaign artifacts NOT yet present:** `reports/funding_carry_real.json`, `reports/execution_lob_real.json` (MISSING — heavy work required). **No bottlenecks found.** **Do not** do docs-only edits, cleanup, refactors, planning detours, exploratory side quests, status-only bookkeeping, or continue the separate C248/C249 `research_state/` artifact track before producing next-campaign artifacts.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T11:47:42Z | INITIAL TASK MESSAGE — Campaign #1 COMPLETE; Next Focus: Alternative Data / Funding Rates / Basis-Carry / LOB Feasibility (HIGH, HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL)]**

**NEXT AGENTIC SESSION: EXECUTE THE NEXT FOCUS CAMPAIGN NOW.** Campaign #1 is complete. Absence of new user direction does **not** permit lighter work. Your first actions must be implementation, tests, real-data fetch/validation, and artifact emission for the next focus campaign — **never** planning, summaries, alternate handoffs, cleanup, refactors, or `research_state/`/C249 registry/status work. This file is the **only** durable handoff; do not create or follow parallel handoffs/TODOs.

1. **Next focus campaign (HIGH, required artifacts): Alternative data / funding rates / basis-carry / LOB feasibility.**
   - **Funding/basis-carry (required):** obtain real public funding-rate data (`/fapi/v1/fundingRate` semantics) and build a funding/basis-carry analysis usable by the codebase. `api.binance.com`/`fapi.binance.com` 451 must **not** be relied upon — use a working public host chain consistent with loader policy and record every route attempted. Unblock/extend `funding_basis_carry` support in `data/real_feed_loader.py` and add loader-compatible provenance/metadata handling as needed. **Real data only; no fabrication.** If a route is blocked, record exact `blocked_routes` (host/path/status/error) and continue with feasible public alternatives; still emit an honest artifact.
   - **LOB/intrabar microstructure feasibility (required):** assess/order-book or intrabar microstructure feasibility from real public data where feasible; unblock/extend `intrabar_microstructure` handling in `data/real_feed_loader.py` if feasible. If real L2/intrabar data is unavailable via permitted public routes, emit an honest feasibility artifact documenting what was attempted, `blocked_routes`, limits, and what real inputs would be required — **no fabricated fills/data**.
   - **Required artifacts (must exist regardless of outcome):** `reports/funding_carry_real.json` and `reports/execution_lob_real.json`. Each must include `real_data_only: true`, `fabricated_data: false`, UTC timestamps, data sources/hosts, request/route details, symbols/assets, windows/freq, row counts/checksums where data is obtained, `blocked_routes` (empty or explicit), metrics/results, and clear pass/fail/blocked status. Never fabricate numbers to satisfy a target.
2. **Evaluation:** held-out validation where applicable; report metrics honestly even if unmet. No lookahead; cointegration/strategy gates fail-closed.
3. **Quality gates (must pass before done):** `python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`.
4. **Handoff update:** when this campaign reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, HEAD, gates, artifacts, outcomes, blockers). Keep it the single durable handoff.

**Bottlenecks removed (verified 2026-11-09T11:47:42Z): NONE.** No missing source deps (`numpy/pandas/scipy/hmmlearn` present), no known failing gates (last recorded green on substantively unchanged code), no competing root handoff/TODO docs (only `HANDOFF.md`), no uncommitted work, working tree clean on `main@e76bc79`. Loader blocked-route families `funding_basis_carry`/`intrabar_microstructure` are the **work to do**, not deferral reasons — attempt real public routes, implement honestly, and emit required artifacts with `blocked_routes` if blocked.

**Handoff timestamp (UTC)**: 2026-11-09T11:47:42Z (state re-verified — deps OK, no bottlenecks, next-campaign artifacts pending)
**Repository**: `cryptoquantstatarbstrats` (Crypto Quantitative Statistical Arbitrage Strategies).
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ e76bc79` (clean at verification time)
**Single durable handoff rule**: this is the ONLY handoff document for the next session. Do **not** create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes (timestamp, gates, artifacts, blockers, outcomes).
**Campaign #1 status**: COMPLETE — HMM regime detection (`utils/regime.py`), regime-conditioned sweeps (`backtest/sweep.py`), regime transition costs (`backtest/execution.py`), real-data example (`examples/run_regime_detection_real.py`), and artifact (`reports/regime_adaptive_sweep.json`) all done.
**Next focus status**: NOT STARTED — `reports/funding_carry_real.json` and `reports/execution_lob_real.json` missing; next agent must produce them with real data/provenance.

---

## 1) Verified state (bottlenecks cleared) — re-confirmed 2026-11-09T10:54:21Z

- **Tests**: `928 passed, 1 skipped, 0 failures` (`python -m pytest tests/ -q`). Last verified on `main@fc32a87` (2026-11-09T10:54:21Z); tree unchanged since.
- **Ruff**: `All checks passed!` across `backtest/ data/ strategies/ utils/ tests/ examples/`. Last verified on `main@fc32a87`. (Fixed E501 line-too-long at `backtest/execution.py:358` and removed unused `pandas` import in `examples/run_regime_detection_real.py`.)
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`). Last verified on `main@fc32a87`.
- **Dependencies**: `hmmlearn==0.3.3` listed in `[project.optional-dependencies] dev`; installed via `pip install -e ".[dev]"` and confirmed `from hmmlearn.hmm import GaussianHMM` OK.
- **Real data path**: Binance spot fetch works via loader host chain (`www.binance.com`; `api.binance.com` 451 is never relied upon). **Never fabricate data**; report `blocked_routes` honestly when a series cannot be reconstructed.
- **Campaign #1 artifacts**: `examples/run_regime_detection_real.py` (fixed broken `load_real_ohlcv` import → `DataLoader.load_binance_data`) and `reports/regime_adaptive_sweep.json` (written 2026-11-09T10:42:35Z).
- **Campaign #1 outcomes (honest)**: held-out classifier accuracy proxy 0.473 (< 0.65 target, `meets_accuracy_target: false`); best OOS mean return 0.0 (no regime with positive OOS Sharpe after costs); `blocked_routes: []`. Reported honestly, not fabricated.
- **Bottlenecks**: **NONE** (no missing source deps, no failing gates, no loader blocker, no stale parallel handoff, no uncommitted WIP; dev deps installed and verified).
- **Working tree**: clean on `main` (`fc32a87`), no uncommitted changes.

## 1.1) Parallel-track caution (do not let it block the next focus campaign)

`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`) records a locked C104-C248 RQA/volume costed-OOS artifact line with `oos_edge_proven: false`. This is **real repository state** but **not** the next heavy-work priority for this handoff. The next agent must **not** spend the session on C249 registry/status bookkeeping instead of the next focus campaign. If C249 work is explicitly requested by the user in a future turn, treat it as a separate request; otherwise ignore it and execute the next focus campaign.

## 2) CAMPAIGN #1 — COMPLETED (verified 2026-11-09T10:54:21Z)

| Area | State | Verified |
|---|---|---|
| `utils/regime.py` | HMM (`GaussianHMM`), `hmm_regimes(...)`, `regime_transition_probs(...)`, `detect_regimes(...)` integration, causal fit, no lookahead, deterministic seeding | Implemented + tested |
| `backtest/sweep.py` | Regime-conditioned sweeps accept `regime_labels`/`regime_grids`, walk-forward discipline | Already supported |
| `backtest/execution.py` | Regime transition costs/handling (no fabricated fills) | Already supported |
| Real-data validation | `examples/run_regime_detection_real.py` loads real Binance spot candles only, emits artifact | Ran OK; 0 blocked routes |
| Artifact | `reports/regime_adaptive_sweep.json` per-regime OOS metrics + provenance | Written (`real_data_only: true`, `fabricated_data: false`) |

**Honest outcome summary** (from `reports/regime_adaptive_sweep.json`): held-out classifier accuracy proxy 0.473 (target >65% **not met**); best OOS mean return 0.0 (no regime with positive OOS Sharpe after costs). Artifacts produced regardless of outcome; no data fabricated.

## 3) Next focus campaign — Alternative data / funding rates / basis-carry (HIGH)

Execute per §1 item 1. Real Binance public data only; no fabrication; honest `blocked_routes`; full provenance; artifacts required regardless of outcome; quality gates must stay green.

## 4) Follow-on campaigns (only after the next focus campaign is complete + artifacts exist)

1. **ML-augmented signal filtering (HIGH)** — Classifier for cointegration persistence (rolling EG p, Johansen trace, half-life, Hurst, spread vol, regime); ML-gated sizing; purged WF CV. Artifact: `reports/ml_gated_pairs.json`.
2. **HF/multi-timeframe (MEDIUM)** — 5m/15m, multi-TF cointegration (1h hedge, 5m signals), seasonality, realistic 5m execution. Artifact: `reports/pairs_mtf_5m_1h.json`.
3. **Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract for the executing session

- **Start with the next focus campaign immediately.** The repo is unblocked; there is no valid reason to defer heavy work.
- Produce real artifacts with provenance. If a real-data path is blocked, record exact `blocked_routes` and rationale in the artifact/report — do not fabricate.
- When the next focus campaign reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, gates, artifacts, outcomes, blockers). Keep it the single durable handoff.
