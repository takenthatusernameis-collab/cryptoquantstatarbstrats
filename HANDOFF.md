## READ THIS FIRST — C78 INITIAL TASK (20261106T095925Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #78 now — no investigation-only work.**

### State (verified this session)
- **C77 not started** (C76 just completed at ~09:55Z). Previous campaign C76: `oos_edge_proven=false`. Latest registry: `reports/strategy_edge_registry_20261106T095532Z.json` (superseded prior). Latest unblock status: `reports/real_feed_unblock_status_20261106T095526Z.json` (blocked, delta vs prior unchanged).
- **C76 R-B (real_quote_volume, 11 assets, 5112 bars, WF 720/168/168, cost 0–40bps, B&H same windows):** "Volume Theil L (GE(0) Mean-Log Deviation) Inequality Shock Mean Reversion" — rolling Theil L / GE(0), ZLB=168, fade shocks |d_z|>=1.25, exit |d_z|<0.25/hold>=12/flip. Aggregate OOS net negative across all costs (0@-0.229 down to 40@-1.427), not beating B&H. `oos_edge_proven=false`. Artifact: `reports/real_quote_volume_theil_l_ge0_mld_shock_mr_costed_oos_20261106T095525Z.json`.
- **Blocked families (substantive):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure` — `blocked_no_real_feed`. No proxies labeled real. No fabricated feeds/provenance.
- **`real_quote_volume` heavily exhausted:** C23 and C40–C76 tested (38 hypotheses). Current cache validated. Any R-B must be genuinely distinct from all prior.
- **Infra:** full suite green at C76 end (`928 passed, 1 skipped, 0 failed` rc=0).

### Bottlenecks to remove now
- **Primary:** Find/generate a genuinely NEW real feed for any of the 4 blocked families with complete provenance (source, schema, tz, granularity, window, checksum/ingest log) passing fail-closed validation, OR produce a truly novel R-B on `real_quote_volume` not seen in C23/C40–C76.
- **Secondary:** Eliminate any "analysis-only" path — if no unblocking artifact is possible this session, you MUST take the smallest concrete unblocking step (e.g., fix ingestion/loader to accept a real source format, add validated adapter, or surface exact missing fields with a runnable script/patch) and still emit `>=3` artifacts.
- **Tertiary:** Prevent zero-artifact sessions. Every session must produce concrete, tested artifacts (not just logs).

### Do now (>= 3 new `reports/` artifacts)
**R-A preferred** — if any blocked family has a new real feed discoverable/constructible from existing validated sources or new real data with full provenance:
1. Run fail-closed validation (prove real, no proxy labeled real, complete provenance) → `reports/<family>_real_feed_validation_<UTC>.json` (with checksums/source/loader)
2. Costed OOS if tradable on that feed, else justified feasibility + concrete adapter: `reports/<family>_<strategy>_costed_oos_<UTC>.json` OR `reports/<family>_feed_feasibility_<UTC>.json` with concrete next steps
3. Unblock status delta: `reports/real_feed_unblock_status_<UTC>.json` via `generate_unblock_status_report(..., campaign=78, prior_report='reports/real_feed_unblock_status_20261106T095526Z.json')`
4. Registry supersede: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T095532Z.json` with pytest rerun counts

**R-B if R-A impossible** — pre-state a genuinely distinct hypothesis on `real_quote_volume` (transform/mechanic not in C23/C40–C76; e.g. different shock definition/window/normalizer/exit regime filter not used). Produce:
1. Tested runner/script that implements ONLY that hypothesis
2. `reports/real_quote_volume_<hyp>_costed_oos_<UTC>.json` with WF 720/168/168, cost grid 0–40bps, B&H same windows, full traceability to code
3. Unblock status + registry as above

**Blocker fallback (only if neither possible after taking concrete action):**
- `reports/campaign78_execution_blocker_<UTC>.json` with: exact missing priors (files/fields/sources), smallest concrete unblocking step taken THIS session (diffs/commands/scripts added), candidate real sources checked with evidence, and a single actionable next command/blocker to resolve
- Still must include unblock status + registry + >=1 more concrete artifact (e.g., feasibility scan with evidence)

### Mandatory rules (hard)
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C76 reruns unchanged; no gate weakening; no proxies labeled real; no fabricated feeds/provenance.
- Edge claim ONLY if exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows.
- Rerun `python -m pytest tests/ -q` and record counts in new registry.
- Real data only. Fail-closed always.
- >=3 new concrete artifacts in `reports/` every session. Zero-artifact/investigation-only = failure.

### Anti-evasion
- "Tried to look" is not enough — produce code/artifacts or a blocker with concrete action taken.
- Must not copy C76 hypothesis verbatim; must justify distinction if R-B.
- Must reference prior unblock status and prior registry in outputs.

### CAMPAIGN #78 INITIAL TASK MESSAGE (EXECUTE FIRST, NO DELAY)
PRIORITY 78 — EXECUTE NOW. Start with implementation: check for any new real feed files in data/cache/ingest with complete meta/provenance; if none obvious, pick the most plausible blocked family and write a minimal fail-closed loader/feasibility test against real data paths. Produce heavy artifacts first. No status summary before artifacts.
