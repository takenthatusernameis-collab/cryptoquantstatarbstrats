# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T10:54:40Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state:** `python -m pytest tests/ -q` → **green (1169 passed, 2 skipped)**. C281B→C286, C288, C289 are **COMPLETE formal negative results**. **C290 (wider-universe true-5m OHLCV cross-sectional stat-arb, 26 real spot assets, 162 runs) is COMPLETE — formal negative result (NOT_TRADABLE, 0/162 edge, binding `cost_sensitivity`).** **C287 (testnet gateway) is BLOCKED by an external-only geographic CDN block and is DECOUPLED from economic progress.**
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T10:54:40Z) — C291 REAL USDT-M PERP FUNDING-CARRY / BASIS CROSS-SECTIONAL STAT-ARB: HEAVY WORK REQUIRED, NO AVOIDANCE

**Focus = C291 (economic stat-arb, derivatives).** The spot-OHLCV space is closed: C281B→C286, C288, C289 all `NOT_TRADABLE`, C289 `economic_space_closed: true`, and **C290 confirms the wider 26-asset true-5m OHLCV space is also closed (0/162 edge, binding cost_sensitivity)**. The remaining economic lever named by the prior handoff was **derivatives funding/basis**. That lever is **now reachable from this environment** — the prior "derivatives blocked" conclusion was wrong because it only probed `fapi.binance.com` (HTTP 451). The **Binance public-data archive host `data.binance.vision` serves USDT-M futures monthly klines and funding-rate archives** (not the fapi REST API), verified this session:

- `data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip` → HTTP 200 (BTCUSDT 2026-08/09/10: 397158/389713/400552 bytes; 8,928 bars/month; columns `open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore`)
- `data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip` → HTTP 200 (90–93 rows/month; columns `calc_time,funding_interval_hours,last_funding_rate`; 8h interval; real non-zero rates)
- Capability probe (read-only, all 26 C290 symbols × 3 months × 2 kinds): **24/26 fully reachable**; only `PEPEUSDT` and `UUSDT` have no USDT-M archive (404). Evidence: `reports/campaign291_derivatives_reachability_20261113T105429Z.json` (SHA `9c5231148bcf895f95b611f5cf1a76648df8742e453655a123785647f7ec36c4`), produced by `scripts/probe_c291_derivatives_archives.py`.

**Deliverable (C291):** a complete, runnable, tested, pre-registered, costed OOS economic campaign on a genuinely new data dimension (derivatives) and mechanism (funding carry + spot/perp basis):
1. **Ingest** real USDT-M futures 5m klines + 8h funding rates from the verified archives for the **24-perp universe** (C290 spot symbols minus the two without perp archives), window **2026-08-01T00:00Z → 2026-10-30T23:55Z** (26,208 5m bars). Parse the archive CSVs (header present), truncate to the window, align on exact 5m UTC timestamps. Reuse the **already-verified real C290 spot 5m cache** only as the spot leg for basis (same real data; never relabeled as new). Persist `data/cache/campaign291_perp_5m.pkl` + `.meta.json` + `.provenance.json` with **SHA256-from-bytes**, `real_data_only: true`, `fabricated_data: false`, source host/endpoint, HTTP statuses, per-symbol bar counts, funding row counts, and the recorded 404 exclusions. **No synthetic data, no relabeled old caches, no resampling.**
2. **Mechanism (new):** cross-sectional stat-arb on perps with funding cashflows and spot/perp basis. Pre-registered features (all causal, `shift(1)`, true 5m):
   - `funding_level` = last funding rate known at t−1 (8h forward-fill); score = `-funding_level` (negative funding → long carry).
   - `funding_z` = trailing z-score of funding over L funding observations; score = `-funding_z`.
   - `basis_ma` = rolling mean of `(perp_close − spot_close)/spot_close` over L 5m bars; score = `-basis_ma` (high perp premium → short perp, convergence).
   - `basis_z` = rolling z-score of basis over L; score = `-basis_z`.
   - `perp_mom` = rolling mean of perp 5m log-returns over L; score = `+perp_mom`.
   - `perp_lowvol` = rolling std of perp 5m log-returns over L; score = `-perp_lowvol`.
   - Lookbacks L ∈ {288, 1008, 2016} 5m bars; 6 features × 3 L × 3 K × 3 holds = **162 runs**.
