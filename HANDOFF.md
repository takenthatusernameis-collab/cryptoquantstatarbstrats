# DURABLE HANDOFF — SINGLE AUTHORITATIVE START (cryptoquantstatarbstrats)

## INITIAL TASK MESSAGE — 2026-11-13T03:33:06Z UTC (supersedes 02:45:01Z handoff)

**Repo priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage** (cointegration/pairs core). Economic relevance requires **costed out-of-sample spot-price PnL on real, provable data**. Quote-volume return metrics are **not tradable PnL**. Ranking below follows this priority.

**BLOCKER REMOVED — the previous "no new real data" premise is FALSE, twice.** Two independent proofs (verified 2026-11-13T03:33Z):
1. **Newer provable cache already on disk:** `data/cache/26736ab8…pkl` (sha256 `9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df`, 522733 B) is real Binance spot **5427 hourly bars × 11 assets [ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP], 2026-04-01→2026-11-13T02:00Z, USDT, `fetch_real_data_only=true`, `fetch_fabricated_data=false`, 0 NaNs**. Meta `…meta.json` sha256 `95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1`. This is **4 days newer** than the 2026-11-09 ceiling the prior handoff called "the limit" and 14 days newer than C279's exhausted 2026-10-30 window. It was simply not inventoried.
2. **Live network fetch works here:** `https://data-api.binance.vision/api/v3/klines` returns **HTTP 200** and already serves bars through **2026-11-13T03:00Z** (BTCUSDT 1h). `api.binance.com` returns 451, but the loader's host list (`www.binance.com` / `data-api.binance.vision` / `api[1-3].binance.com`) plus `DataLoader.fetch_with_provenance` and `DataLoader.load_binance_data` are usable. Do **not** repeat "no data" claims.

**State:** C279 COMPLETE, verdict `NOT_TRADABLE` on the exhausted 2026-04-01→2026-10-30 cache (5112×11). C280 Path A executed 2026-11-13T02:44:33Z on 2026-10-01→2026-11-09 data: 171 runs, 0 edge, `NOT_TRADABLE` — do **not** rerun. **C281A (fresh real-data fetch) is already DONE** at 2026-11-13T02:47:31Z: `reports/campaign281_data_provenance_20261113T024731Z.json` (verdict `NEW_REAL_DATA_FETCHED`, cache `26736ab8…`, 5427 bars →2026-11-13T02:00Z, `cache_hit=false`). Working tree clean at HEAD `4e4d908`. **The unfinished, mandatory work is C281B + C281C below.**

## MANDATORY HEAVY WORK — C281 (no status/planning turns; produce durable evidence)

**C281A — DONE 2026-11-13T02:47:31Z.** Fresh real spot cache `26736ab8…` (5427×11, →2026-11-13T02:00Z, `fetch_real_data_only=true`, `fabricated=false`, `cache_hit=false`) with `reports/campaign281_data_provenance_20261113T024731Z.json`. Do **not** repeat it. Optionally extend past 2026-11-13T02:00Z with `DataLoader.fetch_with_provenance`; not required to proceed.

**C281B — COSTED OOS EDGE TEST on the C281A dataset (the floor; verified runnable).** Source `data/cache/26736ab8…pkl` (28 WF splits of 720/168/168 — vs only 1 split on the exhausted C280 data). Reuse the C280 Path A protocol verbatim so results are comparable and non-cherry-picked:
- WF `train=720, test=168, step=168`; cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps.
- Fail-closed: strict enriched gates (`use_enriched_gates=True`, `strict_enriched_gates=True`); no `pair_diagnostics_file`/`enriched_diagnostics` static shortcuts.
- Universe: all 17 pairs from `reports/portfolio_real.json` + all 11 single assets; MR × Momentum grids from `scripts/run_c280_path_a_oos.py` (`MR_LOOKBACKS/MR_ENTRIES/MR_EXITS`, `MOM_N/MOM_M/MOM_ENTRIES`, pair `LOOKBACKS/ENTRIES/EXITS`).
- Edge rule (unchanged): `oos_edge_proven=true` IFF OOS exposure>0 AND **every** cost slice OOS net sum>0 AND mean OOS net > mean B&H OOS net on the same WF windows.
- Correct constructors (verified): `MeanReversionStrategy(asset=A, lookback=lb, entry_threshold=e, exit_threshold=x)`; `MomentumStrategy(asset=A, n=nn, m=mm, entry_threshold=e)`; `CointegrationPairsStrategy(pair=(A,B), lookback=lb, entry_threshold=e, exit_threshold=x, cointegration_pvalue=0.05, cointegration_check_interval=lb, use_enriched_gates=True, strict_enriched_gates=True)`. Build weights then `pos = weights.shift(1).fillna(0.0)`; use the `costed_oos`/`bh_oos`/`wf_splits` helpers from `scripts/run_c280_path_a_oos.py`.
- Runtime: single-asset <1 s, pair ~1.6 s → **~15–20 min** for the full grid. No excuse for a partial run.
- Emit `campaign281_oos_sweep_<ts>.json`, `campaign281_tradable_edge_registry_<ts>.json`, `campaign281_summary_<ts>.json`, `campaign281_verdict_<ts>.json` (honest verdict only; `NOT_TRADABLE` is a valid, expected outcome — never fabricate an edge).

