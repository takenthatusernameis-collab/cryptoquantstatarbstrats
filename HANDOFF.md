# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-10T23:40:00Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C12 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-10T23:40:00Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Close Campaign #12** by finishing the 2 remaining per-cache causal enriched-gate evaluations on unevaluated real caches under **unmodified gate thresholds** (no fabrication, no network refetch), then integrate all 5 cache outcomes into C12 deliverables with tests+gates green. C1–C11 exhausted the 1h `0bab5d6a...fcf7` line (`rolling_stable_ok` blocks 5112/5112). **3/5 target caches are DONE with timestamped honest artifacts+SHA256 recorded; 2/5 (90d10b, 4fd3e87f) were (re)launched this session and had not produced reports by 23:40Z — they must be run to completion and their reports SHA256-recorded.** Work is not complete until every target cache has a timestamped artifact and recorded honest outcome, required C12 deliverables/tests exist, and gates are green as feasible, OR concretely evidenced `insufficient_or_blocked`.

**STATE (verified 2026-11-10T23:40:00Z UTC):** `main`; only durable handoff `HANDOFF.md`. Baseline gates last verified 2026-11-10T22:43:28Z: `pytest tests/ -q` => **1080 passed, 1 skipped**; `ruff check ...` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success** (not re-run this session). Env: `/home/runner/work/_temp/kilo-tmp/c7-venv`, `PYTHONPATH=$PWD`, `PY=$VENV/bin/python`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `state.yaml` untouched.

**C12 progress (real-data-only, no refetch, thresholds unmodified, `examples/run_campaign12_causal_gates.py`):**
- **DONE:** `reports/campaign12_causal_per_bar_enriched_gates_595e501a_20261110T230047Z.json` — cache `595e501a...` (3sym BTC/ETH/SOL, **5m**, 26208, 2026-08-01..2026-10-30), pkl SHA `414b9cca7c785b6abf0164c0b2b2c892fbf65400631b594b84e6c17511a8c574`, meta SHA `53ce62467ea2e848d1a63d07be5d512e1b1384a67676bff6b0c5ab886c8f011f`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, reason: mixed blocker pattern/unassessable gates). **Report SHA256 `41fb84c41518e2943f67b207aea6df2ba57a9223e7431a185d3e684d39525e1b`.**
- **DONE:** `reports/campaign12_causal_per_bar_enriched_gates_4c3bc2f1_20261110T224731Z.json` — cache `4c3bc2f1...` (3sym, **1h**, 944, 2026-10-01..2026-11-09), pkl SHA `dec04f719339480ac1dce151d153d90ff385f0e7bfb95c59425ed45f5edfbb06`, meta SHA `5ad256a381afd6d1b1d39ae50092b8b8a28ebac2aab24a22ad680b5c3c7fd2b1`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `df4f561bf4a3294093ba40cad938cb6c9b25dce4dda75c70011114a8d7b2c871`.**
- **DONE:** `reports/campaign12_causal_per_bar_enriched_gates_dcd5764a_20261110T224700Z.json` — cache `dcd5764a...` (3sym, **1h**, 272, 2026-10-29..2026-11-09), pkl SHA `8404aa7f7b7ee67a635f4b1d0df334c4b442cb46c84c774ea869af81dced1fe3`, meta SHA `a78255571a3b4ed56eae31f74577a4977f507b5b3414bbec354a9169d4602c90`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `25f04e95ce3fccccfeb60542ff7d1c82794bdf247d3e13c9bccd75e5036e0d45`.** No gate-pass/edge in any completed cache.
- **PENDING (must complete):**
  - `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d` (11sym, **1h**, 5064, 2026-04-01..2026-10-28, real-only; pkl SHA `4d04e74ed1338f5b7955941603d867fe3190e31696a98f170fdc6f42e578f671`, meta SHA `621346a8feebefa6dd1ffdc76995236b663662ff8ced5cd0f26793934897fa32`). Relaunched 2026-11-10T23:38Z via `nohup $PY examples/run_campaign12_causal_gates.py --cache 4fd3e87f... > /tmp/c12_4fd3e87f.log 2>&1 &` (pid ~16405); exited/running status unconfirmed at 23:40Z, **no report produced yet**. Expect `reports/campaign12_causal_per_bar_enriched_gates_4fd3e87f_<STAMP>.json`.
  - `90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263` (11sym, **5m**, 26208, 2026-08-01..2026-10-30, real-only; pkl SHA `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`, meta SHA `e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e`). **Heavy/long-running (55 pairs).** Relaunched 2026-11-10T23:38Z via nohup (pid ~16407); exited/running status unconfirmed at 23:40Z, **no report produced yet**. Expect `reports/campaign12_causal_per_bar_enriched_gates_90d10b87_<STAMP>.json`.

