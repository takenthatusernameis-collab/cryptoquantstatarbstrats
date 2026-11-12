#!/usr/bin/env python3
"""C275 deterministic verification for MEDCOUPLE edge.
Reads saved C275 artifacts only (real cached data provenance preserved; no refetch/synthetic)."""
from __future__ import annotations
import hashlib, json, math, subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
STRATEGY_ID = 'VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR'
COST_KEYS = ['fee0_slip0','fee5_slip5','fee10_slip10','fee20_slip20','fee40_slip40']

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def latest(pattern: str) -> Path:
    matches = sorted(reports.glob(pattern))
    if not matches:
        raise SystemExit(f'NO_MATCHING_ARTIFACT: {pattern}')
    return matches[-1]

def run_distinctness_grep():
    pat = "RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|MEDCOUPLE"
    cmd = f"grep -rnE '{pat}' scripts/ strategies/ backtest/ utils/ 2>&1"
    proc = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
    out = (proc.stdout + proc.stderr).strip()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    self_stems = {
        Path(__file__).stem,
        'run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos',
        'verify_c275_medcouple_edge',
        'run_c275_medcouple_split_decomposition', 'run_c275_medcouple_param_sensitivity',
    }
    nonself = []
    for ln in lines:
        if any(stem in ln for stem in self_stems): continue
        if 'medcouple' in ln.lower(): nonself.append(ln)
    return len(nonself), "\n".join(lines)

checks = []
def add(name, ok, detail=None):
    checks.append({'check': name, 'ok': bool(ok), 'detail': detail})

ART = {
    'oos': latest('real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_*.json'),
    'ingest': latest('real_feed_ingest_attempt_275_*.json'),
    'registry': latest('strategy_edge_registry_275_*.json'),
    'summary': latest('campaign275_execution_summary_*.json'),
    'script': root / 'scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py',
}
for k, p in ART.items():
    add(f'{k}_exists', p.exists(), str(p) if p.exists() else 'missing')

o = json.loads(ART['oos'].read_text()) if ART['oos'].exists() else {}
ing = json.loads(ART['ingest'].read_text()) if ART['ingest'].exists() else {}
reg = json.loads(ART['registry'].read_text()) if ART['registry'].exists() else {}
summ = json.loads(ART['summary'].read_text()) if ART['summary'].exists() else {}

oos_sha = sha(ART['oos']) if ART['oos'].exists() else None
script_sha = sha(ART['script']) if ART['script'].exists() else None

add('registry_oos_sha_matches_oos_file', reg.get('oos_sha256') == oos_sha, {'registry': reg.get('oos_sha256'), 'file': oos_sha})
add('summary_oos_sha_matches_oos_file', summ.get('artifacts', {}).get('oos', {}).get('sha256') == oos_sha, {'summary': summ.get('artifacts', {}).get('oos', {}).get('sha256'), 'file': oos_sha})
add('summary_ingest_sha_matches_ingest_file', summ.get('artifacts', {}).get('ingest', {}).get('sha256') == sha(ART['ingest']) if ART['ingest'].exists() else False, None)
add('summary_registry_sha_matches_registry_file', summ.get('artifacts', {}).get('registry', {}).get('sha256') == sha(ART['registry']) if ART['registry'].exists() else False, None)
add('summary_script_sha_matches_script_file', summ.get('artifacts', {}).get('script', {}).get('sha256') == script_sha, {'summary': summ.get('artifacts', {}).get('script', {}).get('sha256'), 'file': script_sha})
add('strategy_id_consistent', o.get('strategy_id') == reg.get('strategy_id') == summ.get('strategy_id') == STRATEGY_ID, {'oos': o.get('strategy_id'), 'registry': reg.get('strategy_id'), 'summary': summ.get('strategy_id')})
add('campaign_consistent', o.get('campaign') == reg.get('campaign') == summ.get('campaign') == ing.get('campaign') == 275, {'oos': o.get('campaign'), 'registry': reg.get('campaign'), 'summary': summ.get('summary') if False else summ.get('campaign'), 'ingest': ing.get('campaign')})
add('ingest_real_data_only_flags', ing.get('real_data_only') is True and ing.get('fabricated_data') is not True and ing.get('network_refetch') is False, {k: ing.get(k) for k in ('real_data_only','fabricated_data','network_refetch')})

