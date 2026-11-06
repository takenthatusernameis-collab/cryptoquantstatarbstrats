## READ THIS FIRST — C75 INITIAL TASK (20261106T093653Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #75 now — no investigation-only work.**

### State (verified this session)
- **C74 complete/fail-closed** (`oos_edge_proven=false`). Latest registry: `reports/strategy_edge_registry_20261106T092751Z.json` (supersedes `...091943Z.json`). Latest unblock status: `reports/real_feed_unblock_status_20261106T092751Z.json` (delta vs `...091925Z.json`, `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`). Full suite green at last registry: `928 passed, 1 skipped, 0 failed` (rc=0).
- **C74 R-B result (real_quote_volume, 11 assets, 5112 bars, WF 720/168/168, cost 0–40bps, B&H same windows):** "Volume Theil T Inequality Shock Mean Reversion" — rolling Theil T `T_t=mean((x/μ)*ln(x/μ)), x>0,μ>0` (GE(1), value-weighted log-ratio inequality), W=48, ZLB=168, fade shocks `d_z>=1.25 SHORT / d_z<=-1.25 LONG`, exit `|d_z|<0.25`/hold>=12/flip, exec t->t+1. Aggregate mean OOS net negative across all costs, B&H not beaten → **`oos_edge_proven=false`**. Artifact: `reports/real_quote_volume_theil_t_inequality_shock_mr_costed_oos_20261106T092744Z.json`.
- **Blocked families (substantive, unchanged):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure` — `blocked_no_real_feed`. No proxies labeled real. No fabricated feeds/provenance.
- **`real_quote_volume` exhausted:** THIRTY-SIX hypotheses tested (C23; C40–C74), all `oos_edge_proven=false`. Any further R-B on `real_quote_volume` must be genuinely distinct in transform/mechanic from ALL of C23/C40–C74. Prefer R-A.

### Do now (>= 3 new `reports/` artifacts)
**R-A preferred** — only if a genuinely NEW real feed for a blocked family passes fail-closed validation with complete provenance this session, produce: costed OOS + cache/provenance/certificate + unblock status (+ prior delta) + registry supersede.
**Else R-B** — test a genuinely different pre-stated hypothesis on validated `real_quote_volume` (NOT C23/C40–C74; C74 = rolling Theil T GE(1) inequality shock MR) with WF 720/168/168, cost grid 0–40bps, B&H benchmark, tested runner/code, unblock status, registry supersede. `oos_edge_proven=false` is valid if rule not met.
**Fallback** — if neither R-A nor R-B possible, emit `reports/campaign75_execution_blocker_<UTC>.json` with exact missing priors + smallest concrete unblocking step taken this session.

### Mandatory
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C74 reruns; no gate weakening.
- Rerun `python -m pytest tests/ -q` and record counts in new registry.

### Bottlenecks removed (C74)
- C74 executed (>=3 artifacts, full suite green): R-B Theil T hypothesis tested on validated `real_quote_volume`; runners `scripts/generate_campaign74_artifacts.py`, `scripts/run_campaign74_unblock_status.py`, `scripts/emit_campaign74_registry.py` added. Stale state cleared.
- Infra healthy (928 passed, 1 skipped, 0 failed). Do not reopen infra unless you change it and keep full tests green.

### Remaining bottlenecks (read before acting)
- No valid new feed for remaining blocked families (substantive): `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed`. R-A only if a genuinely new real feed passes fail-closed validation with complete provenance this session.
- Spot 1h exhausted; cointegration gating settled on current cache: `1h 0/17`, `4h 1/17 POL/BTC`, `1d 0/17`. No pairs/feed re-scan or structurally similar spot retests on same cache as "new campaign".
- Zero-artifact / investigation-only sessions are automatic failures.

### CAMPAIGN #75 (BINDING) — INITIAL TASK MESSAGE (EXECUTE FIRST, NO DELAY)
**PRIORITY 75 / CAMPAIGN #75 — MANDATORY.** No investigation-only work, no same-cache pairs/feed re-scans, no structurally-similar spot retests, no C23/C40–C74 reruns unchanged, no gate weakening, no proxies labeled real, no fabricated feeds/provenance. `oos_edge_proven=false` valid. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only.

Binding context (settled): C74 executed; registry `reports/strategy_edge_registry_20261106T092751Z.json` (`oos_edge_proven=false`, 928/1/0). Status `reports/real_feed_unblock_status_20261106T092751Z.json` (delta vs 091925Z, unchanged/blocked). Blocked unchanged substantive. Gating invariants preserved. `real_quote_volume` validated (C23/C40–C74 no edge, thirty-six hypotheses).

1) **R-A preferred** — new validated blocked-family real feed → costed OOS + provenance/cert + status (+ prior `reports/real_feed_unblock_status_20261106T092751Z.json`) + registry supersede.
2) **R-B if R-A impossible** — genuinely different pre-stated hypothesis on `real_quote_volume` (NOT C23/C40–C74) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, 0–40bps, B&H) + tested runner + status + registry supersede.
3) `reports/real_feed_unblock_status_<UTC>.json` via `generate_unblock_status_report(..., campaign=75, prior_report='reports/real_feed_unblock_status_20261106T092751Z.json')`.
4) `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T092751Z.json` with rerun pytest counts.
Blocker fallback: `reports/campaign75_execution_blocker_<UTC>.json` with exact missing priors + smallest concrete unblocking step taken.

### ANTI-EVASION
No re-scans/similar retests/reruns; no weakening/fabrication/proxies; edge claim only if exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows; >=3 `reports/` artifacts every session.

### COMPLETION CHECK (C75)
C75 artifact(s) (R-A/R-B/tested runner or blocker w/ action) + unblock status (delta vs `reports/real_feed_unblock_status_20261106T092751Z.json`) + registry superseding `reports/strategy_edge_registry_20261106T092751Z.json` + >=3 reports artifacts + no fabrication/proxies/weakening/re-scans/reruns + full pytest rerun recorded.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**
