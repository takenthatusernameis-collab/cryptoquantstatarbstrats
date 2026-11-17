# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T21:57:26Z. Repo: `cryptoquantstatarbstrats` — crypto quantitative **statistical arbitrage**. Priority (from repo name): **statistical-arb edge discovery on real on-disk C312 5m data**, fail-closed, costed out-of-sample, real-data-only.

Economic progress = a real-data costed out-of-sample PnL run, a passing test, or a durable-artifact update. A session that only re-reads this handoff, re-declares closure, re-runs a frozen campaign, or re-plans is NOT economic progress and is a hard violation. **This AGENTS.md is the single durable handoff — DO NOT create a separate HANDOFF.md or any duplicate handoff file; update this file in place.**

---

## INITIAL TASK MESSAGE — C356 (timestamped 2026-11-17T21:57:26Z, ACTIVE — NOT STARTED)

**EXECUTE C356 NOW (heavy work required; no re-planning, no spec changes, no downscoping): CROSS-SECTIONAL INTRADAY MULTISCALE ENTROPY (MSE) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data.**

**State verified 2026-11-17T21:57:26Z (no bottlenecks):**
- C312 5m source present: `data/cache/campaign312_usdt_m_ofi_5m/` (10 symbols × 315,648 bars, `perp_close` 0 NaN, meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`).
- Runtime deps importable: numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0 (`scipy.optimize.minimize_scalar`, `scipy.stats` OK). If missing: `python scripts/bootstrap_dev_env.py` (idempotent).
- C281B–C355 ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~92k+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`). C355 frozen `20261117T204322Z` (1296, RETRACTED, dominant `sampen_m3_placebo` 0.3069). No edge proven through C355.
- **C356 NOT STARTED:** no `scripts/build|preflight|run_c356*`, no `tests/test_*c356*`, no `data/cache/campaign356_multiscale_entropy_5m/`, no `reports/campaign356_*`.
- C287 externally blocked/decoupled (451/403) — never retry as economic work. Do NOT re-run frozen C281B–C355/C287. Do NOT weaken gates.

**C356 pre-registered spec is COMPLETE and FROZEN — see "C356 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)" below. Execute it verbatim.**

