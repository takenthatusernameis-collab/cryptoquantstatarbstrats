# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-18T22:33:09Z (disk re-verified 2026-11-18T22:33:09Z). **Repo name `cryptoquantstatarbstrats` = crypto quantitative STATISTICAL ARBITRAGE — prioritization is therefore fixed: (1) cross-sectional relative-value stat-arb (dollar-neutral rank dispersion across the 10 USDT-M perps) is the PRIMARY axis, (2) seasonal-dislocation mean-reversion is the signal overlay on that primary axis, (3) costed out-of-sample validation with Holm+BH multiplicity control is the ONLY acceptance gate. Every campaign must be a stat-arb edge attempt on real on-disk C312 5m data, not a directional bet.** **C281B–C375 ALL FROZEN FORMAL NEGATIVES.** **C371 (RSK/RKT) FROZEN (20261118T151130Z):** 1296 configs, 0 Holm+BH survivors, `edge_proven:false`, binding `multiple_testing`, dominant `rkt_placebo` 0.4164. **C372 (TIRV) FROZEN (20261118T160248Z):** 0 survivors, dominant `tir4_placebo` 0.4789. **C373 (RLRV) FROZEN (20261118T202427Z):** 0 survivors, dominant `medrv_rv_ratio_placebo` 0.3766. **C374 (SIGNRUN) FULLY EXECUTED & FROZEN (20261118T212227Z):** 1296 configs costed-OOS, 0 Holm+BH survivors, `edge_proven:false`, RETRACTED, binding `multiple_testing`, dominant attribution `max_run_share_placebo` 0.4773; 5 SHA256 artifacts + cache on disk (SHAs in the C374 RESULT block). **C375 (ACOVK — MULTI-LAG REALIZED AUTOCOVARIANCE PROFILE) FULLY EXECUTED & FROZEN (20261118T222249Z):** 1296 configs costed-OOS, 0 Holm+BH survivors, `edge_proven:false`, RETRACTED, binding `multiple_testing`, dominant attribution `acov_sum_placebo` 0.4173; 5 SHA256 artifacts + cache on disk (SHAs in the C375 RESULT block). **C376 (QSPREAD — REALIZED QUANTILE SPREAD PROFILE) IS THE ACTIVE CAMPAIGN — PRE-SEEDED, EXECUTE END-TO-END NOW.** **Queue depth = 2 (C376 QSPREAD active → C377 PSLOPE pre-seeded) so the queue can never be empty.** **Bottlenecks: NONE.**

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a HARD VIOLATION. **This AGENTS.md is the single durable handoff — DO NOT create HANDOFF.md or any duplicate handoff file; update this file in place.**

