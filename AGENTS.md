# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T23:37:05Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority: **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — DO NOT create HANDOFF.md or any duplicate handoff file; update this file in place.**

---

## INITIAL TASK MESSAGE — C358 (timestamped 2026-11-17T23:37:05Z, ACTIVE — FROZEN SPEC, HEAVY EXECUTION REQUIRED)

**EXECUTE C358 NOW (heavy work required; no re-planning, no spec changes, no downscoping): CROSS-SECTIONAL INTRADAY MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA, generalized Hurst exponent h(q) across moments q) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. (timestamped 2026-11-17T23:37:05Z, ACTIVE — FROZEN SPEC, HEAVY EXECUTION REQUIRED)**

### State verified (no bottlenecks)
- C312 5m source present: `data/cache/campaign312_usdt_m_ofi_5m/` (10 symbols × 315,648 bars, `perp_close` 0 NaN, meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`).
- Runtime deps: numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 importable. If missing run `python scripts/bootstrap_dev_env.py` (idempotent).
- C281B–C357 ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~93k+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C357 frozen `20261117T224353Z` (1296, RETRACTED, dominant `lzc_sign_placebo` 0.2856). No edge proven through C357.
- **C358 NOT YET RUN:** no `campaign358_*` cache/scripts/tests/artifacts on disk. This session MUST produce them.
- C287 externally blocked/decoupled (451/403) — never retry as economic work. Do NOT re-run frozen C281B–C357/C287. Do NOT weaken gates. Do NOT declare terminal closure by fiat.

### Mandatory run sequence (economic progress = ALL of these)
1. `python scripts/build_c358_mfdfa_features.py` → `data/cache/campaign358_mfdfa_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; <100 MB).
2. `python scripts/preflight_c358.py` → `ready:true`.
3. `python scripts/run_c358_mfdfa_xsec_oos.py` — **full 1296-config costed-OOS sweep** (no downscoping) → 5 SHA256 artifacts `reports/campaign358_*_<TS>Z.json` + gitignored `.full.json`.
4. `python -m pytest tests/test_preflight_c358.py tests/test_c358_mfdfa_xsec_oos.py -q` — **≥21 green incl. MF-DFA brute-force equality test**.
5. Record truthful result in this `AGENTS.md` (new C358 RESULT) + `research_state/state.yaml`; add C358 to frozen table with 5 SHAs (+ cache SHAs); set C359 active with next genuinely-new price-only family spec placeholder. No edge claim unless Holm+BH over all 1296 AND `attribution_ok` AND `stability`.

Terminal closure by fiat PROHIBITED. A prose-only/partial handoff is a HARD VIOLATION. The heavy sweep IS the deliverable.

---

## C358 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)

**C358 — CROSS-SECTIONAL INTRADAY MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA, generalized Hurst exponent h(q) across moments q) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

### Distinctness (pre-registered)
- MF-DFA (Kantelhardt et al. 2002): multifractal scaling profile across moments `q`. For scales `n ∈ {4,8,16,32,64,128}` within `W=256`, `F_q(n) = [ (1/N_n) Σ_k (F²(n,k))^{q/2} ]^{1/q}` (detrended box mean-square residuals), `h(q)` = OLS slope of `log F_q(n)` vs `log n`. Real scalars: `mfdfa_h0 = h(2)` (standard DFA exponent); `mfdfa_spread = h(-10) - h(+10)` over `q ∈ {-10,-5,-2,-1,1,2,5,10}` (multifractal spectrum width). Genuinely distinct from C350 (monofractal DFA α, single q=2), C346 R/S, C351/C352 GPH/local-Whittle d, C353 variance ratio, C357 LZC, C349 permutation entropy, C355 SampEn, C356 MSE, C354 Higuchi, C343 |r| autocorr, C344 sign-change, C326 lag-1 autocorr, C345 close-in-envelope, C317 realized-vol; C342/C340/C341 need volume; C315/C320 trade raw seasonal return. Price-only (`perp_close`), volume-free.