**Mandatory run sequence (economic progress = all of these):**
1. `scripts/build_c356_multiscale_entropy_features.py` → `data/cache/campaign356_multiscale_entropy_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; <100 MB).
2. `python scripts/preflight_c356.py` → `ready:true`.
3. `python scripts/run_c356_multiscale_entropy_xsec_oos.py` — **full 1296-config costed-OOS sweep** (no downscoping) → 5 SHA256 artifacts `reports/campaign356_*_<TS>Z.json` + gitignored `.full.json`.
4. `python -m pytest tests/test_preflight_c356.py tests/test_c356_multiscale_entropy_xsec_oos.py -q` — **≥21 green incl. MSE brute-force equality test**.
5. Record truthful result in this `AGENTS.md` (new C356 RESULT) + `research_state/state.yaml`; add C356 to frozen table with 5 SHAs (+ cache SHAs); set C357 active with next genuinely-new price-only family spec placeholder. No edge claim unless Holm+BH over all 1296 AND `attribution_ok` AND `stability`.

Terminal closure by fiat PROHIBITED. A prose-only/partial handoff is a HARD VIOLATION. The heavy sweep IS the deliverable.

---

## C353 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

**C353 — CROSS-SECTIONAL INTRADAY VARIANCE-RATIO (Lo–MacKinlay) RANDOM-WALK DEVIATION × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. FULLY PRE-REGISTERED — EXECUTED VERBATIM: build → preflight (`ready:true`) → full 1296-config costed-OOS sweep → pytest (28/28 green) → 5 SHA256 artifacts → recorded → frozen → set C354 active. Verdict: RETRACTED (formal negative), `edge_proven:false`, binding `multiple_testing`, dominant `vr8_placebo` 0.3065 (< 0.5 → `attribution_ok:false`).**

Context you must accept as true (already verified on disk this session 2026-11-17T16:09:13Z):
- C281B–C352 are **ALL COMPLETE FORMAL NEGATIVES** on real C312 5m data (~82,100+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C352 `20261117T150754Z` frozen (1296 configs, RETRACTED, dominant `lw_abs_placebo` 0.3195, 0 Holm+BH). No edge proven through C352.
- **NO BOTTLENOCKS — re-verified on disk 2026-11-17T16:09:13Z:** C312 5m input `data/cache/campaign312_usdt_m_ofi_5m/` — 10 shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT) each **315,648 bars**, 2023-01..2025-12, field `perp_close` present (dtype float32, **0 NaN** in all 10 shards, verified); meta sha256 `49ee1f32107da1be9b0ddfba11627232a62d218054c9c4968745b910620f147b`. Runtime deps importable (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0; `scipy.optimize.minimize_scalar` and `scipy.stats` OK). C350/C351/C352 build/cache/scripts/tests/artifacts all on disk as scaffolding reference. C287 external blocked/decoupled (451/403) — never retry as economic work. If deps missing run `python scripts/bootstrap_dev_env.py` (idempotent).
- **Do NOT** re-read/plan/re-declare closure, re-run frozen C281B–C352/C287, or weaken any gate. Do NOT downscope the 1296-config grid. The C353 spec below is COMPLETE and the scripts/cache/tests are already built & validated (see SCAFFOLDING note below) — any "let me define the pre-registration first" or "let me rebuild the kernel" detour is a HARD VIOLATION. RUN the full sweep.

**C353 ECONOMIC-PROGRESS CONTRACT (non-negotiable):** session completion requires all of: (1) `data/cache/campaign353_variance_ratio_5m/` with 10 shards + meta + provenance + SHA256 manifest, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `source_campaign:312`, < 100 MB; (2) `scripts/preflight_c353.py` → `ready:true`; (3) `scripts/run_c353_variance_ratio_xsec_oos.py` full 1296-config costed-OOS sweep → 5 SHA256 artifacts `reports/campaign353_*_<TS>Z.json` + gitignored `.full.json`; (4) `tests/test_preflight_c353.py` + `tests/test_c353_variance_ratio_xsec_oos.py` ≥21 green (incl. variance-ratio brute-force equality test); (5) record truthful result in AGENTS.md + `research_state/state.yaml`, add C353 to frozen table with 5 SHAs, set C354 active. A prose-only or partial handoff is a HARD VIOLATION.

**C353 SCAFFOLDING PRE-BUILT & VALIDATED (2026-11-17T16:09:13Z, by the prior session) — do NOT rebuild from scratch; RUN the sweep:** The C353 build/preflight/runner/test scripts, the `data/cache/campaign353_variance_ratio_5m/` cache (10 shards, 38.48 MB, preflight `ready:true`), and the test suite (28/28 green incl. the variance-ratio brute-force equality test at rtol=1e-9) ALREADY EXIST and were validated this session. The metric kernel was timing-checked (~16s for all 10 assets × 315,648 bars; full sweep est. ~2 min). C353 cache SHAs: meta `45f225006d3dfdbc1548cf700dbab9aa366bff43dc3f8e09d1077f560ff35af3`, provenance `8a3daa6931adda2abb309057dc87254d9ca5a334bbbe1dec44f5cc05800f0766`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38,477,477 bytes total, 4,143,541 max shard). The `reports/campaign353_*` dir is intentionally EMPTY (smoke artifacts were removed) — the next agent's remaining work is EXACTLY: (a) `python scripts/run_c353_variance_ratio_xsec_oos.py` (full 1296-config sweep, ~2 min), (b) `python -m pytest tests/test_preflight_c353.py tests/test_c353_variance_ratio_xsec_oos.py -q` (confirm ≥21 green, now 28), (c) capture the 5 SHA256 artifacts, (d) record the truthful result + SHAs in AGENTS.md and `research_state/state.yaml`, add C353 to the frozen table, set C354 active. This is the heavy economic-progress deliverable — do it, do not re-plan or re-derive the kernel.

---

## C353 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

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

**`ACTIVE — NO-EDGE CONFIRMED THROUGH C355 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED:** execute every pre-registered genuinely-new price-only family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C355 DONE/frozen; C355 (Sample Entropy × seasonal-dislocation mean-reversion) COMPLETE — full pipeline done: build → preflight (`ready:true`) → full 1296-config costed-OOS sweep → pytest (25/25 green) → 5 SHA256 artifacts `reports/campaign355_*_20261117T204322Z.json` + `.full.json` → recorded → frozen → set C356 active. C355 verdict: RETRACTED (formal negative), `edge_proven:false`, binding `multiple_testing`, dominant `sampen_m3_placebo` 0.3069 (< 0.5 → `attribution_ok:false`). C356 is now ACTIVE — the next genuinely-new price-only, volume-free stat-arb family on real C312 5m data. Its pre-registered spec must be defined and frozen before execution.**

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
| C353 | 20261117T161918Z | variance-ratio (Lo–MacKinlay) random-walk deviation × seasonal-dislocation MR | 1296 | vr8_placebo 0.3065 | `fa0016cc882d375350f58b0117526abf4664fcf88b0eb4a87520a77c79b0301f` | `edad339416b9924549500a46741341d09410c6519f7c400021f5590cf734ae96` |
| C354 | 20261117T171655Z | Higuchi fractal dimension (HFD) × seasonal-dislocation MR | 1296 | hfd_placebo 0.2595 | `7a4b0a535616d52f757fff5d918da85161416fd148eb189c1f3f063bd5eb59f6` | `3f4138e4ec50a3710555c5f8f929afdf59556a4833f4746ec47424af6c72649a` |
| C355 | 20261117T204322Z | Sample Entropy (SampEn) × seasonal-dislocation MR | 1296 | sampen_m3_placebo 0.3069 | `3febf019a380a23559b4d931ed301386fe77c4b5f979356d359367138b436ba8` | `590143e898ee54faecc834c0070fb3f5fb60dddf9fd8bf6b152eee8a62ae806c` |
| C356 | TBD | Multiscale Entropy (MSE) × seasonal-dislocation MR | 1296 | TBD | TBD | TBD |

