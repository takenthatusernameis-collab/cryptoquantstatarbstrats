# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-13T19:58:11Z
**Repository priority:** `cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress means **costed out-of-sample PnL on real, provable data**, not infrastructure activity, status reports, or quote-volume return metrics.
**Verified state (this refresh):** `python -m pytest tests/ -q` → **green (1211 passed, 2 skipped, 108s)**. C281B→C286, C288, C289, C290, C291, C292, **C293** are **COMPLETE formal negative results** (`NOT_TRADABLE`, 0 costed-OOS edge). The entire reachable **real-data 5m spot + perp (single-venue and cross-venue)** space is closed (`economic_space_closed: true`). **C287 (testnet gateway) is BLOCKED by an external-only geographic CDN block + no credentials and is DECOUPLED from economic progress.**
**Single-handoff rule:** `AGENTS.md` is the only durable handoff. `HANDOFF.md` is forbidden: do not read, create, or edit it. If a tool reports `HANDOFF.md` missing, ignore it.

## INITIAL TASK MESSAGE (2026-11-13T19:58:11Z) — C294 REAL IMPLIED-VOLATILITY (Deribit DVOL) VOL-RISK-PREMIUM / RELATIVE-VALUE STAT-ARB: MANDATORY HEAVY WORK, END-TO-END (NO AVOIDANCE)

**START HERE. C294 is the only active economic campaign.** The 5m spot+perp space is closed, but a genuinely new **asset class** is now reachable and was previously marked `blocked_no_real_feed`: **real implied volatility** from Deribit. This is a new data dimension (real option IV, not a realized-vol proxy) and a new economic mechanism (variance risk premium / vol carry / BTC-ETH relative value). Verified reachable this session (2026-11-13T19:54–19:58Z, browser UA):
- Deribit DVOL index (real 30-day constant-maturity implied vol) — **HTTP 200**, BTC & ETH, `resolution=3600` (1h); a request returns the most recent ~1000 points in the window → **paginate by moving `end_timestamp` backwards** (BTC 1h reaches ≥2022-04-22; record actual earliest).
- Deribit historical realized vol — **HTTP 200** (BTC & ETH).
- Deribit option book summary (real per-strike/expiry mark IV) — **HTTP 200**; BTC 978 / ETH 790 live option instruments.
- Binance BTC/ETH spot 1h — **HTTP 200** (`data-api.binance.vision/api/v3/klines`), for realized-vol computation and the real-cashflow relative-value leg.
- Blocked (do not use): `fapi.binance.com` 451, `testnet.binance.vision` 451 (C287); `api.bybit.com` 403. OKX/Coinbase spot 5m remain 200 but are NOT needed for C294.

**Deliverables (this is the whole next turn — not planning, not status, not ingest-only):**
1. **Ingest `scripts/ingest_c294_deribit_dvol.py`** → `data/cache/campaign294_deribit_dvol.pkl` + `.meta.json` + `.provenance.json` (SHA256-from-bytes), `real_data_only: true`, `fabricated_data: false`. Pull DVOL 1h for BTC & ETH as deep as Deribit allows (paginate; see pagination note below); a recorded option-chain snapshot (`mark_iv`, `underlying_price`, `instrument_name`, `mid_price`); **Binance BTC/ETH 1h closes** (real, deep) for realized-vol computation and the real-cashflow leg. **Compute realized vol from Binance BTC/ETH 1h closes** — Deribit `get_historical_volatility` is shallow (~16 days) and is a recorded cross-check only, NOT the backtest RV. Store aligned 1h frames. Record `iv_definition: deribit_dvol_index` (real IV, NOT realized-vol proxy). Record any gaps/404s; do not forward-fill across DVOL gaps.
2. **Preflight `scripts/preflight_c294.py`** — fail-closed, prints `"ready": true` only when: pkl/meta/provenance SHAs match; finite DVOL & realized-vol for **both** assets with no gap-fill; native 1h alignment across DVOL / RV / spot; per-asset coverage gate (both full; record any partial with reason); **real-IV provenance check** (reuse `data/real_feed_loader.py::_check_term_structure_not_realized_vol_proxy` — refuse realized-vol mislabeled as IV); WF math `n_splits == (n_bars-720-168)//168 + 1`; feature warmup ≥ max lookback. No missing/None/false treated as permissive.
3. **Runner `scripts/run_c294_deribit_dvol_vrp_xsec_oos.py`** (mirror `scripts/run_c291_perp_funding_basis_xsec_oos.py` structure):
   - Features on DVOL/RV, `shift(1)` then align to 1h: `iv_rv_spread` = DVOL − trailing realized vol over L; `iv_z` = rolling-z(DVOL) over L; `dvol_x_spread` = DVOL_BTC − DVOL_ETH (z over L). **L ∈ {24, 168, 720} 1h bars**, `min_periods = max(3, L//3)`.
   - Portfolio: cross-sectional **K=2** (BTC vs ETH), 0.5/K per leg, gross 1.0, dollar-neutral, cap 0.5; **H ∈ {1, 6, 24} 1h bars**; `weights.shift(1).fillna(0.0)`.
   - PnL — two reported, both real-input:
     - **Real-cashflow leg (primary edge claim):** spot relative-value `w_btc*r_btc − w_eth*r_eth` from **real** Binance BTC/ETH 1h returns; **cost on BOTH legs**.
     - **Variance-swap-proxy leg (diagnostic, explicitly labeled):** `notional*(RV_realized² − IV_entry²)*sign(w)` over horizon from **real** DVOL/RV; artifact records `pnl_model: variance_swap_proxy`, `executed_fills: false`, `inputs: real_dvol_iv+real_realized_vol`; cost on vol notional.
   - Cost grid exactly `[[0,0],[5,5],[10,10],[20,20],[40,40]]` bps; WF **train=720/test=168/step=168** 1h bars; benchmarks = always-long-vol (short VRP) B&H **and** BTC-vs-ETH B&H with the same costs on the same WF windows.
   - **Edge rule identical to C285/C286/C288/C290/C291/C292/C293 (never relaxed):** OOS exposure>0 AND every cost slice net sum>0 AND mean per-split OOS net mean > mean per-split benchmark OOS net mean. Report the full grid (no post-hoc search).
