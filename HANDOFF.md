# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. DO HEAVY WORK NOW.**
> Repo priority (name-inferred): **cryptoquantstatarbstrats = crypto quant stat-arb strategies**. The single non-optional focus is **Campaign #1 — Regime-Adaptive Signal Generation** (§3). **No blockers exist.** `hmmlearn==0.3.3` import OK; `ruff`, `mypy`, `pytest` present; `utils/regime.py` is still a **quantile stub (no HMM)**; `backtest/sweep.py` has **no regime conditioning**; `backtest/execution.py` has **no regime transition handling**. Gates re-verified **2026-11-09T08:58:19Z** on `main@5a1a016`: `928 passed, 1 skipped, 0 failures`, `ruff check` clean, `mypy` clean (32 source files), working tree clean, no `examples/run_regime_detection_real.py`, no `reports/regime_adaptive_sweep.json`. **Do not** do docs-only edits, cleanup, refactors, planning detours, exploratory side quests, or continue the separate C248/C249 `research_state/` artifact track before Campaign #1 implementation. Produce real artifacts with provenance.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T08:58:19Z | INITIAL TASK MESSAGE — Campaign #1 Regime-Adaptive Signal Generation (MANDATORY, HEAVY WORK — NO SUBSTITUTES, NO DEFERRAL)]**

**NEXT AGENTIC SESSION MUST EXECUTE CAMPAIGN #1 IMMEDIATELY.** This is the only authorized starting point. Do not plan, summarize, refactor, create alternate handoffs, do status-only bookkeeping, or run C248/C249-style registry campaigns as a substitute. If you touch code/docs in the first hour, it must be Campaign #1 implementation/tests/validation/artifacts.

1. **`utils/regime.py`** — Implement HMM-based regime detection (`GaussianHMM`/`hmmlearn` on returns + realized-vol features). **Causal fit only, zero lookahead**. Add/extend `hmm_regimes(...)`, `regime_transition_probs(...)`, integrate with `detect_regimes(...)`. Deterministic seeding; explicit feature/window contracts; docstrings.
2. **`backtest/sweep.py`** — Regime-conditioned/per-regime parameter sweeps with walk-forward discipline (accept `regime_labels` and/or per-regime grids).
3. **`backtest/execution.py`** — Regime transition costs/handling consistent with execution model (**no fabricated fills**).
4. **Real-data validation** — Create `examples/run_regime_detection_real.py`; use **real Binance spot candles only** (OOS 2026-11+ where available). **Never fabricate data.** Record `blocked_routes` honestly if a route fails.
5. **Artifact** — Write `reports/regime_adaptive_sweep.json` with per-regime OOS metrics, regime definitions, windows, costs/slippage assumptions, full provenance (`real_data_only: true`, `fabricated_data: false`, timestamps, data source, `blocked_routes` if any).
6. **Evaluation** — Held-out regime-classifier accuracy (target >65%, report honestly if unmet). Check ≥1 regime with positive OOS Sharpe after costs (report honestly with diagnostics if none). **Artifacts required regardless of outcome.**
7. **Gates** — `python -m pytest tests/ -q`, `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `python -m mypy backtest/ strategies/ utils/` must pass. Cointegration gates fail-closed; no lookahead.

**Bottlenecks removed (verified 2026-11-09T08:58:19Z): NONE.** No missing deps, no failing gates, no loader blocker, no parallel handoffs, no uncommitted work, working tree clean. `research_state/state.yaml` tracks a separate locked C248/C249 artifact campaign — **it does not displace Campaign #1 priority and must not be used to avoid heavy implementation work**. **Proceed immediately — no blocker triage, no alternate campaigns.**

**Handoff timestamp (UTC)**: 2026-11-09T08:58:19Z (re-verified)
**Repository**: `cryptoquantstatarbstrats` (Crypto Quantitative Statistical Arbitrage Strategies).
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch/HEAD**: `main @ 5a1a016`
**Single durable handoff rule**: this is the ONLY handoff document for the next session. Do **not** create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes (timestamp, gates, artifacts, blockers, accuracy/Sharpe outcomes).
**Campaign #1 status**: NOT STARTED — heavy implementation work starts now. No blockers.

---

## 1) Verified state (bottlenecks cleared) — re-confirmed 2026-11-09T08:58:19Z

- **Tests**: `928 passed, 1 skipped, 0 failures` (`python -m pytest tests/ -q`).
- **Ruff**: `All checks passed!` across `backtest/ data/ strategies/ utils/ tests/ examples/`.
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`).
- **Dependencies**: `hmmlearn==0.3.3` present in active interpreter; `from utils.regime import detect_regimes` OK; `from hmmlearn.hmm import GaussianHMM` OK.
- **Real data path**: Binance spot fetch works via loader host chain (`www.binance.com`; `api.binance.com` 451 is never relied upon). **Never fabricate data**; report `blocked_routes` honestly when a series cannot be reconstructed.
- **Campaign #1 artifacts missing (expected)**: no `examples/run_regime_detection_real.py`, no `reports/regime_adaptive_sweep.json`.
- **Bottlenecks**: **NONE** (no missing deps, no failing gates, no loader blocker, no stale parallel handoff, no uncommitted WIP).
- **Working tree**: clean on `main` (`5a1a016`), no uncommitted changes.

## 1.1) Parallel-track caution (do not let it block Campaign #1)

