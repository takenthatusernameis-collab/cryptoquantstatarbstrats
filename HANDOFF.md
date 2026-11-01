# SINGLE DURABLE HANDOFF | 2026-11-01T11:29:13Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T11:29:13Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **Campaign 1 DONE:** `reports/cointegration_diagnostics_real.json` written via `examples/run_cointegration_diagnostics_real.py`. Real cached 1h Binance candles (2026-04-01 to 2026-10-30, 5112 bars, all 11 symbols) — no network used. All 17 pairs diagnosed with full gates + `blocked_routes[]` + rationale + provenance.
- **Campaign 2 DONE (POL/BTC):** Analyzed in `reports/pol_btc_regime_analysis.json` (computed 2026-11-01T09:47:58Z, real cached data). POL/BTC shows EG p-value 5.79e-4, Johansen pass, spread ADF very significant (p~8.65e-5), KPSS spread p=0.1, half-life ~108h, Hurst ~0.498. Rolling stability: 9/184 windows pass (frac 0.0489), scattered with no robust causal trailing-only boundary. **Conclusion: temporally unstable → keep `blocked_or_insufficient_data` only on `rolling_stability`.** Do NOT weaken thresholds. No causal filter added.
- **All other 16 pairs:** honestly `blocked_or_insufficient_data`. Every fails at least EG or other gates; none pass all gates. Non-empty `blocked_routes[]` recorded with rationale + provenance.
- `reports/portfolio_real.json` (~664KB) is stale; authoritative recompute is `reports/cointegration_diagnostics_real.json`.
- `reports/.portfolio_real_checkpoint.json` is 0 bytes (empty). No active regen process. **Do not wait for regen.**
- **Tests:** `tests/test_cointegration_diagnostics_schema.py` has 15 tests covering schema/provenance/honest-blocking; all pass. `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` is clean.
- **Bottleneck:** full `pytest tests/` > 5 min (some tests slow). Use targeted invocation.

## BOTTLENECKS REMOVED / MITIGATED
1. **Regen not running** — do not wait/resume `run_portfolio_real.py`. Use targeted diagnostics.
2. **Empty/missing diagnostics** — `reports/cointegration_diagnostics_real.json` complete with full schema, provenance, blocked_routes for all 17 pairs. Enforced by tests.
3. **Network dependence** — `DataLoader.fetch_with_provenance(use_cache=True)` uses `data/cache/`; diagnostics run offline.
4. **Test slowness** — use targeted tests: `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (~1.5s). Only expand scope if necessary.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE:** Close cointegration rigor loop via **Campaign 3: Honest blocking audit + evidence lock-in + near-miss re-examination**. Campaigns 1 & 2 complete. POL/BTC is blocked only on `rolling_stability` (9/184 scattered windows) — must decide fate with evidence: either find a **trailing-only, causal, no-lookahead** regime filter (with tests proving no lookahead, integrate into gates) OR keep blocked with full provenance. All 17 pairs must have non-empty `blocked_routes[]` + rationale + provenance locked by tests.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **Load facts** — Read `reports/cointegration_diagnostics_real.json` fully for all pairs (focus POL/BTC rolling_stability details: passing window start bars 168,1536,1560,2736,2856,2880,2904,3528,4368; n_windows=184, step=24). Read `reports/pol_btc_regime_analysis.json`. Read `strategies/pairs_trading.py` (enriched gates, fail-closed). Read `utils/cointegration.py` (target_schema_diagnostics, rolling_stability, EG/Johansen).
2. **POL/BTC deep dive (HIGHEST ROI)** — Analyze passing vs failing windows: rolling OLS hedge ratio stability (coefficient mean/var over passing vs failing), spread behavior (mean/reversion), volatility/regime, correlation, ADF/KPSS of spread per regime. Quantify with numbers. **Prove causality** for any regime definition (trailing-only, no lookahead). Test proposed filter on cached data only.
3. **Decide POL/BTC fate** —
   - If viable with trailing-only causal no-lookahead filter: add to `strategies/pairs_trading.py` with explicit no-lookahead tests, update gates/schema/tests, verify only trades in passing regimes. Must not weaken existing thresholds.
   - If not viable / temporally unstable: keep `blocked_or_insufficient_data` only on `rolling_stability` with expanded provenance explaining instability + evidence. Do NOT weaken `rolling_stability`.
4. **Near-miss audit (all 16 others)** — For each blocked pair, extract EG p-value, Johansen, spread ADF/KPSS, half-life, `rolling_stability.frac_significant`, Hurst, and failing routes. Identify near-misses numerically (e.g. EG borderline p>0.05 but close; rolling stability high frac but < required; half-life at edge). Document; no threshold weakening.
5. **Lock-in & verify** — Ensure all blocked pairs have non-empty `blocked_routes[]` + rationale + provenance. Run `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (expect green) and `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` (expect clean). Add/update tests if schema needs hardening.

## FOCUS CAMPAIGN (HEAVY WORK REQUIRED — NON-OPTIONAL)
Future agents must not avoid this. Produce artifacts at each step.

### Campaign 1: Cointegration diagnostics recompute (real data) — COMPLETE
- Artifacts: `reports/cointegration_diagnostics_real.json`. Tests: `tests/test_cointegration_diagnostics_schema.py`.
- Gate: all_pass True only if tradeable; else blocked_or_insufficient_data with non-empty blocked_routes.

### Campaign 2: POL/BTC regime analysis + causal filter — COMPLETE (kept blocked, unstable)
- Artifact: `reports/pol_btc_regime_analysis.json`. No threshold weakening; no causal filter added.

### Campaign 3: Honest blocking audit + evidence lock-in + near-miss re-examination — NEXT (HEAVY)
- Audit all 17 pairs for complete blocked_routes + rationale + provenance; lock with tests.
- POL/BTC deep dive + fate decision with reproducible evidence from cached real data.
- Near-miss re-examination of 16 pairs with numbers; no threshold weakening.
- Verify targeted tests + ruff clean.

### Campaign 4: Bottleneck removal / iteration speed — ONGOING
- Full pytest too slow; keep targeted invocation. If blocked > session, write fast targeted script or narrow scope to cointegration diagnostics only. Preserve schema.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — targeted diagnostics tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Any regime filter must be trailing-only with tests.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — do the work. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py -q  # expect 15 passed
```

**START NOW.** Prioritize POL/BTC deep dive (causal trailing-only filter attempt or evidence-backed keep-blocked) and near-miss audit. Do not wait on non-running regen.
