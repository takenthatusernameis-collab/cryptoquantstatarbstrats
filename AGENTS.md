# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-18T01:16:50Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority: **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — DO NOT create HANDOFF.md or any duplicate handoff file; update this file in place.**

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

## INITIAL TASK MESSAGE — C360 (timestamped 2026-11-18T01:12:10Z, ACTIVE — FROZEN SPEC, HEAVY EXECUTION REQUIRED)

**EXECUTE C360 NOW (heavy work required; no re-planning, no spec changes, no downscoping): LEVERAGE / VOLATILITY-ASYMMETRY COUPLING (LVAC) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

**FIRST ACTION — non-negotiable, do this before reading further:** run `python scripts/build_c360_lvac_features.py` to materialize `data/cache/campaign360_lvac_5m/`. The C360 spec is already frozen below — DO NOT re-plan, re-design, re-scope, or seek clarification. C360 is the signed return × lagged-magnitude cross-correlation (leverage/volatility-asymmetry coupling) — a genuinely-new cross-moment distinct from C343 (`|r|` autocorr = magnitude–magnitude same series), C326 (lag-1 return autocorr), C344 (sign-change/chop), C345 (close-location), C342 (vol-weighted return moments) and every scaling/Hurst/entropy/ordinal family C346–C359; price-only (`perp_close`), volume-free. Clone the structural template from C359 (`scripts/build_c359_opte_features.py`, `scripts/run_c359_opte_xsec_oos.py`, `scripts/preflight_c359.py`, `tests/test_preflight_c359.py`, `tests/test_c359_opte_xsec_oos.py`) — identical grid, gates, Holm/BH, attribution, artifact layout, brute-force-equality test pattern — and extend OPTE→LVAC per spec. The heavy 1296-config sweep IS the deliverable — a session that only re-reads this message, re-declares closure, re-runs frozen C281B–C359/C287, or returns prose instead of the 5 SHA256 artifacts + ≥21 green tests is a HARD VIOLATION.

### State verified (no bottlenecks)
- C312 5m source present: `data/cache/campaign312_usdt_m_ofi_5m/` (10 symbols × 315,648 bars, `perp_close` 0 NaN, meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`).
- Runtime deps: numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 importable. If missing run `python scripts/bootstrap_dev_env.py` (idempotent).
- C281B–C359 ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~96k+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C359 frozen `20261118T005752Z` (1296, RETRACTED, dominant `opte_ent_dev` 0.2616). No edge proven through C359.
- **C360 NOT YET RUN:** no `campaign360_*` cache/scripts/tests/artifacts on disk. This session MUST produce them.
- C287 externally blocked/decoupled (451/403) — never retry as economic work. Do NOT re-run frozen C281B–C359/C287. Do NOT weaken gates. Do NOT declare terminal closure by fiat.

### Mandatory run sequence (economic progress = ALL of these)
1. `python scripts/build_c360_lvac_features.py` → `data/cache/campaign360_lvac_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; <100 MB).
2. `python scripts/preflight_c360.py` → `ready:true`.
3. `python scripts/run_c360_lvac_xsec_oos.py` — **full 1296-config costed-OOS sweep** (no downscoping) → 5 SHA256 artifacts `reports/campaign360_*_<TS>Z.json` + gitignored `.full.json`.
4. `python -m pytest tests/test_preflight_c360.py tests/test_c360_lvac_xsec_oos.py -q` — **≥21 green incl. LVAC brute-force equality test**.
5. Record truthful result in this `AGENTS.md` (C360 RESULT) + `research_state/state.yaml`; add C360 to frozen table with 5 SHAs (+ cache SHAs); set C361 active with next genuinely-new price-only family spec placeholder. No edge claim unless Holm+BH over all 1296 AND `attribution_ok` AND `stability`.

Terminal closure by fiat PROHIBITED. A prose-only/partial handoff is a HARD VIOLATION.

---

## C360 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)

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

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C359 (ALL FORMAL NEGATIVES)`.** Terminal closure by fiat PROHIBITED — execute pre-registered genuinely-new price-only families on real on-disk C312 5m data until one proven unreachable with on-disk evidence. C360 is the active pre-registered family.

**Bottlenecks: NONE.** C312 5m present (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars). Runtime deps importable. C287 externally blocked/decoupled (451/403) — never retry.

---

## Frozen campaigns (do NOT re-run)

C281B–C359: ALL FORMAL NEGATIVES, 0 Holm+BH survivors, binding `multiple_testing`, `edge_proven:false`, `attribution_ok:false`, verdict RETRACTED. Full per-campaign SHAs + cache SHAs in `research_state/state.yaml` and `reports/`.

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

C358 extra SHAs: tradable_edge_registry `1b7a29cae878e97bdd6f952264709dd22358c547e8b48a74b7ec912ea1132f7e`, summary `2998bb4440b93ce293fb87c298ae9c386c19147910d220677fdf2ad660c4a083`, binding_constraint `1a7ad762a238efec0c98cc752745479352657347953b732215bf0a2c7ee46830`. C358 cache SHAs: meta `4a12a5d594afb9e23690a88c439c4dd6ed7b875619d01533ac5fa2e9a72e3655`, provenance `f173ca343bb0188aba9ad46e8e8976f49f452235e504bf93bec2b668fc03c886`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

C359 extra SHAs: tradable_edge_registry `af4acf9a1bb7d3818e7ca6dc81701ddff9b9c4e739418d494bac512aee633cef`, summary `3431451cd3a6f7c765396b2d94c061ad6d2e3b2edd1d203d5e83f018cfffe67f`, binding_constraint `8ac5734f487b92a6101396535acc714d0bd8a81ee524705b1907e8a012c5d5b2`. C359 cache SHAs: meta `c532129e610793b67a5267f0f018a8d976aa0bf621ee3779be45756095e1c05f`, provenance `287746d15a0cc0a19059f7f0ba4bc852677ac30fd28d95ecfa6434b7fe888da4`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa`.

(Full per-campaign SHAs in `research_state/state.yaml` and `reports/`.)

---

## C359 — ARCHIVED SPEC (frozen formal negative; kept for reproducibility, DO NOT re-run)

C359 was **ORDINAL PATTERN TRANSITION ENTROPY (OPTE)**: Bandt–Pompe ordinal patterns of dimension D=5, delay τ=1 over trailing returns W=256 → 120 permutation states; consecutive states form transitions accumulated into a 120×120 count matrix C; `P=C/rowsum(C)` (zero rows → uniform); marginal `p_i=rowsum(C)_i/ΣC`; scalars `opte_ent = -Σ_i p_i Σ_j P_ij ln P_ij` (transition entropy rate, nats) and `opte_complexity = opte_ent × JSD(P, U_120)` (statistical complexity). Same 1296-config grid, seasonal-dislocation baseline, cross-sectional dollar-neutral construction, gates (Holm+BH+MDE+stability+attribution) and artifact layout as C360. Executed 20261118T005752Z → RETRACTED (multiple_testing). Scripts/cache/tests/artifacts on disk under `campaign359_*`.