# SINGLE DURABLE HANDOFF | 2026-11-01T12:45:00Z | CAMPAIGN 4 OOS DONE — INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean except one unstaged ruff fix (see Bottlenecks). **Do not commit unless explicitly requested.**

## CURRENT VERIFIED STATE (2026-11-01T12:45:00Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `415900a chore(kilo): checkpoint agent session` (12:31:51Z).
- Campaign 3 + Campaign 4 artifacts committed: `examples/run_cointegration_diagnostics_oos.py`, `examples/run_cointegration_diagnostics_oos_full.py`, `reports/cointegration_diagnostics_oos.json`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **Campaign 4 STEP 1 (OOS re-validation) DONE:** `reports/cointegration_diagnostics_oos.json` computed `2026-11-01T12:25:18.604905+00:00` on a different real Binance window (cached data only). **0/17 pass all gates.** POL/BTC blocked solely on `rolling_stability` (rolling_stable_ok=False; eg/johansen/spread_mr/hl/leg all True). Blocking confirmed window-robust, not window-specific. No fabrication; no threshold weakening.
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` 21 tests, all pass (1.53s).
- **Ruff:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` **clean** (E501 in `examples/run_cointegration_diagnostics_oos.py:100` fixed — see Bottlenecks).

## BOTTLENECKS REMOVED / MITIGATED
1. **Ruff E501 (REMOVED):** `examples/run_cointegration_diagnostics_oos.py:100` line too long (102 > 100). Fixed by wrapping `oos_window` dict across multiple lines. Change is **unstaged** — commit only if explicitly requested.
2. **OOS re-validation (DONE):** 0/17 pass on OOS window; POL/BTC blocked solely on `rolling_stability`. Blocking is window-robust.
3. **Regen not running** — ignore `run_portfolio_real.py`; use `reports/cointegration_diagnostics_real.json` + `_oos.json` as source of truth. **Do not wait for regen.**
4. **Diagnostics complete** — all 17 pairs have schema/provenance/blocked_routes/near_miss_audit enforced by tests (real + OOS).
5. **Network dependence** — offline via `data/cache/` (real public Binance data, 2026-04-01 to 2026-10-30, 11 symbols).
6. **Test slowness** — targeted invocation only; full suite >5min is a known bottleneck for Campaign 5.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 5 — HEAVY, NON-OPTIONAL):** Extend OOS robustness to a genuinely different real window + threshold-invariance lock-in + commit Campaign 4/5 artifacts, then define Campaign 6.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **OOS robustness on a different real window (HIGHEST ROI):** Re-run `target_schema_diagnostics`/`rolling_cointegration_stability` on a **genuinely different real Binance window** for all 17 pairs (pre-2026-04-01 cached history if present, else fetch pre-2026-04-01 via `www.binance.com`; cached data only preferred). Confirm **0/17 pass all gates** on this window too (blocking is not window- or cache-specific). Confirm POL/BTC remains blocked solely on `rolling_stability`. Produce `reports/cointegration_diagnostics_oos_v2.json`. No fabrication; no threshold weakening.
2. **Threshold-invariance / near-miss lock-in:** Add tests that pin all 17 near-miss gate values (eg_pvalue, spread_adf_pvalue, half_life_ou, hurst_exponent, rolling_frac vs 0.6 required) so no future change can quietly weaken thresholds without a test failure. Keep `blocked_routes` non-empty for all failing pairs.
3. **Stale portfolio refresh (only if cheap):** `reports/portfolio_real.json` is stale (~664KB). Refresh only if a cheap real-data path exists; otherwise document why and leave stale.
4. **Commit:** Commit the unstaged ruff fix + Campaign 4/5 artifacts (`reports/`, `examples/`, `scripts/`, `tests/`) **only if explicitly requested.** Do not commit secrets.
5. **Verify:** `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (21 passed); `python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` (clean).

**FOCUS CAMPAIGNS**
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data).
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter evaluation (kept blocked).
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-examination.
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal.
- Campaign 5 (NEXT - HEAVY): Different-window OOS v2 + threshold-invariance lock-in + portfolio refresh + commit.
- Campaign 6 (BACKLOG): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs.

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

**START NOW.** Prioritize different-window OOS v2 to confirm blocking is not cache/window-specific, then lock thresholds with tests. The unstaged ruff fix must be committed only if explicitly requested. Do not wait on non-running regen.
