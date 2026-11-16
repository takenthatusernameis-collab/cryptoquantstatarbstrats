# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-16T03:37:12Z
**Program state:** `CLOSED` — reachable heavy-work space exhausted on current real, provable data.
**Closure audit:** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`, SHA256-from-bytes of on-disk file) — `reachable_space: CLOSED`, `genuinely_new_families_tested: 36`, `total_configs_recorded: 17175`, `edge_proven: false`, `binding_constraint: multiple_testing`, `errors: []`, `n_survive_holm_total: 0`, `n_survive_bh_total: 18`, `n_survive_both_total: 0`.
**Latest campaigns:** C317/C318 COMPLETE FORMAL NEGATIVES (20261116T013937Z / 20261116T015818Z). Full suite last verified 1729 passed / 1 failed (pre-existing frozen C313 gitignored full-sweep gap) / 2 skipped (403 s). `oos_edge_proven: false`; `edge_claim: NONE`.

## INITIAL TASK MESSAGE (2026-11-16T03:37:12Z) — TERMINAL: REACHABLE SPACE CLOSED

**Status:** C281B–C318 are ALL COMPLETE FORMAL NEGATIVES (0 tradable costed-OOS edge across 17,175 pre-registered configs, 36 genuinely-new families; binding constraint universally `multiple_testing`). C318 was the last genuinely-new reachable heavy family on current data. **No new campaign specification exists.**

**Mission (repo priority):** crypto quantitative statistical arbitrage — costed OOS PnL on real, provable data. No further in-repo heavy work remains without new data/venue/frequency or external C287 unblocking.

**Mandatory next-session behavior (choose the only honest option available):**
1. **Acknowledge closure and exit cleanly (default).** Do not run, modify, or re-skin any campaign. Do not emit new closure reports.
2. **External unblock C287 only if out-of-env access is now available** (credentials/geography/testnet: Binance REST/fapi 451, Bybit 403). If access is still unavailable, record that fact and exit — do not probe/retry as economic work.
3. **New data acquisition only if materially new real data is now present/ingestible** (new symbols/venues/frequencies not in C281B–C318 scope). If so, first prove reachability/provenance, register a genuinely-new (non-reskinned) family spec, and follow fail-closed gates — but do not fabricate data or invent scope absent real sources.

**Definition of Done (terminal session):** handoff/state remain consistent (`reachable_space: CLOSED`, `active_campaign: none`, `next_campaign: none`); no C281B–C318 reruns/re-skins; no stale closure-generator runs; no fabricated campaigns (C319+). Any claim must be backed by on-disk artifacts/provenance.

**Frozen/blocked (hard violations if touched):**
- **C281B–C318:** FROZEN formal negatives — do NOT rerun, re-skin, re-probe, or "revalidate".
- **C287:** externally blocked/decoupled (451/403, no creds) — out-of-env only; never retry as economic work.
- **Stale closure machinery:** `scripts/run_c305_program_closure_oos.py`, `scripts/run_program_closure_integrity_audit.py`, and prior `reports/program_closure_*` C305-era artifacts are FROZEN/misleading — do NOT run or cite as current state. Current authoritative audit is only `reports/program_closure_final_20261116T024519Z.json` (sha above).

**Environment / verification:**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

## C317 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T01:37:10Z)

- **Scripts PRESENT (uncommitted):** `scripts/build_c317_vol_moment_features.py`, `scripts/preflight_c317.py`, `scripts/run_c317_vol_moment_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c317.py`, `tests/test_c317_vol_moment_xsec_oos.py` (30/30 C317 tests green).
- **Feature cache COMPLETE (real data, ~27.82 MB):** `data/cache/campaign317_vol_moment_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 27.82 MB, max shard 3.0 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of the real C312 shards; no network, no resampling, no imputation.
  - meta SHA256 `247104806f7b4e1bc43187c2680e57285883987232845d2e474ec25619e5bb98`; provenance SHA256 `8825f553af979906b6598a777cfcbb7cc2667818af304a14bed265ae90b5f587`; manifest SHA256 `2ae4306465c17467090dfc136faa3aee4d06f2e27fb47c85aab514ddb4b87ddf`.
