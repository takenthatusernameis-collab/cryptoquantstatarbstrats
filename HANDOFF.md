## READ THIS FIRST — C99 INITIAL TASK (20261106T171929Z, produced by C98 handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #99 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule below.

### C98 state (reference; do not rerun unchanged)
- **Env/pytest OK.** `.venv` deps present; pytest rerun C98: **928 passed, 1 skipped, 0 failed, rc=0, 3578 warnings, 50.51s** (record in C99 registry if rerun; else cite).
- **C98 R-B executed (TKEO, VOLUME_TKEO_SHOCK_MR, distinct pre-stated/grep-verified):** `reports/real_quote_volume_tkeo_shock_mr_costed_oos_20261106T171624Z.json` (sha256 `3c83df9c99558664aa6a96538244b15325609f77f92b419f09d018184136ed1a`) — `oos_edge_proven=false`, any_exposure=true, all_pos=false, beats_bh=false. No edge.
- **C98 ingest attempt:** `reports/real_feed_ingest_attempt_20261106T171838Z.json` (sha256 `6bb481f50589ee5c57343f19e7831d087b02fe30a3a95f5a17bcfb71db25c51a`) — impossible on stale cache; operator must place real artifact.
- **Latest registry/summary:** `reports/strategy_edge_registry_20261106T171910Z.json` (sha256 `307e6b43a3d0e176ac2fdba15d7ba40a255e45395eb46262eaf096c1a514005c`), `reports/campaign98_execution_summary_20261106T171929Z.json` (sha256 `a551e5f4c216ea1a834734dc877d05f82c13a15cc124b29632938625320c5530`).
- **Feed status (reference only, NO rescan):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80`) — 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`); only `real_quote_volume` validated.

### PRIMARY BLOCKERS — REMOVE NOW (hard requirements)
1. **Stale cache blocks nonspot path.** If a real nonspot feed artifact becomes available, ingest it into `data/cache/` with fail-closed provenance/meta for exactly one blocked family and run loader/unblock audit for that family. If impossible, emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence. Do not fabricate. Do not rescan stale cache as new edge work.
2. **Execute C99 R-B — genuinely distinct candidate (MANDATORY).** Pre-state a candidate mechanically distinct from ALL prior RQV families (C23/C40–C98: location/dispersion/skew/kurtosis/TP/runs/mean-run-length/VR/BDS/OU-HL/LZ76/Hjorth/Higuchi/Katz/TKEO/entropy/ACF variants already tested as applicable). FIRST run `grep -rn "<candidate_tokens>" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py`; must be empty before implementation. Implement `scripts/run_real_quote_volume_<candidate>_shock_mr_costed_oos.py`, run with exact fail-closed edge rule/WF/cost/B&H, produce `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json`. Do NOT rerun C98 TKEO or prior scripts unchanged.
3. **Rerun pytest** if code/scripts changed in a way that affects tests; record authoritative counts/rc in new registry.
4. **Emit >=3 new concrete reports artifacts this session.** Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C99 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence with concrete reason)
- `reports/strategy_edge_registry_<UTC>.json` (superseding `reports/strategy_edge_registry_20261106T171910Z.json`; include pytest counts/rc)
- `reports/campaign99_execution_summary_<UTC>.json`

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no C23/C40–C98 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T171910Z.json` in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