`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`) records a locked C104-C248 RQA/volume costed-OOS artifact line with `oos_edge_proven: false`. This is **real repository state** but **not** the next heavy-work priority for this handoff. The next agent must **not** spend the session on C249 registry/status bookkeeping instead of Campaign #1. If C249 work is explicitly requested by the user in a future turn, treat it as a separate request; otherwise ignore it and execute Campaign #1.

## 2) CURRENT GAP vs Campaign #1 (close ALL)

| Area | Current state | Required |
|---|---|---|
| `utils/regime.py` | Quantile-based stub (`volatility_regime`, `trend_detection`, `detect_regimes`) | HMM (`GaussianHMM`), `hmm_regimes(...)`, `regime_transition_probs(...)`, causal fit, no lookahead, deterministic seeding, feature/window contracts |
| `backtest/sweep.py` | Sweeps/walk-forward; no regime conditioning | Accept `regime_labels` and/or per-regime grids; per-regime sweeps with walk-forward discipline |
| `backtest/execution.py` | Fill simulation; no regime transition handling | Regime transition costs/handling consistent with execution model (no fabricated fills) |
| Artifacts | Missing | `examples/run_regime_detection_real.py` (real data only) + `reports/regime_adaptive_sweep.json` (per-regime OOS, provenance) |

**First 10 minutes (mandatory):** 1) `pip install -e ".[dev]"` (if needed), 2) confirm `hmmlearn` import, 3) read `utils/regime.py`, `backtest/sweep.py`, `backtest/execution.py`, 4) start implementing HMM in `utils/regime.py` with tests. No alternate planning phase.

## 3) MANDATORY INITIAL TASK — Campaign #1 (HEAVY WORK, NON-OPTIONAL)

**REGIME-ADAPTIVE SIGNAL GENERATION (CRITICAL PATH).** Do **not** substitute lighter refactors, docs-only edits, cleanup, or exploratory tinkering unless strictly required to unblock Campaign #1 — and if you do, document the unblocker here and return to Campaign #1 immediately.

### Execute in order (do not skip)
1. **`utils/regime.py`** — Implement HMM-based regime detection (e.g., `GaussianHMM` on returns/realized-vol features). **Causal fit only, zero lookahead**. Provide/extend `hmm_regimes(...)`, `regime_transition_probs(...)`, integrate with `detect_regimes(...)`. Deterministic seeding; explicit feature/window contracts; clear docstrings.
2. **`backtest/sweep.py`** — Add regime-conditioned parameter selection: accept `regime_labels` and/or per-regime grids; run parameter sweeps per regime with walk-forward discipline.
3. **`backtest/execution.py`** — Add regime transition costs/handling consistent with the execution model (no fabricated fills).
4. **Validation (real data)** — Run on extended OOS window (2026-11 onward where real Binance candles are available). Create `examples/run_regime_detection_real.py`; it must load **real data only** and emit artifacts.
5. **Artifact** — Write `reports/regime_adaptive_sweep.json` with per-regime OOS metrics, regime definitions, windows, costs/slippage assumptions, and provenance (`real_data_only: true`, `fabricated_data: false`, timestamps, data source, `blocked_routes` if any).

### Acceptance criteria (session incomplete until all true)
- HMM regime detection is causal (no lookahead), tested, and documented.
- `reports/regime_adaptive_sweep.json` exists with per-regime OOS metrics and full provenance.
- Regime classifier evaluated on held-out data; **report accuracy (target > 65%)**. If target not met, document why and iterate — **do not claim success**.
- At least one regime shows **positive OOS Sharpe after costs**; if none, report honestly with diagnostics and propose the next targeted experiment (still produce artifacts).
- `python -m pytest tests/ -q`, `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `python -m mypy backtest/ strategies/ utils/` all pass.

### Rules (non-negotiable)
- ❌ No fabricated data/synthetic results presented as real. Synthetic allowed only in isolated tests explicitly flagged `fabricated_data: true`.
- ❌ Do not weaken cointegration gates (fail-closed).
- ❌ No lookahead in features, labels, regime assignment used for decisions, or walk-forward splits.
- ✅ Walk-forward validation for any new/changed strategy behavior.
- ✅ Keep quality gates green before finishing.
- ✅ Report blockers honestly (`blocked_routes`, rationale) — never guess or fabricate.

---

## 4) Follow-on campaigns (only after Campaign #1 complete + artifacts exist)

1. **Alternative data (HIGH)** — Funding rates (`/fapi/v1/fundingRate` with host handling), L2/order-book features where feasible; basis/carry; unblock `funding_basis_carry` / `intrabar_microstructure` in `data/real_feed_loader.py`. Artifacts: `reports/funding_carry_real.json`, `reports/execution_lob_real.json`.
2. **ML-augmented signal filtering (HIGH)** — Classifier for cointegration persistence (rolling EG p, Johansen trace, half-life, Hurst, spread vol, regime); ML-gated sizing; purged WF CV. Artifact: `reports/ml_gated_pairs.json`.
3. **HF/multi-timeframe (MEDIUM)** — 5m/15m, multi-TF cointegration (1h hedge, 5m signals), seasonality, realistic 5m execution. Artifact: `reports/pairs_mtf_5m_1h.json`.
4. **Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
pip install -e ".[dev]"
python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract for the executing session

- **Start with Campaign #1 immediately.** The repo is unblocked; there is no valid reason to defer heavy work.
- Produce real artifacts with provenance. If a real-data path is blocked, record exact `blocked_routes` and rationale in the artifact/report — do not fabricate.
- When Campaign #1 reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, gates, artifacts, accuracy/Sharpe outcomes, blockers). Keep it the single durable handoff.