> **INITIAL TASK MESSAGE (written 2026-11-18T22:33:09Z — ONE authoritative timestamp; supersedes all earlier session messages) — NEXT SESSION: EXECUTE C376 (QSPREAD — REALIZED QUANTILE SPREAD PROFILE) END-TO-END NOW. Disk re-verified this session: C375 scripts/tests/cache/5 artifacts present and frozen; NO `campaign376_*` file exists yet — all of C376 is pure work to do; C312 source 10 × 315,648 bars ready; deps numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0. START WITH HEAVY EXECUTION (WRITE CODE → BUILD CACHE → PREFLIGHT → FULL COSTED-OOS SWEEP → PYTEST → 5 SHA256 ARTIFACTS), NOT RE-READING, RE-PLANNING, OR PROSE. NO DOWNSCOPING, NO STUB/PROSE-ONLY OUTPUT, NO RE-RUN OF C281B–C375 OR C287. ZERO TOLERANCE FOR AVOIDANCE.**
>
> **EXECUTION CARD (copy-paste order, no thought required):**
> ```
> cp scripts/build_c375_acovk_features.py   scripts/build_c376_qspread_features.py
> cp scripts/preflight_c375.py                scripts/preflight_c376.py
> cp scripts/run_c375_acovk_xsec_oos.py       scripts/run_c376_qspread_xsec_oos.py
> cp tests/test_preflight_c375.py             tests/test_preflight_c376.py
> cp tests/test_c375_acovk_xsec_oos.py        tests/test_c376_qspread_xsec_oos.py
> # adapt the 5 files to the C376 QSPREAD spec below (qspread_ratio/qspread_asym replacing the ACOVK acov_sum/acov_decay metrics)
> python3 scripts/build_c376_qspread_features.py      # -> data/cache/campaign376_qspread_5m/
> python3 scripts/preflight_c376.py                 # must print ready:true
> python3 scripts/run_c376_qspread_xsec_oos.py        # FULL 1296-config costed OOS sweep
> python3 -m pytest tests/test_preflight_c376.py tests/test_c376_qspread_xsec_oos.py -q   # >=21 green
> sha256sum reports/campaign376_*_<TS>Z.json        # record 5 artifact SHAs
> ```
> Target artifacts: `reports/campaign376_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>Z.json` + gitignored `.full.json`.
> Repo `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Priority order is fixed by the repo name: **(1) cross-sectional relative-value stat-arb** — rank the 10 perps on the campaign signal, go dollar-neutral long-top/short-bottom (this is the arbitrage, never a directional bet); **(2) seasonal-dislocation mean-reversion overlay** — the signal itself is a causal seasonal-deviation score; **(3) costed OOS + Holm+BH validation** — the only acceptance gate, no gate weakening. The ONLY acceptable outcome is **real execution progress** — a real-data, costed, out-of-sample stat-arb edge attempt on on-disk C312 5m data — leaving durable artifacts on disk.
>
> **Verified state (2026-11-18T22:33:09Z, disk re-verified this session):** C281B–C375 ALL frozen formal negatives (0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`, RETRACTED). **C374 (SIGNRUN) DONE/FROZEN (20261118T212227Z):** 5 artifacts `reports/campaign374_*_20261118T212227Z.json` re-hashed this session — oos_sweep `80480e1f473cd7a50dbe9dd5a6c42b5824952f5d901a911472f51f346ac2d10d`, registry `ac605492ee9510f31d0334ff6165c5c623bc841d7817b8fe65360ff50422ae4a`, summary `5e0ae2bb8886343a5c99794b0596cc81d419b345750def40bf2fa7406df2f8ba`, verdict `cb9fd1d125741fab7dd43ff7efd9b8187319db7b24463f4908bdbe0f170adade`, binding_constraint `7492e120993be80822b3e080bc7124a94d4176ffc95e78d0a5805193b0bfa820`; cache `data/cache/campaign374_signrun_5m/` (10 shards × 315,648 bars, meta `5cfae24a64131505eefd2e3a70645b0186fd5ee6c8835e4bb7569f88b5df6653`, provenance `945b58c16d2080508b07a59543af5b427ccb5406a946868e45f6aef30cf45044`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`). **C375 (ACOVK) DONE/FROZEN (20261118T222249Z):** 1296 configs costed-OOS, 0 Holm+BH survivors, `edge_proven:false`, RETRACTED, binding `multiple_testing`, dominant attribution `acov_sum_placebo` 0.4173; 5 artifacts `reports/campaign375_*_20261118T222249Z.json` — oos_sweep `512ea714143752b6adedd92cff7904cf6ce4ea54ff4bb6f8dac241fc5358ee8f`, registry `02c2eca46cf256fec14b0107715dc633bbad56d5cc28fd0d7b39281e3807ea39`, summary `a3075f41ed6683669f48f8c8c671f6847be97a158544157c429cf82487f9f185`, verdict `19c52ccd115bab44dde1052bd77df34062b54d95a3896f65acfe3462fd667eb8`, binding_constraint `4bad255546d62dc2f16f8e654c237debbc564fd7b17767aaa2a9efc5862f9996`; cache `data/cache/campaign375_acovk_5m/` (10 shards × 315,648 bars, meta `00c8b7afa919a176139248b471c89f8fa501c68b6d227daa00488ed2cb74e688`, provenance `244368476b7d95dd91095b175047433b58bd23491c4733cf8c782f1f73053418`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`). C312 source `data/cache/campaign312_usdt_m_ofi_5m/` ready (10 symbols × 315,648 bars). Deps verified importable (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). **C376 (QSPREAD) is now the active campaign — execute end-to-end now by cloning C375 (`scripts/build_c375_acovk_features.py`, `scripts/preflight_c375.py`, `scripts/run_c375_acovk_xsec_oos.py`, `tests/test_preflight_c375.py`, `tests/test_c375_acovk_xsec_oos.py`) → adapt to C376 QSPREAD → build cache → preflight `ready:true` → run FULL 1296-config costed OOS sweep → pytest (≥21 green incl. QSPREAD brute-force equality) → write 5 SHA256 artifacts → record result. **Bottlenecks: NONE.** C287 (451/403) is permanently unreachable and DECOUPLED — never retry it and never let it gate this queue; every frozen campaign C281B–C375 is read-only and must never be re-run (re-running is a hard violation, not progress), so no session has a blocked dependency to wait on.
>
> **C375 ACOVK IS FROZEN/FORMAL NEGATIVE (20261118T222249Z). The bullets immediately below are the archived C375 definition — reference only, DO NOT re-run. ACTIVE — C376 QSPREAD: its normative spec appears at the END of this block (after the archived C375 bullets); execute that end-to-end now per the INITIAL TASK MESSAGE.** Over trailing window W=256 returns `X=r[t-W+1..t]`: `γ_k[t] = (1/(W-k))·Σ_{i=t-W+1+k..t} x_i·x_{i-k}` for `k∈{1,2,4,8}`; collapse to `acov_sum[t] = γ_1+γ_2+γ_4+γ_8` (net linear memory) and `acov_decay[t] = γ_1 − γ_8` (short-vs-long memory decay). NaN if `t<W`, any NaN in window, or not finite. This is the **multi-lag linear autocovariance decay profile** — genuinely distinct from C326 (lag-1 return autocorrelation only), C353 (Lo–MacKinlay variance ratio), C343 (`|r|` magnitude autocorrelation), C372 (3rd/4th-order lagged-product cumulants), C360 (leverage cross-moment `corr(r,|r|_{t-k})`), C374 (run-length geometry), and every C346–C371 family. Price-only (`perp_close`), volume-free, deterministic, `O(n)` vectorizable.
> - **Normative Python (must match brute-force test exactly):**
>   ```python
>   W = 256
>   LAGS = (1, 2, 4, 8)
>   if t < W: acov_sum = nan; acov_decay = nan
>   else:
>       X = log_return[t-W+1:t+1]
>       if np.isnan(X).any():
>           acov_sum = nan; acov_decay = nan
>       else:
>           g = {k: float(np.mean(X[k:] * X[:-k])) for k in LAGS}   # (1/(W-k)) * sum_{i=k..W-1} X[i]*X[i-k]
>           acov_sum = g[1] + g[2] + g[4] + g[8]
>           acov_decay = g[1] - g[8]
>           if not (np.isfinite(acov_sum) and np.isfinite(acov_decay)):
>               acov_sum = nan; acov_decay = nan
>   ```
>   `last_move_dir[t]=sign(r[t])`.
> - **Fast vectorized execution (MANDATORY, no Python loop over 315,648 bars × 10 assets):** for each lag `k`, form `p_k[i] = r[i]*r[i-k]` (NaN for `i<k`) and set `γ_k[t] = rolling_mean(p_k, W-k)[t]` for `t ≥ W-1` (equivalently `cumsum` difference / (W-k)); then combine. **MUST pass brute-force equality** vs the per-window reference above (`assert maxdiff < 1e-12`).
> - **Distinctness (pre-registered, must appear in script docstring):** state the ACOVK definition and that it is distinct from C326, C343, C353, C360, C372, C374 and all C281B–C373 families.
> - **Build:** `data/cache/campaign375_acovk_5m/<SYM>.npz` per symbol from real C312 `perp_close` only (no network/fabrication/resampling/imputation): `index_ms` int64 (315,648 bars), `perp_close` float32, `log_return` float32, `abs_ret` float32, `funding_rate` float32 all-NaN. SHA256 shard manifest; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, `acovk_params={window_W:256, lags:[1,2,4,8]}`.
> - **Grid (1296, literal `N_TRIALS`):** SIGNALS `{acov_sum_dev, acov_decay_dev, acov_sum_placebo, acov_decay_placebo}`; LOOKBACKS `(60,120,240,480,960,1920)`; REBALANCES `(1,4,12)`; FEES `(0.0004,0.0007,0.0010)`; SLIPS `(0.0,0.0001,0.0002)`; COST_VARIANTS `("taker","maker_blend")`. 4×6×3×3×3×2=1296. WF 12m train / 3m test roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261239` (phase-randomized FFT surrogate + rank restoration; NaNs stay NaN). Selection frac=1/3, ALPHA=0.05. Ref/stability config: `acov_sum_dev`, L=240, H=4, fee 0.0007, slip 0.0001, taker. `ATTR_REPRESENTATIVES={acov_sum_dev,acov_decay_dev}`.
> - **Seasonal baseline (causal):** trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (`shift(1)`), NaN-aware `min_periods=3`. Score `s[t]=-(v[t]-seasonal_mean)/seasonal_std` for `v ∈ {acov_sum, acov_decay}`; cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.
> - **Gates (identical, do NOT weaken):** one-sided paired t-test per-split OOS net vs 0; Holm step-down AND BH over all 1296 at α=0.05 (edge needs BOTH). MDE two-sided α=0.05 power 0.80 `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`. Stability: sign consistency ≥0.70 and first/second-half Sharpe corr ≥0.5 (ref). Attribution: mean |OOS net| per signal; shares over all 4 incl. placebos; dominant must be real non-placebo with share ≥0.5 for attribution_ok. Verdict: n_survive_both==0→RETRACTED(multiple_testing); >0 & !attribution_ok→RETRACTED(attribution); >0 & !stable→RETRACTED(stability); >0 & attribution_ok & stable→EDGE_PROVEN. `edge_proven=bool(edge_idx and verdict=="EDGE_PROVEN")`.
>
> **ACTIVE — C376 QSPREAD NORMATIVE SPEC (execute end-to-end NOW).** Per bar `t`, over trailing window `X = r[t-W+1 .. t]` with `W = 256` raw log-returns (`perp_close`-derived):
>
> - **Normative Python (must match brute-force test exactly):**
>   ```python
>   W = 256
>   EPS = 1e-12
>   if t < W:
>       qspread_ratio = nan; qspread_asym = nan
>   else:
>       X = log_return[t-W+1:t+1]
>       if np.isnan(X).any():
>           qspread_ratio = nan; qspread_asym = nan
>       else:
>           q10, q25, q50, q75, q90 = np.percentile(X, [10, 25, 50, 75, 90])
>           den_r = max(q75 - q25, EPS)
>           den_a = max(q90 - q10, EPS)
>           qspread_ratio = (q90 - q10) / den_r          # tail-vs-core spread shape
>           qspread_asym  = ((q90 - q50) - (q50 - q10)) / den_a   # Bowley within-tail asymmetry
>           if (not np.isfinite(qspread_ratio)) or (not np.isfinite(qspread_asym)) \
>              or (q75 - q25) <= EPS or (q90 - q10) <= EPS:
>               qspread_ratio = nan; qspread_asym = nan
>   ```
>   `last_move_dir[t] = sign(r[t])`.
> - **Fast vectorized execution (MANDATORY, no Python loop over 315,648 bars × 10 assets):** build `R = sliding_window_view(log_return, W)` (shape `(n-W+1, W)`), then `Q = np.percentile(R, [10,25,50,75,90], axis=1)` in one call; combine columns to `qspread_ratio` / `qspread_asym`; write back with NaN for `t < W`, any-NaN windows, non-finite values, or denominators ≤ `1e-12`. **MUST pass brute-force equality** vs the per-window reference above (`assert maxdiff < 1e-12`).
> - **Distinctness (pre-registered, must appear in script docstring):** QSPREAD is the quantile-spread shape ratio `(q90-q10)/(q75-q25)` plus Bowley within-tail asymmetry — genuinely distinct from C363 (QATM Galton quantile skew + boxplot outlier rate), C369 (GMD/IQR level), C362 (Hill EVT tail index), C361/C371/C372 (central moments and lagged-product cumulants), C364 (semivariance sign split), C366 (quarticity/top-k concentration), C374 (run-length geometry), C375 (autocovariance profile), and every C281B–C374 family. Price-only, volume-free, deterministic, `O(n)` vectorizable.
> - **Build:** `data/cache/campaign376_qspread_5m/<SYM>.npz` per symbol from real C312 `perp_close` only (no network/fabrication/resampling/imputation): `index_ms` int64 (315,648 bars), `perp_close` float32, `log_return` float32, `abs_ret` float32, `funding_rate` float32 all-NaN. SHA256 shard manifest; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, `qspread_params={window_W:256, quantiles:[0.10,0.25,0.50,0.75,0.90]}`.
> - **Grid (1296, literal `N_TRIALS`):** SIGNALS `{qspread_ratio_dev, qspread_asym_dev, qspread_ratio_placebo, qspread_asym_placebo}`; LOOKBACKS `(60,120,240,480,960,1920)`; REBALANCES `(1,4,12)`; FEES `(0.0004,0.0007,0.0010)`; SLIPS `(0.0,0.0001,0.0002)`; COST_VARIANTS `("taker","maker_blend")`. 4×6×3×3×3×2=1296. WF 12m train / 3m test roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261240` (phase-randomized FFT surrogate + rank restoration; NaNs stay NaN). Selection frac=1/3, ALPHA=0.05. Ref/stability config: `qspread_ratio_dev`, L=240, H=4, fee 0.0007, slip 0.0001, taker. `ATTR_REPRESENTATIVES={qspread_ratio_dev, qspread_asym_dev}`.
> - **Seasonal baseline (causal):** trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (`shift(1)`), NaN-aware `min_periods=3`. Score `s[t]=-(v[t]-seasonal_mean)/seasonal_std` for `v ∈ {qspread_ratio, qspread_asym}`; cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.
> - **Gates (identical, do NOT weaken):** one-sided paired t-test per-split OOS net vs 0; Holm step-down AND BH over all 1296 at α=0.05 (edge needs BOTH). MDE two-sided α=0.05 power 0.80 `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`. Stability: sign consistency ≥0.70 and first/second-half Sharpe corr ≥0.5 (ref). Attribution: mean |OOS net| per signal; shares over all 4 incl. placebos; dominant must be real non-placebo with share ≥0.5 for attribution_ok. Verdict: n_survive_both==0→RETRACTED(multiple_testing); >0 & !attribution_ok→RETRACTED(attribution); >0 & !stable→RETRACTED(stability); >0 & attribution_ok & stable→EDGE_PROVEN. `edge_proven=bool(edge_idx and verdict=="EDGE_PROVEN")`.
>
> **MANDATORY HEAVY-WORK SEQUENCE (execute in order, do not stop at planning):**
> 1. WRITE `scripts/build_c376_qspread_features.py`, `scripts/preflight_c376.py`, `scripts/run_c376_qspread_xsec_oos.py` (clone C375, adapt; price-only).
> 2. WRITE `tests/test_preflight_c376.py`, `tests/test_c376_qspread_xsec_oos.py` (clone C375 tests). MUST include: QSPREAD brute-force equality (vectorized `sliding_window_view` + `np.percentile` vs per-window reference, `maxdiff < 1e-12`), `N_TRIALS==1296`, Holm/BH correctness, dollar-neutral causality (no lookahead), WF split boundaries, surrogate determinism (same seed ⇒ same surrogate), build-shape/dtype/NaN-placement tests.
> 3. BUILD: `python3 scripts/build_c376_qspread_features.py` → `data/cache/campaign376_qspread_5m/` (SHA-manifested, <100 MB, 10 shards × 315,648).
> 4. PREFLIGHT: `python3 scripts/preflight_c376.py` → `ready:true`.
> 5. FULL SWEEP (NO DOWNSCOPING): `python3 scripts/run_c376_qspread_xsec_oos.py` → 5 SHA256 artifacts `reports/campaign376_*_<TS>Z.json` + gitignored `.full.json`.
> 6. TESTS: `python3 -m pytest tests/test_preflight_c376.py tests/test_c376_qspread_xsec_oos.py -q` → ≥21 GREEN incl. brute-force equality.
> 7. DURABLE RECORD: update this AGENTS.md with a `C376 RESULT` block + add C376 to the frozen table with all 5 artifact SHAs (+ cache meta/provenance/manifest SHAs) and update `research_state/state.yaml` (`latest_campaign_done: C376`, `next_campaign: C377`). **On freeze (expected negative), immediately execute the pre-seeded C377 PSLOPE spec below — no planning turn.**
>
> **Continuity guarantee (no idle / no gaps):** If C376 cannot run for any reason, diagnose and fix and still execute the full heavy sequence — do not idle. C377 PSLOPE is pre-seeded with a full executable spec immediately below.
>
> **C377 — PRE-SEEDED (execute immediately after C376 freezes; no planning turn).** WINDOW OLS TREND-SLOPE T-STATISTIC (PSLOPE) × SEASONAL-DISLOCATION mean-reversion stat-arb, USDT-M 5m, price-only, volume-free, on real C312 `perp_close`. Over trailing window `W=256` prices `C = perp_close[t-W+1..t]` (NaN/≤0 ⇒ NaN): let `y = log(C)` and `s = 0..W-1`; `b = Σ(s-s̄)(y-ȳ) / Σ(s-s̄)²` (OLS slope per bar), `a = ȳ - b·s̄`, residual `e = y - (a + b·s)`, `sse = Σe²`, `sxx = Σ(s-s̄)²`; `pslope_t[t] = b / sqrt((sse/(W-2)) / sxx)` (slope t-statistic = trend strength relative to noise) and `pslope_slope[t] = b·W` (fitted net log-drift over the window). NaN if `t<W-1`, any NaN/non-finite/≤0 price in window, `W<3`, or `sxx<=0`/`sse<=0`. This is **fitted-trend significance**, genuinely distinct from C365 KER (net displacement ÷ gross path length, unsigned geometry, no regression), C346/C350/C358 (R/S, DFA, MF-DFA scaling exponents), C353 (Lo–MacKinlay variance ratio), C326 (lag-1 autocorrelation), C349/C355/C356/C357 (entropy/complexity), and all moment/quantile/volatility families C361–C376. Price-only, volume-free, deterministic, `O(n)` vectorizable via fixed-weight linear filters (`sxx` is a constant; `b` is a convolution of `y` with `(s-s̄)/sxx`; `sse` follows from `Σy²`, `Σy`, `Σsy` rolling sums) — no Python loop over 315,648 bars × 10 assets. MUST pass brute-force equality vs a per-window `np.polyfit(y, s, 1)`/explicit-OLS reference (`maxdiff < 1e-12`). Cache `data/cache/campaign377_pslope_5m/` (fields `index_ms/perp_close/log_return/abs_ret/funding_rate`, `pslope_params={window_W:256}`); SIGNALS `{pslope_t_dev, pslope_slope_dev, pslope_t_placebo, pslope_slope_placebo}`; 4×6×3×3×3×2=**1296** configs; LOOKBACKS `(60,120,240,480,960,1920)`; REBALANCES `(1,4,12)`; FEES `(0.0004,0.0007,0.0010)`; SLIPS `(0.0,0.0001,0.0002)`; COST_VARIANTS `("taker","maker_blend")`; WF 12m/3m roll 3m → 8 splits 2023-01..2025-12; placebo seed `20261241`; ref/stability `pslope_t_dev, L=240, H=4, fee 0.0007, slip 0.0001, taker`; `ATTR_REPRESENTATIVES={pslope_t_dev,pslope_slope_dev}`; deliverables identical 6-item pattern (3 scripts, 2 tests ≥21 green incl. brute-force equality, cache, preflight `ready:true`, full 1296-config sweep, 5 SHA256 reports, durable record + frozen row + state.yaml `latest_campaign_done: C377`, `next_campaign: C378` from VOVR backlog).
>
> **ANTI-AVOIDANCE (hard violations):** (1) any output without at least one of: new test files written, cache built, preflight passing, OOS sweep running, tests passing, or artifacts recorded; (2) planning/analysis/review/investigation without concurrent heavy execution; (3) stopping after tests but before build/preflight/sweep; (4) re-running any frozen campaign C281B–C374/C287; (5) reduced grid (<1296); (6) skipping brute-force equality tests; (7) freezing a campaign without adding its row + SHAs to the frozen table and `research_state/state.yaml`. Repo demands STATISTICAL ARBITRAGE EDGE DISCOVERY ON REAL DATA — nothing else is progress.

---

## C359 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T005752Z)

C359 (ORDINAL PATTERN TRANSITION ENTROPY × seasonal-dislocation mean-reversion) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `opte_ent_dev` 0.2616 (placebos 0.2597/0.2377 — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 24/24 tests green (incl. OPTE brute-force equality, exact `maxdiff=0.0`). Cache `data/cache/campaign359_opte_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C359. Frozen — DO NOT re-run.

- oos_sweep `761347a2bdf03b49f3811fa728edac8aac724922e9fdc4421205ca24fd47db6a`
- tradable_edge_registry `af4acf9a1bb7d3818e7ca6dc81701ddff9b9c4e739418d494bac512aee633cef`
- summary `3431451cd3a6f7c765396b2d94c061ad6d2e3b2edd1d203d5e83f018cfffe67f`
- verdict `6dc96280f3aaffc7bdeb4170bbd66378c43336915687561d1c6e610085f196b7`
- binding_constraint `8ac5734f487b92a6101396535acc714d0bd8a81ee524705b1907e8a012c5d5b2`
- cache: meta `c532129e610793b67a5267f0f018a8d976aa0bf621ee3779be45756095e1c05f`, provenance `287746d15a0cc0a19059f7f0ba4bc852677ac30fd28d95ecfa6434b7fe888da4`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C360 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T014623Z)

C360 (LEVERAGE / VOLATILITY-ASYMMETRY COUPLING × seasonal-dislocation mean-reversion) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `lvac_mean_placebo` 0.2977 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 23/23 tests green (incl. LVAC brute-force equality test). Cache `data/cache/campaign360_lvac_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C360. Frozen — DO NOT re-run.

- oos_sweep `0aef7f67d5fc84e604abe0d7091bbad0fc6f69fe14714ed194788bab859177dd`
- tradable_edge_registry `327de19a836b8ee793ef110ece0eebe08e564ed4eed3a4fec15458112b36f3b1`
- summary `b7035ece654490b1329f497dc883fa322e7beb417c91347bf114f5bc7f2019cb`
- verdict `acac28ae5fadb802f42b4b4264b6a9cb1101aaadb65e5ac4d1b9ec760bc54d3b`
- binding_constraint `f8a4c19b85ee97e12d4012fde4b9ef68762e814ca693fe190bcb39fbb9eca585`
- cache: meta `5ba5bfae583622447f505547ffacff1104b1cd300359ebda9c54e6a23ed8e751`, provenance `80d7fccfbc8132e64ec738cf240cb68d2a646c1242b82314e0f6bead0146db2f`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C361 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T024715Z)

