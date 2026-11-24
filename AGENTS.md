# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-24T07:05:21Z (repo = `cryptoquantstatarbstrats` = crypto quant **stat-arb strategies** → top priority is the next costed OOS stat-arb EDGE campaign; **C422–C429 ALL FROZEN formal negatives** (C429 SIGNENTROPY DONE / RETRACTED 20261124T054818Z, 0 Holm+BH survivors, dominant signentropy_trans_entropy_placebo 0.1691, 44 tests green); **C430 DISTCOR ACTIVE next, placebo seed 20261294**) — **THE ONLY AUTHORITATIVE HANDOFF. There is no HANDOFF.md and none may be created.**

This block is the SINGLE active directive. Everything below the first `---` under it is history/archived evidence only and never overrides this message.

## INITIAL TASK MESSAGE (2026-11-24T05:55:32Z; supersedes every earlier session message; the ONLY active directive)

**PRIORITY (derived from repo name `cryptoquantstatarbstrats` = crypto quant stat-arb strategies): the single most relevant next unit of work is the next pre-registered, fully-costed, real-data-only, walk-forward OOS stat-arb EDGE campaign on the C312 USDT-M 5m `perp_close` universe. C429 SIGNENTROPY is DONE (RETRACTED formal negative). The queue's next such campaign is C430 DISTCOR.**

**NEXT SESSION MUST BUILD C430 DISTCOR END-TO-END — NO EXCEPTIONS, NO STOPPING, NO SHORTCUTS, NO LIGHT-WORK.**

C422–C429 are ALL FROZEN formal negatives (0 Holm+BH survivors, placebos dominate, NO EDGE). The queue advances to **C430 DISTCOR** (placebo seed **20261294**): a genuinely-new price-only, volume-free, close-only kernel on real C312 `perp_close` measuring **nonlinear (in)dependence via distance correlation** `dCor` (Székely–Rizzo–Bakirov 2007). For two equal-length causal series X, Y over a trailing estimation window `window_W = 256`:
  - `a_ij = |X_i - X_j|`, `b_ij = |Y_i - Y_j|`, double-center `A_ij = a_ij - ā_i· - ā_·j + ā_··`, `B_ij = b_ij - b̄_i· - b̄_·j + b̄_··`;
  - `dCov² = mean(A ∘ B)`, `dVar²_X = mean(A ∘ A)`, `dVar²_Y = mean(B ∘ B)`;
  - `dCor = sqrt( dCov² / sqrt(dVar²_X · dVar²_Y) ) ∈ [0,1]`, and `dCor = 0` **iff X ⊥ Y** (captures ALL dependence, linear + nonlinear — unlike Pearson covariance which is blind to nonlinear-only dependence).

**4 KERNEL CONCEPTS** (each seasonally-deviated per `(weekday, time-of-day)` causal bucket, identical mechanism to C422–C429), from causal log-returns `r[t]=log(c[t]/c[t-1])`:
  1. **serial** `dcor_serial_dev` = mean over lags k∈{1,2,4} of `dCor(r[t-k], r[t])` — own nonlinear serial dependence (own returns);
  2. **volatility-clustering** `dcor_volserial_dev` = mean over lags k∈{1,2,4} of `dCor(|r[t-k]|, |r[t]|)` — nonlinear magnitude/volatility-clustering dependence;
  3. **market co-movement** `dcor_market_dev` = `dCor(r_i[t], mkt[t])` where `mkt = mean_i r_i` (equal-weight cross-section) — nonlinear co-movement vs market;
  4. **direction–magnitude coupling** `dcor_signmag_dev` = `dCor(sign(r[t]), |r[t]|)` — contemporaneous nonlinear sign/magnitude coupling.

**GRID (identical structure to C428/C429):** 4 concepts × 2 variants each (dev + matched placebo) = **8 signals** × 6 lookbacks {60,120,240,480,960,1920} × 3 rebalances {1,4,12} × 3 fees {0.0004,0.0007,0.0010} × 3 slips {0.0,0.0001,0.0002} × 2 cost variants {taker, maker_blend} = **2592 literal configs** for the FULL costed OOS sweep. Placebo = recorded-seed (20261294) phase randomization of the real return series only (never market data, never fabricated).

**IMPLEMENTATION NOTE (performance — MUST respect so the heavy build stays feasible):** compute the dCor series ONCE per (concept, asset) over all 315,648 bars (do NOT recompute per lookback; the lookback L only trailing-averages the seasonally-deviated dCor score, exactly as C429 does). Naive per-window `O(window_W²)` distance matrices over 315k bars × 10 assets × 4 concepts are too slow in pure Python — the build MUST use the **fast 1D sliding-window distance-covariance algorithm** (Huo–Székely 2016 `O(window_W log window_W)`) or an equivalent vectorized rolling formulation, and cache per-(signal, lookback) scores. If even the fast form is too slow, the ONLY permitted fallback is reducing `window_W` 256→128 (still heavy, still genuinely-new); NEVER reduce the 2592-config sweep, NEVER switch to synthetic data, and ALWAYS keep the brute-force equality guard against the naive `O(window_W²)` double-centered reference on a small sample.

