# HANDOFF (SINGLE DURABLE) — INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION
**Timestamp (UTC): 2026-11-05T10:40:10Z (P11/Campaign #7 completed)**
**Repo (inferred priority): `cryptoquantstatarbstrats` — Crypto Quantitative Statistical Arbitrage Strategies.**
Mission: find/validate a **net-of-cost OOS statistical/arbitrage edge on real crypto data only**. Fail-closed. Heavy, reproducible artifacts required. This file is the **only** durable handoff. Read it first. Execute it. Do not re-litigate settled facts.

## P11/CAMPAIGN #7 COMPLETION (THIS SESSION — >=3 ARTIFACTS)
- **A:** `reports/spot_leadlag_diffusion_costed_oos_20261105T103908Z.json` — structurally new: causal lead-lag cross-asset information diffusion. Per target, (leader, lag) selected by highest |corr(lagged leader, target)| on trailing TRAIN window only (lag candidates {1,2,3,4,6,12}, pre-stated); trade causally z-scored lagged leader signal in test, direction fixed by train corr sign. WF 720/168/168, cost grid 0–40 bps combos, B&H benchmark, real cached spot 1h 2026-04-01..2026-10-30 (5112 bars). **`oos_edge_proven=false` (0/11).** Named: BTC oos_0bps=+0.0455 (bh 0.0569) oos_40bps=-2.8145; ETH oos_0bps=+0.0829 (bh 0.0609) oos_40bps=-2.7771; SOL oos_0bps=-0.0598 oos_40bps=-2.7958; BNB oos_0bps=+0.0838 (bh 0.1679) oos_40bps=-2.5402. Fails all-slices net>0 and/or benchmark rule. Flags: `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, new_external_feeds=false, proxies=false`.
- **B:** `reports/real_feed_unblock_status_20261105T104010Z.json` — honest re-check; **no new real feeds with provenance**. Dual-venue/funding-basis-carry/real IV-vol surface = `blocked_no_real_feed`. Pairs PROVEN BLOCKED (no re-scan). Covers P10 gap.
- **C:** `reports/strategy_edge_registry_20261105T104010Z.json` (supersedes `20261105T095736Z.json`) — includes P10 residual momentum + P11 lead-lag diffusion; rerun tests **832 passed, 1 skipped, 0 failed, 3573 warnings, 40.20s** (`PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q`). Covers P10 gap.

## INITIAL TASK MESSAGE (EXECUTE FIRST — NO DELAY)
**PRIORITY 12 / CAMPAIGN #8 — MANDATORY.** Next agent MUST NOT do investigation-only work. Produce **>= 3 new concrete artifacts in `reports/`**. Real data only. No fabrication. No threshold weakening. No proxies labeled as real. `oos_edge_proven=false` is valid and required if edge is not proven. **Zero-artifact sessions are automatic failures.**

### Binding context (settled)
- **Tests (P11):** 832 passed, 1 skipped, 0 failed. Re-run and record in new registry.
- **Real spot cache:** `data/cache/*_2026-04-01_2026-10-30_1h.pkl` + `.meta.json` — 11 assets, 5112 bars, 2026-04-01..2026-10-30 1h, Binance public spot. **Use as-is. Do not re-fetch.**
- **Pairs:** PROVEN BLOCKED (165/165). No re-scan. No gate weakening.
- **Feeds:** dual-venue/funding-basis-carry/real IV-vol surface `blocked_no_real_feed`. No fabricated feeds.

### Core truth (no proven net-of-cost OOS edge on real cached spot 1h, WF 720/168/168, cost grid 0/5/10/20 bps combos)
- P4 momentum 0/11, mean_reversion 0/11 (`momentum_mr_costed_oos_20261105T081323Z.json`)
- P5 cross_sectional_risk_adjusted_return_rank (`spot_alt_signal_costed_oos_20261105T084619Z.json`)
- P6 donchian_breakout_volfilter 0/11 (`spot_breakout_volfilter_costed_oos_20261105T093626Z.json`)
- P7 range_breakout_reversion_volband 0/11 (`spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json`)
- P9 spot_zscore_regime_mean_reversion_pairs 0/11, 55 pairs (`spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json`)
- P10 spot_residual_momentum 0/11 (`spot_residual_momentum_costed_oos_20261105T100459Z.json`)
- P11 spot_leadlag_diffusion 0/11 (`spot_leadlag_diffusion_costed_oos_20261105T103908Z.json`)
- Latest registry: `reports/strategy_edge_registry_20261105T104010Z.json`

## CAMPAIGN #8 (BINDING — CANNOT BE AVOIDED)
Structurally distinct spot-only families on the current 11-asset 1h window are **exhausted** across tested pre-stated hypotheses (raw mom/MR, xsec rank, Donchian, range breakout-reversion+volband, pairwise OLS-hedge spread MR, residual momentum, causal lead-lag diffusion). Next session MUST follow **Path C unless a genuinely new real feed with provenance is ingested in-session**:

### Path C (default, required if no new real feed)
Produce **>=3 artifacts**:
1. `reports/spot_universe_exhausted_memo_<UTC>.json` — fail-closed memo: enumerate tested families + artifacts, explicitly rule out remaining *pre-stated* micro-hypotheses on same cached spot (must be specific, e.g. vol-managed sizing overlays on each tested signal family with causal regime filter; intrabar-unavailable so not testable here — state why; no hand-waving), document why no further structurally distinct spot-only hypothesis is justified on this window without new data, and give a concrete **real-feed acquisition checklist** (funding/basis schema, dual-venue schema, real IV/vol surface schema) with provenance/validation requirements. `real_data_only=true, fabricated_data=false, fail_closed=true`.
2. `reports/real_feed_unblock_status_<UTC>.json` — honest re-check (no fabrication).
3. `reports/strategy_edge_registry_<UTC>.json` — supersedes `20261105T104010Z.json`, rerun test counts, states spot-only exhaustion and blocked real feeds.

### Path R (only if new real feed with provenance ingested this session)
If a genuinely new real dataset/feed is added **with verifiable provenance in `data/cache`/metadata** this session: produce `reports/<family>_costed_oos_<UTC>.json` (fail-closed, WF/costs pre-stated, net-of-costs/carry) + feed unblock status + registry supersede (>=3). Do **not** claim ingestion without provenance files.

## ANTI-EVASION (ENFORCED)
- **No escape:** No pairs/feed re-scans unless genuinely new real dataset + new fail-closed audit added this session. No structurally similar spot retests presented as new.
- **No edge claim:** `oos_edge_proven=true` only if pre-stated: exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows.
- **No weakening:** Never weaken enriched gates or fail-closed flags. No proxies labeled real.
- **Heavy work mandatory:** >=3 new artifacts.
- **Honesty:** `oos_edge_proven=false` is valid; exhaustion must be explicit and specific.

## COMPLETION CHECK
- [ ] `spot_universe_exhausted_memo_<UTC>.json` (Path C) OR new-feed `*_costed_oos_<UTC>.json` (Path R) exists with fail-closed flags
- [ ] `real_feed_unblock_status_<UTC>.json` exists (honest)
- [ ] `strategy_edge_registry_<UTC>.json` supersedes `20261105T104010Z.json` with test counts
- [ ] No fabrication/proxies/threshold weakening; no pairs re-scan
- [ ] >= 3 new artifacts in `reports/`

**START NOW. No status summary first. Produce the heavy analysis artifact first.**
