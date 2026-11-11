# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (updated 2026-11-11T05:22:56Z UTC). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C14 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T05:22:56Z UTC; UPDATED 2026-11-11T07:10Z UTC)

**Initial task (execute immediately, heavy work, no status-only):** Campaign #13 is COMPLETE (3/3 evaluated, all with timestamped artifacts+SHA256 and honest conclusions). **Bottlenecks removed — none remain.** Next unambiguous heavy focus: **Campaign #14 — causal gate edge search on wider universe with real-data-only enforcement.** Campaign #14 IN PROGRESS — 6/7 caches complete (all honest `no_edge`/`insufficient_or_blocked`, zero edge found). **ONLY CACHE #1 (90d10b87) REMAINS — it is the heaviest (11 sym, 5m, 26208 bars) and is still running in background.** Do **NOT** summarize state; finish cache #1 then update this handoff with all 7 results.

**C14 RESULTS SO FAR (verified 2026-11-11T07:10Z UTC):**
| # | Cache8 | SHA256 | Conclusion |
|---|--------|--------|------------|
| 1 | 90d10b87 | **PENDING** (running) | — |
| 2 | 595e501a | `cf4c6cabc68a179d6391bc4dedebcf23d4c060c685ee3563af44b4fceeb7530e` | insufficient_or_blocked |
| 3 | 4fd3e87f | `aaf7a2ca32cb5b884e239f5daf3804270cb31d971cb47c802ed6dcf8187c9c84` | insufficient_or_blocked |
| 4 | 74e86e8e | `657ecf30b12a30839f08372e41275b4cbaec9f65a4400bfb57ba1071a9218bd4` | insufficient_or_blocked |
| 5 | 76dedb82 | `1902a2c2ed6b5e0ad6d275983e1b1e31c0226fef15d2bf3e18fbe4460543cd1e` | insufficient_or_blocked |
| 6 | a74dcf38 | `123b866fda7977aea4d13fe9c4edd04b0366838bc77b43cd56378534da402c9d` | no_edge (rolling_stable_ok blocks all bars) |
| 7 | 749b2218 | `e9631e325dd617efef53ec64ead0d105746d5abd0669ee0bd2017098058fad1d` | insufficient_or_blocked |

All artifacts: `reports/campaign14_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`. Runner writes `campaign13_*` prefix by design — copy/rename to `campaign14_*` after each run. No edge found in any completed cache; no cost-aware OOS validation triggered.

**Verified state (2026-11-11T05:22:56Z UTC):** `main` @ `22ca033` (HEAD), prior handoff baseline `4fed0a3`; working tree was clean at check. Gates (prior verified): `pytest tests/ -q` => **1089 passed, 2 skipped, 15 failed (pre-existing, unrelated)**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**. Env: venv `/home/runner/work/_temp/kilo-tmp/c7-venv` (Python 3.12.3) present, deps expected ok; use `export PYTHONPATH=$PWD` and `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`. All 7 Campaign #14 cache `.pkl`+`.meta.json` present in `data/cache/`. Runner exists: `examples/run_campaign13_causal_gates.py`. `research_state/state.yaml` untouched (locked RQA line). No blockers identified for Campaign #14 heavy execution.

**C13 final (verified):**
- `reports/campaign13_causal_per_bar_enriched_gates_385aae3f_20261111T013410Z.json` (SHA256 `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`) — BTC,ETH 1h — **no_edge**
- `reports/campaign13_causal_per_bar_enriched_gates_6d2e08d4_20261111T013412Z.json` (SHA256 `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`) — POL,BTC 1h — **insufficient_or_blocked**
- `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_20261111T040502Z.json` (SHA256 `0113bb115395a5d908e715cc246dce009ebf9c7d5867f8d1fd865b6255610b69`) — 11sym 1h, 55/55 pairs, 0 bar passes — **insufficient_or_blocked**

## MANDATORY HEAVY ACTION — CAMPAIGN #14 (NON-DEFERRABLE)

**Priority order (7 caches). Execute in this exact order. Each run MUST produce a timestamped artifact + SHA256. Stop ONLY if `edge` found (then run cost-aware OOS validation immediately). ALL 7 must complete otherwise.**

