# DURABLE HANDOFF — SINGLE AUTHORITATIVE START (cryptoquantstatarbstrats)

## INITIAL TASK MESSAGE — 2026-11-13T02:07:14Z UTC

**Repo priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**; core declared edge is **cointegration pairs**. Economic relevance requires **costed out-of-sample spot-price PnL from real data** (quote-volume return units are not PnL/tradable).

**State:** Environment and methodology bottlenecks are removed. **C279 is COMPLETE with verdict `NOT_TRADABLE`** on the full real 11-asset spot cache. No spot-price config in the repo produces costed OOS edge under the locked WF/cost rules. **Do not redo C1–C279, do not re-sweep the same cache/config families, do not lower thresholds or coerce gates.**

## VERIFIED ENVIRONMENT / DATA (ready)
- Python: `/usr/bin/python3` 3.12.3 with numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, hmmlearn 0.3.3, pytest 9.2.0, pydantic 2.14.3, aiohttp 3.14.5, pytest-asyncio 1.5.0. `pytest tests/ --collect-only` → **1106 tests**; targeted `-k "mean_reversion or momentum or pairs or coint"` → **191 passed** (this session). `ruff`/`mypy` not installed. Ignore stale venv in `research_state/state.yaml`.
- Real spot cache (no network, no synthetic): `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, meta sha256 per `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json`, **5112 hourly bars × 11 assets** (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP), 2026-04-01→2026-10-30, 0 NaNs. Volume artifacts present but volume-return metrics are not tradable PnL (see frozen evidence).
- Git: HEAD `eb602b3` on `main`. This handoff + untracked C279 artifacts/scripts may be present locally. No active heavy process required.

## C279 RESULTS (final, on disk)
WF 720/168/168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; real data only.
- **C279A causal pairs sweep:** `scripts/run_c279_causal_pairs_sweep.py`; `reports/campaign279_causal_pairs_20261113T020211Z.json` sha256 `9f93742ef35a84708e6f0506b21f7ecab6d468a95233814cc2acc9533f554c7f`. 17 pairs × 6 configs = **102 runs**, NO `pair_diagnostics_file`/NO `enriched_diagnostics`, `use_enriched_gates=True`, `strict_enriched_gates=True`. **0 edge proven, 102 zero exposure**; `rolling_stable_ok` pass share 0.0 on every run (binding gate).
- **C279B single-asset price-only sweep:** `scripts/run_c279_price_only_sweep.py`; `reports/campaign279_price_only_sweep_20261113T020443Z.json` sha256 `17b803a758f137e3a9d52b9a666a9ab1ba46813adacad7b15f5fba1ece88fc13`. MR (24) + Momentum (27) × 11 assets = **561 runs**, exposure present, **0 edge proven**.
- **C279C verdict:** `scripts/run_c279_verdict.py`; `reports/campaign279_negative_result_20261113T020539Z.json` sha256 `28800c0c5a7b8bf26ef28cb1170b94c7a799b43058521b1abe7a508b8560ca31`. Verdict **`NOT_TRADABLE`**. No statistic invented, no thresholds lowered, no gates fabricated.

## FROZEN PRIOR EVIDENCE (do not rewrite)
- C277A price-PnL revalidation: `reports/campaign277_c273_price_pnl_revalidation_20261112T172258Z.json` sha256 `3b5bf3094ccd46d6afa985022232c245424a9634711a5a49df71c09f62e12f1b` — `price_pnl_edge_proven=false`; cross-asset price PnL negative at every cost slice.
- C273 metric-validity: `reports/campaign273_metric_validity_finding_20261112T172258Z.json` sha256 `7a595cfadd330ffb5616cf23b041aa2fcc745ca2446eb7cfb92c03b5b170e231`. C273 volume-return OOS (`...050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`) is **not tradable**.
- C278 baseline: `reports/campaign278_price_only_baseline_20261112T172556Z.json` sha256 `f484a0978bb9572779598a3d8b82779d70eed6638a7182a1724e8e90ceb8ffe2` — `price_only_edge_proven=false`.
- Registry: `reports/tradable_edge_registry_20261112T172556Z.json` sha256 `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2` (0 tradable).
- `reports/portfolio_real.json` sha256 `b573077ae2aaf4b0234c426d17b3b017867c4822438031a6979e6df184aa9e07` (17 pairs blocked/insufficient, `all_pass=false`). Static cached-diagnostics pairs path is a guaranteed no-op under strict gates — never use.

## NEXT FOCUS CAMPAIGN (heavy work, only if justified by NEW real evidence)
Because exhaustive spot-price search on the available real cache is negative, **default next action is to stop fabricating edge-search campaigns on the same data.** Future work must be materially new and evidence-producing:

1. **New real data (only viable path to a different answer):** if and only if a genuinely new real dataset can be obtained/verified with provenance (different time period, additional liquid spot pairs, or a non-spot series the framework can cost correctly e.g. funding/perp/microstructure *with real fetch+provenance and no fabrication*), design and run a **C280 pre-registered, costed OOS** campaign on that new data. Requirements: document source, SHA256, no network blind spots, no synthetic fallback, fail-closed gates, same edge rule (OOS exposure>0, all cost slices net sum>0, mean OOS net > mean B&H OOS net). If no such data is available in-environment, record a **blocked-by-data-availability** evidence artifact (no fake results) and stop.
2. **Research hardening (non-edge, only if requested):** reproduce key results/tests, or document why `rolling_stable_ok`/cointegration fails on this sample from real diagnostics — purely explanatory, no edge claims.
3. **Do not**: add new volume/quote-return "alpha", rescale to claim PnL, relax `strict_enriched_gates`, pass static `pair_diagnostics_file`, cherry-pick windows/costs, or run C1–C279 again.

## HARD BANS
- No status/planning-only turns.
- No C1–C279 reruns; no 7 pool families; no C273 volume-return families; no static cached-diagnostics pairs route.
- No network refetch; no synthetic/fabricated data; no threshold weakening; no gate coercion.
- Do not edit frozen artifacts or `research_state/state.yaml` unless explicitly requested. Record SHA256-from-bytes for any new artifact.
- Canonical handoff is this file only.

**END OF DURABLE HANDOFF — 2026-11-13T02:07:14Z UTC. C279 complete, `NOT_TRADABLE` on real 11-asset spot cache; no proven spot-price edge.**
