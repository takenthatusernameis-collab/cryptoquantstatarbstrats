# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T07:37:40Z. Repo: cryptoquantstatarbstrats — crypto quantitative **statistical arbitrage**. Economic progress = real-data costed out-of-sample PnL run, passing test, or artifact update. A session that only re-reads this handoff, re-declares closure, or re-runs a frozen campaign is NOT economic progress and is a hard violation. **This AGENTS.md is the single authoritative durable handoff — do NOT create a separate HANDOFF.md or any duplicate handoff file; update this file in place.**

> **INITIAL TASK MESSAGE (2026-11-17T07:37:40Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP): C348 — cross-sectional intraday REALIZED-VARIANCE CONCENTRATION (HHI of squared returns) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), PRICE-ONLY.** C281B–C347 are ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~76,900+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C347 `20261117T073740Z` frozen (1296 configs, RETRACTED, dominant `dd_long_placebo` 0.2783). **No bottlenecks** — C347 build+preflight+cache+tests+full sweep all on disk and green (24/24 tests); 5 SHA256 artifacts emitted. C312 5m on-disk (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars, 2023-01..2025-12, fields incl. `perp_close`). C287 external blocked/decoupled (451/403) — never retry. Do NOT re-read/plan/re-declare closure/re-run frozen C281B–C347/C287 or weaken any gate.
>
> **EXECUTE C348 NOW (full pipeline, no pauses):**
> 1. **Build** `scripts/build_c348_realized_var_concentration_features.py` → `data/cache/campaign348_realized_var_concentration_5m/` (10 shards `<SYM>.npz` + `meta.json` + `provenance.json` + SHA256 manifest). Real C312 `perp_close` only; no network/fabrication/resampling/imputation/relabeling. Fields per shard: `index_ms int64`, `perp_close float32`, `log_return float32` (`r[t]=log(c[t]/c[t-1])`, `r[0]=0`), `abs_ret float32`, `funding_rate float32` (all-NaN control). `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `source_campaign:312`, cache <100 MB, idempotent (`--force`).
> 2. **Preflight** `scripts/preflight_c348.py` — fail-closed cache/integrity/field/coverage checks → `ready:true`.
> 3. **Sweep** `scripts/run_c348_realized_var_concentration_xsec_oos.py` — full pre-registered costed-OOS grid (see C348 pre-registration section below), 8 splits 12m train/3m test roll 3m over 2023-01..2025-12. Emit 5 SHA256 artifacts: `reports/campaign348_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>Z.json` + gitignored `.full.json`.
> 4. **Tests** `tests/test_preflight_c348.py` + `tests/test_c348_realized_var_concentration_xsec_oos.py` — ≥21 green.
> 5. **Record** truthful result (formal negative or edge) in `AGENTS.md` + `research_state/state.yaml`, update frozen list + SHAs, and set the next genuinely-new price-only family as active. Heavy sweep is economic progress — do not abort.
>
> **C348 spec** — full pre-registered spec, grid (1296 configs), gates, and distinctness proof are in the `PRE-REGISTERED NEXT CAMPAIGN — C348` section below. Signals `hhi_dev`, `hhi_norm_dev`, `hhi_placebo`, `hhi_norm_placebo`; lookbacks `(60,120,240,480,960,1920)`; reb `(1,4,12)`; fees `(0.0004,0.0007,0.0010)`; slips `(0.0,0.0001,0.0002)`; cost variants `(taker,maker_blend)`; placebo seed `20261123`; selection frac 1/3; ALPHA 0.05. Gates: Holm+BH over all 1296 (BOTH), MDE, stability (ref `hhi_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker), attribution (dominant real non-placebo signal share ≥0.5). Verdict: 0 both → RETRACTED(multiple_testing); else not attribution_ok → RETRACTED(attribution); else not stable → RETRACTED(stability); else EDGE_PROVEN. No edge claim without Holm+BH+attribution_ok+stability. Single-leg dollar-neutral, costs on turnover, `executed_fills:false`.
>
> **After C348:** record result truthfully, mark frozen with SHAs, and set the next genuinely-new price-only family as active. Never stop for lack of a named next campaign.

