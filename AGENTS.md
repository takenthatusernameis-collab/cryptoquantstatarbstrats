# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T19:20:55Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **green (1211 passed, 2 skipped, recorded at C293 close)**. C281B→C286, C288, C289, C290, C291, C292, **C293** are **COMPLETE formal negative results** (`NOT_TRADABLE`, 0 costed-OOS edge). **C287 (testnet gateway) is BLOCKED by an external-only geographic CDN block and is DECOUPLED from economic progress.**
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T19:09:06Z) — C293 CROSS-VENUE PERP FUNDING-CARRY STAT-ARB: MANDATORY HEAVY WORK, COMPLETE END-TO-END (NO AVOIDANCE)

**START HERE. C293 is the only active economic campaign.** Binance single-venue spot (C281B→C286/C288/C289/C290), single-venue USDT-M perp funding/basis (C291), and cross-venue real **spot** basis/lead-lag (C292, 25 pairs, 81 runs) are all **COMPLETE = NOT_TRADABLE** (binding `cost_sensitivity`). The sole untested economic lever is **cross-venue PERP FUNDING carry**: the same asset's funding rate on OKX USDT-M perp vs Binance USDT-M perp. Real cashflows (long one perp / short the other), new data dimension, new mechanism.

**INGEST IS ALREADY DONE AND REPRODUCED (2026-11-13T19:05:41Z).** Do NOT rerun the ingest — the cache is frozen and re-running only rewrites the meta timestamp. Verified this session: `scripts/ingest_c293_crossvenue_funding.py` ran to completion and reproduced a **byte-identical** pkl to the committed one.
- `data/cache/campaign293_crossvenue_funding.pkl` — SHA256-from-bytes `ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554`
- `data/cache/campaign293_crossvenue_funding.meta.json` — SHA256 `c24ba0d2607972e36ef88024d504f3512ef6b774c886b41af01e5ee5f8945265`
- `data/cache/campaign293_crossvenue_funding.provenance.json` — SHA256 `df3b211679264bc2048ec15faaa2f2b603bf4f7c70c6164daaa8ef732fabb2d6`
- **Shape:** 24 symbols × **23,424 5m bars**, window **2026-08-10T16:00:00Z → 2026-10-30T23:55:00Z**, `real_data_only: true`, `fabricated_data: false`, `excluded_symbols: {}`.
- **Measured per-symbol native funding coverage (the gate the preflight MUST enforce):** 8h symbols have 244 native points (BNB **only 129** — Binance-side gap); 4h symbols have 488 (TAO **244** OKX-side gap, ONDO **423**, PUMP **451**). These four symbols are PARTIAL on one venue and must be excluded fail-closed with a recorded reason, or gated out, before any PnL. Do not silently forward-fill partial funding into cashflows.
- Cache keys: `symbols`, `okx_instids`, `binance_closes`, `okx_closes`, `binance_funding_rates`, `okx_funding_rates`, `binance_funding_intervals_by_symbol`, `window_start_utc`, `window_end_utc`, `n_bars`, `universe_binance`, `excluded_symbols`.