3. **Portfolio / PnL:** long top-K / short bottom-K by score, K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, per-asset cap 0.5; hold H∈{1,6,24} 5m bars; `weights.shift(1).fillna(0.0)`; PnL on real **perp** 5m returns; **funding cashflow applied at every 8h funding timestamp to the position held across the boundary: `funding_pnl = −funding_rate × signed_weight`** (long pays when rate>0, short receives), using only funding known at/before the boundary (causal). 5m cost grid exactly `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps; walk-forward train=720/test=168/step=168 = **151 OOS splits**; benchmark = equal-weight 24-perp buy-and-hold **with the same funding cashflows** on the same WF windows. **Edge rule identical to C285/C286/C288/C290 (never relaxed):** OOS exposure>0 AND every cost slice net sum>0 AND mean per-split OOS net mean > mean per-split equal-weight B&H OOS net mean on the same WF windows. Report the full grid (no post-hoc search, no cherry-picking).
4. **Build** `scripts/ingest_c291_perp_funding.py`, `scripts/preflight_c291.py` (fail-closed: cache SHAs, 26,208×24 shape, window, no NaNs, positive prices, exact 5m spacing, funding 8h coverage ≥90 rows/asset, WF math, feature warmup), `scripts/run_c291_perp_funding_basis_xsec_oos.py` (mirror `scripts/run_c290_wider_universe_oohlcv_xsec_oos.py`), and tests `tests/test_preflight_c291.py`, `tests/test_c291_perp_funding_basis_xsec_oos.py`.
5. **Run** preflight (must print `"ready": true`) then the full sweep; emit five timestamped artifacts with SHA256-from-bytes: `reports/campaign291_oos_sweep_<ts>.json`, `campaign291_tradable_edge_registry_<ts>.json`, `campaign291_summary_<ts>.json`, `campaign291_verdict_<ts>.json`, and `campaign291_binding_constraint_<ts>.json` if NOT_TRADABLE.

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
python scripts/probe_c291_derivatives_archives.py --json   # must print ready:true (24/26)
python scripts/ingest_c291_perp_funding.py --json
python scripts/preflight_c291.py --json              # must print ready:true
python scripts/run_c291_perp_funding_basis_xsec_oos.py     # full 162-run sweep -> 5 artifacts
python -m pytest tests/ -q                            # must stay green
```
Then update `research_state/state.yaml` + this file with artifact paths + SHA256-from-bytes, and record the verdict.

**If an archive endpoint or cache check fails:** do NOT fabricate. Emit fail-closed BLOCKED C291 artifacts (exact host/status/blocked route, per-symbol coverage) with SHA256-from-bytes, add tests, update state + this handoff, keep `pytest` green. A turn without persisted artifacts + state/handoff update + green tests is a failed handoff.

**If C291 also closes:** that is a **definitive result** — record the binding-constraint artifact and `economic_space_closed: true` for the Binance spot+perp 5m space, then **escalate to C292** (also heavy, not a stop): **cross-venue real-spot basis/stat-arb** using the fallback venues verified reachable this session — OKX `https://www.okx.com/api/v5/market/history-candles` (HTTP 200), Coinbase `https://api.exchange.coinbase.com/products/BTC-USD/candles` (HTTP 200), Kraken `https://api.kraken.com/0/public/OHLC` (HTTP 200). Only after C292 also closes is the remaining lever external execution (testnet/allowed network). Do **not** loop on another Binance spot-OHLCV signal family.

**No avoidance (binding):** no status-only/planning-only/inventory-only turn. No reruns/edits of frozen artifacts C281B→C286, C288, C289, C290. No weakened gates/thresholds/cost grid/edge rule/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data, no simulated fills presented as real. Existing deps only (numpy/pandas/scipy/statsmodels/scikit-learn/aiohttp/pydantic). No `.github/workflows/main.yml` edits. No `HANDOFF.md`.