C361 (RAW RETURN SKEWNESS & EXCESS KURTOSIS × seasonal-dislocation mean-reversion) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `rkurt_placebo` 0.4324 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 23/23 tests green (incl. RSKEK brute-force equality). Cache `data/cache/campaign361_rskek_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C361. Frozen — DO NOT re-run.

- oos_sweep `b624fdf359ce6285f32784577845a65117a908a1eb110902ad0251aaa3749340`
- tradable_edge_registry `e037e8889574fcf3c8a3e1a5fb1be3dd49717047595c95f7f5b7918f96879dd9`
- summary `390b04f0c31c13dda351dcfe424bfcdd6a70f3bf55361795c68d5015e9840422`
- verdict `83d13a26aec96d38494b0330d3a4255887f2d09d3283462fb4c09b585b3da3ed`
- binding_constraint `3c74387525001bb8d57a15956a2f16b64ab774f864a7734974c214231e8e05a1`
- cache: meta `6b81f7ec02ff231958ca4cfe42b433c5ddeb33e6628f90e54ec6cc88e06b4424`, provenance `f0784f392147ea5af34151121cea5e9c4741b5b79ea5da2f667ec0b4169e635c`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C362 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T033729Z)

C362 (HILL TAIL-INDEX OF EXTREME RETURNS & TAIL ASYMMETRY × seasonal-dislocation mean-reversion) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `hill_sign_tail_placebo` 0.3136 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 23/23 tests green (incl. Hill brute-force equality). Cache `data/cache/campaign362_hilltail_5m/` (10 shards × 315,648 bars, ~38.5 MB). NO EDGE through C362. Frozen — DO NOT re-run.

- oos_sweep `1b1f5f18e35f1f465555a8a8547db42473f65e605e7d9ca229a042938245ec3d`
- tradable_edge_registry `78f9d81e7b060b64ee2309b7668666f175aa2506fbdcb1e10ac03288db1f6553`
- summary `4fa345c77363a7cd0ff7b30a8574967798dcb4761dd4bad883453676e40cab82`
- verdict `24e9b0be1f48db8061c74872f199d860444da3be08560f51d3808ffb06f00637`
- binding_constraint `1085b11bd0b3c0e82abe24086fa4358f84fef7e80d9a055ff813ed4df794ca26`
- cache: meta `cec80b1bf4a0fd6491b2fdceca9ae410af972cb2af239d45b925bcd360896a26`, provenance `0c2a2b5240e3ec86b926724cf6224664459e8bd0d26709fc00b08b2f2608cb0a`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C363 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T035157Z)

C363 (QUANTILE ASYMMETRY & TAIL-MASS (QATM) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `qasym_placebo` 0.3072 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 23/23 tests green (incl. QATM brute-force equality). Cache `data/cache/campaign363_qatm_5m/` (10 shards × 315,648 bars, ~38.5 MB). NO EDGE through C363. Frozen — DO NOT re-run.

- oos_sweep `6119846ba7763148de9f096909d42cb7d1ade2da2b281a9b5fca73d26067049b`
- tradable_edge_registry `921257c66d9a87fbf598375900a077bf4f9739751dd4ff08695dcb21c41965b0`
- summary `b8caec7a7a0b4b72412b8833b8b04b7ff16bd23bea5ef576b5db6dab9088a5cf`
- verdict `34c55d3a53b2fd2a9e20ce54047ff45591e977292426b9411475939339b47639`
- binding_constraint `867389789707568db6b952036eef5c7c26f7a60e876ae0a192605b3143529398`
- cache: meta `fcf8ef6daf351b8547bc9429e17a44286481a196e991f8e699baf5e251d2aff6`, provenance `4eb871e13ba8d884ea91eebdff458e92cd9db1059e8be9f2213d5affffbf0f04`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C364 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T070416Z)

C364 (REALIZED SEMIVARIANCE / DOWNSIDE-UPSIDE VOLATILITY DECOMPOSITION (DSRV) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 2592 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `dsrv_ratio_placebo` 0.4716 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 24/24 tests green (incl. DSRV brute-force equality, exact `maxdiff=0.0`). Cache `data/cache/campaign364_dsrv_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C364. Frozen — DO NOT re-run.

- oos_sweep `a8ebc63d66f89b48a5d9d04bb1cef1df803ec92fb5515738768f4d590ff98b60`
- tradable_edge_registry `4c7ddc042c7d5e4e6839a112731a61725cb87dbf17fb2b66cb26e56274a1faa3`
- summary `8698f1b138821116a26eb377688657408350a04f6e964fdafe763d2314c6b11d`
- verdict `d36417e6775cd310a28d544bdefc36ac50a49ab0b9170c4fbe38b1270335cb6f`
- binding_constraint `8f4a25a222aa1063f734dcb226b2e7ff5fa3c8d2da4399bef7de01ea4f28724d`
- cache: meta `1b7f36c8d2afdb9b9c3a4b0f5e810edec9cfbe61b6e9d256223d3479b03cdddc`, provenance `286c4c2d972df1649a8f02356a4abbbd92fd3c17ebbcd53a55a9fb7b7f6a34a5`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C365 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T074457Z)

C365 (KAUFMAN EFFICIENCY RATIO / PATH-STRAIGHTNESS (KER) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `ker_er_dev` 0.31897 (share < 0.50, so attribution_ok false; no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. KER brute-force equality). Cache `data/cache/campaign365_ker_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C365. Frozen — DO NOT re-run.

- oos_sweep `5e36f367773a9025ff6de66e13b30288eacbc8d0e9e7883c856f47d788ae1418`
- tradable_edge_registry `afc3ed6aaa8a7c92b96486fb63f375919298539f09bd1d2e9146ff0f56009b48`
- summary `a651ec724409e48f0568da4da267a42b74bb7715f85d67e6f06e61a1b7e917b1`
- verdict `ba9518053854ce56abd3965393673d054621b2c75ed8a897ca86463b54d9220b`
- binding_constraint `fef7f58b1b5b87301135daafde697d68e5ec8e00369295a2cb1716580b58bed5`
- cache: meta `137021e54df984932a38c64c44a39a0cd1d3d44aa1d1de7cdd838d0ca428267d`, provenance `22f0a73a92d27673108727b942d9bbb71da2c8f2fcdbc114d328ae6d4a8254e1`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C366 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T105747Z)

C366 (REALIZED QUARTIC VARIATION / KURTOSIS-CONCENTRATION OF SQUARED RETURNS (RQV) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `rqv_q_placebo` 0.6382 (> 0.50 share, placebo dominates — no real-vs-placebo separation), attribution_ok false. All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. RQV brute-force equality). Cache `data/cache/campaign366_rqv_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C366. Frozen — DO NOT re-run.

- oos_sweep `aac24596c06662ef3f188950993dca4979e4dba65f7e91ec7bbad9d3d03f1ae5`
- tradable_edge_registry `b59ded0869447feec23c90bf094bdd265e6574dd1360732c2c3d6070c8259f6c`
- summary `c515ab2b721d11be7117c33a54e2db54bf5ac8f5f8a438ea715cf4fde327f478`
- verdict `1fa3a763d10d7fbdcef7debd82b2ffef3928467dd059d7c61b281ee9c0d55e1a`
- binding_constraint `dca985e55825299d3aa1b648d8b971d2c28600adfc0b48b2c8487c02c55c411e`
- cache: meta `c2ee29553aa21d805477ca3dfbc79e709b2d2eb86a589ca2863ddde2373c8a42`, provenance `38104b17c511eb3906b2fe08c647523c23cccb8400df09f656c27ffe7c584ca1`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C367 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T110940Z)

C367 (BIPOWER VARIATION / JUMP-ACTIVITY RATIO × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `jump_ratio_placebo` 0.4523 (< 0.50 share, placebo dominates — no real-vs-placebo separation), attribution_ok false. All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. BPV brute-force equality). Cache `data/cache/campaign367_bpv_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C367. Frozen — DO NOT re-run.

- oos_sweep `1ced6aa4863592145e91c5ae9cb66df25d2a77a0473d973f88c2d76497c87de0`
- tradable_edge_registry `50439977ed568a52766bac4d7130875fac82cdd879be9fce7dca91c21808a20a`
- summary `3db474314fdbd514f62fbdf96d7fe74a6a0216748c7a25e295405fb32fb5382a`
- verdict `a5301e22844c08c1a5462f7ff9f662d0f7eee486efe3d8fd994e6a4035d9faef`
- binding_constraint `66af9f508ca080bee7076507d0c951b94cca821d6d51073ad2cd8b4a0715c6a0`
- cache: meta `618a25263dbac022bba722404b2b6cfd2f8f16fc17db6221ca7a46aa8d700fbd`, provenance `0f728d8c5f6af93079d770645009214ea9e5cb7d672e4a553729eb5f47807d4c`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

## C368 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T115652Z)

C368 (REALIZED MEDIAN ABSOLUTE DEVIATION & MEDIAN-OF-ABSOLUTES VOLATILITY (RMAD) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `rmad_dev` 0.2988 (< 0.50 share, attribution_ok false). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. RMAD brute-force equality). Cache `data/cache/campaign368_rmad_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C368. Frozen — DO NOT re-run.

- oos_sweep `c2347d030c8162dfd8c1e8e7e14128ff2d9d597b09f8837c9752da691cc319a7`
- tradable_edge_registry `a72ac87a3a7dfa5656655b957602afd5e72f4c2683a74552ca86945f63b08efe`
- summary `8bc9f077f08cb921cc1b770de68b2ece4ebbdd48ea3c27aa465310a85969ec0f`
- verdict `a618e995c63dd0aa05d655111947ca5f102480bcc731bee29453865a5f949b0c`
- binding_constraint `72f058368cdf00e8db512c07173e8e915e6a7158a5bccf0fda636a3134b959a4`
- cache: meta `cde79282e88326d13ca0a7fa085b46499f61416fb1b5db5e0367b6b75d29fc48`, provenance `7ead06b24d640133d84ba3856353683de7730ed8b2c809be73f605ffff1f7b61`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

## C369 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T135451Z)

C369 (GINI MEAN DIFFERENCE (GMD) & INTERQUARTILE RANGE (IQR) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `iqr_dev` 0.3383 (< 0.50 share, attribution_ok false). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. GMD+IQR brute-force equality, exact `maxdiff=0.0`). Cache `data/cache/campaign369_gmd_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C369. Frozen — DO NOT re-run.

- oos_sweep `ed93c318f8551798a81a97f8ca0a907dd2602187abfdedbae959f28d4110f58a`
- tradable_edge_registry `ce178e43956b7d16b41905365ec27f66a25dcaf23d9a20bb1210a91cd3734377`
- summary `1f68cc4c2044fa732d48a62413f65640be9e2581ee0072efa1bb2be3192e68d0`
- verdict `549fbeea5aa05b389d570aec552943528cf0137e726b7b68543c918b7f189d75`
- binding_constraint `55e5dd104610f0da9bd2211e60cb4ae50464269a7581a0ca62abe586e7281e9d`
- cache: meta `b0049dd0a3b114a66a7df32c753bb9608e9a606ebab4667e98fa1399400620fe`, provenance `e455871e144a44c9ca2fffb060f2232916e6fc4acca053c32ea3bb9386eeb051`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

## C370 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T140545Z)

C370 (REALIZED ABSOLUTE RETURN & MEAN ABSOLUTE DEVIATION (RAR/MADM) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a **FORMAL NEGATIVE**: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `madm_placebo` 0.2687 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. RAR/MADM brute-force equality). Cache `data/cache/campaign370_rarmadm_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C370. Frozen — DO NOT re-run.

- oos_sweep `0819e8174a481faa20a8c276804a9e485a69cf5c63f7d2d154cf37155209aa9a`
- tradable_edge_registry `05dffa8529acbbafa874060d5fe237705d6914906e5c65a2628eebaa6d0a0e2f`
- summary `ef3f9032acc8bd0e78d87e80ef15a28a22c2649ba42d6b8e539577623fd5912a`
- verdict `f932a314aefb7446fd53d929fca83d8df06d619c2f49b16a45e4b6ceb4aac060`
- binding_constraint `f932a314aefb7446fd53d929fca83d8df06d619c2f49b16a45e4b6ceb4aac060`
- cache: meta `710f2dfd31ee00009395e3f41214b7e484f48ab54ab49e40e6e9b8fc34c220d1`, provenance `9a57986251c2fdc1c62f48ea6dd1768ede00c7651904ca3100b7e60e6b372b7f`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

