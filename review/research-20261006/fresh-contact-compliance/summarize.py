"""Derive convergence and interpretation checks from the stored C matrices."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
levels = [0.2, 0.12, 0.09]
reports = [json.loads((root / f'compliance-{level:g}.json').read_text()) for level in levels]
out = []
for case in range(2):
    rows = [report['results'][case] for report in reports]
    last, previous = rows[-1], rows[-2]
    F, old_F = last['illustrative_equal_displacement_forces_N'], previous['illustrative_equal_displacement_forces_N']
    matrix = last['compliance_mm_per_N']
    relative_diagonal_change = [abs(matrix[i][i]/previous['compliance_mm_per_N'][i][i]-1) for i in range(4)]
    # Absolute row coupling is the safer diagnostic: a signed sum can hide
    # cancellation between positive and negative off-diagonal entries.
    row_abs_coupling = [sum(abs(matrix[i][j]) for j in range(4) if j != i)/matrix[i][i] for i in range(4)]
    independent = last['incorrect_independent_diagonal_forces_N']
    item = dict(support=last['support'],finest_equal_displacement_force_range_N=[min(F),max(F)],max_relative_force_change_last_refinement=max(abs(F[i]/old_F[i]-1) for i in range(4)),relative_diagonal_compliance_change_last_refinement=relative_diagonal_change,max_abs_row_coupling_relative_to_diagonal=max(row_abs_coupling),max_independent_diagonal_force_relative_error=max(abs(independent[i]/F[i]-1) for i in range(4)),finest_matrix_positive_definite=min(last['compliance_eigenvalues_mm_per_N'])>0,maximum_reciprocity_relative_error=max(row['reciprocity_relative_error'] for row in rows),maximum_free_equilibrium_relative_residual=max(max(row['free_equilibrium_relative_residuals']) for row in rows),all_meshes_no_negative_quality=all(report['negative_quality_element_count']==0 for report in reports))
    out.append(item)
payload = dict(study='fresh four-patch compliance summary',source_report_sha256={f'compliance-{level:g}.json':hashlib.sha256((root/f'compliance-{level:g}.json').read_bytes()).hexdigest() for level in levels},mesh_levels_mm=levels,results=out,claims=['Weak inter-patch coupling confirmed only under the prescribed floor-support idealizations.','Largest illustrative force change on the final refinement is reported; no asymptotic error bound or contact qualification.','No geometry changes or actual installed contact forces established.'])
(root/'summary.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,indent=2))