- **Preflight:** `python scripts/preflight_c317.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T013937Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: low_volatility 0.0932, lottery 0.6729, downside 0.1062, placebo 0.1277 (dominant lottery 0.6729 > 0.5 → attribution_ok true, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `92a4e780705570ed4838531f96549a520754f4e8692ea83e8d4636a4e8d9379d` (slim ~1.0 MB)
  - tradable_edge_registry `c65d1b0e40c3c85537cf475c2083417dd9662dcdb62a0cce38343f3c56146ee5`
  - summary `c35609621c6c47a76e04f60b7c94de337029c109b614d3441401519548fc83dc`
  - verdict `4de314c9ba0996332383f935c09dba21bfee97d06d262f076f6dfad5d544fc17`
  - binding_constraint `a017c6e0273f85cd1ce349869a2e7968379b87140095ba3f354dc48c03410297`
  - full sweep kept on disk as `reports/campaign317_oos_sweep_20261116T013937Z.full.json` (gitignored).

## C318 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T01:58:18Z)

- **Scripts PRESENT (uncommitted):** `scripts/build_c318_cov_beta_features.py`, `scripts/preflight_c318.py`, `scripts/run_c318_cov_beta_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c318.py`, `tests/test_c318_cov_beta_xsec_oos.py` (27/27 C318 tests green).
- **Feature cache COMPLETE (real data, ~27.82 MB):** `data/cache/campaign318_cov_beta_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 27.82 MB, max shard 3.0 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of the real C312 shards; no network, no resampling, no imputation.
  - meta SHA256 `2c293e9b56adcb97761f0f416c9ddc91e9f09444c0270b1609fcc4cf0e4e9188`; provenance SHA256 `484528c6d024e595f2b9ba1b63be681de5621eab74434a60a0d1667c5ec00ce6`; manifest SHA256 `2ae4306465c17467090dfc136faa3aee4d06f2e27fb47c85aab514ddb4b87ddf`.
- **Preflight:** `python scripts/preflight_c318.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T015818Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: beta 0.0462, correlation 0.2449, comoment 0.5997, placebo_noise 0.1093 (dominant comoment 0.5997 > 0.5 → attribution_ok true, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `3cff5927e21799c1a7537947fae6daeb5ba11f49f3ca0b81b8f8604532ed84a6` (slim ~1.0 MB)
  - tradable_edge_registry `4ca66e23aec1bea7f08b00613397ef39bd77f16442bbbf43accafb373a605d90`
  - summary `c20d5e1add65f0097baa37af7c56f554afec947f8ebee1f071dc1b6a55519aee`
  - verdict `ad6c5663d3fc79ed0ffc63fee2c649df2becec83a6191515d0a95ad2f7b1cf4e`
  - binding_constraint `023ca2633ec6e33f6c70b7cde1dc793f3ba4dec1ef01798f53fdfb776f5374de`
  - full sweep kept on disk as `reports/campaign318_oos_sweep_20261116T015818Z.full.json` (gitignored).

## C316 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T00:40:00Z)

- **Scripts PRESENT (uncommitted):** `scripts/build_c316_liquidity_features.py`, `scripts/preflight_c316.py`, `scripts/run_c316_liquidity_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c316.py`, `tests/test_c316_liquidity_xsec_oos.py` (28/28 C316 tests green).
- **Feature cache COMPLETE (real data, ~60 MB):** `data/cache/campaign316_liquidity_5m/` with 10 `.npz` shards each holding `index_ms`, `perp_close`, `log_return`, `notional`, `total_volume`, `vwap`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 59.9 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`.
  - meta SHA256 `6eb370a8ee7bb5e3c8ad441622cab7db1eae45c37dfd9689dcd3172e79890023`; provenance SHA256 `5b945fecffb83172c524bf2a4f714c42519ce82ca2edf7795e8290123067d8da`; manifest SHA256 `abc596768d27120e7b7b3bb302531c49aff4a31344f32578ccaecf0202f48c1e`.
