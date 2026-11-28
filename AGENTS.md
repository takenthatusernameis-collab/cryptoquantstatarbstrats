# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-28T13:06:39Z — THE ONLY ACTIVE DIRECTIVE.
**REPO PRIORITY (from repo name `cryptoquantstatarbstrats` = CRYPTO QUANT STAT-ARB STRATEGIES):** C441 TDA (LIVE) → C442 corr-dim (NEXT, MANDATORY HEAVY) → C443 RQA (AFTER, MANDATORY HEAVY).
**VERIFIED STATE 2026-11-28T13:06:39Z:** C441 sweep LIVE — PERSISTENT bg (pid 4660 + 4 workers 4693-4696, `pgrep -af run_c441_tda_xsec_oos` LIVE). `.venv` rebuilt (ripser 0.6.15 imports OK). 24/80 auto-committed checkpoints in `data/cache/_ckpt_tda_10x315648/` (newest `real_5_6.npy`). Cache meta/provenance PRESENT (`data/cache/campaign441_tda_5m.meta.json`). git clean on `main`. All 5 C442 files present. C442 guard CLEAN. C443 guard CLEAN. **BRANCH (b): LIVE AND checkpoints > 0.** Re-arm +4h FIRST this session, then exit — DO NOT relaunch/kill/duplicate. No polling.

## INITIAL TASK MESSAGE FOR NEXT SESSION (2026-11-28T13:06:39Z — C441 LIVE + 24 ckpts, BRANCH (b))

**C441 TDA sweep is LIVE and healthy. C442 guard CLEAN. DO NOT relaunch/kill/duplicate. ONLY job: (1) re-arm ONE +4h wakeup FIRST, (2) run ONE status check, (3) pick ONE branch, (4) exit. No polling.**

**C442 HEAVY WORK MANDATORY AFTER C441. C443 HEAVY WORK MANDATORY AFTER C442. NO OPT-OUT. NO DEFER. NO EXCUSES.**

### The ONE check
`pgrep -af run_c441_tda_xsec_oos` AND `ls data/cache/_ckpt_tda_10x315648/ | wc -l` AND `ls reports/campaign441_* 2>/dev/null` AND `ls data/cache/campaign441_tda_metrics.npz 2>/dev/null`

- (a) LIVE AND ckpts==0 → +90min, exit
- (b) LIVE AND ckpts>0 → +4h, exit (CURRENT)
- (c) NO process + 5 reports + metrics → DONE → ON SWEEP COMPLETION
- (d) NO process + no reports → rebuild venv, relaunch persistent, +4h, exit

### ON SWEEP COMPLETION (c) — EXECUTE IMMEDIATELY, NO PAUSE
1. VERIFY 5 SHA256 reports + metrics npz.
2. FILL c441_status in research_state/state.yaml (all fields).
3. ADVANCE QUEUE: active=next=queued=C442, latest_done=C441.
4. BEGIN C442: build → preflight (ready:true) → tests (all pass) → full 2592-config sweep (auto-ckpt _ckpt_corr_dim_*), +4h discipline.
5. ON C442 DONE → BEGIN C443 RQA same sequence (auto-ckpt _ckpt_rqa_*).

## RULES
- WAKEUPS PER-SESSION: re-arm ONE +4h FIRST every session.
- DO NOT kill sweep / spawn duplicate / monitor with command. Use logs/status with bg id.
- CHECKPOINT DIR = data/cache/_ckpt_tda_10x315648/. METRICS = data/cache/campaign441_tda_metrics.npz.
- C442 GUARD: pgrep run_c442 + ls reports/campaign442_*. If running or reports exist → +4h exit. Only one session claims C442.
- C443 GUARD: same for rqa.
- BOTTLENECK REMOVAL: blocked/stalled/uncertain → execute next heavy campaign step immediately. No analysis paralysis.
- **NO SESSION MAY END WITHOUT RE-ARMING WAKEUP OR ADVANCING TO NEXT MANDATORY CAMPAIGN.**

## CAMPAIGNS
- C430-C440: FROZEN (NO EDGE). Do NOT re-run.
- C441: TDA H1 persistence entropy, m∈{3,4,5,6}, placebo seed 20261441, price-only perp_close.
- C442: Correlation Dimension D2, m∈{3,4,5,6}, placebo seed 20261442, 2592-config OOS, MANDATORY after C441.
- C443: RQA DET/LAM/ENTR, m∈{3,4,5,6}, placebo seed 20261443, 2592-config OOS, MANDATORY after C442.
