# SINGLE DURABLE HANDOFF | 2026-11-01T11:35:03Z | CAMPAIGN 3 COMPLETE — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree currently has uncommitted Campaign 3 changes (reports/, tests/, examples/, scripts/). **Do not commit unless explicitly requested.**

## CURRENT VERIFIED STATE (2026-11-01T11:35:03Z)
- Branch: `main`. Up to date with `origin/main`; Campaign 3 changes are uncommitted.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **Campaign 1 DONE:** `reports/cointegration_diagnostics_real.json` (real cached 1h Binance candles, 2026-04-01 to 2026-10-30, 5112 bars, 11 symbols). All 17 pairs diagnosed; **0/17 pass all gates.**
- **Campaign 2 DONE (POL/BTC):** `reports/pol_btc_regime_analysis.json`. EG p=5.79e-4, Johansen pass, spread ADF strong, HL~108h, Hurst~0.498. Rolling stability 9/184 (frac 0.0489). **Blocked only on `rolling_stability`.** No causal filter added; thresholds not weakened.
- **Campaign 3 DONE:** Honest blocking audit + evidence lock-in + near-miss re-examination.
  - `reports/pol_btc_deep_dive.json` written: trailing-only causal filter evaluation on cached data. Best filter `hl_lt_30` → precision 0.417 / recall 0.556 (7 FP, 4 FN). **No trailing-only causal filter robustly isolates the 9 passing windows;** POL/BTC stays blocked solely on `rolling_stability`. Passing windows show hurst mean 0.508 (not even mean-reverting on average) → temporal instability confirmed.
  - `reports/cointegration_diagnostics_real.json` updated: every pair has non-empty `blocked_routes[]` + rationale + `near_miss_audit` (eg_pvalue, spread_adf_pvalue, half_life_ou, hurst_exponent, rolling_frac vs 0.6 required, `near_miss_gates`). Near-misses documented numerically: LTC/BTC spread_adf_p=0.0592 + eg_p=0.168; SOL/BNB spread_adf_p=0.071 + rs_frac=0.022; XRP/BTC spread_adf_p=0.080; AVAX/BTC rs_frac=0.370 (high but < 0.6); BTC/BNB hl=498.5 + LINK/BTC hl=475.6 (near 500 bound); BTC/ETH joh_pass=True but eg_p=0.519 + rs_frac=0.185. **No fabrication; no threshold weakening.**
  - `tests/test_cointegration_diagnostics_schema.py`: +6 tests (21 total), all pass. New: near_miss_audit present for all pairs, rolling frac < 0.6 for all pairs (honest blocking), thresholds not weakened, near-miss pairs documented, POL/BTC deep_dive locked, blocked_routes non-empty for all failing pairs.
  - `examples/pol_btc_deep_dive.py`, `scripts/lock_near_miss_audit.py` added (reproducible from cached data only).
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` 21 tests, all pass. `ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` clean.
- **Bottlenecks:** `reports/portfolio_real.json` stale (~664KB); `reports/.portfolio_real_checkpoint.json` empty; no regen running. **Do not wait for regen.** Full `pytest` >5min — use targeted tests only.

## BOTTLENECKS REMOVED / MITIGATED
1. **Regen not running** — ignore `run_portfolio_real.py`; use `reports/cointegration_diagnostics_real.json` as source of truth.
2. **Diagnostics incomplete** — complete for all 17 pairs with schema/provenance/blocked_routes/near_miss_audit enforced by tests.
3. **Network dependence** — offline via `data/cache/` (real public Binance data).
4. **Test slowness** — targeted invocation only; full suite >5min is a known bottleneck for Campaign 4.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 4 — HEAVY, NON-OPTIONAL):** Out-of-sample robustness re-validation of the blocking decision + iteration-speed bottleneck removal, then commit Campaign 3/4 artifacts.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **Out-of-sample re-validation (HIGHEST ROI):** Re-run `target_schema_diagnostics`/`rolling_cointegration_stability` on a **different real Binance window** (e.g. pre-2026-04-01 cached history or 2026-01-01 to 2026-03-31) for all 17 pairs using cached data only. Confirm **0/17 pass all gates on the OOS window too** (blocking is not window-specific). Confirm POL/BTC remains blocked solely on `rolling_stability` on OOS. Produce `reports/cointegration_diagnostics_oos.json`. No fabrication; no threshold weakening.
2. **Bottleneck removal / iteration speed:** Profile why full `pytest` >5min (real-series cointegration diagnostics are expensive). Optimize the slowest tests without weakening coverage; keep the targeted-test workflow (`tests/test_cointegration_diagnostics_schema.py` only). Fix/refresh `reports/portfolio_real.json` only if a cheap real-data path exists; otherwise keep stale and document.
3. **Commit:** Commit Campaign 3 + Campaign 4 artifacts (`reports/`, `examples/`, `scripts/`, `tests/`) **only if explicitly requested.** Do not commit secrets.
4. **Verify:** `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (21 passed); `python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` (clean).

**FOCUS CAMPAIGNS**
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data).
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter evaluation (kept blocked).
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-examination.
- Campaign 4 (NEXT - HEAVY): OOS robustness re-validation + bottleneck removal + commit.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — diagnostics schema tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Any regime filter must be trailing-only with tests.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — do the work. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py -q
```

**START NOW.** Prioritize OOS re-validation to confirm blocking is window-robust, then remove bottlenecks. All Campaign 3 changes are currently uncommitted — commit only if explicitly requested. Do not wait on non-running regen.