### Raw inputs (build)
`data/cache/campaign358_mfdfa_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network/fabrication/resampling/imputation):
```
index_ms      int64    common 5m grid (intersection, 315,648 bars)
perp_close    float32  real 5m kline close
log_return    float32  r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest.

### Runner-derived causal metrics (per asset, per bar t)
`W=256`, scales `n∈{4,8,16,32,64,128}` (all divide 256), `q∈{-10,-5,-2,-1,1,2,5,10}`, linear detrend `m=1`.
- Trailing returns `X=r[t-W+1..t]` (NaN if `t<W` or any NaN); demean `y=X-mean(X)`; integrate `Y=cumsum(y)`.
- For each `n`: split `Y` into non-overlapping front boxes of length `n` (tile `[0,W)`); per box OLS-detrend → residual `ε`; `F²(n,k)=mean(ε²)`.
- For each nonzero `q`: `F_q(n)=[(1/N_n) Σ_k (F²(n,k))^{q/2}]^{1/q}` (`q=2` via sqrt; guard `q<0` zeros). NaN if any `F²(n,k)≤0` for `q<0` or `N_n<1`.
- `mfdfa_h0[t]=h(2)` = OLS slope of `log F_2(n)` vs `log n` over 6 scales.
- `mfdfa_spread[t]=h(-10)-h(+10)` (each `h(q)` = OLS slope of `log F_q(n)` vs `log n`). NaN if either NaN (require ≥4 finite `F_q(n)` points per slope).
- `last_move_dir[t]=sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday×tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t]=-(v[t]-seasonal_mean)/seasonal_std` for `v∈{mfdfa_h0,mfdfa_spread}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `mfdfa_h0` and `mfdfa_spread` for all bars per asset with vectorized `sliding_window_view` + chunked box-detrending (no Python loop over 315,648 bars × 10 assets). MUST pass brute-force equality test against reference per-window MF-DFA (manual loop over windows, per-box `np.polyfit` detrend, explicit `F_q(n)` and OLS slope).

### Pre-registered grid — 1296 configs
- SIGNALS = `mfdfa_h0_dev`, `mfdfa_spread_dev`, `mfdfa_h0_placebo`, `mfdfa_spread_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60,120,240,480,960,1920)`; REBALANCES = `(1,4,12)`; FEES = `(0.0004,0.0007,0.0010)`; SLIPS = `(0.0,0.0001,0.0002)`; COST_VARIANTS = `("taker","maker_blend")`.
- 4×6×3×3×3×2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits 2023-01..2025-12. Placebo seed `20261224` (phase-randomized FFT surrogate + rank restoration; NaN positions stay NaN). selection frac=1/3, ALPHA=0.05.
- Reference config: `mfdfa_h0_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES={mfdfa_h0_dev,mfdfa_spread_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND BH over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config).
- **Attribution**: mean |OOS net| per signal across its configs; shares = |mean|/sum(|means|) over all 4 incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (ALL six, in order)
1. `scripts/build_c358_mfdfa_features.py` → `data/cache/campaign358_mfdfa_5m/`
2. `scripts/preflight_c358.py` → `ready:true`
3. `scripts/run_c358_mfdfa_xsec_oos.py` → 5 SHA256 artifacts + `.full.json`: `oos_sweep`, `tradable_edge_registry`, `summary`, `verdict`, `binding_constraint` (`reports/campaign358_*_<TS>Z.json`)
4. `tests/test_preflight_c358.py` + `tests/test_c358_mfdfa_xsec_oos.py` — ≥21 green (incl. MF-DFA brute-force equality test)
5. Record truthful result in this `AGENTS.md` (C358 RESULT) + `research_state/state.yaml`; add C358 to frozen table with 5 SHAs (+ cache SHAs); set C359 active with next genuinely-new price-only family spec placeholder
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts

