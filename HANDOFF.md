## READ THIS FIRST — C98 INITIAL TASK (20261106T171352Z, produced by C97 handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #98 now — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule below.

### C97 state (reference; do not rerun unchanged)
- **Env restored.** `.venv` rebuilt with project deps (pip install -e '.[dev]'); system blockage removed.
- **C97 R-B executed (Katz FD):** `reports/real_quote_volume_katz_fd_shock_mr_costed_oos_20261106T171349Z.json` (sha256 `1e8e553edc21fe528896aa2de2d86a33544b7d83385c22bfcded862f9f44d4ef`) — `oos_edge_proven=false`, any_exposure=true, all_pos=false, beats_bh=false. No edge.
- **Feed status (reference only, no rescan):** `reports/real_feed_unblock_status_20261106T130243Z.json` — 4 families still blocked; only `real_quote_volume` validated.
- **C96 ingest attempt (reference):** `reports/real_feed_ingest_attempt_20261106T170620Z.json` — impossible on stale cache; operator must place real artifact.

### PRIMARY BLOCKERS — REMOVE NOW (hard requirements)
1. **Stale cache blocks nonspot path.** Attempt to discover and ingest a NEW real nonspot feed artifact into `data/cache/` with fail-closed provenance/meta for exactly one of the 4 blocked families. If impossible, emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence. Do not fabricate.
2. **Execute C98 R-B — TKEO candidate (genuinely distinct).** First run `grep -rn "teager\|tkeo" reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py`; must be empty. Implement `scripts/run_real_quote_volume_tkeo_shock_mr_costed_oos.py` with Teager-Kaiser energy operator `psi(x_t)=x_t^2 - x_{t-1}x_{t+1}` on log-volume changes; distinctness pre-stated vs all prior families. Run with exact fail-closed edge rule/WF/cost/B&H. Produce `reports/real_quote_volume_tkeo_shock_mr_costed_oos_<UTC>.json`.
3. **Rerun pytest** after env restore; record counts/rc in new registry.
4. **Emit >=3 new concrete reports artifacts this session.** Produce artifacts before any summary.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid 0–40bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### C98 deliverables (required)
- `reports/real_feed_ingest_attempt_<UTC>.json`
- `reports/real_quote_volume_tkeo_shock_mr_costed_oos_<UTC>.json` (or blocker evidence)
- `reports/strategy_edge_registry_<UTC>.json` (superseding `reports/strategy_edge_registry_20261106T170645Z.json`; include pytest counts/rc)
- `reports/campaign98_execution_summary_<UTC>.json`
- If truly blocked: still produce >=3 artifacts.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no C23/C40–C97 reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if OOS exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and `reports/strategy_edge_registry_20261106T170645Z.json` in outputs.
- Pre-state distinctness; grep-verify not duplicated.
- No status summary before >=3 new concrete reports artifacts.
