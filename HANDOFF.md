# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. DO HEAVY WORK NOW.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 — Regime-Adaptive Signal Generation is COMPLETE**. Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **Re-verified 2026-11-09T14:44:00Z on `main@14fd79f6b73bdc542280caa48893ffb5d10366bf` (clean):** core deps importable (`numpy`, `pandas`, `scipy`, `hmmlearn/GaussianHMM OK`). Campaign #1 artifacts present: `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Quality gates **re-run and PASS this pass**: `928 passed, 1 skipped, 0 failures`; `ruff` All checks passed; `mypy` Success (32 source files) — **re-run gates before claiming done on Campaign #2 changes.** **Campaign #2 required artifacts MISSING:** `reports/funding_carry_real.json`, `reports/execution_lob_real.json`. **No setup bottlenecks found** (clean tree, deps OK, no competing handoffs). Loader families `funding_basis_carry`/`intrabar_microstructure` already exist in `data/real_feed_loader.py` (specs/validation hooks present); real-public-route fetch + artifact emission remain the assigned work, not excuses. **Forbidden before Campaign #2 artifacts exist:** docs-only edits, cleanup, refactors, planning detours, exploratory side quests, status-only bookkeeping, alternate handoffs/TODOs, or `research_state/` C249 registry/status work.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T14:44:00Z | INITIAL TASK MESSAGE — Campaign #1 COMPLETE (GATES RE-VERIFIED PASS); CAMPAIGN #2 (FUNDING/BASIS-CARRY + LOB/INTRABAR FEASIBILITY) IS THE ONLY VALID NEXT WORK. HEAVY WORK, NON-OPTIONAL, NO SUBSTITUTES, NO DEFERRAL, NO FABRICATION.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #2 NOW.** Campaign #1 is complete. Absence of new user direction does **not** permit lighter work. Your first actions must be implementation, tests, real-data fetch/validation, and artifact emission — **never** planning, summaries, alternate handoffs, cleanup, refactors, `research_state/`/C249 registry/status work, or gate-only reruns without producing artifacts. This file is the **only** durable handoff.

**Required Campaign #2 deliverables (both required; "blocked" must still be evidenced):**

1. **`reports/funding_carry_real.json` (REQUIRED):** real public funding-rate/basis-carry analysis.
   - Fetch real public funding-rate data (`/fapi/v1/fundingRate` semantics or equivalent). **Do not rely on `api.binance.com`/`fapi.binance.com` 451**; attempt a working public host chain consistent with loader policy and record every route attempted.
   - Unblock/extend `funding_basis_carry` support in `data/real_feed_loader.py` and provenance/metadata handling as needed. Add/adjust tests for the loader path and for the artifact-emission script/example.
   - Compute honest funding/basis-carry metrics usable by the codebase (e.g., funding time series, annualized carry, basis where feasible, summary stats, window/asset coverage). **No fabricated numbers/data.**
   - If a route is blocked/unavailable, record exact `blocked_routes` (host/path/status/error/UTC) and continue with feasible public alternatives; still emit the artifact with `status: blocked`/partial as honest.

2. **`reports/execution_lob_real.json` (REQUIRED):** real LOB/intrabar microstructure feasibility.
   - Assess order-book/intrabar microstructure feasibility from real public data where feasible; unblock/extend `intrabar_microstructure` handling in `data/real_feed_loader.py` if feasible. Add/adjust tests.
   - If real L2/intrabar data is unavailable via permitted public routes, emit an honest feasibility artifact: attempted routes/hosts, exact `blocked_routes`, observed limits, schema/provenance expectations, and what real inputs would be required. **No fabricated fills/order books.**

3. **Artifact schema minimum (both files):** `real_data_only: true`, `fabricated_data: false`, `generated_at_utc`, `campaign`, `status` (`ok|partial|blocked`), `data_sources`/hosts/routes attempted, `symbols`/assets, time window/freq, row counts/checksums/sample hashes where data obtained, `blocked_routes` (empty array or explicit objects), metrics/results/feasibility findings, and notes on limitations. Honest failure is acceptable; fabrication is not.

4. **Evaluation discipline:** held-out validation where applicable; no lookahead; cointegration/strategy gates fail-closed; report metrics honestly even if unmet.