---

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C357 (ALL FORMAL NEGATIVES)`.** Terminal closure by fiat PROHIBITED — execute pre-registered genuinely-new price-only families on real on-disk C312 5m data until one proven unreachable with on-disk evidence. C358 is the active pre-registered family.

**Bottlenecks: NONE.** C312 5m present (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars). Runtime deps importable. C287 externally blocked/decoupled (451/403) — never retry.

---

## Frozen campaigns (do NOT re-run)

C281B–C357: ALL FORMAL NEGATIVES, 0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`, `attribution_ok:false`, verdict RETRACTED. Full per-campaign SHAs + cache SHAs in `research_state/state.yaml` and `reports/`.

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
| C352 | 20261117T150754Z | local-Whittle MLE d | 1296 | lw_abs_placebo 0.3195 | `39657e8df596360efe4e42db7ec200df7265153f62db47d97b5a2fcd3d8775ec` | `82f9c754c1345551e18fcfd94beeba76200dbb2d8ccd3843ce7edc374f304d4b` |
| C353 | 20261117T161918Z | variance-ratio (Lo–MacKinlay) | 1296 | vr8_placebo 0.3065 | `fa0016cc882d375350f58b0117526abf4664fcf88b0eb4a87520a77c79b0301f` | `edad339416b9924549500a46741341d09410c6519f7c400021f5590cf734ae96` |
| C354 | 20261117T171655Z | Higuchi fractal dimension (HFD) | 1296 | hfd_placebo 0.2595 | `7a4b0a535616d52f757fff5d918da85161416fd148eb189c1f3f063bd5eb59f6` | `3f4138e4ec50a3710555c5f8f929afdf59556a4833f4746ec47424af6c72649a` |
| C355 | 20261117T204322Z | Sample Entropy (SampEn) | 1296 | sampen_m3_placebo 0.3069 | `3febf019a380a23559b4d931ed301386fe77c4b5f979356d359367138b436ba8` | `590143e898ee54faecc834c0070fb3f5fb60dddf9fd8bf6b152eee8a62ae806c` |
| C356 | 20261117T221026Z | Multiscale Entropy (MSE) | 1296 | mse_area_placebo 0.2559 | `f4c5cf8e3094a65a0319fc2aed63c00a492fb36bec57ffccf4358e3ea5ddcf36` | `f3b8cb864be93f40c7af8e826e3d90f7e606584a47d072353ec64ab8a509c437` |
| C357 | 20261117T224353Z | Lempel–Ziv Complexity (LZC) | 1296 | lzc_sign_placebo 0.2856 | `ebb610a78530263d7f24f189bcebc5e46be6f6d0c57436b73f1824691ed5bc89` | `8a21578e6c970d2ba68ac21da338f7f5f43c03a7a7d08cb06741e9bc24d5c176` |

C357 extra SHAs: tradable_edge_registry `6df653dbc9d465c3c1598ea50a392902f47e5fcfa78143eab5c6f289a80fbf7a`, summary `de0314c9dbaf84303c49f3bbcbb951fdb7305cda2f1bc164cf71cc00e7f209ec`, binding_constraint `0a257a107237f1898c7a6e4c0bbee129b6867d35c91f681aa57a4934d6d6c74e`. C357 cache SHAs: meta `1341c61faff2d49aacb1044f421f797c39663766d9879e662d3c2f136696edc8`, provenance `915d928f07caa5bb40fd9a44ab2efa8505086afdf64355ecbe600a9b4fe90799`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C357 RESULT (frozen 20261117T224353Z) — FORMAL NEGATIVE (RETRACTED)
`verdict:RETRACTED`, `edge_proven:false`, `n_survive_both:0` (binding `multiple_testing`), `attribution_ok:false` (dominant `lzc_sign_placebo` 0.2856). 1296 configs, 26/26 tests, 5 SHA256 artifacts, `real_data_only:true`.

## Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling, no gate weakening, no cherry-picked windows/costs.
- No edge claim unless costed OOS survives Holm+BH over all 1296 configs AND `attribution_ok` AND `stability`.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization.
- No terminal closure by fiat — continue executing pre-registered genuinely-new price-only families until one proven unreachable with on-disk evidence.
