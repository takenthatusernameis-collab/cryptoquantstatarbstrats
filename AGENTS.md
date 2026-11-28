# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-28T15:08:18Z — THE ONLY ACTIVE DIRECTIVE.
**REPO PRIORITY (from `cryptoquantstatarbstrats` = CRYPTO QUANT STAT-ARB STRATEGIES):** C441 TDA (LIVE) → C442 corr-dim D2 (NEXT, MANDATORY HEAVY, ALL 5 FILES READY) → C443 RQA (AFTER, MANDATORY HEAVY, ALL 5 FILES NOW AUTHORED & TRACKED — RUN, DO NOT RE-AUTHOR).

**VERIFIED STATE 2026-11-28T15:08:18Z:** C441 sweep LIVE — PERSISTENT bg `bgp_221d1699f001sGlxgqN9peJ0wo` (pid 4660 parent + 4 workers 4693-4696, `pgrep -af run_c441_tda_xsec_oos` LIVE). CPU-delta RE-VERIFIED ADVANCING at 15:08:18Z (two samples 20s apart): 4693 +1961, 4694 +1928, 4695 +1943, 4696 +1945 ticks/20s = genuine forward progress, NOT a hang, NOT stalled; parent 4660 static is NORMAL — it waits on the pool. 24/80 auto-committed checkpoints in `data/cache/_ckpt_tda_10x315648/` (assets 0-5 real done; count 24 UNCHANGED because the 4 tail series assets 6-9 are pathologically slow — CPU-delta proves work IS happening, do NOT misread unchanged count as a stall). 16 real (assets 6-9) + 40 placebo REMAIN. Cache meta/provenance PRESENT (`data/cache/campaign441_tda_5m.meta.json`). git clean on `main`. All 5 C442 files present in `scripts/`+`tests/`. **C443 ALL 5 FILES NOW AUTHORED & GIT-TRACKED** (build_c443_rqa_features.py, preflight_c443.py, run_c443_rqa_xsec_oos.py, test_preflight_c443.py, test_c443_rqa_xsec_oos.py; authored 14:21–14:31Z). C442 guard CLEAN (no proc, no reports, `_ckpt_corr_dim_10x315648/` empty). C443 guard CLEAN (no proc, no reports, `_ckpt_rqa_10x315648/` empty). NOTE: stale aborted dir `data/cache/_ckpt_corr_dim_3x200/` (old 3x200 spec) exists in git history — IGNORE it; current C442 spec dir is `_ckpt_corr_dim_10x315648/`. **BRANCH (b): LIVE AND checkpoints > 0 (24), CPU-delta ADVANCING → NOT branch (e).** +6h wakeup due 21:08:18Z — then exit. DO NOT relaunch/kill/duplicate. No polling.

## BOTTLENECK ANALYSIS (2026-11-28T13:14:00Z — READ, DO NOT RE-DERIVE)
- REAL bottleneck: the 4-worker pool is HEAD-OF-LINE BLOCKED on 4 pathologically slow TAIL series (assets 6-9, m=3). Assets 0-5 are done; the tail series grind on (degenerate/near-zero-variance windows produce large persistence diagrams ripser chokes on).
- VERIFIED NOT A HANG / NOT STALLED: CPU-delta re-verified advancing at 14:15:01Z (+766–777 ticks/8s per worker). They WILL finish; it is just slow (many more hours — EXPECTED and acceptable).
- BOTTLENECK REMOVAL (do NOT re-derive): DO NOT kill the sweep, DO NOT relaunch, DO NOT spawn duplicates, DO NOT reduce W_q (256 LOCKED pre-registered spec). The per-(asset,embedding) auto-commit checkpoint guarantees durability across resets. The session's job is to re-arm +6h and exit, OR advance to C442 once C441 completes — NOT to babysit or re-confirm in a loop.
- Branch (e) is the ONLY kill path and requires CPU-delta==0 proof: `for p in $(pgrep -f run_c441_tda_xsec_oos); do awk '{print $14}' /proc/$p/stat; done` twice 20s apart; if all identical → stalled → kill bg `bgp_221d1699f001sGlxgqN9peJ0wo`, relaunch persistent, +6h, exit.

## INITIAL TASK MESSAGE FOR NEXT SESSION (2026-11-28T15:08:18Z — C441 LIVE + 24 ckpts, BRANCH (b), SLOW TAIL, CPU-delta VERIFIED ADVANCING +1961/+1928/+1943/+1945 ticks/20s)

**C441 TDA sweep is LIVE and genuinely progressing (slow tail series, NOT a hang — verified via CPU-delta +1928–1961 ticks/20s per worker at 15:08:18Z; ckpt count 24 unchanged is EXPECTED for the pathologically slow assets 6-9 tail, NOT a stall). C442 ready (all 5 files). C443 NOW AUTHORED & TRACKED (all 5 files) — do NOT re-author. DO NOT relaunch/kill/duplicate. ONLY job: (1) re-arm ONE +6h wakeup FIRST, (2) run ONE status check, (3) pick ONE branch, (4) exit. No polling, no re-deriving the bottleneck.**

