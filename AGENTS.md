# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T13:09:21Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority (from repo name): **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — do NOT create a separate HANDOFF.md or any duplicate handoff file; update this file in place.**

---

## INITIAL TASK MESSAGE — C350 (timestamped 2026-11-17T13:09:21Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP)

**C350 — CROSS-SECTIONAL INTRADAY DETRENDED FLUCTUATION ANALYSIS (DFA) SCALING EXPONENT α × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data (USDT-M 5m). FULLY PRE-REGISTERED — DO NOT re-choose the family.**

Context you must accept as true (already verified on disk):
- C281B–C349 are **ALL COMPLETE FORMAL NEGATIVES** on real C312 5m data (~78,200+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C349 `20261117T130414Z` frozen (1296 configs, RETRACTED, dominant `perm_ent_dev` 0.2513, 0 Holm+BH). No edge proven through C349.
- **NO BOTTLENOCKS** (re-verified 2026-11-17T13:09:21Z): C312 5m on disk (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars, 2023-01..2025-12, field `perp_close` present — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT); C349 build/cache on disk (~38.5 MB < 100 MB, integrity-verified), preflight `ready:true` (exit 0), full sweep complete (5 SHA256 artifacts `reports/campaign349_*_20261117T125619Z.json` + `.full.json`), tests 26/26 green; runtime deps importable (numpy 2.5.5 / pandas 3.1.1 / scipy 1.18.1 / pytest 9.2.0, py 3.12.3) — run `python scripts/bootstrap_dev_env.py` (idempotent) if missing. C287 external blocked/decoupled (451/403, no creds) — never retry.
- **Do NOT** re-read/plan/re-declare closure, re-run frozen C281B–C349/C287, or weaken any gate. Do NOT downscope the 1296-config grid.

**EXECUTE C350 NOW — full pipeline, no pauses (this is the only permitted work):**

1. **Design (PRE-REGISTERED, NON-NEGOTIABLE):** execute the `C350 — PRE-REGISTERED SPEC` section below verbatim.
2. **Build** `scripts/build_c350_dfa_features.py` → `data/cache/campaign350_dfa_5m/` (10 shards `<SYM>.npz` + `meta.json` + `provenance.json` + SHA256 manifest). Real C312 `perp_close` only; cache <100 MB; idempotent (`--force`).
3. **Preflight** `scripts/preflight_c350.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
4. **Sweep** `scripts/run_c350_dfa_xsec_oos.py` — full pre-registered costed-OOS grid (1296 configs), 8 splits 12m train/3m test roll 3m over 2023-01..2025-12. Emit 5 SHA256 artifacts: `reports/campaign350_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>Z.json` + gitignored `.full.json`.
5. **Tests** `tests/test_preflight_c350.py` + `tests/test_c350_dfa_xsec_oos.py` — ≥21 green.
6. **Record** the truthful result (formal negative or edge) in this `AGENTS.md` + `research_state/state.yaml`, update the frozen list + SHAs, and set the next genuinely-new price-only family (C351, queued below) as active.

**Exact run sequence (verbatim, no pauses):** `python scripts/preflight_c350.py` → `python scripts/run_c350_dfa_xsec_oos.py` (full 1296-config costed-OOS grid, 8 splits 12m train/3m test roll 3m over 2023-01..2025-12 → emits 5 SHA256 artifacts + gitignored `.full.json`) → `python -m pytest tests/test_preflight_c350.py tests/test_c350_dfa_xsec_oos.py -q` (≥21 green) → capture the 5 SHA256 artifacts → record the truthful result (formal negative or edge) in this `AGENTS.md` + `research_state/state.yaml`, add C350 to the frozen table with its 5 SHAs, set C351 as active. Only after all five artifacts + green tests exist may you write the result into `AGENTS.md` and `research_state/state.yaml`.

**NO-LIGHT-WORK RULE (non-negotiable):** The ONLY acceptable completion of this session is the on-disk emission of all 5 SHA256 `reports/campaign350_*_<TS>Z.json` artifacts (plus the gitignored `.full.json`) AND ≥21 green tests. A prose summary, a plan, a partial build, a "next steps" note, or another re-read of this handoff WITHOUT those artifacts is a HARD VIOLATION and is NOT economic progress. The full 1296-config costed-OOS sweep IS the deliverable; if it is slow, it is PROGRESS — never abort it, never downscope it, never replace it with a toy subset.

---

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C349 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED:** execute every pre-registered genuinely-new price-only family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C349 DONE/frozen; C350 (cross-sectional intraday DFA scaling-exponent α × seasonal-dislocation mean-reversion) ACTIVE — full pre-registration below; remaining work = build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → record → freeze → set next genuinely-new price-only family active.**

**Bottlenecks: NONE** (re-verified 2026-11-17T13:09:21Z). C312 5m input data sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT — × 315,648 bars, 2023-01..2025-12; field `perp_close`). C349 build/cache on disk (~38.5 MB < 100 MB, integrity-verified), preflight `ready:true` (exit 0), full sweep complete (5 SHA256 artifacts `reports/campaign349_*_20261117T125619Z.json` + `.full.json`), tests 26/26 green. C349 verdict: RETRACTED (formal negative), `edge_proven:false`, binding `multiple_testing`, dominant attribution `perm_ent_dev` 0.2513 (< 0.5 → `attribution_ok:false`), stability false. C337–C348 caches/artifacts/tests on disk. C287 externally blocked/decoupled (451/403, no creds) — never retry as economic work. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests. The heavy C350 sweep IS the economic progress — do not abort.

**Closure audit (C281B–C318 scope only, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C349 extend the record. Do NOT regenerate/run stale closure generators.

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

C348 extra SHAs: tradable_edge_registry `fd3c9aadfc6484b955e7a4164b687a396262662bacfc57871d30d3eea9056b7b`, summary `fa3ac0ce24a80af66cee791fd83692bf6bc2abac5219f10f8b1239d0a2f01ab2`, binding_constraint `85c07aa1f1dfe03dd075c3a401222fa13b2d0f1e0e096873d6b5b05e6a89f306`.
C349 extra SHAs: tradable_edge_registry `60ab151230b9211c2da943e3d990725422b7426a1d903d0ae4ca5bfa471b23a8`, summary `5e64f0197e05ea7a58fe86a0d637532ce1bef59c8c07bbdab975e6601fad2607`, binding_constraint `8f328590e3786454de51d3b13e06b5438ee2deace8f3bf9054d6345a62e7498c`.

---

## C349 RESULT (frozen 20261117T130414Z) — FORMAL NEGATIVE (RETRACTED)

C349 ordinal-pattern / permutation-entropy (Bandt–Pompe) × seasonal-dislocation mean-reversion on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T125619Z`), tests 26/26 green.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `perm_ent_dev` 0.2513 (< 0.5)
- `stability:false` — reference config `perm_ent_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker: sign consistency 0.00
- Truthful result recorded: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312.

---

## C350 — PRE-REGISTERED SPEC (ACTIVE, EXECUTE VERBATIM)

C350 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C349.

**Distinctness proof (pre-registered):**
- C350 measures the **detrended fluctuation analysis (DFA) scaling exponent α** of the return series — OLS slope of log fluctuation `F(n)` vs log scale `n` over scales `n ∈ {4, 8, 16, 32, 64, 128}` within an intrinsic window `W = 256` bars. α ≈ 0.5 uncorrelated/random-walk-like; α > 0.5 persistent; α < 0.5 anti-persistent.
- **C346** measured R/S = single-window range of the cumulative centered sum (one effective scale) — C350 is multi-scale *detrended* fluctuation (slope across 6 scales).
- **C349** measured ordinal-pattern entropy (no integration/detrending, no scale slope).
- **C326** measured lag-1 signed-return AUTOCORRELATION (single pairwise product) — C350 is whole-window multi-scale long-range correlation.
- **C343** measured autocorrelation of `|r|` (vol clustering) — C350 is fluctuation scaling of the integrated demeaned return profile.
- **C344** measured SIGN-CHANGE RATE — C350 is an RMS-fluctuation slope, not a chop count.
- **C347** measured drawdown duration / time-under-water — C350 is scaling-exponent complexity, not path duration.
- **C345** measured close location within trailing envelope — C350 is DFA α.
- **C317** measured realized-vol LEVELS — C350 is scale-invariant correlation scaling.
- **C342/C340/C341** need volume/notional/price-impact; C350 is price-only and volume-free.
- **C315/C320** trade raw seasonal RETURN mean-reversion — C350 fades seasonal dislocation in *DFA α*, conditioned on last-move direction.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign350_dfa_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network, no fabrication, no resampling, no imputation). Fields per shard (identical layout to C349):
```
index_ms      int64    common 5m grid (intersection across all 10 perps, ~315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB total (per-symbol float32 npz shard layout; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Scales `n ∈ {4, 8, 16, 32, 64, 128}`. Intrinsic window `W = 256` bars (fixed, decoupled from seasonal lookback L for tractability).
- For each bar t, take trailing `W` returns `r[t-W+1 .. t]` (NaN if `t < W` or any NaN in the window).
- DFA on the window: (1) demean the window; (2) form the profile `y = cumsum(demeaned)`; (3) split `y` into non-overlapping boxes of scale n (front and back segments to use all points); (4) detrend each box by OLS linear fit; (5) `F(n) = sqrt(mean of squared residuals over all boxes and both segments)`; (6) `dfa[t] = α[t]` = OLS slope of `log F(n)` vs `log n` over the 6 scales. NaN if `t < W` or any NaN in window or zero valid scales.
- `dfa_norm[t] = dfa[t] - 0.5` — deviation from the uncorrelated α = 0.5 benchmark.
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std of `v[t]` at the same `(weekday × tod)` bucket (288 bars/day × 7 weekdays = 2016 buckets) from history strictly BEFORE bar t (causal `shift(1)`), NaN-aware `min_periods=3` excluding NaN obs. Score `s[t] = -(v[t] - seasonal_mean) / seasonal_std` where `v[t] ∈ {dfa[t], dfa_norm[t]}` (symmetric z-fade).

Cross-sectional rank across the 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker = fee+slip; maker_blend = 0.5*fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute DFA α for all bars per asset exactly; per-window DFA must be vectorized (no Python loop over 315,648 bars × 10 assets) and must pass brute-force equality tests against a reference per-window DFA implementation (manual loop over windows × scales with `np.polyfit` detrending).

### Pre-registered grid — 1296 configs
- SIGNALS = `dfa_dev`, `dfa_norm_dev`, `dfa_placebo`, `dfa_norm_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS (seasonal-baseline history, bars) = `(60, 120, 240, 480, 960, 1920)`.
- REBALANCES (bars) = `(1, 4, 12)`.
- FEES = `(0.0004, 0.0007, 0.0010)`.
- SLIPS = `(0.0, 0.0001, 0.0002)`.
- COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`).
- Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12.
- Placebo seed: `20261127` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN).
- selection frac = 1/3, ALPHA = 0.05.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `dfa_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c350_dfa_features.py` → `data/cache/campaign350_dfa_5m/` (10 shards `<SYM>.npz` + `meta.json` + `provenance.json` + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c350.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c350_dfa_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign350_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign350_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign350_summary_<TS>Z.json`
   - `reports/campaign350_verdict_<TS>Z.json`
   - `reports/campaign350_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c350.py` + `tests/test_c350_dfa_xsec_oos.py` — ≥21 green.
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C350 section) + `research_state/state.yaml`; add C350 to the frozen table with its 5 SHAs; set C351 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

---

## C351 QUEUED (NOT ACTIVE — do NOT start until C350 recorded/frozen)

C351 = cross-sectional fractional integration order `d` (Geweke–Porter–Hudak / local Whittle log-periodogram regression on `r`) × seasonal-dislocation mean-reversion, price-only, real C312 `perp_close` only; compact pre-registration to be written by the C350 session into this AGENTS.md before C351 is set active. C350 must finish first.

---

## Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.
