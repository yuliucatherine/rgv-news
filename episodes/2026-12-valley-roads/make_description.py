"""Fills description_template.md from demo/ep6/episode6_meta.json and the photos the timeline actually uses -> description.md"""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__))
TITLE = open(os.path.join(D, "title.txt")).read().strip() if os.path.exists(os.path.join(D, "title.txt")) else "TITLE"
meta = json.load(open("demo/ep6/episode6_meta.json"))
ch = "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in meta["chapters"])
tl = json.load(open(os.path.join(D, "timeline.json")))
used = []
for b in tl["blocks"]:
    for v in b["visuals"]:
        p = v.get("image", "")
        if "/aerial/" not in p and p and p not in used: used.append(p)
cred = {}
for p in used:
    cj = os.path.join(os.path.dirname(p), "credits.json"); cred.update(json.load(open(cj)))
lines = []
for p in used:
    c = cred[os.path.splitext(os.path.basename(p))[0]]
    name = c.get("title") or re.sub(r"\s*\(\d{6,}\)", "", os.path.splitext(c["file"])[0])
    lines.append(f"- {name}: {c['artist']}, {c['license']}")
music = [os.path.basename(s["track"])[:-4].replace("_", " ") for s in tl["music"]["segments"]]
mus = ", ".join(f'"{m}"' for m in music[:-1]) + f' and "{music[-1]}"'
out = open(os.path.join(D, "description_template.md")).read().replace("{chapters}", ch).replace("{photos}", "\n".join(lines))
out = out.replace("{music}", mus).replace("{title}", TITLE)
open(os.path.join(D, "description.md"), "w").write(out)
print(out[:3000])
