## READ THIS FIRST — C104 INITIAL TASK (20261106T205038Z, produced by C104 execution agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #104 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule below. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; C104 R-B proceeds on the validated `real_quote_volume` family regardless and does not depend on nonspot unblock.

### C103 state (done; do not rerun unchanged)
- **Env/pytest (post-C103).** Registry shows C103 pytest run context; see `reports/strategy_edge_registry_20261106T204555Z.json`. C102: 928 passed, 1 skipped, 0 failed. C103 registry: passed 928, skipped 1, failed 0, rc 0.
- **C103 R-B executed (VOLUME_SPECTRAL_ENTROPY_SHOCK_MR):** `reports/real_quote_volume_spectral_entropy_shock_mr_costed_oos_20261106T204151Z.json` (sha256 `f648e6f42a33808773bdcb41fd3f1bbcdc12c351235d92318cbc3ea5224d4c58`) — `oos_edge_proven=false`.
- **C103 ingest attempt:** `reports/real_feed_ingest_attempt_20261106T204259Z.json` — `IMPOSSIBLE_WITH_AVAILABLE_REAL_ARTIFACTS_FAIL_CLOSED` for blocked nonspot families; no new real nonspot artifacts found; operator must place real artifact.
- **Latest registry/summary (C103):** `reports/strategy_edge_registry_20261106T204555Z.json` (sha256 `e0131d92a11e592e498118cfc80a0e47299adc455c0918841675b936440c59dd`), `reports/campaign103_execution_summary_20261106T204711Z.json` (sha256 `669331da00c3b5c61071bd78330cbd3ecbf3b68fbb2fff51101e46c8e6632e30`).
- **Feed status (reference):** `reports/real_feed_unblock_status_20261106T130243Z.json` (sha256 `49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80`) — 4 families blocked, only `real_quote_volume` validated.

### PRIMARY BLOCKERS — REMOVE NOW (hard requirements)
1. **Nonspot ingest still blocked.** If a real nonspot feed artifact becomes available in `data/cache/` (with matching .meta.json + .provenance.json, fail-closed schema), ingest exactly one blocked family and run loader/unblock audit. If impossible, emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence; do not fabricate/rescan stale cache. This does NOT block C104 R-B on `real_quote_volume`.
2. **Execute C104 R-B — genuinely distinct candidate (MANDATORY).** Candidate `VOLUME_WAVELET_ENTROPY_SHOCK_MR` (wavelet packet/continuous wavelet energy-distribution entropy over scales; time-frequency entropy distinct from periodogram PSD/spectral entropy). grep-verified absent: `grep -rn "wavelet" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py` returns empty. Implement in `scripts/run_real_quote_volume_wavelet_entropy_shock_mr_costed_oos.py`, run with exact fail-closed rule/WF/cost/B&H, produce `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_<UTC>.json`. Do NOT rerun C23/C40–C103 unchanged.
3. **Rerun pytest** if code/scripts changed in a way that affects tests; record authoritative counts/rc in new registry.
4. **Emit >=3 new concrete reports artifacts this session.** Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C104 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence with concrete reason)
- `reports/strategy_edge_registry_<UTC>.json` (superseding `reports/strategy_edge_registry_20261106T204555Z.json`; include pytest counts/rc)
- `reports/campaign104_execution_summary_<UTC>.json`

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no C23/C40–C103 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T204555Z.json` in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
