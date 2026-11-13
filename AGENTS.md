# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T12:34:29Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **green (1184 passed, 2 skipped, last recorded at C291 close)**. C281B→C286, C288, C289, C290, **C291** are **COMPLETE formal negative results** (`NOT_TRADABLE`, 0 costed-OOS edge). **C287 (testnet gateway) is BLOCKED by an external-only geographic CDN block and is DECOUPLED from economic progress.**
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T12:34:29Z) — C292 CROSS-VENUE REAL-SPOT BASIS / LEAD-LAG STAT-ARB: MANDATORY HEAVY WORK, COMPLETE END-TO-END (NO AVOIDANCE)

**START HERE. C292 is the only active economic campaign.** Binance single-venue spot (C281B→C286/C288/C289/C290) and USDT-M perp funding/basis (C291) are **closed/NOT_TRADABLE**. Next lever = **cross-venue real spot** (same asset, different exchanges: Binance cached + OKX paginated). This session's audit found **C292 INCOMPLETE**: `scripts/ingest_c292_crossvenue_spot.py` is a partial stub only; `scripts/preflight_c292.py`, `scripts/run_c292_crossvenue_basis_xsec_oos.py`, C292 tests, cache, and all 5 report artifacts are **missing**. **Do not stop at planning, probing, or ingest-only — complete the full C292 pipeline in this turn.**

**Focus = C292 (economic stat-arb, multi-venue real spot).** The Binance single-venue space is now **closed on both spot and derivatives**: C281B→C286, C288, C289, C290 (spot OHLCV / quote-volume / true-5m OHLCV) and **C291 (real USDT-M perp funding-carry + spot/perp basis, 24 perps)** are all `NOT_TRADABLE` (C291 binding `cost_sensitivity`, gross edge only at 0bps). The next economic lever is **cross-venue real spot** — the SAME asset trading on DIFFERENT exchanges. This is a genuinely new data dimension (multi-venue) and mechanism (cross-venue basis convergence / lead-lag).

**Data reachability — VERIFIED THIS SESSION (probe, read-only):**
- **OKX** `https://www.okx.com/api/v5/market/history-candles?instId=<PAIR>&bar=5m&limit=100[&after=<ms>]` → HTTP 200; **deep 5m history** (paginate with `after=<epoch_ms>`; direct `after` at 2026-08-05/08-20/09-15 returned candles, so it reaches the window start).
- **Coinbase** `https://api.exchange.coinbase.com/products/<PAIR>/candles?granularity=300[&start=&end=]` → HTTP 200; **deep 5m history** (2026-08-01 window returns data; 300 candles/request, paginate by `start/end`).
- **Kraken** `https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=5` → HTTP 200 but **only the last 720 candles (~12h)** — **EXCLUDE Kraken at 5m**. Kraken `interval=1440` (daily) is 720 days deep, only if a daily leg is needed.
- **Binance spot 5m** is already cached (verified C290 cache `data/cache/campaign290_ohlcv.pkl`) and is reused as one venue leg (never relabeled).
- **Blocked routes (recorded, do not retry):** `fapi.binance.com`, `testnet.binance.vision`, `api.binance.com` → HTTP 451.

**Deliverable (C292):** a complete, runnable, tested, pre-registered, costed OOS economic campaign on the multi-venue real-spot basis mechanism:
1. **Ingest** real 5m spot klines for the **overlapping USDT pairs across Binance (cached) + OKX (paginated)** (optionally a Coinbase USD leg), window **2026-08-01T00:00Z → 2026-10-30T23:55Z** (26,208 5m bars), align on exact 5m UTC timestamps, persist `data/cache/campaign292_crossvenue_5m.pkl` + `.meta.json` + `.provenance.json` with **SHA256-from-bytes**, `real_data_only: true`, `fabricated_data: false`, per-venue source host/endpoint, HTTP statuses, per-asset per-venue bar counts, and recorded 404/gap exclusions. **No synthetic data, no relabeled old caches, no resampling.** Record the actual overlap (pairs present on both venues with full coverage) before any PnL is computed.
2. **Mechanism (new):** cross-venue basis convergence / lead-lag. Pre-registered causal features (`shift(1)`, true 5m):
   - `xbasis_ma` = rolling mean of `(okx_close − binance_close)/binance_close` over L 5m bars; score = `-xbasis_ma` (high OKX premium → short OKX / long Binance, convergence).
   - `xbasis_z` = rolling z-score of the cross-venue basis over L; score = `-xbasis_z`.
   - `xleadlag` = causal lead-lag: correlation of OKX 5m returns with lagged Binance 5m returns over L (or the causal spread momentum); score sign chosen to trade the lagging venue (pre-register the exact definition).
   - Lookbacks L ∈ {288, 1008, 2016} 5m bars; 3 features × 3 L × 3 K × 3 holds = **81 runs** (or 162 if you add a 6-feature set — pre-register before running; do not add features after seeing results).