C348 extra SHAs: tradable_edge_registry `fd3c9aadfc6484b955e7a4164b687a396262662bacfc57871d30d3eea9056b7b`, summary `fa3ac0ce24a80af66cee791fd83692bf6bc2abac5219f10f8b1239d0a2f01ab2`, binding_constraint `85c07aa1f1dfe03dd075c3a401222fa13b2d0f1e0e096873d6b5b05e6a89f306`.
C349 extra SHAs: tradable_edge_registry `60ab151230b9211c2da943e3d990725422b7426a1d903d0ae4ca5bfa471b23a8`, summary `5e64f0197e05ea7a58fe86a0d637532ce1bef59c8c07bbdab975e6601fad2607`, binding_constraint `8f328590e3786454de51d3b13e06b5438ee2deace8f3bf9054d6345a62e7498c`.
C350 extra SHAs: tradable_edge_registry `111b9477136df90d90630cfec87d192c29f4132baa4fda2ade942095a8111995`, summary `72ee010c45d1e69629a404f9a0c51ad1fa0e4c79e19c71af47ca28b5985cfb49`, binding_constraint `05ee31dbbcc744d72262e210ab35f343151eadc9a879f241fd1e19aada995b3b`. C350 cache SHAs: meta `35fd3020e89b0411c6093265683ca1b23f48b968f6c66be7401f2e202e9ad2e9`, provenance `d4e3f82a4839490d6a4897bcecadda85fab82aae55a44d6e7efb19213d71b7ca`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C351 extra SHAs: tradable_edge_registry `cdda03df34027a1762872dde3a615e8c37b26e021e385551b973d92b697a6d49`, summary `126036db2d4b5be7a33d3007bdf37acdb56ff0c6520b362c8410f2af1dfbaed9`, binding_constraint `4565e0099cc63da13ae8aa982b023f78d27bda39b48dd5031919be51db6bf134`. C351 cache SHAs: meta `dbbf70185b9c54d827d27438fec0d3f6bab906b52e155a3187692d9863d8f6c9`, provenance `21418fc702ec75d0741b488df5369f3ed96d11fae5b298d37bf4beaa622d35c2`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C352 extra SHAs: tradable_edge_registry `780e4832c7f141efbeb727b07fee1cf1555a923c562345150be9e85b3e617838`, summary `23f69c53ecda0373247b7acd9dd5303f417947ffb92831192af496fb3409ce4c`, binding_constraint `2be0403829208154287d987422dc0756404f62adbf4e1e25520383b5fd3eb75c`. C352 cache SHAs: meta `c098c40da9e0727f6a24b899318e10d94bdf63e9583c69d3d9990aa4bd28f71e`, provenance `fca1d81ec9b55ea2059024f841db75a0d49006a0993df751d82ad10fd3c18b9e`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C353 extra SHAs: tradable_edge_registry `c9d919d6396cda5543e876c2b22cef9710ffee8bbd38c2ffd47caba0264ed616`, summary `0480ff13bd7f3ad9f7204e78bbdeccd9cb06e9417387a1e62e737b368bd66fb4`, binding_constraint `e6e8480233daad2f193b5bded09589d1c9325f5eaf5525e5dabc1785e614ba55`. C353 cache SHAs: meta `45f225006d3dfdbc1548cf700dbab9aa366bff43dc3f8e09d1077f560ff35af3`, provenance `8a3daa6931adda2abb309057dc87254d9ca5a334bbbe1dec44f5cc05800f0766`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).
C355 extra SHAs: tradable_edge_registry `b3c6f876c800e3cbdcde059e2bff6d1131141c295ae074a44f52757d71bb936b`, summary `dd25ee4e16693e2a1b587db1d062a12bc76026a07dfe73043b288cb6f2fd35de`, binding_constraint `0d3862c61f8e8cc90493565ddc6fad00b00c85dc684706360879166587bb5d53`. C355 cache SHAs: meta `8e827350211624253558aeda45931bf953b0ef03aad47700e0c3cdae1a328ebe`, provenance `2a777ed4aa3d2aea1f61e3f3a88fd7aabb7792f63874cc155f27f315652ea3f0`, manifest `4d953a7d839991000c3460dec48ddd0c54aaefa28b0e39cf06103c81dfbdfdaa` (38.48 MB total, 4.14 MB max shard).

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

