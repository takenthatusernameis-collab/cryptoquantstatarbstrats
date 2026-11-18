# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-18T06:46:05Z (single authoritative handoff; RE-VERIFIED on disk 2026-11-18T06:46:05Z — no HANDOFF.md/duplicate handoff files; C363 5 reports present `campaign363_*_20261118T035030Z.json`; C363 template scripts intact & non-empty `scripts/{build,preflight,run}_c363_*.py`, `tests/{test_preflight,test}_c363_*.py`; C312 5m source ready `data/cache/campaign312_usdt_m_ofi_5m/` = 10 symbols × 315,648 bars each with `perp_close`; no `c364`/`dsrv` scripts, tests, cache, or reports present; numpy 2.5.5/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0 importable). C363 QATM FROZEN formal negative (SHAs in `state.yaml`/this handoff); **C364 DSRV is pre-registered and ACTIVE — unexecuted**. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority: **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only. **This refresh (06:46:05Z) is the ONE authoritative timestamp — ignore any earlier per-section timestamp.**

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — DO NOT create HANDOFF.md or any duplicate handoff file; update this file in place.**

> **INITIAL TASK MESSAGE (2026-11-18T06:46:05Z) — NEXT SESSION: EXECUTE C364 DSRV END-TO-END NOW. NO RE-READ-ONLY, NO RE-PLAN, NO DOWNSCOPING, NO STUB/PROSE-ONLY OUTPUT.**
> Repo `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. The ONLY acceptable outcome of the next session is **real execution progress** — a real-data, costed, out-of-sample stat-arb edge attempt on the on-disk C312 5m data — leaving durable artifacts on disk.
>
> **Verified state (2026-11-18T06:46:05Z):** C281B–C363 ALL frozen formal negatives (0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`); C363 verified (5 artifact SHAs + cache SHAs match `research_state/state.yaml`). **C364 DSRV does NOT exist yet** — no `scripts/*c364*`, `tests/*c364*`, `data/cache/campaign364_dsrv_5m/`, or `reports/campaign364_*`. C363 template is intact (clone source). **DO NOT RE-RUN ANY FROZEN CAMPAIGN (C281B–C363, C287).**
>
> **ACTIVE CAMPAIGN: C364 — REALIZED SEMIVARIANCE / DOWNSIDE-UPSIDE VOLATILITY DECOMPOSITION (DSRV) × SEASONAL-DISLOCATION mean-reversion (USDT-M 5m, price-only, volume-free, real C312 `perp_close`).** Full pre-registered spec: **`C364 — ARCHIVED SPEC`** below. Clone/adapt these frozen templates (do NOT modify them): `scripts/build_c363_qatm_features.py`, `scripts/preflight_c363.py`, `scripts/run_c363_qatm_xsec_oos.py`, `tests/test_preflight_c363.py`, `tests/test_c363_qatm_xsec_oos.py`.
>
> **MANDATORY HEAVY-WORK SEQUENCE — EXECUTE IN ORDER, DO NOT STOP AT PLANNING:**
> 1. **WRITE** 5 C364 scripts/tests (adapt C363 template to DSRV spec exactly): `scripts/build_c364_dsrv_features.py`, `scripts/preflight_c364.py`, `scripts/run_c364_dsrv_xsec_oos.py`, `tests/test_preflight_c364.py`, `tests/test_c364_dsrv_xsec_oos.py`.
> 2. **BUILD:** `python3 scripts/build_c364_dsrv_features.py` → `data/cache/campaign364_dsrv_5m/` (SHA-manifested, <100 MB, real-data-only).
> 3. **PREFLIGHT:** `python3 scripts/preflight_c364.py` → must report `ready:true`.
> 4. **FULL SWEEP (NO DOWNSCOPING):** `python3 scripts/run_c364_dsrv_xsec_oos.py` → complete **2592-config** costed OOS sweep producing 5 SHA256 artifacts `reports/campaign364_*_<TS>Z.json` + `.full.json` (`oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint`).
> 5. **TESTS:** `python3 -m pytest tests/test_preflight_c364.py tests/test_c364_dsrv_xsec_oos.py -q` → **≥21 GREEN** incl. DSRV brute-force equality (vectorized kernel vs reference per-window).
> 6. **DURABLE RECORD (truthful):** update this AGENTS.md with a `C364 RESULT` block + add C364 to frozen table with all 5 artifact SHAs (+ cache meta/provenance/manifest SHAs) and update `research_state/state.yaml` to match. On freeze, set **C365 (KER)** ACTIVE per the pre-registered placeholder spec below so work never stalls.
>
> **Continuity guarantee (bottleneck removal):** C365 (KER) is fully pre-registered below — if C364 cannot run for any reason, execute C365 instead; never idle. There is ALWAYS a ready, fully-specified campaign queued.
>
> **Bottlenecks removed (re-verified 2026-11-18T06:46:05Z): NONE.** C312 10 symbols × 315,648 bars ready; numpy 2.5.5/pandas 3.1.1/scipy 1.18.1/pytest 9.2.0 importable; C363 template intact; C287 451/403 permanently blocked but DECOUPLED — never retry. Do NOT weaken gates, do NOT declare terminal closure by fiat, do NOT invent results, do NOT narrow the grid. A session that leaves C364 unbuilt/unrun with only prose is a HARD VIOLATION.

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

