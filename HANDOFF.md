# DURABLE HANDOFF — SINGLE AUTHORITATIVE START (cryptoquantstatarbstrats)

## INITIAL TASK MESSAGE — 2026-11-13T02:45:01Z UTC

**Repo priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage** (cointegration/pairs core). Economic relevance requires **costed out-of-sample spot-price PnL on real, provable data**. Quote-volume return metrics are **not tradable PnL**.

**State:** C279 COMPLETE, verdict `NOT_TRADABLE` on exhausted real spot cache (5112×11, 2026-04-01→2026-10-30). C280 Path B inventory executed 2026-11-13T02:43:17Z: the "no new real data" premise was **falsified** — provable Binance spot caches through 2026-11-09 exist on disk (`4c3bc2f1…pkl` 944 bars 2026-10-01→2026-11-09, sha256 `dec04f719339480ac1dce151d153d90ff385f0e7bfb95c59425ed45f5edfbb06`; `dcd5764a…pkl` 272 bars 2026-10-29→2026-11-09, sha256 from inventory report), both `fetch_real_data_only=true`/`fetch_fabricated_data=false`, SHA256-from-bytes verified. C280 Path A executed 2026-11-13T02:44:33Z on the new data: costed OOS sweep, WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, strict enriched gates fail-closed, no `pair_diagnostics_file`/`enriched_diagnostics` — **171 runs, 0 edge proven, verdict `NOT_TRADABLE`**. No active blockers except absence of genuinely newer provable real data beyond 2026-11-09.

**Next session must do heavy evidenced work (C280 follow-up), not status/planning.** If genuinely new provable real data beyond 2026-11-09 appears/is obtainable here → execute Path A on it: data provenance report, costed OOS sweep, registry/summary/verdict JSONs, SHA256-from-bytes for every artifact, honest verdict only. Otherwise remain `BLOCKED_NO_NEW_REAL_DATA` with C280 evidence on disk; Path C explanatory gate diagnostics optional (no edge claims). Do **not** rerun C279 or C280 Path A.

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

## C280 — EXECUTED (Path A costed OOS on new provable data; Path B premise falsified)

### Path B — DATA-AVAILABILITY INVENTORY (executed 2026-11-13T02:43:17Z; premise falsified)
`scripts/run_c280_data_availability_blocker.py` enumerated `data/` and `data/cache/`, SHA256-hashed every file, asserted absence of new-period/new-venue/raw funding-perp-microstructure datasets **relative to the 2026-04-01→2026-10-30 locked universe**, and found the premise false: two provable real spot caches extend to 2026-11-09 (9 days beyond C279's exhausted window). Verdict `NEW_DATA_DETECTED` (not blocked).
- `reports/campaign280_data_availability_blocker_20261113T024317Z.json` sha256 `861a897855da33fb907e9b02b7df2b7efddedabe7a4f15dabe0282e7f1601258`
- `reports/campaign280_blocker_assertions_20261113T024317Z.json` sha256 `c25771840751a3973e99df461ff86f5cd02e1efa9fc2a9cc4267e28bd0c80b4d`
- `reports/campaign280_execution_summary_20261113T024317Z.json` sha256 `1d872672f482d867431b578932a86410de3ced578ca7e20ea96fdb3c022e2ffe`

### Path A — NEW-DATA COSTED OOS (executed 2026-11-13T02:44:33Z; mandatory heavy focus, done)
`scripts/run_c280_path_a_oos.py` ran fail-closed costed OOS on new provable data (`4c3bc2f1…pkl`, BTC/ETH/SOL 1h 2026-10-01→2026-11-09, 944 bars, `fetch_real_data_only=true`/`fetch_fabricated_data=false`), WF 720/168/168 (1 split), cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, edge rule (OOS exposure>0, all cost slices net sum>0, mean OOS net > mean B&H OOS net), no static diagnostics files. **171 runs (18 pairs + 153 single-asset), 0 edge proven.**
- `reports/campaign280_data_provenance_20261113T024433Z.json` sha256 `d1e1f69754730ef37c07bd317341f7878a2495a266c4d4acae822aa02641b092`
- `reports/campaign280_oos_sweep_20261113T024433Z.json` sha256 `a7d2051327103d7e30c3446705258a5e56bf1cac0bfd7fc35ed6db38d0da5df2`
- `reports/campaign280_tradable_edge_registry_20261113T024433Z.json` sha256 `66ebcbd4baf8b11533c26e709082815551e4694d088250dc738e7eb2fff02e6c`
- `reports/campaign280_summary_20261113T024433Z.json` sha256 `65a7b03bd84867f6d80953b2c87fac40c03d1348c58b27585d026fe7366f18fd`
- `reports/campaign280_verdict_20261113T024433Z.json` sha256 `d302e452f5781ef0a70e1a8da8184b1d8c721b6f1e90523f7d38004823d52539`

Verdict `NOT_TRADABLE`: no costed OOS edge on new provable spot data through 2026-11-09. C280 complete; exit criteria met (scripts ran without error, all JSONs on disk with SHA256-from-bytes, `edge_proven=false`, honest verdict). HANDOFF.md updated.

**Next concrete action:** remain `BLOCKED_NO_NEW_REAL_DATA` until genuinely newer provable real data beyond 2026-11-09 is available here, then run Path A on it. Path C explanatory diagnostics optional alongside; never a substitute for Path A.

## HARD BANS
- No status/planning-only turns; no C1–C279 reruns; no C273 volume-return/7-pool/static-diagnostics reruns.
- No synthetic/fabricated data; no relabeling existing caches as new; no unprovenanced network fetch claims; no threshold/gate weakening; no cherry-picked windows/costs.
- Do not edit frozen artifacts or `research_state/state.yaml` unless explicitly requested. Record SHA256-from-bytes for every new artifact.
- Update this single handoff file when C280 produces durable evidence.

**END — 2026-11-13T02:45:01Z UTC. C279 `NOT_TRADABLE` on exhausted real spot cache; C280 Path A `NOT_TRADABLE` on new provable data through 2026-11-09 (171 runs, 0 edge); all artifacts + SHA256-from-bytes on disk. Next session: Path A only if genuinely newer provable real data beyond 2026-11-09 appears, else remain blocked with evidence.**