| Priority | Cache8 | Full hash | Symbols | Interval | Bars | Window |
|----------|--------|-----------|---------|----------|------|--------|
| 1 | `90d10b87` | `90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263` | 11: ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP | 5m | 26208 | 2026-08-01..2026-10-30 |
| 2 | `595e501a` | `595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5` | 3: BTC,ETH,SOL | 5m | 26208 | 2026-08-01..2026-10-30 |
| 3 | `4fd3e87f` | `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d` | 11: ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP | 1h | 5064 | 2026-04-01..2026-10-28 |
| 4 | `74e86e8e` | `74e86e8e4b0a7933c26fc9328b8b753711f3ab76e2333a44b6057856699eec1a` | 6: BTC,POL,ETH,XRP,AVAX,LTC | 1h | 5112 | 2026-04-01..2026-10-30 |
| 5 | `76dedb82` | `76dedb82e6b94ca7f326484a09194c2b3eb557d0477cd04c607b146fd1b74a0d` | 3: BTC,ETH,SOL | 1h | 5112 | 2026-04-01..2026-10-30 |
| 6 | `a74dcf38` | `a74dcf38854ff20d174609ceffba98d555ec4498d23446ce031a247c8c12bc6e` | 3: BTC,ETH,POL | 1h | 5064 | 2026-04-01..2026-10-28 |
| 7 | `749b2218` | `749b221871e0e42146ebe66b03069eaeeeef57f2c8570ba81f2fc3c435b9eeee` | 3: BTC,ETH,SOL | 1h | 5064 | 2026-04-01..2026-10-28 |

**Run (from repo root):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python

$PY examples/run_campaign13_causal_gates.py --cache 90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263
$PY examples/run_campaign13_causal_gates.py --cache 595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5
$PY examples/run_campaign13_causal_gates.py --cache 4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d
$PY examples/run_campaign13_causal_gates.py --cache 74e86e8e4b0a7933c26fc9328b8b753711f3ab76e2333a44b6057856699eec1a
$PY examples/run_campaign13_causal_gates.py --cache 76dedb82e6b94ca7f326484a09194c2b3eb557d0477cd04c607b146fd1b74a0d
$PY examples/run_campaign13_causal_gates.py --cache a74dcf38854ff20d174609ceffba98d555ec4498d23446ce031a247c8c12bc6e
$PY examples/run_campaign13_causal_gates.py --cache 749b221871e0e42146ebe66b03069eaeeeef57f2c8570ba81f2fc3c435b9eeee
```

**Per-cache requirements:**
- Produce timestamped artifact: `reports/campaign14_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`
- Print report to stdout with **SHA256** (verify manually)
- Record honest conclusion: `edge` / `no_edge` / `insufficient_or_blocked` with evidence (pairs evaluated, bar passes, pvalues/half-life/gates)
- If `edge` (bars_pass > 0): run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence
- Update **THIS HANDOFF** with verified UTC, commands run, artifact paths+SHA256, conclusions, and next unambiguous directive. **Do not** edit `research_state/state.yaml`.

## BOTTLENECK REMOVAL (pre-cleared for this session — no work is blocked)
- C12 complete (5/5), C13 complete (3/3) — no re-runs permitted except evidence-backed defect fix.
- Lint/typecheck green; 15 pre-existing test failures unrelated to campaign work — do not treat as blockers.
- All 7 campaign14 cache files present in `data/cache/`; no network refetch needed (real cached spot only).
- `research_state/state.yaml` locked — do not touch; it cannot block C14.
- No status-only work counts toward C14; every cache must produce an artifact+SHA256 or an honest blocked conclusion with evidence.

## HARD BANS
- ❌ No status-only work
- ❌ No re-runs of C1–C13 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked)
- ❌ No edits to `research_state/state.yaml`
- ❌ No early exit — all 7 caches must complete unless `edge` found

## KEY FILES
- C13: `scripts/run_campaign13_0bab5d6a_chunked.py`, `examples/run_campaign13_{0bab5d6a,385aae3f,6d2e08d4}_causal_gates.py`, `reports/campaign13_causal_per_bar_enriched_gates_{385aae3f,6d2e08d4,0bab5d6a}_*.json`
- Strategy/gates: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/{0bab5d6a,385aae3f,6d2e08d4,90d10b87,595e501a,4fd3e87f,74e86e8e,76dedb82,a74dcf38,749b2218}*.{pkl,meta.json}`

**END OF DURABLE HANDOFF — 2026-11-11T05:22:56Z UTC.** C12 COMPLETE (5/5). C13 COMPLETE (3/3). Campaign #14 NOT STARTED — zero `reports/campaign14_causal_per_bar_enriched_gates_*` artifacts. Next: **Campaign #14 — run all 7 caches in priority order; produce artifacts+SHA256 per cache; honest conclusion per cache; validate on `edge` only with cost-aware OOS; update this handoff. No status-only work. Bottlenecks pre-cleared; heavy work is mandatory, not optional.**