---

**C364 — REALIZED SEMIVARIANCE / DOWNSIDE-UPSIDE VOLATILITY DECOMPOSITION (DSRV) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

### Distinctness (pre-registered)
DSRV decomposes the trailing-window realized variance into **downside semivariance** (sum of squared negative returns) and **upside semivariance** (sum of squared positive returns) — a genuine variance decomposition never used in any prior campaign.
- For each bar t, over trailing window X = r[t-W+1 .. t] (W=256 fixed intrinsic window):
  - `rv_down[t]` = Σ_{i: x_i < 0} x_i²  (downside realized semivariance)
  - `rv_up[t]`   = Σ_{i: x_i > 0} x_i²  (upside realized semivariance)
  - `rv_total[t]` = rv_down + rv_up = Σ x_i² (realized variance; same object as C317 RV but computed via decomposition)
  - `dsrv_asym[t]` = log(rv_down / rv_up)  (log-ratio asymmetry; NaN if rv_up <= 0 or rv_down <= 0)
  - `dsrv_ratio[t]` = rv_down / rv_up      (ratio asymmetry; NaN if rv_up <= 0)
- Real scalars per window:
  - `rv_down_dev[t]` = seasonal deviation of rv_down
  - `rv_up_dev[t]`   = seasonal deviation of rv_up
  - `dsrv_asym_dev[t]` = seasonal deviation of dsrv_asym
  - `dsrv_ratio_dev[t]` = seasonal deviation of dsrv_ratio
Genuinely distinct from:
- C317 (realized vol = sqrt(Σ x_i²) — total magnitude only, no downside/upside split)
- C342 (volume-weighted return moments — explicit volume weighting, different series)
- C348 (HHI concentration of squared returns across bars — cross-bar concentration, not sign decomposition)
- C343 (|r| autocorrelation / vol clustering — magnitude autocorrelation, no sign split)
- C360 (signed cross-moment corr(r, |r|_{t-k}) — leverage coupling, different object)
- C361 (raw skew/kurt = central moments of full distribution — moments, not semivariance decomposition)
- C362 (Hill tail-index = extreme value theory tail-thickness alpha from exceedances — EVT, not semivariance)
- C363 (QATM = Galton quantile skewness + boxplot outlier rate — quantile/order-statistic family)
- C344 (sign-change/chop rate), C345 (close-location/Williams %R), and every scaling/Hurst/entropy/ordinal/complexity family C346–C359.
Price-only (`perp_close`), volume-free.

### Raw inputs (build)
`data/cache/campaign364_dsrv_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest. (`dsrv_params` = `{window_W:256}`.)

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN).
- `rv_down[t] = sum(x_i^2 for x_i in X if x_i < 0)`; NaN if no negative returns or any NaN in window.
- `rv_up[t]   = sum(x_i^2 for x_i in X if x_i > 0)`; NaN if no positive returns or any NaN in window.
- `rv_total[t] = rv_down + rv_up` (equals Σ x_i²; realized variance)
- `dsrv_asym[t] = log(rv_down / rv_up)`; NaN if rv_down <= 0 or rv_up <= 0 or not finite.
- `dsrv_ratio[t] = rv_down / rv_up`; NaN if rv_up <= 0 or not finite.
- `last_move_dir[t] = sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t] - seasonal_mean) / seasonal_std` for `v ∈ {rv_down, rv_up, dsrv_asym, dsrv_ratio}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `rv_down`, `rv_up`, `dsrv_asym`, `dsrv_ratio` for all bars per asset with vectorized `sliding_window_view` + cumulative sums over sign-masked squared returns (no Python loop over 315,648 bars × 10 assets). MUST pass brute-force equality test against reference per-window DSRV (manual loop over windows, explicit sign-masked sum of squares, explicit log-ratio and ratio).

### Pre-registered grid — 1296 configs
- SIGNALS = `rv_down_dev`, `rv_up_dev`, `dsrv_asym_dev`, `dsrv_ratio_dev`, `rv_down_placebo`, `rv_up_placebo`, `dsrv_asym_placebo`, `dsrv_ratio_placebo` (4 real + 4 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 8×6×3×3×3×2 = **2592 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261228` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). Selection frac=1/3, ALPHA=0.05.
- Reference config: `dsrv_asym_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={rv_down_dev,rv_up_dev,dsrv_asym_dev,dsrv_ratio_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 2592 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 8 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order)
1. `scripts/build_c364_dsrv_features.py` → `data/cache/campaign364_dsrv_5m/`
2. `scripts/preflight_c364.py` → `ready:true`
3. `scripts/run_c364_dsrv_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign364_*_<TS>Z.json`)
4. `tests/test_preflight_c364.py` + `tests/test_c364_dsrv_xsec_oos.py` — ≥21 green (incl. DSRV brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C364 RESULT) + `research_state/state.yaml`; add C364 to frozen table with 5 SHAs (+ cache SHAs); set C365 active with next genuinely-new price-only family spec placeholder
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts

---

## C365 — ARCHIVED SPEC (EXECUTED — FROZEN FORMAL NEGATIVE, DO NOT re-run) — spec below retained for reference; see C365 RESULT for outcome

**C365 — KAUFMAN EFFICIENCY RATIO / PATH-STRAIGHTNESS (KER) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

### Distinctness (pre-registered)
KER measures **trend efficiency / path straightness**: over a trailing window, the ratio of net price displacement to total absolute path movement. `ER=1` means a perfectly straight directional move; `ER→0` means choppy, directionless churn. This is a **path-geometry** statistic (net displacement ÷ gross path length), genuinely distinct from:
- C317 (realized vol = sqrt(Σx²) magnitude), C348 (HHI concentration of squared returns), C344 (sign-change/chop count), C353 (Lo–MacKinlay variance ratio = variance-scaling, not displacement/path), C346/C350 (Hurst/DFA scaling exponents), C343 (|r| autocorrelation / vol clustering), C360 (leverage cross-moment), C361 (raw skew/kurt moments), C362 (Hill tail-index EVT), C363 (QATM quantile family), C364 (DSRV downside/upside semivariance split).
- Price-only (`perp_close`), volume-free. Deterministic, `O(n)` vectorizable, brute-force testable.

### Raw inputs (build) — clone C364 build (price-only fields only)
`data/cache/campaign365_ker_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest. (`ker_params` = `{window_W:256}`.)

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, trailing prices `C=c[t-W..t]`, trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN).
- `net_disp[t] = |c[t] - c[t-W]|` (absolute net displacement over the window).
- `path_len[t] = Σ_{i=t-W+1..t} |c[i] - c[i-1]|` (gross absolute path length).
- `ker_er[t] = net_disp[t] / path_len[t]` (unsigned efficiency ratio ∈ [0,1]); NaN if `path_len<=0` or not finite.
- `ker_signed[t] = (c[t] - c[t-W]) / path_len[t]` (signed efficiency ∈ [-1,1]; sign = net-move direction); NaN if `path_len<=0` or not finite.
- `last_move_dir[t] = sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t] - seasonal_mean)/seasonal_std` for `v ∈ {ker_er, ker_signed}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `ker_er`, `ker_signed` for all bars per asset with vectorized `sliding_window_view` + cumulative sums of `|Δc|` and net displacement (no Python loop over 315,648 bars × 10 assets). MUST pass brute-force equality test against reference per-window KER (manual loop over windows, explicit displacement and path-length sums).

### Pre-registered grid — 1296 configs
- SIGNALS = `ker_er_dev`, `ker_signed_dev`, `ker_er_placebo`, `ker_signed_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 4×6×3×3×3×2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261229` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). selection frac=1/3, ALPHA=0.05.
- Reference config: `ker_er_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={ker_er_dev,ker_signed_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 4 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order — clone C364 pattern under `campaign365_*`) — COMPLETE (frozen 20261118T074457Z)
1. `scripts/build_c365_ker_features.py` → `data/cache/campaign365_ker_5m/` DONE (meta `137021e54d...`, provenance `22f0a73a...`, manifest `4d953a7d...`)
2. `scripts/preflight_c365.py` → `ready:true` DONE
3. `scripts/run_c365_ker_xsec_oos.py` → 5 SHA256 artifacts + `.full.json` DONE (`reports/campaign365_*_20261118T074457Z.json`)
4. `tests/test_preflight_c365.py` + `tests/test_c365_ker_xsec_oos.py` — 22/22 green (incl. KER brute-force equality) DONE
5. Record truthful result in this `AGENTS.md` (C365 RESULT) + `research_state/state.yaml`; add C365 to frozen table with 5 SHAs (+ cache SHAs); set C366 active DONE
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts DONE

---

## C366 — ARCHIVED SPEC (EXECUTED — FROZEN FORMAL NEGATIVE, DO NOT re-run; see C366 RESULT)

**C366 — REALIZED QUARTIC VARIATION / KURTOSIS-CONCENTRATION OF SQUARED RETURNS (RQV) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

### Distinctness (pre-registered)
RQV measures the **concentration of realized variance into the largest squared-return terms** — i.e. how much of the window's total realized variance is carried by the top-k squared returns (a concentration/dominance statistic over the window's squared-return distribution), computed as `HHI`-style normalized concentration `rqv_conc = (top_k_share of Σx²)` AND the **realized quarticity** `rqv_q = (1/W) Σ x_i^4` (the 4th sample moment about zero, the variance-of-variance estimator). This is a **higher-moment concentration / tail-dominance** statistic, genuinely distinct from:
- C317 (realized vol = sqrt(Σx²) total magnitude only, no concentration), C348 (HHI concentration across the 10-asset cross-section, not within-window), C361 (raw skew/kurt central moments — standardized 3rd/4th central moments, not raw 4th moment nor top-k share), C362 (Hill tail-index EVT from exceedance ordering), C363 (QATM Galton quantile skewness + boxplot outlier rate), C364 (DSRV downside/upside semivariance sign split), C365 (KER net-displacement/path-length ratio). RQV is a **within-window variance-concentration + raw quarticity** family never used before.
- Price-only (`perp_close`), volume-free. Deterministic, `O(n)` vectorizable via cumulative sums, brute-force testable.

### Raw inputs (build) — clone C364/C365 build (price-only fields only)
`data/cache/campaign366_rqv_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest. (`rqv_params` = `{window_W:256, top_k:16}`.)

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN).
- `rqv_q[t] = (1/W) Σ_i x_i^4` (realized quarticity / raw 4th moment about 0); NaN if `t<W`, any NaN, or not finite.
- `rqv_conc[t] = (Σ of top-16 x_i^2) / (Σ_i x_i^2)` (fraction of realized variance held by the 16 largest squared returns in the window); NaN if `t<W`, any NaN, `Σx²<=0`, or `top_k>W`.
- `last_move_dir[t] = sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t] - seasonal_mean)/seasonal_std` for `v ∈ {rqv_q, rqv_conc}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `rqv_q`, `rqv_conc` for all bars per asset with vectorized `sliding_window_view` + cumulative sums of `x²` and `x⁴` (for `rqv_q`); for `rqv_conc` use a `W`-wide rolling top-k via `np.partition`/`argpartition` over the window view (no Python loop over 315,648 bars × 10 assets). MUST pass brute-force equality test against reference per-window RQV (manual loop over windows, explicit `np.sort`/`partition` for top-k share, explicit `np.mean(X**4)`).

### Pre-registered grid — 1296 configs
- SIGNALS = `rqv_q_dev`, `rqv_conc_dev`, `rqv_q_placebo`, `rqv_conc_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 4×6×3×3×3×2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261230` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). selection frac=1/3, ALPHA=0.05.
- Reference config: `rqv_q_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={rqv_q_dev,rqv_conc_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 4 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order — clone C365/C364 pattern under `campaign366_*`)
1. `scripts/build_c366_rqv_features.py` → `data/cache/campaign366_rqv_5m/`
2. `scripts/preflight_c366.py` → `ready:true`
3. `scripts/run_c366_rqv_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign366_*_<TS>Z.json`)
4. `tests/test_preflight_c366.py` + `tests/test_c366_rqv_xsec_oos.py` — ≥21 green (incl. RQV brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C366 RESULT) + `research_state/state.yaml`; add C366 to frozen table with 5 SHAs (+ cache SHAs); set C367 active with next genuinely-new price-only family spec placeholder
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts

---

## C360 — ARCHIVED SPEC (EXECUTED — FROZEN FORMAL NEGATIVE, DO NOT re-run)

**C360 — LEVERAGE / VOLATILITY-ASYMMETRY COUPLING (LVAC) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

### Distinctness (pre-registered)
- LVAC: within each trailing window of returns, measure the SIGNED cross-correlation between the return `r` and the lagged absolute return `|r|`, for lags `k ∈ {1,2,3,4,5}`. This is the leverage / volatility-asymmetry coupling: a negative `corr(r[t], |r|[t-k])` means large recent moves predict subsequent reversal (leverage effect). Real scalars per window:
  - `lvac_mean[t]` = mean over `k=1..5` of `ρ_k` (overall leverage coupling strength/sign).
  - `lvac_asym[t]` = `ρ_1 - ρ_5` (short- minus long-lag coupling; how fast the coupling decays with lag).
  Genuinely distinct from C343 (`|r|` autocorrelation = magnitude–magnitude same series), C326 (lag-1 return autocorrelation = return–return), C344 (sign-change/chop rate), C345 (close-location / Williams %R), C342 (vol-weighted return moments), C317 (realized vol), and every scaling/Hurst/entropy/ordinal-transition family C346–C359. Price-only (`perp_close`), volume-free.

