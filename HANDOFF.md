## READ THIS FIRST — C96 INITIAL TASK (20261106T152510Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #96 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`; use `.venv/bin/python`, pytest 9.2.0). Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance validated) is a nonspot feed with provenance; 4 families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below.

### C95 state (reference, do not rerun unchanged)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked: `funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`. `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** Do NOT re-run R-A on the same stale cache.
- **C95 feed ingest attempt (mandatory bottleneck removal):** `reports/real_feed_ingest_attempt_20261106T151639Z.json` (sha256 `ae847078…`) — `NO_NEW_REAL_NONSPOT_FEED_INGESTED_FAIL_CLOSED`. Cache/workspace searched (pytest tmp/.venv/__pycache__/tests excluded); no real deployable artifacts for the 4 blocked families in `data/cache`. Smallest unblocking action: operator/ingestion must place a real artifact with full fail-closed provenance+sha256 satisfying the family spec (e.g. `FUNDING_BASIS_CARRY_SPEC`) in `data/cache`, then re-run `generate_unblock_status_report`/audit.
- **C95 R-B (genuinely distinct):** `reports/real_quote_volume_higuchi_fd_shock_mr_costed_oos_20261106T151757Z.json` (sha256 `13b30af3…`, hypothesis `VOLUME_HIGUCHI_FD_SHOCK_MR`) — rolling Higuchi Fractal Dimension (geometric curve-length scaling `L(k)~k^{-D}`, multi-interval k resampling, `log(L)-log(1/k)` slope, W=168,k_max=8,ZLB=168) of log-volume changes as MR shocks. Distinct vs C94 Hjorth (derivative variance ratios), Hurst/RS, entropy, LZ76, WW-runs/mean-run-length/TP, BDS, VR, OU/HL, single-lag ACF, location/dispersion/skew/kurtosis. **Result:** `oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED` (0bps net +2.02; 5–40bps cross-asset net sums negative; beats-B&H false). 11 assets, WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Registry (supersedes C94):** `reports/strategy_edge_registry_20261106T151843Z.json` (sha256 `6ca9ab15…`) — supersedes `reports/strategy_edge_registry_20261106T150449Z.json`. **pytest:** `928 passed, 1 skipped, 0 failed, rc=0` (3570 warnings, 56.70s).
- **RQV transform families exhausted through C95 (no edge proven):** 60 `real_quote_volume_*_costed_oos` reports. Coverage includes location/dispersion/shape/entropy/complexity/persistence/timescale/geometric-roughness families incl. Shannon/perm/sample/Renyi2 entropy, spectral entropy, LZ76, Hjorth Mobility, Higuchi FD, Hurst/RS, BDS, VR(q), OU/HL, WW runs, mean run-length, **turning-point rate** (`reports/real_quote_volume_turning_point_rate_shock_mr_costed_oos_20261106T122053Z.json`, `TP=(1/(n-2))*sum I[(x_i-x_{i-1})*(x_{i+1}-x_i)<0]`), single/lead ACF variants, OBV/divergence, climax/dryup/illiq/vov, etc. **No OOS-proven edge.**