**C281C — WHY-NO-EDGE gate diagnostics (explanatory only, no edge claims).** If C281B is `NOT_TRADABLE`, emit per-gate pass-share breakdown on the refreshed data (e.g. `rolling_stable_ok`, half-life bounds, structural-break discipline) to localize the binding constraint. This is diagnosis, never a substitute for C281B and never a license to weaken gates.

**Anti-avoidance rules (binding):** C281 must not be answered with a status/planning/inventory-only turn. **C281B is the floor — it must actually run and produce the four JSONs.** If the fetch partially fails, record the failure honestly and run C281B on the best real subset (documented) — do **not** fall back to synthetic, fabricated, relabeled, or quote-volume data. Record SHA256-from-bytes for **every** new artifact and update this file + `research_state/state.yaml` (only the state fields, per prior mandate) when C281 produces durable evidence.

## VERIFIED ENVIRONMENT / TESTS
- Python 3.12.3 (`/usr/bin/python3`): numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, hmmlearn 0.3.3, pytest 9.2.0, pydantic 2.14.3, aiohttp 3.14.5, pytest-asyncio 1.5.0. `pytest tests/ --collect-only` → **1106**; targeted `-k "mean_reversion or momentum or pairs or coint"` → **191 passed**. `ruff`/`mypy` not installed. Ignore stale venv path in `research_state/state.yaml`.

## VERIFIED REAL DATA INVENTORY (2026-11-13T03:33Z)
- **NEWEST real spot (tradable):** `data/cache/26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl` sha256 `9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df`; meta sha256 `95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1`. 5427×11, 2026-04-01→2026-11-13T02:00Z, 0 NaN, real/non-fabricated. **Use this for C281 (or refresh past it).**
- **Exhausted C279 cache:** `data/cache/0bab5d6a…pkl` sha256 `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b` (5112×11, →2026-10-30). Frozen.
- **Quote-volume (NOT tradable PnL):** `data/cache/volume_1h_full.pkl` sha256 `4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c` (17 symbols incl DOGE/SHIB/TRX/AAVE/UNI, 81792 rows →2026-10-30). Frozen — never for edge/PnL.
- 70 cache files total; all `fetch_real_data_only=true` spot/5m caches are within/derived from the 2026-04-01→2026-11-13 Binance spot universe. No local CSV/parquet/funding/perp/L2 raw datasets exist.

## FROZEN PRIOR EVIDENCE (do not rewrite or rerun)
- C279: `reports/campaign279_causal_pairs_20261113T020211Z.json` (102 runs, 0 edge); `reports/campaign279_price_only_sweep_20261113T020443Z.json` (561 runs, 0 edge); `reports/campaign279_negative_result_20261113T020539Z.json` (`NOT_TRADABLE`).
- C280: `reports/campaign280_data_availability_blocker_20261113T024317Z.json`; `reports/campaign280_oos_sweep_20261113T024433Z.json` (171 runs, 0 edge); `reports/campaign280_verdict_20261113T024433Z.json` (`NOT_TRADABLE`).
- C281A: `reports/campaign281_data_provenance_20261113T024731Z.json` (`NEW_REAL_DATA_FETCHED`, cache `26736ab8…`, 5427 bars →2026-11-13T02:00Z). Do not redo.
- Registry: `reports/tradable_edge_registry_20261112T172556Z.json` (0 tradable). `reports/portfolio_real.json` (17 pairs).

## HARD BANS
- No status/planning-only turns; no C1–C280 reruns; no C273 volume-return/7-pool/static-diagnostics reruns.
- No synthetic/fabricated data; no relabeling existing caches as new; no unprovenanced fetch claims; no threshold/gate weakening; no cherry-picked windows/costs.
- Do not edit frozen artifacts. Record SHA256-from-bytes for every new artifact. Update this single handoff + `research_state/state.yaml` when C281 produces durable evidence.

**END — 2026-11-13T03:33:06Z UTC. Blocker (`BLOCKED_NO_NEW_REAL_DATA`) is REMOVED: provable real spot exists through 2026-11-13T02:00Z on disk and live fetch reaches 2026-11-13T03:00Z. C281A is done. Next session MUST execute C281B (heavy costed OOS on the 28-split real dataset) and C281C if no edge, with SHA256-from-bytes on every artifact and an honest verdict.**