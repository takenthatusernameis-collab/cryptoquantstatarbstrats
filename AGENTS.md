# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-16T01:58:18Z — **C281B–C318 CLOSED (all COMPLETE FORMAL NEGATIVES; 0 tradable costed-OOS edge across 15,000+ pre-registered configs; binding constraint universally `multiple_testing`). C287 remains externally blocked (out-of-env only; REST 451 / fapi 451 / bybit 403).** C317 → COMPLETE FORMAL NEGATIVE (20261116T013937Z). **C318 (cross-sectional COVARIANCE / BETA co-movement: beta/BAB, correlation, co-skewness, co-kurtosis, downside-beta) BUILT and RUN end-to-end this session → COMPLETE FORMAL NEGATIVE (`RETRACTED`, `edge_proven:false`, `binding_constraint:multiple_testing`, 0/1440 deterministic edge, 0 survive Holm+BH, dominant attribution comoment 0.5997).** Verified on-disk: `data/cache/campaign318_cov_beta_5m/` (10 perps, 315,648 bars, 27.82 MB, SHA-verified); 5 slim artifacts + gitignored full.json at `20261116T015818Z`; feature cache + meta + provenance + preflight `ready:true`; 27 C318 tests green; **FULL SUITE 1727 passed / 2 skipped / 0 failed (426 s)**. `active_campaign: C318` (COMPLETE); `oos_edge_proven: false`; `edge_claim: NONE`; **reachable space CLOSED (TEXT ONLY — C318 was the last genuinely-new reachable heavy family).** C317 (cross-sectional REALIZED-VOLATILITY / higher-moment: rv, ivol, skew, maxret, dsvol) was BUILT and RUN end-to-end this session → COMPLETE FORMAL NEGATIVE (`RETRACTED`, `edge_proven:false`, `binding_constraint:multiple_testing`, 0/1440 deterministic edge, 0 survive Holm+BH, dominant attribution lottery 0.6729). Verified on-disk: `data/cache/campaign317_vol_moment_5m/` (10 perps, 315,648 bars, 27.82 MB, SHA-verified); 5 slim artifacts + gitignored full.json at `20261116T013937Z`; feature cache + meta + provenance + preflight `ready:true`; 30 C317 tests green; **FULL SUITE 1700 passed / 2 skipped / 0 failed (423 s)**; `latest_campaign_done: C317`. The one genuinely-new reachable heavy family left after C317 is now REGISTERED as the active campaign: **C318 — cross-sectional COVARIANCE / BETA (co-movement) stat-arb (betting-against-beta, correlation, co-skewness, co-kurtosis, downside-beta) on the real on-disk USDT-M 5m `perp_close`, economically distinct from C317 own-moment factors (it trades the JOINT return distribution / systematic co-movement, not own variance or a liquidity/first-moment characteristic). No network ingest required.** `active_campaign: C318`; `oos_edge_proven: false`; `edge_claim: NONE`. **CLOSURE-TRAP (recurring session failure — still binding):** 283 `reports/program_closure_*` artifacts + generators `scripts/run_c305_program_closure_oos.py` and `scripts/run_program_closure_integrity_audit.py` are FROZEN stale C305-era output — the latest `program_closure_final_20261116T005430Z` still says `campaign:C305 / reachable...:CLOSED / genuinely_new_reachable_families=[]`, which is WRONG for the current state. They are NOT authoritative; do NOT re-run the closure generators and do NOT read any `program_closure_*` as "space closed". The authoritative state is `active_campaign:C318` (REGISTERED_NOT_STARTED).

## INITIAL TASK MESSAGE (2026-11-16T01:58:18Z) — BUILD + RUN C318 (cross-sectional covariance / beta co-movement factors), THEN VERIFY + CLOSE

**STATUS: COMPLETE — C318 built and run end-to-end (20261116T015818Z).** All steps executed: (1) bootstrap_dev_env ready; (2) C318 feature cache built from read-only C312 `perp_close` (27.82 MB, <100 MB, meta+provenance+SHA256, `real_data_only:true, fabricated_data:false, executed_fills:false`); (3) `preflight_c318.py --json` → `ready:true`, `blocked_reasons:[]`; (4) `run_c318_cov_beta_xsec_oos.py` → 5 artifacts + gitignored `full.json` with SHA256-from-bytes, 1440 pre-registered configs, Holm+BH reported; (5) `tests/test_preflight_c318.py` + `tests/test_c318_cov_beta_xsec_oos.py` added and passing; full `pytest tests/ -q` green (1727 passed / 2 skipped / 0 failed); (6) AGENTS.md + state.yaml synced with verdict/SHAs/binding constraint. Reachable space CLOSED (TEXT ONLY) — C318 was the last genuinely-new reachable heavy family. **Do NOT re-run/re-skin/re-probe C281B–C317 or C287; do NOT run the C305 closure generators or emit new `program_closure_*` reports.**