### Bottlenecks — REMOVE NOW (hard requirements)
1. **Stale cache blocks nonspot path. PRIMARY BLOCKER.** Do NOT rescan existing cache as "new campaign work". Reference only `reports/real_feed_unblock_status_20261106T130243Z.json`. **Mandatory:** attempt to **discover and ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta for **exactly one** of the 4 blocked families. If impossible with real artifacts, emit `reports/real_feed_ingest_attempt_<UTC>.json` documenting concrete search paths checked, exact missing artifact(s), checksum/provenance requirements, and the smallest unblocking action. **Do not fabricate.**
2. **RQV transform space exhausted through C95.** C96 R-B **MUST** be a **genuinely distinct** `real_quote_volume` transform **not in C23/C40–C95**. **Pre-state mechanical distinctness** vs ALL prior families (incl. TP/turning-point rate, Higuchi, Hjorth, Hurst/RS) **before implementation**. Grep-verify not duplicated across `reports/real_quote_volume_*costed_oos*` and relevant scripts. Do **NOT** rerun any prior transform unchanged. **If you cannot justify distinctness to the letter, DO NOT run it.**
3. **No status-only work.** Emit **>=3** new concrete `reports/` artifacts this session. Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C96 R-B — required distinct transform (verify mechanically, then implement)
**Primary candidate: Katz Fractal Dimension (KFD) shock mean-reversion on log-volume changes** (planar-curve length vs max diameter self-similarity).
- Compute rolling Katz FD over W=168, ZLB=168 on `dlogv_t = log(v_t)-log(v_{t-1})` (real log-volume changes). Katz FD = `log10(n-1) / (log10(n-1) + log10(d/a))` where `L = sum sqrt(1 + (x_i-x_{i-1})^2)` (planar curve length, unit time steps), `a = L/(n-1)`, `d = max_i sqrt(i^2 + (x_i-x_0)^2)` (max diameter from first point). **Document formula/variant and unit-time-step convention; verify numerically on a toy series before full run.**
- **Mechanical distinctness (must grep-verify absent):** uses **total planar curve length + max diameter** (no sign-change counting as the FD input, no multi-interval resampling). **NOT** Higuchi C95 (no k-interval `L(k)` curve-length resampling/scaling slope), **NOT** Hjorth C94 (no derivative variance ratios), **NOT** Hurst/RS (not rescaled-range/long-memory scaling of cumulative deviations), **NOT** turning-point rate (TP counts interior peaks/troughs as a rate statistic `I[(x_i-x_{i-1})*(x_{i+1}-x_i)<0]` — Katz is a length/diameter fractal-dimension value; if implementation reduces to sign-change/TP counting, it is NOT distinct — abort), **NOT** entropy, **NOT** LZ76, **NOT** WW-runs/mean-run-length, **NOT** BDS/VR/OU-HL, **NOT** single-lag ACF, **NOT** location/dispersion/skew/kurtosis.
- **Pre-check (mandatory):** `grep -rn "katz\|kfd\|planar.*fractal\|max_diameter.*fd" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py` must show **no prior Katz/KFD transform**. If found, pick a different genuinely distinct transform (e.g. **Teager–Kaiser energy operator / TKEO shock MR** on log-volume changes — ONLY if `grep -rn "teager\|tkeo" ...` is empty and you document mechanical distinctness vs variance/energy proxies already done: TKEO `psi(x_t)=x_t^2 - x_{t-1}x_{t+1}` is a local instantaneous-energy/nonlinear operator, distinct from variance/dispersion/skew/kurtosis/entropy; verify not duplicated) or document why only feed ingestion can produce a new edge. **Do not run a duplicate.**
- Signal: causal z-shock of transform (fade extremes), MR-style entry/exit, max_hold sensible (e.g. 12h), same WF/cost/B&H as rule.

### Execute first (heavy work, no avoidance)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate

# 1) PRE-STATE (mandatory): loadability, RQV costed_oos count, grep candidate names, read priors, state mechanical distinctness
# 2) BOTTLENECK REMOVAL ATTEMPT (mandatory): attempt real nonspot feed ingest into data/cache/ for one blocked family; emit reports/real_feed_ingest_attempt_<UTC>.json
# 3) C96 R-B (mandatory, genuinely distinct): WF 720/168/168, 0-40bps [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows, fail-closed, exact edge rule
# 4) REGISTRY + SUMMARY + TESTS: registry superseding 20261106T151843Z, summary >=3 artifacts, full pytest
```

### C96 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json` — concrete attempt to ingest a NEW real nonspot feed for one of the 4 blocked families (or explicit, evidence-backed impossibility with smallest unblocking steps). **Do not skip.**
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` — hypothesis **not in C23/C40–C95**. Must state mechanical distinctness vs all C23–C95 families and apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` — superseding `reports/strategy_edge_registry_20261106T151843Z.json`, include executed pytest counts/rc, reference `reports/real_feed_unblock_status_20261106T130243Z.json`, `reports/real_quote_volume_higuchi_fd_shock_mr_costed_oos_20261106T151757Z.json`, and include C96 R-B outcome.
- `reports/campaign96_execution_summary_<UTC>.json` — list >=3 concrete artifacts, bottlenecks addressed/remaining, next concrete action.
- **If truly blocked with no viable distinct RQV transform and no feed ingest possible:** `reports/campaign96_execution_blocker_<UTC>.json` with concrete actions taken, exact missing priors/feeds/artifacts, smallest unblocking steps (still must include feed ingest attempt).

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on the same stale cache as "new campaign work"; no C23/C40–C95 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T151843Z.json` in outputs.
- Pre-state distinctness. TP/sign-change exists as turning-point rate — do NOT repackage it without mechanical proof of distinction.
- **No status summary before >=3 new concrete `reports/` artifacts.**
