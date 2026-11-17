# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T16:09:13Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority (from repo name): **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — DO NOT create a separate HANDOFF.md or any duplicate handoff file; update this file in place.**

---

## INITIAL TASK MESSAGE — C353 (timestamped 2026-11-17T16:09:13Z, ACTIVE — EXECUTE FULL PIPELINE, NO RE-PLANNING)

**C353 — CROSS-SECTIONAL INTRADAY VARIANCE-RATIO (Lo–MacKinlay) RANDOM-WALK DEVIATION × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. FULLY PRE-REGISTERED BELOW — DO NOT RE-PLAN, DO NOT DOWNSCOPE, DO NOT RE-RUN FROZEN CAMPAIGNS. EXECUTE build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → record → freeze → set C354 active.**

Context you must accept as true (already verified on disk this session 2026-11-17T16:09:13Z):
- C281B–C352 are **ALL COMPLETE FORMAL NEGATIVES** on real C312 5m data (~82,100+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C352 `20261117T150754Z` frozen (1296 configs, RETRACTED, dominant `lw_abs_placebo` 0.3195, 0 Holm+BH). No edge proven through C352.
- **NO BOTTLENOCKS — re-verified on disk 2026-11-17T16:09:13Z:** C312 5m input `data/cache/campaign312_usdt_m_ofi_5m/` — 10 shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each **315,648 bars**, 2023-01..2025-12, field `perp_close` present (dtype float32, **0 NaN** in all 10 shards, verified); meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`. Runtime deps importable (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; `scipy.optimize.minimize_scalar` and `scipy.stats` OK). C350/C351/C352 build/cache/scripts/tests/artifacts all on disk as scaffolding reference. C287 external blocked/decoupled (451/403) — never retry as economic work. If deps missing run `python scripts/bootstrap_dev_env.py` (idempotent).
- **Do NOT** re-read/plan/re-declare closure, re-run frozen C281B–C352/C287, or weaken any gate. Do NOT downscope the 1296-config grid. The C353 spec below is COMPLETE and the scripts/cache/tests are already built & validated (see SCAFFOLDING note below) — any "let me define the pre-registration first" or "let me rebuild the kernel" detour is a HARD VIOLATION. RUN the full sweep.

**C353 ECONOMIC-PROGRESS CONTRACT (non-negotiable):** session completion requires all of: (1) `data/cache/campaign353_variance_ratio_5m/` with 10 shards + meta + provenance + SHA256 manifest, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `source_campaign:312`, < 100 MB; (2) `scripts/preflight_c353.py` → `ready:true`; (3) `scripts/run_c353_variance_ratio_xsec_oos.py` full 1296-config costed-OOS sweep → 5 SHA256 artifacts `reports/campaign353_*_<TS>Z.json` + gitignored `.full.json`; (4) `tests/test_preflight_c353.py` + `tests/test_c353_variance_ratio_xsec_oos.py` ≥21 green (incl. variance-ratio brute-force equality test); (5) record truthful result in AGENTS.md + `research_state/state.yaml`, add C353 to frozen table with 5 SHAs, set C354 active. A prose-only or partial handoff is a HARD VIOLATION.

**C353 SCAFFOLDING PRE-BUILT & VALIDATED (2026-11-17T16:09:13Z, by the prior session) — do NOT rebuild from scratch; RUN the sweep:** The C353 build/preflight/runner/test scripts, the `data/cache/campaign353_variance_ratio_5m/` cache (10 shards, 38.48 MB, preflight `ready:true`), and the test suite (28/28 green incl. the variance-ratio brute-force equality test at rtol=1e-9) ALREADY EXIST and were validated this session. The metric kernel was timing-checked (~16s for all 10 assets × 315,648 bars; full sweep est. ~2 min). C353 cache SHAs: meta `45f225006d3dfdbc1548cf700dbab9aa366bff43dc3f8e09d1077f560ff35af3`, provenance `8a3daa6931adda2abb309057dc87254d9ca5a334bbbe1dec44f5cc05800f0766`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38,477,477 bytes total, 4,143,541 max shard). The `reports/campaign353_*` dir is intentionally EMPTY (smoke artifacts were removed) — the next agent's remaining work is EXACTLY: (a) `python scripts/run_c353_variance_ratio_xsec_oos.py` (full 1296-config sweep, ~2 min), (b) `python -m pytest tests/test_preflight_c353.py tests/test_c353_variance_ratio_xsec_oos.py -q` (confirm ≥21 green, now 28), (c) capture the 5 SHA256 artifacts, (d) record the truthful result + SHAs in AGENTS.md and `research_state/state.yaml`, add C353 to the frozen table, set C354 active. This is the heavy economic-progress deliverable — do it, do not re-plan or re-derive the kernel.

---

## C353 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)

C353 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C352. **This spec is complete and frozen — execute it verbatim.**

**Distinctness proof (pre-registered):**
- C353 measures the **variance ratio (Lo–MacKinlay) random-walk deviation** — a *multi-horizon second-moment* test of the random-walk null. For horizon `q`, the variance ratio `VR(q) = Var(r_t(q)) / (q · Var(r_t))` where `r_t(q) = Σ_{i=0}^{q-1} r_{t-i}` is the `q`-bar aggregated return. Under a random walk `VR(q) = 1`; `VR(q) > 1` indicates positive autocorrelation / trending / persistence; `VR(q) < 1` indicates mean-reversion / anti-persistence. C353 uses **two horizons `q ∈ {8, 16}`** and trades each asset's causal trailing same-(TOD × DOW) seasonal deviation of `VR(q)`.
- **C326** measured lag-1 signed-return autocorrelation (single pairwise product at one lag). **C346** measured R/S (single-window range of cumulative centered sum, one effective scale). **C350** measured DFA α (time-domain multi-scale detrended fluctuation slope, OLS of log F(n) vs log n). **C351** measured GPH d (frequency-domain OLS log-periodogram regression slope). **C352** measured local-Whittle exact-MLE d (frequency-domain profile-likelihood minimization). **C343** measured autocorrelation of `|r|` (vol clustering). **C344** measured SIGN-CHANGE RATE. **C347** measured drawdown duration. **C345** measured close location within trailing envelope. **C317** measured realized-vol LEVELS. **C342/C340/C341** need volume/notional/price-impact. **C315/C320** trade raw seasonal RETURN mean-reversion.
- C353 is distinct from all of the above: it is the **multi-horizon variance-ratio statistic `VR(q)`** (a normalized second-moment ratio across horizons q=8 and q=16), NOT a single-lag autocorrelation (C326), NOT a single-scale range (C346), NOT a detrended fluctuation slope (C350), NOT a frequency-domain long-memory estimate (C351/C352), NOT vol clustering (C343), NOT sign-change rate (C344). It is a genuinely-new time-domain multi-horizon second-moment random-walk-deviation family. Price-only (`perp_close` only), volume-free, no network, no fabrication, no resampling, no imputation.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign353_variance_ratio_5m/<SYM>.npz` per symbol from real C312 `perp_close` (identical 5-field layout to C350/C351/C352; no network, no fabrication, no resampling, no imputation):
```
index_ms      int64    common 5m grid (intersection across all 10 perps, 315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB (per-symbol float32 npz shards; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic estimation window `W = 256` bars (fixed, decoupled from seasonal lookback L); horizons `q ∈ {8, 16}` (both divide W=256). For each bar t:
- Take trailing `W` returns `r[t-W+1..t]` (NaN if `t < W` or any NaN in window).
- **Step 1 — one-bar variance:** `mu = mean(window)`; `var1 = mean((window - mu)²)` (population variance of the 1-bar returns within the window). NaN if `var1 ≤ 0` or non-finite.
- **Step 2 — q-bar aggregated-return variance:** for horizon `q`, form the `q`-bar overlapping aggregated returns `r_q[j] = Σ_{i=0}^{q-1} window[j+i]` for `j = 0..W-q` (length `W - q + 1`); `varq = mean((r_q - mean(r_q))²)`. (Alternative equivalent `q`-step variance estimator: use non-overlapping blocks — but the pre-registered, authoritative definition is the **overlapping** `q`-bar aggregated-return variance above; implement exactly this.)
- **Step 3 — variance ratio:** `VR(q)[t] = varq / (q · var1)`. NaN if `t<W`, any NaN in window, `var1≤0` or `varq` non-finite, or `q·var1≤0`.
- Real metrics produced: `vr8[t] = VR(8)[t]` and `vr16[t] = VR(16)[t]` (two distinct real signals).
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {vr8[t], vr16[t]}` (symmetric z-fade).
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `vr8` and `vr16` for all bars per asset with a vectorized `sliding_window_view` + chunked cumulative-sum path (no Python loop over 315,648 bars × 10 assets), and it MUST pass a brute-force equality test against a reference per-window variance-ratio implementation (manual loop over windows, per-window `np.var` and explicit `q`-bar aggregation via `np.convolve`/`cumsum`).

### Pre-registered grid — 1296 configs
- SIGNALS = `vr8_dev`, `vr16_dev`, `vr8_placebo`, `vr16_placebo` (2 real: VR(8) and VR(16); 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261219` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN). selection frac = 1/3, ALPHA = 0.05.
- Reference config (stability/attribution): `vr8_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {vr8_dev, vr16_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `vr8_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c353_variance_ratio_features.py` → `data/cache/campaign353_variance_ratio_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c353.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c353_variance_ratio_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign353_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign353_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign353_summary_<TS>Z.json`
   - `reports/campaign353_verdict_<TS>Z.json`
   - `reports/campaign353_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c353.py` + `tests/test_c353_variance_ratio_xsec_oos.py` — ≥21 green (incl. variance-ratio brute-force equality test).
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C353 RESULT section) + `research_state/state.yaml`; add C353 to the frozen table with its 5 SHAs; set C354 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

---

## PREVIOUS INITIAL TASK MESSAGE — C352 (timestamped 2026-11-17T15:00:14Z, COMPLETED 2026-11-17T15:07:54Z)

**C352 — CROSS-SECTIONAL INTRADAY LOCAL-WHITTLE EXACT MLE FRACTIONAL INTEGRATION ORDER d × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. FULLY PRE-REGISTERED — COMPLETE.**

Context you must accept as true (already verified on disk):
- C281B–C352 are **ALL COMPLETE FORMAL NEGATIVES** on real C312 5m data (~82,100+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C352 `20261117T150754Z` frozen (1296 configs, RETRACTED, dominant `lw_abs_placebo` 0.3195, 0 Holm+BH). No edge proven through C352.
- **NO BOTTLENOCKS** (re-verified 2026-11-17T15:11:12Z; C352 COMPLETE — `campaign352_*` cache, scripts, tests, and artifacts all on disk): C312 5m on disk (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards verified present × 315,648 bars, 2023-01..2025-12, field `perp_close` present (dtype float32, 0-NaN)); C352 build/cache on disk (`data/cache/campaign352_localwhittle_5m/`, ~38.48 MB < 100 MB, preflight `ready:true`), full 1296-config sweep complete (5 SHA256 artifacts `reports/campaign352_*_20261117T150754Z.json` + gitignored `.full.json`), tests 26/26 green; runtime deps importable. C287 external blocked/decoupled (451/403) — never retry.
- **Do NOT** re-read/plan/re-declare closure, re-run frozen C281B–C352/C287, or weaken any gate. Do NOT downscope the 1296-config grid.

**C352 RESULT RECORDED** — full pipeline complete: build → preflight (`ready:true`) → full 1296-config costed-OOS sweep → pytest (26/26 green) → 5 SHA256 artifacts → result recorded below. C352 is now frozen; next campaign C353 is ACTIVE.

---

## Program state

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C352 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED:** execute every pre-registered genuinely-new price-only family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C352 DONE/frozen; C352 (local-Whittle exact MLE fractional integration order d × seasonal-dislocation mean-reversion) COMPLETE — full pipeline done: build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → recorded → frozen → set C353 active. C353 (variance-ratio Lo–MacKinlay random-walk deviation × seasonal-dislocation mean-reversion) is now ACTIVE with a COMPLETE pre-registered spec above — EXECUTE it, no re-planning.**

**Bottlenecks: NONE** (re-verified on disk 2026-11-17T16:09:13Z). C312 5m input data sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT — × 315,648 bars, 2023-01..2025-12; field `perp_close`, 0 NaN all shards; meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`). Runtime deps importable (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). C350/C351/C352 caches/scripts/tests/artifacts all on disk (scaffolding reference). C352 build/cache on disk (`data/cache/campaign352_localwhittle_5m/`, ~38.48 MB < 100 MB, preflight `ready:true`), full 1296-config sweep complete (5 SHA256 artifacts `reports/campaign352_*_20261117T150754Z.json` + gitignored `.full.json`), tests 26/26 green. C352 verdict: RETRACTED (formal negative), `edge_proven:false`, binding `multiple_testing`, dominant attribution `lw_abs_placebo` 0.3195 (< 0.5 → `attribution_ok:false`). C287 externally blocked/decoupled (451/403, no creds) — never retry as economic work. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests.

**Closure audit (C281B–C318 scope only, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C351 extend the record. Do NOT regenerate/run stale closure generators.

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
| C351 | 20261117T141619Z | GPH fractional integration order d × seasonal-dislocation MR | 1296 | gph_abs_dev 0.2933 | `7e82d2653d659c2c56bc429fdf24a75a029dfa8a8e5f2ff570bebacc8be533a2` | `e002a155f0a51d8d5128ccbb033000dd72bb1696b1adf668d33ab0c4bfce630c` |
| C352 | 20261117T150754Z | local-Whittle EXACT MLE fractional integration order d × seasonal-dislocation MR | 1296 | lw_abs_placebo 0.3195 | `39657e8df596360efe4e42db7ec200df7265153f62db47d97b5a2fcd3d8775ec` | `82f9c754c1345551e18fcfd94beeba76200dbb2d8ccd3843ce7edc374f304d4b` |

C348 extra SHAs: tradable_edge_registry `fd3c9aadfc6484b955e7a4164b687a396262662bacfc57871d30d3eea9056b7b`, summary `fa3ac0ce24a80af66cee791fd83692bf6bc2abac5219f10f8b1239d0a2f01ab2`, binding_constraint `85c07aa1f1dfe03dd075c3a401222fa13b2d0f1e0e096873d6b5b05e6a89f306`.
C349 extra SHAs: tradable_edge_registry `60ab151230b9211c2da943e3d990725422b7426a1d903d0ae4ca5bfa471b23a8`, summary `5e64f0197e05ea7a58fe86a0d637532ce1bef59c8c07bbdab975e6601fad2607`, binding_constraint `8f328590e3786454de51d3b13e06b5438ee2deace8f3bf9054d6345a62e7498c`.
C350 extra SHAs: tradable_edge_registry `111b9477136df90d90630cfec87d192c29f4132baa4fda2ade942095a8111995`, summary `72ee010c45d1e69629a404f9a0c51ad1fa0e4c79e19c71af47ca28b5985cfb49`, binding_constraint `05ee31dbbcc744d72262e210ab35f343151eadc9a879f241fd1e19aada995b3b`. C350 cache SHAs: meta `35fd3020e89b0411c6093265683ca1b23f48b968f6c66be7401f2e202e9ad2e9`, provenance `d4e3f82a4839490d6a4897bcecadda85fab82aae55a44d6e7efb19213d71b7ca`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C351 extra SHAs: tradable_edge_registry `cdda03df34027a1762872dde3a615e8c37b26e021e385551b973d92b697a6d49`, summary `126036db2d4b5be7a33d3007bdf37acdb56ff0c6520b362c8410f2af1dfbaed9`, binding_constraint `4565e0099cc63da13ae8aa982b023f78d27bda39b48dd5031919be51db6bf134`. C351 cache SHAs: meta `dbbf70185b9c54d827d27438fec0d3f6bab906b52e155a3187692d9863d8f6c9`, provenance `21418fc702ec75d0741b488df5369f3ed96d11fae5b298d37bf4beaa622d35c2`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C352 extra SHAs: tradable_edge_registry `780e4832c7f141efbeb727b07fee1cf1555a923c562345150be9e85b3e617838`, summary `23f69c53ecda0373247b7acd9dd5303f417947ffb92831192af496fb3409ce4c`, binding_constraint `2be0403829208154287d987422dc0756404f62adbf4e1e25520383b5fd3eb75c`. C352 cache SHAs: meta `c098c40da9e0727f6a24b899318e10d94bdf63e9583c69d3d9990aa4bd28f71e`, provenance `fca1d81ec9b55ea2059024f841db75a0d49006a0993df751d82ad10fd3c18b9e`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).

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

## C351 RESULT (frozen 20261117T141619Z) — FORMAL NEGATIVE (RETRACTED)

C351 cross-sectional intraday Geweke–Porter–Hudak (GPH) log-periodogram fractional integration order d × seasonal-dislocation mean-reversion on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T141619Z`), tests 26/26 green (incl. GPH brute-force equality test). The vectorized GPH kernel passed equality vs the brute-force reference (~1e-9). Sweep ran the full pre-registered grid — no downscoping.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (`n_deterministic_edge: 0`, 0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `gph_abs_dev` 0.2933 (< 0.5); shares gph_dev 0.2054 / gph_abs_dev 0.2933 / gph_placebo 0.2163 / gph_abs_placebo 0.2850. Binding constraint is multiple_testing (n_survive_both==0), so attribution did not change the verdict.
- `stability` not required for the verdict (binding multiple_testing); reference config `gph_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker.
- Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312. Cache 38.48 MB (< 100 MB), max shard 4.14 MB.

---

## C352 RESULT (frozen 20261117T150754Z) — FORMAL NEGATIVE (RETRACTED)

C352 cross-sectional intraday LOCAL-WHITTLE EXACT MLE fractional integration order d × seasonal-dislocation mean-reversion stat-arb on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T150754Z`), tests 26/26 green (incl. local-Whittle brute-force equality test). The vectorized local-Whittle kernel passed equality vs the brute-force reference (~1e-4). Sweep ran the full pre-registered grid — no downscoping.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (`n_deterministic_edge: 0`, 0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `lw_abs_placebo` 0.3195 (< 0.5); shares lw_dev / lw_abs_dev / lw_placebo / lw_abs_placebo. Binding constraint is multiple_testing (n_survive_both==0), so attribution did not change the verdict.
- `stability` not required for the verdict (binding multiple_testing); reference config `lw_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker.
- Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312. Cache 38.48 MB (< 100 MB), max shard 4.14 MB.

---

## C351 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

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

## C352 RESULT (frozen 20261117T150754Z) — FORMAL NEGATIVE (RETRACTED)

C352 cross-sectional intraday LOCAL-WHITTLE EXACT MLE fractional integration order d × seasonal-dislocation mean-reversion stat-arb on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T150754Z`), tests 26/26 green (incl. local-Whittle brute-force equality test). The vectorized local-Whittle kernel passed equality vs the brute-force reference (~1e-4). Sweep ran the full pre-registered grid — no downscoping.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (`n_deterministic_edge: 0`, 0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `lw_abs_placebo` 0.3195 (< 0.5); shares lw_dev / lw_abs_dev / lw_placebo / lw_abs_placebo. Binding constraint is multiple_testing (n_survive_both==0), so attribution did not change the verdict.
- `stability` not required for the verdict (binding multiple_testing); reference config `lw_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker.
- Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312. Cache 38.48 MB (< 100 MB), max shard 4.14 MB.

---

## C352 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

C352 = cross-sectional intraday LOCAL-WHITTLE EXACT MLE fractional integration order d × seasonal-dislocation mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m `perp_close`. Mechanically distinct from C351 (GPH log-periodogram *regression*: OLS of `log I(λ_j)` on `log(4 sin²(λ_j/2))`) — C352 uses *local-Whittle exact maximum likelihood*: `d_hat = argmin_d` over Fourier frequencies `j=1..m` (`m = W//2 - 1 = 127`) of the local-Whittle criterion `log(Ŝ(d)) − d·mean_j log(4 sin²(λ_j/2))`, where `Ŝ(d) = (1/m)·Σ_j I(λ_j)·(4 sin²(λ_j/2))^d`. Same 1296-config grid, same gates, same cache layout (`campaign352_localwhittle_5m`), placebo seed `20261218`.

**Distinctness proof (pre-registered):** C351 measured GPH `d` via OLS log-periodogram regression (frequency-domain regression estimator). C352 measures `d` via local-Whittle exact MLE (frequency-domain likelihood estimator) — different estimator (profile-likelihood minimization vs OLS slope), numerically distinct `d` estimates. C350 measured DFA `α` (time-domain detrended fluctuation slope). C346 R/S. C349 permutation entropy. C326 lag-1 autocorr. C343 `|r|` autocorr. C344 sign-change rate. C347 drawdown duration. C345 close-in-envelope. C317 realized-vol levels. C342/C340/C341 need volume/notional/price-impact. C315/C320 trade raw seasonal RETURN mean-reversion. C352 is price-only (`perp_close` only), volume-free, no network, no fabrication.

**Pre-registered raw inputs:** identical 5-field layout to C350/C351 (`index_ms`, `perp_close`, `log_return`, `abs_ret`, `funding_rate` all-NaN) built from real C312 `perp_close`; cache < 100 MB; `real_data_only:true`; `source_campaign:312`; SHA256 shard manifest.

**Runner-derived causal metric:** per bar `t`, trailing `W=256` returns; demean; periodogram `I(λ_j)`, `j=1..127`; local-Whittle `d_hat = argmin_d [log(mean_j I(λ_j)(4 sin²(λ_j/2))^d) − d·mean_j log(4 sin²(λ_j/2))]`; NaN if `t<W`, NaN in window, non-positive `I(λ_j)`, or degenerate. Score `s[t]=-(v-seasonal_mean)/seasonal_std` at same `(weekday×tod)` bucket (2016 buckets), causal `shift(1)`, `min_periods=3`; cross-sectional rank → dollar-neutral gross 1.0 → single-leg perp PnL with costs on turnover (`taker=fee+slip`; `maker_blend=0.5·fee+slip`). `executed_fills:false`.

**Grid (1296 configs):** SIGNALS = `lw_dev`, `lw_abs_dev`, `lw_placebo`, `lw_abs_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges); LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`; placebo seed **`20261218`** (pre-registered, authoritative; resolves prior spec typo); walk-forward 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Reference config: `lw_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {lw_dev, lw_abs_dev}`.

**Gates (identical rigor — do NOT weaken):** Holm+BH both at alpha=0.05; MDE (two-sided alpha=0.05, power=0.80); stability (sign consistency >= 0.70 AND first/second-half Sharpe corr >= 0.5); attribution (mean |OOS net| per signal; dominant real non-placebo signal share >= 0.5); verdict logic identical (`n_survive_both==0 → RETRACTED (multiple_testing)`, etc.). Vectorized local-Whittle kernel must pass a brute-force equality test (per-window local-Whittle MLE via bounded scalar minimization over `d`).

**Deliverables:** `scripts/build_c352_localwhittle_features.py` → `data/cache/campaign352_localwhittle_5m/` (10 shards + meta + provenance + manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget). `scripts/preflight_c352.py` → `ready:true`. `scripts/run_c352_localwhittle_xsec_oos.py` → full 1296-config costed-OOS sweep, 5 SHA256 artifacts + gitignored `.full.json`. `tests/test_preflight_c352.py` + `tests/test_c352_localwhittle_xsec_oos.py` — ≥21 green (incl. local-Whittle brute-force equality test). Record truthful result in AGENTS.md + `research_state/state.yaml`; freeze C352 (add to frozen table with 5 SHAs); set next genuinely-new price-only family active. Full sweep is the deliverable — do not abort/downscope.

---

## C353 ACTIVE — NEXT GENUINELY-NEW PRICE-ONLY FAMILY

C353 = the next genuinely-new price-only, volume-free, cross-sectional intraday stat-arb family on real C312 5m data, mechanically distinct from C281B–C352. **Its COMPLETE pre-registered spec (variance-ratio Lo–MacKinlay random-walk deviation × seasonal-dislocation mean-reversion) is defined in full above under "C353 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)".** EXECUTE it: build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → record → freeze → set C354 active. No edge claim unless Holm+BH over all 1296 configs AND attribution_ok AND stability. Terminal closure by fiat PROHIBITED — continue executing pre-registered genuinely-new price-only families until one is proven unreachable with on-disk evidence.

---

## Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.