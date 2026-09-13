"""Build a deployment ZIP from explicit paths; never include local credentials."""
import json
import zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
app = root / 'apps/order-portal'
output = root / '.local/order-portal.zip'
if not (app/'dist/index.html').exists():
    raise SystemExit('Run npm run build in apps/order-portal first.')
manifest = json.loads((app/'package.json').read_text())
# The frontend is prebuilt locally. Oryx installs dependencies but must not try
# to rebuild absent development sources. Keep lockfile-compatible dependencies.
manifest['scripts'] = {'start':'node server/index.js'}
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('package.json',json.dumps(manifest,indent=2))
    archive.write(app/'package-lock.json','package-lock.json')
    for path in sorted((app/'dist').rglob('*')):
        if path.is_file(): archive.write(path,path.relative_to(app).as_posix())
    for name in ['index.js','app.js','db.js','filters.js','actions.js','order-action.sql']:
        archive.write(app/'server'/name,'server/'+name)
print(f'Deployment package: {output} ({output.stat().st_size:,} bytes)')
