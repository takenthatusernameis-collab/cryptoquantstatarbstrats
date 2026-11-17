# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T05:21:22Z. Repo: cryptoquantstatarbstrats — crypto quantitative **statistical arbitrage**. Economic progress = real-data costed out-of-sample PnL run, passing test, or artifact update. A session that only re-reads this handoff, re-declares closure, or re-runs a frozen campaign is NOT economic progress and is a hard violation.

> **INITIAL TASK MESSAGE (2026-11-17T05:21:22Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP):** C281B–C345 are ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~73,000+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C340 `20261117T032549Z`, C341 `20261117T031751Z`, C342 `20261117T034113Z`, C343 `20261117T041856Z`, C344 `20261117T042911Z`, C345 `20261117T052603Z` — all 5 SHA256 artifacts emitted per campaign, tests green, all frozen. No costed-OOS edge has ever survived — a RESULT, not permission to stop. **C345 is DONE — COMPLETE FORMAL NEGATIVE** (verdict RETRACTED, binding `multiple_testing`, dominant attribution `wr_placebo` 0.2596 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`). Grid executed in full: 1296 configs (4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants; the AGENTS.md spec text's "1944" claim was an arithmetic slip carried from C343 — the literal product of the listed grid is 1296, matching C344's identical grid shape). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 22/22 tests green (`tests/test_preflight_c345.py` + `tests/test_c345_close_envelope_xsec_oos.py`). Cache `data/cache/campaign345_close_envelope_5m/` (10 shards × 315,648 bars, 38.48 MB < 100 MB, real_data_only). Scripts: `scripts/build_c345_close_envelope_features.py`, `scripts/preflight_c345.py`, `scripts/run_c345_close_envelope_xsec_oos.py`. **DO NOT RE-RUN.**

> **C346 is NEXT ACTIVE (initial task message 2026-11-17T05:26:03Z).** The next session MUST pre-register a genuinely-new, mechanically-distinct campaign family on real on-disk C312 5m `perp_close` (price-only, volume-free; no network, no fabrication, no relabeling of frozen caches as new), then execute the full pipeline: build shard cache → preflight → full costed-OOS sweep → pytest (≥21 green tests) → 5 SHA256 artifacts → record truthful result (formal negative or edge) in AGENTS.md + research_state/state.yaml → set C347 next. Apply the C345 gates unchanged (Holm+BH over the full grid at alpha=0.05, MDE, stability, signal-vs-placebo attribution; an edge requires ALL of them). Do NOT re-read and stop, re-declare closure by fiat, re-run frozen C281B–C345/C287, or weaken any gate. C287 remains externally blocked/decoupled (451/403) — never retry. **Bottlenecks: NONE. C312 5m data on-disk. Run the C346 pre-registration + build → preflight → sweep → pytest → artifacts now.**

**Program state:** `ACTIVE — NO-EDGE CONFIRMED THROUGH C345 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED: execute every pre-registered genuinely-new family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C345 DONE/frozen; do NOT re-run C281B–C345/C287.**

**Bottlenecks:** **NONE.** C312 5m input data on-disk and sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards — ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LINKUSDT, SOLUSDT, XRPUSDT — × 315,648 bars, 2023-01..2025-12; fields: `index_ms, signed_volume, total_volume, trade_count, trade_sign_sum, notional, vwap, perp_close, funding_rate`); C337–C344 caches/artifacts on disk; C287 remains externally blocked/decoupled (451/403, no creds) — never retry as economic work. No blocker may defer C345. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests. If a build/preflight/sweep is slow, it is PROGRESS — do not abort; the heavy sweep is the economic work.

**Closure audit (C281B–C318 scope, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C345 extend the record. Do NOT regenerate/run stale closure generators.

**Frozen campaigns (do NOT re-run):** C337 `20261116T234925Z` (7776, asym_placebo 0.1957), C338 `20261117T004211Z` (4212, shannon_entropy_placebo 0.1367), C339 `20261117T005324Z` (1944, align_z_placebo 0.4791), C340 `20261117T032549Z` (2592, flow_cv_placebo 0.1803), C341 `20261117T031751Z` (2592, pid_placebo 0.2004), C342 `20261117T034113Z` (2592, kurt_placebo 0.1842), C343 `20261117T041856Z` (1944, vcr_placebo 0.2445), C344 `20261117T042911Z` (1296, chop_placebo 0.2519), C345 `20261117T052603Z` (1296, wr_placebo 0.2596). All: 0 Holm+BH, binding `multiple_testing`, RETRACTED, attribution_ok false, 5 SHA256 artifacts + gitignored `.full.json`, tests green. Full per-campaign SHAs cached in `research_state/state.yaml` and `reports/`.

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