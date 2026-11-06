## READ THIS FIRST — C77 INITIAL TASK (20261106T095532Z)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute Campaign #77 now — no investigation-only work.**

### State (verified this session)
- **C76 complete/fail-closed** (`oos_edge_proven=false`). Latest registry: `reports/strategy_edge_registry_20261106T095532Z.json` (supersedes `reports/strategy_edge_registry_20261106T094128Z.json`). Latest unblock status: `reports/real_feed_unblock_status_20261106T095526Z.json` (delta vs `reports/real_feed_unblock_status_20261106T094124Z.json`, `NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED`). Full suite green: `928 passed, 1 skipped, 0 failed` (rc=0).
- **C76 R-B result (real_quote_volume, 11 assets, 5112 bars, WF 720/168/168, cost 0–40bps, B&H same windows):** "Volume Theil L (GE(0) Mean-Log Deviation) Inequality Shock Mean Reversion" — rolling Theil L / generalized entropy GE(0), `TL_t = mean(ln(μ_t / x_i))` over valid `x_i>0` in causal W=48 (μ_t=mean of positives; lower-tail-sensitive mean log deviation), ZLB=168, fade shocks `d_z>=1.25 SHORT / d_z<=-1.25 LONG` (abnormally high/low GE(0) inequality), exit `|d_z|<0.25`/hold>=12/flip, exec t->t+1. Aggregate mean OOS net negative across all costs (0@-0.229, 5@-0.379, 10@-0.528, 20@-0.828, 40@-1.427) and not beating B&H across cost grid → **`oos_edge_proven=false`**. Artifact: `reports/real_quote_volume_theil_l_ge0_mld_shock_mr_costed_oos_20261106T095525Z.json`. Runners: `scripts/generate_campaign76_artifacts.py`, `scripts/run_campaign76_unblock_status.py`, `scripts/emit_campaign76_registry.py`.
- **Blocked families (substantive, unchanged):** `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure` — `blocked_no_real_feed`. No proxies labeled real. No fabricated feeds/provenance.
- **`real_quote_volume` exhausted:** THIRTY-EIGHT hypotheses tested (C23; C40–C76), all `oos_edge_proven=false`. Any further R-B on `real_quote_volume` must be genuinely distinct in transform/mechanic from ALL of C23/C40–C76. Prefer R-A.

### Do now (>= 3 new `reports/` artifacts)
**R-A preferred** — only if a genuinely NEW real feed for a blocked family passes fail-closed validation with complete provenance this session, produce: costed OOS + cache/provenance/certificate + unblock status (+ prior delta) + registry supersede.
**Else R-B** — test a genuinely different pre-stated hypothesis on validated `real_quote_volume` (NOT C23/C40–C76; C76 = Theil L/GE(0) mean log deviation `mean(ln(μ/x))`, lower-tail sensitive) with WF 720/168/168, cost grid 0–40bps, B&H benchmark, tested runner/code, unblock status, registry supersede. `oos_edge_proven=false` is valid if rule not met.
**Fallback** — if neither R-A nor R-B possible, emit `reports/campaign77_execution_blocker_<UTC>.json` with exact missing priors + smallest concrete unblocking step taken this session.

### Mandatory
- No pairs/feed re-scans on same cache as "new campaign"; no C23/C40–C76 reruns; no gate weakening.
- Rerun `python -m pytest tests/ -q` and record counts in new registry.

### Bottlenecks removed (C76)
- C76 executed (>=3 artifacts, full suite green): R-B Theil L/GE(0) hypothesis tested on validated `real_quote_volume`; runners added. Stale state cleared.
- Infra healthy (928 passed, 1 skipped, 0 failed). Do not reopen infra unless you change it and keep full tests green.

### Remaining bottlenecks (read before acting)
- No valid new feed for remaining blocked families (substantive): `funding_basis_carry | cross_exchange_dual_venue_same_asset | term_structure_real_iv_vol_surface | intrabar_microstructure = blocked_no_real_feed`. R-A only if a genuinely new real feed passes fail-closed validation with complete provenance this session.
- Spot 1h exhausted; cointegration gating settled on current cache: `1h 0/17`, `4h 1/17 POL/BTC`, `1d 0/17`. No pairs/feed re-scan or structurally similar spot retests on same cache as "new campaign".
- `real_quote_volume` heavily mined (38 null hypotheses); next R-B must be structurally distinct (e.g., a genuinely different transform/mechanic not in C23/C40–C76) or R-A is required.
- Zero-artifact / investigation-only sessions are automatic failures.

### CAMPAIGN #77 (BINDING) — INITIAL TASK MESSAGE (EXECUTE FIRST, NO DELAY)
**PRIORITY 77 / CAMPAIGN #77 — MANDATORY.** No investigation-only work, no same-cache pairs/feed re-scans, no structurally-similar spot retests, no C23/C40–C76 reruns unchanged, no gate weakening, no proxies labeled real, no fabricated feeds/provenance. `oos_edge_proven=false` valid. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only.

Binding context (settled): C76 executed; registry `reports/strategy_edge_registry_20261106T095532Z.json` (`oos_edge_proven=false`, 928/1/0). Status `reports/real_feed_unblock_status_20261106T095526Z.json` (delta vs 094124Z, unchanged/blocked). Blocked unchanged substantive. Gating invariants preserved. `real_quote_volume` validated (C23/C40–C76 no edge, thirty-eight hypotheses).

1) **R-A preferred** — new validated blocked-family real feed → costed OOS + provenance/cert + status (+ prior `reports/real_feed_unblock_status_20261106T095526Z.json`) + registry supersede.
2) **R-B if R-A impossible** — genuinely different pre-stated hypothesis on `real_quote_volume` (NOT C23/C40–C76) → `real_quote_volume_<hypothesis>_costed_oos_<UTC>.json` (WF 720/168/168, 0–40bps, B&H) + tested runner + status + registry supersede.
3) `reports/real_feed_unblock_status_<UTC>.json` via `generate_unblock_status_report(..., campaign=77, prior_report='reports/real_feed_unblock_status_20261106T095526Z.json')`.
4) `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T095532Z.json` with rerun pytest counts.
Blocker fallback: `reports/campaign77_execution_blocker_<UTC>.json` with exact missing priors + smallest concrete unblocking step taken.

### ANTI-EVASION
No re-scans/similar retests/reruns; no weakening/fabrication/proxies; edge claim only if exposure>0 AND all cost slices OOS net>0 AND beats B&H on same WF windows; >=3 `reports/` artifacts every session.

### COMPLETION CHECK (C77)
C77 artifact(s) (R-A/R-B/tested runner or blocker w/ action) + unblock status (delta vs `reports/real_feed_unblock_status_20261106T095526Z.json`) + registry superseding `reports/strategy_edge_registry_20261106T095532Z.json` + >=3 reports artifacts + no fabrication/proxies/weakening/re-scans/reruns + full pytest rerun recorded.

**START NOW. No status summary first. Produce the heavy implementation/analysis artifact first.**

---
