## READ THIS FIRST — C103 INITIAL TASK (20261106T202424Z, produced by C102 execution agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #103 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule below.

### C102 state (reference; do not rerun unchanged)
- **Env/pytest OK.** C102: **928 passed, 1 skipped, 0 failed, rc=0, 3562 warnings, ~48s** (`.venv/bin/python -m pytest -q`).
- **C102 R-B executed (VOLUME_APEN_SHOCK_MR, Approximate Entropy of log-volume changes, m=2 r=0.2*std; vector-regularity entropy distinct from permutation/sample/shannon/renyi block-frequency entropies):** `reports/real_quote_volume_approximate_entropy_shock_mr_costed_oos_20261106T201839Z.json` (sha256 `0a344a04425f075fa3fd2f3122091d747e9243edf0842488f8497d905782cc41`) — `oos_edge_proven=false`, n_assets=11, any_exposure=true, all_pos=false, beats_bh=false. Cross-asset OOS net sums negative at all cost slices (fee0 -1.350 … fee40 -16.182); mean OOS net (-0.000309 … -0.003705) below mean B&H OOS mean (+1.438e-05). No edge. Bottleneck fixed: volume now pivoted long->wide so all 11 spot-cache assets process (prior C101 DFA ran n_assets=0 due to un-pivoted long frame).
- **C102 ingest attempt:** `reports/real_feed_ingest_attempt_20261106T202242Z.json` (sha256 `440a0e62bb1e7529987accdf5a9a5b4012d678e82c3f1f59cfb0c02b0c59a69d`) — `IMPOSSIBLE_WITH_AVAILABLE_REAL_ARTIFACTS_FAIL_CLOSED` for `cross_exchange_dual_venue_same_asset` (a different blocked family than C101's `funding_basis_carry`); no real nonspot artifacts in `data/cache`/workspace; operator must place real artifact. Cache audit + unblock status also emitted (`reports/real_feed_cache_audit_102_20261106T202242Z.json`, `reports/real_feed_unblock_status_102_20261106T202242Z.json`); unblock delta unchanged (still blocked).
- **Latest registry/summary (C102):** `reports/strategy_edge_registry_20261106T202343Z.json` (sha256 `ce1d2d411542eaad47c2829b5983a89f007bef277f631c7ebd86927be0b9b0c5`), `reports/campaign102_execution_summary_20261106T202343Z.json` (sha256 `affb42a18d054bcce0918cae03846497a1ee9cd8a75399685cbbfc82490e6d7`).
- **Feed status (reference only, NO rescan):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80`) — 4 families blocked (`funding_basis_carry`, `cross_exchange_dual_venue_same_asset`, `term_structure_real_iv_vol_surface`, `intrabar_microstructure`); only `real_quote_volume` validated.

### PRIMARY BLOCKERS — REMOVE NOW (hard requirements)
1. **Nonspot ingest still blocked.** If a real nonspot feed artifact becomes available, ingest it into `data/cache/` with fail-closed provenance/meta for exactly one blocked family and run loader/unblock audit for that family. If impossible, emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence. Do not fabricate. Do not rescan stale cache as new edge work.
2. **Execute C103 R-B — genuinely distinct candidate (MANDATORY).** Pre-state a candidate mechanically distinct from ALL prior RQV families (C23/C40–C100: location/dispersion/skew/kurtosis/TP/runs/mean-run-length/VR/BDS/OU-HL/LZ76/Hjorth/Higuchi/Katz/TKEO/Petrosian-FD/ZCR/entropy/ACF variants already tested as applicable; C101 DFA; C102 Approximate Entropy). Suggested C103 candidate: `VOLUME_SPECTRAL_ENTROPY_SHOCK_MR` (spectral/power-spectral-density distribution entropy of log-volume changes — frequency-domain entropy, distinct from all time-domain entropies tested). FIRST run `grep -rn "<candidate_tokens>" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py`; must be empty before implementation. Implement `scripts/run_real_quote_volume_<candidate>_shock_mr_costed_oos.py`, run with exact fail-closed edge rule/WF/cost/B&H, produce `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json`. Do NOT rerun C100/C101/C102 scripts unchanged.
3. **Rerun pytest** if code/scripts changed in a way that affects tests; record authoritative counts/rc in new registry.
4. **Emit >=3 new concrete reports artifacts this session.** Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C103 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_<candidate>_shock_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence with concrete reason)
- `reports/strategy_edge_registry_<UTC>.json` (superseding `reports/strategy_edge_registry_20261106T202343Z.json`; include pytest counts/rc)
- `reports/campaign103_execution_summary_<UTC>.json`

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no C23/C40–C102 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T202343Z.json` in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
