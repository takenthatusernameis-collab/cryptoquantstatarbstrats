# SINGLE DURABLE HANDOFF | 2026-11-01T13:20:51Z | CAMPAIGN 5 DONE — CAMPAIGN 6 NEXT (MULTI-TIMEFRAME + STRUCTURAL BREAK)

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## CURRENT VERIFIED STATE (2026-11-01T13:20:51Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `b921062` (chore(kilo): checkpoint agent session). Working tree clean.
- **Campaign 5 DONE:**
  1. `examples/run_cointegration_diagnostics_oos_v2.py` — different real window (middle slice 0.25–0.65 of cached `data/cache/`). Produced `reports/cointegration_diagnostics_oos_v2.json` (0/17 all gates pass; `POL/BTC` blocked on `rolling_stable_ok=False` plus EG/johansen/spread_mr/structural-break). Full provenance present. `computed_at` 2026-11-01T12:38:40Z+.
  2. `tests/test_cointegration_threshold_invariance.py` — pins near-miss metrics (`eg_pvalue`, `spread_adf_pvalue`, `half_life_ou`, `hurst_exponent`, `rolling_frac_stable` vs >=0.6, leg ADF pvalues) across `cointegration_diagnostics_real.json`, `_oos.json`, `_oos_v2.json`. Blocked routes non-empty for failing pairs. Any gate weakening fails tests.
  3. `reports/pol_btc_rolling_stability_deepdive.json` — `POL/BTC` rolling stability deep-dive (causal/trailing only) across `POL/BTC`, `DOT/BTC`, `LINK/BTC`, `AVAX/BTC`, `LTC/BTC`.
  4. Portfolio hygiene: `reports/portfolio_real.json` present; regen skipped/documented as-is (cached-data regen would not change blocked status).
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` + `tests/test_cointegration_threshold_invariance.py` — **24 passed**.
- **Ruff:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/` — **clean**.
- Data: `data/cache/` holds real Binance spot 1h (2026-04-01→2026-10-30) for 12 symbols (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP). Offline-capable; no network required for resampled 4h/1d work.

## BOTTLENECKS (ALL REMOVED / MITIGATED — NONE REMAINING)
1. Ruff E501 — fixed, clean.
2. OOS signal — 0/17 all-pass established across three windows; no regen dependency.
3. Network — offline via `data/cache/` (real public Binance 1h); `www.binance.com` preferred when available.
4. Test scope — targeted schema/gates/threshold tests green; full suite slow but not required.
5. Handoff friction — this single handoff is the only starting instruction.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 6 — HEAVY, NON-OPTIONAL):** Multi-timeframe (4h/1d) rolling cointegration stability + structural-break re-validation across all 17 pairs, causal/trailing only, real cached data. Prove blocking is timeframe-robust (not 1h-specific), lock thresholds, harden provenance/tests. Do not coast.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **Multi-timeframe OOS diagnostics (HIGHEST ROI):** Create `examples/run_cointegration_diagnostics_oos_mt.py` that resamples cached 1h `data/cache/` into **4h** and **1d** (causal trailing resample — `resample("4h").last()`/`.ohlc()` close, no lookahead) and runs `target_schema_diagnostics` on all 17 pairs for each timeframe. Produce `reports/cointegration_diagnostics_oos_mt_4h.json` and `reports/cointegration_diagnostics_oos_mt_1d.json` with full provenance (`source`, `real_data_only`, `fabricated_data`, `computed_at`, `timeframe`, `blocked_routes`). **Assert/record:** expect **0/17 pass all gates** on both timeframes. Confirm `POL/BTC` remains blocked solely on `rolling_stable_ok` (and EG/johansen/spread_mr as applicable). No threshold changes.
2. **Structural-break re-validation across all pairs:** Extend step 1 to emit `structural_breaks.flagged` + `relative_change` per pair per timeframe into the mt reports; log pairs flagged for structural break to `reports/mt_structural_breaks_summary.json`. Causal half-sample Chow heuristic only (trailing windows).
3. **Threshold-invariance extension:** Add `reports/cointegration_diagnostics_oos_mt_4h.json` and `_1d.json` to `tests/test_cointegration_threshold_invariance.py` REPORTS list so near-miss metrics are pinned across timeframes. Any threshold weakening on 4h/1d must fail tests.
4. **Cross-timeframe blocking matrix:** Produce `reports/mt_blocking_matrix.json` — per-pair × per-timeframe (1h/4h/1d) `all_pass`, `blocked_routes`, `rolling_frac_stable`, `structural_breaks.flagged`. Confirm no pair passes all gates on any timeframe (honest blocking preserved).
5. **Verify & record:** Run schema tests + threshold-invariance tests + ruff. Update this handoff only if new hard blockers found (do not rewrite the mission).

## FOCUS CAMPAIGNS
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (NEXT/ACTIVE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs
- Campaign 7 (BACKLOG): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation on mt timeframes

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data); no synthetic substitution.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — diagnostics schema tests green; threshold-invariance tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only. Resample must not use future bars.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — produce artifacts/tests/logs. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py -q
```

**START NOW.** Execute Campaign 6 in order. Do not wait for non-running regen.
