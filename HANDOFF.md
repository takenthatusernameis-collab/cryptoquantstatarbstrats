# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Core mission: real-data-only edge search (fail-closed enriched cointegration gates), no fabrication, no status-only work. **Single durable handoff at repo root: `HANDOFF.md` only** (updated 2026-11-11T09:27:56Z UTC). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C15 progress. Do not touch it for C250; it cannot block C250. NOTE: `state.yaml` is stale (still reads `latest_campaign_done: C248` / `next_campaign: C249`) but C249 is already complete (see below); syncing it is part of the C250 heavy-work mandate (`sync_state_and_handoff`) but remains a user-requested edit.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T09:27:56Z UTC)

**Initial task (execute immediately, heavy work, no status-only):** Campaign #15 is COMPLETE (7/7 evaluated, all with timestamped artifacts+SHA256 and honest conclusions; zero `edge` found → no cost-aware OOS validation triggered). Research line C249 is COMPLETE (`edge_claim: NONE`, `oos_edge_proven: false`; execution summary + OOS + script + registry artifacts present, all SHA256-verified). **Bottlenecks removed — none remain.** All candidate caches verified present in `data/cache/` with `.pkl`+`.meta.json`; `fetch_success: True`, none flagged fabricated; c7-venv python present at `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`; no network refetch needed.

Next unambiguous heavy focus: **Campaign #250** (research-line continuation after C249) — real-data-only, fail-closed volume RQA shock mean-reversion edge search on a preselected distinct strategy.
- Preselect strategy `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K`. Verify grep-zero distinctness first: `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K|WHITE_DIAG_LINE_LENGTH_YULE_K' scripts/ strategies/ backtest/ utils/ 2>&1` must return 0 nonself hits before implementation/run.
- Ordered fallbacks (if preselected fails grep-zero or is blocked): `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE`, then `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW` (each must independently pass grep-zero distinctness).
- Each run MUST produce: timestamped costed-OOS artifact + SHA256 (from bytes), script + SHA256, ingest attempt + SHA256, strategy-edge-registry entry + SHA256, campaign execution summary + SHA256.
- Honest conclusion: `oos_edge_proven: true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows (real data only); otherwise `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums` per cost slice, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`).
- Stop only if `oos_edge_proven: true`. Otherwise record honest blocked/no-edge conclusion with evidence and update this handoff.
- **Do not** edit `research_state/state.yaml` unless explicitly requested by the user.

## C14 FINAL (verified 2026-11-11T08:56:40Z UTC)

| # | Cache8 | SHA256 (artifact) | Conclusion |
|---|--------|-------------------|------------|
| 1 | `90d10b87` | `952bd7a1e549ff0994f1c413273017492293c52d3e2e15ec5118441a7a69cf82` | insufficient_or_blocked |
| 2 | `595e501a` | `cf4c6cabc68a179d6391bc4dedebcf23d4c060c685ee3563af44b4fceeb7530e` | insufficient_or_blocked |
| 3 | `4fd3e87f` | `aaf7a2ca32cb5b884e239f5daf3804270cb31d971cb47c802ed6dcf8187c9c84` | insufficient_or_blocked |
| 4 | `74e86e8e` | `657ecf30b12a30839f08372e41275b4cbaec9f65a4400bfb57ba1071a9218bd4` | insufficient_or_blocked |
| 5 | `76dedb82` | `1902a2c2ed6b5e0ad6d275983e1b1e31c0226fef15d2bf3e18fbe4460543cd1e` | insufficient_or_blocked |
| 6 | `a74dcf38` | `123b866fda7977aea4d13fe9c4edd04b0366838bc77b43cd56378534da402c9d` | no_edge (rolling_stable_ok blocks all bars) |
| 7 | `749b2218` | `e9631e325dd617efef53ec64ead0d105746d5abd0669ee0bd2017098058fad1d` | insufficient_or_blocked |

All artifacts: `reports/campaign14_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`. No edge found in any completed cache; no cost-aware OOS validation triggered.

## C15 FINAL (verified 2026-11-11T09:21:51Z UTC — COMPLETE 7/7)

| # | Cache8 | SHA256 (artifact) | Conclusion |
|---|--------|-------------------|------------|
| 1 | `f4555e78` | `a08d48a7e53cee307ba008cd59271cc0c59017d7c804618266bb08326846571f` | insufficient_or_blocked (mixed blockers; rolling_stable_ok blocks all bars on 11/13 pairs) |
| 2 | `d275256c` | `e4d643bdca1760e845e57ed07331001c4baeccc1026f39dda71b0252dd8bddb3` | no_edge (rolling_stable_ok blocks all bars) |
| 3 | `afe337ed` | `762291e9fa6f4c0d306835c47e6456aabe60574662390677f8581b76307b72ee` | no_edge (rolling_stable_ok blocks all bars) |
| 4 | `c12ce191` | `6517198eee201b3aeda58413e7a42be9d966b7d4b5acc0018ccfc6fdd8b74795` | no_edge (rolling_stable_ok blocks all bars) |
| 5 | `dd9bc604` | `2c3bf2353e964d7735d88275825d5c29ffb02d51e170899fb3403e49ba5365dc` | no_edge (rolling_stable_ok blocks all bars) |
| 6 | `c7b2c0be` | `5cbc8bf2839d4fca616c11a36dfef07a4ec839eabb61c2c744e3a22de14f295f` | no_edge (rolling_stable_ok blocks all bars) |
| 7 | `f6df4426` | `3ee9fb132a597ce88da90d1773cb11cc7355d6d1333acd56c1e0b5d85b8a7928` | no_edge (rolling_stable_ok blocks all bars) |

