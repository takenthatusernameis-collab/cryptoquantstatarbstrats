# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-16T07:55:50Z (re-verified this session: `python scripts/verify_env.py --json` → `ready:true`, `missing:[]` on Python 3.12.3; C323 COMPLETE formal negative — verdict + 5 SHA256-from-bytes artifacts on disk at 20261116T074752Z, 26/26 C323 tests green; C312 5m cache `data/cache/campaign312_usdt_m_ofi_5m/` with `perp_close,signed_volume,total_volume,trade_sign_sum,trade_count,notional` readable for C324). No closure-by-fiat; next heavy work is C324.
**Program state:** `ACTIVE — NO-EDGE CONFIRMED, NEXT FAMILY MANDATED`. C281B–C323 are ALL COMPLETE FORMAL NEGATIVES (0 tradable costed-OOS edge across ~30,135 pre-registered configs; binding constraint universally `multiple_testing`). Terminal "closure by fiat" is PROHIBITED: the only honest exit is executing every pre-registered genuinely-new family on real on-disk data until one is proven unreachable with on-disk evidence. **C323 (cross-sectional intraday ORDER-FLOW & TRADE-ACTIVITY SEASONALITY mean-reversion, 20261116T074752Z, 1440 configs, 0 deterministic edge, 0 survive Holm+BH)** is the newest COMPLETE formal negative. **C324 (cross-sectional intraday AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION mean-reversion) is the mandated next heavy campaign (spec below); C324 scripts/tests/cache/artifacts are NOT yet on disk.**
**Bottleneck status (re-verified 2026-11-16T07:55:50Z):** `verify_env.py --json` → `ready:true`, `missing:[]`; C312 5m + C319–C323 caches/artifacts present and readable; no data/env/network blockers for C324 (build/preflight/run/tests + verdict artifacts are mandatory next heavy work on real on-disk C312 5m data). Pre-existing known full-suite note: frozen C313 gitignored full-sweep gap (not a blocker).
**Closure audit (C281B–C318 scope, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318; C319–C323 extend the record and are also formal negatives. Do NOT regenerate/run stale closure generators.
**Latest campaigns:** C323 COMPLETE FORMAL NEGATIVE (20261116T074752Z, cross-sectional intraday ORDER-FLOW & TRADE-ACTIVITY SEASONALITY mean-reversion, 1440 configs, 0 survive Holm+BH, binding `multiple_testing`). C322 COMPLETE FORMAL NEGATIVE (20261116T073235Z, VWAP-close fair-value dislocation, 1440 configs, 0 survive Holm+BH). C321 COMPLETE FORMAL NEGATIVE (20261116T063209Z, intraday range/breakout/overnight-intraday seasonality, 1440 configs, 0 survive Holm+BH). C320 COMPLETE FORMAL NEGATIVE (20261116T053110Z, intraday TOD/DOW seasonality, 1440 configs, 0 survive Holm+BH). `oos_edge_proven: false`; `edge_claim: NONE`.

## INITIAL TASK MESSAGE (2026-11-16T07:55:50Z) — MANDATORY HEAVY WORK: BUILD + RUN C324 (NEXT AGENT START HERE)

**Mission (repo priority):** crypto quantitative statistical arbitrage — costed out-of-sample PnL on real, provable data. Economic progress = a real-data costed-OOS run, a passing test, or an artifact update. A session that only re-reads this handoff, re-declares closure, or re-runs a frozen campaign is NOT economic progress and is a hard violation.

**State of the record:** C281B–C323 are ALL COMPLETE FORMAL NEGATIVES on real data (~30,135 pre-registered configs; binding constraint universally `multiple_testing`; C323 newest: cross-sectional intraday ORDER-FLOW & TRADE-ACTIVITY SEASONALITY mean-reversion, 20261116T074752Z, 1440 configs, 0 deterministic edge, 0 survive Holm+BH, real artifacts + SHAs on disk, 26/26 C323 tests green). No costed-OOS edge has ever survived. That is a RESULT, not a reason to stop: keep executing pre-registered genuinely-new families on the real on-disk 5m data (C312 cache) until one is proven unreachable with on-disk evidence.

**MANDATORY NEXT CAMPAIGN — C324: cross-sectional intraday AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION mean-reversion (native USDT-M 5m).**
- **Data (on disk, real, no network):** `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` → `perp_close`, `signed_volume`, `total_volume`, `trade_sign_sum`, `trade_count`, `notional` (10 perps, 315,648 common 5m bars, 2023-01..2025-12). Derive causal `log_return` and illiquidity `illiq = |log_return| / notional` (NaN where `notional<=0`). Funding all-NaN (control only). Mirror the C322/C323 build→preflight→run→test pipeline.
- **PRE-REGISTERED zero-activity/NaN POLICY (follow exactly, no improvisation):** `illiq` NaN where `notional<=0`; `log_tc = log(trade_count)` NaN where `trade_count<=0` (control cross-check). Same-time-of-day trailing mean/std/ewm are NaN-aware with explicit `min_periods=L` and EXCLUDE NaN same-tod observations — do NOT forward-fill, do NOT impute, do NOT drop the whole shard, do NOT treat NaN as 0. Any asset whose feature is NaN at bar t receives cross-sectional weight 0 at t (others renormalized to gross 1.0). Preflight must report per-shard NaN counts/shares for each derived field and assert denominator-zero NaNs are 100% explained by the corresponding zero-activity bars and share < 0.1% (fail-closed on unexplained NaNs or corrupt data).
- **Genuinely-new vs prior families:** C316 = size/volume/turnover liquidity as level/rank characteristics; C317 = own realized-vol/higher-moment; C318 = return covariance/beta; C319 = price-level cointegration/pairs; C320 = intraday TOD/DOW seasonal RETURN mean-reversion; C321 = intraday range/breakout/overnight-vs-intraday structure; C322 = intraday VWAP-close fair-value anchor; C323 = causal same-tod ORDER-FLOW & TRADE-ACTIVITY SEASONALITY deviations. C324 is DISTINCT: it trades **causal same-time-of-day seasonal deviations of AMIHUD ILLIQUIDITY** (price impact per unit volume, |log_return|/notional) vs each asset's own trailing same-tod baseline — a liquidity/price-impact signal source, different from C323's flow/activity intensity and C316's size levels. Do not re-skin C316/C323.
- **Signals (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral gross 1.0; score = -seasonal-dislocation):** `illiq_dev` = illiq_t − trailing_mean_L(illiq at same tod); score = −dev (Amihud illiquidity seasonality); `illiq_ewm` = illiq_t − causal ewm_mean_L(illiq at same tod); score = −dev; `tc_dev` = log_tc_t − trailing_mean_L(log_tc at same tod); score = −dev (trade-count intensity cross-check). `illiq_placebo` attribution bucket (permuted returns) that is NOT a signal. Finalize names in `scripts/build_c324_*.py`.
- **Grid:** 3 signals × lookback{30,60,90 days} × rebalance{6,12,48 bars} × fee{1,5,10,20}bps × slip{1,2,5,10}bps × cost_variant{symmetric,perp_heavy} = 864 pre-registered configs, ALL reported.
- **Gates (fail-closed):** expanding WF 12m/3m/3m (8 splits); one-sided paired t per split; Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH required); MDE; stability (sign-consistency ≥ 0.70, first/second-half Sharpe corr ≥ 0.5); signal-vs-placebo attribution (dominant share > 0.5). Artifacts `reports/campaign324_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` (+ gitignored full.json), SHA256-from-bytes, `real_data_only:true, fabricated_data:false, executed_fills:false`.
- **Definition of Done (the ONLY acceptable session outcome):** a C324 verdict artifact exists on disk with a real verdict (`EDGE_PROVEN` or `RETRACTED` + binding constraint) and 5 SHA256-from-bytes artifacts, AND `python -m pytest tests/test_c324_* tests/test_preflight_c324.py -q` is green.
- **NO-COAST CLAUSE:** do NOT exit with "reachable space closed / no new campaign". Exiting without a C324 verdict artifact (or on-disk proof, with exact error text, that C312 5m data is unreachable/corrupt) is a hard violation. If C324 is itself a formal negative, immediately proceed to C325 on the same C312 5m data — do NOT re-declare closure.
- **Do NOT** rerun/re-skin C281B–C323; do NOT run stale closure generators; do NOT create `HANDOFF.md`.

