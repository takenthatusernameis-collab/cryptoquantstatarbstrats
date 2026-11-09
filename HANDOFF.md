# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

**Handoff timestamp (UTC)**: 2026-11-09T05:03:26Z
**Repository**: `cryptoquantstatarbstrats` (Crypto Quantitative Statistical Arbitrage Strategies). Repo-name priority: crypto quant stat arb — **regime-adaptive signal generation is the #1 critical path**.
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch**: `main`
**Single durable handoff rule**: this is the ONLY handoff document for the next session. Do **not** create parallel handoff docs, summary notes, or alternate TODOs. Update this file in place only when materially verified state changes (timestamp, gates, artifacts, blockers).

---

## 1) Verified state at this handoff (bottlenecks cleared)

- **Tests**: `928 passed, 1 skipped, 0 failures` (`python -m pytest tests/ -x -q`, 2026-11-09).
- **Ruff**: `All checks passed!` across `backtest/ data/ strategies/ utils/ tests/ examples/`.
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`).
- **Dependencies**: `hmmlearn==0.3.3` present in active interpreter.
- **Real data path**: Binance spot fetch works via loader host chain (`www.binance.com`; `api.binance.com` 451 is never relied upon). Smoke: `DataLoader().load_binance_data(['BTC'], '2026-10-01', '2026-10-02', '1h')` returned 48 rows. **Never fabricate data**; report `blocked_routes` honestly when a series cannot be reconstructed.
- **Bottlenecks**: **NONE** (no missing deps, no failing gates, no loader blocker). Heavy implementation work can start immediately.
- **Research context**: Real-market framework (public Binance spot candles, no API keys). Static strategies underperform buy-and-hold OOS; cost sensitivity is high; cointegration gates are fail-closed — do not weaken.

## 2) CURRENT GAP vs Campaign #1 (work NOT done — next session must close it)

- `utils/regime.py` is a **quantile-based stub** (`volatility_regime`, `trend_detection`, `detect_regimes`). **Missing**: HMM (`GaussianHMM`), `hmm_regimes(...)`, `regime_transition_probs(...)`, causal fit contract, lookahead guard, deterministic seeding.
- `backtest/sweep.py` has sweeps/walk-forward but **no regime-conditioned parameter selection** (`regime_labels` / per-regime grids).
- `backtest/execution.py` has fill simulation but **no regime transition costs/handling**.
- **Missing artifacts**: `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`.

## 3) MANDATORY INITIAL TASK — Campaign #1 (HEAVY WORK, NON-OPTIONAL)

**REGIME-ADAPTIVE SIGNAL GENERATION (CRITICAL PATH).** This is the session's focus. Do **not** substitute lighter refactors, docs-only edits, cleanup, or exploratory tinkering unless strictly required to unblock Campaign #1 — and if you do, document the unblocker in this file and return to Campaign #1 immediately.

### Objective
Replace static parameter behavior with regime-conditioned, causally fit signal/parameter selection validated out-of-sample with full provenance.

### Execute in order (do not skip)
1. **`utils/regime.py`** — Implement HMM-based regime detection (e.g., `GaussianHMM` on returns/realized-vol features). **Causal fit only, zero lookahead**. Provide/extend `hmm_regimes(...)`, `regime_transition_probs(...)`, integrate with `detect_regimes(...)`. Deterministic seeding; explicit feature/window contracts; clear docstrings.
2. **`backtest/sweep.py`** — Add regime-conditioned parameter selection: accept `regime_labels` and/or per-regime grids; run parameter sweeps per regime with walk-forward discipline.
3. **`backtest/execution.py`** — Add regime transition costs/handling consistent with the execution model (no fabricated fills).
4. **Validation (real data)** — Run on extended OOS window (2026-11 onward where real Binance candles are available). Create `examples/run_regime_detection_real.py`; it must load **real data only** and emit artifacts.
5. **Artifact** — Write `reports/regime_adaptive_sweep.json` with per-regime OOS metrics, regime definitions, windows, costs/slippage assumptions, and provenance (`real_data_only: true`, `fabricated_data: false`, timestamps, data source, `blocked_routes` if any).

### Acceptance criteria (session is incomplete until all true)
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

## 4) Follow-on campaigns (only after Campaign #1 is complete and artifacts exist)

1. **Alternative data (HIGH)** — Funding rates (`/fapi/v1/fundingRate` with appropriate host handling), L2/order-book features where feasible; basis/carry; unblock `funding_basis_carry` / `intrabar_microstructure` in `data/real_feed_loader.py`. Artifacts: `reports/funding_carry_real.json`, `reports/execution_lob_real.json`.
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
python examples/run_pairs_multi.py
python examples/run_mean_reversion_real.py
python examples/run_portfolio_real.py
```

## 6) Handoff contract for the executing session

- **Start with Campaign #1 immediately.** The repo is unblocked; there is no valid reason to defer heavy work.
- Produce real artifacts with provenance. If a real-data path is blocked, record exact `blocked_routes` and rationale in the artifact/report — do not fabricate.
- When Campaign #1 reaches a material checkpoint or completes, update **only** `HANDOFF.md` with verified truth (timestamp, gates, artifacts, accuracy/Sharpe outcomes, blockers). Keep it the single durable handoff.