**MANDATORY HEAVY ACTION (next session, non-deferrable):**
1. **Collect/finish 4fd3e87f & 90d10b:** check for `reports/campaign12_causal_per_bar_enriched_gates_4fd3e87f_*.json` and `*_90d10b87_*.json` and logs `/tmp/c12_4fd3e87f.log`, `/tmp/c12_90d10b.log`. If missing or incomplete, run to completion: `PYTHONPATH=$PWD $PY examples/run_campaign12_causal_gates.py --cache <hash>` (allow long runtime; prefer background/monitor; 90d10b 11sym×5m is heavy). Record each report path, SHA256, conclusion (`edge`/`no_edge`/`insufficient_or_blocked`), and provenance.
2. **Complete C12 deliverables:** for all 5 target caches ensure a timestamped `reports/campaign12_*` artifact with SHA256 recorded in this handoff and honest outcome (+ `blocked_routes`/rationale where applicable). If contract requires per-cache `examples/run_campaign12_<cache8>_*.py` / `tests/test_campaign12_<cache8>.py`, add deterministic ones (may wrap `examples/run_campaign12_causal_gates.py`/assert report schema) and run targeted tests.
3. **Gates:** run `$PT tests/ -q`, `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `$PY -m mypy backtest/ strategies/ utils/` and fix regressions if any.
4. **If any gate-pass/edge signal appears:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.
5. **Update this HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`. No fabrication, no refetch, no threshold weakening.

**Hard bans:** no status-only work; no re-runs of C1–C11 except evidence-backed defect fix; no network refetch; no synthetic data; no threshold weakening; no edits to `research_state/state.yaml`.

**MANDATORY HEAVY ACTION (prioritized, non-deferrable):**
1. **§0.P1 — Campaign #12 cache evaluations (required).** For each target cache: re-verify SHA256 from bytes of `data/cache/<hash>.pkl`+`.meta.json` (done 2026-11-10T21:29:15Z, all match), confirm `fetch_real_data_only:true`, `fetch_fabricated_data:false`, then run a timestamped causal per-bar enriched-gate campaign (reuse/adapt C9–C11 methodology, **thresholds unchanged**, trailing/causal, fail-closed). Produce per cache: `examples/run_campaign12_<cache8>_<UTC>.py`, `reports/campaign12_<cache8>_<UTC>.json` (SHA256 recorded, full provenance incl. `real_data_only`, `fabricated_data: false`, `blocked_routes`, rationale, per-pair/slice gate accounting, conclusion `edge`/`no_edge`/`insufficient_or_blocked`), and `tests/test_campaign12_<cache8>.py`.
   **Unevaluated real-cache targets (SHA-audited 2026-11-10T22:43:28Z, `data/cache/`):**
   - `90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263` — 11 sym (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP), **5m**, 2026-08-01..2026-10-30, 26208 rows, real-only. pkl `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`, meta `e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e`. **High priority (intraday).**
   - `595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5` — BTC,ETH,SOL, **5m**, 2026-08-01..2026-10-30, 26208 rows, real-only. pkl `414b9cca7c785b6abf0164c0b2b2c892fbf65400631b594b84e6c17511a8c574`, meta `53ce62467ea2e848d1a63d07be5d512e1b1384a67676bff6b0c5ab886c8f011f`.
   - `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d` — 11 sym, **1h**, 2026-04-01..2026-10-28, 5064 rows, real-only. pkl `4d04e74ed1338f5b7955941603d867fe3190e31696a98f170fdc6f42e578f671`, meta `621346a8feebefa6dd1ffdc76995236b663662ff8ced5cd0f26793934897fa32`.
   - `4c3bc2f1ad1323961abdc5280080e595fc9f9b5791d8b7f642a1303eac6d26cd` — BTC,ETH,SOL, **1h**, 2026-10-01..2026-11-09, 944 rows (post-Oct), real-only. pkl `dec04f719339480ac1dce151d153d90ff385f0e7bfb95c59425ed45f5edfbb06`, meta `5ad256a381afd6d1b1d39ae50092b8b8a28ebac2aab24a22ad680b5c3c7fd2b1`.
   - `dcd5764a285f56ce79d88be83a8cfaef1a8c7fad474525163816585fb2783796` — BTC,ETH,SOL, **1h**, 2026-10-29..2026-11-09, 272 rows (likely `insufficient_or_blocked` for rolling-stability windows) — **must still be evaluated and reported honestly with evidence/blocked_routes**. pkl `8404aa7f7b7ee67a635f4b1d0df334c4b442cb46c84c774ea869af81dced1fe3`, meta `a78255571a3b4ed56eae31f74577a4977f507b5b3414bbec354a9169d4602c90`.
