# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T14:07:58Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority (from repo name): **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — do NOT create a separate HANDOFF.md or any duplicate handoff file; update this file in place.**

---

## INITIAL TASK MESSAGE — C351 (timestamped 2026-11-17T14:07:58Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP)

**C351 — CROSS-SECTIONAL INTRADAY FRACTIONAL INTEGRATION ORDER d (Geweke–Porter–Hudak log-periodogram regression) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. FULLY PRE-REGISTERED — DO NOT re-choose the family.**

Context you must accept as true (already verified on disk):
- C281B–C350 are **ALL COMPLETE FORMAL NEGATIVES** on real C312 5m data (~79,500+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C350 `20261117T140129Z` frozen (1296 configs, RETRACTED, dominant `dfa_placebo` 0.2644, 0 Holm+BH). No edge proven through C350.
- **NO BOTTLENOCKS** (re-verified 2026-11-17T14:07:58Z; C351 is UNCLAIMED — no `campaign351_*` cache, scripts, tests, or artifacts exist yet, so start the pipeline fresh with no work lost): C312 5m on disk (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards verified present × 315,648 bars, 2023-01..2025-12, field `perp_close` present — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT); C350 build/cache on disk (`data/cache/campaign350_dfa_5m/`, ~38.48 MB < 100 MB, preflight `ready:true`), full 1296-config sweep complete (5 SHA256 artifacts `reports/campaign350_*_20261117T140129Z.json` + gitignored `.full.json`), tests 26/26 green; runtime deps importable (verified 2026-11-17T14:07:58Z: numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0, py 3.12.3) — run `python scripts/bootstrap_dev_env.py` (idempotent) if missing. C287 external blocked/decoupled (451/403, no creds) — never retry.
- **C350 DFA KERNEL WAS BUGGED AND IS NOW FIXED (do not regress):** the prior session's `scripts/run_c350_dfa_xsec_oos.py::_compute_dfa_vectorized` closed-form had multiple index/algebra errors (crashed with `IndexError` at `P_kS1[s_vec+hi+1]`). It was replaced this session with a correct `numpy.sliding_window_view` + chunked box-detrending kernel, validated to machine precision (~1e-16) against `_dfa_alpha_bruteforce` on random, real, and NaN-injected inputs. C351's periodogram kernel must likewise pass a brute-force equality test.
- **Do NOT** re-read/plan/re-declare closure, re-run frozen C281B–C350/C287, or weaken any gate. Do NOT downscope the 1296-config grid.

**EXECUTE C351 NOW — full pipeline, no pauses (this is the only permitted work):**

1. **Design (PRE-REGISTERED, NON-NEGOTIABLE):** execute the `C351 — PRE-REGISTERED SPEC (ACTIVE)` section below verbatim.
2. **Build** `scripts/build_c351_frac_diff_features.py` → `data/cache/campaign351_frac_diff_5m/` (10 shards `<SYM>.npz` + `meta.json` + `provenance.json` + SHA256 manifest). Real C312 `perp_close` only; cache <100 MB; idempotent (`--force`).
3. **Preflight** `scripts/preflight_c351.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
4. **Sweep** `scripts/run_c351_frac_diff_xsec_oos.py` — full pre-registered costed-OOS grid (1296 configs), 8 splits 12m train/3m test roll 3m over 2023-01..2025-12. Emit 5 SHA256 artifacts: `reports/campaign351_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>Z.json` + gitignored `.full.json`.
5. **Tests** `tests/test_preflight_c351.py` + `tests/test_c351_frac_diff_xsec_oos.py` — ≥21 green (including a GPH brute-force equality test).
6. **Record** the truthful result (formal negative or edge) in this `AGENTS.md` + `research_state/state.yaml`, update the frozen list + SHAs, and set the next genuinely-new price-only family (C352, queued below) as active.

**Exact run sequence (verbatim, no pauses):** `python scripts/preflight_c351.py` → `python scripts/run_c351_frac_diff_xsec_oos.py` (full 1296-config costed-OOS grid, 8 splits 12m train/3m test roll 3m over 2023-01..2025-12 → emits 5 SHA256 artifacts + gitignored `.full.json`) → `python -m pytest tests/test_preflight_c351.py tests/test_c351_frac_diff_xsec_oos.py -q` (≥21 green) → capture the 5 SHA256 artifacts → record the truthful result (formal negative or edge) in this `AGENTS.md` + `research_state/state.yaml`, add C351 to the frozen table with its 5 SHAs, set C352 as active. Only after all five artifacts + green tests exist may you write the result into `AGENTS.md` and `research_state/state.yaml`.

**NO-LIGHT-WORK RULE (non-negotiable):** The ONLY acceptable completion of this session is the on-disk emission of all 5 SHA256 `reports/campaign351_*_<TS>Z.json` artifacts (plus the gitignored `.full.json`) AND ≥21 green tests. A prose summary, a plan, a partial build, a "next steps" note, or another re-read of this handoff WITHOUT those artifacts is a HARD VIOLATION and is NOT economic progress. The full 1296-config costed-OOS sweep IS the deliverable; if it is slow, it is PROGRESS — never abort it, never downscope it, never replace it with a toy subset.

---

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C350 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED:** execute every pre-registered genuinely-new price-only family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C350 DONE/frozen; C351 (cross-sectional intraday fractional integration order d, GPH × seasonal-dislocation mean-reversion) ACTIVE — full pre-registration below; remaining work = build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → record → freeze → set next genuinely-new price-only family active.**

**Bottlenecks: NONE** (re-verified 2026-11-17T14:07:58Z). C312 5m input data sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT — × 315,648 bars, 2023-01..2025-12; field `perp_close`). C350 build/cache on disk (`data/cache/campaign350_dfa_5m/`, ~38.48 MB < 100 MB, preflight `ready:true`), full 1296-config sweep complete (5 SHA256 artifacts `reports/campaign350_*_20261117T140129Z.json` + gitignored `.full.json`), tests 26/26 green. **C350 DFA vectorized kernel bug FIXED + validated this session** (was `IndexError` in `_compute_dfa_vectorized`; replaced with `sliding_window_view` kernel, ~1e-16 vs brute force). C350 verdict: RETRACTED (formal negative), `edge_proven:false`, binding `multiple_testing`, dominant attribution `dfa_placebo` 0.2644 (< 0.5 → `attribution_ok:false`), stability false. C337–C349 caches/artifacts/tests on disk. C287 externally blocked/decoupled (451/403, no creds) — never retry as economic work. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests. The heavy C351 sweep IS the economic progress — do not abort.

**Closure audit (C281B–C318 scope only, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C350 extend the record. Do NOT regenerate/run stale closure generators.

---

## Frozen campaigns (do NOT re-run)

All: 0 Holm+BH survivors, binding `multiple_testing`, verdict RETRACTED, `edge_proven:false`, `attribution_ok:false`, 5 SHA256 artifacts + gitignored `.full.json`, tests green. Full per-campaign SHAs + cache SHAs in `research_state/state.yaml` and `reports/`.

| Camp | Frozen ts (UTC) | Family | n_configs | Dominant attribution (share) | oos_sweep sha256 | verdict sha256 |
|---|---|---|---|---|---|---|
| C337 | 20261116T234925Z | orderflow skew | 7776 | asym_placebo 0.1957 | see state.yaml | see state.yaml |
| C338 | 20261117T004211Z | orderflow entropy | 4212 | shannon_entropy_placebo 0.1367 | see state.yaml | see state.yaml |
| C339 | 20261117T005324Z | orderflow return alignment | 1944 | align_z_placebo 0.4791 | see state.yaml | see state.yaml |
| C340 | 20261117T032549Z | trading-activity dispersion | 2592 | flow_cv_placebo 0.1803 | see state.yaml | see state.yaml |
| C341 | 20261117T031751Z | price-impact dispersion | 2592 | pid_placebo 0.2004 | see state.yaml | see state.yaml |
| C342 | 20261117T034113Z | vol-weighted return moments | 2592 | kurt_placebo 0.1842 | `5625dc783dd53e5ef49b5ea448a33979edbffe78c5d612e1968c607b96b51985` | `7c8f75c4ab824aa5f80012621ebec60f8d4318da09af41fb07c86d73476274a0` |
| C343 | 20261117T041856Z | vol clustering / \|r\| autocorr | 1944 | vcr_placebo 0.2445 | `c1193a4e4dd708c87ad7f582c383ba1ceeec20b95ec044eabb17ae2123ba78a5` | `983ccc56d6a455640565b3853224dddab70d2a6898d0591eb2d7d2647b830af7` |
| C344 | 20261117T042911Z | return sign-change / chop | 1296 | chop_placebo 0.2519 | `37d4b29b371661db7ff98c8fc94650f9bc8f4a79cd5edf9ca4b8f6d141d7d337` | `0dc1a72af26f275485d1a862480bec27614c7c2006f9ca87ae6e3a5a6fd42cb9` |
| C345 | 20261117T052603Z | close-location in trailing envelope (Williams %R) | 1296 | wr_placebo 0.2596 | `c0078c5539823d4ba4b2e7cec0e36e9fcc8ae4443487f4578a1d2316f7904616` | `52a3bbefe07a58b04fb66d715aed3f47781ae15f95758b1a58e1ffe48a15a92c` |
| C346 | 20261117T063205Z | rescaled-range / Hurst proxy (R/S) | 1296 | rs_dir_placebo 0.4432 | `977a60576be0395b37ab6f8001fa1a11d5803ad361b3a77d72dfb780e5a8f784` | `d846c590b179167d77802dc8d5681a456bc61916d715824f643438d2208aa87a` |
| C347 | 20261117T073740Z | drawdown duration / time-under-water | 1296 | dd_long_placebo 0.2783 | `9415b29aec5d7b0a796b4906b47db77dbaba03cc4c486edd574f43efdfa16a41` | `e974564b40f571f98cd0db2ef2a6328710daff9fc2c60bba3c936de14cd06c87` |
| C348 | 20261117T082608Z | realized-variance concentration (HHI) | 1296 | hhi_placebo 0.3768 | `b951f1abe8c01c748aaca77c737aba56d72aa1fe9e5e9b77b894779eff871640` | `7338068e5f221cacf9320b4a6d9ca306459f3f479b0b12be4ef21d175b03ef81` |
| C349 | 20261117T130414Z | ordinal-pattern / permutation entropy (Bandt–Pompe) | 1296 | perm_ent_dev 0.2513 | `98d792fe1f7675f1b457b30a9aceab99c0923be22dd557328cb5f60f3efb8811` | `b91138b2dbc6319e6ff665cb7e46591c4bbb7b0dd299ee3e03b3c84f69f650dc` |
| C350 | 20261117T140129Z | DFA scaling exponent α × seasonal-dislocation MR | 1296 | dfa_placebo 0.2644 | `0f2a23039e47c790eddc2f7ad1a09921de9e13114f12faa19b5ffc3547eb0286` | `ac90205fc7f86e12ce3795713bf182bb316952e7cc58b4086eeecf3378001c8f` |

C348 extra SHAs: tradable_edge_registry `fd3c9aadfc6484b955e7a4164b687a396262662bacfc57871d30d3eea9056b7b`, summary `fa3ac0ce24a80af66cee791fd83692bf6bc2abac5219f10f8b1239d0a2f01ab2`, binding_constraint `85c07aa1f1dfe03dd075c3a401222fa13b2d0f1e0e096873d6b5b05e6a89f306`.
C349 extra SHAs: tradable_edge_registry `60ab151230b9211c2da943e3d990725422b7426a1d903d0ae4ca5bfa471b23a8`, summary `5e64f0197e05ea7a58fe86a0d637532ce1bef59c8c07bbdab975e6601fad2607`, binding_constraint `8f328590e3786454de51d3b13e06b5438ee2deace8f3bf9054d6345a62e7498c`.
C350 extra SHAs: tradable_edge_registry `111b9477136df90d90630cfec87d192c29f4132baa4fda2ade942095a8111995`, summary `72ee010c45d1e69629a404f9a0c51ad1fa0e4c79e19c71af47ca28b5985cfb49`, binding_constraint `05ee31dbbcc744d72262e210ab35f343151eadc9a879f241fd1e19aada995b3b`. C350 cache SHAs: meta `35fd3020e89b0411c6093265683ca1b23f48b968f6c66be7401f2e202e9ad2e9`, provenance `d4e3f82a4839490d6a4897bcecadda85fab82aae55a44d6e7efb19213d71b7ca`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).

---

## C350 RESULT (frozen 20261117T140129Z) — FORMAL NEGATIVE (RETRACTED)

C350 cross-sectional intraday DETRENDED FLUCTUATION ANALYSIS (DFA) scaling-exponent α × seasonal-dislocation mean-reversion on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T140129Z`), tests 26/26 green. **Note:** the runner's vectorized DFA kernel was bugged (IndexError) on first run and was fixed + validated this session before the sweep; the sweep itself completed in ~90s.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `dfa_placebo` 0.2644 (< 0.5; a placebo dominated, as expected for no real edge)
- `stability:false` — reference config `dfa_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker: sign consistency 0.00 (all 8 OOS splits negative)
- PnL is real and non-trivial: all 1296 configs have non-zero turnover (8.7k–94.9k) and non-zero net (all negative, −113.7..−1.48); costs dominate gross (~0.3). Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312.

---

## C350 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

C350 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C349.

**Distinctness proof (pre-registered):**
- C350 measured the **detrended fluctuation analysis (DFA) scaling exponent α** — OLS slope of log fluctuation `F(n)` vs log scale `n` over scales `n ∈ {4, 8, 16, 32, 64, 128}` within intrinsic window `W = 256` bars.
- **C346** measured R/S (single-window range of cumulative centered sum, one effective scale) — C350 is multi-scale *detrended* fluctuation (slope across 6 scales). **C349** measured ordinal-pattern entropy (no integration/detrending). **C326** measured lag-1 signed-return autocorrelation (single pairwise product). **C343** measured autocorrelation of `|r|` (vol clustering). **C344** measured SIGN-CHANGE RATE. **C347** measured drawdown duration. **C345** measured close location within trailing envelope. **C317** measured realized-vol LEVELS. **C342/C340/C341** need volume/notional/price-impact. **C315/C320** trade raw seasonal RETURN mean-reversion.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign350_dfa_5m/<SYM>.npz` per symbol from real C312 `perp_close`. Fields per shard:
```
index_ms      int64    common 5m grid (intersection across all 10 perps, ~315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB (per-symbol float32 npz shards; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic window `W = 256` bars; scales `n ∈ {4, 8, 16, 32, 64, 128}`. For each bar t, trailing `W` returns `r[t-W+1..t]`: demean; profile `y = cumsum(demeaned)`; split `y` into non-overlapping front boxes of scale n (every scale divides 256 so front boxes tile `[0,W)`; reference back segment coincides and leaves F(n) unchanged); OLS-detrend each box; `F(n)=sqrt(mean sq residual)`; `dfa[t]=α[t]=` OLS slope of `log F(n)` vs `log n`. `dfa_norm[t]=dfa[t]-0.5`. NaN if `t<W` or any NaN in window or any F(n)≤0. Vectorized via `sliding_window_view` + chunked box detrending (validated to ~1e-16 vs `_dfa_alpha_bruteforce`).
Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {dfa[t], dfa_norm[t]}`.
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Pre-registered grid — 1296 configs
- SIGNALS = `dfa_dev`, `dfa_norm_dev`, `dfa_placebo`, `dfa_norm_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs**. Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261127`. selection frac = 1/3, ALPHA = 0.05.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `dfa_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`.