**START HERE — execute in this order, no improvisation, no closure talk:**
1. `python scripts/verify_env.py --json` → require `ready:true`, `missing:[]` (re-run only after an unexplained dependency error).
2. Create exactly these five files, mirroring C323's structure/APIs: `scripts/build_c324_illiq_seasonality_features.py`, `scripts/preflight_c324.py`, `scripts/run_c324_illiq_seasonality_xsec_oos.py`, `tests/test_preflight_c324.py`, `tests/test_c324_illiq_seasonality_xsec_oos.py`. Use `<family>` = `illiq_seasonality`.
3. Build the feature cache: read-only derivation from `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` into `data/cache/campaign324_illiq_seasonality_5m/` (10 shards; fields `index_ms`, `perp_close`, `log_return`, `illiq`, `log_tc`, `funding_rate` all-NaN; `<100 MB`, `real_data_only:true, fabricated_data:false, executed_fills:false`, causal `shift(1)` only, no network/resample/impute). Apply the PRE-REGISTERED zero-activity/NaN POLICY verbatim.
4. `python scripts/preflight_c324.py --json` → require `ready:true`, `blocked_reasons:[]`, 10/10 shards, full 315,648-bar grid in window, and per-field denominator-zero NaNs < 0.1% and 100% explained by zero-activity bars (fail-closed otherwise).
5. Run the full 864-config sweep to real artifacts at `reports/campaign324_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<ts>.json` plus gitignored `full.json`; verify 5 SHA256-from-bytes and `edge_proven` is a real boolean.
6. `python -m pytest tests/test_c324_* tests/test_preflight_c324.py -q` → must be green.
7. Update ONLY `AGENTS.md` and `research_state/state.yaml` with the new verdict, binding constraint, all 5 artifact SHAs, config counts, attribution shares, and test counts. Do NOT create `HANDOFF.md`; do NOT touch frozen C281B–C323 artifacts.
8. If C324 is a formal negative, immediately start C325 on the same C312 5m data (next genuinely-new family); a C324 negative is a RESULT, not permission to stop.