**KERNEL-DISTINCTNESS (MUST hold, else the campaign is a clone and is void — clone-and-rename campaigns are permanently quarantined):** C430 distance-correlation `dCor` is a strict nonlinear generalization beyond, and is DISTINCT from, every prior linear/sign/spectral/tail family — specifically: `multi_lag_realized_autocovariance_profile`, `normalized_autocorrelation_function_decorrelation_horizon_vs_own_returns`, `sign_sequence_autocorrelation_profile_vs_own_returns`, `signed_conditional_lag_covariance`, `average_pairwise_cross_correlation_profile` (all Pearson/linear, =0 under nonlinear-only dependence); `cross_sectional_co_skewness_co_kurtosis` (3rd/4th moments); `sign_agreement_motion` (sign-only); `tail_dependence_coefficient` (extremal only); `spectral_coherence` (frequency-domain linear); `realized_time_irreversibility` cumulants / XSKew3; `transfer_entropy` (conditional/directional vs dCor unconditional/symmetric); `quantile_regression_slope`; `first_order_markov_sign_transition` (C429, transition probabilities); `sign_count Shannon entropy` (C329, bin-based); `permutation entropy` (C349, ordinal); RQA / sample entropy / multiscale entropy (recurrence/neighbor); and every fractal/spectral/vol-of-vol/moment/entropy family C281B–C429. The test file MUST include a kernel-distinctness guard vs ALL of the above AND a brute-force equality check (maxdiff < 1e-12) against an independent double-centered-distance-matrix reference, plus NaN-propagation checks.

**MANDATORY SEQUENCE (execute in order, no stopping):**
```
cp scripts/build_c429_signet_features.py scripts/build_c430_distcor_features.py
cp scripts/preflight_c429.py scripts/preflight_c430.py
cp scripts/run_c429_signet_xsec_oos.py scripts/run_c430_distcor_xsec_oos.py
cp tests/test_preflight_c429.py tests/test_preflight_c430.py
cp tests/test_c429_signet_xsec_oos.py tests/test_c430_distcor_xsec_oos.py
# edit each copied file: replace order-1 Markov sign-transition logic with distance-correlation (dCor) logic;
# change all 429/signet/signentropy/SIGNENTROPY/20261293 self-references, cache dir -> data/cache/campaign430_distcor_5m, seed -> 20261294, signals -> 8 (4 dev + 4 placebo)
# grep self-check MUST return NOTHING for 429/signet/signentropy/SIGNENTROPY/20261293 in scripts/*c430* tests/*c430* (apart from legitimate distinctness-guard refs to prior families)
python3 scripts/build_c430_distcor_features.py -> data/cache/campaign430_distcor_5m/ (10 shards + meta + provenance)
python3 scripts/preflight_c430.py -> ready:true
python3 scripts/run_c430_distcor_xsec_oos.py (FULL literal 2592-config costed OOS sweep)
python3 -m pytest tests/test_preflight_c430.py tests/test_c430_distcor_xsec_oos.py -q (>=21 green incl brute-force dCor equality maxdiff < 1e-12 + kernel-distinctness guards vs ALL prior families)
sha256sum reports/campaign430_*_<TS>Z.json (record all 5 artifact SHAs: oos_sweep, tradable_edge_registry, summary, verdict, binding_constraint)
```

**SESSION COMPLETION CRITERIA (NO-LIGHT-WORK RULE):** The session is complete ONLY when it produces: 3 scripts + 2 test files + cache (10 shards + meta + provenance) + preflight ready:true + FULL 2592-config costed OOS sweep + 5 SHA256 report artifacts + ≥21 green tests (incl. brute-force dCor equality maxdiff < 1e-12 + kernel-distinctness guards vs ALL prior families) + truthful RESULT + SHAs recorded in THIS file AND research_state/state.yaml + queue advanced to C431. If the session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.

