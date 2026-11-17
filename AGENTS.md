# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T04:11:44Z. Repo: cryptoquantstatarbstrats — crypto quantitative **statistical arbitrage**. Economic progress = real-data costed out-of-sample PnL run, passing test, or artifact update. A session that only re-reads this handoff, re-declares closure, or re-runs a frozen campaign is NOT economic progress and is a hard violation.

> **INITIAL TASK MESSAGE (2026-11-17T04:11:44Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP):** C281B–C342 are ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~67,000+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C340 `20261117T032549Z`, C341 `20261117T031751Z`, C342 `20261117T034113Z` — all 5 SHA256 artifacts emitted, 19/19 tests green, all frozen. No costed-OOS edge has ever survived — a RESULT, not permission to stop. **C343 is NOT STARTED** (no scripts/tests/cache/artifacts). Real C312 5m data is on-disk and sufficient: `data/cache/campaign312_usdt_m_ofi_5m/` 10 shards × 315,648 bars, 0-NaN on usable C343 fields (`perp_close`; `total_volume`,`signed_volume`,`notional` not required). No network/ingest needed. **Immediately begin C343 — cross-sectional intraday VOLATILITY-CLUSTERING / ABSOLUTE-RETURN AUTOCORRELATION SEASONAL DISLOCATION mean-reversion stat-arb (USDT-M 5m)** per the full pre-registered spec below (build cache → preflight → full 1944-config costed-OOS sweep → pytest → 5 artifacts → update AGENTS.md/state.yaml → set C344 next). Do **not** re-read and stop, re-declare closure, re-run frozen C281B–C342/C287, or regenerate stale closure generators.

**Program state:** `ACTIVE — NO-EDGE CONFIRMED THROUGH C342 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED: execute every pre-registered genuinely-new family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337/C338/C339/C340/C341/C342 DONE/frozen; do NOT re-run C281B–C342/C287.**

**Bottlenecks:** **NONE for C343.** C312 5m input data on-disk and sufficient; C337–C342 caches/artifacts on disk; C287 remains externally blocked/decoupled (451/403, no creds) — never retry as economic work. No blocker may defer C343. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests.

**Closure audit (C281B–C318 scope, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C342 extend the record. Do NOT regenerate/run stale closure generators.

**Frozen campaigns (do NOT re-run):** C337 `20261116T234925Z` (7776, asym_placebo 0.1957), C338 `20261117T004211Z` (4212, shannon_entropy_placebo 0.1367), C339 `20261117T005324Z` (1944, align_z_placebo 0.4791), C340 `20261117T032549Z` (2592, flow_cv_placebo 0.1803), C341 `20261117T031751Z` (2592, pid_placebo 0.2004), C342 `20261117T034113Z` (2592, kurt_placebo 0.1842). All: 0 Holm+BH, binding `multiple_testing`, RETRACTED, attribution_ok false, 5 SHA256 artifacts + gitignored `.full.json`, 19/19 tests green. Full per-campaign SHAs cached in `research_state/state.yaml` and `reports/`.

---

## MANDATORY CAMPAIGN — C343: cross-sectional intraday VOLATILITY-CLUSTERING / ABSOLUTE-RETURN AUTOCORRELATION SEASONAL DISLOCATION mean-reversion stat-arb (USDT-M 5m)

Mechanically distinct from C315–C342:
- C326 measured signed-return autocorrelation (first-moment direction dependence). C343 measures **second-moment dependence**: autocorrelation of `|log_return|` (volatility clustering) — distinct from C326.
- C317 measured realized-vol LEVELS. C343 measures vol CLUSTERING/REGIME-SHIFT vs seasonal baseline — distinct from C317.
- C342 measured volume-weighted return skewness/kurtosis. C343 is unweighted absolute-return dependence — distinct from C342.

**Pre-registered spec (execute as written):**
- Per symbol/bar (fail-closed NaN on degenerate/insufficient): `log_return_t = log(close_t/close_{t-1})`. `abs_ret_t = |log_return_t|`. `sq_ret_t = log_return_t^2`.
- Over trailing `lookback` bars ending at bar t-1 (causal, `shift(1)`), NaN-aware with explicit min_periods, no ffill/impute (NaN if std<=0 or insufficient finite obs):
  - `vcl1_t = lag-1 autocorrelation of abs_ret` — volatility clustering at lag 1.
  - `vcl5_t = lag-5 autocorrelation of abs_ret` — volatility clustering at lag 5.
  - `vcr_t = mean(|r| over most recent lookback/4 bars in window) / mean(|r| over preceding lookback/4 bars in window)` — realized-vol regime ratio; NaN if denominator<=0.
- Seasonal baseline = trailing seasonal mean/std at same (TOD × DOW) bucket from history strictly before bar t (causal, `shift(1)`), NaN-aware min-periods, fail-closed NaN if undefined; no ffill/impute.
- Score = `-seasonal-dislocation = -(signal_t - seasonal_baseline_t) / seasonal_std_t` (fail-closed NaN where undefined). Cross-sectional rank across 10 symbols each bar; dollar-neutral gross 1.0 (long top rank, short bottom rank, equal weight), exclude NaN scores with renormalization.
- Costed OOS: expanding walk-forward **12m train / 3m val / 3m test, 8 splits, 2023-01..2025-12**.
- **Full grid = 1944 configs (do not shrink):** signal ∈ {`vcl1_dev`,`vcl5_dev`,`vcr_dev`,`vcl1_placebo`,`vcl5_placebo`,`vcr_placebo`} × lookback ∈ {60,120,240,480,960,1920} bars × rebalance ∈ {1bar,4bar,12bar} × fee ∈ {0.0004,0.0007,0.0010} × slip ∈ {0,0.0001,0.0002} × cost_variant ∈ {taker,maker_blend}.
  - **Grid arithmetic:** 6 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants = **1944** configs. Do NOT re-derive with a different cardinality; if runner produces ≠1944, fix the grid, not the artifact.
  - **Signal definitions:** `vcl1_dev`/`vcl5_dev`/`vcr_dev` = seasonal dislocation of vcl1/vcl5/vcr; `vcl1_placebo`/`vcl5_placebo`/`vcr_placebo` = seasonal dislocation of recorded-seed phase-randomized surrogates (same marginal distribution, destroys temporal alignment) — attribution placebos, NOT real signals, never edges.
  - **Attribution accounting:** per-signal OOS mean edge share across 1944; dominant share must be a REAL (non-`placebo`) signal AND ≥0.5 for `attribution_ok:true`. Placebo-dominant → `attribution_ok:false`. Placebos reported in `attribution_shares` but never counted as edges.
  - **No fabrication guard:** every artifact carries `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; only RNG is recorded-seed placebo phase randomization (documented, not market data).