**Mission (repo priority = cryptoquantstatarbstrats → costed OOS stat-arb PnL on real, provable data):** C281B–C317 are ALL formal negatives and remain FROZEN (do not rerun/re-skin/re-probe). C287 is externally blocked (out-of-env only). **Exactly one genuinely-new reachable heavy family remains — register, build, and execute it this session: C318, cross-sectional COVARIANCE / BETA (co-movement) factors on the real on-disk USDT-M 5m data.** This is economically distinct from every frozen family (carry/OFI/basis/lead-lag = C281B–C314; price first-moment momentum/reversal = C315; size/volume/turnover liquidity = C316; own realized-vol / higher-moment = C317) and is NOT a re-skin: it trades the JOINT (systematic co-movement / covariance) structure of the return distribution — beta, correlation, co-skewness, co-kurtosis, downside-beta — not a single asset's own variance, not the first moment, and not a liquidity/size characteristic. A session that only re-attests closure, re-runs C281B–C317, or re-probes C287 is non-compliant and NOT economic progress.

**THE PRIMARY DE-BOTTLENECK (no network ingest — all data already on disk, SHA-verified):**
- `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` — 10 perps (BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,LINK,AVAX)USDT, 315,648 common-grid 5m bars, 2023-01..2025-12. C318 needs only `perp_close` (real 5m close) to derive `log_return` and the equal-weight market return `r_m = mean_i r_i`. No download bottleneck — the heavy work is the feature build + preflight + costed OOS sweep + gates + attribution + tests + artifacts.
- C318 MAY reuse `data/cache/campaign317_vol_moment_5m/` read-only (it holds `index_ms`, `perp_close`, `log_return`, `funding_rate`) OR build its own cache from C312 `perp_close`. To force independent provenance and heavy work, C318 MUST add its own `scripts/build_c318_cov_beta_features.py` (own `<100 MB` cache + meta + provenance + SHA256) even if the arrays are identical to C317.

**C318 CAMPAIGN SPECIFICATION (non-negotiable, heavy-work forcing):**
- **Objective:** prove or retract costed OOS edge for cross-sectional covariance / beta (co-movement) factors on 10 USDT-M linear perps, 2023-01..2025-12, native 5m.
- **Market return:** `r_m,t = mean_i r_i,t` (equal-weight cross-sectional mean of causal log-returns per bar). All co-movement signals are computed vs this market return.
- **Signals (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral gross 1.0; risk-factor sign so LONG LOW co-movement / SHORT HIGH co-movement):**
  - `beta` = trailing-L OLS slope of `r_i` on `r_m` = cov(r_i,r_m)/var(r_m); score = `-beta` (betting-against-beta: long low-beta, short high-beta).
  - `corr` = trailing-L Pearson correlation of `r_i` vs `r_m`; score = `-corr` (long low-correlation diversifiers, short high-correlation).
  - `coskew` = trailing-L co-skewness = mean(rd_i · rd_m^2) / (std(rd_i)·std(rd_m)^2) with demeaned returns; score = `-coskew` (avoid high systematic co-skew / market-lottery).
  - `cokurt` = trailing-L co-kurtosis = mean(rd_i · rd_m^3) / (std(rd_i)·std(rd_m)^3) with demeaned returns; score = `-cokurt` (avoid high tail co-movement).
  - `dsbeta` = trailing-L downside beta = cov(min(r_i,0), min(r_m,0)) / var(min(r_m,0)); score = `-dsbeta` (avoid high downside co-movement).
  - Hold rebalance {6,12,48} bars; lookback L {288, 1008, 2016}. Warm-up: full-window trailing -> first L-1 bars NaN (fail-closed, never traded).