## C353 (COMPLETED FORMAL NEGATIVE — historical next-pointer, see C353 RESULT below)

C353 = the next genuinely-new price-only, volume-free, cross-sectional intraday stat-arb family on real C312 5m data, mechanically distinct from C281B–C352. **Its COMPLETE pre-registered spec (variance-ratio Lo–MacKinlay random-walk deviation × seasonal-dislocation mean-reversion) is defined in full above under "C353 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)".** EXECUTE it: build → preflight → full 1296-config costed-OOS sweep → pytest ≥21 green → 5 SHA256 artifacts → record → freeze → set C354 active. No edge claim unless Holm+BH over all 1296 configs AND attribution_ok AND stability. Terminal closure by fiat PROHIBITED — continue executing pre-registered genuinely-new price-only families until one is proven unreachable with on-disk evidence.

---

## C353 RESULT (frozen 20261117T161918Z) — FORMAL NEGATIVE (RETRACTED)

C353 cross-sectional intraday VARIANCE-RATIO (Lo–MacKinlay) random-walk deviation × seasonal-dislocation mean-reversion stat-arb on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T161918Z`), tests 28/28 green (incl. variance-ratio brute-force equality test). The vectorized variance-ratio kernel passed equality vs the brute-force reference. Sweep ran the full pre-registered grid — no downscoping.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (`n_deterministic_edge: 0`, 0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `vr8_placebo` 0.3065 (< 0.5); shares vr8_dev / vr16_dev / vr8_placebo / vr16_placebo. Binding constraint is multiple_testing (n_survive_both==0), so attribution did not change the verdict.
- `stability` not required for the verdict (binding multiple_testing); reference config `vr8_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker.
- Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312. Cache 38.48 MB (< 100 MB), max shard 4.14 MB.

## C354 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

C354 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C353. **This spec is complete and frozen — execute it verbatim.**