**Program state:** `ACTIVE — NO-EDGE CONFIRMED THROUGH C347 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED: execute every pre-registered genuinely-new family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C347 DONE/frozen; do NOT re-run C281B–C347/C287.**

**Bottlenecks:** **NONE.** C347 pipeline fully complete (build+preflight+cache+tests+full sweep on disk, 24/24 tests, 5 SHA256 artifacts at `20261117T073740Z`); the prior C346 half-build bottleneck was removed in the previous session. C312 5m input data on-disk and sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT — × 315,648 bars, 2023-01..2025-12; fields incl. `perp_close`); C337–C347 caches/artifacts on disk; C287 remains externally blocked/decoupled (451/403, no creds) — never retry as economic work. No blocker may defer C348. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests. If a build/preflight/sweep is slow, it is PROGRESS — do not abort; the heavy sweep is the economic work.

**Closure audit (C281B–C318 scope, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C346 extend the record. Do NOT regenerate/run stale closure generators.

**Frozen campaigns (do NOT re-run):** C337 `20261116T234925Z` (7776, asym_placebo 0.1957), C338 `20261117T004211Z` (4212, shannon_entropy_placebo 0.1367), C339 `20261117T005324Z` (1944, align_z_placebo 0.4791), C340 `20261117T032549Z` (2592, flow_cv_placebo 0.1803), C341 `20261117T031751Z` (2592, pid_placebo 0.2004), C342 `20261117T034113Z` (2592, kurt_placebo 0.1842), C343 `20261117T041856Z` (1944, vcr_placebo 0.2445), C344 `20261117T042911Z` (1296, chop_placebo 0.2519), C345 `20261117T052603Z` (1296, wr_placebo 0.2596), C346 `20261117T063205Z` (1296, rs_dir_placebo 0.4432), C347 `20261117T073740Z` (1296, dd_long_placebo 0.2783). All: 0 Holm+BH, binding `multiple_testing`, RETRACTED, attribution_ok false, 5 SHA256 artifacts + gitignored `.full.json`, tests green. Full per-campaign SHAs cached in `research_state/state.yaml` and `reports/`.

---

## MANDATORY CAMPAIGN — C343: cross-sectional intraday VOLATILITY-CLUSTERING / ABSOLUTE-RETURN AUTOCORRELATION SEASONAL DISLOCATION mean-reversion stat-arb (USDT-M 5m) — COMPLETE / FROZEN

Mechanically distinct from C315–C342:
- C326 measured signed-return autocorrelation (first-moment direction dependence). C343 measures **second-moment dependence**: autocorrelation of `|log_return|` (volatility clustering) — distinct from C326.
- C317 measured realized-vol LEVELS. C343 measures vol CLUSTERING/REGIME-SHIFT vs seasonal baseline — distinct from C317.
- C342 measured volume-weighted return skewness/kurtosis. C343 is unweighted absolute-return dependence — distinct from C342.

**Result (truthful, on-disk):** `20261117T041856Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `vcr_placebo` 0.2445 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1944 configs (6 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 21/21 tests green (`tests/test_preflight_c343.py` + `tests/test_c343_volatility_clustering_xsec_oos.py`). Cache `data/cache/campaign343_volatility_clustering_5m/` (10 shards × 315,648 bars, 49.38 MB < 100 MB, real_data_only). Scripts: `scripts/build_c343_volatility_clustering_features.py`, `scripts/preflight_c343.py`, `scripts/run_c343_volatility_clustering_xsec_oos.py`. **DO NOT RE-RUN.**

---

## MANDATORY CAMPAIGN — C344: cross-sectional intraday RETURN SIGN-CHANGE (CHOP/WHIPSAW) RATE x LAST-MOVE DIRECTION / MAGNITUDE-CONDITIONED OVERREACTION-REVERSAL mean-reversion stat-arb (USDT-M 5m) — COMPLETE / FROZEN

Mechanically distinct from C281B–C343:
- C326 measured signed-return AUTOCORRELATION (lag-1 first-moment direction). C344 measures the SIGN-CHANGE RATE over a whole window (multi-bar chop) × last-move direction — different functional and trade rule.
- C343 measured autocorrelation of `|log_return|` (volatility clustering). C344 is a directional reversal of the last move, not vol autocorrelation.
- C317 measured realized-vol LEVELS / higher moments. C344 is directional and conditions the fade on chop rate / magnitude extremity.
- C340/C341/C342 need volume/notional/price-impact; C344 is price-only and volume-free.
- C315/C320 trade raw seasonal RETURN mean-reversion (signed deviation). C344 conditions the fade on chop rate / magnitude extremity of the last move.

**Result (truthful, on-disk):** `20261117T042911Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `chop_placebo` 0.2519 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1296 configs (4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 21/21 tests green (`tests/test_preflight_c344.py` + `tests/test_c344_return_chop_xsec_oos.py`). Cache `data/cache/campaign344_return_chop_5m/` (10 shards × 315,648 bars, ~49.38 MB < 100 MB, real_data_only). Scripts: `scripts/build_c344_return_chop_features.py`, `scripts/preflight_c344.py`, `scripts/run_c344_return_chop_xsec_oos.py`. **DO NOT RE-RUN.**

---

## MANDATORY CAMPAIGN — C345: cross-sectional intraday CLOSE-LOCATION-WITHIN-TRAILING-EXTREME-ENVELOPE (WILLIAMS %R-STYLE) x LAST-MOVE DIRECTION SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m) — COMPLETE / FROZEN

C345 is a mechanically-distinct, genuinely-new, price-only (volume-free) family. It is NOT a re-skin of C281B–C344. It is buildable from real C312 `perp_close` alone (no fabricated high/low needed — rolling max/min of the close series defines the envelope).

**Result (truthful, on-disk):** `20261117T052603Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `wr_placebo` 0.2596 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1296 configs (4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants — the spec text's "1944" claim was an arithmetic slip; the literal product of the listed grid is 1296). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 22/22 tests green (`tests/test_preflight_c345.py` + `tests/test_c345_close_envelope_xsec_oos.py`). Cache `data/cache/campaign345_close_envelope_5m/` (10 shards × 315,648 bars, 38.48 MB < 100 MB, real_data_only). Scripts: `scripts/build_c345_close_envelope_features.py`, `scripts/preflight_c345.py`, `scripts/run_c345_close_envelope_xsec_oos.py`. **DO NOT RE-RUN.**

### Why C345 is genuinely new (distinctness proof)
- C330 measured realized-path DRAWDOWN/RUNUP/PATH-EFFICIENCY (drawdown from running peak, close-to-close). C345 measures the **level of the current close within its trailing L-bar high–low envelope** (a bounded [0,1] position statistic, Williams %R-style) — different functional (relative position in range, not path drawdown), different normalization (rolling extreme envelope, not running peak-to-close distance).
- C326 measured signed-return AUTOCORRELATION (lag-1 first-moment product). C345 measures an extremum-relative POSITION statistic × last-move direction — not an autocorrelation.
- C344 measured SIGN-CHANGE RATE over a window × last-move direction. C345's conditioning variable is the close's position within the trailing price envelope (how extended vs its own range), not chop rate.
- C343 measured `|log_return|` autocorrelation (vol clustering). C345 is a directional overextension fade, not vol clustering.
- C317 measured realized-vol LEVELS. C345 is a positional (range) statistic, scale-free and directional.
- C342/C340/C341 need volume/notional/price-impact; C345 is price-only and volume-free.
- C315/C320 trade raw seasonal RETURN mean-reversion. C345 fades EXTENSION within the trailing close envelope, conditioned on last-move direction.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign345_close_envelope_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network, no fabrication, no resampling, no imputation). Fields:
```
index_ms      int64    common 5m grid (intersection across all 10 perps, ~315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache must stay < 100 MB total (same per-symbol float32 npz shard layout as C344; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, trailing lookback L bars ending at bar t)
Let `c` = perp_close, `r` = log_return. Over trailing window `[t-L+1 .. t]`:
- `roll_max[t] = max(c[t-L+1..t])`, `roll_min[t] = min(c[t-L+1..t])`, `env_range[t] = roll_max - roll_min`.
- `clv_pos[t] = (c[t] - roll_min[t]) / env_range[t]` in [0,1] — **Close Location Value within trailing extreme envelope** (Williams %R = clv_pos - 0.5). NaN where `env_range <= 0` or `t < L`.
- `wr[t] = sign(r[t]) * (clv_pos[t] - 0.5)` — directional overextension: positive when close sits high in its range after an up-move (overbought → fade down), negative when low after a down-move.
- `wr_ext[t] = sign(r[t]) * clv_pos[t]` — direction-conditioned extreme version (close pinned at top/bottom of envelope).

Seasonal baseline: trailing mean/std at same `(weekday × tod)` bucket (288 bars/day × 7 weekdays = 2016 buckets) from history strictly BEFORE bar t (causal shift(1)), NaN-aware min_periods=3 excluding NaN obs. Score `s[t] = -(v[t] - seasonal_mean) / seasonal_std` (fade: unusually extended → expect reversion). Cross-sectional rank, dollar-neutral gross 1.0, single-leg dollar-neutral perp PnL with costs on turnover (taker = fee+slip; maker_blend = 0.5*fee+slip).

### Pre-registered grid — 1944 configs
- SIGNALS = `wr_dev`, `wr_ext_dev`, `wr_placebo`, `wr_ext_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS (bars) = `(60, 120, 240, 480, 960, 1920)`.
- REBALANCES (bars) = `(1, 4, 12)`.
- FEES = `(0.0004, 0.0007, 0.0010)`.
- SLIPS = `(0.0, 0.0001, 0.0002)`.
- COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1944 configs** (must be the literal `N_TRIALS`).
- Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12.
- Placebo seed: record a fixed integer seed (e.g. 20261119); phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN.
- selection frac = 1/3, ALPHA = 0.05.

### Gates (identical rigor to C344 — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1944 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `wr_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Delivered (C345 session, complete — all heavy work produced this session)
1. `scripts/build_c345_close_envelope_features.py` — real C312 `perp_close` shard cache + meta + provenance + SHA256 manifest, idempotent (`--force`), 100 MB budget check; cache `data/cache/campaign345_close_envelope_5m/` 38.48 MB < 100 MB, `real_data_only:true`, 0 NaN.
2. `scripts/preflight_c345.py` — fail-closed cache verification; `ready:true`.
3. `scripts/run_c345_close_envelope_xsec_oos.py` — full 1296-config costed-OOS sweep; 5 SHA256 artifacts emitted (ts `20261117T052603Z`):
   - `reports/campaign345_oos_sweep_20261117T052603Z.json` (sha256 `c0078c5539823d4ba4b2e7cec0e36e9fcc8ae4443487f4578a1d2316f7904616`) + gitignored `.full.json`
   - `reports/campaign345_tradable_edge_registry_20261117T052603Z.json` (sha256 `850ab7b2ccdf6b00d639c8592cc4ab58cdf328dcaae9a1e732b49f32a00f47b7`)
   - `reports/campaign345_summary_20261117T052603Z.json` (sha256 `b429572353168b26a7dfba9064dd71658733888bf2fa97c5cbd122256f4426c5`)
   - `reports/campaign345_verdict_20261117T052603Z.json` (sha256 `52a3bbefe07a58b04fb66d715aed3f47781ae15f95758b1a58e1ffe48a15a92c`)
   - `reports/campaign345_binding_constraint_20261117T052603Z.json` (sha256 `14fa2dd2ab9ae2e5b94ab5e463843bd9bb4221cf7b8cf14213810220e3e61643`)
4. `tests/test_preflight_c345.py` + `tests/test_c345_close_envelope_xsec_oos.py` — 22/22 tests green.
5. Run sequence executed: build → preflight → full costed-OOS sweep → pytest → 5 SHA256 artifacts captured above.
6. Truthful result recorded in this AGENTS.md (this C345 section) + `research_state/state.yaml`; C346 set next active (see INITIAL TASK MESSAGE above).

Result summary: verdict RETRACTED, binding `multiple_testing`, `edge_proven:false`, 0 Holm+BH survivors over the 1296-config grid, dominant attribution `wr_placebo` 0.2596 < 0.5 → `attribution_ok:false`. Formal negative — no costed-OOS edge survived C345.

### Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1944 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.
---

## MANDATORY CAMPAIGN — C346: cross-sectional intraday RESCALED-RANGE / HURST-PROXY (R/S) x SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m) — COMPLETE / FROZEN

C346 is a mechanically-distinct, genuinely-new, price-only (volume-free) family. It is NOT a re-skin of C281B–C345. It is buildable from real C312 `perp_close` alone (no fabricated data needed).

**Result (truthful, on-disk):** `20261117T063205Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `rs_dir_placebo` 0.4432 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1296 configs (4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 23/23 tests green (`tests/test_preflight_c346.py` + `tests/test_c346_rescaled_range_xsec_oos.py`). Cache `data/cache/campaign346_rescaled_range_5m/` (10 shards × 315,648 bars, 38.48 MB < 100 MB, real_data_only). Scripts: `scripts/build_c346_rescaled_range_features.py`, `scripts/preflight_c346.py`, `scripts/run_c346_rescaled_range_xsec_oos.py`. **DO NOT RE-RUN.**

### Artifacts (ts 20261117T063205Z)
- `reports/campaign346_oos_sweep_20261117T063205Z.json` (sha256 `977a60576be0395b37ab6f8001fa1a11d5803ad361b3a77d72dfb780e5a8f784`) + gitignored `.full.json`
- `reports/campaign346_tradable_edge_registry_20261117T063205Z.json` (sha256 `e05a3d755a26ef3a819baacda9449dceea64c4803d359a6675dc93235849ca4c`)
- `reports/campaign346_summary_20261117T063205Z.json` (sha256 `e2fec4319fc1ce8fea6fc3c55f4abaf2c8e9d4e5041771e6ce8340d4e04b890f`)
- `reports/campaign346_verdict_20261117T063205Z.json` (sha256 `d846c590b179167d77802dc8d5681a456bc61916d715824f643438d2208aa87a`)
- `reports/campaign346_binding_constraint_20261117T063205Z.json` (sha256 `3f3f2468e598e1e66fa177f57a82a6f116f9940d397e284a92ca97105ce7e1d5`)

### Why C346 is genuinely new (distinctness proof)
- C346 measures the **range R = max(Z) − min(Z) of the cumulative centered-return sum** over a fixed trailing window, normalized as `rs_norm = (R / S) / sqrt(L)` (a rescaled-range / Hurst proxy). This is a global range–dispersion / persistence statistic over the whole window.
- C326 measured lag-1 signed-return AUTOCORRELATION (first-moment product at one lag) — C346 is a whole-window range statistic, not a point autocorrelation.
- C343 measured autocorrelation of `|r|` (second-moment vol clustering) — C346 is a cumulative-sum range, not a second-moment autocorrelation.
- C344 measured SIGN-CHANGE RATE over a window × last-move direction — C346 is a continuous range statistic, not a chop count.
- C330 measured realized-path DRAWDOWN/RUNUP/PATH-EFFICIENCY (price drawdown from running peak) — C346 is the range of the cumulative CENTERED sum within a fixed window, differently normalized (bounded by window size, scaled by sqrt(L)).
- C345 measured close LOCATION within a trailing high–low envelope (Williams %R-style bounded position) — C346 is a cumulative-sum range, not an envelope position.
- C317 measured realized-vol LEVELS — C346 is a scale-normalized range proxy.
- C342/C340/C341 need volume/notional/price-impact; C346 is price-only and volume-free.
- C315/C320 trade raw seasonal RETURN mean-reversion — C346 fades the rescaled-range seasonal dislocation, conditioned on last-move direction.

Result summary: verdict RETRACTED, binding `multiple_testing`, `edge_proven:false`, 0 Holm+BH survivors over the 1296-config grid, dominant attribution `rs_dir_placebo` 0.4432 < 0.5 → `attribution_ok:false`. Formal negative — no costed-OOS edge survived C346.

---

## MANDATORY CAMPAIGN — C347: cross-sectional intraday DRAWDOWN DURATION / TIME-UNDER-WATER (CUMULATIVE CENTERED-SUM PATH) x SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), PRICE-ONLY — COMPLETE / FROZEN

C347 is a mechanically-distinct, genuinely-new, price-only (volume-free) family. It is NOT a re-skin of C281B–C346. It is buildable from real C312 `perp_close` alone (no fabricated data needed).

**Result (truthful, on-disk):** `20261117T073740Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `dd_long_placebo` 0.2783 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1296 configs (4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 24/24 tests green (`tests/test_preflight_c347.py` + `tests/test_c347_drawdown_duration_xsec_oos.py`). Cache `data/cache/campaign347_drawdown_duration_5m/` (10 shards × 315,648 bars, 38.48 MB < 100 MB, real_data_only). Scripts: `scripts/build_c347_drawdown_duration_features.py`, `scripts/preflight_c347.py`, `scripts/run_c347_drawdown_duration_xsec_oos.py`. **DO NOT RE-RUN.**

### Artifacts (ts 20261117T073740Z)
- `reports/campaign347_oos_sweep_20261117T073740Z.json` (sha256 `9415b29aec5d7b0a796b4906b47db77dbaba03cc4c486edd574f43efdfa16a41`) + gitignored `.full.json`
- `reports/campaign347_tradable_edge_registry_20261117T073740Z.json` (sha256 `25c5e67cc9b38153b503b1449054108474deef341690ba5e2c37158702c30e29`)
- `reports/campaign347_summary_20261117T073740Z.json` (sha256 `b88b7895f807fcbfbfec79ec4b26a02922b25304ba0ef26d79c8e7d79ee34920`)
- `reports/campaign347_verdict_20261117T073740Z.json` (sha256 `e974564b40f571f98cd0db2ef2a6328710daff9fc2c60bba3c936de14cd06c87`)
- `reports/campaign347_binding_constraint_20261117T073740Z.json` (sha256 `c13f9c3abb15b3c9848319b0b485bbad8ce044fe94cb04fca0ed012d17443bfc`)

### Why C347 is genuinely new (distinctness proof — pre-registered)
- C347 measures **DRAWDOWN DURATION / TIME-UNDER-WATER** of the cumulative CENTERED-return sum path (longest consecutive underwater run `dd_long`, and underwater fraction `dd_frac`) within a trailing window — temporal persistence, not magnitude.
- C346 measured RESCALED-RANGE / Hurst proxy (R/S = MAGNITUDE of the cumulative centered-sum range) — C347 is duration underwater, not range magnitude.
- C330 measured realized-path DRAWDOWN/RUNUP/PATH-EFFICIENCY (price drawdown from running peak, close-to-close) — C347 measures duration below running peak of the cumulative CENTERED sum.
- C343 measured autocorrelation of `|r|` (vol clustering) — C347 is a duration statistic on the cumulative path.
- C344 measured SIGN-CHANGE RATE over a window × last-move direction (chop) — C347 is time-under-water, not a chop count.
- C345 measured close LOCATION within trailing high–low envelope (Williams %R-style) — C347 is duration underwater.
- C317 measured realized-vol LEVELS — C347 is a temporal persistence statistic.
- C342/C340/C341 need volume/notional/price-impact; C347 is price-only and volume-free.
- C315/C320 trade raw seasonal RETURN mean-reversion — C347 fades seasonal dislocation in drawdown duration, conditioned on last-move direction.

Result summary: verdict RETRACTED, binding `multiple_testing`, `edge_proven:false`, 0 Holm+BH survivors over the 1296-config grid, dominant attribution `dd_long_placebo` 0.2783 < 0.5 → `attribution_ok:false`. Formal negative — no costed-OOS edge survived C347.

---: cross-sectional intraday REALIZED-VARIANCE CONCENTRATION (HERFINDAHL-HHI OF SQUARED RETURNS) × SEASONAL-DISLOCATION mean-reversion stat-arb (USDT-M 5m), PRICE-ONLY

C348 is a mechanically-distinct, genuinely-new, price-only (volume-free) family. It is NOT a re-skin of C281B–C347. It is buildable from real C312 `perp_close` alone (no fabricated data needed).

### Why C348 is genuinely new (distinctness proof — pre-registered)
- **C348 measures the Herfindahl-Hirschman Index (HHI) of squared returns within a trailing window** — a concentration/inequality metric on the *distribution of variance contributions* across bars. High HHI = few bars dominate the realized variance (concentrated bursts); low HHI = variance spread evenly (diffuse).
- **C330** measured realized-path DRAWDOWN/RUNUP/PATH-EFFICIENCY (magnitude of price drawdown from running peak) — C348 measures *concentration of squared returns*, not path drawdown magnitude.
- **C343** measured autocorrelation of `|r|` (vol clustering / temporal dependence) — C348 measures *cross-sectional concentration* of variance contributions within a window, not serial correlation.
- **C344** measured SIGN-CHANGE RATE over a window × last-move direction (chop) — C348 is a distributional inequality statistic on squared returns, not a sign-change count.
- **C345** measured close LOCATION within trailing high–low envelope (Williams %R-style) — C348 is a variance-concentration statistic, not an envelope position.
- **C346** measured RESCALED-RANGE / Hurst proxy (R/S of cumulative centered sum) — C348 measures HHI of squared returns (variance concentration), not range of cumulative sum.
- **C347** measures DRAWDOWN DURATION / time-under-water of the cumulative centered-sum path (temporal persistence) — C348 measures *concentration of squared returns* within the window (distributional inequality), not duration underwater.
- **C317** measured realized-vol LEVELS (std/scale) — C348 measures *how concentrated* the variance is (HHI ∈ [1/L, 1]), not the level.
- **C342/C340/C341** need volume/notional/price-impact; C348 is price-only and volume-free.
- **C315/C320** trade raw seasonal RETURN mean-reversion — C348 fades seasonal dislocation in *variance concentration* (HHI), conditioned on last-move direction.

### Pre-registered raw inputs (build step)
Build `data/cache/campaign348_realized_var_concentration_5m/<SYM>.npz` per symbol from real C312 `perp_close` (no network, no fabrication, no resampling, no imputation). Fields per shard:
```
index_ms      int64    common 5m grid (intersection across all 10 perps, ~315,648 bars)
perp_close    float32  real 5m kline close (execution price)
log_return    float32  causal log-return r[t]=log(c[t]/c[t-1]), r[0]=0
abs_ret       float32  |log_return_t|
funding_rate  float32  all-NaN (control only; USDT-M funding unreachable — fapi 451)
```
Cache must stay < 100 MB total (per-symbol float32 npz shard layout; meta + provenance JSON; `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `network_ingest:false`, `resample:false`, `interval:5m`, `source_campaign:312`, SHA256 shard manifest).

### Runner-derived causal metrics (per asset, trailing lookback L bars ending at bar t)
Let `r` = log_return. Over trailing window `[t-L+1 .. t]`:
- `sq[t] = r[t]^2` — squared return (variance contribution of bar t).
- `sum_sq = sum(sq[t-L+1..t])` — total realized variance in window (NaN if any NaN in window or t<L).
- `hhi[t] = sum( (sq_i / sum_sq)^2 )` for i in window — **Herfindahl-Hirschman Index of squared returns**. Range: [1/L, 1]. High = few bars dominate variance; low = variance evenly spread. NaN if t<L or sum_sq ≤ 0.
- `hhi_norm[t] = (hhi[t] - 1/L) / (1 - 1/L)` — normalized to [0,1] (0 = perfectly diffuse, 1 = perfectly concentrated on one bar).
- `last_move_dir[t] = sign(r[t])` — direction of most recent bar.

Seasonal baseline: trailing mean/std at same `(weekday × tod)` bucket (288 bars/day × 7 weekdays = 2016 buckets) from history strictly BEFORE bar t (causal shift(1)), NaN-aware min_periods=3 excluding NaN obs. Score `s[t] = -(v[t] - seasonal_mean) / seasonal_std` where `v[t]` ∈ {`hhi[t]`, `hhi_norm[t]`} (fade: unusually concentrated variance → expect diffusion; unusually diffuse → expect concentration). Cross-sectional rank, dollar-neutral gross 1.0, single-leg dollar-neutral perp PnL with costs on turnover (taker = fee+slip; maker_blend = 0.5*fee+slip).

### Pre-registered grid — 1296 configs
- SIGNALS = `hhi_dev`, `hhi_norm_dev`, `hhi_placebo`, `hhi_norm_placebo` (2 real + 2 phase-randomized-surrogate placebos; placebos never edges).
- LOOKBACKS (bars) = `(60, 120, 240, 480, 960, 1920)`.
- REBALANCES (bars) = `(1, 4, 12)`.
- FEES = `(0.0004, 0.0007, 0.0010)`.
- SLIPS = `(0.0, 0.0001, 0.0002)`.
- COST_VARIANTS = `("taker", "maker_blend")`.
- 4 × 6 × 3 × 3 × 3 × 2 = **1296 configs** (literal `N_TRIALS`).
- Walk-forward: 12m train / 3m test, roll 3m → 8 OOS splits over 2023-01..2025-12.
- Placebo seed: `20261123` (phase-randomized FFT surrogate + rank restoration to original marginal; NaN positions stay NaN).
- selection frac = 1/3, ALPHA = 0.05.

### Gates (identical rigor — do NOT weaken)
- **Multiple testing**: one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05; edge requires BOTH.
- **MDE**: two-sided alpha=0.05, power=0.80: `(t_{0.975}+t_{0.80})*s/sqrt(n_splits)`.
- **Stability**: sign consistency ≥ 0.70 of splits AND first/second-half Sharpe corr ≥ 0.5 (reference config `hhi_dev`, L=240, H=4, fee=0.0007, slip=0.0001, taker).
- **Attribution**: mean |OOS net| per signal across all its configs; shares = |mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share ≥ 0.5 for `attribution_ok`.
- **Verdict logic**: `n_survive_both==0 → RETRACTED (multiple_testing)`; `>0 and not attribution_ok → RETRACTED (attribution)`; `>0 and not stable → RETRACTED (stability)`; `>0 and attribution_ok and stable → EDGE_PROVEN`. `edge_proven = bool(edge_idx and verdict=="EDGE_PROVEN")`.

### Mandatory constraints (carry-over, non-negotiable)
- Real on-disk C312 `perp_close` only; no network, no fabrication, no relabeling existing caches as new, no threshold/gate weakening, no cherry-picked windows/costs.
- No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs AND attribution_ok AND stability.
- Single-leg dollar-neutral perp PnL, costs on turnover; `executed_fills:false`. Only RNG is recorded-seed placebo phase randomization (never market data).
- Do NOT declare terminal closure by fiat. Keep executing pre-registered genuinely-new families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.