### C287 status — BLOCKED, DECOUPLED (do not let it block economic work)
`scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` exist and are runnable. Fail-closed BLOCKED artifacts were emitted 2026-11-13T09:28:33Z (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Blockers: missing `BINANCE_TESTNET_API_KEY/SECRET`; REST ping/time/exchangeInfo **HTTP 451** from `testnet.binance.vision` (CloudFront geographic block, not transient); WS TCP/TLS reachable. **Cannot be resolved from this execution environment.** **Do not re-emit C287 artifacts every session**: the prior session already emitted four duplicate sets at 10:46:32–10:46:35Z; that is wasted work and is forbidden. Re-run `--blocker-artifacts` only if new capability evidence changes.

### C291 specification (pre-registered; no post-hoc scope creep)
- **Data**: real Binance public-data archive (`data.binance.vision`): USDT-M futures 5m klines + 8h funding rates, 2026-08-01→2026-10-30T23:55Z, 24 perps (C290 spot symbols minus `PEPEUSDT`, `UUSDT`, which 404). Spot leg = verified C290 5m cache for basis. SHA256-from-bytes + meta/provenance; `real_data_only: true`, `fabricated_data: false`.
- **Features**: `funding_level`, `funding_z`, `basis_ma`, `basis_z`, `perp_mom`, `perp_lowvol`; lookbacks {288, 1008, 2016} 5m bars; min_periods `max(20, L//3)` for 5m features, `max(10, L//3)` for funding observations.
- **Portfolio**: long top-K / short bottom-K by score, K∈{2,3,5}, 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; H∈{1,6,24} 5m bars; `weights.shift(1)`; 5m cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; WF 720/168/168 = 151 splits; funding cashflow `−rate×signed_weight` at each 8h boundary.
- **Gates (fail-closed)**: score finite for ≥2K assets; cross-sectional dispersion>0; no NaN/non-finite perp or spot price in selected legs; funding staleness ≤ 24h+1 bar; basis finite where used; block & record reason otherwise; no missing/None/false treated as permissive.
- **Edge rule**: identical to C285/C286/C288/C290 (never relaxed).
- **Required artifacts**: `reports/campaign291_oos_sweep_<ts>.json`, `reports/campaign291_tradable_edge_registry_<ts>.json`, `reports/campaign291_summary_<ts>.json`, `reports/campaign291_verdict_<ts>.json` (+ `campaign291_binding_constraint_<ts>.json` if NOT_TRADABLE), each with `real_data_only: true`, `fabricated_data: false`, dataset SHAs, config, all 162 run results, and SHA256-from-bytes.

### C291 completion gate (a turn that ends without this is a failed handoff)
1. `scripts/ingest_c291_perp_funding.py`, `scripts/preflight_c291.py`, `scripts/run_c291_perp_funding_basis_xsec_oos.py` exist, executed; preflight prints `ready: true`.
2. Full 162-run sweep executed end-to-end (not smoke-only) with all five artifacts fresh + SHA256-from-bytes.
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
```
`scripts/bootstrap_dev_env.py` installs `requirements.txt` plus `pytest`, `pytest-asyncio`, `hmmlearn`, `pydantic`, and `aiohttp` with `--user`, then verifies every import. If pip has no network and deps are missing, stop with a blocker artifact; do not fabricate a result. Never edit `.github/workflows/main.yml` (the controller token cannot persist workflow-file changes and it will loop on persistence failure).

## Bottlenecks removed (this refresh)
- **Derivatives data bottleneck REMOVED:** `fapi.binance.com` is still HTTP 451, but `data.binance.vision` public futures archives are HTTP 200 (24/26 perps have 5m klines + funding for all three months). The prior handoff's "derivatives blocked here" was an incomplete probe and is corrected. Evidence: `scripts/probe_c291_derivatives_archives.py` + `reports/campaign291_derivatives_reachability_20261113T105429Z.json` (SHA `9c5231148bcf895f95b611f5cf1a76648df8742e453655a123785647f7ec36c4`), plus tests `tests/test_probe_c291_derivatives_archives.py` (8 tests, no network).
- **Stale handoff fixed:** C290 was completed at 10:43–10:47Z but `AGENTS.md` still said C290 was pending. This refresh records C290 as COMPLETE and sets C291 as the mandatory next campaign.
- **C287 re-emission loop closed:** the prior session wrote four duplicate C287 artifact sets (10:46:32–35Z); the handoff now forbids re-emitting them absent new capability evidence.
- **C290 campaign:** `scripts/preflight_c290.py` + `scripts/run_c290_wider_universe_oohlcv_xsec_oos.py` + `scripts/ingest_c290_universe.py` exist and ran end-to-end; five artifacts with SHA256-from-bytes; tests added (`tests/test_preflight_c290.py`, `tests/test_c290_wider_universe_oohlcv_xsec_oos.py`).
- **Dependency bootstrap:** `scripts/bootstrap_dev_env.py` + `scripts/verify_env.py` install and verify runtime + test imports.
- **HANDOFF.md loop:** `AGENTS.md` is the only handoff; `HANDOFF.md` is forbidden; ignore missing-file errors for it.

## Current research state (verified 2026-11-13T10:54Z)

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
| C291 | **NEXT** — real USDT-M perp funding-carry + spot/perp basis cross-sectional stat-arb, 24 perps, 151 WF splits | 162 | **REQUIRED — heavy work, no avoidance** |

Frozen evidence (C281B→C290):
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (SHA `8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (SHA `b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (SHA `e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (SHA `9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (SHA `d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); verdict `reports/campaign284_verdict_20261113T061220Z.json`; binding `reports/campaign284_binding_constraint_20261113T061220Z.json` (SHA `9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (SHA `2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (SHA `23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (SHA `512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (SHA `2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding `reports/campaign285_binding_constraint_20261113T065205Z.json` (SHA `15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
- C286: `reports/campaign286_oos_sweep_20261113T072725Z.json` (SHA `c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca`); registry `reports/campaign286_tradable_edge_registry_20261113T072725Z.json` (SHA `6f7eb06d56abbfde9273973f38264574f4d36443e127da8b55334b7fb6977d8f`); summary `reports/campaign286_summary_20261113T072725Z.json` (SHA `9f4d987e776b91a70efaaf6dbe472b7058a523dc481d74bf9bc3e99df67ae9da`); verdict `reports/campaign286_verdict_20261113T072725Z.json` (SHA `338e4b5dec412bcef32b0b37fd88865543ced68cfe0e94749247ce4bad7fb9fe`); binding `reports/campaign286_binding_constraint_20261113T072725Z.json` (SHA `b0d7f0d9e9ac67efd501fe9ae814273ad036eaa9f2534711475003f528ddcf12`).
- C288: `reports/campaign288_oos_sweep_20261113T094728Z.json` (SHA `75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d`); registry `reports/campaign288_tradable_edge_registry_20261113T094728Z.json` (SHA `8c35996e5675d151a5f3b80f4e8f4545a7cb99923adc41e0ad4fa03ef5a7c7d8`); summary `reports/campaign288_summary_20261113T094728Z.json` (SHA `fc236ad1ad51d53fe909444d02648909188b80fab8013e299140e7f292ec8eb5`); verdict `reports/campaign288_verdict_20261113T094728Z.json` (SHA `cb7f80a755a0ce84c8c2bb83ec51a7576d436fea0026303688a5aa596b94419a`); binding `reports/campaign288_binding_constraint_20261113T094728Z.json` (SHA `46248de8b9441b3c3fdcf402d8b0bba2de8bda1c25ef6f66bee085269013c763`). Verdict `NOT_TRADABLE`, 0/81.
- C289: `reports/campaign289_closure_20261113T095308Z.json` (SHA `1abf68af6f9e9d96f158b41b9a0694ed7bc9feba5afed387483bc6069d0f1b77`); summary `reports/campaign289_summary_20261113T095308Z.json` (SHA `7ed5717296df3b146fe1b87747182cc9e2e6f3cf1282e817fac9dfe8ecf09e92`); verdict `reports/campaign289_verdict_20261113T095308Z.json` (SHA `d1a7894e0c38e077d34e24a156bb1c1cfaadab0469729b1cdf1d7236243f52b5`). `economic_space_closed: true`.
- C290: `reports/campaign290_oos_sweep_20261113T104321Z.json` (SHA `e20b2ee2602134d7e15c144e30a482f1196a5ad4f995b2d72f87e9fc6d060ed8`); registry `reports/campaign290_tradable_edge_registry_20261113T104321Z.json` (SHA `f89b6af757a0df50ecb6e5ad83a851504618f664ec286b5c8a9afbdc1908397d`); summary `reports/campaign290_summary_20261113T104321Z.json` (SHA `da0eb512c72984dd5ec51ef343d80433fb15b34a70977909513d11b88d9fe8a4`); verdict `reports/campaign290_verdict_20261113T104321Z.json` (SHA `07d1f731eee9eb397ef22fcd87ae9c7d40dea753360d7af5766a656e842059b7`); binding `reports/campaign290_binding_constraint_20261113T104321Z.json` (SHA `ad8938c07324afa2e3937fcf85a27da53c2acb8497402350c791a010763b812b`). Dataset `data/cache/campaign290_ohlcv.pkl` SHA `6f06e6902e60eebabb161839e3cce4d04ea23b0dca63585a4c075f422f066f0e` (meta `5c9ff6c8473e460c30790e8854f2934af57ccdac7f3cba7e824ba04c1bcc0103`, provenance `2edde6202866d32e078b1c4497a195796de8d18ec7312161cbfd4e6640af2193`). Verdict `NOT_TRADABLE`, 0/162.
- C291 reachability evidence: `reports/campaign291_derivatives_reachability_20261113T105429Z.json` (SHA `9c5231148bcf895f95b611f5cf1a76648df8742e453655a123785647f7ec36c4`); 24/26 perps fully reachable; `PEPEUSDT`/`UUSDT` 404; fapi/testnet/api.binance.com 451; OKX/Coinbase/Kraken 200.
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
python scripts/probe_c291_derivatives_archives.py --json
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

- Derivatives/funding/basis (C291): `data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip` and `.../fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip` (HTTP 200). `fapi.binance.com` remains HTTP 451; do not use it.
- Cross-venue spot (C292 fallback): OKX `https://www.okx.com/api/v5/market/history-candles`, Coinbase `https://api.exchange.coinbase.com/products/BTC-USD/candles`, Kraken `https://api.kraken.com/0/public/OHLC` — all verified HTTP 200 from this egress.
- New spot data (C290, frozen): `data-api.binance.vision/api/v3/klines` (HTTP 200) + `data/loader.py::DataLoader.load_binance_data` + `data/real_feed_loader.py` host chain.
- Binance API/host changes → `data/real_feed_loader.py` host chain.
- Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable).
- Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285/C286/C288/C289/C290 are complete and frozen; current next campaign is **C291**.

**END OF HANDOFF — refreshed 2026-11-13T10:54:40Z.** Economic status: the 11-asset close/1h-quote-volume space (C281B→C286, C288, C289) and the wider 26-asset true-5m spot-OHLCV space (C290) are **closed**. **C287 is BLOCKED and decoupled** (testnet REST HTTP 451 + no creds; external execution only). **C291 is now unblocked:** real USDT-M futures 5m klines + 8h funding archives on `data.binance.vision` are reachable (24/26 perps, verified probe). Next session MUST build + run C291 end-to-end (heavy work), update state + this file, keep tests green; if C291 closes, run C292 cross-venue real-spot basis (OKX/Coinbase/Kraken verified reachable). **No avoidance: a status-only/planning-only turn, or substituting infra/refactor/docs for C291, is a failed handoff.**