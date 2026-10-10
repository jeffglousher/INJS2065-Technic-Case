from pathlib import Path
import json,sys
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
source=(ROOT/'review/retention-fit-20261009/paired-screen.py').read_text()
for tag in sys.argv[1:] or ['nub-28','nub-30']:
 code=source.replace("out=Path(__file__).resolve().parent",f"out=Path({str(OUT)!r})")
 code=code.replace("out/'assembly-fit-candidate-slice/plate_1.gcode'",f"out/'{tag}-slice/plate_1.gcode'")
 code=code.replace("out/'candidate-paths.json'",f"out/'{tag}-paths.json'")
 code=code.replace("out/'all-corners.json'",f"out/'{tag}-all-corners.json'")
 print('CASE',tag,flush=True);exec(compile(code,'<recorded-paired-bead-screen>','exec'))
 report=json.loads((OUT/f'{tag}-all-corners.json').read_text())
 report['source_project_sha256']=json.loads((OUT/f'{tag}-slice.json').read_text())['project_sha256']
 report['source_script']='review/retention-fit-20261009/paired-screen.py (path substitutions only)'
 (OUT/f'{tag}-all-corners.json').write_text(json.dumps(report,indent=2))
