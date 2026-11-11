# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Core mission: real-data-only edge search (fail-closed enriched cointegration gates), no fabrication, no status-only work. **Single durable handoff at repo root: `HANDOFF.md` only** (updated 2026-11-11T10:44:15Z UTC, this session). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (C104–C248 locked, currently stale at `latest_campaign_done: C248` / `next_campaign: C249`; C249 is already complete — see below). Separate research line; must not be edited to block/replace C1–C15 progress. Syncing `state.yaml` is only permitted if explicitly requested by the user.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T10:44:15Z UTC)

**DO THIS FIRST (heavy execution, no status-only, no planning substitute): Campaign #251 — real-data-only fail-closed volume RQA shock mean-reversion costed-OOS edge search. Primary strategy: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE` (midrange = (max+min)/2 on qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0). Ordered fallback if blocked/fails distinctness: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW`. Use `python3` (3.12.3); deps `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 available.**

**State (verified 2026-11-11T10:44:15Z UTC):** C12 5/5, C13 3/3, C14 7/7 (zero edge), C15 7/7 (zero edge) — no re-runs except evidence-backed defect fix. Research line C249 COMPLETE (`edge_claim: NONE`, `oos_edge_proven: false`). **C250 COMPLETE** (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K`, `edge_claim: NONE`, `oos_edge_proven: false`; all 5 artifacts + SHA256 from bytes on disk, see C250 section). Caches present in `data/cache/` (68 files incl. `.pkl`+`.meta.json`); no network refetch. **Bottlenecks cleared (this session):** missing `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python` resolved by using `python3`; C249/C250 artifacts+script present on disk; grep-zero re-verified MIDRANGE=0, PEARSON_SKEW=0 (scripts/strategies/backtest/utils); no blocking background process. No status-only work permitted. Stop only if `oos_edge_proven: true`; otherwise record honest `edge_claim: NONE` with evidence and update this handoff. Do not edit `research_state/state.yaml` unless explicitly requested by user.

**C251 plan (non-deferrable):**
- **Preselected strategy:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE` (midrange = (max+min)/2 on qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if denominator/feature undefined or insufficient qualifying segments per pre-stated rules — follow C249/C250 script conventions).
- **Distinctness gate (must re-confirm before implementation/run):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE|WHITE_DIAG_LINE_LENGTH_MIDRANGE' scripts/ strategies/ backtest/ utils/` → **0 nonself hits required**.
- **Ordered fallback if blocked/fails distinctness:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW` — must pass grep-zero independently.
- **Implement by adapting C250 pattern:** `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py` → new script for chosen strategy; preserve fail-closed, real-data-only, SHA256-from-bytes, and artifact/registry/summary/ingest emission patterns.
- **Required outputs (all SHA256 from bytes):** timestamped costed-OOS artifact, script, ingest attempt, strategy-edge-registry entry, campaign execution summary (all under `reports/`/`scripts/` as appropriate).
- **Edge rule (honest, fail-closed):** `oos_edge_proven: true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence: `cross_asset_oos_net_sums` per cost slice, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`.
- **Stop only if `oos_edge_proven: true`.** Otherwise record honest blocked/no-edge conclusion with evidence and update this handoff (paths, SHA256s, conclusion, next directive). No planning/researching as a substitute for execution. Do **not** edit `research_state/state.yaml` unless explicitly requested by user.

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

## C250 (MAIN LINE — COMPLETE)

- Campaign 250, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, edge_claim NONE, oos_edge_proven false, all_new_c250_artifact_paths_sha256_from_bytes true.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos_20261111T103421Z.json` (sha256 `af1e3767a474fe28f839a42cc7662fd2f933aadd72df57a4ae76249af211bd7b`)
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py` (sha256 `1f94dc35ae8bda2f94e933ed90bee5f34ccde81efacee9ae8cb6352a1764828b`)
- Ingest: `reports/real_feed_ingest_attempt_20261111T104044Z.json` (sha256 `eed9819368d4c5106fa6aab1c01e0a0cd5bb22fcdc62e23e22614b797480d903`)
- Registry: `reports/strategy_edge_registry_20261111T104048Z.json` (sha256 `37d4a9b6f418c7dcf180c39e02bf89aeb3751c060b6d75b510c19bec4ec6b4d7`)
- Summary: `reports/campaign250_execution_summary_20261111T104050Z.json` (sha256 `facee955b68c9498aac50631a3bda06097042f9e44a1175f226b3da69a66729f`)
- Evidence: `cross_asset_oos_net_sums` all negative across cost slices (fee0_slip0=-0.334, fee5_slip5=-1.996, fee10_slip10=-3.658, fee20_slip20=-6.982, fee40_slip40=-13.630); `any_exposure_oos: true`; `all_cost_slices_positive_oos_net_sum: false`; `all_cost_slices_beat_bh_mean_rule: false`. No edge found; honest no-edge conclusion recorded.

## MANDATORY HEAVY ACTION — CAMPAIGN #251 (NON-DEFERRABLE)

**Goal:** Execute one real-data-only, fail-closed volume RQA shock mean-reversion edge evaluation on a preselected distinct strategy (MIDRANGE primary; PEARSON_SKEW ordered fallback), producing timestamped artifact + SHA256 + registry + OOS validation. Each run MUST produce all artifacts with SHA256 from bytes. Stop ONLY if `oos_edge_proven: true`. Otherwise record honest `edge_claim: NONE` with evidence.

**Runner (from repo root):** implement/run the C251 script following the C250 pattern (see `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py`), substituting the preselected strategy id (MIDRANGE = (max+min)/2 of qualifying WHITE diagonal segment lengths) and verifying grep-zero distinctness first.

**Per-campaign requirements:**
- Verify grep-zero distinctness for the chosen strategy id before implementation/run (0 nonself hits in scripts/, strategies/, backtest/, utils/).
- Produce timestamped artifact: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos_<UTC>.json`
- Produce script + SHA256, ingest attempt + SHA256, strategy-edge-registry entry + SHA256, campaign execution summary + SHA256.
- Record honest conclusion: `oos_edge_proven` / `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums` per cost slice, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`).
- Update **THIS HANDOFF** with verified UTC, commands run, artifact paths+SHA256, conclusions, and next unambiguous directive. **Do not** edit `research_state/state.yaml` unless explicitly requested by the user.

## BOTTLENECK REMOVAL (pre-cleared — 2026-11-11T10:44:15Z UTC, re-verified this session)

- C12 complete (5/5), C13 complete (3/3), C14 complete (7/7), C15 complete (7/7) — no re-runs permitted except evidence-backed defect fix.
- C249 complete (research line), C250 complete (main line) — no re-runs permitted except evidence-backed defect fix.
- All caches `.pkl`+`.meta.json` present in `data/cache/` (68 files); no network refetch (real cached spot/volume only).
- **Python/deps bottleneck cleared:** use `python3` (3.12.3) with `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 (missing c7-venv is not a blocker).
- C249/C250 script/summary/registry/ingest/OOS artifacts present on disk (verified).
- `research_state/state.yaml` locked/stale — do not touch; does not block C251.
- **Grep-zero re-verified (2026-11-11T10:44:15Z UTC):** MIDRANGE (0 hits), PEARSON_SKEW fallback (0 hits).
- No blocking background process. No status-only work.

## HARD BANS

- ❌ No status-only work
- ❌ No re-runs of C1–C15 or C249 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15)
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user
- ❌ No early exit — C251 run must complete unless `oos_edge_proven: true`
- ❌ No "planning" or "researching" as substitute for running the script and producing artifacts

