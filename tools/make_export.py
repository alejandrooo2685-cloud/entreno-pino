#!/usr/bin/env python3
"""Empaqueta los datos exportados de una app de Claude en el .zip que lee migrar/index.html.
Uso: python3 make_export.py <carpeta_export> <app> <salida.zip>
La carpeta contiene db/<coleccion>/<doc>.json (ArtifactData list con out_dir) y media/<id>.<ext> (Artifact read de cada asset)."""
import sys, os, json, zipfile, mimetypes
src, app, out = sys.argv[1:4]
docs = []
for col in sorted(os.listdir(os.path.join(src, "db"))):
    for fn in sorted(f for f in os.listdir(os.path.join(src, "db", col)) if f.endswith(".json") and not f.startswith(".")):
        d = json.load(open(os.path.join(src, "db", col, fn), encoding="utf-8"))
        data = d.get("data", d)
        docs.append({"path": f"{col}/{fn[:-5]}", "data": data})
media = []
mdir = os.path.join(src, "media")
with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
    for fn in (sorted(f for f in os.listdir(mdir) if not f.startswith(".")) if os.path.isdir(mdir) else []):
        mid, ext = os.path.splitext(fn)
        typ = mimetypes.guess_type(fn)[0] or "application/octet-stream"
        media.append({"id": mid, "type": typ})
        z.write(os.path.join(mdir, fn), "media/" + mid)
    z.writestr("export.json", json.dumps({"app": app, "docs": docs, "media": media}, ensure_ascii=False))
print(f"{out}: {len(docs)} docs, {len(media)} archivos, {os.path.getsize(out)//1024} KB")