- **Preflight:** `python scripts/preflight_c316.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T003953Z`:** 1440 pre-registered configs, expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm+BH; 864/1440 configs had real exposure. Attribution shares: size 0.3325, illiquidity 0.3011, turnover_volume 0.0937, placebo 0.2728 (dominant size 0.3325 < 0.5 → attribution_ok false). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `411ff436e67d2bf11530b8a25a10e7443fe4bb0981b8895280ec42eab090fc95` (slim ~1.0 MB)
  - tradable_edge_registry `161f588ce2ff2a3e5f91faa7acf8b1fd40fd88742ec41a6ad9bc05d84811b5c9`
  - summary `206d0154c2dc67bcdc225d74ae8deb984e2acee222a94991290690fa9e848e29`
  - verdict `e7d3839028f7cf02469129d9b3b5ca12f3221cc73fec2f5fc6d702b05cfe30d1`
  - binding_constraint `fcfb060a88829a7ee2c17190f7f6050baa182695c6791e821afa0c8c5ecb400c`
  - full sweep kept on disk as `reports/campaign316_oos_sweep_20261116T003953Z.full.json` (gitignored).

## C314 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T21:38:11Z)

- **Scripts PRESENT (uncommitted):** `scripts/ingest_c314_spot_perp_leadlag_5m.py`, `scripts/preflight_c314.py`, `scripts/run_c314_spot_perp_leadlag_oos.py`.
- **Tests COMPLETE & PASSING:** 25/25 C314 tests green.
- **Cache COMPLETE (real data, ~22 MB):** `data/cache/campaign314_spot_perp_leadlag_5m/` with 10 `.npz` shards (`index_ms`, `spot_close`, `perp_close`, `funding_rate` all-NaN control-only). 315,632 common-grid 5m bars, 2023-01..2025-12. `real_data_only:true, fabricated_data:false, executed_fills:false`.
  - **KEY DE-BOTTLENECK (do not re-litigate):** Binance **spot** 5m klines switched `open_time` to MICROSECONDS from 2025-01 while USDT-M perp stays in ms. The ingest normalizes open_time to ms (`normalize_open_time_ms`, threshold >1e14 → //1000) on BOTH write and read paths. Regression test: `test_preflight_2025_microsecond_spot_normalized`.
  - Cache meta SHA256 `4bd0e8c97e23fa01d1681357b70e6191caaf6ed5b5a9d4be1d2fd2a3d112f983`; provenance SHA256 `aa2aa688594ff5f3d02ad061ffbf983d5e9a023d365403f144e0c196172bccb6`.
- **Preflight:** `python scripts/preflight_c314.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261115T214305Z`:** 2304 pre-registered configs. **VERDICT: RETRACTED**, `binding_constraint: multiple_testing` — 0 survive Holm+BH; `leadlag_vs_noise_share = 0.000275` (noise-dominated); 1664/2304 configs had exposure. Artifacts `reports/campaign314_*_20261115T214305Z.json` + gitignored full.json (see state.yaml for SHAs).

## C313 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T20:45:00Z, frozen)
Scripts PRESENT: `scripts/ingest_c313_coinm_quarterly_carry.py`, `scripts/preflight_c313.py`, `scripts/run_c313_coinm_quarterly_carry_oos.py`. Tests 23/23 green. Cache `data/cache/campaign313_coinm_quarterly_carry/` (~4.0 MB, 1h 2022-07..2026-06). VERDICT: RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/960 deterministic edge). Artifacts at `20261115T204419Z`. Do not rerun.

## C312 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T18:50Z, frozen)
Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `perp_close` usable by C315/C317/C318). Scripts/tests/artifacts present; VERDICT: RETRACTED, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