**C442 HEAVY WORK MANDATORY AFTER C441 (all 5 files ready). C443 HEAVY WORK MANDATORY AFTER C442 (all 5 files ALREADY AUTHORED — just preflight→tests→sweep, NO authoring, no opt-out). IF BLOCKED/TRULY-STALLED/UNCERTAIN → EXECUTE NEXT HEAVY CAMPAIGN STEP IMMEDIATELY. No analysis paralysis.**

### The ONE check
`pgrep -af run_c441_tda_xsec_oos` AND `ls data/cache/_ckpt_tda_10x315648/ | wc -l` AND `ls reports/campaign441_* 2>/dev/null` AND `ls data/cache/campaign441_tda_metrics.npz 2>/dev/null`

- (a) LIVE AND ckpts==0 → +90min, exit
- (b) LIVE AND ckpts>0 → verify CPU-delta (two `/proc/$p/stat` field-14 samples 20s apart); if ADVANCING → +6h, exit (CURRENT — slow tail, do NOT shorten, do NOT kill on unchanged ckpt count alone); if ALL IDENTICAL → branch (e)
- (c) NO process + 5 reports + metrics → DONE → ON SWEEP COMPLETION (below)
- (d) NO process + no reports → rebuild venv, relaunch persistent, +6h, exit
- (e) LIVE BUT CPU-delta==0 (truly stalled, ckpt count irrelevant) → kill bg `bgp_221d1699f001sGlxgqN9peJ0wo`, relaunch persistent, +6h, exit.

### ON SWEEP COMPLETION (c) — EXECUTE IMMEDIATELY, NO PAUSE
1. VERIFY 5 SHA256 reports + metrics npz.
2. FILL c441_status in research_state/state.yaml (all fields).
3. ADVANCE QUEUE: active=next=queued=C442, latest_done=C441.
4. BEGIN C442 (ALL 5 FILES READY): build → preflight (ready:true) → tests (all pass) → full 2592-config sweep (auto-ckpt `data/cache/_ckpt_corr_dim_10x315648/`), +6h discipline. C442 uses SAME slow-tail risk — apply branch (e) if truly stalled.
5. ON C442 DONE → RUN C443 RQA (ALL 5 FILES ALREADY AUTHORED & TRACKED — do NOT re-author: `scripts/build_c443_rqa_features.py`, `scripts/preflight_c443.py`, `scripts/run_c443_rqa_xsec_oos.py`, `tests/test_preflight_c443.py`, `tests/test_c443_rqa_xsec_oos.py`; DET/LAM/ENTR, m∈{3,4,5,6}, placebo seed 20261443, auto-ckpt `data/cache/_ckpt_rqa_10x315648/`) → preflight ready:true → tests green → full 2592-config sweep → +6h discipline.

## RULES
- WAKEUPS PER-SESSION: re-arm ONE +6h FIRST every session (slow tail justifies 6h over 4h).
- DO NOT kill sweep / spawn duplicate / monitor with command. Use logs/status with bg id `bgp_221d1699f001sGlxgqN9peJ0wo`. Branch (e) is the ONLY kill path and requires CPU-delta==0 proof.
- CHECKPOINT DIR = `data/cache/_ckpt_tda_10x315648/`. METRICS = `data/cache/campaign441_tda_metrics.npz`. C442 ckpt = `data/cache/_ckpt_corr_dim_10x315648/`. C443 ckpt = `data/cache/_ckpt_rqa_10x315648/`.
- C442 GUARD: pgrep run_c442 + ls reports/campaign442_*. If running or reports exist → +6h exit. Only one session claims C442.
- C443 GUARD: same for rqa.
- BOTTLENECK REMOVAL: blocked/truly-stalled/uncertain → execute next heavy campaign step immediately. No analysis paralysis. Do NOT re-derive the slow-tail analysis (it is recorded above).
- **NO SESSION MAY END WITHOUT RE-ARMING WAKEUP OR ADVANCING TO NEXT MANDATORY CAMPAIGN.**

## CAMPAIGNS
- C430-C440: FROZEN (NO EDGE). Do NOT re-run.
- C441: TDA H1 persistence entropy, m∈{3,4,5,6}, placebo seed 20261441, price-only perp_close. LIVE (24/80 ckpts, CPU-delta advancing 2026-11-28T15:08:18Z).
- C442: Correlation Dimension D2 (Grassberger-Procaccia), m∈{3,4,5,6}, placebo seed 20261442, 2592-config OOS, MANDATORY after C441. ALL 5 FILES READY.
- C443: RQA DET/LAM/ENTR, m∈{3,4,5,6}, placebo seed 20261443, 2592-config OOS, MANDATORY after C442. ALL 5 FILES AUTHORED & GIT-TRACKED (2026-11-28T14:21–14:31Z) — run, do NOT re-author.
