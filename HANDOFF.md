## READ THIS FIRST — C101 INITIAL TASK (20261106T174241Z, produced by C100 execution agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #101 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule below.

### C100 state (reference; do not rerun unchanged)
- **Env/pytest OK.** C100: **928 passed, 1 skipped, 0 failed, rc=0, 3565 warnings, ~48s** (`.venv/bin/python -m pytest -q`).
- **C100 R-B executed (Zero-Crossing Rate ZCR, VOLUME_ZCR_SHOCK_MR, distinct pre-stated/grep-verified `zero_crossing|zcr_shock|rolling_zcr|ZCR|sign_change_rate_x|volume_zcr` absent pre-impl):** `reports/real_quote_volume_zcr_shock_mr_costed_oos_20261106T174105Z.json` (sha256 `c3caf4dfdf66fedfb522f61233172c541f6cae7852c78173c6a41156bbc55951`) — `oos_edge_proven=false`, n_assets=11, any_exposure=true, all_pos=false, beats_bh=false. No edge. Distinct from C99 PFD (sign changes in first differences d1→FD) — ZCR counts sign changes of series x itself (zero-crossing rate).
- **C100 ingest attempt:** `reports/real_feed_ingest_attempt_20261106T174241Z.json` (sha256 `48e360a6bb61bac14e0ed7942f325168976b8e188df0b491460081168f4fe1b6`) — `IMPOSSIBLE_WITH_AVAILABLE_REAL_ARTIFACTS_FAIL_CLOSED` (no real nonspot artifacts in `data/cache`/workspace); operator must place real artifact.
- **Latest registry/summary (C100):** `reports/strategy_edge_registry_20261106T174241Z.json` (sha256 `28ae0a7bc9b11afd145f43907f70f464d2a41e76168fb24a6edeeebbf0e8dd3d`), `reports/campaign100_execution_summary_20261106T174241Z.json` (sha256 `e313c0a6c5047ba1ed459a337dc2fb577be703606999ea9f755e62b6087d7adb`).
- **Feed status (reference only, NO rescan):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80`) — 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`); only `real_quote_volume` validated.

### PRIMARY BLOCKERS — REMOVE NOW (hard requirements)
1. **Stale cache blocks nonspot path.** If a real nonspot feed artifact becomes available, ingest it into `data/cache/` with fail-closed provenance/meta for exactly one blocked family and run loader/unblock audit for that family. If impossible, emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence. Do not fabricate. Do not rescan stale cache as new edge work.
2. **Execute C101 R-B — genuinely distinct candidate (MANDATORY).** Pre-state a candidate mechanically distinct from ALL prior RQV families (C23/C40–C100: location/dispersion/skew/kurtosis/TP/runs/mean-run-length/VR/BDS/OU-HL/LZ76/Hjorth/Higuchi/Katz/TKEO/Petrosian-FD/ZCR/entropy/ACF variants already tested as applicable). FIRST run `grep -rn "<candidate_tokens>" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py`; must be empty before implementation. Implement `scripts/run_real_quote_volume_<candidate>_shock_mr_costed_oos.py`, run with exact fail-closed edge rule/WF/cost/B&H, produce `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json`. Do NOT rerun C100 ZCR or prior scripts unchanged.
3. **Rerun pytest** if code/scripts changed in a way that affects tests; record authoritative counts/rc in new registry.
4. **Emit >=3 new concrete reports artifacts this session.** Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C101 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence with concrete reason)
- `reports/strategy_edge_registry_<UTC>.json` (superseding `reports/strategy_edge_registry_20261106T174241Z.json`; include pytest counts/rc)
- `reports/campaign101_execution_summary_<UTC>.json`

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no C23/C40–C100 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T174241Z.json` in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
