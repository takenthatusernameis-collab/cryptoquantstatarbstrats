# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Core mission: real-data-only edge search (fail-closed enriched cointegration gates), no fabrication, no status-only work. **Single durable handoff at repo root: `HANDOFF.md` only** (updated 2026-11-11T08:56:40Z UTC). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C15 progress. Do not touch it for C15; it cannot block C15.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T08:56:40Z UTC)

**Initial task (execute immediately, heavy work, no status-only):** Campaign #14 is COMPLETE (7/7 evaluated, all with timestamped artifacts+SHA256 and honest conclusions; zero `edge` found → no cost-aware OOS validation triggered). **Bottlenecks removed — none remain.** All 7 candidate C15 caches verified present in `data/cache/` with `.pkl`+`.meta.json`; `fetch_success: True`, none flagged fabricated; c7-venv python present at `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`; no network refetch needed. Next unambiguous heavy focus: **Campaign #15 — causal gate edge search on remaining unevaluated real spot caches (wider-universe + OOS windows), real-data-only enforcement, unmodified thresholds.** Campaign #15 NOT STARTED — zero `reports/campaign15_causal_per_bar_enriched_gates_*` artifacts. Every eligible cache must produce a timestamped artifact + SHA256 or an honest blocked conclusion with evidence. Stop only if `edge` found (then run cost-aware OOS validation immediately).

**C14 FINAL (verified 2026-11-11T08:56:40Z UTC):**
| # | Cache8 | SHA256 (artifact) | Conclusion |
|---|--------|--------|------------|
| 1 | `90d10b87` | `952bd7a1e549ff0994f1c413273017492293c52d3e2e15ec5118441a7a69cf82` | insufficient_or_blocked |
| 2 | `595e501a` | `cf4c6cabc68a179d6391bc4dedebcf23d4c060c685ee3563af44b4fceeb7530e` | insufficient_or_blocked |
| 3 | `4fd3e87f` | `aaf7a2ca32cb5b884e239f5daf3804270cb31d971cb47c802ed6dcf8187c9c84` | insufficient_or_blocked |
| 4 | `74e86e8e` | `657ecf30b12a30839f08372e41275b4cbaec9f65a4400bfb57ba1071a9218bd4` | insufficient_or_blocked |
| 5 | `76dedb82` | `1902a2c2ed6b5e0ad6d275983e1b1e31c0226fef15d2bf3e18fbe4460543cd1e` | insufficient_or_blocked |
| 6 | `a74dcf38` | `123b866fda7977aea4d13fe9c4edd04b0366838bc77b43cd56378534da402c9d` | no_edge (rolling_stable_ok blocks all bars) |
| 7 | `749b2218` | `e9631e325dd617efef53ec64ead0d105746d5abd0669ee0bd2017098058fad1d` | insufficient_or_blocked |

All artifacts: `reports/campaign14_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`. No edge found in any completed cache; no cost-aware OOS validation triggered.

## MANDATORY HEAVY ACTION — CAMPAIGN #15 (NON-DEFERRABLE)

**Goal:** Extend the causal per-bar enriched-gate edge search to the remaining unevaluated real spot caches (wider-universe and OOS windows) with real-data-only enforcement and unmodified thresholds. Each run MUST produce a timestamped artifact + SHA256. Stop ONLY if `edge` found (then run cost-aware OOS validation immediately). All eligible caches must complete otherwise.

