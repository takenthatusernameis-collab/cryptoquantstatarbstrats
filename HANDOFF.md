# SINGLE DURABLE HANDOFF | 2026-11-01T11:30:45Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T11:30:45Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **Campaign 1 DONE:** `reports/cointegration_diagnostics_real.json` written via real cached 1h Binance candles (2026-04-01 to 2026-10-30, 5112 bars, 11 symbols). All 17 pairs diagnosed with full gates + `blocked_routes[]` + rationale + provenance. **0/17 pass all gates.**
- **Campaign 2 DONE (POL/BTC):** `reports/pol_btc_regime_analysis.json` (2026-11-01T09:47:58Z). EG p=5.79e-4, Johansen pass, spread ADF strong, KPSS spread p=0.1, HL~108h, Hurst~0.498. Rolling stability: 9/184 windows pass (frac 0.0489), scattered with no robust causal trailing-only boundary. **Conclusion: temporally unstable → blocked only on `rolling_stability`.** No causal filter added; do not weaken thresholds.
- **Bottlenecks:** `reports/portfolio_real.json` stale (~664KB), `reports/.portfolio_real_checkpoint.json` empty (0 bytes), no regen running. **Do not wait for regen.** Full `pytest` >5min — use targeted tests only.
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` has 15 tests, all pass. `ruff check backtest/ strategies/ utils/ tests/ examples/` clean.

## BOTTLENECKS REMOVED / MITIGATED
1. **Regen not running** — ignore `run_portfolio_real.py`; use `reports/cointegration_diagnostics_real.json` as source of truth.
2. **Diagnostics incomplete** — complete for all 17 pairs with schema/provenance/blocked_routes enforced by tests.
3. **Network dependence** — offline via `data/cache/` (real public Binance data).
4. **Test slowness** — targeted invocation only.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 3 — HEAVY, NON-OPTIONAL):** Close cointegration rigor loop via **Honest blocking audit + evidence lock-in + near-miss re-examination**. Produce artifacts and lock-in with tests.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **Load facts (immediate):** Read `reports/cointegration_diagnostics_real.json` fully. Read `reports/pol_btc_regime_analysis.json`. Read `strategies/pairs_trading.py` (enriched gates, fail-closed). Read `utils/cointegration.py` (target_schema_diagnostics, rolling_stability, EG/Johansen). Note POL/BTC passing windows: start_bars [168,1536,1560,2736,2856,2880,2904,3528,4368], n_windows=184, frac=0.0489.
2. **POL/BTC deep dive (HIGHEST ROI):** Analyze passing vs failing windows - rolling OLS hedge ratio stability (mean/var), spread behavior, volatility/regime, correlation. **Prove causality** for any regime definition (trailing-only, no lookahead). Test candidate trailing-only filters on cached data only. **DECIDE FATE:** (a) If viable with trailing-only causal no-lookahead filter AND provably robust with tests (no threshold weakening) → add to `strategies/pairs_trading.py` with explicit no-lookahead tests, update gates/schema/tests. (b) Else → keep `blocked_or_insufficient_data` only on `rolling_stability` with expanded provenance in the diagnostic artifact explaining instability with concrete numbers. Do NOT weaken `rolling_stability`.
3. **Near-miss audit (all 16 others):** For each blocked pair extract EG p-value, Johansen, spread ADF/KPSS, half-life, `rolling_stability.frac_significant`, Hurst, failing routes. Identify near-misses numerically (EG borderline, rolling_stability high frac but < required, HL at edge). Document concretely. **NO threshold weakening.**
4. **Evidence lock-in:** Ensure every pair has non-empty `blocked_routes[]` with rationale + provenance. If schema needs hardening to prevent regression, add/strengthen tests. Regenerate/update `reports/cointegration_diagnostics_real.json` only if adding evidence/provenance; do not fabricate data.
5. **Verify:** `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (15 passed), `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` (clean). Commit artifacts only if explicitly requested.

**FOCUS CAMPAIGNS**
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data).
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter evaluation (kept blocked).
- Campaign 3 (NEXT - HEAVY): Honest blocking audit + evidence lock-in + near-miss re-examination.
- Campaign 4 (ONGOING): Bottleneck removal/iteration speed - use targeted tests/scripts; preserve schema.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — diagnostics schema tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Any regime filter must be trailing-only with tests.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — do the work. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py -q
```

**START NOW.** Prioritize POL/BTC deep dive (causal trailing-only filter attempt OR evidence-backed keep-blocked) and complete near-miss audit for all pairs. Do not wait on non-running regen.