cross = o.get('cross_asset', {}).get('oos_net_sums', {})
vals = [cross.get(k) for k in COST_KEYS]
all_pos_vals = all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in vals)
any_exp = bool(o.get('any_exposure_oos'))
beat_bh = bool(o.get('all_cost_slices_beat_bh_mean_rule'))
flag_all_pos = bool(o.get('all_cost_slices_positive_oos_net_sum'))
edge_flag = bool(o.get('oos_edge_proven'))
edge_claim = o.get('edge_claim')
rule_expected = bool(any_exp and flag_all_pos and beat_bh)
outcome_checks = []
outcome_checks.append(('cross_asset_has_all_cost_keys', all(k in cross for k in COST_KEYS), list(cross.keys())))
outcome_checks.append(('all_cost_slices_positive_from_values', all_pos_vals, cross))
outcome_checks.append(('flag_all_cost_positive_matches_values', flag_all_pos == all_pos_vals, {'flag': flag_all_pos, 'from_values': all_pos_vals}))
outcome_checks.append(('edge_rule_internal_consistency', edge_flag == rule_expected, {'edge_flag': edge_flag, 'expected_from_flags': rule_expected, 'any_exposure': any_exp, 'all_pos_flag': flag_all_pos, 'beat_bh': beat_bh}))
outcome_checks.append(('edge_claim_consistent', (edge_flag and edge_claim == 'CONDITIONAL_EDGE_PROVEN') or ((not edge_flag) and edge_claim in ('NONE', None)), {'edge_flag': edge_flag, 'edge_claim': edge_claim}))
outcome_checks.append(('cross_asset_oos_net_sums_all_zero_when_no_exposure', (not any_exp) and all(isinstance(v, (int, float)) and v == 0.0 for v in vals), vals))
mono = True
for i in range(len(vals) - 1):
    if vals[i] is None or vals[i + 1] is None or not (vals[i] >= vals[i + 1]):
        mono = False
outcome_checks.append(('cross_asset_cost_monotonic_cost_degrades_net', mono, vals))
for name, ok, detail in outcome_checks:
    add(name, ok, detail)
edge_rule_satisfied = rule_expected

per_asset = o.get('per_asset', {})
recomputed = {k: 0.0 for k in COST_KEYS}
recomputed_means = {k: 0.0 for k in COST_KEYS}
recomputed_bh = {k: 0.0 for k in COST_KEYS}
cons_ok = True
per_asset_detail = {}
n_assets = 0
for sym, a in per_asset.items():
    n_assets += 1
    per_asset_detail[sym] = {}
    pc = a if isinstance(a, dict) else {}
    for ck in COST_KEYS:
        v = pc.get(ck, {}).get('oos_net_sum') if isinstance(pc.get(ck), dict) else None
        m = pc.get(ck, {}).get('oos_net_mean') if isinstance(pc.get(ck), dict) else None
        b = pc.get(ck, {}).get('bh_oos_mean') if isinstance(pc.get(ck), dict) else None
        if not isinstance(v, (int, float)) or not math.isfinite(v):
            cons_ok = False
        else:
            recomputed[ck] += float(v)
        per_asset_detail[sym][ck] = {'oos_net_sum': v, 'oos_net_mean': m, 'bh_oos_mean': b}
        if isinstance(m, (int, float)) and math.isfinite(m):
            recomputed_means[ck] += float(m)
        if isinstance(b, (int, float)) and math.isfinite(b):
            recomputed_bh[ck] += float(b)
add('per_asset_cost_keys_complete', cons_ok, None)
add('n_assets_matches_reported', n_assets == o.get('n_assets'), {'recomputed': n_assets, 'reported': o.get('n_assets')})
for ck in COST_KEYS:
    add(f'recomputed_cross_sum_{ck}_matches', abs(recomputed[ck] - float(cross.get(ck, 0.0))) < 1e-9, {'recomputed': recomputed[ck], 'reported': cross.get(ck)})
    n = len(per_asset)
    add(f'recomputed_mean_oos_net_{ck}_matches', abs(recomputed_means[ck] / n - float(o.get('cross_asset', {}).get('mean_oos_net_means', {}).get(ck, 0.0))) < 1e-9 if n else True, None)
    add(f'recomputed_mean_bh_oos_{ck}_matches', abs(recomputed_bh[ck] / n - float(o.get('cross_asset', {}).get('mean_bh_oos_means', {}).get(ck, 0.0))) < 1e-9 if n else True, None)

