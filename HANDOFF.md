## READ THIS FIRST — C104/C105 INITIAL TASK (20261106T212000Z, produced by handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C103 DONE: `VOLUME_SPECTRAL_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_spectral_entropy_shock_mr_costed_oos_20261106T204151Z.json`, `oos_edge_proven=false`. Latest registry `reports/strategy_edge_registry_20261106T204555Z.json`. pytest: 928 passed / 1 skipped / 0 failed, rc=0.
- C104 `VOLUME_WAVELET_ENTROPY_SHOCK_MR` (wavelet packet/continuous wavelet energy-distribution entropy over scales): grep-verified ABSENT — no `wavelet_entropy` script/report exists. **EXECUTE FIRST.**
- C105 `VOLUME_HURST_RS_PERSISTENCE_MR` (rescaled-range Hurst exponent / long-memory persistence over rolling windows; distinct from variance-ratio/OU-halflife/DFA/Higuchi/Petrosian/Katz fractal candidates AND distinct from existing `hurst_exponent_shock_mr`): grep-verified ABSENT — no `hurst_rs_persistence` script/report exists. **EXECUTE AFTER C104.**
- Nonspot ingest: `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT` (families: funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure). **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache `0bab5d6a...pkl` present.

### NEXT FOCUS CAMPAIGN — C104 THEN C105 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** Do not skip to C105 without C104 unless `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_*.json` already exists.

#### Step 1 — C104 R-B `VOLUME_WAVELET_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. **Grep-verify distinctness** (must pass before coding):
   ```bash
   grep -r "wavelet_entropy\|wavelet.*entropy\|wavelet_packet.*entropy\|continuous.*wavelet.*entropy" reports/ scripts/ | wc -l
   ```
   (expect 0). Also confirm not duplicating existing wavelet/fractal candidates.
2. **Environment check**: `python -c "import pywt" 2>&1 | tail -1` (PyWavelets may be missing). Implement robustly: prefer `pywt` if present; else use `scipy.signal.cwt`/`scipy.fft` Morlet with log-energy over scales; else pure numpy FFT-based band energy. Do **not** fake results.
3. **Create** `scripts/run_real_quote_volume_wavelet_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_spectral_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed).
   - Feature: wavelet energy distribution entropy over rolling window `W_WAV` (e.g. 168). Compute scale-wise energies `E_s`, normalize `p_s = E_s/sum E_s`, Shannon entropy `H_w = -sum p_s log p_s`, normalize by `log(n_scales)`. Distinct from spectral entropy (PSD) and all prior.
   - Signal: shock = `|z(H_w)|` vs baseline `ALB` (e.g. 336), entry_z>=1.5 -> high wavelet-entropy shock fades short (-1), low fades long (+1), exit_z<0.5 or max_hold (24) or flip; execution t->t+1.
4. **Run** with exact params: WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
5. **Emit** `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_<UTC>.json` (include pre_stated_distinctness, references to prior unblocks/registries, per-asset + aggregate with edge rule computed).

#### Step 2 — C105 R-B `VOLUME_HURST_RS_PERSISTENCE_MR` (PRIORITY 2, after C104)
1. **Grep-verify distinctness**:
   ```bash
   grep -r "hurst_rs_persistence\|rescaled.*range.*hurst" reports/ scripts/ | wc -l
   ```
   (expect 0). Must be distinct from `hurst_exponent_shock_mr` (if exists) and from variance-ratio/OU-halflife/DFA/Higuchi/Petrosian/Katz.
2. **Create** `scripts/run_real_quote_volume_hurst_rs_persistence_mr_costed_oos.py` same framework.
   - Feature: rolling rescaled-range (R/S) analysis over window `W_RS` (e.g. 168). For subseries compute mean-adjusted deviations, range R, std S, get R/S; fit log(R/S)=H*log(n)+c over scales or use classical R/S H estimate on window (robust). Distinct R/S persistence measure.
   - Signal: shock on |z(H_rs)| vs baseline; fade extremes per same logic (high persistence shock -> short; low -> long) with t->t+1, same WF/costs.
3. **Run** and emit `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_<UTC>.json`.

#### Step 3 — Registry + ingest evidence + pytest + execution summaries (MANDATORY)
1. **Nonspot ingest evidence** (do not block): emit `reports/real_feed_ingest_attempt_<UTC>.json` with concrete evidence checked in `data/cache/` (look for nonspot families: funding_basis_carry, cross_exchange_dual_venue_same_asset, term_structure_real_iv_vol_surface, intrabar_microstructure). If none found with `.meta.json` + `.provenance.json` and real artifacts, record `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT` with file listing. If any real nonspot artifact exists, ingest **exactly one** blocked family with full provenance.
2. **Pytest** if code changed: `python -m pytest tests/ -q` (record passed/skipped/failed/rc).
3. **Registry**: emit `reports/strategy_edge_registry_<UTC>.json` superseding latest (reference `reports/strategy_edge_registry_20261106T204555Z.json`), include C104 and C105 results, pytest counts/rc, references to prior unblock.
4. **Summaries**: emit `reports/campaign104_execution_summary_<UTC>.json` and `reports/campaign105_execution_summary_<UTC>.json` with actions, artifacts, edge results, distinctness checks.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist.**
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed
- Nonspot ingest blocker decoupled from R-B: proceed on `real_quote_volume` family (C104 wavelet_entropy, C105 hurst_rs_persistence) without waiting for nonspot unblock.
- C104 is hard prerequisite to C105: execute C104 first, only then C105.
- Force heavy work: implementation required, not analysis-only.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -r "wavelet_entropy" reports/ scripts/ | wc -l  # expect 0
grep -r "hurst_rs_persistence" reports/ scripts/ | wc -l  # expect 0
python -c "import pywt,numpy,scipy,pandas" && echo "deps_ok" || true
```
Then implement C104 script, run it, emit artifacts, then C105. Do not stop until Step 3 complete with >=3 new artifacts.