4. **Tests:** `tests/test_preflight_c294.py` + `tests/test_c294_deribit_dvol_vrp_xsec_oos.py`.
5. **Emit five timestamped artifacts with SHA256-from-bytes:** `reports/campaign294_oos_sweep_<ts>.json`, `campaign294_tradable_edge_registry_<ts>.json`, `campaign294_summary_<ts>.json`, `campaign294_verdict_<ts>.json`, and `campaign294_binding_constraint_<ts>.json` if NOT_TRADABLE. Each records `real_data_only: true`, `fabricated_data: false`, dataset SHAs, config, all run results.
6. **Update** `research_state/state.yaml` + this file with verdict/paths/SHAs; keep `python -m pytest tests/ -q` green.

**Mandatory execution path (heavy work, no status-only turn):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py --json          # 900000 ms shell timeout
python scripts/verify_env.py --json
python scripts/preflight_c285.py --json && python scripts/preflight_c286.py --json
python scripts/preflight_c288.py --json && python scripts/preflight_c289.py --json
python scripts/preflight_c290.py --json && python scripts/preflight_c291.py --json
python scripts/preflight_c292.py --json && python scripts/preflight_c293.py --json
python scripts/ingest_c294_deribit_dvol.py          # build the real-IV cache
python scripts/preflight_c294.py --json             # must print ready:true
python scripts/run_c294_deribit_dvol_vrp_xsec_oos.py # full sweep -> 5 artifacts
python -m pytest tests/ -q                           # must stay green
```

**C294 completion gate (a turn that ends without this is a failed handoff):**
1. Ingest, preflight (`ready:true`), and runner exist and executed end-to-end (not smoke-only).
2. Five artifacts fresh with SHA256-from-bytes; `economic_space_closed` claim either upheld for a new asset class or an edge found.
3. `research_state/state.yaml` + this file record the result, paths, SHAs.
4. `python -m pytest tests/ -q` green (tests added for new code).

**If C294 closes (NOT_TRADABLE):** record the binding constraint; the real-IV VRP family is then also closed. **Queued next campaign C295** = three-venue real 5m spot cross-sectional stat-arb (Binance + OKX + **Coinbase**, all HTTP 200) to test the `economic_space_closed` claim on a genuinely new venue/market structure. **If C294 finds a costed OOS edge:** escalate to external execution (C287) — still blocked by testnet REST HTTP 451 + no creds — do not fabricate fills.

**No avoidance (binding):** no status-only/planning-only/inventory-only/ingest-only turn. No reruns/edits of frozen artifacts C281B→C293. No weakened gates/thresholds/cost grid/edge rule/drift tolerance/cherry-picking. No synthetic/fabricated/relabeled data; no simulated fills presented as real (the variance-swap-proxy leg must be explicitly labeled `executed_fills: false`). Existing deps only (numpy/pandas/scipy/statsmodels/scikit-learn/aiohttp/pydantic). No `.github/workflows/main.yml` edits. No `HANDOFF.md`.

### Bottlenecks removed (this refresh, 2026-11-13T19:58:11Z)
- **Contradictory handoff removed:** the prior `AGENTS.md` said C293 was COMPLETE at the top but still ordered the next agent to BUILD C293 below — causing loop/avoidance. This file now has **one** forward task (C294) and records C293 as frozen/complete.
- **`state.yaml` synced:** prior `state.yaml` still said `next_campaign: C293` and `campaign293.status: required_pending_heavy_work`. Updated to C293 complete + C294 next.
- **Real-IV feed bottleneck removed:** the repo's `term_structure_real_iv_vol_surface` family was `blocked_no_real_feed`. Deribit DVOL (real implied vol, BTC/ETH, 1h, deep) is now **verified reachable** — the family is unblocked and becomes C294.
- **C293 verified complete (frozen):** artifacts present, SHAs match, 0/81 edge, binding `cost_sensitivity`, 72/81 with exposure, suite green.
- **C287 decoupled (external-only):** testnet REST HTTP 451 + no creds. Do not re-emit C287 artifacts absent new capability evidence.

### C287 status — BLOCKED, DECOUPLED (do not let it block economic work)
`scripts/preflight_c287.py` (exit 2, 4 blockers) and `scripts/run_c287_testnet_gateway.py` exist and are runnable. Fail-closed BLOCKED artifacts were emitted 2026-11-13T09:28:33Z (gateway_spec `a7ceeba9280183d6a9a2d96451f033ddeeb99b69051443dfaa5d6e81c7223c25`, live_run `3596a15cf226f1fd8f6abd710f5ecf8a4a38fc93a82fdbf421a61bbb15e8b234`, drift_report `d8a2ec515f36235d8aa121e66a739e671abf42a6adcaae237641f08b9710cf0c`, kill_switch_test `88be9bd4ae06d3f86f04f324bf54f01923ed9d7666dd85caf79225e3936f58f2`, summary `2635b45e50e2544671388271ef15f898884a9a38a1a0b3aa5f10a783c3a07c20`). Blockers: missing `BINANCE_TESTNET_API_KEY/SECRET`; REST ping/time/exchangeInfo **HTTP 451** from `testnet.binance.vision` (CloudFront geographic block, not transient); WS TCP/TLS reachable. **Cannot be resolved from this execution environment.** Re-run `--blocker-artifacts` only if new capability evidence changes.

## Current research state (verified 2026-11-13T19:58Z)

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
| **C294** | **Real Deribit DVOL implied-vol VRP / BTC-ETH relative-value stat-arb, 1h, real cashflow leg + labeled variance-swap proxy, WF 720/168/168** | **pending** | **ACTIVE — next heavy campaign** |

### Frozen evidence (C281B→C293) — paths + SHA256-from-bytes
- C281B: `reports/campaign281_oos_sweep_20261113T034058Z.json` (`8c266cae6fa43f9c249b568f7420dafb4c3cc11acd2db8cb001fbb5278a1fea9`); verdict `reports/campaign281_verdict_20261113T034058Z.json`.
- C281C: `reports/campaign281c_gate_diagnostics_20261113T034422Z.json` (`b88b4dfa3513c376318b3d90ab4a5c6dbd5809ae27cecc71046f6b5e13e16265`).
- C282: `reports/campaign282_oos_sweep_20261113T043542Z.json` (`e727dcfb876b40d4206fea7da860574dd5d3fe5f117e79f5fc89f970f299c090`); verdict `reports/campaign282_verdict_20261113T043542Z.json`.
- C283: `reports/campaign283_oos_sweep_20261113T034830Z.json` (`9202d6f5a965ce4b3d1820bbd7fbf25d93a726fdfda3854a22d7e60ce6149ae0`); verdict `reports/campaign283_verdict_20261113T034830Z.json`.
- C284: `reports/campaign284_oos_sweep_20261113T061220Z.json` (`d1eb2e2c2337b72f2c3899616b8b022258235d506796894281a9f1b725623c26`); binding `reports/campaign284_binding_constraint_20261113T061220Z.json` (`9bf7eea9029b268a5a1cc671e6b1814ddd405baf43b8d36d81ea83289a0cac14`).
- C285: `reports/campaign285_oos_sweep_20261113T065205Z.json` (`2cb3ea9716f2cc59c0debce68bfd58217d58b7ca464ad8f86b25ac1bcd4477fc`); registry `reports/campaign285_tradable_edge_registry_20261113T065205Z.json` (`23cfb01fc1567918090f7ebd849f4389557b6a52b18397f39fce8b05fb4e6ff3`); summary `reports/campaign285_summary_20261113T065205Z.json` (`512bbb4b75f30eb26d6969e1fb135a481b9bfe892f52c39185d021802405cdbb`); verdict `reports/campaign285_verdict_20261113T065205Z.json` (`2e64ccf3fda6e423b7b098b2cf093430054e537227739ff6fa27aa6bbd76ce4b`); binding `reports/campaign285_binding_constraint_20261113T065205Z.json` (`15f29a2fe1e6b03fbff8454ed1ad024f943f298afa7d6943c146f9f65dc60e9a`).
- C286: `reports/campaign286_oos_sweep_20261113T072725Z.json` (`c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca`); registry `reports/campaign286_tradable_edge_registry_20261113T072725Z.json` (`6f7eb06d56abbfde9273973f38264574f4d36443e127da8b55334b7fb6977d8f`); summary `reports/campaign286_summary_20261113T072725Z.json` (`9f4d987e776b91a70efaaf6dbe472b7058a523dc481d74bf9bc3e99df67ae9da`); verdict `reports/campaign286_verdict_20261113T072725Z.json` (`338e4b5dec412bcef32b0b37fd88865543ced68cfe0e94749247ce4bad7fb9fe`); binding `reports/campaign286_binding_constraint_20261113T072725Z.json` (`b0d7f0d9e9ac67efd501fe9ae814273ad036eaa9f2534711475003f528ddcf12`).
- C288: `reports/campaign288_oos_sweep_20261113T094728Z.json` (`75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d`); registry `reports/campaign288_tradable_edge_registry_20261113T094728Z.json` (`8c35996e5675d151a5f3b80f4e8f4545a7cb99923adc41e0ad4fa03ef5a7c7d8`); summary `reports/campaign288_summary_20261113T094728Z.json` (`fc236ad1ad51d53fe909444d02648909188b80fab8013e299140e7f292ec8eb5`); verdict `reports/campaign288_verdict_20261113T094728Z.json` (`cb7f80a755a0ce84c8c2bb83ec51a7576d436fea0026303688a5aa596b94419a`); binding `reports/campaign288_binding_constraint_20261113T094728Z.json` (`46248de8b9441b3c3fdcf402d8b0bba2de8bda1c25ef6f66bee085269013c763`).
- C289: `reports/campaign289_closure_20261113T095308Z.json` (`1abf68af6f9e9d96f158b41b9a0694ed7bc9feba5afed387483bc6069d0f1b77`); summary `reports/campaign289_summary_20261113T095308Z.json` (`7ed5717296df3b146fe1b87747182cc9e2e6f3cf1282e817fac9dfe8ecf09e92`); verdict `reports/campaign289_verdict_20261113T095308Z.json` (`d1a7894e0c38e077d34e24a156bb1c1cfaadab0469729b1cdf1d7236243f52b5`). `economic_space_closed: true`.
- C290: `reports/campaign290_oos_sweep_20261113T104321Z.json` (`e20b2ee2602134d7e15c144e30a482f1196a5ad4f995b2d72f87e9fc6d060ed8`); registry `reports/campaign290_tradable_edge_registry_20261113T104321Z.json` (`f89b6af757a0df50ecb6e5ad83a851504618f664ec286b5c8a9afbdc1908397d`); summary `reports/campaign290_summary_20261113T104321Z.json` (`da0eb512c72984dd5ec51ef343d80433fb15b34a70977909513d11b88d9fe8a4`); verdict `reports/campaign290_verdict_20261113T104321Z.json` (`07d1f731eee9eb397ef22fcd87ae9c7d40dea753360d7af5766a656e842059b7`); binding `reports/campaign290_binding_constraint_20261113T104321Z.json` (`ad8938c07324afa2e3937fcf85a27da53c2acb8497402350c791a010763b812b`). Dataset `data/cache/campaign290_ohlcv.pkl` (`6f06e6902e60eebabb161839e3cce4d04ea23b0dca63585a4c075f422f066f0e`).
- C291: `reports/campaign291_oos_sweep_20261113T113705Z.json` (`5986229bbfe988e26a2b6cf21997b11ebec1b872ae581e5d5a55870ef61dd02e`); registry `reports/campaign291_tradable_edge_registry_20261113T113705Z.json` (`354c203197be2e8a54a984ffc14f0e613ecd33dce35ab025fa23952579ab05b3`); summary `reports/campaign291_summary_20261113T113705Z.json` (`25a3973c02ae66d61accf480a44b2e30bdba4cc9ac66ea080e839ce4f08f3a45`); verdict `reports/campaign291_verdict_20261113T113705Z.json` (`5a55a81b280112d407df76757cf33c08ee46a3b895f83a045e5c4e5307cef244`); binding `reports/campaign291_binding_constraint_20261113T113705Z.json` (`6c17380122c65e0cccac37b990f265cbeb65f1c2056886b7fda5098614ab29ef`). Dataset `data/cache/campaign291_perp_5m.pkl` (`fb28f147f11dfcbcc00d5a0685c973197fb019757db885583bd06aa70a1a2487`, meta `3abe2da3d14bf34d774c44192d1291a503fc7529b5daf0faa73ca242f7f0339f`, provenance `6b63d012bb18968eaa59a04e47b35359ac648a4f01cbef3bf87d0b78ee5385b8`).
- C292: `reports/campaign292_oos_sweep_20261113T164603Z.json` (`02854406654b921f00a438f32db651a07d24a8c87c16826b38ddc677788c0b7f`); registry `reports/campaign292_tradable_edge_registry_20261113T164603Z.json` (`5ea904d1e26deb18af44dbadb15a8f5a041f198ed8f97474a98bcf58cc1cf7a1`); summary `reports/campaign292_summary_20261113T164603Z.json` (`59c29e041f4fd23ca3e9c2f9ad30dbf47637018f1fef7243275055eb14ab2d38`); verdict `reports/campaign292_verdict_20261113T164603Z.json` (`5e46cfcbefb7a217175db7b886c26b6551adb32ff67e1e3fac7a245a0c808af1`); binding `reports/campaign292_binding_constraint_20261113T164603Z.json` (`21ae1a686ff4c66bd4d8c75ef34983ec6cb6a06fc2595776a3a192fcc5c5e8bf`). Dataset `data/cache/campaign292_crossvenue_5m.pkl` (`aa0448517ac36145141ab69a4c83ef94dbbcecaf090a04420222ae3e98117975`, meta `77342481c4095358c5f385074791f722ff6b3565050c9209222855086290efa6`, provenance `ab243df7be7b1711046b8c82ce0eb447387e2e5a99f601f4d8e57db603b58e26`).
- C293: `reports/campaign293_oos_sweep_20261113T192048Z.json` (`38b20984f4ac366daf299a93a1519ca227bf064d9043f42e90da36659241f5bd`); registry `reports/campaign293_tradable_edge_registry_20261113T192048Z.json` (`13bd97a1818116933c90eb40378949857c5a3daac00ff61f9ead33968d73b7a4`); summary `reports/campaign293_summary_20261113T192048Z.json` (`b04c38a2f71c75795268e10f29cfad31efd0f3d81fb6c5adff47c2d9228fc695`); verdict `reports/campaign293_verdict_20261113T192048Z.json` (`d2c0a0859084751098b347a55dce76cb0c25d5127df20d52e360a8aa4719d613`); binding `reports/campaign293_binding_constraint_20261113T192048Z.json` (`13a8ce2ba1cc25d3be712eb08f9cade80db1fe6364efd7a15c5a2f03116b9aa3`). Dataset `data/cache/campaign293_crossvenue_funding.pkl` (`ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554`, meta `c24ba0d2607972e36ef88024d504f3512ef6b774c886b41af01e5ee5f8945265`, provenance `df3b211679264bc2048ec15faaa2f2b603bf4f7c70c6164daaa8ef732fabb2d6`).
- Global registry with zero tradable edge: `reports/tradable_edge_registry_20261112T172556Z.json` (`62258e98bbc1f907858101ca785062bfe4788d57d4f32f79e3a2c6aa3783efc2`). Pairs universe: `reports/portfolio_real.json` (17 pairs).

## C294 data source — Deribit real implied volatility (verified reachable 2026-11-13T19:54–19:58Z, browser UA)
- **DVOL index (real 30-day constant-maturity implied vol):** `GET https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={BTC|ETH}&start_timestamp=<ms>&end_timestamp=<ms>&resolution=3600` — HTTP 200; `result.data = [[ts_ms, open, high, low, close], ...]` (use `close`). **Pagination:** a request returns the **most recent ~1000 points within [start,end]**; to go deeper, page by moving `end_timestamp` backwards (verified: BTC 1h DVOL reaches **≥2022-04-22**; record the actual earliest). Only BTC & ETH return DVOL (SOL/XRP/BNB/... return 0 points).
- **Realized vol (RV):** Deribit `GET .../get_historical_volatility?currency={BTC|ETH}` is **SHALLOW (~384 points ≈ 16 days)** — do NOT use it for the backtest. Compute RV from **real Binance BTC/ETH 1h closes** (`data-api.binance.vision/api/v3/klines`, deep) over the same window; keep the Deribit RV pull only as a recorded cross-check.
- **Option chain snapshot (real per-strike/expiry mark IV):** `GET https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency={BTC|ETH}&kind=option` — HTTP 200; BTC 978 / ETH 790 live instruments; record `instrument_name`, `mark_iv`, `underlying_price`, `mid_price`.
- **Spot 1h (real):** `GET https://data-api.binance.vision/api/v3/klines?symbol={BTCUSDT|ETHUSDT}&interval=1h` — HTTP 200.
- **Real-IV provenance rule:** `data/real_feed_loader.py::_check_term_structure_not_realized_vol_proxy` refuses realized-vol mislabeled as IV. DVOL is genuine implied vol (`iv_definition: deribit_dvol_index`) — it passes; a realized-vol proxy does not.

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
python scripts/preflight_c293.py --json
```

Known-good: Python 3.12, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may not be installed in the runtime shell; do not claim they passed unless actually run.

**pandas 3.x datetime note:** a UTC `DatetimeIndex` defaults to **microsecond** resolution (`datetime64[us, UTC]`). Never assume `view("int64")` is nanoseconds; convert explicitly to the target unit (see `scripts/ingest_c292_crossvenue_spot.py::to_epoch_ms`).

**CI dependency note:** the scheduled agent-loop worker can start without numpy/pandas/scipy/statsmodels/hmmlearn/pydantic/aiohttp. Run the Step 0 bootstrap before running campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix it by editing `.github/workflows/main.yml`.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact records `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid plus real funding/cashflow legs; zero-cost runs are labeled; any model PnL (e.g. variance-swap proxy) is explicitly labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward with all pre-registered configs reported, OOS/IS degradation tracked.
6. **TESTS MUST PASS** — any new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and the state fields in `research_state/state.yaml`; do not create a competing handoff.
8. **ECONOMIC PRIORITY** — economic stat-arb (costed OOS PnL) is the priority; operational hardening (C287) must not preempt or block it.