dist = o.get('pre_stated_distinctness', {})
live_hits, live_out = run_distinctness_grep()
add('distinctness_grep_hits_zero_saved', dist.get('grep_hits_nonself_at_run') == 0, dist.get('grep_hits_nonself_at_run'))
add('distinctness_grep_hits_zero_live', live_hits == 0, live_hits)
add('collision_fail_closed_false', dist.get('collision_fail_closed') is False, dist.get('collision_fail_closed'))
add('wf_params_match', o.get('walk_forward') == {'train': 720, 'test': 168, 'step': 168}, o.get('walk_forward'))
add('cost_grid_match', o.get('cost_grid_bps') == [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]], o.get('cost_grid_bps'))
add('params_match_stated', o.get('params', {}).get('W_RR') == 168 and o.get('params', {}).get('ENTRY_Z') == 1.5 and o.get('params', {}).get('EXIT_Z') == 0.5, o.get('params'))
add('real_data_only_flag', o.get('data', {}).get('real_data_only') is True, o.get('data', {}).get('real_data_only'))

structural_names = {
    'oos_exists','ingest_exists','registry_exists','summary_exists','script_exists',
    'registry_oos_sha_matches_oos_file','summary_oos_sha_matches_oos_file',
    'summary_ingest_sha_matches_ingest_file','summary_registry_sha_matches_registry_file',
    'summary_script_sha_matches_script_file','strategy_id_consistent','campaign_consistent',
    'ingest_real_data_only_flags','per_asset_cost_keys_complete','n_assets_matches_reported',
    'recomputed_cross_sum_fee0_slip0_matches','recomputed_cross_sum_fee5_slip5_matches',
    'recomputed_cross_sum_fee10_slip10_matches','recomputed_cross_sum_fee20_slip20_matches',
    'recomputed_cross_sum_fee40_slip40_matches','recomputed_mean_oos_net_fee0_slip0_matches',
    'recomputed_mean_oos_net_fee5_slip5_matches','recomputed_mean_oos_net_fee10_slip10_matches',
    'recomputed_mean_oos_net_fee20_slip20_matches','recomputed_mean_oos_net_fee40_slip40_matches',
    'recomputed_mean_bh_oos_fee0_slip0_matches','recomputed_mean_bh_oos_fee5_slip5_matches',
    'recomputed_mean_bh_oos_fee10_slip10_matches','recomputed_mean_bh_oos_fee20_slip20_matches',
    'recomputed_mean_bh_oos_fee40_slip40_matches','distinctness_grep_hits_zero_saved',
    'distinctness_grep_hits_zero_live','collision_fail_closed_false','wf_params_match',
    'cost_grid_match','params_match_stated','real_data_only_flag',
}
internal_consistency_passed = all(c['ok'] for c in checks if c['check'] in structural_names)
verification_passed = internal_consistency_passed
verification = {
    'generated_at_utc': ts, 'campaign': 275, 'strategy_id': STRATEGY_ID,
    'verification_passed': verification_passed,
    'internal_consistency_passed': internal_consistency_passed,
    'edge_rule_satisfied': bool(edge_rule_satisfied),
    'artifacts': {k: str(v.relative_to(root)) if v.is_relative_to(root) else str(v) for k, v in ART.items()},
    'artifact_sha256': {k: sha(v) if v.exists() else None for k, v in ART.items()},
    'oos_file_sha256': oos_sha, 'script_sha256': script_sha,
    'checks': checks,
    'cross_asset_oos_net_sums': cross,
    'recomputed_cross_asset_oos_net_sums': recomputed,
    'per_asset_detail': per_asset_detail,
    'ok_asset_count': n_assets,
    'edge_claim': edge_claim, 'oos_edge_proven': edge_flag,
    'any_exposure_oos': any_exp,
    'all_cost_slices_positive_oos_net_sum': flag_all_pos,
    'all_cost_slices_beat_bh_mean_rule': beat_bh,
}
vpath = reports / f'campaign275_verification_{ts}.json'
vpath.write_text(json.dumps(verification, indent=2) + '\n')
print(json.dumps({
    'verification': str(vpath.relative_to(root)), 'verification_sha256': sha(vpath),
    'verification_passed': verification_passed, 'oos_edge_proven': edge_flag,
    'cross_asset_oos_net_sums': cross, 'any_exposure_oos': any_exp,
}, indent=2))