**C323 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T07:47:52Z):**
- **Scripts PRESENT on disk:** `scripts/build_c323_flow_activity_seasonality_features.py`, `scripts/preflight_c323.py`, `scripts/run_c323_flow_activity_seasonality_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c323.py`, `tests/test_c323_flow_activity_seasonality_xsec_oos.py` (26/26 C323 tests green, `pytest tests/test_c323_* tests/test_preflight_c323.py -q`).
- **Feature cache COMPLETE (real data, ~67.48 MB):** `data/cache/campaign323_flow_activity_seasonality_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `ofi_ratio`, `tss_ratio`, `log_tc`, `log_notional`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of real C312 shards; no network, no resampling, no imputation. PRE-REGISTERED zero-activity NaN POLICY applied: `ofi_ratio=signed_volume/total_volume` NaN where `total_volume==0`; `tss_ratio=trade_sign_sum/trade_count` NaN where `trade_count==0`; `log_tc=log(trade_count)` NaN where `trade_count<=0`; `log_notional=log(notional)` NaN where `notional<=0` (24 bars/shard, BTC 43; ≤0.014%, <0.1%, 100% explained).
  - meta SHA256 `ac525374479337040ff6876dc6d8fac7ba96744366cafbe497de02684a93877f`; provenance SHA256 `ae435a968dec9f349aad2ab419c5c48f39d78cf954a127cf95a58c31b637cf52`; manifest SHA256 `057719eae950029797b63814183b97c1ed8c8abfa6e42dcc7ddf192e2bc32960`.
- **Preflight:** `python scripts/preflight_c323.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window, per-field denominator-zero NaNs < 0.1% and 100% explained by zero-activity bars.
- **Runner/artifacts COMPLETE at `20261116T074752Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: ofi_dev 0.1861, tss_dev 0.1734, tc_dev 0.1243, notional_dev 0.1434, ofi_ewm 0.1864, flow_placebo 0.1864 (dominant ofi_ewm 0.1864 < 0.5 → attribution_ok false, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `af63f3afd4046b016cb05f2c9a869debed77a28df518ed95e0de8724421cbdf1` (slim ~1.1 MB)
  - tradable_edge_registry `676335194f28d593b47ee77dccb23612cfa405dc6c1c75f04b7d8efdaa49a639`
  - summary `0b94f85f14292b46fa31e69de84114d5bf70b9442b66cc981cbab06092a4fd8e`
  - verdict `63aed80f095c44da3ef78534737a3a66a2a6bfc52530b9912ca726ad115ce110`
  - binding_constraint `e4ac4447d6bd237270fdfa58a52cb8b028c892ed2712bc6d6d11ca208a6edf83`
  - full sweep kept on disk as `reports/campaign323_oos_sweep_20261116T074752Z.full.json` (gitignored).
- **Scripts PRESENT on disk:** `scripts/build_c322_vwap_dislocation_features.py`, `scripts/preflight_c322.py`, `scripts/run_c322_vwap_dislocation_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c322.py`, `tests/test_c322_vwap_dislocation_xsec_oos.py` (23/23 C322 tests green, `pytest tests/test_c322_* tests/test_preflight_c322.py -q`).
- **Feature cache COMPLETE (real data, ~47.11 MB):** `data/cache/campaign322_vwap_dislocation_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `vwap`, `log_vwap`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of real C312 shards; no network, no resampling, no imputation. PRE-REGISTERED vwap-NaN POLICY applied: `log_vwap=log(vwap)` where `vwap>0` else NaN; vwap NaNs only where `total_volume==0` (24 bars/shard, BTC 43; 0.008–0.014%, <0.1%, 100% explained).
  - meta SHA256 `cf8ee550b3e84467d13008ad93702bfbe69e6e94418ad76b14f467b503a4ae2b`; provenance SHA256 `45fbe0251654e7df47aa9732d1fd7785c3c800a811365130fae9ff9143024c7a`; manifest SHA256 `8850e31fcf1a2522084ee428dc7715640a770e67ae568ca7d70fb71ec1eaadd3`.
