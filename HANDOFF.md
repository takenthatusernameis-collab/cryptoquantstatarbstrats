# SINGLE DURABLE HANDOFF | 2026-11-01T12:50:00Z | CAMPAIGN 5 READY — DIFFERENT-WINDOW OOS v2 + THRESHOLD LOCK-IN

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## CURRENT VERIFIED STATE (2026-11-01T12:50:00Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `415900a` (chore(kilo): checkpoint agent session).
- Campaign 3 + 4 artifacts present: `examples/run_cointegration_diagnostics_oos.py`, `examples/run_cointegration_diagnostics_oos_full.py`, `reports/cointegration_diagnostics_oos.json`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **Campaign 4 DONE:** OOS re-validation on cached window (`2026-04-01`→`2026-10-30`, split) shows **0/17 pass all gates**. `POL/BTC` blocked solely on `rolling_stable_ok=False`; all other gates pass. Blocking confirmed window-robust from prior runs.
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` — **21 passed**.
- **Ruff:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` — **clean**.

## BOTTLENECKS (REMOVED/MITIGATED)
1. **Ruff E501** — fixed in `examples/run_cointegration_diagnostics_oos.py`. Clean.
2. **OOS signal** — 0/17 all-pass is established; no regen dependency. Do **not** wait on `run_portfolio_real.py`.
3. **Network** — offline-capable via `data/cache/` (real public Binance 1h). `www.binance.com` preferred.
4. **Test scope** — use targeted tests for schema/gates (full suite slow).
5. **Handoff friction** — this single handoff is the only starting instruction.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 5 — HEAVY, NON-OPTIONAL):** Prove blocking is not cache/window-specific, lock thresholds against weakening, and harden provenance/tests. Do not coast.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **Different-window OOS v2 (HIGHEST ROI):** Create `examples/run_cointegration_diagnostics_oos_v2.py` that runs `target_schema_diagnostics` on a **genuinely different real window** from `data/cache/` (e.g. earlier slice: first 20-30% of cached series, or split by time before mid-window). Use only cached real data. Produce `reports/cointegration_diagnostics_oos_v2.json` with full provenance (`source`, `real_data_only`, `fabricated_data`, `computed_at`, `blocked_routes`). **Assert/record:** expect **0/17 pass all gates**. Explicitly confirm `POL/BTC` blocked solely on `rolling_stable_ok`. No threshold changes.
2. **Threshold-invariance lock-in:** Add tests (e.g. `tests/test_cointegration_threshold_invariance.py`) that pin near-miss values for all 17 pairs from both `cointegration_diagnostics_real.json` and `cointegration_diagnostics_oos.json` (and later v2) — `eg_pvalue`, `spread_adf_pvalue`, `half_life_ou`, `hurst_exponent`, `rolling_frac_stable` vs required (>=0.6), `leg_adf_pvalues`, etc. Any change that weakens gates must fail tests. Ensure `blocked_routes` non-empty for failing pairs.
3. **Rolling stability deep-dive (targeted):** For pairs near boundary (focus `POL/BTC`, scan others), log `rolling_frac_stable` distribution and window counts to `reports/pol_btc_rolling_stability_deepdive.json` (or append to existing). Keep causal/trailing only.
4. **Portfolio hygiene (cheap only):** If regenerating `reports/portfolio_real.json` is cheap with cached data and doesn't risk fabrication/network, do it; else document rationale in a short note and leave as-is.
5. **Verify & record:** Run schema tests + ruff. Update this handoff only if new hard blockers found (do not rewrite the mission).

**FOCUS CAMPAIGNS**
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (IN PROGRESS/NEXT): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (BACKLOG): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — diagnostics schema tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — produce artifacts/tests/logs. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py -q
```

**START NOW.** Execute Campaign 5 in order. Do not wait for non-running regen.
