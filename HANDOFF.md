# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-13T02:05:39Z UTC (AUTHORITATIVE)

**Repo-prioritized focus:** `cryptoquantstatarbstrats` = crypto quant **statistical arbitrage**, whose core edge is **cointegration pairs** (README: "Cointegration is the core edge of this repo"). The only economically relevant question is whether a signal produces **costed out-of-sample PnL from real spot prices**. Anything measured in quote-volume return units is not a PnL and is not tradable.

**This session removed the environment + methodology bottlenecks. Do not redo them:**
1. **Dependencies installed and verified.** `/usr/bin/python3` (3.12.3) has `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `statsmodels 0.15.0`, `scikit-learn 1.9.1`, `hmmlearn 0.3.3`, `pytest 9.2.0`, `pydantic 2.14.3`, `aiohttp 3.14.5`, `pytest-asyncio 1.5.0` (user site). `pytest tests/ --collect-only` collects **1106 tests**; `-k "mean_reversion or momentum or pairs or coint"` → **191 passed**. Ignore the stale venv path in `research_state/state.yaml` (`/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` does not exist) — use `/usr/bin/python3`.
2. **The static cached-diagnostics pairs test is a guaranteed no-op. Do NOT repeat it.** `reports/portfolio_real.json` `cointegration_diagnostics` has **all 17 pairs `status="blocked_or_insufficient_data"` with `gates.all_pass=false`** (BTC/ETH EG p=0.5186; only `johansen`/`hl_bounds` pass). C278 fed that static full-sample aggregate via `pair_diagnostics_file=...`; under `strict_enriched_gates=True` the cached path is fail-closed, so **0 OOS exposure for every pair is structurally forced**, not discovered.
3. **C279 is COMPLETE.** C279A (causal pairs sweep), C279B (single-asset price-only sweep), and C279C (negative result verdict) all executed on the real 11-asset spot cache. **Zero tradable edge found.** `rolling_stable_ok=0.0` is the binding gate on every pair run; all 102 pair runs had 0 exposure; all 561 single-asset configs failed the costed OOS edge test. Do not re-run C279 or any C1–C278 campaign. No new statistic, no threshold lowering, no gate coercion, no fabricated data.

**Bottom line:** no spot-price config in the repo produces costed OOS PnL on the real 11-asset cache. C279 verdict: `NOT_TRADABLE`. All artifacts on disk with SHA256 recorded below.

### C279 — COMPLETE (all three parts executed)

Data (verified): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`, sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, **5112 hourly bars × 11 assets** (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP), 2026-04-01→2026-10-30, 0 NaNs. No network, no synthetic data. WF = 720/168/168; cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps.

**C279A — CAUSAL cointegration-pairs sweep: DONE.**
`scripts/run_c279_causal_pairs_sweep.py` created and executed. 17 pairs × 6 configs (lookback {240,480,720} × entry {2.0,2.5} × exit 0.5) = **102 runs**, all with NO `pair_diagnostics_file`/NO `enriched_diagnostics`, `use_enriched_gates=True`, `strict_enriched_gates=True`. **Result: 0 edge proven, 102 zero exposure.** `rolling_stable_ok` pass share = 0.0 on every run (binding gate). Artifact: `reports/campaign279_causal_pairs_20261113T020211Z.json` sha256 `9f93742ef35a84708e6f0506b21f7ecab6d468a95233814cc2acc9533f554c7f`.

**C279B — Single-asset price-only sweep: DONE.**
`scripts/run_c279_price_only_sweep.py` created and executed. MeanReversion (lookback {24,48,96,120} × entry {1.5,2.0,2.5} × exit {0.25,0.5} = 24) + Momentum (n {10,20,40} × m {20,40,80} × entry {0.005,0.01,0.02} = 27) across 11 assets = **561 runs**, all with exposure but **0 edge proven**. Artifact: `reports/campaign279_price_only_sweep_20261113T020443Z.json` sha256 `17b803a758f137e3a9d52b9a666a9ab1ba46813adacad7b15f5fba1ece88fc13`.

**C279C — Negative result verdict: DONE.**
`scripts/run_c279_verdict.py` executed. Zero tradable configs across C279A + C279B. Artifact: `reports/campaign279_negative_result_20261113T020539Z.json` sha256 `28800c0c5a7b8bf26ef28cb1170b94c7a799b43058521b1abe7a508b8560ca31`. Verdict: `NOT_TRADABLE`. No new statistic invented, no thresholds lowered, no gates fabricated.