2. **If §0.P1 yields any gate-pass/edge signal:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record `edge`/`no_edge` with full evidence.
3. **Orthogonal real-data-only strategy research** in-repo on cached real data only (not re-running C1–C11), no threshold weakening, strict provenance → code + timestamped artifact + tests. (Secondary to §0.P1.)
4. **If (1)-(3) concretely impossible:** record an evidence-backed `insufficient_or_blocked` closeout in this handoff (what searched, why blocked, no refetch/credentials/synthetic) and stop; do **not** invent work, do **not** weaken thresholds, do **not** modify `research_state/state.yaml`.

**Hard bans:** no status-only work; no re-runs of C1–C11 except evidence-backed defect fix; no network refetch; no synthetic/fabricated data; no threshold weakening; no edits to `research_state/state.yaml`. Any continuation must create new timestamped deliverables and keep gates green.

## BOTTLENECK REMOVAL (verified 2026-11-10T23:34:00Z UTC)

- **Environment bootstrap bottleneck:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` ready; `PYTHONPATH=$PWD`.
- **C12 target audit bottleneck:** CLEARED — all 5 target caches SHA/provenance audited (real-only, `fetch_fabricated_data:false`).
- **C12 evaluation bottleneck (partially cleared):** 3/5 caches evaluated with timestamped artifacts and SHAs recorded above (595e501a `insufficient_or_blocked`, 4c3bc2f1 `no_edge`, dcd5764a `no_edge`). 2/5 (90d10b87 11sym 5m 26208, 4fd3e87f 11sym 1h 5064) **relaunched 2026-11-10T23:38Z** (`/tmp/c12_90d10b.log`, `/tmp/c12_4fd3e87f.log`) but **no reports by 23:40Z** — **next session must confirm/complete runs and record report paths+SHA256s.** No gate-pass/edge observed in completed caches.
- **C249 emission bottleneck:** EXECUTED — registry/summary present; `oos_edge_proven:false`, `edge_claim:NONE`. RQA line (`state.yaml`) SEPARATE and untouched.

- **Parallel lines separated:** HANDOFF C1–C12 (enriched gates) vs `state.yaml` RQA C104–C248 (locked). Do not merge/substitute.

## NEXT FOCUS CAMPAIGN — CAMPAIGN #12 (MANDATORY; HEAVY WORK)

**Objective:** Determine whether any unevaluated real cache in `data/cache/` yields a causal per-bar enriched-gate edge (any bar passes all enriched gates under **unmodified** thresholds) on any pair across trailing configs, without weakening thresholds and without fabrication — producing honest `edge`/`no_edge`/`insufficient_or_blocked` per cache.

**Targets (5 caches, all real-only/fetch_fabricated_data:false):** `90d10b...` (11sym,5m,26208,Aug–Oct), `595e501...` (3sym,5m,26208,Aug–Oct), `4fd3e87...` (11sym,1h,5064,Apr–Oct28), `4c3bc2f...` (3sym,1h,944,Oct1–Nov9), `dcd5764...` (3sym,1h,272,Oct29–Nov9; may be `insufficient_or_blocked` for rolling windows — must be evidenced).

**Mandatory deliverables per cache evaluated (no status-only work):**
- `examples/run_campaign12_<cache8>_<UTC>.py` — causal per-bar gate script (real cache only, no network refetch, no synthetic)
- `reports/campaign12_<cache8>_<UTC>.json` — timestamped artifact + SHA256 + full provenance (`real_data_only`, `fabricated_data: false`, `blocked_routes`, rationale)
- `tests/test_campaign12_<cache8>.py` — deterministic test asserting schema/provenance and recording the outcome
- SHA256 of all new artifacts recorded in this handoff

**Completion gate (non-negotiable):** Session NOT complete until every target cache is either evaluated with timestamped campaign + tests + gates green, OR concretely evidenced as `insufficient_or_blocked` with `blocked_routes` and rationale. Then update **only** `HANDOFF.md` with UTC timestamp, commands run, artifact paths + SHA256, gate outcomes, findings, and the next unambiguous heavy directive.

**Future-agent lock:** Do not substitute status-only work, threshold weakening, fabrication, or re-runs of C1–C11 for Campaign #12. Campaign #12 cannot be deferred, bypassed, or marked complete without the per-cache deliverables above and gates green on every target cache (or evidenced `insufficient_or_blocked`).

### READY STATE (verified context)

- **Env:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (python/pytest/ruff/mypy) — **bootstrapped and green**. Use `PYTHONPATH=$PWD`. Re-verified 2026-11-10T22:43:28Z UTC.
- **Cached real spot (do not refetch):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (SHA256 `56075733...f5f8c9b` / `d03556ba...d2d80d`; ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars). Volume cache present.
- **No exchange/testnet creds and no public historical L2/intrabar replay.** Honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale only — never fabricate.

#### BOOTSTRAP

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### SESSION COMPLETION CONTRACT (NON-NEGOTIABLE)

- **NOT COMPLETE** until you produce verified real-data artifacts/tests/code with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials/threshold-weakening.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

## 1) VERIFIED BASELINE SNAPSHOT (2026-11-10T21:42:29Z; baseline re-verified 2026-11-10T22:43:28Z)

- **Repo:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#11:** COMPLETE (honest/evidence-first). C11 confirms structural blocker on cached-real enriched-gate line.
- **Gates (re-verified this session):** `pytest tests/ -q` => **1080 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**.
- **This session (bottleneck removal):** emitted C249 registry `reports/strategy_edge_registry_20261110T170949Z.json` (SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`) and summary `reports/campaign249_execution_summary_20261110T170949Z.json` (SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`); C249 `oos_edge_proven: False`, `edge_claim: NONE`.
- **RQA locked (separate, untouched):** `research_state/state.yaml` C104–C248, `next_campaign: C249`, `oos_edge_proven: false`. NOT edited.

## 2) CAMPAIGN OUTCOMES (REFERENCE)

| Campaign | State | Notes / key artifacts |
|---|---|---|
| #1 Regime-adaptive signal generation | COMPLETE | `reports/regime_adaptive_sweep.json` |
| #2 Funding/basis-carry + LOB/intrabar feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py` |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py` |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json` |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json` |
| #7 Operator deployment hardening | COMPLETE | config/observability/playbooks/reconciliation + artifacts; gates green |
| #8 Stat-arb edge hardening & honest real-data extension | COMPLETE (`no_edge`) | `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py` |
| #9 Enriched-gate causal/per-bar edge discovery & robustness | COMPLETE (`no_edge`) | `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`), `tests/test_campaign9_causal_gate_edge_search.py` |
| #10 Wider-universe causal per-bar gate validation | COMPLETE (`insufficient_or_blocked`) | `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json` (SHA256 `8c3c5d5785c0d7bd33c805f939528771809494dba400e6f990d269dd3369b895`), `tests/test_campaign10_wider_universe_causal_gates.py` |
| **#11 Rolling-stability blocker diagnosis & gate-pass feasibility** | **COMPLETE (`no_edge`)** | `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py` |

## 3) CAMPAIGN #11 — EXECUTION RECORD (COMPLETE)

**Objective:** On cached real data only, determine whether `rolling_stable_ok` trailing-window insufficiency is the sole structural blocker (no bar passes all enriched gates on any wider-universe pair under unmodified thresholds) or whether any pair/slice ever achieves a causal per-bar gate pass, across trailing sample lengths/check intervals, **without weakening gate thresholds**.

**Constraints honored:** No network refetch, no synthetic/fabricated data/labels/metrics/fills/IV/volume. Gate thresholds unmodified. `research_state/state.yaml` RQA line untouched. Campaigns #1–#10 not redone.

**Deliverables:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`.

**Findings (honest, reproducible):** conclusion `no_edge` (edge_claim false). No bar passes all enriched gates on any wider-universe pair under swept configs with unmodified thresholds. `rolling_stable_ok` blocks **5112/5112 bars** across pairs/sweeps (structural blocker confirmed). Cached-aggregate and causal-per-bar paths agree (fail-closed). No positive OOS/replay edge; zero gate-pass slices => cost-aware evaluation not possible. Cached-real/gate research line exhausted under current gate schema/thresholds without fabricating data/trades/edge.

## 4) REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/
```

## 5) KEY FILES

- **C11:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`
- **C10:** `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json`, `tests/test_campaign10_wider_universe_causal_gates.py`
- **C9:** `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json`, `tests/test_campaign9_causal_gate_edge_search.py`
- **C8:** `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`

---

**END OF DURABLE HANDOFF — CAMPAIGNS #1–#11 COMPLETE (`no_edge` on cached-real enriched-gate line). C249 EXECUTED (`oos_edge_proven:false`, `edge_claim:NONE`, RQA locked/untouched). C12: 3/5 DONE (595e501a `insufficient_or_blocked` SHA `41fb84c4...`, 4c3bc2f1 `no_edge` SHA `df4f561b...`, dcd5764a `no_edge` SHA `25f04e95...`); 2/5 (4fd3e87f, 90d10b) relaunched 23:38Z, reports pending — NEXT SESSION MUST finish them, record SHA256s, add per-cache deliverables/tests if required, run gates, and update HANDOFF only. NO STATUS-ONLY WORK.**
