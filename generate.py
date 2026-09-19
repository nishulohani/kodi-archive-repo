import os, re, hashlib, zipfile

ADDONS = ["plugin.video.archiveorg", "repository.archiveorg"]
os.makedirs("zips", exist_ok=True)

xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
for a in ADDONS:
    src = open(f"{a}/addon.xml", encoding="utf-8").read()
    ver = re.search(r'<addon[^>]*version="([^"]+)"', src).group(1)
    xml += re.sub(r'<\?xml[^>]*\?>\s*', '', src).strip() + "\n"

    out = f"zips/{a}"
    os.makedirs(out, exist_ok=True)
    with zipfile.ZipFile(f"{out}/{a}-{ver}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(a):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, p)   # keeps the top-level folder name Kodi requires
xml += "</addons>\n"

open("addons.xml", "w", encoding="utf-8").write(xml)
open("addons.xml.md5", "w").write(hashlib.md5(xml.encode("utf-8")).hexdigest())
print("Done")