## Escalation

- **C294 (ACTIVE):** Deribit DVOL / historical-vol / option book summary (endpoints above, HTTP 200, browser UA); Binance BTC/ETH 1h via `data-api.binance.vision/api/v3/klines`.
- C293 (frozen): OKX `https://www.okx.com/api/v5/public/funding-rate-history?instId=<SYM>-USDT-SWAP&limit=100[&after=<fundingTime_ms>]` (HTTP 200, browser UA); Binance USDT-M funding cached in `data/cache/campaign291_perp_5m.pkl`.
- C292 (frozen): OKX `https://www.okx.com/api/v5/market/history-candles` (5m, deep, HTTP 200 with browser UA); Coinbase `https://api.exchange.coinbase.com/products/<PAIR>/candles` (5m, deep, HTTP 200); Kraken 5m ~12h only → 1D `interval=1440` only.
- C291 (frozen): `data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip` and `.../fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip` (HTTP 200). `fapi.binance.com` remains HTTP 451; do not use it.
- Blocked: `fapi.binance.com` 451, `testnet.binance.vision` 451, `api.bybit.com` 403. Reachable: `www.deribit.com` 200, `api.exchange.coinbase.com` 200, `www.okx.com` 200, `data-api.binance.vision` 200.
- Binance API/host changes → `data/real_feed_loader.py` host chain. Statsmodels warnings → `utils/cointegration.py` (`result_object=True` where applicable). Schema drift → `python -m pytest tests/test_*_schema.py -v`.
- Campaign numbering conflict → highest campaign JSON in `reports/`; C285/C286/C288/C289/C290/C291/C292/C293 are complete and frozen; **current next campaign is C294** (then C295 = three-venue Coinbase spot).

**END OF HANDOFF — refreshed 2026-11-13T19:58:11Z.** Economic status: Binance single-venue spot (C281B→C286/C288/C289/C290), real USDT-M perp funding/basis (C291), cross-venue real-spot basis (C292), and cross-venue perp funding-carry (C293) are **closed/NOT_TRADABLE** (frozen; `economic_space_closed: true` for reachable 5m spot+perp). **C287 is BLOCKED/decoupled** (testnet REST HTTP 451 + no creds). **C294 is the sole active economic campaign** — real Deribit DVOL implied-vol VRP / BTC-ETH relative-value stat-arb, a genuinely new asset class that unblocks the repo's former `blocked_no_real_feed` family. **It must be completed end-to-end in one turn: ingest → preflight (`ready:true`) → full costed OOS sweep → 5 SHA256-from-bytes artifacts → tests → `pytest -q` green → state/handoff updated.** A status-only, planning-only, ingest-only, or infra-substituting turn is a failed handoff.