3. **Portfolio / PnL:** long the discounted venue / short the premium venue on the spread; cross-sectional top-K/bottom-K by score, K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, per-asset cap 0.5; hold H∈{1,6,24} 5m bars; `weights.shift(1).fillna(0.0)`; PnL on real venue 5m returns; **cost charged on BOTH legs**; 5m cost grid exactly `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps; walk-forward train=720/test=168/step=168 = **151 OOS splits**; benchmark = equal-weight cross-venue buy-and-hold of the same pairs with the same two-leg costs on the same WF windows. **Edge rule identical to C285/C286/C288/C290/C291 (never relaxed):** OOS exposure>0 AND every cost slice net sum>0 AND mean per-split OOS net mean > mean per-split benchmark OOS net mean on the same WF windows. Report the full grid (no post-hoc search, no cherry-picking).
4. **Build** `scripts/ingest_c292_crossvenue_spot.py`, `scripts/preflight_c292.py` (fail-closed: cache SHAs, shape, window, no NaNs, positive prices, exact 5m spacing, per-venue coverage, WF math, feature warmup), `scripts/run_c292_crossvenue_basis_xsec_oos.py` (mirror `scripts/run_c291_perp_funding_basis_xsec_oos.py` / `run_c290_wider_universe_oohlcv_xsec_oos.py`), and tests `tests/test_preflight_c292.py`, `tests/test_c292_crossvenue_basis_xsec_oos.py`.
5. **Run** preflight (must print `"ready": true`) then the full sweep; emit five timestamped artifacts with SHA256-from-bytes: `reports/campaign292_oos_sweep_<ts>.json`, `campaign292_tradable_edge_registry_<ts>.json`, `campaign292_summary_<ts>.json`, `campaign292_verdict_<ts>.json`, and `campaign292_binding_constraint_<ts>.json` if NOT_TRADABLE.

**Mandatory execution path (heavy work, no status-only turn):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json          # 900000 ms shell timeout
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json
python scripts/preflight_c291.py --json              # must print ready:true
python scripts/ingest_c292_crossvenue_spot.py --json
python scripts/preflight_c292.py --json              # must print ready:true
python scripts/run_c292_crossvenue_basis_xsec_oos.py # full sweep -> 5 artifacts
python -m pytest tests/ -q                            # must stay green
```
Then update `research_state/state.yaml` + this file with artifact paths + SHA256-from-bytes, and record the verdict.

**If a venue endpoint fails or coverage is short:** do NOT fabricate. Emit fail-closed BLOCKED C292 artifacts (exact host/status/blocked route, per-symbol per-venue coverage) with SHA256-from-bytes, add tests, update state + this handoff, keep `pytest` green. A turn without persisted artifacts + state/handoff update + green tests is a failed handoff.

**If C292 also closes:** that is a **definitive result** — record the binding-constraint artifact and `economic_space_closed: true` for the Binance + OKX/Coinbase spot 5m space. The only remaining lever is then **external execution** (testnet/allowed network); record that as a definitive external-execution-only blocker (C287 evidence: testnet REST HTTP 451 + no creds). Do **not** loop on another Binance single-venue signal family.

**No avoidance (binding):** no status-only/planning-only/inventory-only turn. No reruns/edits of frozen artifacts C281B→C286, C288, C289, C290, C291. No weakened gates/thresholds/cost grid/edge rule/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data, no simulated fills presented as real. Existing deps only (numpy/pandas/scipy/statsmodels/scikit-learn/aiohttp/pydantic). No `.github/workflows/main.yml` edits. No `HANDOFF.md`.