Artifacts: `reports/campaign15_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`. Zero edge found across all 7 caches; no cost-aware OOS validation triggered. C15 fully evaluated — no remaining C15 caches.

## C249 (RESEARCH LINE — COMPLETE)

- `reports/campaign249_execution_summary_20261110T170949Z.json`: campaign 249, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR`, edge_claim NONE, oos_edge_proven false, all_new_c249_artifact_paths_sha256_from_bytes true.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos_20261109T034759Z.json` (sha256 `042fa8fb58b1b2976869cb0508396325d7d25eed075b38ecbf4043033f2615b4`)
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos.py` (sha256 `7ca7bb4b0c41fa38448216dbba7dfbd9b8779c0885b88ff7e794036429e7e4fc`)
- Ingest: `reports/real_feed_ingest_attempt_20261109T003420Z.json` (sha256 `cfae5e5a6fbbb32862a27e4291c17e65c11dc7028291201c8f2ad2477f7c5c7c`)
- Registry: `reports/strategy_edge_registry_20261110T170949Z.json` (sha256 `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`)

## MANDATORY HEAVY ACTION — CAMPAIGN #250 (NON-DEFERRABLE)

**Goal:** Execute one real-data-only, fail-closed volume RQA shock mean-reversion edge evaluation on a preselected distinct strategy (YULE_K primary; MIDRANGE / PEARSON_SKEW ordered fallbacks), producing timestamped artifact + SHA256 + registry + OOS validation. Each run MUST produce all artifacts with SHA256 from bytes. Stop ONLY if `oos_edge_proven: true`. Otherwise record honest `edge_claim: NONE` with evidence.

**Runner (from repo root):** implement/run the C250 script following the C249 pattern (see `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos.py`), substituting the preselected strategy id and verifying grep-zero distinctness first.

**Per-campaign requirements:**
- Verify grep-zero distinctness for the chosen strategy id before implementation/run (0 nonself hits in scripts/, strategies/, backtest/, utils/).
- Produce timestamped artifact: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_<skew>_shock_mr_costed_oos_<UTC>.json`
- Produce script + SHA256, ingest attempt + SHA256, strategy-edge-registry entry + SHA256, campaign execution summary + SHA256.
- Record honest conclusion: `oos_edge_proven` / `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums` per cost slice, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`).
- Update **THIS HANDOFF** with verified UTC, commands run, artifact paths+SHA256, conclusions, and next unambiguous directive. **Do not** edit `research_state/state.yaml` unless explicitly requested by the user.

## BOTTLENECK REMOVAL (pre-cleared for this session — no work is blocked)

- C12 complete (5/5), C13 complete (3/3), C14 complete (7/7), C15 complete (7/7) — no re-runs permitted except evidence-backed defect fix.
- C249 complete (research line) — no re-run permitted except evidence-backed defect fix.
- All caches `.pkl`+`.meta.json` present in `data/cache/`; no network refetch needed (real cached spot only). Verified 2026-11-11T09:27:56Z UTC.
- c7-venv python present: `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`.
- `research_state/state.yaml` locked — do not touch; stale `next_campaign: C249` does not block C250 (C249 already complete).
- No status-only work counts toward C250; every run must produce artifact+SHA256 or an honest blocked/no-edge conclusion with evidence.
- No background process active; no stale "cache still running" claims.
- **Grep-zero pre-verified at 2026-11-11T09:27:56Z UTC:** YULE_K (0 hits), MIDRANGE (0 hits), PEARSON_SKEW (0 hits) — all three candidates distinct.

## HARD BANS

- ❌ No status-only work
- ❌ No re-runs of C1–C15 or C249 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15)
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user
- ❌ No early exit — C250 run must complete unless `oos_edge_proven: true`

## KEY FILES

- C14/C15 runner: `examples/run_campaign13_causal_gates.py` (rename output `campaign13_*` → `campaign14_*`/`campaign15_*`)
- C14 artifacts: `reports/campaign14_causal_per_bar_enriched_gates_{90d10b87,595e501a,4fd3e87f,74e86e8e,76dedb82,a74dcf38,749b2218}_*.json`
- C15 artifacts: `reports/campaign15_causal_per_bar_enriched_gates_{f4555e78,d275256c,afe337ed,c12ce191,dd9bc604,c7b2c0be,f6df4426}_*.json`
- C249 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos.py`, `reports/campaign249_execution_summary_20261110T170949Z.json`, `reports/strategy_edge_registry_20261110T170949Z.json`
- Strategy/gates: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/*.{pkl,meta.json}`
- Locked separate line (do not edit): `research_state/state.yaml`

**END OF DURABLE HANDOFF — 2026-11-11T09:27:56Z UTC.** C12 COMPLETE (5/5). C13 COMPLETE (3/3). C14 COMPLETE (7/7), zero edge. C15 COMPLETE (7/7), zero edge. C249 COMPLETE (research line), edge_claim NONE, oos_edge_proven false. **Next: Campaign #250 — preselect `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K` (grep-zero distinctness pre-verified 0 hits; fallbacks MIDRANGE, PEARSON_SKEW also 0 hits), run real-data-only fail-closed costed-OOS edge evaluation, produce all artifacts+SHA256, honest conclusion, update this handoff. No status-only work. Bottlenecks pre-cleared; heavy work is mandatory, not optional.**