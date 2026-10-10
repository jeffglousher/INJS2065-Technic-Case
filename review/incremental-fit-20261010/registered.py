from pathlib import Path
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
code=(ROOT/'review/contact-fix-20261009/registered_project.py').read_text()
code=code.replace("OUT=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/contact-fix-20261009')",f'OUT=Path({str(OUT)!r})')
code=code.replace("SOURCE=ROOT/'review/retention-fit-20261009/assembly-fit-candidate.3mf'","SOURCE=OUT/'nub-28.3mf'")
code=code.replace('nominal 0.26 mm clips','nominal 0.28 mm clips, unbeveled hexes')
exec(compile(code,'<recorded-complete-shell-project-builder>','exec'))