**Remaining heavy work (this is the whole next turn — not planning, not status):**
1. **Build `scripts/preflight_c293.py`** — fail-closed, prints `"ready": true` only when: pkl/meta/provenance SHAs match the values above; shape `(23424, 24)`; window exact; closes have **zero NaN**; per-symbol native funding-boundary alignment (OKX 8h; Binance 8h/4h from `binance_funding_intervals_by_symbol`); per-venue coverage gate (exclude/flag BNB, TAO, ONDO, PUMP with reasons); WF math `n_splits == (n_bars-720-168)//168 + 1` with `n_bars=23424`; feature warmup ≥ max lookback. No missing/None/false treated as permissive.
2. **Build `scripts/run_c293_crossvenue_funding_xsec_oos.py`** mirroring `scripts/run_c291_perp_funding_basis_xsec_oos.py`. Features on the funding spread, `shift(1)` then ffill to 5m: `xfr_spread_ma` = −rolling-mean(okx−binance) over L; `xfr_spread_z` = −rolling-z(okx−binance) over L; `xfr_leadlag` = −rolling-mean((okx−binance).shift(1)) over L. **L ∈ {8,24,60} funding observations**, `min_periods = max(3, L//3)`. Portfolio: cross-sectional K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; H∈{1,6,24} 5m bars; `weights.shift(1).fillna(0.0)`; PnL = `r_binance − r_okx` **plus real funding cashflows on BOTH legs** (`-okx_rate*w_okx - binance_rate*w_binance` at native boundaries); **cost on BOTH legs**; cost grid exactly `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps; WF **train=720/test=168/step=168**; benchmark = equal-weight cross-venue funding-carry B&H with the same two-leg costs on the same WF windows. **Edge rule identical to C285/C286/C288/C290/C291/C292 (never relaxed):** OOS exposure>0 AND every cost slice net sum>0 AND mean per-split OOS net mean > mean per-split benchmark OOS net mean. Report the full grid (no post-hoc search).
3. **Add tests** `tests/test_preflight_c293.py` and `tests/test_c293_crossvenue_funding_xsec_oos.py`.
4. **Run** preflight (`ready:true`) then the full sweep; emit five timestamped artifacts with SHA256-from-bytes: `reports/campaign293_oos_sweep_<ts>.json`, `campaign293_tradable_edge_registry_<ts>.json`, `campaign293_summary_<ts>.json`, `campaign293_verdict_<ts>.json`, and `campaign293_binding_constraint_<ts>.json` if NOT_TRADABLE.
5. **Update** `research_state/state.yaml` + this file with verdict/paths/SHAs.

**Mandatory execution path (heavy work, no status-only turn):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json          # 900000 ms shell timeout (deps verified ready 2026-11-13T19:05Z)
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json
python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json
python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json
python scripts/preflight_c291.py --json
python scripts/preflight_c292.py --json
# DO NOT rerun ingest_c293 (cache frozen at the SHA above).
python scripts/preflight_c293.py --json              # must print ready:true
python scripts/run_c293_crossvenue_funding_xsec_oos.py # full sweep -> 5 artifacts
python -m pytest tests/ -q                            # must stay green
```

**C293 RESULT (2026-11-13T19:20:48Z):** `NOT_TRADABLE`, 0/81 edge, 72/81 with exposure, binding `cost_sensitivity`. All five artifacts emitted with SHA256-from-bytes. Tests added and passing. **The entire reachable real-data 5m spot+perp (single-venue and cross-venue) economic space is now CLOSED: `economic_space_closed: true`.** The only remaining lever is external execution (C287 testnet gateway), blocked by geographic CDN (HTTP 451) and missing credentials.

**If C293 closes:** that is a **definitive result** — record the binding-constraint artifact and `economic_space_closed: true` for the entire reachable real-data 5m spot + perp (single-venue and cross-venue) space. The only remaining lever is then **external execution** (testnet/allowed network); record that as a definitive external-execution-only blocker (C287 evidence: testnet REST HTTP 451 + no creds). Do **not** loop on another single-venue signal family.

**No avoidance (binding):** no status-only/planning-only/inventory-only turn. No reruns/edits of frozen artifacts C281B→C286, C288, C289, C290, C291, C292. No weakened gates/thresholds/cost grid/edge rule/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data, no simulated fills presented as real. Existing deps only (numpy/pandas/scipy/statsmodels/scikit-learn/aiohttp/pydantic). No `.github/workflows/main.yml` edits. No `HANDOFF.md`.

### Bottlenecks removed (this refresh, 2026-11-13T19:05:41Z)
- **C293 ingest bottleneck removed:** the prior handoff falsely claimed no `data/cache/*c293*` existed. In fact the ingest had already been committed; this session **re-ran it and reproduced a byte-identical pkl** (`ea4e5f17…`), confirming the cache is real, deterministic, and frozen. The next agent must NOT rerun the ingest; go straight to preflight → runner → sweep.
- **Partial-coverage data facts surfaced** (BNB/TAO/ONDO/PUMP) so the next preflight cannot be blocked by a naive all-or-nothing coverage assert — gate per symbol fail-closed and record exclusions.
- **C287 decoupled (external-only):** testnet REST HTTP 451 + no creds. Do not re-emit C287 artifacts absent new capability evidence. **`HANDOFF.md` absent and forbidden** (`AGENTS.md` only). No workflow edits.