- **Preflight:** `python scripts/preflight_c322.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window, per-shard vwap NaN share < 0.1% and 100% explained by `total_volume==0`.
- **Runner/artifacts COMPLETE at `20261116T073235Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: vwap_dev 0.020703, vwap_z 0.031654, close_vwap_spread 0.453237, vwap_ewm 0.021669, vwap_vol_z 0.450090, placebo_noise 0.022647 (dominant close_vwap_spread 0.453237 < 0.5 → attribution_ok false, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `fea5571b738e0dae3c9e85c6f5a14ad2f7f6a2144b6be479f638907dd60fb37e` (slim ~1.1 MB)
  - tradable_edge_registry `8b31b157d0f2d2c81bf6e8777d7128d0b5a2a572d7adb27a894942b685288139`
  - summary `9ccfa1a9e1d78585fdea7fb1ae882bb2c223218ffc73f2b6d2b8ee3945ec4655`
  - verdict `fa3801146177874f3c92b7365c1511f4b616978bce541d5ac8b6103f802817ab`
  - binding_constraint `5ad2bf982fa7d4460729a6e16ab3df152d6033d4525966746a6d1f910349fca0`
  - full sweep kept on disk as `reports/campaign322_oos_sweep_20261116T073235Z.full.json` (gitignored).

**C321 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T06:33:00Z):**
- **Scripts PRESENT on disk (uncommitted):** `scripts/build_c321_intraday_range_breakout_features.py`, `scripts/preflight_c321.py`, `scripts/run_c321_intraday_range_breakout_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c321.py`, `tests/test_c321_intraday_range_breakout_xsec_oos.py` (31/31 C321 tests green).
- **Feature cache COMPLETE (real data, ~27.82 MB):** `data/cache/campaign321_intraday_range_breakout_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 27.82 MB, max shard ~3.0 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of the real C312 shards; no network, no resampling, no imputation.
  - meta SHA256 `b392be5a1dd86f00c275a7adc78c06b1d2dce294d27fb960908ba1a92d441045`; provenance SHA256 `63764aeea06ec259946d70901b10114376b2ad7f052a63951d91c0f892284d1e`; manifest SHA256 `2ae4306465c17467090dfc136faa3aee4d06f2e27fb47c85aab514ddb4b87ddf`.
- **Preflight:** `python scripts/preflight_c321.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T063209Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: range_dev 0.2166, brk_dev 0.1253, oi_dev 0.0050, vol_z 0.2216, ewm_dev 0.2184, placebo_noise 0.2131 (dominant vol_z 0.2216 < 0.5 → attribution_ok false, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `2eb22256356a327495fbcbd9adb375dd6c036c29ee131735d5549d70d6c1f0c5` (slim ~1.0 MB)
  - tradable_edge_registry `f3cd56221e7ff777812d82a1c8cc5e0d71f63baf017047f541ea264c3a5fff1d`
  - summary `cf076b85be58bee7c2eeb37a93d6355820cec4e148440b065992004c60b69842`
  - verdict `57ec836c9cf697fd31b6a9fc7b5e7a93ce8cf500217d69ca40ee1b00929417e4`
  - binding_constraint `d53bf316dc05b1ca6ff733c997b4d8b6de4d47fabea47f25860bd2cdd296a3a5`
  - full sweep kept on disk as `reports/campaign321_oos_sweep_20261116T063209Z.full.json` (gitignored).

**C320 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T05:43:30Z):**
- **Scripts PRESENT and COMMITTED (working tree clean):** `scripts/build_c320_tod_seasonality_features.py`, `scripts/preflight_c320.py`, `scripts/run_c320_tod_seasonality_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c320.py`, `tests/test_c320_tod_seasonality_xsec_oos.py` (26/26 C320 tests green).
- **Feature cache COMPLETE (real data, ~27.82 MB):** `data/cache/campaign320_tod_seasonality_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 27.82 MB, max shard ~3.0 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of the real C312 shards; no network, no resampling, no imputation.
  - meta SHA256 `9f670189d68e69264fa77a61fa71769c533e95541a0b7277b1b98a920f4f2d15`; provenance SHA256 `79f78d7d6e225e6f1df764c94de8e8b74922124c97336eed3cc0c92b277cf909`; manifest SHA256 `2ae4306465c17467090dfc136faa3aee4d06f2e27fb47c85aab514ddb4b87ddf`.
- **Preflight:** `python scripts/preflight_c320.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T053110Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: tod_dev 0.1684, tod_z 0.1679, dow_dev 0.1579, tod_rv 0.1679, tod_ewm 0.1687, placebo_noise 0.1692 (dominant placebo_noise 0.1692 < 0.5 → attribution_ok false, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `aa70118a1dc9010e71953540ee88e6e2b1e76434c319e87ccb1b420b2cc70b0f` (slim ~1.0 MB)
  - tradable_edge_registry `7e2db6c6e7b4f09ef06f3b18168f0a2a9546f23c40f1aad32a50b6f99a139b0d`
  - summary `df83c516d4bbe4237feecd64cc656c6ec22dc3d66bcc7eae96f466a5d9e89b35`
  - verdict `c469aeb52824933ea7a23db3a6d1f296c0452ed75b0ec274043bde8a460689cc`
  - binding_constraint `5da5e941ccc516c5b3b58732217b38802f191317f369e11632e6d4fc3c687b25`
  - full sweep kept on disk as `reports/campaign320_oos_sweep_20261116T053110Z.full.json` (gitignored).

**Frozen/blocked (hard violations if touched):**
- **C281B–C323:** FROZEN formal negatives — do NOT rerun, re-skin, re-probe, or "revalidate".
- **C287:** externally blocked/decoupled (451/403, no creds) — out-of-env only; never retry as economic work.
- **Stale closure machinery:** `scripts/run_c305_program_closure_oos.py`, `scripts/run_program_closure_integrity_audit.py`, and prior `reports/program_closure_*` C305-era artifacts are FROZEN/misleading — do NOT run or cite as current state. The C281B–C318 audit `reports/program_closure_final_20261116T024519Z.json` (sha above) is the only citable closure audit; C319–C323 extend it.

**Environment / verification:**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.5, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

**Last verified (2026-11-16T07:55:50Z):** `python scripts/verify_env.py --json` → `ready:true`, `missing:[]`. Prior verified: C323 tests **26 passed**, C322 **23 passed**, C321 **31 passed**; C312/C319–C323 caches and C323 artifacts readable; C323 formal negative (20261116T074752Z, 1440 configs, 0/0/0 Holm/BH/both, binding multiple_testing). Note: full suite has a PRE-EXISTING frozen C313 gitignored full-sweep failure — NOT a regression. Running the full suite regenerates `reports/program_closure_final_<TS>.json` (side-effect); pinned citable audit remains `...024519Z.json` (sha `aebd52…`). **No data/env bottlenecks for C324; proceed to C324 immediately.**

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

## C319 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-16T04:54:43Z)

- **Scripts PRESENT (uncommitted):** `scripts/build_c319_cointegration_features.py`, `scripts/preflight_c319.py`, `scripts/run_c319_cointegration_xsec_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c319.py`, `tests/test_c319_cointegration_xsec_oos.py` (30/30 C319 tests green).
- **Feature cache COMPLETE (real data, ~27.82 MB):** `data/cache/campaign319_cointegration_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `perp_close`, `log_return`, `funding_rate` (all-NaN control-only). 315,648 common-grid 5m bars, 2023-01..2025-12. Total 27.82 MB, max shard 3.0 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`. Read-only derivation of the real C312 shards; no network, no resampling, no imputation.
  - meta SHA256 `16d1ec7b6fee8c13a8ae4c08750ca5ab395d7b0f4ff7301bdce09d3b6973b23f`; provenance SHA256 `4753fd07704103c79f5ebe3ccc2a3830f3e45ec7e1b4d0a87e4a96bdc9030bd1`; manifest SHA256 `2ae4306465c17467090dfc136faa3aee4d06f2e27fb47c85aab514ddb4b87ddf`.
- **Preflight:** `python scripts/preflight_c319.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261116T045428Z`:** 1440 pre-registered configs (signal×lookback×rebalance×fee×slip×cost_variant), expanding WF 12m/3m/3m (8 splits). **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; 1440/1440 configs had real exposure. Attribution shares: hedge_z 0.2558, relative_value 0.2558, halflife 0.2624, placebo_noise 0.2261 (dominant halflife 0.2624 < 0.5 → attribution_ok false, but no edge to attribute). All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `180acf79520aa1c88de25cdd5f44264a2e76ea9c6afdbc186f969049fa460dd5` (slim ~1.0 MB)
  - tradable_edge_registry `9da376ae4f1226f3b91fdd3a1b59d0805bcd3cee575a01041b3550f9adce0b1e`
  - summary `b2fea8e2d06a50f6b85323465d6c9a7bd959a059c0eddbb9284a6d646ce80860`
  - verdict `efa9136e013d78a6488e6d12632f5c1460273f7af733a36f3c1efb6cbedf83bf`
  - binding_constraint `1ab52a4c639c642c8ad8f374e20c0cd9af05d04fe44519ca9eab557d19b8bc15`
  - full sweep kept on disk as `reports/campaign319_oos_sweep_20261116T045428Z.full.json` (gitignored).

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
Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `perp_close` usable by C315/C317/C318, `vwap`/`signed_volume`/`trade_sign_sum`/`notional` usable by C322/C323). Scripts/tests/artifacts present; VERDICT: RETRACTED, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

