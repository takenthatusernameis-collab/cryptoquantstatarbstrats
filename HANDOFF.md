# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

**Handoff timestamp (UTC)**: 2026-11-09T04:56:53Z
**Repository**: `cryptoquantstatarbstrats` (Crypto Quantitative Statistical Arbitrage Strategies) — repo name implies crypto quant stat arb, so regime-adaptive signal generation is the core edge and takes priority #1.
**Path**: `/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats`
**Branch**: `main` (clean at handoff)
**This file is the single durable handoff for the next session. Do not create parallel handoff docs; update this file if state changes.**

---

## 1) Verified state (gates run at handoff)

- **Tests**: `928 passed, 1 skipped, 0 failures` (`python -m pytest tests/ -x -q`)
- **Ruff**: clean across `backtest/ data/ strategies/ utils/ tests/ examples/`
- **mypy**: `Success: no issues found in 32 source files` (`backtest/ strategies/ utils/`)
- **Environment**: `hmmlearn==0.3.3` installed into active interpreter. Real Binance spot data fetches succeed via the loader host chain (`www.binance.com` first; `api.binance.com` returns HTTP 451 and is never relied upon). Verified: `DataLoader().load_binance_data(['BTC','ETH','SOL'], '2026-10-01', '2026-11-08', '1h')` returns 936 rows with empty `blocked_routes`. Never fabricate data; report `blocked_routes` honestly when a series cannot be reconstructed.
- **Bottlenecks**: RESOLVED. No missing dependencies, no network blocker on the public spot loader, no failing gates. The next session can start heavy work immediately.
- **Repo context**: Real-market research framework (public Binance spot candles, no API keys, no fabricated data). Static strategies underperform buy-and-hold OOS on real data; cost sensitivity is high; cointegration gates are fail-closed.

## 2) CURRENT GAP vs Campaign #1 (must be closed this session)

- `utils/regime.py` exists but is only a **quantile-based stub** (`volatility_regime`, `trend_detection`, `detect_regimes`). There is **no HMM** (`GaussianHMM`), no `hmm_regimes(...)`, no `regime_transition_probs(...)`, no causal fit, no lookahead guard.
- `backtest/sweep.py` has `run_parameter_sweep`/`engine_walk_forward` but **no regime-conditioned parameter selection** (no `regime_labels`/per-regime grids).
- `backtest/execution.py` has fill simulation but **no regime transition costs/handling**.
- `reports/regime_adaptive_sweep.json` **does not exist**.
- `examples/run_regime_detection_real.py` **does not exist**.

## 3) MANDATORY INITIAL TASK (do this first; heavy work, non-optional)

**Campaign #1 — REGIME-ADAPTIVE SIGNAL GENERATION (CRITICAL PATH)**

**Objective**: Replace static parameter behavior with regime-conditioned, causally fit signal/parameter selection validated out-of-sample with full provenance.

**Execute in order (do not skip steps):**

1. **`utils/regime.py`** — Implement HMM-based regime detection (e.g., `GaussianHMM` on returns/realized-vol features). **Causal fit only, no lookahead**. Provide/extend APIs such as `hmm_regimes(...)`, `regime_transition_probs(...)`, and integrate with `detect_regimes(...)`. Deterministic seeding; clear feature/window contracts.
2. **`backtest/sweep.py`** — Add regime-conditioned parameter selection: accept `regime_labels` and/or per-regime grids; run parameter sweeps per regime with walk-forward discipline.
3. **`backtest/execution.py`** — Add regime transition costs/handling consistent with the execution model (no fabricated fills).
4. **Validation** — Run on extended OOS window (2026-11 onward where real Binance candles are available). Create `examples/run_regime_detection_real.py` (or equivalent); it must load real data only and emit artifacts.
5. **Artifact** — Write `reports/regime_adaptive_sweep.json` with per-regime OOS metrics, regime definitions, windows, costs/slippage assumptions, and provenance (`real_data_only: true`, `fabricated_data: false`, timestamps, data source).

**Acceptance criteria (session incomplete until all true):**
- HMM regime detection in `utils/regime.py` is causal (no lookahead), tested, and documented in code/docstrings.
- `reports/regime_adaptive_sweep.json` exists with per-regime OOS metrics and full provenance.
- Regime classifier evaluated on held-out data; report accuracy (target **> 65%**). If target not met, document why and iterate — do not claim success.
- At least one regime shows **positive OOS Sharpe after costs**; if none, report honestly with diagnostics and propose next targeted experiment (still produce artifacts).
- `python -m pytest tests/ -q`, `python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `python -m mypy backtest/ strategies/ utils/` all pass.

**Rules (non-negotiable):**
- ❌ No fabricated data/synthetic results presented as real. Synthetic allowed only in isolated tests explicitly flagged `fabricated_data: true`.
- ❌ Do not weaken cointegration gates (fail-closed).
- ❌ No lookahead in features, labels, regime assignment used for decisions, or walk-forward splits.
- ✅ Walk-forward validation for any new/changed strategy behavior.
- ✅ Keep quality gates green before finishing.

---

## 4) Follow-on campaigns (after Campaign #1 is complete)

1. **Alternative data (HIGH)** — Funding rates (`/fapi/v1/fundingRate` via appropriate host handling), L2/order-book features where feasible; basis/carry; unblock `funding_basis_carry` / `intrabar_microstructure` in `data/real_feed_loader.py`. Artifacts: `reports/funding_carry_real.json`, `reports/execution_lob_real.json`.
2. **ML-augmented signal filtering (HIGH)** — Classifier for cointegration persistence (rolling EG p, Johansen trace, half-life, Hurst, spread vol, regime); ML-gated sizing; purged WF CV. Artifact: `reports/ml_gated_pairs.json`.
3. **HF/multi-timeframe (MEDIUM)** — 5m/15m, multi-TF cointegration (1h hedge, 5m signals), seasonality, realistic 5m execution. Artifact: `reports/pairs_mtf_5m_1h.json`.
4. **Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py`.

---

## 5) Reproduction commands

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

---

## 6) Handoff contract for the executing session

- Start with **Campaign #1** immediately. Do not substitute lighter refactors/docs-only work unless required to unblock Campaign #1 (and document why).
- Produce real artifacts with provenance. Report blockers honestly (`blocked_routes`, rationale) if data/access prevents completion.
- Update this `HANDOFF.md` only to reflect materially changed truth (new timestamp, gate results, completed artifacts, new blockers). Keep it the single durable handoff.