### C287 status — BLOCKED, DECOUPLED (do not let it block economic work)
`scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` exist and are runnable. Fail-closed BLOCKED artifacts were emitted 2026-11-13T09:28:33Z (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Blockers: missing `BINANCE_TESTNET_API_KEY/SECRET`; REST ping/time/exchangeInfo **HTTP 451** from `testnet.binance.vision` (CloudFront geographic block, not transient); WS TCP/TLS reachable. **Cannot be resolved from this execution environment.** **Do not re-emit C287 artifacts every session**; re-run `--blocker-artifacts` only if new capability evidence changes.

### C292 result — COMPLETE (formal negative result; frozen)
- **Mechanism:** cross-venue real-spot basis / lead-lag cross-sectional stat-arb, Binance (cached C290) + OKX (paginated 5m), 25 overlapping USDT pairs, 3 features (`xbasis_ma`, `xbasis_z`, `xleadlag`) × 3 lookbacks {288,1008,2016} × 3 K {2,3,5} × 3 holds {1,6,24} = 81 runs, 151 WF splits, 5 cost slices, cost on BOTH legs, benchmark equal-weight cross-venue B&H with the same two-leg costs.
- **Verdict:** `NOT_TRADABLE`, 0/81 edge, 81/81 with exposure, binding `cost_sensitivity` (gross 0bps: 17/81 net positive; 0/81 all-slices net positive; 0/81 beat B&H; benchmark B&H OOS mean 1.36e-08).
- **Artifacts (SHA256-from-bytes):** `reports/campaign292_oos_sweep_20261113T164603Z.json` (`02854406654b921f00a438f32db651a07d24a8c87c16826b38ddc677788c0b7f`), registry `campaign292_tradable_edge_registry_20261113T164603Z.json` (`5ea904d1e26deb18af44dbadb15a8f5a041f198ed8f97474a98bcf58cc1cf7a1`), summary `campaign292_summary_20261113T164603Z.json` (`59c29e041f4fd23ca3e9c2f9ad30dbf47637018f1fef7243275055eb14ab2d38`), verdict `campaign292_verdict_20261113T164603Z.json` (`5e46cfcbefb7a217175db7b886c26b6551adb32ff67e1e3fac7a245a0c808af1`), binding `campaign292_binding_constraint_20261113T164603Z.json` (`21ae1a686ff4c66bd4d8c75ef34983ec6cb6a06fc2595776a3a192fcc5c5e8bf`).
- **Dataset:** `data/cache/campaign292_crossvenue_5m.pkl` (`aa0448517ac36145141ab69a4c83ef94dbbcecaf090a04420222ae3e98117975`), meta (`77342481c4095358c5f385074791f722ff6b3565050c9209222855086290efa6`), provenance (`ab243df7be7b1711046b8c82ce0eb447387e2e5a99f601f4d8e57db603b58e26`). 25 pairs; UUSDT excluded (OKX no_data). Binance leg = verified C290 cache (referenced, never relabeled).
- **Scripts:** `scripts/ingest_c292_crossvenue_spot.py`, `scripts/preflight_c292.py` (ready:true), `scripts/run_c292_crossvenue_basis_xsec_oos.py`. **Tests:** `tests/test_preflight_c292.py`, `tests/test_c292_crossvenue_basis_xsec_oos.py`.

### C293 result — COMPLETE (formal negative result; frozen)
- **Mechanism:** cross-venue USDT-M perp funding-carry cross-sectional stat-arb, Binance (C291 cache) + OKX (paginated funding-rate-history), 20 active symbols (4 excluded for partial coverage: BNBUSDT, ONDOUSDT, PUMPUSDT, TAOUSDT), 3 features (`xfr_spread_ma`, `xfr_spread_z`, `xfr_leadlag`) × 3 lookbacks {8, 24, 60} × 3 K {2, 3, 5} × 3 holds {1, 6, 24} = 81 runs, 135 WF splits (720/168/168), 5 cost slices, cost on BOTH legs, real funding cashflows on both legs, benchmark equal-weight cross-venue funding-carry B&H with the same two-leg costs.
- **Verdict:** `NOT_TRADABLE`, 0/81 edge, 72/81 with exposure, binding `cost_sensitivity`.
- **Artifacts (SHA256-from-bytes):** `reports/campaign293_oos_sweep_20261113T192048Z.json` (`38b20984f4ac366daf299a93a1519ca227bf064d9043f42e90da36659241f5bd`), registry `campaign293_tradable_edge_registry_20261113T192048Z.json` (`13bd97a1818116933c90eb40378949857c5a3daac00ff61f9ead33968d73b7a4`), summary `campaign293_summary_20261113T192048Z.json` (`b04c38a2f71c75795268e10f29cfad31efd0f3d81fb6c5adff47c2d9228fc695`), verdict `campaign293_verdict_20261113T192048Z.json` (`d2c0a0859084751098b347a55dce76cb0c25d5127df20d52e360a8aa4719d613`), binding `campaign293_binding_constraint_20261113T192048Z.json` (`13a8ce2ba1cc25d3be712eb08f9cade80db1fe6364efd7a15c5a2f03116b9aa3`).
- **Dataset:** `data/cache/campaign293_crossvenue_funding.pkl` (`ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554`), meta (`c24ba0d2607972e36ef88024d504f3512ef6b774c886b41af01e5ee5f8945265`), provenance (`df3b211679264bc2048ec15faaa2f2b603bf4f7c70c6164daaa8ef732fabb2d6`). 24 symbols (20 active, 4 excluded); window 2026-08-10T16:00Z → 2026-10-30T23:55Z; 23,424 5m bars; `real_data_only: true`.
- **Scripts:** `scripts/ingest_c293_crossvenue_funding.py`, `scripts/preflight_c293.py` (ready:true), `scripts/run_c293_crossvenue_funding_xsec_oos.py`. **Tests:** `tests/test_preflight_c293.py`, `tests/test_c293_crossvenue_funding_xsec_oos.py`.

### C293 specification (pre-registered; no post-hoc scope creep)
- **Data:** real OKX USDT-M perp funding-rate history (public endpoint, paginated) + Binance USDT-M funding (C291 cache) over the common window ≈2026-08-10→2026-10-30T23:55Z; aligned on native funding boundaries; SHA256-from-bytes + meta/provenance; `real_data_only: true`, `fabricated_data: false`; record 404/gap exclusions.
- **Features:** `xfr_spread_ma`, `xfr_spread_z`, `xfr_leadlag`; lookbacks {8, 24, 60} funding observations; min_periods `max(3, L//3)`.
- **Portfolio:** cross-sectional K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; H∈{1,6,24} 5m bars; `weights.shift(1)`; cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; WF 720/168/168; cost on BOTH legs; real funding cashflows on both legs.
- **Gates (fail-closed):** per-venue per-perp funding finite/aligned/native-boundary coverage; score finite for ≥2K assets; dispersion>0; no NaN in selected legs; no missing/None/false treated as permissive.
- **Edge rule:** identical to C285/C286/C288/C290/C291/C292 (never relaxed).
- **Required artifacts:** `reports/campaign293_oos_sweep_<ts>.json`, `campaign293_tradable_edge_registry_<ts>.json`, `campaign293_summary_<ts>.json`, `campaign293_verdict_<ts>.json` (+ `campaign293_binding_constraint_<ts>.json` if NOT_TRADABLE), each with `real_data_only: true`, `fabricated_data: false`, dataset SHAs, config, all run results, and SHA256-from-bytes.

### C293 completion gate (a turn that ends without this is a failed handoff)
1. `scripts/ingest_c293_crossvenue_funding.py`, `scripts/preflight_c293.py`, `scripts/run_c293_crossvenue_funding_xsec_oos.py` exist, executed; preflight prints `ready: true`.
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
python scripts/preflight_c292.py --json
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml`.

## Bottlenecks removed (this refresh, 2026-11-13T18:52:28Z)
- **Cross-venue spot lever COMPLETE (C292):** real Binance+OKX 5m ingested (25 pairs), preflight ready:true, 81-run costed OOS sweep run end-to-end, five SHA256-from-bytes artifacts, tests added. The Binance single-venue spot/perp space and the cross-venue spot 5m basis family are now closed.
- **C292 build bugs fixed (see above):** browser UA (OKX 403), pandas-3.1 µs unit (epoch-ms reindex), and zero-volume false-exclusion (positive prices / non-negative volume). These are reusable lessons for any future OKX ingest.
- **C290/C291 (frozen):** wider 26-asset 5m OHLCV and real USDT-M perp funding+basis campaigns completed with SHA256-from-bytes artifacts; tests added.
- **C287 re-emission loop closed:** the prior session wrote four duplicate C287 artifact sets (10:46:32–35Z); the handoff forbids re-emitting them absent new capability evidence.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is forbidden; ignore missing-file errors for it.

## Current research state (verified 2026-11-13T19:20Z)

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
| C292 | Cross-venue real-spot basis / lead-lag stat-arb, Binance+OKX (USDT) 5m, 25 pairs, cost on both legs, 151 WF splits | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity (17/81 gross positive) |
| C293 | Cross-venue PERP funding-carry stat-arb, OKX + Binance USDT-M funding, cost on both legs, WF 720/168/168 | 81 | `NOT_TRADABLE`, 0 edge, binding: cost_sensitivity (72/81 with exposure) |

Frozen evidence (C281B→C292):
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
- C292: `reports/campaign292_oos_sweep_20261113T164603Z.json` (SHA `02854406654b921f00a438f32db651a07d24a8c87c16826b38ddc677788c0b7f`); registry `reports/campaign292_tradable_edge_registry_20261113T164603Z.json` (SHA `5ea904d1e26deb18af44dbadb15a8f5a041f198ed8f97474a98bcf58cc1cf7a1`); summary `reports/campaign292_summary_20261113T164603Z.json` (SHA `59c29e041f4fd23ca3e9c2f9ad30dbf47637018f1fef7243275055eb14ab2d38`); verdict `reports/campaign292_verdict_20261113T164603Z.json` (SHA `5e46cfcbefb7a217175db7b886c26b6551adb32ff67e1e3fac7a245a0c808af1`); binding `reports/campaign292_binding_constraint_20261113T164603Z.json` (SHA `21ae1a686ff4c66bd4d8c75ef34983ec6cb6a06fc2595776a3a192fcc5c5e8bf`). Dataset `data/cache/campaign292_crossvenue_5m.pkl` SHA `aa0448517ac36145141ab69a4c83ef94dbbcecaf090a04420222ae3e98117975` (meta `77342481c4095358c5f385074791f722ff6b3565050c9209222855086290efa6`, provenance `ab243df7be7b1711046b8c82ce0eb447387e2e5a99f601f4d8e57db603b58e26`). Verdict `NOT_TRADABLE`, 0/81, 25 pairs.
- C293: `reports/campaign293_oos_sweep_20261113T192048Z.json` (SHA `38b20984f4ac366daf299a93a1519ca227bf064d9043f42e90da36659241f5bd`); registry `reports/campaign293_tradable_edge_registry_20261113T192048Z.json` (SHA `13bd97a1818116933c90eb40378949857c5a3daac00ff61f9ead33968d73b7a4`); summary `reports/campaign293_summary_20261113T192048Z.json` (SHA `b04c38a2f71c75795268e10f29cfad31efd0f3d81fb6c5adff47c2d9228fc695`); verdict `reports/campaign293_verdict_20261113T192048Z.json` (SHA `d2c0a0859084751098b347a55dce76cb0c25d5127df20d52e360a8aa4719d613`); binding `reports/campaign293_binding_constraint_20261113T192048Z.json` (SHA `13a8ce2ba1cc25d3be712eb08f9cade80db1fe6364efd7a15c5a2f03116b9aa3`). Dataset `data/cache/campaign293_crossvenue_funding.pkl` SHA `ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554` (meta `c24ba0d2607972e36ef88024d504f3512ef6b774c886b41af01e5ee5f8945265`, provenance `df3b211679264bc2048ec15faaa2f2b603bf4f7c70c6164daaa8ef732fabb2d6`). Verdict `NOT_TRADABLE`, 0/81, 20 active symbols (4 excluded).
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
python scripts/preflight_c292.py --json
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**pandas 3.x datetime note:** a UTC `DatetimeIndex` defaults to **microsecond** resolution (`datetime64[us, UTC]`). Never assume `view("int64")` is nanoseconds; convert explicitly to the target unit (see `scripts/ingest_c292_crossvenue_spot.py::to_epoch_ms`).

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

- Cross-venue perp funding (C293, ACTIVE — ingest done): OKX `https://www.okx.com/api/v5/public/funding-rate-history?instId=<SYM>-USDT-SWAP&limit=100[&after=<fundingTime_ms>]` (HTTP 200, browser UA, ~95-day depth to ~2026-08-10, returns list of dicts); Binance USDT-M funding cached in `data/cache/campaign291_perp_5m.pkl`. C293 cache `data/cache/campaign293_crossvenue_funding.pkl` (SHA `ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554`).
- Cross-venue spot (C292, frozen): OKX `https://www.okx.com/api/v5/market/history-candles` (5m, deep, HTTP 200 with browser UA); Coinbase `https://api.exchange.coinbase.com/products/<PAIR>/candles` (5m, deep, HTTP 200); Binance spot 5m cached. Kraken 5m is ~12h only → 1D `interval=1440` only.
- Derivatives/funding/basis (C291, frozen): `data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip` and `.../fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip` (HTTP 200). `fapi.binance.com` remains HTTP 451; do not use it.
- New spot data (C290, frozen): `data-api.binance.vision/api/v3/klines` (HTTP 200) + `data/loader.py::DataLoader.load_binance_data` + `data/real_feed_loader.py` host chain.
- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285/C286/C288/C289/C290/C291/C292 are complete and frozen; current next campaign is **C293**.

**END OF HANDOFF — refreshed 2026-11-13T19:09:06Z.** Economic status: Binance single-venue spot (C281B→C286/C288/C289/C290), real USDT-M perp funding/basis (C291), and cross-venue real-spot basis/lead-lag (C292) are **closed/NOT_TRADABLE** (frozen). **C287 is BLOCKED/decoupled** (testnet REST HTTP 451 + no creds). **C293 is the sole active economic campaign and its INGEST IS DONE + REPRODUCED/FROZEN** (`data/cache/campaign293_crossvenue_funding.pkl` SHA `ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554`, meta `c24ba0d2…`, provenance `df3b2116…`, 24 symbols × 23,424 5m bars, window 2026-08-10T16:00Z→2026-10-30T23:55Z, `real_data_only: true`). **Remaining (must complete in one turn): `scripts/preflight_c293.py` (`ready:true`), `scripts/run_c293_crossvenue_funding_xsec_oos.py` end-to-end (not smoke-only), 5 artifacts with SHA256-from-bytes, tests `tests/test_preflight_c293.py` + `tests/test_c293_crossvenue_funding_xsec_oos.py`, keep `pytest -q` green, and update `research_state/state.yaml` + this file with verdict/paths/SHAs.** Do NOT rerun the ingest. Gate partial-coverage symbols (BNB/TAO/ONDO/PUMP) fail-closed with recorded reasons. If C293 closes, record the binding-constraint artifact and definitive `economic_space_closed: true` for reachable real-data 5m spot+perp (single & cross-venue) with external-execution-only blocker noted (C287). **A status-only, planning-only, ingest-only, or infra-substituting turn is a failed handoff.**