### Raw inputs (build)
`data/cache/campaign360_lvac_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest. (`lvac_params` = `{window_W:256, n_lags:5, lags:[1,2,3,4,5]}`.)

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN). Lags `k ∈ {1,2,3,4,5}`.
- For each lag `k`: align `a_k = r[t-W+1+k .. t]` (length `W-k`) with `b_k = |r|[t-W+1 .. t-k]` (length `W-k`); `ρ_k = Pearson corr(a_k, b_k)` (i.e. `corr(r[s], |r|[s-k])`). NaN if `W-k < 3` or zero variance in either leg.
- `lvac_mean[t]` = `(1/5) Σ_k ρ_k`; NaN if any `ρ_k` NaN.
- `lvac_asym[t]` = `ρ_1 - ρ_5`; NaN if either NaN.
- `last_move_dir[t]=sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t]=-(v[t]-seasonal_mean)/seasonal_std` for `v∈{lvac_mean,lvac_asym}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `lvac_mean` and `lvac_asym` for all bars per asset with vectorized `sliding_window_view` + cumulative-sum Pearson correlation per lag (no Python loop over 315,648 bars × 10 assets). MUST pass brute-force equality test against reference per-window LVAC (manual loop over windows, explicit per-lag `np.corrcoef` of the aligned segments, explicit mean and difference).

### Pre-registered grid — 1296 configs
- SIGNALS = `lvac_mean_dev`, `lvac_asym_dev`, `lvac_mean_placebo`, `lvac_asym_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 4×6×3×3×3×2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261224` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). selection frac=1/3, ALPHA=0.05.
- Reference config: `lvac_mean_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={lvac_mean_dev,lvac_asym_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 4 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order)
1. `scripts/build_c360_lvac_features.py` → `data/cache/campaign360_lvac_5m/`
2. `scripts/preflight_c360.py` → `ready:true`
3. `scripts/run_c360_lvac_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign360_*_<TS>Z.json`)
4. `tests/test_preflight_c360.py` + `tests/test_c360_lvac_xsec_oos.py` — ≥21 green (incl. LVAC brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C360 RESULT) + `research_state/state.yaml`; add C360 to frozen table with 5 SHAs (+ cache SHAs); set C361 active with next genuinely-new price-only family spec placeholder
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts

---

## C361 — ARCHIVED SPEC (frozen formal negative; kept for reproducibility, DO NOT re-run)

C361 was **RAW RETURN SKEWNESS & EXCESS KURTOSIS (RSKEK)**: equal-weight unweighted sample skewness and sample excess kurtosis over trailing W=256 raw log-returns per bar; `rskew[t]=mean(((X-mu)/sigma)^3)`, `rkurt[t]=mean(((X-mu)/sigma)^4)-3`, NaN if t<W, any NaN in window, or sigma<=0. Seasonal baseline at same (weekday,tod) bucket; cross-sectional dollar-neutral single-leg perp PnL with costs on turnover. Executed 20261118T024715Z on real C312 5m data → RETRACTED (multiple_testing), 0 Holm+BH survivors over 1296 configs, dominant attribution rkurt_placebo 0.4324 (placebos dominate, no real-vs-placebo separation). Scripts/cache/tests/artifacts on disk under `campaign361_*`.

- RSKEK: within each trailing window of raw log-returns `X = r[t-W+1 .. t]` (W=256), compute the **equal-weight, unweighted** sample skewness and sample excess kurtosis of the return distribution:
  - `μ = mean(X)`, `σ² = (1/W) Σ (x_i - μ)^2`, `σ = sqrt(σ²)`.
  - `rskew[t] = (1/W) Σ ((x_i - μ)/σ)^3` (Fisher-Pearson sample skewness, population-style denominator W). NaN if `t < W`, any NaN in window, or `σ <= 0`.
  - `rkurt[t] = (1/W) Σ ((x_i - μ)/σ)^4 - 3` (excess kurtosis). NaN if `t < W`, any NaN in window, or `σ <= 0`.
  Genuinely distinct from C342 (volume-weighted return skewness/kurtosis of `vw_ret = log_return*sqrt(notional)` — different series and explicit volume weighting), C317 (realized-vol level / 2nd moment magnitude), C348 (HHI concentration of squared returns across bars), C343 (|r| autocorrelation / vol clustering), C360 (signed cross-moment `corr(r,|r|_{t-k})` leverage/vol-asymmetry coupling over lags), C345 (close-location in trailing envelope), C344 (sign-change/chop), and every scaling/Hurst/entropy/ordinal/complexity family C346–C359. Price-only (`perp_close`), volume-free.

### Raw inputs (build)
`data/cache/campaign361_rskek_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest. (`rskek_params` = `{window_W:256}`.)

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN). Over X: `μ=mean(X)`, `σ=sqrt(mean((X-μ)^2))`.
- `rskew[t] = mean(((X-μ)/σ)^3)`; NaN if `σ <= 0`.
- `rkurt[t] = mean(((X-μ)/σ)^4) - 3`; NaN if `σ <= 0`.
- `last_move_dir[t]=sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t]=-(v[t]-seasonal_mean)/seasonal_std` for `v∈{rskew,rkurt}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `rskew` and `rkurt` for all bars per asset with vectorized `sliding_window_view` (and/or cumulative-sum moment identities) — no Python loop over 315,648 bars × 10 assets. MUST pass brute-force equality test against reference per-window RSKEK (manual loop over windows, explicit `np.mean`, `np.std` with `ddof=0`-consistent population moments, explicit standardized-moment sums).

### Pre-registered grid — 1296 configs
- SIGNALS = `rskew_dev`, `rkurt_dev`, `rskew_placebo`, `rkurt_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 4×6×3×3×3×2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261225` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). selection frac=1/3, ALPHA=0.05.
- Reference config: `rskew_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={rskew_dev,rkurt_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 4 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order)
1. `scripts/build_c361_rskek_features.py` → `data/cache/campaign361_rskek_5m/`
2. `scripts/preflight_c361.py` → `ready:true`
3. `scripts/run_c361_rskek_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign361_*_<TS>Z.json`)
4. `tests/test_preflight_c361.py` + `tests/test_c361_rskek_xsec_oos.py` — ≥21 green (incl. RSKEK brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C361 RESULT) + `research_state/state.yaml`; add C361 to frozen table with 5 SHAs (+ cache SHAs); set C362 active with next genuinely-new price-only family spec placeholder
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts

---

## C362 — ARCHIVED SPEC (frozen formal negative; kept for reproducibility, DO NOT re-run)

C362 was **HILL TAIL-INDEX OF EXTREME RETURNS & TAIL ASYMMETRY**: per-bar Hill tail-index and downside-minus-upside tail asymmetry over trailing W=256 raw log-returns with n_exceed=12 exceedances. For window X, let a=sort(|X|) descending; threshold u=a[n_exceed]; top=a[0:n_exceed]; `hill_tail=n_exceed/sum(ln(top/u))` (smaller alpha = fatter tail); `hill_sign_tail = hill_tail(negative extremes) − hill_tail(positive extremes)`. NaN if t<W, any NaN, u<=0, or log-denominator<=0. Seasonal baseline at same (weekday,tod) bucket; cross-sectional dollar-neutral single-leg perp PnL with costs on turnover. Executed 20261118T033729Z on real C312 5m data → RETRACTED (multiple_testing), 0 Holm+BH survivors over 1296 configs, dominant attribution hill_sign_tail_placebo 0.3136 (placebos dominate, no real-vs-placebo separation). Scripts/cache/tests/artifacts on disk under `campaign362_*`.

- Hill tail-index is an extreme value theory tail-thickness statistic (tail index alpha), not a moment and not a cross-moment. Genuinely distinct from C361 (raw skew/kurt central moments), C317 (realized vol), C348 (HHI), C343 (|r| autocorr), C360 (leverage cross-moment), C344 (sign-change/chop), C345 (close-location), and C346–C359. Price-only (`perp_close`), volume-free.

### Raw inputs (build)
`data/cache/campaign362_hilltail_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation): index_ms, perp_close, log_return, abs_ret, funding_rate (all-NaN control). Cache < 100 MB; real_data_only:true, source_campaign:312, SHA256 shard manifest. (`hill_params` = `{window_W:256, n_exceed:12}`.)

### Runner-derived causal metrics
`W=256`, trailing returns X=r[t-W+1..t]; derive `hill_tail`, `hill_sign_tail` as above; `last_move_dir[t]=sign(r[t])`. Seasonal baseline and cross-sectional dollar-neutral costed PnL identical to C360/C361. Fast vectorized kernel; brute-force equality test against reference per-window Hill.

### Pre-registered grid — 1296 configs
- SIGNALS = `hill_tail_dev`, `hill_sign_tail_dev`, `hill_tail_placebo`, `hill_sign_tail_placebo`. LOOKBACKS/REBALANCES/FEES/SLIPS/COST_VARIANTS as C360. 4×6×3×3×3×2=1296. Placebo seed `20261226`. Reference `hill_tail_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={hill_tail_dev,hill_sign_tail_dev}`. Gates/verdict identical to C360.

### Deliverables — identical 6-item C360 pattern under `campaign362_*`.

---

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C375 (ALL FORMAL NEGATIVES)`.** Terminal closure by fiat PROHIBITED — execute pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. C365–C375 all FROZEN formal negatives. **C376 (QSPREAD — REALIZED QUANTILE SPREAD PROFILE) is the ACTIVE next campaign — PRE-SEEDED, execute end-to-end now. C377 (PSLOPE) is PRE-SEEDED behind it.**

**Bottlenecks: NONE — environment fully ready (re-verified 2026-11-18T22:33:09Z: C375 frozen artifacts present, C376 absent from disk, C312 10×315,648 intact, deps importable).** C312 5m present (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 symbols × 315,648 bars). Deps verified importable (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). C287 451/403 permanently blocked but DECOUPLED — never retry; not on the critical path. No queued/blocked sessions. **C374 SIGNRUN FROZEN formal negative — `campaign374_*` scripts/tests/cache/reports present and frozen (20261118T212227Z).** **C375 ACOVK FROZEN formal negative — `campaign375_*` scripts/tests/cache/reports present and frozen (20261118T222249Z).** **C376 QSPREAD is now ACTIVE — PRE-SEEDED with a full executable spec in the INITIAL TASK MESSAGE above** (2 real signals `qspread_ratio_dev`/`qspread_asym_dev` + 2 placebos, 1296 configs 4×6×3×3×3×2, W=256, placebo_seed=20261240, ref `qspread_ratio_dev` L=240 H=4). Next session must execute C376 end-to-end by cloning C375 (build, preflight, full 1296-config costed OOS sweep, pytest incl. brute-force equality, 5 SHA256 artifacts, durable record). Queue depth is 2+ (C376 active, C377 PSLOPE pre-seeded with a full executable OLS-t-stat spec in the INITIAL TASK MESSAGE, plus a VOVR C378 backlog) so the queue can never be empty.

## C371 — FROZEN CAMPAIGN (RSK/RKT; executed after C370 froze, see C371 RESULT block)

C371 (REALIZED SKEWNESS & REALIZED KURTOSIS × SEASONAL-DISLOCATION mean-reversion stat-arb) is fully executed and frozen — see **C371 RESULT** block (frozen 20261118T151130Z). DO NOT re-run.

---

## C372 — FROZEN CAMPAIGN (TIRV; executed after C371 froze, see C372 RESULT block)

C372 (REALIZED TIME-IRREVERSIBILITY / LAGGED-PRODUCT CUMULANTS (TIRV) × SEASONAL-DISLOCATION mean-reversion stat-arb) is fully executed and frozen — see **C372 RESULT** block (frozen 20261118T160248Z). DO NOT re-run.

---

## C373 — ARCHIVED SPEC (EXECUTED — FROZEN FORMAL NEGATIVE, DO NOT re-run; see C373 RESULT)

**C373 — REALIZED LÉVY/JUMP-ROBUST MedRV (RLRV) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m, price-only, volume-free, on real C312 5m data).** Jump-robust volatility estimator using median-of-three adjacent absolute returns: `MedRV[t] = (π/(6-4√3+π))·(W/(W-2))·Σ_{i=t-W+2..t} med(|x_{i-1}|,|x_i|,|x_{i+1}|)²` and its ratio to RV: `medrv_rv_ratio[t] = MedRV[t] / RV[t]`, `W=256`. These probe jump-robust realized volatility — genuinely distinct from C317 (RV), C367 (BPV/JAR), C368 (RMAD/RABS), C364 (DSRV), C366 (RQV), C365 (KER), C362 (Hill EVT), C361/C363/C371 (same-bar distributional moments). Price-only (`perp_close`), volume-free, deterministic, `O(n)` vectorizable via sliding window medians of 3-bar absolute-return triples.