### SESSION COMPLETION RULE
All C279 completion criteria met:
- `reports/campaign279_causal_pairs_20261113T020211Z.json` — valid JSON, sha256 `9f93742ef35a84708e6f0506b21f7ecab6d468a95233814cc2acc9533f554c7f`
- `reports/campaign279_price_only_sweep_20261113T020443Z.json` — valid JSON, sha256 `17b803a758f137e3a9d52b9a666a9ab1ba46813adacad7b15f5fba1ece88fc13`
- `reports/campaign279_negative_result_20261113T020539Z.json` — valid JSON, sha256 `28800c0c5a7b8bf26ef28cb1170b94c7a799b43058521b1abe7a508b8560ca31`
- This handoff updated with exact paths, SHA256s, and new UTC timestamp (above).

### HARD BANS
- No status-only or planning-only turns.
- No re-running C1–C278, the 7 pool families, the C273 volume-return families, or the C278 static cached-diagnostics route.
- **Never pass `pair_diagnostics_file`/`enriched_diagnostics` (static aggregate) to the pairs strategy.** Use the causal per-bar path only.
- No network refetch; no synthetic/fabricated data; no threshold weakening; no gate coercion.
- No edits to frozen C273 artifacts (read, never rewrite).
- No edits to `research_state/state.yaml` unless explicitly requested; C279 must sync it at completion.
- Record all new/updated artifact SHA256s from file bytes.

## FROZEN EVIDENCE (verified 2026-11-12T19:43Z UTC)
- C277A price-PnL revalidation: `reports/campaign277_c273_price_pnl_revalidation_20261112T172258Z.json` sha256 `3b5bf3094ccd46d6afa985022232c245424a9634711a5a49df71c09f62e12f1b` — `price_pnl_edge_proven=false`; cross-asset price PnL negative at every cost slice (fee0 −1.7524, fee5 −3.0134, fee10 −4.2744, fee20 −6.7964, fee40 −11.8404); volume-return baseline reproduced to max_abs_diff 0.0 (tol 1e-9).
- C273 metric-validity finding: `reports/campaign273_metric_validity_finding_20261112T172258Z.json` sha256 `7a595cfadd330ffb5616cf23b041aa2fcc745ca2446eb7cfb92c03b5b170e231`.
- C278 price-only baseline: `reports/campaign278_price_only_baseline_20261112T172556Z.json` sha256 `f484a0978bb9572779598a3d8b82779d70eed6638a7182a1724e8e90ceb8ffe2` — static cached pairs blocked (0 exposure); MR fallback (lookback 30, entry 2.0, exit 0.5) `price_only_edge_proven=false`, cross-asset fee0 −40.2291, fee40 −78.1091.
- Tradable edge registry: `reports/tradable_edge_registry_20261112T172556Z.json` sha256 `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2` (16 candidates, 0 tradable).
- Frozen C273 volume-return baseline (evidence only, NOT tradable): OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`; cross-asset volume-return fee0 +80.68 … fee40 +70.60 (not spot-price PnL).
- `reports/portfolio_real.json` sha256 `b573077ae2aaf4b0234c426d17b3b017867c4822438031a6979e6df184aa9e07` (all 17 pairs `blocked_or_insufficient_data`, `all_pass=false`).

## STATE SNAPSHOT (verified 2026-11-13T01:58:03Z UTC)
- **Env:** `/usr/bin/python3` 3.12.3 with deps installed and verified (see top). `pytest tests/ --collect-only` collects **1106 tests**; `ruff` and `mypy` NOT installed — skip lint/typecheck until available. Ignore the stale venv path in `research_state/state.yaml` — use `/usr/bin/python3`.
- **Data:** `data/cache/` = 68 real files; spot cache sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b` (11 assets, 5112 hourly bars, 2026-04-01→2026-10-30). Volume pkl sha256 `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`. No network refetch; no synthetic data.
- **Git:** HEAD `eb602b3` on `main`; only this handoff is modified. New artifacts/scripts stay untracked unless committed. No active heavy process.
- **Canonical handoff:** this file only. `research_state/state.yaml` is stale (`latest_campaign_done: C248`, `next_campaign: C249`, nonexistent venv path); this HANDOFF supersedes it.
- **C273:** frozen; volume-return metric; **not tradable** (C277A price-PnL negative at all cost slices).
- **C274/C275/C276:** NO EDGE. No action needed.
- **C277/C278:** DONE (both `price_*_edge_proven=false`).
- **C279:** DONE (all three parts executed; verdict `NOT_TRADABLE`; zero spot-price edge on the real 11-asset cache).

**END OF DURABLE HANDOFF — refreshed 2026-11-13T02:05:39Z UTC (C279 complete, verdict NOT_TRADABLE; all environment and methodology bottlenecks removed and verified; no spot-price edge exists on the real 11-asset cache).**
