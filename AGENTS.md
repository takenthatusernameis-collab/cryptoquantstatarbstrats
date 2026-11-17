# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-17T04:18:56Z. Repo: cryptoquantstatarbstrats — crypto quantitative **statistical arbitrage**. Economic progress = real-data costed out-of-sample PnL run, passing test, or artifact update. A session that only re-reads this handoff, re-declares closure, or re-runs a frozen campaign is NOT economic progress and is a hard violation.

> **INITIAL TASK MESSAGE (2026-11-17T04:18:56Z, MANDATORY, START HERE — DO NOT RE-READ/PLAN/STOP):** C281B–C343 are ALL COMPLETE FORMAL NEGATIVES on real C312 5m data (~70,000+ pre-registered configs; binding universally `multiple_testing`; `oos_edge_proven:false`, `edge_claim:NONE`). C340 `20261117T032549Z`, C341 `20261117T031751Z`, C342 `20261117T034113Z`, C343 `20261117T041856Z` — all 5 SHA256 artifacts emitted per campaign, 21/21 C343 tests green, all frozen. No costed-OOS edge has ever survived — a RESULT, not permission to stop. **C343 is DONE — COMPLETE FORMAL NEGATIVE** (verdict RETRACTED, binding `multiple_testing`, dominant attribution `vcr_placebo` 0.2445 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`). Scripts/tests/cache/artifacts all on disk under `campaign343_volatility_clustering_5m/`. **C344 is NEXT ACTIVE** — the next genuinely-new stat-arb family on real C312 5m data. Do **not** re-read and stop, re-declare closure, re-run frozen C281B–C343/C287, or regenerate stale closure generators.

**Program state:** `ACTIVE — NO-EDGE CONFIRMED THROUGH C343 (ALL FORMAL NEGATIVES)`. Terminal closure by fiat PROHIBITED: execute every pre-registered genuinely-new family on real on-disk C312 5m data until one is proven unreachable with on-disk evidence. **C337–C343 DONE/frozen; do NOT re-run C281B–C343/C287.**

**Bottlenecks:** **NONE.** C312 5m input data on-disk and sufficient (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 shards × 315,648 bars, 2023-01..2025-12); C337–C343 caches/artifacts on disk; C287 remains externally blocked/decoupled (451/403, no creds) — never retry as economic work. No blocker may defer C344. If runtime deps missing, run `python scripts/bootstrap_dev_env.py` (idempotent) before tests.

**Closure audit (C281B–C318 scope, unchanged):** `reports/program_closure_final_20261116T024519Z.json` (sha256 `aebd52b87b1a44fc61c16d8f020b6b7a1f048b83ac0179ebfc5177e095d78dca`) — `reachable_space: CLOSED` for C281B–C318 only; C319–C343 extend the record. Do NOT regenerate/run stale closure generators.

**Frozen campaigns (do NOT re-run):** C337 `20261116T234925Z` (7776, asym_placebo 0.1957), C338 `20261117T004211Z` (4212, shannon_entropy_placebo 0.1367), C339 `20261117T005324Z` (1944, align_z_placebo 0.4791), C340 `20261117T032549Z` (2592, flow_cv_placebo 0.1803), C341 `20261117T031751Z` (2592, pid_placebo 0.2004), C342 `20261117T034113Z` (2592, kurt_placebo 0.1842), C343 `20261117T041856Z` (1944, vcr_placebo 0.2445). All: 0 Holm+BH, binding `multiple_testing`, RETRACTED, attribution_ok false, 5 SHA256 artifacts + gitignored `.full.json`, tests green. Full per-campaign SHAs cached in `research_state/state.yaml` and `reports/`.

---

## MANDATORY CAMPAIGN — C343: cross-sectional intraday VOLATILITY-CLUSTERING / ABSOLUTE-RETURN AUTOCORRELATION SEASONAL DISLOCATION mean-reversion stat-arb (USDT-M 5m) — COMPLETE / FROZEN

Mechanically distinct from C315–C342:
- C326 measured signed-return autocorrelation (first-moment direction dependence). C343 measures **second-moment dependence**: autocorrelation of `|log_return|` (volatility clustering) — distinct from C326.
- C317 measured realized-vol LEVELS. C343 measures vol CLUSTERING/REGIME-SHIFT vs seasonal baseline — distinct from C317.
- C342 measured volume-weighted return skewness/kurtosis. C343 is unweighted absolute-return dependence — distinct from C342.

**Result (truthful, on-disk):** `20261117T041856Z` — **COMPLETE FORMAL NEGATIVE**. verdict RETRACTED, binding `multiple_testing`, dominant attribution `vcr_placebo` 0.2445 < 0.5 → `attribution_ok:false`; 0 Holm+BH survivors; `edge_proven:false`. Grid executed in full: 1944 configs (6 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost_variants). 8 splits 12m train/3m test, 2023-01..2025-12. 5 SHA256 artifacts emitted + gitignored `.full.json`. 21/21 tests green (`tests/test_preflight_c343.py` + `tests/test_c343_volatility_clustering_xsec_oos.py`). Cache `data/cache/campaign343_volatility_clustering_5m/` (10 shards × 315,648 bars, 49.38 MB < 100 MB, real_data_only). Scripts: `scripts/build_c343_volatility_clustering_features.py`, `scripts/preflight_c343.py`, `scripts/run_c343_volatility_clustering_xsec_oos.py`. **DO NOT RE-RUN.**

---

## NEXT ACTIVE CAMPAIGN — C344: next genuinely-new stat-arb family on real C312 5m data

C344 must be a mechanically-distinct, genuinely-new family NOT re-skinned from C281B–C343. Candidates must be distinct from:
- C326 (signed-return autocorrelation, first-moment) and C343 (abs-return autocorrelation / vol clustering, second-moment)
- C317 (realized-vol LEVELS), C342 (volume-weighted return skewness/kurtosis)
- C340 (activity-magnitude CV dispersion), C341 (price-impact dispersion / vwvol)

The next session MUST:
1. Define and pre-register the C344 spec (signals, lookbacks, grid, gates) in this AGENTS.md section.
2. Implement `scripts/build_c344_*_features.py`, `scripts/preflight_c344.py`, `scripts/run_c344_*_xsec_oos.py` from the pre-registered spec.
3. Implement `tests/test_preflight_c344.py` + `tests/test_c344_*_xsec_oos.py`.
4. Run build → preflight → full costed-OOS sweep → pytest → 5 SHA256 artifacts.
5. Record truthful result (formal negative or edge) in AGENTS.md + `research_state/state.yaml`; set C345 next.

Do **not** declare terminal closure by fiat. Keep executing pre-registered genuinely-new families on real on-disk C312 5m data until one is proven unreachable with on-disk evidence.