- **Normative Python (must match brute-force test):**
  ```python
  W = 256
  if t < W: medrv = nan; medrv_rv_ratio = nan
  else:
      X = log_return[t-W+1:t+1]
      triples = np.column_stack([np.abs(X[:-2]), np.abs(X[1:-1]), np.abs(X[2:])])
      meds = np.median(triples, axis=1)
      c = np.pi / (6 - 4*np.sqrt(3) + np.pi)
      medrv = c * (W / (W-2)) * np.sum(meds**2)
      rv = np.sum(X**2)
      medrv_rv_ratio = medrv / rv if rv > 0 else nan
  ```
  NaN if `t<W`, any NaN in window, or not finite. `last_move_dir[t]=sign(r[t])`.

- **Vectorized kernel:** sliding window median of 3-bar absolute-return triples via `np.lib.stride_tricks.sliding_window_view` — no Python loop over 315,648 bars × 10 assets. **MUST pass brute-force equality** vs the per-window reference above (`assert maxdiff < 1e-12`).

- **Build:** `data/cache/campaign373_rlrv_5m/<SYM>.npz` from real C312 `perp_close` only: `index_ms` int64 (315,648), `perp_close` float32, `log_return` float32, `abs_ret` float32, `funding_rate` float32 all-NaN. SHA256 shard manifest; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, `rlrv_params={window_W:256}`.

- **Grid (1296, literal `N_TRIALS`):** SIGNALS `{medrv_dev,medrv_rv_ratio_dev,medrv_placebo,medrv_rv_ratio_placebo}`; LOOKBACKS `(60,120,240,480,960,1920)`; REBALANCES `(1,4,12)`; FEES `(0.0004,0.0007,0.0010)`; SLIPS `(0.0,0.0001,0.0002)`; COST_VARIANTS `("taker","maker_blend")`; 4×6×3×3×3×2=1296. WF 12m train/3m test roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261237` (phase-randomized FFT surrogate + rank restoration; NaNs stay NaN). Selection frac=1/3, ALPHA=0.05. Ref/stability config: `medrv_dev`, L=240, H=4, fee 0.0007, slip 0.0001, taker. `ATTR_REPRESENTATIVES={medrv_dev,medrv_rv_ratio_dev}`.

- **Gates/verdict:** identical to C372 (one-sided paired t per split; Holm AND BH over 1296 at α=0.05; MDE power 0.80; stability sign consistency ≥0.70 and half-Sharpe corr ≥0.5; attribution share ≥0.5 by real non-placebo; RETRACTED(multiple_testing|attribution|stability) else EDGE_PROVEN).

- **Deliverables — identical 6-item pattern under `campaign373_*`:** 3 scripts, 2 test files (≥21 green incl. RLRV brute-force equality), cache, preflight `ready:true`, full sweep with 5 SHA256 `reports/campaign373_*_<TS>Z.json` + `.full.json`, durable record + frozen-table row + state.yaml update (`latest_campaign_done: C373`, `next_campaign: C374`).

### Family backlog for C377+ (all price-only, volume-free, close-only; pick in order, do not reuse)

1. **QSPREAD — Realized quantile spread profile** (PRE-SEEDED as C376): `(q90−q10)/max(q75−q25, eps)` tail-vs-core spread shape plus Bowley-type within-tail asymmetry `((q90−q50)−(q50−q10))/max(q90−q10, eps)` over W=256. Distinct from QATM (C363), GMD/IQR (C369), Hill (C362).
2. **PSLOPE — Window OLS trend-slope t-statistic**: regress `log(close)` on bar index over the trailing window; signal = slope / (residual std / sqrt(Σ(t−t̄)²)) = the slope t-stat (trend strength relative to noise). Distinct from KER (C365 displacement/path-length ratio), Hurst/DFA (C346/C350 scaling exponents), variance ratio (C353), and all moment/entropy families — this is **fitted-trend significance**, never used.
3. **VOVR — Volatility-of-volatility ratio**: split the W=256 window into 16 non-overlapping 16-bar blocks, compute each block's realized variance, and form `vovr = std(block_RV)/max(mean(block_RV), eps)` (dispersion of volatility across sub-blocks). Distinct from RQV (C366 within-window 4th moment/top-k concentration of squared returns), RV level (C317), RMAD (C368), MedRV (C373) — this is **cross-sub-block RV dispersion**, never used.

### C375 — FROZEN (executed/frozen 20261118T222249Z; archived spec, DO NOT re-run)

**C375 — MULTI-LAG REALIZED AUTOCOVARIANCE PROFILE (ACOVK) × SEASONAL-DISLOCATION mean-reversion stat-arb, USDT-M 5m, price-only, volume-free, on real C312 `perp_close`.** Per bar t over `X=r[t-W+1..t]`, `γ_k=(1/(W-k))·Σ_{i=t-W+1+k..t} x_i·x_{i-k}` for `k∈{1,2,4,8}`; `acov_sum=γ_1+γ_2+γ_4+γ_8`, `acov_decay=γ_1−γ_8`; NaN if `t<W`, any NaN, or non-finite. Vectorized form: `p_k[i]=r[i]·r[i-k]` then `γ_k[t]=rolling_mean(p_k, W-k)[t]` — MUST match the per-window reference with `maxdiff < 1e-12`. Signals `{acov_sum_dev, acov_decay_dev, acov_sum_placebo, acov_decay_placebo}`, 1296 configs, placebo seed `20261239`, ref `acov_sum_dev` L=240 H=4 fee 0.0007 slip 0.0001 taker; cache `data/cache/campaign375_acovk_5m/` with `acovk_params={window_W:256, lags:[1,2,4,8]}`. Deliverables: 3 scripts, 2 tests (≥21 green incl. brute-force equality), cache, preflight `ready:true`, full 1296-config costed OOS sweep → 5 SHA256 `reports/campaign375_*_<TS>Z.json` + `.full.json`, durable record here + frozen-table row + `research_state/state.yaml` (`latest_campaign_done: C375`, `next_campaign: C376`). **C375 does not exist on disk — it is pure work to do.**

### C376 — ACTIVE CAMPAIGN (execute end-to-end NOW; full executable spec in the INITIAL TASK MESSAGE above)

**C376 — REALIZED QUANTILE SPREAD PROFILE (QSPREAD) × SEASONAL-DISLOCATION mean-reversion stat-arb, USDT-M 5m, price-only, volume-free, on real C312 `perp_close`.** Over `X=r[t-W+1..t]`, `W=256`:
```python
q10, q25, q50, q75, q90 = np.percentile(X, [10, 25, 50, 75, 90])
qspread_ratio = (q90 - q10) / max(q75 - q25, 1e-12)          # tail-vs-core spread shape
qspread_asym  = ((q90 - q50) - (q50 - q10)) / max(q90 - q10, 1e-12)   # Bowley-type within-tail asymmetry
```
NaN if `t<W`, any NaN in window, non-finite, or a denominator ≤ `eps=1e-12`. Distinct from C363 (QATM Galton skew + boxplot outlier rate), C369 (GMD/IQR level), C362 (Hill EVT tail index), C361/C371 (central moments), C364 (semivariance sign split), C366 (quarticity/top-k concentration), C374 (run lengths), C375 (autocovariance profile). Cache `data/cache/campaign376_qspread_5m/` (fields `index_ms/perp_close/log_return/abs_ret/funding_rate`, `qspread_params={window_W:256, quantiles:[0.10,0.25,0.50,0.75,0.90]}`); SIGNALS `{qspread_ratio_dev, qspread_asym_dev, qspread_ratio_placebo, qspread_asym_placebo}`; 4×6×3×3×3×2=**1296** configs; LOOKBACKS `(60,120,240,480,960,1920)`; REBALANCES `(1,4,12)`; FEES `(0.0004,0.0007,0.0010)`; SLIPS `(0.0,0.0001,0.0002)`; COST_VARIANTS `("taker","maker_blend")`; WF 12m/3m roll 3m → 8 splits 2023-01..2025-12; placebo seed `20261240`; ref/stability `qspread_ratio_dev, L=240, H=4, fee 0.0007, slip 0.0001, taker`; `ATTR_REPRESENTATIVES={qspread_ratio_dev,qspread_asym_dev}`; brute-force equality test mandatory (`maxdiff < 1e-12`, vectorized `sliding_window_view` + `np.percentile` vs per-window reference loop); deliverables identical 6-item pattern, then `state.yaml` (`latest_campaign_done: C376`, `next_campaign: C377` from PSLOPE above).

---

## Frozen campaigns (do NOT re-run)

C281B–C372: ALL FORMAL NEGATIVES, 0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`, `attribution_ok:false`, verdict RETRACTED. Full per-campaign SHAs + cache SHAs in `research_state/state.yaml` and `reports/`.