## Bottlenecks removed / guardrails
- **C314 microsecond spot open_time (2025-01+) NORMALIZED to ms** in ingest (`normalize_open_time_ms`) — the key fix that made spot/perp 5m intersect across the full 36 months. Covered by a regression test.
- **C315–C323 DONE** — real 5m prices/fields already on disk (C312 cache); no download bottleneck. All are COMPLETE FORMAL NEGATIVES (see Escalation); do not rerun. C324 is the mandated next heavy family (see INITIAL TASK MESSAGE).
- **C322 de-bottleneck (verified 2026-11-16T07:32:35Z):** C322 VWAP-dislocation is COMPLETE FORMAL NEGATIVE (cache built, preflight ready, 1440-config run, 5 artifacts, 23/23 tests green). C312 flow/activity fields (`signed_volume,total_volume,trade_sign_sum,trade_count,notional`) confirmed on disk for C323 — C323 fully data-unblocked (no network/ingest); apply pre-registered zero-activity NaN-aware policy (ratios/logs NaN where denominators/values <=0, exclude, weight 0).
- Resumable manifest ingest (per symbol/market/month) where ingest is needed; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C321 frozen.
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

- **C323 (COMPLETE FORMAL NEGATIVE, 20261116T074752Z):** cross-sectional intraday ORDER-FLOW & TRADE-ACTIVITY SEASONALITY DISLOCATION mean-reversion stat-arb (ofi_dev, tss_dev, tc_dev, notional_dev, ofi_ewm; score = -seasonal-dislocation; causal shift(1); cross-sectional rank; dollar-neutral gross 1.0), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution shares ofi_dev 0.1861 / tss_dev 0.1734 / tc_dev 0.1243 / notional_dev 0.1434 / ofi_ewm 0.1864 / flow_placebo 0.1864 (dominant ofi_ewm 0.1864 < 0.5 → attribution_ok false, but no edge to attribute); 5 artifacts + full.json + 26 C323 tests green. De-bottleneck: real 5m perp_close+signed_volume+total_volume+trade_sign_sum+trade_count+notional on disk from C312 (no network ingest; pre-registered NaN-aware ratio/log policy applied). NEWEST modern family.
- **C322 (COMPLETE FORMAL NEGATIVE, 20261116T073235Z):** cross-sectional VWAP-CLOSE FAIR-VALUE DISLOCATION mean-reversion stat-arb (vwap_dev, vwap_z, close_vwap_spread, vwap_ewm, vwap_vol_z; score = -fair-value-dislocation; causal shift(1); cross-sectional rank; dollar-neutral gross 1.0), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution shares vwap_dev 0.0207 / vwap_z 0.0317 / close_vwap_spread 0.4532 / vwap_ewm 0.0217 / vwap_vol_z 0.4501 / placebo_noise 0.0226 (dominant close_vwap_spread 0.4532 < 0.5 → attribution_ok false, but no edge to attribute); 5 artifacts + full.json + 23 C322 tests green. De-bottleneck: real 5m perp_close+vwap on disk from C312 (no network ingest; pre-registered NaN-aware vwap policy applied).
- **C321 (COMPLETE FORMAL NEGATIVE, 20261116T063209Z):** cross-sectional INTRADAY RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY SEASONALITY mean-reversion stat-arb (range_dev, brk_dev, oi_dev, vol_z, ewm_dev; score = -seasonal-mispricing; causal shift(1); cross-sectional rank; dollar-neutral gross 1.0), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution shares range_dev 0.2166 / brk_dev 0.1253 / oi_dev 0.0050 / vol_z 0.2216 / ewm_dev 0.2184 / placebo_noise 0.2131 (dominant vol_z 0.2216 < 0.5 → attribution_ok false, but no edge to attribute); 5 artifacts + full.json + 31 C321 tests green.
- **C320 (COMPLETE FORMAL NEGATIVE, 20261116T053110Z):** cross-sectional INTRADAY TIME-OF-DAY / DAY-OF-WEEK SEASONALITY mean-reversion stat-arb (tod_dev, tod_z, dow_dev, tod_rv, tod_ewm; score = -seasonal-mispricing; causal shift(1); cross-sectional rank; dollar-neutral gross 1.0), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution shares tod_dev 0.1684 / tod_z 0.1679 / dow_dev 0.1579 / tod_rv 0.1679 / tod_ewm 0.1687 / placebo_noise 0.1692 (dominant placebo_noise 0.1692 < 0.5 → attribution_ok false, but no edge to attribute); 5 artifacts + full.json + 26 C320 tests green. De-bottleneck: real 5m prices on disk from C312 (no network ingest).
- **C319 (COMPLETE FORMAL NEGATIVE, 20261116T045428Z):** cross-sectional COINTEGRATION / PAIRS mean-reversion stat-arb on price-level equilibrium residuals (hedge-z, relative-value z, unhedged beta=1 spread z, half-life-scaled z, level-correlation-scaled z), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution shares hedge_z 0.2558 / relative_value 0.2558 / halflife 0.2624 / placebo_noise 0.2261 (dominant halflife 0.2624 < 0.5 → attribution_ok false); 5 artifacts + full.json + 30 C319 tests green. De-bottleneck: real 5m prices on disk from C312 (no network ingest).
- **C318 (COMPLETE FORMAL NEGATIVE, 20261116T015818Z):** cross-sectional COVARIANCE / BETA co-movement stat-arb (beta/BAB, correlation, co-skewness, co-kurtosis, downside-beta), 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; dominant attribution comoment 0.5997 (beta 0.0462, correlation 0.2449, placebo_noise 0.1093); 5 artifacts + full.json + 27 C318 tests green. De-bottleneck: real 5m prices on disk from C312 (no network ingest).
- **C317 (COMPLETE FORMAL NEGATIVE, 20261116T013937Z):** cross-sectional realized-vol / higher-moment stat-arb, 1440 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`; attribution dominant lottery 0.6729 (low_volatility 0.0932, downside 0.1062, placebo 0.1277); 5 artifacts + full.json + 30 C317 tests green. De-bottleneck: real 5m prices on disk from C312 (no network ingest).
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