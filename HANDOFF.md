# HANDOFF (SINGLE DURABLE) — 2026-11-05T05:54:00Z
REPO: cryptoquantstatarbstrats | CORE EDGE: pairs/spreads/cointegration (MANDATORY PRIORITY #1). Real data only. Fail-closed. No threshold weakening. Causal trailing only.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)

DO THIS IMMEDIATELY IN ORDER (ARTIFACTS REQUIRED):

1) **CONFIRM FRESH SCAN ARTIFACT EXISTS (BLOCKERS REMOVED)**
   - Fresh scan: `reports/pairs_candidate_scan_20261105T050821Z.json` exists (n_pairs_scanned_tf=165, n_pass_all_gates=0).
   - Fresh blocked summary: `reports/pairs_blocked_summary_20261105T055351Z.json` exists with per-gate failures.
   - Gate failures (TF-aggregate): leg_stationarity_ok is dominant blocker; eg_pass/johansen_pass/spread_mr_pass/hl_bounds_pass/rolling_stable_ok/no_structural_break also fail on real crypto. Do NOT weaken any gate.

2) **HEAVY CAMPAIGN: FIND ANY HONEST PATH TO A PASSING PAIR (NO WEAKENING)**
   - **Leg stationarity reality**: both legs must be ADF stationary (p<=0.05). On current 1h/4h/1d real series this is rare. Explore ONLY via non-weakening means: (a) different pair selection within cached universe (focus pairs where both legs show stronger mean-reversion/ADF evidence), (b) verify data cleaning/resampling doesn't drop structure, (c) confirm causal trailing windows are correct. Do NOT change thresholds/p-values/significance or "relax" tests.
   - **Spread/cointegration**: if legs approach stationarity, EG/Johansen/spread MR/rolling stability must hold causally. Any fix must be assessability-only or correctness/parity only.
   - **If you find >=1 pair passing ALL gates on real data**: build walk-forward OOS backtest with fresh proof artifact under `reports/` (nonzero trades or honest zeros with full diagnostics; no fabrication).
   - **If none pass after exhaustive honest search**: update/write a more detailed blocked summary under `reports/pairs_blocked_summary_<UTC>.json` adding concrete pair-level examples of why leg_stationarity_ok fails (top failing pairs per TF with ADF p-values/provenance) without weakening gates.

3) **HARDEN PARITY + TRACE (VERIFY ONLY)**
   - Confirm `strategies/pairs_trading.py` enriched gates causal per-bar, interval caching parity with cached/uncached paths, fail-closed.
   - Confirm `utils/cointegration.py` assessability fixes intact (>=2 windows). Only fix assessability/correctness bugs. Never touch gate thresholds.

4) **VALIDATE + COMMIT ARTIFACTS**
   - Run: `python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v`
   - Lint/typecheck: `python -m ruff check utils/cointegration.py strategies/pairs_trading.py && python -m mypy utils/cointegration.py strategies/pairs_trading.py`
   - Every session MUST leave >=1 new concrete artifact in `reports/` (scan/blocked summary/detailed failure analysis/OOS proof). No investigation-only loops.

## CURRENT STATE (2026-11-05T05:54:00Z)
- Branch main clean, up to date with origin/main.
- Tests: 35 passed (campaign31 MT, diagnostics schema, pairs real market).
- ruff/mypy clean on utils/cointegration.py + strategies/pairs_trading.py.
- Fresh scan done (20261105T050821Z): 165 (55×3), n_pass_all_gates=0. Blocked summary written (20261105T055351Z).
- Assessability (rolling stability) fixed. Parity verified. Leg stationarity is genuine blocker on real crypto price legs.

## BOTTLENECKS
- **Leg stationarity (REMAINING, CANNOT WEAKEN)**: Both legs need ADF p<=0.05. Dominant failure. Do not spend cycles trying to bypass — do heavy honest work to find pairs where this can be true on real data, or document concretely why impossible.
- **Other gates**: EG/Johansen/spread MR/structural break/rolling stability/hurdle bounds all matter; failures cascade once legs fail.

## NEXT FOCUS CAMPAIGN (MANDATORY, HEAVY)
Priority order (by repo name): pairs > spreads > cointegration.
1. Deep-dive failing pairs for leg_stationarity: pick top candidates by other gates passing (eg_pass/johansen_pass/spread_mr_pass) and inspect ADF p-values per leg/TF with provenance.
2. If any pair shows both legs stationary on real data with causal windows → full enriched gate trace + walk-forward OOS with proof.
3. Else produce detailed per-gate, per-pair breakdown (honest) in reports/ with concrete numbers. No threshold changes.
4. Keep parity/caching/fail-closed intact. Validate tests+lint+mypy.

## FILES TO FOCUS ON
- `utils/cointegration.py` (gates/ADF/EG/Johansen/rolling stability; assessability fixed, don't weaken)
- `strategies/pairs_trading.py` (causal enriched gates, parity)
- `examples/run_pair_universe_scan.py`, `examples/run_pairs_multi.py`
- `reports/` (artifacts required)

## VERIFICATION
```bash
python examples/run_pair_universe_scan.py
python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v
python -m ruff check utils/cointegration.py strategies/pairs_trading.py
python -m mypy utils/cointegration.py strategies/pairs_trading.py
```

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (ADF p<=0.05, significance levels unchanged).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Commit nothing unless explicitly asked.
- Heavy working immediately. No investigation-only. Every session leaves concrete artifact in `reports/`.
