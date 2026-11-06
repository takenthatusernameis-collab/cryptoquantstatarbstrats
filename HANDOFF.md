## READ THIS FIRST — C95 INITIAL TASK (20261106T151345Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #95 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Environment READY (`.venv`, pandas/numpy/scipy/scikit-learn/statsmodels/PyYAML/pytest; use `.venv/bin/python`).**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
**Fail-closed, real-data-only stat-arb edge validation** — walk-forward OOS, costed backtests, B&H comparison, full provenance, no fabricated data. Only `real_quote_volume` (`volume_1h_full`, 81792 rows, provenance present) is a validated nonspot feed; 4 nonspot families remain `blocked_no_real_feed`. Edge is claimed ONLY under the exact fail-closed edge rule below; everything else is a null/research outcome.

### C94 state (reference)
- **R-A (reference-only, NO rerun on stale cache):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad…7a6d80`) — `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`. 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`). `real_quote_volume` validated-only. **No new validated nonspot feed; path_r infeasible on stale cache.** Do NOT re-run R-A on the same stale cache.
- **C94 R-B:** `reports/real_quote_volume_hjorth_mobility_shock_mr_costed_oos_20261106T150449Z.json` (sha256 `35aec052…97546`, hypothesis `VOLUME_HJORTH_MOBILITY_SHOCK_MR`) — `oos_edge_proven=false, NO_OOS_EDGE_PROVEN_FAIL_CLOSED` (cross-asset net<0 at 0bps, beats-B&H false).
- **Registry (superseded baseline):** `reports/strategy_edge_registry_20261106T150449Z.json` (sha256 `d4e35f01…add444b5`). pytest `928 passed, 1 skipped, 0 failed, rc=0`.
- **RQV transform families exhausted through C94:** 59 `real_quote_volume_*_costed_oos` reports exist. Coverage includes location (C83–C86), TP (C87), WW runs (C88), mean run-length (C89), VR(q) (C90), BDS (C91), OU/HL (C92), LZ76 (C93), Hjorth Mobility/Complexity (C94), plus dispersion/entropy/skew/kurtosis/ACF/Hurst/OBV/divergence/climax/dryup/illiq/vov etc. **No edge proven.**