### Bottlenecks removed this refresh (2026-11-13T12:34:29Z)
- **Stale handoff clock cleared:** refreshed to current session time so next agent cannot treat C292 as "just queued" from a prior turn.
- **Incomplete-pipeline blocker surfaced:** C292 currently has only a partial `scripts/ingest_c292_crossvenue_spot.py` stub; no preflight/runner/tests/cache/reports. This is the active execution gap and must be closed by building and running the full C292 stack end-to-end now.
- **Re-read/reprobe loops blocked:** OKX/Coinbase 5m deep history and Binance C290 cache reachability are already verified (recorded above). Do not spend the turn re-probing venues except as part of actual ingest; proceed to implementation + execution.
- **C287 decoupled:** external-only (testnet REST HTTP 451 + no creds). Do not re-emit C287 artifacts absent new capability evidence.

### C287 status — BLOCKED, DECOUPLED (do not let it block economic work)
`scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` exist and are runnable. Fail-closed BLOCKED artifacts were emitted 2026-11-13T09:28:33Z (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Blockers: missing `BINANCE_TESTNET_API_KEY/SECRET`; REST ping/time/exchangeInfo **HTTP 451** from `testnet.binance.vision` (CloudFront geographic block, not transient); WS TCP/TLS reachable. **Cannot be resolved from this execution environment.** **Do not re-emit C287 artifacts every session**; re-run `--blocker-artifacts` only if new capability evidence changes.

### C291 result — COMPLETE (formal negative result; frozen)
- **Mechanism:** real USDT-M perp funding-carry + spot/perp basis cross-sectional stat-arb, 24 perps, 6 features × 3 lookbacks × 3 K × 3 holds = 162 runs, 151 WF splits, 5 cost slices, real funding cashflows (`−rate×signed_weight` at each native 8h/4h boundary), benchmark equal-weight 24-perp B&H with the same funding.
- **Verdict:** `NOT_TRADABLE`, 0/162 edge, 162/162 with exposure, binding `cost_sensitivity` (gross edge at 0bps: max +0.3248, 77/162 positive; every run ≤0 at ≥5bps), mean gate pass share 0.988.
- **Artifacts (SHA256-from-bytes):** `reports/campaign291_oos_sweep_20261113T113705Z.json` (`5986229bbfe988e26a2b6cf21997b11ebec1b872ae581e5d5a55870ef61dd02e`), registry `campaign291_tradable_edge_registry_20261113T113705Z.json` (`354c203197be2e8a54a984ffc14f0e613ecd33dce35ab025fa23952579ab05b3`), summary `campaign291_summary_20261113T113705Z.json` (`25a3973c02ae66d61accf480a44b2e30bdba4cc9ac66ea080e839ce4f08f3a45`), verdict `campaign291_verdict_20261113T113705Z.json` (`5a55a81b280112d407df76757cf33c08ee46a3b895f83a045e5c4e5307cef244`), binding `campaign291_binding_constraint_20261113T113705Z.json` (`6c17380122c65e0cccac37b990f265cbeb65f1c2056886b7fda5098614ab29ef`).
- **Dataset:** `data/cache/campaign291_perp_5m.pkl` (`fb28f147f11dfcbcc00d5a0685c973197fb019757db885583bd06aa70a1a2487`), meta (`3abe2da3d14bf34d774c44192d1291a503fc7529b5daf0faa73ca242f7f0339f`), provenance (`6b63d012bb18968eaa59a04e47b35359ac648a4f01cbef3bf87d0b78ee5385b8`). Spot basis leg = verified C290 cache (referenced, never relabeled).
- **Scripts:** `scripts/ingest_c291_perp_funding.py`, `scripts/preflight_c291.py` (ready:true), `scripts/run_c291_perp_funding_basis_xsec_oos.py`. **Tests:** `tests/test_preflight_c291.py`, `tests/test_c291_perp_funding_basis_xsec_oos.py`.

### C292 specification (pre-registered; no post-hoc scope creep)
- **Data:** real OKX + Binance (USDT) 5m spot, window 2026-08-01→2026-10-30T23:55Z, overlapping pairs; SHA256-from-bytes + meta/provenance; `real_data_only: true`, `fabricated_data: false`; record 404/gap exclusions.
- **Features:** `xbasis_ma`, `xbasis_z`, `xleadlag`; lookbacks {288, 1008, 2016} 5m bars; min_periods `max(20, L//3)`.
- **Portfolio:** long discounted venue / short premium venue; cross-sectional K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; H∈{1,6,24} 5m bars; `weights.shift(1)`; 5m cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; WF 720/168/168 = 151 splits; cost on BOTH legs.
- **Gates (fail-closed):** per-venue per-asset finite/positive/exact-5m coverage; score finite for ≥2K assets; dispersion>0; no NaN in selected legs; no missing/None/false treated as permissive.
- **Edge rule:** identical to C285/C286/C288/C290/C291 (never relaxed).
- **Required artifacts:** `reports/campaign292_oos_sweep_<ts>.json`, `campaign292_tradable_edge_registry_<ts>.json`, `campaign292_summary_<ts>.json`, `campaign292_verdict_<ts>.json` (+ `campaign292_binding_constraint_<ts>.json` if NOT_TRADABLE), each with `real_data_only: true`, `fabricated_data: false`, dataset SHAs, config, all run results, and SHA256-from-bytes.

### C292 completion gate (a turn that ends without this is a failed handoff)
1. `scripts/ingest_c292_crossvenue_spot.py`, `scripts/preflight_c292.py`, `scripts/run_c292_crossvenue_basis_xsec_oos.py` exist, executed; preflight prints `ready: true`.
2. Full sweep executed end-to-end (not smoke-only) with all five artifacts fresh + SHA256-from-bytes.
3. `research_state/state.yaml` and this file record the result, artifact paths, and SHA256-from-bytes.
4. `python -m pytest tests/ -q` green (add/update tests for new code).

## Step 0 — dependency bootstrap and preflight (run before anything else)
The scheduled Kilo worker shell may start without the repo's Python dependencies. Run this idempotent bootstrap first, with a **900000 ms shell timeout**:
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json
python scripts/preflight_c291.py --json
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml`.

## Bottlenecks removed (this refresh)
- **Derivatives lever COMPLETE (C291):** real USDT-M perp 5m klines + native 8h/4h funding ingested from `data.binance.vision` for 24 perps; 162-run costed OOS sweep run end-to-end; formal negative result. The Binance spot+perp 5m space is now closed.
- **Native funding-interval correction:** Binance perps use variable funding intervals (19×8h, 5×4h: PUMP/TAO/TRUMP/ONDO/GRAM). Ingest floors `calc_time` to each symbol's native interval and the runner applies funding at every native boundary; this yields exactly the pre-registered 24-perp universe.
- **Cross-venue lever UNBLOCKED (C292):** verified this session that OKX 5m history-candles and Coinbase 5m candles retain deep 5m history over the window; Kraken 5m is only ~12h (1D-only). C292 is therefore buildable and is the mandatory next campaign.
- **C290 campaign (frozen):** `scripts/preflight_c290.py` + `scripts/run_c290_wider_universe_oohlcv_xsec_oos.py` + `scripts/ingest_c290_universe.py` ran end-to-end; five artifacts with SHA256-from-bytes; tests added.
- **C287 re-emission loop closed:** the prior session wrote four duplicate C287 artifact sets (10:46:32–35Z); the handoff forbids re-emitting them absent new capability evidence.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is forbidden; ignore missing-file errors for it.

## Current research state (verified 2026-11-13T11:44Z)

| Campaign | Test | Runs | Result |
|----------|------|------|--------|
| C281B | Refreshed real-spot MR/momentum/OLS-pairs, 28 WF splits, 5 cost slices | 663 | `NOT_TRADABLE`, 0 edge |
| C281C | Gate diagnostics on same data | 680 gate evals | `rolling_stable_ok` binding (0.29% pass) |
| C282 | Cross-sectional stat-arb on same data | 128 | `NOT_TRADABLE`, 0 edge |
| C283 | Turnover-reduced cointegration pairs | 17 | `NOT_TRADABLE`, 0 exposure |
| C284 | Kalman dynamic-hedge-ratio pairs, 28 WF splits, 5 cost slices | 1088 | `NOT_TRADABLE`, 0 exposure, binding: zero_exposure |
| C285 | Volume-conditioned cross-sectional stat-arb, 11 assets, 26 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C286 | 5m execution overlay of C285 signal, 26,208-bar 5m cache, causal 1h-vol, 151 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C287 | Operational hardening: Binance Spot Testnet gateway + kill-switch | — | **BLOCKED** (env: testnet REST HTTP 451 + no creds), decoupled |
| C288 | NEW realized-vol / vol-reversal / low-skew cross-sectional stat-arb, 5m close-only, 151 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity |
| C289 | OOS multiple-testing + MDE closure over C286+C288 (162 configs) | 810 tests | **`economic_space_closed: true`** (0 Holm, 0 BH; max DSR 0.0; MDE 0.106 bps ≪ 10 bps) |
| C290 | WIDER 26-asset true-5m OHLCV cross-sectional stat-arb, 151 WF splits, 5 cost slices | 162 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity (gate pass 98.6%) |
| C291 | REAL USDT-M perp funding-carry + spot/perp basis cross-sectional stat-arb, 24 perps, 151 WF splits, real funding cashflows | 162 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity (gate pass 98.8%) |
| C292 | **NEXT** — cross-venue real-spot basis / lead-lag stat-arb, Binance+OKX (USDT) 5m, cost on both legs, 151 WF splits | 81–162 | **REQUIRED — heavy work, no avoidance** |

Frozen evidence (C281B→C291):
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (SHA `2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (SHA `23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (SHA `512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (SHA `2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding `reports/campaign285_binding_constraint_20261113T065205Z.json` (SHA `15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
- C286: `reports/campaign286_oos_sweep_20261113T072725Z.json` (SHA `c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca`); registry `reports/campaign286_tradable_edge_registry_20261113T072725Z.json` (SHA `6f7eb06d56abbfde9273973f38264574f4d36443e127da8b55334b7fb6977d8f`); summary `reports/campaign286_summary_20261113T072725Z.json` (SHA `9f4d987e776b91a70efaaf6dbe472b7058a523dc481d74bf9bc3e99df67ae9da`); verdict `reports/campaign286_verdict_20261113T072725Z.json` (SHA `338e4b5dec412bcef32b0b37fd88865543ced68cfe0e94749247ce4bad7fb9fe`); binding `reports/campaign286_binding_constraint_20261113T072725Z.json` (SHA `b0d7f0d9e9ac67efd501fe9ae814273ad036eaa9f2534711475003f528ddcf12`).
- C288: `reports/campaign288_oos_sweep_20261113T094728Z.json` (SHA `75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d`); registry `reports/campaign288_tradable_edge_registry_20261113T094728Z.json` (SHA `8c35996e5675d151a5f3b80f4e8f4545a7cb99923adc41e0ad4fa03ef5a7c7d8`); summary `reports/campaign288_summary_20261113T094728Z.json` (SHA `fc236ad1ad51d53fe909444d02648909188b80fab8013e299140e7f292ec8eb5`); verdict `reports/campaign288_verdict_20261113T094728Z.json` (SHA `cb7f80a755a0ce84c8c2bb83ec51a7576d436fea0026303688a5aa596b94419a`); binding `reports/campaign288_binding_constraint_20261113T094728Z.json` (SHA `46248de8b9441b3c3fdcf402d8b0bba2de8bda1c25ef6f66bee085269013c763`). Verdict `NOT_TRADABLE`, 0/81.
- C289: `reports/campaign289_closure_20261113T095308Z.json` (SHA `1abf68af6f9e9d96f158b41b9a0694ed7bc9feba5afed387483bc6069d0f1b77`); summary `reports/campaign289_summary_20261113T095308Z.json` (SHA `7ed5717296df3b146fe1b87747182cc9e2e6f3cf1282e817fac9dfe8ecf09e92`); verdict `reports/campaign289_verdict_20261113T095308Z.json` (SHA `d1a7894e0c38e077d34e24a156bb1c1cfaadab0469729b1cdf1d7236243f52b5`). `economic_space_closed: true`.
- C290: `reports/campaign290_oos_sweep_20261113T104321Z.json` (SHA `e20b2ee2602134d7e15c144e30a482f1196a5ad4f995b2d72f87e9fc6d060ed8`); registry `reports/campaign290_tradable_edge_registry_20261113T104321Z.json` (SHA `f89b6af757a0df50ecb6e5ad83a851504618f664ec286b5c8a9afbdc1908397d`); summary `reports/campaign290_summary_20261113T104321Z.json` (SHA `da0eb512c72984dd5ec51ef343d80433fb15b34a70977909513d11b88d9fe8a4`); verdict `reports/campaign290_verdict_20261113T104321Z.json` (SHA `07d1f731eee9eb397ef22fcd87ae9c7d40dea753360d7af5766a656e842059b7`); binding `reports/campaign290_binding_constraint_20261113T104321Z.json` (SHA `ad8938c07324afa2e3937fcf85a27da53c2acb8497402350c791a010763b812b`). Dataset `data/cache/campaign290_ohlcv.pkl` SHA `6f06e6902e60eebabb161839e3cce4d04ea23b0dca63585a4c075f422f066f0e`. Verdict `NOT_TRADABLE`, 0/162.
- C291: `reports/campaign291_oos_sweep_20261113T113705Z.json` (SHA `5986229bbfe988e26a2b6cf21997b11ebec1b872ae581e5d5a55870ef61dd02e`); registry `reports/campaign291_tradable_edge_registry_20261113T113705Z.json` (SHA `354c203197be2e8a54a984ffc14f0e613ecd33dce35ab025fa23952579ab05b3`); summary `reports/campaign291_summary_20261113T113705Z.json` (SHA `25a3973c02ae66d61accf480a44b2e30bdba4cc9ac66ea080e839ce4f08f3a45`); verdict `reports/campaign291_verdict_20261113T113705Z.json` (SHA `5a55a81b280112d407df76757cf33c08ee46a3b895f83a045e5c4e5307cef244`); binding `reports/campaign291_binding_constraint_20261113T113705Z.json` (SHA `6c17380122c65e0cccac37b990f265cbeb65f1c2056886b7fda5098614ab29ef`). Dataset `data/cache/campaign291_perp_5m.pkl` SHA `fb28f147f11dfcbcc00d5a0685c973197fb019757db885583bd06aa70a1a2487` (meta `3abe2da3d14bf34d774c44192d1291a503fc7529b5daf0faa73ca242f7f0339f`, provenance `6b63d012bb18968eaa59a04e47b35359ac648a4f01cbef3bf87d0b78ee5385b8`). Reachability `reports/campaign291_derivatives_reachability_20261113T105429Z.json` (SHA `9c5231148bcf895f95b611f5cf1a76648df8742e453655a123785647f7ec36c4`). Verdict `NOT_TRADABLE`, 0/162.
- Global registry with zero tradable edge: `reports/tradable_edge_registry_20261112T172556Z.json` (SHA `62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2`).
- Pairs universe: `reports/portfolio_real.json` (17 pairs).

## Environment / verification

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json
python scripts/preflight_c291.py --json
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact records `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid plus real funding cashflows; zero-cost runs are labeled.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — economic stat-arb (costed OOS PnL) is the priority; operational hardening (C287) must not preempt or block it.

## Escalation

- Cross-venue real spot (C292, NEXT): OKX `https://www.okx.com/api/v5/market/history-candles` (5m, deep, HTTP 200), Coinbase `https://api.exchange.coinbase.com/products/<PAIR>/candles` (5m, deep, HTTP 200); Binance spot 5m cached. Kraken 5m is ~12h only → 1D `interval=1440` only.
- Derivatives/funding/basis (C291, frozen): `data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip` and `.../fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip` (HTTP 200). `fapi.binance.com` remains HTTP 451; do not use it.
- New spot data (C290, frozen): `data-api.binance.vision/api/v3/klines` (HTTP 200) + `data/loader.py::DataLoader.load_binance_data` + `data/real_feed_loader.py` host chain.
- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285/C286/C288/C289/C290/C291 are complete and frozen; current next campaign is **C292**.

**END OF HANDOFF — refreshed 2026-11-13T12:34:29Z.** Economic status: Binance single-venue spot (C281B→C286/C288/C289/C290) and real USDT-M perp funding/basis (C291) are **closed**. **C287 is BLOCKED/decoupled** (testnet REST HTTP 451 + no creds). **C292 is the sole active economic campaign and is UNFINISHED in-repo** (only partial ingest stub exists). Next session MUST complete C292 end-to-end: finish ingest, build preflight/runner/tests, execute full sweep, emit all required artifacts with SHA256-from-bytes, update state + this file, keep tests green. If C292 closes, record definitive external-execution-only blocker. **A status-only, planning-only, ingest-only, or infra-substituting turn is a failed handoff.**