| Camp | Frozen ts (UTC) | Family | n_configs | Dominant attribution | oos_sweep sha256 | verdict sha256 |
|---|---|---|---|---|---|---|
| C337 | 20261116T234925Z | orderflow skew | 7776 | asym_placebo 0.1957 | state.yaml | state.yaml |
| C338 | 20261117T004211Z | orderflow entropy | 4212 | shannon_entropy_placebo 0.1367 | state.yaml | state.yaml |
| C339 | 20261117T005324Z | orderflow return alignment | 1944 | align_z_placebo 0.4791 | state.yaml | state.yaml |
| C340 | 20261117T032549Z | trading-activity dispersion | 2592 | flow_cv_placebo 0.1803 | state.yaml | state.yaml |
| C341 | 20261117T031751Z | price-impact dispersion | 2592 | pid_placebo 0.2004 | state.yaml | state.yaml |
| C342 | 20261117T034113Z | vol-weighted return moments | 2592 | kurt_placebo 0.1842 | `5625dc783dd53e5ef49b5ea448a33979edbffe78c5d612e1968c607b96b51985` | `7c8f75c4ab824aa5f80012621ebec60f8d4318da09af41fb07c86d73476274a0` |
| C343 | 20261117T041856Z | vol clustering / \|r\| autocorr | 1944 | vcr_placebo 0.2445 | `c1193a4e4dd708c87ad7f582c383ba1ceeec20b95ec044eabb17ae2123ba78a5` | `983ccc56d6a455640565b3853224dddab70d2a6898d0591eb2d7d2647b830af7` |
| C344 | 20261117T042911Z | return sign-change / chop | 1296 | chop_placebo 0.2519 | `37d4b29b371661db7ff98c8fc94650f9bc8f4a79cd5edf9ca4b8f6d141d7d337` | `0dc1a72af26f275485d1a862480bec27614c7c2006f9ca87ae6e3a5a6fd42cb9` |
| C345 | 20261117T052603Z | close-location (Williams %R) | 1296 | wr_placebo 0.2596 | `c0078c5539823d4ba4b2e7cec0e36e9fcc8ae4443487f4578a1d2316f7904616` | `52a3bbefe07a58b04fb66d715aed3f47781ae15f95758b1a58e1ffe48a15a92c` |
| C346 | 20261117T063205Z | rescaled-range / Hurst (R/S) | 1296 | rs_dir_placebo 0.4432 | `977a60576be0395b37ab6f8001fa1a11d5803ad361b3a77d72dfb780e5a8f784` | `d846c590b179167d77802dc8d5681a456bc61916d715824f643438d2208aa87a` |
| C347 | 20261117T073740Z | drawdown duration / time-under-water | 1296 | dd_long_placebo 0.2783 | `9415b29aec5d7b0a796b4906b47db77dbaba03cc4c486edd574f43efdfa16a41` | `e974564b40f571f98cd0db2ef2a6328710daff9fc2c60bba3c936de14cd06c87` |
| C348 | 20261117T082608Z | realized-variance concentration (HHI) | 1296 | hhi_placebo 0.3768 | `b951f1abe8c01c748aaca77c737aba56d72aa1fe9e5e9b77b894779eff871640` | `7338068e5f221cacf9320b4a6d9ca306459f3f479b0b12be4ef21d175b03ef81` |
| C349 | 20261117T130414Z | permutation entropy (Bandt–Pompe) | 1296 | perm_ent_dev 0.2513 | `98d792fe1f7675f1b457b30a9aceab99c0923be22dd557328cb5f60f3efb8811` | `b91138b2dbc6319e6ff665cb7e46591c4bbb7b0dd299ee3e03b3c84f69f650dc` |
| C350 | 20261117T140129Z | DFA scaling exponent α | 1296 | dfa_placebo 0.2644 | `0f2a23039e47c790eddc2f7ad1a09921de9e13114f12faa19b5ffc3547eb0286` | `ac90205fc7f86e12ce3795713bf182bb316952e7cc58b4086eeecf3378001c8f` |
| C351 | 20261117T141619Z | GPH fractional integration d | 1296 | gph_abs_dev 0.2933 | `7e82d2653d659c2c56bc429fdf24a75a029dfa8a8e5f2ff570bebacc8be533a2` | `e002a155f0a51d8d5128ccbb033000dd72bb1696b1adf668d33ab0c4bfce630c` |
| C352 | 20261117T150754Z | local-Whittle MLE d | 1296 | lw_abs_placebo 0.3195 | `39657e8df596360efe4e42db7ec200df7265153f62db47d97b5a2fcd3d8775ec` | `82f9f754c1345551e18fcfd94beeba76200dbb2d8ccd3843ce7edc374f304d4b` |
| C353 | 20261117T161918Z | variance-ratio (Lo–MacKinlay) | 1296 | vr8_placebo 0.3065 | `fa0016cc882d375350f58b0117526abf4664fcf88b0eb4a87520a77c79b0301f` | `edad339416b9924549500a46741341d09410c6519f7c400021f5590cf734ae96` |
| C354 | 20261117T171655Z | Higuchi fractal dimension (HFD) | 1296 | hfd_placebo 0.2595 | `7a4b0a535616d52f757fff5d918da85161416fd148eb189c1f3f063bd5eb59f6` | `3f4138e4ec50a3710555c5f8f929afdf59556a4833f4746ec47424af6c72649a` |
| C355 | 20261117T204322Z | Sample Entropy (SampEn) | 1296 | sampen_m3_placebo 0.3069 | `3febf019a380a23559b4d931ed301386fe77c4b5f979356d359367138b436ba8` | `590143e898ee54faecc834c0070fb3f5fb60dddf9fd8bf6b152eee8a62ae806c` |
| C356 | 20261117T221026Z | Multiscale Entropy (MSE) | 1296 | mse_area_placebo 0.2559 | `f4c5cf8e3094a65a0319fc2aed63c00a492fb36bec57ffccf4358e3ea5ddcf36` | `f3b8cb864be93f40c7af8e826e3d90f7e606584a47d072353ec64ab8a509c437` |
| C357 | 20261117T224353Z | Lempel–Ziv Complexity (LZC) | 1296 | lzc_sign_placebo 0.2856 | `ebb610a78530263d7f24f189bcebc5e46be6f6d0c57436b73f1824691ed5bc89` | `8a21578e6c970d2ba68ac21da338f7f5f43c03a7a7d08cb06741e9bc24d5c176` |
| C358 | 20261117T235447Z | MF-DFA generalized Hurst h(q) | 1296 | mfdfa_spread_dev 0.3312 | `11a05f1428a1e1d22c4d0fc993c3fe76a69cdd0fd8e31704c2f8e3dc188095c9` | `2881c1ec03536b1b89b59c9b97517fa6855c2b20a13ab568d0f560684827656e` |
| C359 | 20261118T005752Z | ordinal pattern transition entropy (OPTE) | 1296 | opte_ent_dev 0.2616 | `761347a2bdf03b49f3811fa728edac8aac724922e9fdc4421205ca24fd47db6a` | `6dc96280f3aaffc7bdeb4170bbd66378c43336915687561d1c6e610085f196b7` |
| C360 | 20261118T014623Z | leverage / volatility-asymmetry coupling (LVAC) | 1296 | lvac_mean_placebo 0.2977 | `0aef7f67d5fc84e604abe0d7091bbad0fc6f69fe14714ed194788bab859177dd` | `acac28ae5fadb802f42b4b4264b6a9cb1101aaadb65e5ac4d1b9ec760bc54d3b` |
| C361 | 20261118T024715Z | raw return skewness & excess kurtosis (RSKEK) | 1296 | rkurt_placebo 0.4324 | `b624fdf359ce6285f32784577845a65117a908a1eb110902ad0251aaa3749340` | `83d13a26aec96d38494b0330d3a4255887f2d09d3283462fb4c09b585b3da3ed` |
| C362 | 20261118T033729Z | Hill tail-index of extreme returns & tail asymmetry | 1296 | hill_sign_tail_placebo 0.3136 | `1b1f5f18e35f1f465555a8a8547db42473f65e605e7d9ca229a042938245ec3d` | `24e9b0be1f48db8061c74872f199d860444da3be08560f51d3808ffb06f00637` |
| C363 | 20261118T035157Z | quantile asymmetry & tail-mass (QATM) | 1296 | qasym_placebo 0.3072 | `6119846ba7763148de9f096909d42cb7d1ade2da2b281a9b5fca73d26067049b` | `34c55d3a53b2fd2a9e20ce54047ff45591e977292426b9411475939339b47639` |
| C364 | 20261118T070416Z | realized semivariance / downside-upside volatility decomposition (DSRV) | 2592 | dsrv_ratio_placebo 0.4716 | `a8ebc63d66f89b48a5d9d04bb1cef1df803ec92fb5515738768f4d590ff98b60` | `d36417e6775cd310a28d544bdefc36ac50a49ab0b9170c4fbe38b1270335cb6f` |
| C365 | 20261118T074457Z | kaufman efficiency ratio / path-straightness (KER) | 1296 | ker_er_dev 0.31897 | `5e36f367773a9025ff6de66e13b30288eacbc8d0e9e7883c856f47d788ae1418` | `ba9518053854ce56abd3965393673d054621b2c75ed8a897ca86463b54d9220b` |
| C366 | 20261118T105747Z | realized quartic variation / kurtosis-concentration of squared returns (RQV) | 1296 | rqv_q_placebo 0.6382 | `aac24596c06662ef3f188950993dca4979e4dba65f7e91ec7bbad9d3d03f1ae5` | `1fa3a763d10d7fbdcef7debd82b2ffef3928467dd059d7c61b281ee9c0d55e1a` |
| C367 | 20261118T110940Z | bipower variation / jump-activity ratio (BPV/JAR) | 1296 | jump_ratio_placebo 0.4523 | `1ced6aa4863592145e91c5ae9cb66df25d2a77a0473d973f88c2d76497c87de0` | `a5301e22844c08c1a5462f7ff9f662d0f7eee486efe3d8fd994e6a4035d9faef` |
| C368 | 20261118T115652Z | realized median absolute deviation & median-of-absolutes volatility (RMAD/RABS) | 1296 | rmad_dev 0.2988 | `c2347d030c8162dfd8c1e8e7e14128ff2d9d597b09f8837c9752da691cc319a7` | `a618e995c63dd0aa05d655111947ca5f102480bcc731bee29453865a5f949b0c` |
| C369 | 20261118T135451Z | gini mean difference & interquartile range (GMD/IQR) | 1296 | iqr_dev 0.3383 | `ed93c318f8551798a81a97f8ca0a907dd2602187abfdedbae959f28d4110f58a` | `549fbeea5aa05b389d570aec552943528cf0137e726b7b68543c918b7f189d75` |
| C370 | 20261118T140545Z | realized absolute return & mean absolute deviation (RAR/MADM) | 1296 | madm_placebo 0.2687 | `0819e8174a481faa20a8c276804a9e485a69cf5c63f7d2d154cf37155209aa9a` | `f932a314aefb7446fd53d929fca83d8df06d619c2f49b16a45e4b6ceb4aac060` |
| C371 | 20261118T151130Z | realized skewness & realized kurtosis (RSK/RKT) | 1296 | rkt_placebo 0.4164 | `5150c94f697e290d5d32d32bd8cba95a8922147f997ba952b84a9618215e85be` | `be74cfdfb404c15682b7b4224ee328d3a37d4465243c6fb605835cf7d91d4ee8` |
| C372 | 20261118T160248Z | realized time-irreversibility / lagged-product cumulants (TIRV) | 1296 | tir4_placebo 0.4789 | `3d8d542a11180f7910cff8942fba708e4f31aab54b762cab09c543fd6ce18788` | `35085dfd74e0426e64eb4ec05b588553e970dc6c405341741979ff497e19b6f6` |
| C373 | 20261118T202427Z | realized Lévy/jump-robust MedRV (RLRV) | 1296 | medrv_rv_ratio_placebo 0.3766 | `b273c2ed4735744f944ae0072ae4755dba39a44c573fc9302acd87176ac88d62` | `c996e92c6de836946d57201a5d080abe1fd83319b804393a07922cf1cd60c222` |
| C374 | 20261118T212227Z | signed run-length asymmetry (SIGNRUN) | 1296 | max_run_share_placebo 0.4773 | `80480e1f473cd7a50dbe9dd5a6c42b5824952f5d901a911472f51f346ac2d10d` | `cb9fd1d125741fab7dd43ff7efd9b8187319db7b24463f4908bdbe0f170adade` |
| C375 | 20261118T222249Z | multi-lag realized autocovariance profile (ACOVK) | 1296 | acov_sum_placebo 0.4173 | `512ea714143752b6adedd92cff7904cf6ce4ea54ff4bb6f8dac241fc5358ee8f` | `19c52ccd115bab44dde1052bd77df34062b54d95a3896f65acfe3462fd667eb8` |