**ENVIRONMENT (verified 2026-11-24T05:55:32Z):** C312 source intact at `data/cache/campaign312_usdt_m_ofi_5m/` (10 × 315,648-bar `perp_close` shards + manifest). numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. Console scripts at `/home/runner/work/_temp/kilo-home/.local/bin` (NOT on PATH) → always `python3 -m pytest`, never bare `pytest`. BOTTLENECKS: NONE. C429 suite re-run this session = **44 passed in 45s**, confirming the environment is healthy. Session wrapped in `timeout ... 15107s` (~4.2 h) + 15 min idle kill. Prior single-campaign sweeps ran ~2 min end-to-end (build ~40 s + sweep ~60 s + tests ~26–45 s); C430 build+sweep+tests expected well within limits IF the fast distance-covariance algorithm above is used.

**QUARANTINE (re-verified + RE-APPLIED this session 2026-11-24T05:55:32Z):** all 9 `archive/void_*` dirs (void_c381, void_c398_clone, void_c402_clone, void_c402_clone_cache_meta, void_c402_reclone, void_c403_clone, void_c409_leadlag_clone, void_c409_reclone, void_c416_dcbeta_stray) were re-verified READ-ONLY (`dr-xr-xr-x`, owner-write cleared) this session — quarantine intact. NOTE: git tracks only the executable bit, NOT write bits, so a fresh `git checkout` restores default umask and these dirs become writable again — the next session MUST re-run `chmod -R a-w archive/void_*` if it finds any `archive/void_*` writable, and treat quarantine as a POLICY regardless: **never copy/import/cite/fix/freeze/re-run anything under `archive/void_*`** (these are permanently-void clone traps; clone-and-rename campaigns are voided). Live tree verified clean (zero `dcbeta` references under scripts/tests/reports/data/cache; real C416 QREG intact).

**SESSION LIMITS:** whole `kilo run` wrapped in `timeout ... 15107s` (~4.2 h) + `kilo-idle-timeout.py --idle-timeout-seconds 900` (15 min idle). Any blocking wait MUST be < 15 min or the session is killed. If the session dies before the sweep finishes, the NEXT session must re-run it (no shortcut that preserves exactness).

**DISK TRUTH:** C281B–C429 ALL FROZEN formal negatives, NO EDGE through C429. **C429 SIGNENTROPY = COMPLETE_FORMAL_NEGATIVE** (RETRACTED 20261124T054818Z; 2592 configs; 0 Holm+BH survivors; binding multiple_testing; dominant signentropy_trans_entropy_placebo / share 0.1691 [<0.50, attribution_ok false, placebos dominate]; 44 tests green incl brute-force order-1 Markov transition-matrix equality maxdiff<1e-12 + kernel-distinctness guards vs C329/C328/C422/C423/C424/C426/C358/C425/C349/C356/C355/C428). C429's 5 artifact SHAs + cache SHAs are recorded in `research_state/state.yaml` → `c429_status` (artifacts_ts 20261124T044940Z; a 20261124T054818Z re-run reproduced the identical RETRACTED verdict). C312 source intact (10 × 315,648 bars, `perp_close` only). Environment ready. All `archive/void_*` dirs re-quarantined read-only this session — never copy/import/cite/fix/freeze/re-run. C287 permanently decoupled/blocked — never retry. BOTTLENECKS: NONE. No blocked sessions; no clone traps live on disk. Queue depth never runs dry.

**C429 RESULT (frozen — do not re-run; for record):**
  - verdict RETRACTED, edge_proven false, binding multiple_testing, n_survive_holm=0, n_survive_bh=0, n_survive_both=0
  - dominant attribution signentropy_trans_entropy_placebo (share 0.1691), attribution_ok false
  - artifacts (20261124T044940Z): oos_sweep 2bb0f97c877d1a78005b225e819c69c050db562f83005c9f45411815e7046e4c; tradable_edge_registry 3594b30a1f0f01d61de58f29fefbaf29536cf859abc6049fbe522db0ce4592df; summary f1d7766169836d8e83a62922a78ed880fc6d119150d4aa530212ab86d210545a; verdict dcdbf743f07936b74118345ab116b660ed909d1050d1d865b38832a7091cef72; binding_constraint dd4e9a3e972a1424cd2099096eb4601ac1c4e2bf64c6b7ba217130b79ac1d661
  - cache SHAs: meta 569f13bc820d0b52483b7d59927e7ac8aea27fb5b8295b519067d8be1a18ca4b; provenance e92774641ade55791ac2fdfccb9b0ef4764197edfb6d58fbe03967883b550a9d; manifest ed77576cbee8a1579f080428750c6a40b6f45488cc818c22d2971a97eb00479f

**NO-LIGHT-WORK RULE:** a session is complete only when it produces 3 scripts + 2 test files + cache + preflight ready:true + the FULL literal-2592-config costed OOS sweep + 5 SHA256 reports + ≥21 green tests incl. brute-force dCor equality, then records the truthful RESULT + SHAs in this file and research_state/state.yaml and moves the queue forward (C430 → C431). If a session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.
---