### Bottlenecks — REMOVE NOW (hard requirements)
1. **Stale cache blocks nonspot path. PRIMARY BLOCKER.** Do NOT rescan existing cache as "new campaign work". Reference only `reports/real_feed_unblock_status_20261106T130243Z.json`. **Mandatory:** attempt to **discover and ingest a NEW real nonspot feed artifact** into `data/cache/` with fail-closed provenance/meta for **exactly one** of the 4 blocked families (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`). If ingestion is impossible with real artifacts, emit `reports/real_feed_ingest_attempt_<UTC>.json` documenting concrete search paths checked, exact missing artifact(s), checksum/provenance requirements, and the smallest unblocking action. **Do not fabricate.**
2. **RQV transform space exhausted.** C95 R-B **MUST** be a **genuinely distinct** `real_quote_volume` transform **not in C23/C40–C94**. Pre-state mechanical distinctness vs ALL families above before implementation. Do **NOT** rerun any prior transform unchanged. **If you cannot justify distinctness to the letter, DO NOT run it.**
3. **No status-only work.** Emit **>=3** new concrete `reports/` artifacts this session. Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Suggested genuinely-distinct C95 R-B (verify first, do not assume)
**Higuchi Fractal Dimension (HFD) shock mean-reversion on log-volume changes.**
- Compute rolling HFD over W=168, ZLB=168 on `log(volume_{t}) - log(volume_{t-1})` (or equivalent real log-volume change). Use curve-length scaling $L(k) \propto k^{-D}$ over $k=1..k_{max}$; $D \in (1,2)$ is fractal dimension (geometric roughness).
- **Mechanical distinctness (must verify):** geometric curve-length scaling over multiple intervals — **NOT** entropy (no $p\log p$/distribution info), **NOT** LZ76/Hjorth (no phrase parsing / no variance-of-derivative ratio $\sqrt{\mathrm{Var}(\Delta x)/\mathrm{Var}(x)}$), **NOT** BDS/VR/OU-HL (no correlation integral/multi-horizon VR/AR(1) half-life), **NOT** single-lag ACF (uses multi-k scaling), **NOT** runs/TP/mean-run-length, **NOT** Hurst/RS, **NOT** location/dispersion/skew/kurtosis magnitude alone.
- **Verify not duplicated:** grep for `higuchi|hfd|fractal_dimension` across `reports/real_quote_volume_*costed_oos*`. If found or if you deem it insufficiently distinct vs any C23–C94, **do NOT use it** — find another genuinely distinct transform or document why only feed ingestion can produce a new edge.
- Signal: causal z-shock of HFD (fade extremes), MR-style entry/exit with sensible max_hold, same WF/cost/B&H as rule.

### Execute first (heavy work, no avoidance)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
. .venv/bin/activate

# 1) PRE-STATE (mandatory)
# - Confirm real_quote_volume loadable, count existing RQV costed_oos, grep for higuchi/hfd/fractal_dimension
# - Read C94 R-B + registry + unblock status for constraints
# - Justify mechanical distinctness vs ALL C23/C40–C94 in code/comments or artifact

# 2) BOTTLENECK REMOVAL ATTEMPT (mandatory)
# - Attempt to discover/ingest a NEW real nonspot feed into data/cache/ for one of the 4 blocked families
#   with fail-closed provenance/meta. Emit reports/real_feed_ingest_attempt_<UTC>.json

# 3) C95 R-B (mandatory, genuinely distinct)
# - Implement and run ONE genuinely distinct real_quote_volume transform not in C23/C40–C94
# - WF 720/168/168, 0-40bps [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows
# - Fail-closed real loader, exact edge rule. Write script to scripts/ or run inline; emit reports/real_quote_volume_<distinct>_costed_oos_<UTC>.json

# 4) REGISTRY + SUMMARY + TESTS
# - Emit reports/strategy_edge_registry_<UTC>.json superseding reports/strategy_edge_registry_20261106T150449Z.json with real pytest counts/rc and C95 R-B result
# - Emit reports/campaign95_execution_summary_<UTC>.json with >=3 artifacts listed
# - Run full pytest: .venv/bin/python -m pytest tests/ -q (record counts/rc/warnings/time)
```

### C95 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json` — concrete attempt to ingest a NEW real nonspot feed for one of the 4 blocked families (or explicit, evidence-backed impossibility with smallest unblocking steps). **Do not skip.**
- `reports/real_quote_volume_<distinct_transform>_costed_oos_<UTC>.json` — for a hypothesis **not in C23/C40–C94**. Must state mechanical distinctness vs all C23–C94 families and apply exact edge rule.
- `reports/strategy_edge_registry_<UTC>.json` — superseding `reports/strategy_edge_registry_20261106T150449Z.json`, include executed pytest counts/rc, reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/real_quote_volume_hjorth_mobility_shock_mr_costed_oos_20261106T150449Z.json`, and include C95 R-B outcome.
- `reports/campaign95_execution_summary_<UTC>.json` — list >=3 concrete artifacts, bottlenecks addressed/remaining, next concrete action.
- **If truly blocked with no viable distinct RQV transform and no feed ingest possible:** `reports/campaign95_execution_blocker_<UTC>.json` with concrete actions taken, exact missing priors/feeds/artifacts, smallest unblocking steps (still must include feed ingest attempt).

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance.
- No pairs/feed re-scans on the same stale cache as "new campaign work"; no C23/C40–C94 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T150449Z.json` in outputs.
- Pre-state distinctness. If HFD is duplicated or not distinct enough vs prior work, pick another transform or pivot to feed ingestion.
- **No status summary before >=3 new concrete `reports/` artifacts.**
