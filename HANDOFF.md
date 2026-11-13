# DURABLE HANDOFF — SINGLE AUTHORITATIVE START (cryptoquantstatarbstrats)

## INITIAL TASK MESSAGE — 2026-11-13T02:34:30Z UTC

**Repo priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage** (cointegration/pairs core). Economic relevance requires **costed out-of-sample spot-price PnL on real, provable data**. Quote-volume return metrics are **not tradable PnL**.

**State (bottlenecks cleared):** Environment verified and all cached real data inventoried with SHA256. C279 is **COMPLETE, verdict `NOT_TRADABLE`** on the full real 11-asset spot cache (5112×11, 2026-04-01→2026-10-30). No spot-price config in-repo produces costed OOS edge under locked WF/cost rules. **No active blockers remain except absence of genuinely new, provable real data.** Working tree clean at HEAD `085729a` (`main`).

**Next session must do heavy evidenced work (C280), not status/planning.** Execute **Path B** below (data-availability blocker, reproducible, heavy artifacts) because no materially new real dataset exists locally. Execute **Path A** only if genuinely new provable real data is found.

## VERIFIED ENVIRONMENT / TESTS
- Python 3.12.3 (`/usr/bin/python3`): numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, hmmlearn 0.3.3, pytest 9.2.0, pydantic 2.14.3, aiohttp 3.14.5, pytest-asyncio 1.5.0. `pytest tests/ --collect-only` → **1106**; targeted `-k "mean_reversion or momentum or pairs or coint"` → **191 passed** (2026-11-13). `ruff`/`mypy` not installed. Ignore stale venv in `research_state/state.yaml`.
- Git HEAD `085729a` on `main`, clean working tree at handoff time. Canonical handoff: this file only.