5. **Quality gates (must pass before done):** `python -m pytest tests/ -q`; `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`; `python -m mypy backtest/ strategies/ utils/`. Fix regressions caused by your changes.

6. **Handoff update (required at material checkpoint/completion):** update **only** `HANDOFF.md` in place with verified truth — timestamp, `HEAD`, gate results, artifact paths/status, outcomes, exact blockers. Keep it the single durable handoff. Do not create competing docs.

**Bottlenecks removed (re-verified 2026-11-09T14:44:00Z): NONE.** No missing source deps (`numpy/pandas/scipy/hmmlearn` present), clean working tree on `main@14fd79f6b73bdc542280caa48893ffb5d10366bf`, no competing root handoff/TODO docs, no uncommitted WIP. Loader `funding_basis_carry`/`intrabar_microstructure` blocked-route families are the assigned implementation targets — attempt real public routes, implement honestly, and emit required artifacts. C249 (`research_state/state.yaml`, `next_campaign: C249`) is a separate locked RQA/volume track; **do not spend this session on C249 registry/status work** unless explicitly requested by the user.

**Handoff timestamp (UTC)**: 2026-11-09T14:44:00Z (re-verified: HEAD, deps, artifact presence, cleanliness, quality gates PASS)
**Repository**: `cryptoquantstatarbstrats` (Crypto Quantitative Statistical Arbitrage Strategies).
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ 14fd79f6b73bdc542280caa48893ffb5d10366bf` (clean at verification time)
**Single durable handoff rule**: this is the ONLY handoff document for the next session. Do **not** create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes.
**Campaign #1 status**: COMPLETE — HMM regime detection (`utils/regime.py`), regime-conditioned sweeps (`backtest/sweep.py`), regime transition costs (`backtest/execution.py`), real-data example (`examples/run_regime_detection_real.py`), artifact (`reports/regime_adaptive_sweep.json`).
**Campaign #2 status**: **NOT STARTED / REQUIRED** — `reports/funding_carry_real.json` and `reports/execution_lob_real.json` **MISSING**. Next agent must produce both with real public data/provenance or honest evidenced blockers.

## 1) Verified state (bottlenecks cleared) — re-confirmed 2026-11-09T14:44:00Z

- **Tests**: `928 passed, 1 skipped, 0 failures` (`python -m pytest tests/ -q`). Re-verified 2026-11-09T14:44:00Z on `main@14fd79f6b73bdc542280caa48893ffb5d10366bf`.
- **Ruff**: `All checks passed!` across `backtest/ data/ strategies/ utils/ tests/ examples/`. Re-verified 2026-11-09T14:44:00Z on `main@14fd79f6b73bdc542280caa48893ffb5d10366bf`.
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`). Re-verified 2026-11-09T14:44:00Z on `main@14fd79f6b73bdc542280caa48893ffb5d10366bf`.
- **Dependencies**: `hmmlearn==0.3.3` listed in `[project.optional-dependencies] dev`; installed via `pip install -e ".[dev]"` and confirmed `from hmmlearn.hmm import GaussianHMM` OK.
- **Real data path**: Binance spot fetch works via loader host chain (`www.binance.com`; `api.binance.com` 451 is never relied upon). **Never fabricate data**; report `blocked_routes` honestly when a series cannot be reconstructed.
- **Campaign #1 artifacts**: `examples/run_regime_detection_real.py` and `reports/regime_adaptive_sweep.json` present (`real_data_only: true`, `fabricated_data: false`).
- **Campaign #1 outcomes (honest)**: held-out classifier accuracy proxy 0.473 (< 0.65 target, `meets_accuracy_target: false`); best OOS mean return 0.0 (no regime with positive OOS Sharpe after costs); `blocked_routes: []`. Reported honestly, not fabricated.
- **Bottlenecks**: **NONE** (no missing source deps, no failing gates, no loader blocker, no stale parallel handoff, no uncommitted WIP; dev deps installed and verified).
- **Working tree**: clean on `main` (`14fd79f6b73bdc542280caa48893ffb5d10366bf`), no uncommitted changes.

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

## 3) Next focus campaign — Alternative data / funding rates / basis-carry + LOB/intrabar microstructure (HIGH)

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