# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-11T03:14:43Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C13 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T03:14:43Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Complete Campaign #13.** Campaign #12 is COMPLETE (5/5, all `no_edge`/`insufficient_or_blocked`, no edge signal). Campaign #13 targets 3 real cached-spot caches; **2/3 evaluated with timestamped artifacts+SHA256**, **1/3 (`0bab5d6a`, 11sym/55 pairs/5112 bars, 1h) is the active bottleneck** — C13 causal enriched-gate runs die repeatedly in this environment after ~6-7/55 pairs with no report emitted (logs `/tmp/c13_0bab5d6a.log`, `/tmp/c13_0bab5d6a_retry.log`, `/tmp/c13_0bab5d6a_v3.log`). **You must drive `0bab5d6a` to a timestamped `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_<UTC>.json` with SHA256 + full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes`/rationale) and honest conclusion, OR concretely evidenced `insufficient_or_blocked` with `blocked_routes` and rationale — no deferral.**

**STATE (verified 2026-11-11T03:14:43Z UTC):** `main` (`git status`: modified lint-fix files only — `examples/run_campaign12_causal_gates.py`, `examples/run_campaign13_*`, `tests/test_campaign13*.py`; no new C13 0bab5d6a report). Baseline gates re-verified this session: `pytest tests/ -q` => **1089 passed, 2 skipped** (targeted C13 385aae3f/6d2e08d4 tests: **4 passed**); `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**. Env: `/home/runner/work/_temp/kilo-tmp/c7-venv`, `PYTHONPATH=$PWD`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `research_state/state.yaml` untouched.

**C13 progress (real-data-only, no refetch, thresholds unmodified):**
- **DONE (SHA-verified):**
  - `reports/campaign13_causal_per_bar_enriched_gates_385aae3f_20261111T013410Z.json` — cache `385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba` (2sym BTC,ETH, **1h**, 5064 bars, 2026-04-01..2026-10-28). pkl SHA `d0885c3c5165fb33d6ef9731ac1cb557a353b8783bb65572031005287fbf4095`, meta SHA `1f60d88faa43a87d5881e28544573fed28d59e54926a3acc915add1a88658f26`. **Conclusion `no_edge`** (`edge_claim:false`, `honest:true`, bars_min 5064, reason "No bar passes all gates; rolling_stable_ok blocks all bars."). **Report SHA256 `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`**.
  - `reports/campaign13_causal_per_bar_enriched_gates_6d2e08d4_20261111T013412Z.json` — cache `6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383` (2sym POL,BTC, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `977ba2e94a40e4423197ce43377e229cf7d428b0d8a9cb1daf2531383f26fa28`, meta SHA `85ba6c631e3e79b8b9e1c391b7dbaafdb014e044a399c9726dad949c63778504`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, `honest:true`, bars_min 5112, reason "Mixed blocker pattern / unassessable gates on real data."). **Report SHA256 `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`**.
- **INCOMPLETE / BOTTLENECK:**
  - `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7` (11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, meta SHA `d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d`. **No `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_*.json` emitted.** Three monitored runs (`examples/run_campaign13_causal_gates.py --cache 0bab5d6a...`) started 2026-11-11T03:06Z/03:08Z/03:12Z died after reaching pairs 7/55, 7/55, 6/55 respectively (process exit, logs `/tmp/c13_0bab5d6a.log`, `/tmp/c13_0bab5d6a_retry.log`, `/tmp/c13_0bab5d6a_v3.log`); stderr dominated by statsmodels Future/Interpolation/Complex warnings, no final report path. **Must be completed with evidence (report or evidenced blocker).**

**MANDATORY HEAVY ACTION (next session, non-deferrable):**
1. **Finish C13 `0bab5d6a`:** run/restart `PYTHONPATH=$PWD /home/runner/work/_temp/kilo-tmp/c7-venv/bin/python examples/run_campaign13_causal_gates.py --cache 0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7` under monitoring until a timestamped report is written (55 pairs; heavy). On repeated death, capture concrete evidence (exit status/signal, last pair, log tail, `dmesg`/resource limits if accessible) and emit an honest `insufficient_or_blocked` artifact with `blocked_routes`/rationale if completion is impossible without fabrication — do not leave unevidenced.
2. **Collect/record:** for 0bab5d6a record report path, `sha256sum`, conclusion (`edge`/`no_edge`/`insufficient_or_blocked`), `edge_claim`, bars/gate summary, provenance (cache/pkl/meta SHAs). Ensure C13 deliverables exist per evaluated cache: timestamped `reports/campaign13_*` artifact+SHA256 recorded, `examples/run_campaign13_<cache8>_causal_gates.py` and `tests/test_campaign13_<cache8>.py` (deterministic), targeted tests run.
3. **Gates:** run `$PT tests/ -q`, `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `$PY -m mypy backtest/ strategies/ utils/` and fix regressions if any.
4. **If any gate-pass/edge signal appears:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.
5. **Update this HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`. No fabrication, no refetch, no threshold weakening.

**Hard bans:** no status-only work; no re-runs of C1–C12 except evidence-backed defect fix; no network refetch; no synthetic data; no threshold weakening; no edits to `research_state/state.yaml`.

## BOTTLENECK REMOVAL (verified 2026-11-11T03:14:43Z UTC)

- **Environment bootstrap:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` ready; `PYTHONPATH=$PWD`.
- **C12:** COMPLETE (5/5).
- **C13 385aae3f, 6d2e08d4:** CLEARED — evaluated with timestamped artifacts+SHA256 and honest conclusions; targeted tests 4 passed.
- **Lint on modified C13/C12 files:** CLEARED — ruff auto-fix + E501 fix in `examples/run_campaign12_causal_gates.py`; `ruff check` **All checks passed**, `mypy` **Success**.
- **C13 0bab5d6a evaluation:** **ACTIVE BOTTLENECK (runtime).** 55-pair enriched-gate sweep over 5112 bars repeatedly exits before report emission (~6-7 pairs done per attempt; 3 attempts logged). Next session must complete it (or produce evidenced `insufficient_or_blocked` with `blocked_routes`/rationale); consider chunked per-pair runs/aggregation if whole-run stability blocks completion, but only with real cached data, unmodified thresholds, and full provenance — no fabrication.
- **C249 emission:** EXECUTED — registry/summary present; `oos_edge_proven:false`, `edge_claim:NONE`. RQA line (`state.yaml`) SEPARATE and untouched.

## REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

# C13 0bab5d6a (finish)
$PY examples/run_campaign13_causal_gates.py --cache 0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7

# gates
$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/
```

## KEY FILES

- **C13:** `examples/run_campaign13_causal_gates.py`, `examples/run_campaign13_{0bab5d6a,385aae3f,6d2e08d4}_causal_gates.py`, `tests/test_campaign13_{0bab5d6a,385aae3f,6d2e08d4}.py`, `reports/campaign13_causal_per_bar_enriched_gates_{385aae3f,6d2e08d4}_*.json`
- **C12:** `examples/run_campaign12_causal_gates.py`, `reports/campaign12_*.json`, `tests/test_campaign12_*.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Caches (real-only, do not refetch):** `data/cache/{0bab5d6a,385aae3f,6d2e08d4}*.{pkl,meta.json}` (SHAs recorded above)

---

**END OF DURABLE HANDOFF — 2026-11-11T03:14:43Z UTC. C12 COMPLETE (5/5). C13 PARTIAL: 385aae3f `no_edge` (SHA `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`), 6d2e08d4 `insufficient_or_blocked` (SHA `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`), **0bab5d6a BOTTLENECK — no report, 3 run attempts died (~6-7/55 pairs)**. Gates green (1089 passed/2 skipped, ruff all passed, mypy Success). NEXT SESSION: complete 0bab5d6a with timestamped artifact+SHA256+honest conclusion or evidenced `insufficient_or_blocked`; record deliverables; keep gates green. NO STATUS-ONLY WORK. NO FABRICATION. NO REFETCH.**