- **Data handling (fail-closed):** derive `log_return` from `perp_close` (r[0]=0). A lookback without enough finite observations yields NaN -> not traded. Never fabricate/impute. `funding_rate` all-NaN -> control only, excluded from PnL.
- **Cost Model (real, charged on turnover):** fee {1,5,10,20} bps/leg; slippage {1,2,5,10} bps/leg; `symmetric`=(fee+slip) and `perp_heavy`=(1.5·fee+slip). Perp funding unreachable (fapi 451) -> excluded (control only).
- **Walk-Forward / OOS:** expanding train 12m -> test 3m, roll 3m over 36m (8 splits). Multiple-testing: Holm-Bonferroni AND Benjamini-Hochberg alpha=0.05 — BOTH must pass. MDE gate (observed mean vs MDE mean). Stability gate (sign consistency >=70% splits; first/second-half Sharpe corr >=0.5). Attribution gate (dominant of {beta/BAB, correlation, comoment, placebo} share > 0.5 for a positive claim).
- **Artifacts (MUST emit all 5 + gitignored full.json, bounded <100 MB):** `reports/campaign318_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` + gitignored `campaign318_oos_sweep_<TS>.full.json`, each with SHA256-from-bytes and `real_data_only:true,fabricated_data:false,executed_fills:false`.
- **Scripts (MUST add):** `scripts/build_c318_cov_beta_features.py`, `scripts/preflight_c318.py`, `scripts/run_c318_cov_beta_xsec_oos.py`.
- **Tests (MUST add + pass):** `tests/test_preflight_c318.py`, `tests/test_c318_cov_beta_xsec_oos.py`; full suite green.

**Execute in order (all required):**
1. `python scripts/bootstrap_dev_env.py` (deps importable).
2. Build the C318 feature cache from the real on-disk C312 `perp_close` shards (read-only; no network). Emit a `<100 MB` feature cache + `<cache>.meta.json` + `.provenance.json` with SHA256 and the three flags.
3. `python scripts/preflight_c318.py --json` -> `ready:true`, `blocked_reasons:[]` (fail-closed; any SHA mismatch -> BLOCK).
4. Run `scripts/run_c318_cov_beta_xsec_oos.py` -> emit the 5 artifacts + gitignored full.json with SHA256-from-bytes; 1440 pre-registered configs with Holm+BH reported.
5. Add/pass `tests/test_preflight_c318.py` + `tests/test_c318_cov_beta_xsec_oos.py`; run `python -m pytest tests/ -q` -> full suite green.
6. Sync `AGENTS.md` + `research_state/state.yaml` with C318 verdict/SHAs/binding constraint. Register the next genuinely-new family as active ONLY if one exists after C318; otherwise declare the space CLOSED (TEXT ONLY — never regenerate `program_closure_*`). Never create `HANDOFF.md`.
7. Do NOT re-run/re-skin/re-probe C281B–C317 or C287.

**Definition of Done (C318):** all 5 artifacts + full.json on disk with SHA256 provenance; 1440 configs tested with Holm+BH reported; `edge_proven:true` OR formal negative with `binding_constraint`; feature cache <100 MB with correct flags; preflight ready:true; tests green; full suite green; state + handoff synced.

**Guardrails (enforced — C318 session):**
- **No fabricated data / fail-closed / provenance-first:** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; SHA256-from-bytes for every artifact; missing/None/false gates BLOCK.
- **Bounded resources:** per-asset `.npz` shards, each cache <100 MB; slim sweep artifact <100 MB (no per-bar series) + gitignored `full.json`.
- **No overfitting:** ALL pre-registered configs reported; Holm+BH alpha=0.05 BOTH must pass; MDE + stability + attribution required.
- **Costs real:** per-leg fee/slippage grid charged on turnover; model PnL labeled `executed_fills:false`. Perp funding unreachable (fapi 451) -> excluded.

**Frozen/blocked (do NOT rerun, re-skin, re-probe, or pivot to):**
- **C281B–C317** — formal negatives (0/15,000+ configs survive Holm+BH). Re-running, re-skinning, or re-probing any of these is a hard violation.
- **C287** — external-only geographic/credential block (testnet 451, fapi 451, bybit 403, no creds). Do NOT re-probe C287 routes as economic work; unblocking requires out-of-env action only.
- **Closure machinery (stale — do NOT run):** `scripts/run_c305_program_closure_oos.py`, `scripts/run_program_closure_integrity_audit.py`, and all 283 `reports/program_closure_*` files are FROZEN C305-era artifacts (latest `program_closure_final_20261116T005430Z` = `campaign:C305 / CLOSED / genuinely_new_reachable_families=[]`). Re-running them or writing new closure reports is a hard violation — it re-declares the space CLOSED against the live C318 campaign. Authoritative pointer is `active_campaign:C318`.

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
- **C318 (COMPLETE FORMAL NEGATIVE, 20261116T015818Z):** cross-sectional COVARIANCE / BETA co-movement stat-arb (beta/BAB, correlation, co-skewness, co-kurtosis, downside-beta), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; dominant attribution comoment 0.5997 (beta 0.0462, correlation 0.2449, placebo_noise 0.1093); 5 artifacts + full.json + 27 C318 tests green; full suite 1727 passed / 2 skipped / 0 failed (426 s). De-bottleneck: real 5m prices on disk from C312 (no network ingest). LAST genuinely-new reachable heavy family — reachable space CLOSED (TEXT ONLY).
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