---

## C351 — PRE-REGISTERED SPEC (ACTIVE, EXECUTE VERBATIM)

C351 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C350.

**Distinctness proof (pre-registered):**
- C351 measures the **fractional integration order d** via the **Geweke–Porter–Hudak (GPH) log-periodogram regression** on the return series — a *frequency-domain* long-memory estimate: OLS slope of `log I(λ_j)` on `log(4 sin²(λ_j/2))` over Fourier frequencies `λ_j = 2πj/W`. d = 0 short memory; d > 0 long memory / persistence; d < 0 anti-persistence.
- **C350** measured DFA α — a *time-domain* multi-scale *detrended fluctuation* slope (different estimator, different domain; α and d are theoretically related but numerically distinct: GPH regresses the log-periodogram, DFA detrends integrated fluctuations). **C346** measured R/S (time-domain range). **C326** measured lag-1 signed-return autocorrelation (single pairwise product). **C343** measured autocorrelation of `|r|` (vol clustering). **C349** measured ordinal-pattern entropy. **C317** measured realized-vol LEVELS. **C342/C340/C341** need volume/notional/price-impact. **C315/C320** trade raw seasonal RETURN mean-reversion — C351 fades seasonal dislocation in *fractional integration order d*.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign351_frac_diff_5m/<SYM>.npz` per symbol from real C312 `perp_close` (identical 5-field layout to C350; no network, no fabrication, no resampling, no imputation):
```
index_ms int64; perp_close float32; log_return float32 (r[t]=log(c[t]/c[t-1]), r[0]=0); abs_ret float32; funding_rate float32 (all-NaN control)
```
Cache < 100 MB; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest.

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic window `W = 256` bars (fixed, decoupled from seasonal lookback L). For each bar t:
- Take trailing `W` returns `r[t-W+1..t]` (NaN if `t < W` or any NaN in window); demean: `x = window - mean(window)`.
- Periodogram at Fourier frequencies `λ_j = 2πj/W`, `j = 1..m` with `m = W//2 - 1` (exclude DC j=0 and Nyquist): `I(λ_j) = |Σ_{k=0}^{W-1} x[k] e^{-i λ_j k}|²` (via `np.fft.rfft(x)`, `I = |FFT|²`, take `j=1..W//2-1`).
- GPH regression: regress `y_j = log I(λ_j)` on `x_j = log(4 sin²(λ_j/2)) = log(2 - 2cos(λ_j))` (OLS with intercept) over `j=1..m`; `gph[t] = d_hat = -slope`. NaN if `t<W`, any NaN in window, any non-positive/non-finite `I(λ_j)`, or degenerate regression (`Σ(x-x̄)² ≤ 0`).
- `gph_abs[t] = |gph[t]|` — magnitude of long-memory (distinct real signal). (d is already centered at 0, so there is no separate `-0.5`-style norm; `gph` is used directly.)
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {gph[t], gph_abs[t]}` (symmetric z-fade).
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute GPH d for all bars per asset with a vectorized `sliding_window_view` + chunked `np.fft.rfft` path (no Python loop over 315,648 bars × 10 assets), and it MUST pass a brute-force equality test against a reference per-window GPH implementation (manual loop over windows, per-window `np.fft.fft` + `np.polyfit`/`np.linalg.lstsq` regression).

### Pre-registered grid — 1296 configs
- SIGNALS = `gph_dev`, `gph_abs_dev`, `gph_placebo`, `gph_abs_placebo` (2 real: signed d and |d|; 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261217` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN). selection frac = 1/3, ALPHA = 0.05.
- Reference config (stability/attribution): `gph_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {gph_dev, gph_abs_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config above).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c351_frac_diff_features.py` → `data/cache/campaign351_frac_diff_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c351.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c351_frac_diff_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign351_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign351_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign351_summary_<TS>Z.json`
   - `reports/campaign351_verdict_<TS>Z.json`
   - `reports/campaign351_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c351.py` + `tests/test_c351_frac_diff_xsec_oos.py` — ≥21 green (incl. GPH brute-force equality test).
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C351 section) + `research_state/state.yaml`; add C351 to the frozen table with its 5 SHAs; set C352 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

---

## C352 QUEUED (NOT ACTIVE — do NOT start until C351 recorded/frozen)

C352 = a genuinely-new price-only family to be selected by the C351 session from the still-unexplored price-only long-memory / path-property space on real C312 `perp_close` (e.g. local-Whittle exact MLE fractional differencing `d`, or detrended cross-correlation analysis (DCCA) ρ_DCCA scaling exponent). Compact pre-registration to be written by the C351 session into this AGENTS.md before C352 is set active. C351 must finish first.

---

## Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.