C358 extra SHAs: tradable_edge_registry `1b7a29cae878e97bdd6f952264709dd22358c547e8b48a74b7ec912ea1132f7e`, summary `2998bb4440b93ce293fb87c298ae9c386c19147910d220677fdf2ad660c4a083`, binding_constraint `1a7ad762a238efec0c98cc752745479352657347953b732215bf0a2c7ee46830`. C358 cache SHAs: meta `4a12a5d594afb9e23690a88c439c4dd6ed7b875619d01533ac5fa2e9a72e3655`, provenance `f173ca343bb0188aba9ad46e8e8976f49f452235e504bf93bec2b668fc03c886`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C359 extra SHAs: tradable_edge_registry `af4acf9a1bb7d3818e7ca6dc81701ddff9b9c4e739418d494bac512aee633cef`, summary `3431451cd3a6f7c765396b2d94c061ad6d2e3b2edd1d203d5e83f018cfffe67f`, binding_constraint `8ac5734f487b92a6101396535acc714d0bd8a81ee524705b1907e8a012c5d5b2`. C359 cache SHAs: meta `c532129e610793b67a5267f0f018a8d976aa0bf621ee3779be45756095e1c05f`, provenance `287746d15a0cc0a19059f7f0ba4bc852677ac30fd28d95ecfa6434b7fe888da4`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C360 extra SHAs: tradable_edge_registry `327de19a836b8ee793ef110ece0eebe08e564ed4eed3a4fec15458112b36f3b1`, summary `b7035ece654490b1329f497dc883fa322e7beb417c91347bf114f5bc7f2019cb`, binding_constraint `f8a4c19b85ee97e12d4012fde4b9ef68762e814ca693fe190bcb39fbb9eca585`. C360 cache SHAs: meta `5ba5bfae583622447f505547ffacff1104b1cd300359ebda9c54e6a23ed8e751`, provenance `80d7fccfbc8132e64ec738cf240cb68d2a646c1242b82314e0f6bead0146db2f`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C361 extra SHAs: tradable_edge_registry `e037e8889574fcf3c8a3e1a5fb1be3dd49717047595c95f7f5b7918f96879dd9`, summary `390b04f0c31c13dda351dcfe424bfcdd6a70f3bf55361795c68d5015e9840422`, binding_constraint `3c74387525001bb8d57a15956a2f16b64ab774f864a7734974c214231e8e05a1`. C361 cache SHAs: meta `6b81f7ec02ff231958ca4cfe42b433c5ddeb33e6628f90e54ec6cc88e06b4424`, provenance `f0784f392147ea5af34151121cea5e9c4741b5b79ea5da2f667ec0b4169e635c`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C362 extra SHAs: tradable_edge_registry `78f9d81e7b060b64ee2309b7668666f175aa2506fbdcb1e10ac03288db1f6553`, summary `4fa345c77363a7cd0ff7b30a8574967798dcb4761dd4bad883453676e40cab82`, binding_constraint `1085b11bd0b3c0e82abe24086fa4358f84fef7e80d9a055ff813ed4df794ca26`. C362 cache SHAs: meta `cec80b1bf4a0fd6491b2fdceca9ae410af972cb2af239d45b925bcd360896a26`, provenance `0c2a2b5240e3ec86b926724cf6224664459e8bd0d26709fc00b08b2f2608cb0a`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C363 extra SHAs: tradable_edge_registry `921257c66d9a87fbf598375900a077bf4f9739751dd4ff08695dcb21c41965b0`, summary `b8caec7a7a0b4b72412b8833b8b04b7ff16bd23bea5ef576b5db6dab9088a5cf`, binding_constraint `867389789707568db6b952036eef5c7c26f7a60e876ae0a192605b3143529398`. C363 cache SHAs: meta `fcf8ef6daf351b8547bc9429e17a44286481a196e991f8e699baf5e251d2aff6`, provenance `4eb871e13ba8d884ea91eebdff458e92cd9db1059e8be9f2213d5affffbf0f04`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C364 extra SHAs: tradable_edge_registry `4c7ddc042c7d5e4e6839a112731a61725cb87dbf17fb2b66cb26e56274a1faa3`, summary `8698f1b138821116a26eb377688657408350a04f6e964fdafe763d2314c6b11d`, binding_constraint `8f4a25a222aa1063f734dcb226b2e7ff5fa3c8d2da4399bef7de01ea4f28724d`. C364 cache SHAs: meta `1b7f36c8d2afdb9b9c3a4b0f5e810edec9cfbe61b6e9d256223d3479b03cdddc`, provenance `286c4c2d972df1649a8f02356a4abbbd92fd3c17ebbcd53a55a9fb7b7f6a34a5`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C365 extra SHAs: tradable_edge_registry `afc3ed6aaa8a7c92b96486fb63f375919298539f09bd1d2e9146ff0f56009b48`, summary `a651ec724409e48f0568da4da267a42b74bb7715f85d67e6f06e61a1b7e917b1`, binding_constraint `fef7f58b1b5b87301135daafde697d68e5ec8e00369295a2cb1716580b58bed5`. C365 cache SHAs: meta `137021e54df984932a38c64c44a39a0cd1d3d44aa1d1de7cdd838d0ca428267d`, provenance `22f0a73a92d27673108727b942d9bbb71da2c8f2fcdbc114d328ae6d4a8254e1`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C366 extra SHAs: tradable_edge_registry `b59ded0869447feec23c90bf094bdd265e6574dd1360732c2c3d6070c8259f6c`, summary `c515ab2b721d11be7117c33a54e2db54bf5ac8f5f8a438ea715cf4fde327f478`, binding_constraint `dca985e55825299d3aa1b648d8b971d2c28600adfc0b48b2c8487c02c55c411e`. C366 cache SHAs: meta `c2ee29553aa21d805477ca3dfbc79e709b2d2eb86a589ca2863ddde2373c8a42`, provenance `38104b17c511eb3906b2fe08c647523c23cccb8400df09f656c27ffe7c584ca1`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C367 extra SHAs: tradable_edge_registry `50439977ed568a52766bac4d7130875fac82cdd879be9fce7dca91c21808a20a`, summary `3db474314fdbd514f62fbdf96d7fe74a6a0216748c7a25e295405fb32fb5382a`, binding_constraint `66af9f508ca080bee7076507d0c951b94cca821d6d51073ad2cd8b4a0715c6a0`. C367 cache SHAs: meta `618a25263dbac022bba722404b2b6cfd2f8f16fc17db6221ca7a46aa8d700fbd`, provenance `0f728d8c5f6af93079d770645009214ea9e5cb7d672e4a553729eb5f47807d4c`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C368 extra SHAs: tradable_edge_registry `a72ac87a3a7dfa5656655b957602afd5e72f4c2683a74552ca86945f63b08efe`, summary `8bc9f077f08cb921cc1b770de68b2ece4ebbdd48ea3c27aa465310a85969ec0f`, binding_constraint `72f058368cdf00e8db512c07173e8e915e6a7158a5bccf0fda636a3134b959a4`. C368 cache SHAs: meta `cde79282e88326d13ca0a7fa085b46499f61416fb1b5db5e0367b6b75d29fc48`, provenance `7ead06b24d640133d84ba3856353683de7730ed8b2c809be73f605ffff1f7b61`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C369 extra SHAs: tradable_edge_registry `ce178e43956b7d16b41905365ec27f66a25dcaf23d9a20bb1210a91cd3734377`, summary `1f68cc4c2044fa732d48a62413f65640be9e2581ee0072efa1bb2be3192e68d0`, binding_constraint `55e5dd104610f0da9bd2211e60cb4ae50464269a7581a0ca62abe586e7281e9d`. C369 cache SHAs: meta `b0049dd0a3b114a66a7df32c753bb9608e9a606ebab4667e98fa1399400620fe`, provenance `e455871e144a44c9ca2fffb060f2232916e6fc4acca053c32ea3bb9386eeb051`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C370 extra SHAs: tradable_edge_registry `05dffa8529acbbafa874060d5fe237705d6914906e5c65a2628eebaa6d0a0e2f`, summary `ef3f9032acc8bd0e78d87e80ef15a28a22c2649ba42d6b8e539577623fd5912a`, binding_constraint `f932a314aefb7446fd53d929fca83d8df06d619c2f49b16a45e4b6ceb4aac060`. C370 cache SHAs: meta `710f2dfd31ee00009395e3f41214b7e484f48ab54ab49e40e6e9b8fc34c220d1`, provenance `9a57986251c2fdc1c62f48ea6dd1768ede00c7651904ca3100b7e60e6b372b7f`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.
C371 extra SHAs: tradable_edge_registry `099e40dbfb950a4b4f8197de685db5f98c5d3ae0a2e51ae55ebf0e82d2cff6c2`, summary `e627c2746c0eec2f7cd115faa4a6a501167cdcfaedb3d53253bcbc2a80356c0b`, binding_constraint `8dc86c771e447abdf81070bcd6dccb46bbffae951531032c3e21cc4bf4e0475d`. C371 cache SHAs: meta `d762bc9ae1d44d36368d4adf3b13e7baf01bb8a3e3c263152b97802d44892874`, provenance `3cdef5b6e618fbea7ec19a456099b9e4129fbc62e2c5bb5ac34b8b4876b56399`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C372 extra SHAs: tradable_edge_registry `c4099295b3c5e73c0517f517c89be32dab5609d66618a5791de260bd763a0809`, summary `759d550a0aa3f1a550a3272b43c9154570339cb797cc2afe8ec8492c108cf552`, binding_constraint `4c4f4a39f1a04e1458d48f950c3ab71321d135fe9403ad299e6bef32130015ce`. C372 cache SHAs: meta `6690fe01770596250dce0af753dd876562b62cd41b2aa44d0835e63cff6e173b`, provenance `faf9e03a59cf1ec10109d0143d17e21015901d6fd0adb52b3578ea998f4ac424`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C373 extra SHAs: tradable_edge_registry `0e45d164e160525b41d035426e98e8e586ab699a2a5d653b993a379850daf75a`, summary `c4e04f3c2312d13627bdc8b7cd3c3025ef58e57541300814e8211c7404353b8e`, binding_constraint `b0d97de1c03b24fac98b6c3e842b0d3c2f060a219e1b999efeb9d89ee5526ee3`. C373 cache SHAs: meta `020b7edf8f129cc1bb8fb3707779960ad954124e0e23ecc8e1c47520611c64c1`, provenance `8297cf7906d0f5ffc91028290c314ec4ab271b9722577fbaa2657d8012d4b79a`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

---

## C371 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T151130Z)

C371 (REALIZED SKEWNESS & REALIZED KURTOSIS (RSK/RKT) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a FORMAL NEGATIVE: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `rkt_placebo` 0.4164 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. RSK/RKT brute-force equality, `maxdiff < 1e-12`). Cache `data/cache/campaign371_rskrkt_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C371. Frozen — DO NOT re-run.

- oos_sweep `5150c94f697e290d5d32d32bd8cba95a8922147f997ba952b84a9618215e85be`
- tradable_edge_registry `099e40dbfb950a4b4f8197de685db5f98c5d3ae0a2e51ae55ebf0e82d2cff6c2`
- summary `e627c2746c0eec2f7cd115faa4a6a501167cdcfaedb3d53253bcbc2a80356c0b`
- verdict `be74cfdfb404c15682b7b4224ee328d3a37d4465243c6fb605835cf7d91d4ee8`
- binding_constraint `8dc86c771e447abdf81070bcd6dccb46bbffae951531032c3e21cc4bf4e0475d`
- cache: meta `d762bc9ae1d44d36368d4adf3b13e7baf01bb8a3e3c263152b97802d44892874`, provenance `3cdef5b6e618fbea7ec19a456099b9e4129fbc62e2c5bb5ac34b8b4876b56399`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C372 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T160248Z)

C372 (REALIZED TIME-IRREVERSIBILITY / LAGGED-PRODUCT CUMULANTS (TIRV) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a FORMAL NEGATIVE: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `tir4_placebo` 0.4789 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. TIRV brute-force equality, `maxdiff < 1e-12`). Cache `data/cache/campaign372_tirv_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C372. Frozen — DO NOT re-run.

- oos_sweep `3d8d542a11180f7910cff8942fba708e4f31aab54b762cab09c543fd6ce18788`
- tradable_edge_registry `c4099295b3c5e73c0517f517c89be32dab5609d66618a5791de260bd763a0809`
- summary `759d550a0aa3f1a550a3272b43c9154570339cb797cc2afe8ec8492c108cf552`
- verdict `35085dfd74e0426e64eb4ec05b588553e970dc6c405341741979ff497e19b6f6`
- binding_constraint `4c4f4a39f1a04e1458d48f950c3ab71321d135fe9403ad299e6bef32130015ce`
- cache: meta `6690fe01770596250dce0af753dd876562b62cd41b2aa44d0835e63cff6e173b`, provenance `faf9e03a59cf1ec10109d0143d17e21015901d6fd0adb52b3578ea998f4ac424`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C373 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T202427Z)

C373 (REALIZED LÉVY/JUMP-ROBUST MedRV (RLRV) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a FORMAL NEGATIVE: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `medrv_rv_ratio_placebo` 0.3766 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. RLRV brute-force equality, `maxdiff < 1e-12`). Cache `data/cache/campaign373_rlrv_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C373. Frozen — DO NOT re-run.

- oos_sweep `b273c2ed4735744f944ae0072ae4755dba39a44c573fc9302acd87176ac88d62`
- tradable_edge_registry `0e45d164e160525b41d035426e98e8e586ab699a2a5d653b993a379850daf75a`
- summary `c4e04f3c2312d13627bdc8b7cd3c3025ef58e57541300814e8211c7404353b8e`
- verdict `c996e92c6de836946d57201a5d080abe1fd83319b804393a07922cf1cd60c222`
- binding_constraint `b0d97de1c03b24fac98b6c3e842b0d3c2f060a219e1b999efeb9d89ee5526ee3`
- cache: meta `020b7edf8f129cc1bb8fb3707779960ad954124e0e23ecc8e1c47520611c64c1`, provenance `8297cf7906d0f5ffc91028290c314ec4ab271b9722577fbaa2657d8012d4b79a`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C359 — ARCHIVED SPEC (frozen formal negative; kept for reproducibility, DO NOT re-run)

C359 was **ORDINAL PATTERN TRANSITION ENTROPY (OPTE)**: Bandt–Pompe ordinal patterns of dimension D=5, delay τ=1 over trailing returns W=256 → 120 permutation states; consecutive states form transitions accumulated into a 120×120 count matrix C; `P=C/rowsum(C)` (zero rows → uniform); marginal `p_i=rowsum(C)_i/ΣC`; scalars `opte_ent = -Σ_i p_i Σ_j P_ij ln P_ij` (transition entropy rate, nats) and `opte_complexity = opte_ent × JSD(P, U_120)` (statistical complexity). Same 1296-config grid, seasonal-dislocation baseline, cross-sectional dollar-neutral construction, gates (Holm+BH+MDE+stability+attribution) and artifact layout as C360. Executed 20261118T005752Z → RETRACTED (multiple_testing). Scripts/cache/tests/artifacts on disk under `campaign359_*`.

---

## C374 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T212227Z)

C374 (SIGNED RUN-LENGTH ASYMMETRY (SIGNRUN) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a FORMAL NEGATIVE: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `max_run_share_placebo` 0.4773 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. SIGNRUN brute-force equality). Cache `data/cache/campaign374_signrun_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C374. Frozen — DO NOT re-run.

- oos_sweep `80480e1f473cd7a50dbe9dd5a6c42b5824952f5d901a911472f51f346ac2d10d`
- tradable_edge_registry `ac605492ee9510f31d0334ff6165c5c623bc841d7817b8fe65360ff50422ae4a`
- summary `5e0ae2bb8886343a5c99794b0596cc81d419b345750def40bf2fa7406df2f8ba`
- verdict `cb9fd1d125741fab7dd43ff7efd9b8187319db7b24463f4908bdbe0f170adade`
- binding_constraint `7492e120993be80822b3e080bc7124a94d4176ffc95e78d0a5805193b0bfa820`
- cache: meta `5cfae24a64131505eefd2e3a70645b0186fd5ee6c8835e4bb7569f88b5df6653`, provenance `945b58c16d2080508b07a59543af5b427ccb5406a946868e45f6aef30cf45044`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (10 shards × 315,648 bars)

## C375 RESULT — FROZEN FORMAL NEGATIVE (frozen 20261118T222249Z)

C375 (MULTI-LAG REALIZED AUTOCOVARIANCE PROFILE (ACOVK) × SEASONAL-DISLOCATION mean-reversion stat-arb) was fully executed on real C312 5m data and is a FORMAL NEGATIVE: 1296 configs costed-OOS, **0 Holm+BH survivors**, `edge_proven:false`, binding `multiple_testing`, dominant attribution `acov_sum_placebo` 0.4173 (placebos dominate — no real-vs-placebo separation). All 5 SHA256 artifacts + gitignored `.full.json` on disk; 22/22 tests green (incl. ACOVK brute-force equality, `maxdiff < 1e-12`). Cache `data/cache/campaign375_acovk_5m/` (10 shards × 315,648 bars, 38.5 MB). NO EDGE through C375. Frozen — DO NOT re-run.

- oos_sweep `512ea714143752b6adedd92cff7904cf6ce4ea54ff4bb6f8dac241fc5358ee8f`
- tradable_edge_registry `02c2eca46cf256fec14b0107715dc633bbad56d5cc28fd0d7b39281e3807ea39`
- summary `a3075f41ed6683669f48f8c8c671f6847be97a158544157c429cf82487f9f185`
- verdict `19c52ccd115bab44dde1052bd77df34062b54d95a3896f65acfe3462fd667eb8`
- binding_constraint `4bad255546d62dc2f16f8e654c237debbc564fd7b17767aaa2a9efc5862f9996`
- cache: meta `00c8b7afa919a176139248b471c89f8fa501c68b6d227daa00488ed2cb74e688`, provenance `244368476b7d95dd91095b175047433b58bd23491c4733cf8c782f1f73053418`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (10 shards × 315,648 bars)
