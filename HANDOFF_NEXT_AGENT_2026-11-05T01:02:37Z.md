# HANDOFF (SINGLE DURABLE) — 2026-11-05T01:02:37Z

REPO: cryptoquantstatarbstrats. PRIORITY: pairs/spreads/cointegration = core edge.
STATUS: Honest blocked outcome documented. run_pairs.py completes exit 0; reports/pairs_real_market.json trades_count=0 (real data, no fabrication). Gate breakdown: reports/pairs_gate_breakdown_20261105T010211Z.json. Proof: reports/handoff_proof_20261105T010226Z.json. Primary blocker: rolling_stable_ok (frac_significant 0.066-0.176) + eg_pass (p 0.518-0.731) on real Binance 1h 2026-04-01->2026-10-28 for BTC/ETH, ETH/SOL, BTC/SOL. No real window passes all enriched gates.

NEXT FOCUS CAMPAIGN (HEAVY WORK, NO INVESTIGATION-ONLY):
1. Expand pair universe + timeframes: scan all cached symbols (11) across 1h/4h/1d; compute cointegration diagnostics; find any pair/timeframe that passes all gates. Write reports/pairs_candidate_scan_<UTC>.json.
2. If a passing window exists, run walk-forward backtest producing nonzero trades_count/return/sharpe/mdd + fresh handoff_proof.
3. If none pass, document honest blocked outcome with full provenance and stop fabricating.
4. Remove bottlenecks: ensure rolling_cointegration_stability assessable on trailing samples (min_windows>=2, overlapping windows) while fail-closed; propagate honest gates; causal trailing only.
5. Re-run targeted tests: test_cointegration_campaign31_mt, test_cointegration_diagnostics_schema, test_pairs_real_market, test_cointegration_threshold_invariance.

RULES: Real data only. Never fabricate candles/IV/funding. Fail-closed. No threshold weakening. Commit nothing unless asked. Heavy working immediately.
