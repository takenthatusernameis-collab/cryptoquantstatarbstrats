## READ THIS FIRST — C104/C105 INITIAL TASK (20261106T211643Z, produced by handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C103 DONE: `VOLUME_SPECTRAL_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_spectral_entropy_shock_mr_costed_oos_20261106T204151Z.json`, `oos_edge_proven=false`. Latest registry `reports/strategy_edge_registry_20261106T204555Z.json`. pytest: 928 passed / 1 skipped / 0 failed, rc=0.
- C104 `VOLUME_WAVELET_ENTROPY_SHOCK_MR` (wavelet packet/continuous wavelet energy-distribution entropy over scales): NOT on disk — no `wavelet_entropy` script or report. Execute it FIRST as the C104 deliverable before C105 R-B.
- C105 `VOLUME_HURST_RS_PERSISTENCE_MR` (rescaled-range Hurst exponent / long-memory persistence over rolling windows; distinct from variance-ratio/OU-halflife/DFA/Higuchi/Petrosian/Katz fractal candidates): NOT on disk — no `hurst_rs_persistence` script or report. Execute as C105 R-B after C104.
- Nonspot ingest: `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT` (families: funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure). Does NOT block R-B. Emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence if no real nonspot artifact appears in `data/cache/` with .meta.json + .provenance.json; else ingest exactly one blocked family.

### NEXT FOCUS CAMPAIGN — C104 THEN C105 (mandatory, heavy work)
Run in this order. Do not skip to C105 without C104 unless the C104 report already exists.

Step 1 — C104 R-B `VOLUME_WAVELET_ENTROPY_SHOCK_MR`:
- grep-verify absent before implementation (`wavelet_entropy` not in prior real_quote_volume costed OOS reports/scripts).
- Implement `scripts/run_real_quote_volume_wavelet_entropy_shock_mr_costed_oos.py`.
- Run exact fail-closed rule / WF / cost / B&H: WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
- Produce `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_<UTC>.json`.

Step 2 — C105 R-B `VOLUME_HURST_RS_PERSISTENCE_MR`:
- grep-verify absent before implementation (`hurst_rs_persistence` not in prior real_quote_volume costed OOS reports/scripts; distinct from existing `hurst_exponent_shock_mr`).
- Implement `scripts/run_real_quote_volume_hurst_rs_persistence_mr_costed_oos.py`.
- Run exact fail-closed rule / WF / cost / B&H (same params as Step 1).
- Produce `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_<UTC>.json` (or fail-closed blocker evidence).

Step 3 — Registry + ingest + pytest:
- Emit `reports/real_feed_ingest_attempt_<UTC>.json` (concrete nonspot evidence).
- Rerun pytest if code changed; record counts/rc.
- Emit `reports/strategy_edge_registry_<UTC>.json` (superseding `20261106T204555Z`; include C104+C105 results and pytest counts/rc).
- Emit `reports/campaign104_execution_summary_<UTC>.json` and `reports/campaign105_execution_summary_<UTC>.json`.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- No status summary before >=3 new concrete reports artifacts.
- Heavy work mandatory: implement + run + artifact emission; no status-only replies.

### Bottlenecks removed
- Nonspot ingest blocker does NOT block R-B: proceed on `real_quote_volume` family (wavelet_entropy C104, hurst_rs_persistence C105) without waiting for nonspot unblock.
- C104 is the hard prerequisite to C105: execute C104 first; only then C105.