---

## C364 — ARCHIVED SPEC (PRE-REGISTERED — NEXT GENUINELY-NEW PRICE-ONLY FAMILY, TO BE EXECUTED)

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

## C365 — ARCHIVED SPEC (PRE-REGISTERED PLACEHOLDER — set ACTIVE on C364 freeze; execute so work never stalls)

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

### Deliverables (ALL six, in order — clone C364 pattern under `campaign365_*`)
1. `scripts/build_c365_ker_features.py` → `data/cache/campaign365_ker_5m/`
2. `scripts/preflight_c365.py` → `ready:true`
3. `scripts/run_c365_ker_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign365_*_<TS>Z.json`)
4. `tests/test_preflight_c365.py` + `tests/test_c365_ker_xsec_oos.py` — ≥21 green (incl. KER brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C365 RESULT) + `research_state/state.yaml`; add C365 to frozen table with 5 SHAs (+ cache SHAs); set C366 active with next genuinely-new price-only family spec placeholder
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

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C363 (ALL FORMAL NEGATIVES)`.** Terminal closure by fiat PROHIBITED — execute pre-registered genuinely-new price-only families on real on-disk C312 5m data until one proven unreachable with on-disk evidence. **C364 DSRV is the active, unexecuted, pre-registered family — execute end-to-end now (heavy work, no downscoping).**

**Bottlenecks: NONE — environment fully ready (re-verified 2026-11-18T06:46:05Z).** C312 5m present (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars: ADA, AVAX, BNB, BTC, DOGE, DOT, ETH, LINK, SOL, XRP). Runtime deps importable (numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0). C287 externally blocked/decoupled (451/403) — never retry. No queued/blocked sessions to unblock. **Outstanding heavy work (mandatory):** write 5 C364 scripts/tests + build cache + preflight `ready:true` + full 2592-config costed OOS sweep + ≥21 green tests incl. brute-force equality + 5 SHA256 artifacts + truthful C364 RESULT/state update + C365 activation on freeze.

---

## Frozen campaigns (do NOT re-run)

C281B–C363: ALL FORMAL NEGATIVES, 0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`, `attribution_ok:false`, verdict RETRACTED. Full per-campaign SHAs + cache SHAs in `research_state/state.yaml` and `reports/`.

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