**Distinctness proof (pre-registered):**
- C354 measures the **Higuchi fractal dimension (HFD)** — a time-domain fractal-dimension estimator via curve length at multiple scales. For a series `X` of length `W`, for each scale `k` (1..kmax), compute `L(k) = (1/k)·Σ_{m=1}^{k} Σ_{i=1}^{⌊(W-m)/k⌋} |X[m+i·k] − X[m+(i-1)·k]| · (W−1)/(⌊(W-m)/k⌋·k)`, then `HFD = log(kmax) / (log(kmax) + log(L(kmax)/...))`... authoritative definition: fit `log L(k)` vs `log(1/k)` (OLS slope) over `k = 1..kmax`; `HFD = slope`. Range [1,2]: 1 = smooth/trending, 2 = rough/noisy. Distinct from C350 DFA α (detrended fluctuation slope), C346 R/S (range), C351/C352 frequency-domain long-memory d, C353 variance ratio (second-moment ratio). Higuchi uses first differences of the raw series (no integration/detrending), a genuinely different time-domain fractal estimator.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign354_higuchi_fractal_5m/<SYM>.npz` per symbol from real C312 `perp_close` (identical 5-field layout to C350–C353; no network, no fabrication, no resampling, no imputation):
```
index_ms      int64    common 5m grid (intersection across all 10 perps, 315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB (per-symbol float32 npz shards; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic window `W = 256` bars (fixed, decoupled from seasonal lookback L); `kmax = 16` (scales k=1..16). For each bar t:
- Take trailing `W` returns (or prices? returns) `X = r[t-W+1..t]` (NaN if `t < W` or any NaN in window).
- Compute Higuchi curve length `L(k)` for `k = 1..kmax`: `L(k) = (1/k) · Σ_{m=1}^{k} ( (Σ_{i=1}^{⌊(W-m)/k⌋} |X[m+i·k] − X[m+(i-1)·k]|) · (W−1) / (⌊(W-m)/k⌋·k) )`.
- Fit OLS: `log L(k)` vs `log(1/k)` over k=1..kmax; `hfd[t] = slope`. NaN if `t<W`, any NaN in window, or any `L(k)≤0`/non-finite, or degenerate regression.
- `hfd_norm[t] = hfd[t] − 1.5` (centered; distinct real signal).
- `last_move_dir[t] = sign(r[t])`.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {hfd[t], hfd_norm[t]}` (symmetric z-fade).
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute HFD for all bars per asset with a vectorized `sliding_window_view` path (chunked over k), and it MUST pass a brute-force equality test against a reference per-window Higuchi implementation (manual loop over windows, explicit `L(k)` aggregation).

### Pre-registered grid — 1296 configs
- SIGNALS = `hfd_dev`, `hfd_norm_dev`, `hfd_placebo`, `hfd_norm_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261220` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN). selection frac = 1/3, ALPHA = 0.05.
- Reference config (stability/attribution): `hfd_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {hfd_dev, hfd_norm_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config above).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c354_higuchi_fractal_features.py` → `data/cache/campaign354_higuchi_fractal_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c354.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c354_higuchi_fractal_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign354_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign354_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign354_summary_<TS>Z.json`
   - `reports/campaign354_verdict_<TS>Z.json`
   - `reports/campaign354_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c354.py` + `tests/test_c354_higuchi_fractal_xsec_oos.py` — ≥21 green (incl. Higuchi brute-force equality test).
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C354 section) + `research_state/state.yaml`; add C354 to the frozen table with its 5 SHAs; set C355 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

## C355 RESULT (frozen 20261117T204322Z) — FORMAL NEGATIVE (RETRACTED)

C355 cross-sectional intraday SAMPLE ENTROPY (SampEn) × seasonal-dislocation mean-reversion stat-arb on real C312 5m data: full 1296-config costed-OOS sweep complete on disk (5 SHA256 artifacts + gitignored `.full.json`, ts `20261117T204322Z`), tests 25/25 green (incl. SampEn brute-force equality test). The vectorized SampEn kernel passed equality vs the brute-force reference. Sweep ran the full pre-registered grid — no downscoping.
- `verdict: RETRACTED`, `edge_proven:false`
- `n_survive_both: 0` (`n_deterministic_edge: 0`, 0 Holm+BH survivors over 1296 configs) → binding constraint `multiple_testing`
- `attribution_ok:false` — dominant attribution `sampen_m3_placebo` 0.3069 (< 0.5); shares sampen_m2_dev / sampen_m3_dev / sampen_m2_placebo / sampen_m3_placebo. Binding constraint is multiple_testing (n_survive_both==0), so attribution did not change the verdict.
- `stability` not required for the verdict (binding multiple_testing); reference config `sampen_m2_dev` L=240 H=4 fee=0.0007 slip=0.0001 taker.
- Truthful result: formal negative, no edge claim. `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source_campaign=312. Cache 38.48 MB (< 100 MB), max shard 4.14 MB.

---

## C355 — PRE-REGISTERED SPEC (FROZEN / COMPLETED — kept for reference, do NOT re-run)

C355 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C354. **This spec is complete and frozen — execute it verbatim.**

**Distinctness proof (pre-registered):**
- C355 measures **Sample Entropy (SampEn)** — a *nonlinear regularity / complexity* statistic (Richman & Moorman 2000). For an embedded series with embedding dimension `m` and tolerance `r`, SampEn is the negative natural log of the conditional probability that two length-`m` template vectors within Chebyshev distance `r` also remain within `r` after incrementing length to `m+1`: `SampEn = -ln(A/B)` where `B` = number of pairs `(i,j)`, `i≠j`, with `max_{d<m}|z[i+d]-z[j+d]| < r` and `A` = number of pairs with `max_{d<m+1}|z[i+d]-z[j+d]| < r`, over a length-`W` window of the causal return series. Low SampEn = regular/predictable structure; high SampEn = irregular/noisy. Computed on the *z-scored* window with a fixed absolute tolerance.
- **C349** measured permutation entropy (Bandt–Pompe ordinal-pattern Shannon entropy — no template matching, no tolerance). **C354** measured Higuchi fractal dimension (curve-length scaling over k). **C350** measured DFA α (detrended fluctuation slope). **C351/C352** measured frequency-domain fractional-integration d (GPH OLS / local-Whittle MLE). **C353** measured the Lo–MacKinlay variance ratio (second-moment ratio across horizons). **C346** measured R/S. **C343** measured autocorrelation of `|r|`. **C344** measured sign-change rate. **C326** measured lag-1 signed-return autocorrelation. **C345** measured close location in a trailing envelope. **C317** measured realized-vol levels. **C342/C340/C341** need volume/notional/price-impact. **C315/C320** trade raw seasonal RETURN mean-reversion. **C355 is distinct from all of the above:** it is a tolerance-based *template-matching* nonlinear-complexity statistic (SampEn), not an ordinal-pattern entropy (C349), not a curve-length fractal dimension (C354), not a detrended fluctuation slope (C350), not a frequency-domain long-memory estimate (C351/C352), not a variance ratio (C353). Price-only (`perp_close` only), volume-free, no network, no fabrication, no resampling, no imputation.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign355_sample_entropy_5m/<SYM>.npz` per symbol from real C312 `perp_close` (identical 5-field layout to C350–C354; no network, no fabrication, no resampling, no imputation):
```
index_ms      int64    common 5m grid (intersection across all 10 perps, 315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB (per-symbol float32 npz shards; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic window `W = 64` bars (fixed, decoupled from seasonal lookback L); embedding dimension `m ∈ {2, 3}`; tolerance `r = 0.25` (in z-score units). For each bar t:
- Take trailing `W` returns `X = r[t-W+1..t]` (NaN if `t < W` or any NaN in window).
- **Standardize the window:** `z = (X - mean(X)) / std(X)` (population std). NaN if `std(X) ≤ 0` or non-finite.
- For each `m ∈ {2, 3}`, build length-`m` templates `T_m[i] = z[i .. i+m-1]` for `i = 0 .. W-m`, and length-(m+1) templates `T_{m+1}[i] = z[i .. i+m]` for `i = 0 .. W-m-1`.
- **Pair counting (ordered pairs, `i ≠ j`):** `B_m = #{(i,j): i≠j, max_{d<m}|T_m[i][d]-T_m[j][d]| < r}`; `A_m = #{(i,j): i≠j, max_{d<m+1}|T_{m+1}[i][d]-T_{m+1}[j][d]| < r}`. Only the self-pair `i==j` is excluded; overlapping neighbours `|i-j|<m` are INCLUDED (this is the standard Richman–Moorman convention).
- `SampEn_m[t] = ln(B_m) - ln(A_m) = -ln(A_m / B_m)`. NaN if `t<W`, any NaN in window, `std(X)≤0`, `A_m==0`, or `B_m==0` (bar dropped from the cross-section).
- Real metrics produced: `sampen_m2[t] = SampEn with m=2` and `sampen_m3[t] = SampEn with m=3` (two genuinely-distinct real signals — different embedding dimension m).
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {sampen_m2[t], sampen_m3[t]}` (symmetric z-fade).
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute `sampen_m2` and `sampen_m3` for all bars per asset with a vectorized `sliding_window_view` path (chunked over bars; build the `(chunk, W-m+1, m)` template tensor per chunk, broadcast the Chebyshev `max`-abs difference `|T[...,None,:]-T[...,None,:,:]|` → `max` over the feature axis, threshold `< r`, sum over the two template axes, subtract the diagonal to drop `i==j`). No Python loop over 315,648 bars × 10 assets. It MUST pass a brute-force equality test against a reference per-window SampEn implementation (manual loop over windows, explicit double loop over `i,j` with `max(|...|)` Chebyshev distance and explicit `A/B` counting).

### Pre-registered grid — 1296 configs
- SIGNALS = `sampen_m2_dev`, `sampen_m3_dev`, `sampen_m2_placebo`, `sampen_m3_placebo` (2 real: SampEn m=2 and m=3; 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261221` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN). selection frac = 1/3, ALPHA = 0.05.
- Reference config (stability/attribution): `sampen_m2_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {sampen_m2_dev, sampen_m3_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `sampen_m2_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c355_sample_entropy_features.py` → `data/cache/campaign355_sample_entropy_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c355.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c355_sample_entropy_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign355_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign355_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign355_summary_<TS>Z.json`
   - `reports/campaign355_verdict_<TS>Z.json`
   - `reports/campaign355_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c355.py` + `tests/test_c355_sample_entropy_xsec_oos.py` — ≥21 green (incl. SampEn brute-force equality test).
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C355 section) + `research_state/state.yaml`; add C355 to the frozen table with its 5 SHAs; set C356 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

---

## C356 — PRE-REGISTERED SPEC (ACTIVE — FROZEN, EXECUTE EXACTLY)

**C356 — CROSS-SECTIONAL INTRADAY MULTISCALE ENTROPY (MSE) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. FULLY PRE-REGISTERED — EXECUTE VERBATIM: build → preflight (`ready:true`) → full 1296-config costed-OOS sweep → pytest (≥21 green) → 5 SHA256 artifacts → recorded → frozen → set C357 active.**

C356 is mechanically-distinct, genuinely-new, price-only (volume-free), buildable from real C312 `perp_close` alone. NOT a re-skin of C281B–C355. **This spec is complete and frozen — execute it verbatim.**

**Distinctness proof (pre-registered):**
- C356 measures **Multiscale Entropy (MSE)** (Costa, Goldberger, Peng 2002, 2005) — a *multi-scale nonlinear regularity* profile. For a time series, MSE computes Sample Entropy (SampEn) at multiple coarse-grained time scales `τ = 1..τ_max`. At each scale `τ`, the series is coarse-grained by averaging non-overlapping windows of length `τ`, yielding a new series `y^{(τ)}` of length `N/τ`; SampEn is then computed on each `y^{(τ)}` with fixed embedding dimension `m` and tolerance `r`. The MSE profile is the vector `(SampEn(τ=1), SampEn(τ=2), ..., SampEn(τ=τ_max))`. Key scalars: `mse_slope` = OLS slope of SampEn vs `log(τ)` over `τ=1..τ_max` (negative = complexity loss at large scales / long-range regularity; positive = complexity gain); `mse_area` = area under the MSE curve (total complexity across scales). Low SampEn at small scales = local regularity; persistent high SampEn across scales = sustained irregularity/complexity.
- **C355** measured **single-scale Sample Entropy (SampEn)** at fixed `W=64`, `m∈{2,3}`, `r=0.25` — one scale, no coarse-graining. **C349** measured permutation entropy (ordinal patterns, no template matching, no coarse-graining). **C354** measured Higuchi fractal dimension (curve-length scaling, first differences, no template matching). **C350** measured DFA α (detrended fluctuation slope, integration + detrending, OLS of log F(n) vs log n). **C351/C352** measured frequency-domain fractional-integration d (GPH OLS / local-Whittle MLE). **C353** measured Lo–MacKinlay variance ratio (second-moment ratio across horizons q=8,16). **C346** measured R/S (range of cumulative centered sum). **C343** measured autocorrelation of `|r|`. **C344** measured sign-change rate. **C326** measured lag-1 signed-return autocorrelation. **C345** measured close location in trailing envelope. **C317** measured realized-vol levels. **C342/C340/C341** need volume/notional/price-impact. **C315/C320** trade raw seasonal RETURN mean-reversion. **C356 is distinct from all of the above:** it is the *coarse-grained multi-scale SampEn profile* (MSE), computing SampEn at multiple time scales `τ=1..τ_max` on progressively coarse-grained series. This is fundamentally different from single-scale SampEn (C355), ordinal-pattern entropy (C349), curve-length fractal dimension (C354), detrended fluctuation (C350), frequency-domain long-memory (C351/C352), variance ratio (C353). Price-only (`perp_close` only), volume-free, no network, no fabrication, no resampling, no imputation.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign356_multiscale_entropy_5m/<SYM>.npz` per symbol from real C312 `perp_close` (identical 5-field layout to C350–C355; no network, no fabrication, no resampling, no imputation):
```
index_ms      int64    common 5m grid (intersection across all 10 perps, 315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache < 100 MB (per-symbol float32 npz shards; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, per bar t)
Intrinsic window `W = 64` bars (fixed, decoupled from seasonal lookback L); coarse-graining scales `τ ∈ {1, 2, 4, 8, 16, 32}` (`τ_max = 32`; all divide 64); embedding dimension `m = 2`; tolerance `r = 0.25` (in z-score units at each scale). For each bar t:
- Take trailing `W` returns `X = r[t-W+1..t]` (NaN if `t < W` or any NaN in window).
- For each scale `τ ∈ {1, 2, 4, 8, 16, 32}`:
  - **Coarse-grain:** partition `X` into `N_τ = W // τ` non-overlapping blocks of length `τ`; `y^{(τ)}[k] = mean(X[k·τ : (k+1)·τ])` for `k = 0..N_τ-1`.
  - **Standardize:** `z^{(τ)} = (y^{(τ)} - mean(y^{(τ)})) / std(y^{(τ)})` (population std). NaN if `std ≤ 0` or non-finite.
  - **SampEn on coarse-grained series:** build length-`m` templates `T_m[i] = z^{(τ)}[i .. i+m-1]` for `i = 0 .. N_τ-m`, and length-(m+1) templates `T_{m+1}[i] = z^{(τ)}[i .. i+m]` for `i = 0 .. N_τ-m-1`.
  - **Pair counting (ordered pairs, `i ≠ j`):** `B_m^{(τ)} = #{(i,j): i≠j, max_{d<m}|T_m[i][d]-T_m[j][d]| < r}`; `A_m^{(τ)} = #{(i,j): i≠j, max_{d<m+1}|T_{m+1}[i][d]-T_{m+1}[j][d]| < r}`. Only self-pair `i==j` excluded; overlapping neighbours `|i-j|<m` INCLUDED.
  - `SampEn^{(τ)}[t] = ln(B_m^{(τ)}) - ln(A_m^{(τ)}) = -ln(A_m^{(τ)} / B_m^{(τ)})`. NaN if `N_τ < m+1`, `A_m^{(τ)}==0`, or `B_m^{(τ)}==0`.
- **MSE profile scalars (real metrics):**
  - `mse_slope[t]` = OLS slope of `SampEn^{(τ)}` vs `log(τ)` over `τ ∈ {1,2,4,8,16,32}` (requires ≥ 3 finite SampEn points). Negative = complexity decays with scale (long-range regularity); positive = complexity grows with scale.
  - `mse_area[t]` = trapezoidal area under `SampEn^{(τ)}` vs `τ` curve (sum over `τ` of `(SampEn^{(τ)}+SampEn^{(τ_next)})/2 * (τ_next-τ)`). Total complexity across scales.
  - (Both NaN if < 3 finite SampEn points at the required scales.)
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std of `v[t]` at same `(weekday × tod)` bucket (2016 buckets) from history strictly BEFORE t (causal `shift(1)`), NaN-aware `min_periods=3`. Score `s[t] = -(v[t]-seasonal_mean)/seasonal_std` for `v[t] ∈ {mse_slope[t], mse_area[t]}` (symmetric z-fade).
Cross-sectional rank across 10 symbols → dollar-neutral gross 1.0 → single-leg dollar-neutral perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5·fee+slip). `executed_fills:false`.

### Fast vectorized execution requirement
Compute MSE profile (`mse_slope`, `mse_area`) for all bars per asset with a vectorized `sliding_window_view` + chunked coarse-graining path (no Python loop over 315,648 bars × 10 assets). For each chunk, build coarse-grained series at all `τ` via `reshape` + `mean(axis=-1)`, then vectorized SampEn per scale via broadcasted Chebyshev template matching. It MUST pass a brute-force equality test against a reference per-window MSE implementation (manual loop over windows, explicit coarse-graining via loop over `τ`, per-scale `np.mean`, explicit SampEn double loop over `i,j` with `max(|...|)` Chebyshev distance).

### Pre-registered grid — 1296 configs
- SIGNALS = `mse_slope_dev`, `mse_area_dev`, `mse_slope_placebo`, `mse_area_placebo` (2 real: MSE slope and MSE area; 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS = `(60, 120, 240, 480, 960, 1920)`; REBALANCES = `(1, 4, 12)`; FEES = `(0.0004, 0.0007, 0.0010)`; SLIPS = `(0.0, 0.0001, 0.0002)`; COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`). Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12. Placebo seed `20261222` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN). selection frac = 1/3, ALPHA = 0.05.
- Reference config (stability/attribution): `mse_slope_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker. `ATTR_REPRESENTATIVES = {mse_slope_dev, mse_area_dev}`.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `mse_slope_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Deliverables (do ALL six, in order, no pauses)
1. `scripts/build_c356_multiscale_entropy_features.py` → `data/cache/campaign356_multiscale_entropy_5m/` (10 shards + meta + provenance + SHA256 manifest; real C312 `perp_close` only; idempotent `--force`; 100 MB budget check).
2. `scripts/preflight_c356.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
3. `scripts/run_c356_multiscale_entropy_xsec_oos.py` — full 1296-config costed-OOS sweep. Emit 5 SHA256 artifacts + gitignored `.full.json`:
   - `reports/campaign356_oos_sweep_<TS>Z.json` + `.full.json`
   - `reports/campaign356_tradable_edge_registry_<TS>Z.json`
   - `reports/campaign356_summary_<TS>Z.json`
   - `reports/campaign356_verdict_<TS>Z.json`
   - `reports/campaign356_binding_constraint_<TS>Z.json`
4. `tests/test_preflight_c356.py` + `tests/test_c356_multiscale_entropy_xsec_oos.py` — ≥21 green (incl. MSE brute-force equality test).
5. Record the truthful result (formal negative or edge) in this `AGENTS.md` (new C356 RESULT section) + `research_state/state.yaml`; add C356 to the frozen table with its 5 SHAs; set C357 as active.
6. Run sequence: build → preflight → full costed-OOS sweep → pytest → capture 5 SHA256 artifacts. The heavy sweep IS the economic progress — do NOT abort it.

---

## C356 ACTIVE — NEXT GENUINELY-NEW PRICE-ONLY FAMILY

C356 = cross-sectional intraday MULTISCALE ENTROPY (MSE) × seasonal-dislocation mean-reversion stat-arb (USDT-M 5m), price-only, volume-free, on real C312 5m data. PRE-REGISTERED SPEC FROZEN ABOVE — execute verbatim: build → preflight (`ready:true`) → full 1296-config costed-OOS sweep → pytest (≥21 green) → 5 SHA256 artifacts → recorded → frozen → set C357 active. No edge claim unless Holm+BH over all 1296 configs AND attribution_ok AND stability. Terminal closure by fiat PROHIBITED — continue executing pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.

---

## Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new price-only families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.