## VERIFIED REAL DATA INVENTORY (exhaustive local check 2026-11-13)
- **Spot price (tradable, real):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b` (492493 B); meta sha256 `cb5cb0863e3dedd0d373f1eeb52075c6b555c0048bdaf6eaa0d320ccaaf7c749` (569 B). **5112 hourly bars × 11 assets** [ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP], 2026-04-01→2026-10-30 1h, USDT, `fetch_real_data_only=true`, `fetch_fabricated_data=false`, 0 NaNs. This is the exhausted spot sample for C279.
- **Quote-volume (NOT tradable PnL):** `data/cache/volume_1h_full.pkl` sha256 `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c`, meta sha256 `4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616`, provenance sha256 `c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89` (Binance spot klines col5, 16 symbols incl DOGE/SHIB/TRX/AAVE/UNI, 81792 rows 2026-04-01→2026-10-30 1h, real/non-fabricated). **Do not use for edge/PnL claims** (C273/C277/C278 frozen).
- **Other cached artifacts:** 30+ additional cache pkls/metas present — all within/derived from same 2026-04-01→2026-10-30 Binance spot universe; no new period/assets/provenance. Full `data/cache/*` SHA256 inventory computed 2026-11-13 (reproducible via `sha256(file bytes)` over every file in `data/cache/`).
- **No other raw datasets found:** repo-wide search found **no `.csv/.parquet/.feather/.npz` data files** and no local funding/perp/futures/orderbook/microstructure/L2/trade raw datasets outside code/reports refs. `data/real_feed_loader.py` and `examples/run_funding_carry_real.py` reference funding/carry/microstructure concepts but no new provable real feed files exist locally.

## C279 RESULTS (final, on disk — do not rerun/edit)
WF 720/168/168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; real data only.
- **C279A causal pairs sweep:** `scripts/run_c279_causal_pairs_sweep.py`; `reports/campaign279_causal_pairs_20261113T020211Z.json` sha256 `9f93742ef35a84708e6f0506b21f7ecab6d468a95233814cc2acc9533f554c7f`. 17 pairs × 6 configs = **102 runs**, `use_enriched_gates=True`, `strict_enriched_gates=True`. **0 edge proven, 102 zero exposure**; `rolling_stable_ok` pass share 0.0 (binding).
- **C279B single-asset price-only sweep:** `scripts/run_c279_price_only_sweep.py`; `reports/campaign279_price_only_sweep_20261113T020443Z.json` sha256 `17b803a758f137e3a9d52b9a666a9ab1ba46813adacad7b15f5fba1ece88fc13`. MR × Momentum × 11 assets = **561 runs**, exposure present, **0 edge proven**.
- **C279C verdict:** `scripts/run_c279_verdict.py`; `reports/campaign279_negative_result_20261113T020539Z.json` sha256 `28800c0c5a7b8bf26ef28cb1170b94c7a799b43058521b1abe7a508b8560ca31`. Verdict **`NOT_TRADABLE`**.

## FROZEN PRIOR EVIDENCE (do not rewrite)
- C277A price-PnL revalidation: `reports/campaign277_c273_price_pnl_revalidation_20261112T172258Z.json` sha256 `3b5bf3094ccd46d6afa985022232c245424a9634711a5a49df71c09f62e12f1b` — `price_pnl_edge_proven=false`.
- C273 metric-validity: `reports/campaign273_metric_validity_finding_20261112T172258Z.json` sha256 `7a595cfadd330ffb5616cf23b041aa2fcc745ca2446eb7cfb92c03b5b170e231`; volume-return OOS `...050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf` **not tradable**.
- C278: `reports/campaign278_price_only_baseline_20261112T172556Z.json` sha256 `f484a0978bb9572779598a3d8b82779d70eed6638a7182a1724e8e90ceb8ffe2` (`price_only_edge_proven=false`).
- Registry: `reports/tradable_edge_registry_20261112T172556Z.json` sha256 `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2` (0 tradable). `reports/portfolio_real.json` sha256 `b573077ae2aaf4b0234c426d17b3b017867c4822438031a6979e6df184aa9e07`. Static cached-diagnostics pairs path is guaranteed no-op under strict gates — never use.

## C280 — MANDATORY HEAVY FOCUS (execute now, no status-only turns)

### Path A — NEW-DATA costed OOS (only if genuinely new, provable real data exists/obtainable here)
A "new" dataset must be materially different from all inventoried caches above (different time span and/or different real market/venue/series e.g. funding/perp/microstructure) with full provenance. **Do not refetch/relabel existing 2026-04-01→2026-10-30 spot/volume as new.**
1. Emit `reports/campaign280_data_provenance_<UTC>.json`: source/venue, exact symbols/interval/span/bar count, fetch method/hosts+timestamps or local origin, SHA256 of raw bytes/files, `real_data_only=true`, `fabricated_data=false`, explicit diff vs existing inventory.
2. Run pre-registered costed OOS on that new data via `scripts/run_c280_*`: fail-closed gates, **no** static `pair_diagnostics_file`/`enriched_diagnostics`, WF 720/168/168 (or justified), cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, edge rule (OOS exposure>0, all cost slices net sum>0, mean OOS net > mean B&H OOS net).
3. Emit C280 OOS + ingest/registry/summary/verdict JSONs with SHA256-from-bytes per artifact; honest verdict only.

### Path B — DATA-AVAILABILITY BLOCKER (required given current inventory; produce reproducible evidence — THIS SESSION'S FOCUS)
Because no materially new real dataset is present locally (verified 2026-11-13): execute Path B with **heavy, reproducible** artifacts, not prose-only status.
1. Create `scripts/run_c280_data_availability_blocker.py` that programmatically: enumerates `data/` and `data/cache/`, computes SHA256+bytes+meta highlights for relevant files, asserts absence of any new-period/new-venue/raw funding-perp-microstructure datasets, and emits artifacts with `real_data_only=true`, `fabricated_data=false`, `edge_proven=false`.
2. Emit `reports/campaign280_data_availability_blocker_<UTC>.json` documenting exhaustive checks (paths searched, cache inventory summary + key SHA256s, why volume is non-PnL/non-new, why funding/perp/microstructure/extra spot periods unavailable/non-provable here, any network/provenance constraints observed), conclusion `BLOCKED_NO_NEW_REAL_DATA`.
3. Emit `reports/campaign280_execution_summary_<UTC>.json` referencing script/report SHA256-from-bytes and test/collection sanity if run. No fake OOS.
4. **Update this HANDOFF.md** with C280 artifact paths+SHA256s and next concrete action (Path A if new provable data later becomes available, else remain blocked with evidence).
   - Exit criteria for Path B: script runs without error, all three JSONs exist on disk with correct SHA256-from-bytes, `edge_proven=false`, conclusion `BLOCKED_NO_NEW_REAL_DATA`, HANDOFF.md updated.

### Path C — Explanatory diagnostics (optional, alongside A/B only)
Real-data-only diagnostics on why `rolling_stable_ok`/cointegration gates fail (`reports/campaign280_gate_diagnostics_explanatory_*.json`, `edge_claim=NONE`). Never a substitute for A/B; no edge claims.

## HARD BANS
- No status/planning-only turns; no C1–C279 reruns; no C273 volume-return/7-pool/static-diagnostics reruns.
- No synthetic/fabricated data; no relabeling existing caches as new; no unprovenanced network fetch claims; no threshold/gate weakening; no cherry-picked windows/costs.
- Do not edit frozen artifacts or `research_state/state.yaml` unless explicitly requested. Record SHA256-from-bytes for every new artifact.
- Update this single handoff file when C280 produces durable evidence.

**END — 2026-11-13T02:34:30Z UTC. C279 `NOT_TRADABLE` on exhausted real spot cache; execute C280 Path B (reproducible blocker evidence) now; Path A only if genuinely new provable real data is found.**
