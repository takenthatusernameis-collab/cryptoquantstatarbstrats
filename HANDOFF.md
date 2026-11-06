## READ THIS FIRST — C105 INITIAL TASK (20261106T210956Z, produced by C105 handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #105 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### C104 state (expected done by next session; do not rerun unchanged)
- C104 R-B candidate `VOLUME_WAVELET_ENTROPY_SHOCK_MR` (wavelet packet/continuous wavelet energy-distribution entropy over scales). If its report exists, reference it; otherwise execute it first as C104 deliverable before C105 R-B.
- C104 deliverables expected: `reports/real_feed_ingest_attempt_<UTC>.json`, `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_<UTC>.json`, `reports/strategy_edge_registry_<UTC>.json`, `reports/campaign104_execution_summary_<UTC>.json`.
- Latest registry reference: `reports/strategy_edge_registry_20261106T204555Z.json`.

### PRIMARY BLOCKERS — REMOVE NOW
1. Nonspot ingest blocked: if real nonspot artifact appears in `data/cache/` with .meta.json + .provenance.json, ingest exactly one blocked family; else emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence. Does NOT block R-B.
2. Execute C105 R-B — genuinely distinct candidate (MANDATORY). Candidate `VOLUME_HURST_RS_PERSISTENCE_MR` (rescaled-range Hurst exponent / long-memory persistence over rolling windows; distinct from variance-ratio/OU-halflife/DFA/Higuchi/Petrosian/Katz fractal candidates). grep-verify absent before implementation. Implement in `scripts/run_real_quote_volume_hurst_rs_persistence_mr_costed_oos.py`, run exact fail-closed rule/WF/cost/B&H, produce `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_<UTC>.json`.
3. Rerun pytest if code changed; record counts/rc in new registry.
4. Emit >=3 new concrete reports artifacts this session before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C105 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence)
- `reports/strategy_edge_registry_<UTC>.json` (superseding latest; include pytest counts/rc)
- `reports/campaign105_execution_summary_<UTC>.json`

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
- Heavy work mandatory: implement + run + artifact emission; no status-only replies.