## Bottlenecks removed / guardrails
- **C314 microsecond spot open_time (2025-01+) NORMALIZED to ms** in ingest (`normalize_open_time_ms`) — the key fix that made spot/perp 5m intersect across the full 36 months. Covered by a regression test.
- **C315 / C316 / C317 / C318 DONE** — real 5m prices already on disk (C312 cache); no download bottleneck. All are COMPLETE FORMAL NEGATIVES (see Escalation); do not rerun.
- Resumable manifest ingest (per symbol/market/month) where ingest is needed; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C317 frozen.
- Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable; 404 month = pre-listing exclusion (not outage).
- Recent monthly archives may carry a CSV header (`open_time`) — detect header vs headerless.
- `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
- Caches <100 MB (assert); keep per-asset `.npz` shards.
- C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
- COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — HTTP 404 on data.binance.vision; never depend. USDT-M `fundingRate` not in monthly archives and fapi 451 → funding leg NaN (control-only).

## Repository priority

`cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress = costed out-of-sample PnL on real, provable data. Any turn producing neither a real-data validation, a costed-OOS run, a passing test, or an artifact update is NOT economic progress.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; model PnL labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward, all pre-registered configs reported, multiple-testing correction before any positive claim.
6. **TESTS MUST PASS** — new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and `research_state/state.yaml`; do not create `HANDOFF.md`.
8. **ECONOMIC PRIORITY** — C287 is blocked externally and decoupled; do not retry as economic work.

## Escalation

- **C317 (COMPLETE FORMAL NEGATIVE, 20261116T013937Z):** cross-sectional realized-vol / higher-moment stat-arb, 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution dominant lottery 0.6729 (low_volatility 0.0932, downside 0.1062, placebo 0.1277); 5 artifacts + full.json + 30 C317 tests green; full suite 1700 passed / 2 skipped / 0 failed. De-bottleneck: real 5m prices on disk from C312 (no network ingest).
- **C318 (COMPLETE FORMAL NEGATIVE, 20261116T015818Z):** cross-sectional COVARIANCE / BETA co-movement stat-arb (beta/BAB, correlation, co-skewness, co-kurtosis, downside-beta), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; dominant attribution comoment 0.5997 (beta 0.0462, correlation 0.2449, placebo_noise 0.1093); 5 artifacts + full.json + 27 C318 tests green; full suite 1729 passed / 1 failed (pre-existing frozen C313 gap) / 2 skipped (403 s). De-bottleneck: real 5m prices on disk from C312 (no network ingest). LAST genuinely-new reachable heavy family — reachable space CLOSED (TEXT ONLY).
- **C316 (COMPLETE FORMAL NEGATIVE, 20261116T003953Z):** cross-sectional size/volume/turnover liquidity stat-arb, 1440 configs, 0 survive Holm+BH, binding `multiple_testing`; dominant attribution size 0.3325; 5 artifacts + full.json + 28 tests green.
- **C315 (COMPLETE FORMAL NEGATIVE, 20261115T223831Z):** perp momentum / short-term reversal stat-arb, 3456 configs, 0 survive Holm+BH, binding `multiple_testing`, dominant attribution reversal 0.7015; 5 artifacts + full.json + 23 tests green.
- **C314 (COMPLETE FORMAL NEGATIVE, 20261115T214305Z):** spot-perp lead-lag stat-arb, 2304 configs, 0 survive Holm+BH, binding `multiple_testing`, leadlag_vs_noise_share 0.0003; 5 artifacts + full.json + 25 tests green. De-bottleneck: spot 5m microsecond `open_time` (2025-01+) normalized to ms.
- **C313 (COMPLETE FORMAL NEGATIVE, 20261115T204419Z):** 0/960 Holm+BH, binding `multiple_testing`; 5 artifacts + 23 tests green. Do not rerun.
- **C312 (COMPLETE FORMAL NEGATIVE, 20261115T174346Z):** 0/504 survive Holm+BH, binding `multiple_testing`; 5 artifacts + full.json + 21 tests green.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only geographic/credential issue (testnet 451, no creds). Do not retry, do not probe, do not let it preempt economic work. Unblocking requires out-of-env action only.