- Gates: Holm+BH α=0.05 (both), MDE, stability, signal-vs-placebo. Attribution shares vs placebos; dominant real signal ≥0.5 for `attribution_ok`.
- Provenance on every artifact: `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, source=C312 5m, timestamps, SHAs.

**Execution order (complete ALL in this session, in order — do not stop after any single step):**
1. `scripts/build_c343_volatility_clustering_features.py` → build `data/cache/campaign343_volatility_clustering_5m/` read-only from C312 (idempotent, fail-closed NaN, assert cache < 100 MB). Shards hold `index_ms, perp_close, log_return, abs_ret, sq_ret, funding_rate` (funding all-NaN control-only).
2. `scripts/preflight_c343.py --json` → must print `ready:true`, `blocked_reasons:[]` (verify 10/10 shards, 315,648 bars, 2023-01..2025-12 window).
3. `scripts/run_c343_volatility_clustering_xsec_oos.py` → **full 1944-config** expanding-WF costed OOS sweep on real 5m data (bounded memory, gitignored `.full.json` if large).
4. `tests/test_preflight_c343.py` + `tests/test_c343_volatility_clustering_xsec_oos.py` → `python -m pytest tests/test_preflight_c343.py tests/test_c343_volatility_clustering_xsec_oos.py -q` green.
5. Emit 5 artifacts `reports/campaign343_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>Z.json` + gitignored `.full.json`, SHA256-from-bytes.
6. Update `AGENTS.md` + `research_state/state.yaml`: record C343 result (formal negative or otherwise, truthfully) and set next active campaign to C344.

If a step fails, fix and continue. Only stop the family if on-disk data proves it unreachable — record evidence and proceed to C344 in the same session.

**Definition of done:** real C343 cache + ready preflight + 1944-config real-data costed-OOS sweep + 5 SHA256 artifacts + passing C343 tests + handoff/state updated. Anything less is incomplete.