## KEY FILES

- C14/C15 runner: `examples/run_campaign13_causal_gates.py` (rename output `campaign13_*` → `campaign14_*`/`campaign15_*`)
- C14 artifacts: `reports/campaign14_causal_per_bar_enriched_gates_{90d10b87,595e501a,4fd3e87f,74e86e8e,76dedb82,a74dcf38,749b2218}_*.json`
- C15 artifacts: `reports/campaign15_causal_per_bar_enriched_gates_{f4555e78,d275256c,afe337ed,c12ce191,dd9bc604,c7b2c0be,f6df4426}_*.json`
- C249 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos.py`, `reports/campaign249_execution_summary_20261110T170949Z.json`, `reports/strategy_edge_registry_20261110T170949Z.json`
- C250 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py`, `reports/campaign250_execution_summary_20261111T104050Z.json`, `reports/strategy_edge_registry_20261111T104048Z.json`, `reports/real_feed_ingest_attempt_20261111T104044Z.json`
- Strategy/gates: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/*.{pkl,meta.json}`
- Locked separate line (do not edit): `research_state/state.yaml`

## EXACT COMMANDS TO RUN FOR C251 (from repo root)

```bash
# 1. Re-verify grep-zero distinctness for MIDRANGE (MUST return 0 nonself hits)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE|WHITE_DIAG_LINE_LENGTH_MIDRANGE' scripts/ strategies/ backtest/ utils/

# 2. Copy C250 pattern script and adapt for MIDRANGE
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py

# 3. Edit the new script: replace all "YULE_K"/"yule_k" with "MIDRANGE"/"midrange",
#    update strategy_id, feature docstring/formula (midrange = (max+min)/2 on qualifying WHITE diagonal segment
#    lengths pooled over off-diagonal diagonals k!=0), grep-distinctness check string, and artifact/report naming.

# 4. Run the script (heavy work — produces timestamped artifacts; use system python, not missing c7-venv)
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py

# 5. Verify all required artifacts exist and record SHA256-from-bytes for: OOS artifact, script, ingest attempt,
#    strategy-edge-registry entry, campaign execution summary.

# 6. Update THIS HANDOFF.md with: UTC timestamp, commands run, artifact paths+SHA256, conclusion, next directive.
#    Do NOT edit research_state/state.yaml unless explicitly requested by user.
```

**If MIDRANGE fails grep-zero or is blocked:** repeat for PEARSON_SKEW (independently grep-zero verified).

**END OF DURABLE HANDOFF — updated 2026-11-11T10:44:15Z UTC.** C12 COMPLETE (5/5). C13 COMPLETE (3/3). C14 COMPLETE (7/7), zero edge. C15 COMPLETE (7/7), zero edge. C249 COMPLETE (research line), edge_claim NONE, oos_edge_proven false. C250 COMPLETE (main line), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K`, edge_claim NONE, oos_edge_proven false — all 5 artifacts + SHA256 from bytes on disk. **IMMEDIATE NEXT ACTION (non-deferrable): Campaign #251 — implement/run `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE` (grep-zero 0; fallback PEARSON_SKEW 0) via `python3` from C250 pattern, produce timestamped OOS/script/ingest/registry/summary artifacts with SHA256-from-bytes, record honest edge/no-edge with evidence, then update this handoff. Do not stop at planning. No status-only work.**