C358 extra SHAs: tradable_edge_registry `1b7a29cae878e97bdd6f952264709dd22358c547e8b48a74b7ec912ea1132f7e`, summary `2998bb4440b93ce293fb87c298ae9c386c19147910d220677fdf2ad660c4a083`, binding_constraint `1a7ad762a238efec0c98cc752745479352657347953b732215bf0a2c7ee46830`. C358 cache SHAs: meta `4a12a5d594afb9e23690a88c439c4dd6ed7b875619d01533ac5fa2e9a72e3655`, provenance `f173ca343bb0188aba9ad46e8e8976f49f452235e504bf93bec2b668fc03c886`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C359 extra SHAs: tradable_edge_registry `af4acf9a1bb7d3818e7ca6dc81701ddff9b9c4e739418d494bac512aee633cef`, summary `3431451cd3a6f7c765396b2d94c061ad6d2e3b2edd1d203d5e83f018cfffe67f`, binding_constraint `8ac5734f487b92a6101396535acc714d0bd8a81ee524705b1907e8a012c5d5b2`. C359 cache SHAs: meta `c532129e610793b67a5267f0f018a8d976aa0bf621ee3779be45756095e1c05f`, provenance `287746d15a0cc0a19059f7f0ba4bc852677ac30fd28d95ecfa6434b7fe888da4`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C360 extra SHAs: tradable_edge_registry `327de19a836b8ee793ef110ece0eebe08e564ed4eed3a4fec15458112b36f3b1`, summary `b7035ece654490b1329f497dc883fa322e7beb417c91347bf114f5bc7f2019cb`, binding_constraint `f8a4c19b85ee97e12d4012fde4b9ef68762e814ca693fe190bcb39fbb9eca585`. C360 cache SHAs: meta `5ba5bfae583622447f505547ffacff1104b1cd300359ebda9c54e6a23ed8e751`, provenance `80d7fccfbc8132e64ec738cf240cb68d2a646c1242b82314e0f6bead0146db2f`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C361 extra SHAs: tradable_edge_registry `e037e8889574fcf3c8a3e1a5fb1be3dd49717047595c95f7f5b7918f96879dd9`, summary `390b04f0c31c13dda351dcfe424bfcdd6a70f3bf55361795c68d5015e9840422`, binding_constraint `3c74387525001bb8d57a15956a2f16b64ab774f864a7734974c214231e8e05a1`. C361 cache SHAs: meta `6b81f7ec02ff231958ca4cfe42b433c5ddeb33e6628f90e54ec6cc88e06b4424`, provenance `f0784f392147ea5af34151121cea5e9c4741b5b79ea5da2f667ec0b4169e635c`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C362 extra SHAs: tradable_edge_registry `78f9d81e7b060b64ee2309b7668666f175aa2506fbdcb1e10ac03288db1f6553`, summary `4fa345c77363a7cd0ff7b30a8574967798dcb4761dd4bad883453676e40cab82`, binding_constraint `1085b11bd0b3c0e82abe24086fa4358f84fef7e80d9a055ff813ed4df794ca26`. C362 cache SHAs: meta `cec80b1bf4a0fd6491b2fdceca9ae410af972cb2af239d45b925bcd360896a26`, provenance `0c2a2b5240e3ec86b926724cf6224664459e8bd0d26709fc00b08b2f2608cb0a`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C363 extra SHAs: tradable_edge_registry `921257c66d9a87fbf598375900a077bf4f9739751dd4ff08695dcb21c41965b0`, summary `b8caec7a7a0b4b72412b8833b8b04b7ff16bd23bea5ef576b5db6dab9088a5cf`, binding_constraint `867389789707568db6b952036eef5c7c26f7a60e876ae0a192605b3143529398`. C363 cache SHAs: meta `fcf8ef6daf351b8547bc9429e17a44286481a196e991f8e699baf5e251d2aff6`, provenance `4eb871e13ba8d884ea91eebdff458e92cd9db1059e8be9f2213d5affffbf0f04`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C359 — ARCHIVED SPEC (frozen formal negative; kept for reproducibility, DO NOT re-run)

C359 was **ORDINAL PATTERN TRANSITION ENTROPY (OPTE)**: Bandt–Pompe ordinal patterns of dimension D=5, delay τ=1 over trailing returns W=256 → 120 permutation states; consecutive states form transitions accumulated into a 120×120 count matrix C; `P=C/rowsum(C)` (zero rows → uniform); marginal `p_i=rowsum(C)_i/ΣC`; scalars `opte_ent = -Σ_i p_i Σ_j P_ij ln P_ij` (transition entropy rate, nats) and `opte_complexity = opte_ent × JSD(P, U_120)` (statistical complexity). Same 1296-config grid, seasonal-dislocation baseline, cross-sectional dollar-neutral construction, gates (Holm+BH+MDE+stability+attribution) and artifact layout as C360. Executed 20261118T005752Z → RETRACTED (multiple_testing). Scripts/cache/tests/artifacts on disk under `campaign359_*`.

---

## C363 — FROZEN FORMAL NEGATIVE (do NOT re-run)

C363 (QUANTILE ASYMMETRY & TAIL-MASS / QATM) was executed and frozen 20261118T035157Z as a formal negative (SHAs re-verified 2026-11-18). See C363 RESULT + C363 ARCHIVED SPEC (in state.yaml / reports). Do NOT re-run. The next active family is C364, specified in the INITIAL TASK MESSAGE at the top of this handoff.