**Runner (from repo root):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
$PY examples/run_campaign13_causal_gates.py --cache <full_hash>
# The runner writes a campaign13_* prefixed artifact by design — copy/rename to campaign15_* after each run.
```

**Candidate caches (real spot, priority order; skip any cache8 that already has a `campaign15_causal_per_bar_enriched_gates_<cache8>_*` artifact — no duplicate campaign15 artifacts; verify `fetch_fabricated_data != True` and `fetch_success: True` in `data/cache/<hash>.meta.json` before running):**

| Priority | Cache8 | Symbols | Interval | Bars | Window | Notes |
|----------|--------|---------|----------|------|--------|-------|
| 1 | `f4555e78aaf41746791f9959fd08e951f8bb089342f95ffc039145d287db6233` | 7: ADA,BNB,BTC,DOT,ETH,SOL,XRP | 1h | 5112 | 2026-04-01..2026-10-30 | Wider universe, full window — heaviest |
| 2 | `d275256cdefff23a8aaa759e63b16deb3292828d50ab2d8effd6722e89c12c76` | 2: BTC,ETH | 1h | 5112 | 2026-04-01..2026-10-30 | Full window; `fetch_real_data_only` unset — verify provenance |
| 3 | `afe337ed9ac6917a0133e12ec296ff39435ec045e7933d72e244b9748b976af5` | 2: BTC,ETH | 5m | 2016 | 2026-10-01..2026-10-07 | OOS / 5m window |
| 4 | `f6df44264750176ca006536352e43009bf0e24d365a4dc552cac469d61845c49` | 2: BTC,ETH | 5m | 2016 | 2026-10-24..2026-10-30 | Recent 5m window |
| 5 | `dd9bc604a203b3e20eec78508484f267c3061b791de88d1ff108b1683031c1b0` | 2: BTC,ETH | 5m | 864 | 2026-10-01..2026-10-03 | 5m window |
| 6 | `c12ce191b92a399b4cd40393779b330919283008f787824f9aecb8958f19e8ac` | 2: BTC,ETH | 5m | 288 | 2026-10-01 (1 day) | Single-day 5m |
| 7 | `c7b2c0bea881c17a001ba69aca5641638bad92f47c800e5b03cff0129b2fca28` | 2: BTC,ETH | 1h | 72 | 2026-04-01..2026-04-03 | Short |

**Skip (not eligible for C15 fresh evaluation):** `547a6a68` (1 sym, 48 bars — too short/single), `f481053c` (1 sym — pairs strategy N/A), `dcd5764a` (already C12-evaluated). C14 precedent (re-using C12 cache hashes under a new campaign) allows fresh C15 evaluation of unevaluated caches; do not re-produce C12/C13/C14 artifacts.

**Per-cache requirements:**
- Produce timestamped artifact: `reports/campaign15_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`
- Print report to stdout with **SHA256** (verify manually)
- Record honest conclusion: `edge` / `no_edge` / `insufficient_or_blocked` with evidence (pairs evaluated, bar passes, pvalues/half-life/gates)
- If `edge` (bars_pass > 0): run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence
- Update **THIS HANDOFF** with verified UTC, commands run, artifact paths+SHA256, conclusions, and next unambiguous directive. **Do not** edit `research_state/state.yaml`.

## BOTTLENECK REMOVAL (pre-cleared for this session — no work is blocked)
- C12 complete (5/5), C13 complete (3/3), C14 complete (7/7) — no re-runs permitted except evidence-backed defect fix.
- All candidate C15 cache `.pkl`+`.meta.json` present in `data/cache/`; no network refetch needed (real cached spot only). Verified 2026-11-11T08:56:40Z UTC.
- c7-venv python present: `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`.
- `research_state/state.yaml` locked — do not touch; it cannot block C15.
- No status-only work counts toward C15; every cache must produce an artifact+SHA256 or an honest blocked conclusion with evidence.
- Stale "cache still running" claims cleared — no background process active for C14 cache #1 (90d10b87 completed 2026-11-11T08:33:45Z).

## HARD BANS
- ❌ No status-only work
- ❌ No re-runs of C1–C14 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked)
- ❌ No edits to `research_state/state.yaml`
- ❌ No early exit — all eligible C15 caches must complete unless `edge` found

## KEY FILES
- C14: `examples/run_campaign13_causal_gates.py`, `reports/campaign14_causal_per_bar_enriched_gates_{90d10b87,595e501a,4fd3e87f,74e86e8e,76dedb82,a74dcf38,749b2218}_*.json`
- C15 runner: `examples/run_campaign13_causal_gates.py` (rename output `campaign13_*` → `campaign15_*`)
- Strategy/gates: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/*.{pkl,meta.json}`
- Locked separate line (do not edit): `research_state/state.yaml`

**END OF DURABLE HANDOFF — 2026-11-11T08:56:40Z UTC.** C12 COMPLETE (5/5). C13 COMPLETE (3/3). C14 COMPLETE (7/7), zero edge found. Campaign #15 NOT STARTED — zero `reports/campaign15_causal_per_bar_enriched_gates_*` artifacts. Next: **Campaign #15 — run all eligible caches in priority order; produce artifacts+SHA256 per cache; honest conclusion per cache; validate on `edge` only with cost-aware OOS; update this handoff. No status-only work. Bottlenecks pre-cleared; heavy work is mandatory, not optional.**
