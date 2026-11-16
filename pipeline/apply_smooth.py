"""Point a timeline at smoothed clips: replace <name>.mp4 with <name>_s.mp4 and scale ss/len by the stretch.
Usage: python3 pipeline/apply_smooth.py <timeline.json> name=stretch [name=stretch ...]"""
import sys, json
p = sys.argv[1]; t = json.load(open(p))
S = {k: float(v) for k, v in (a.split("=") for a in sys.argv[2:])}
for b in t["blocks"]:
    for v in b.get("visuals", []):
        src = v.get("video", "")
        for name, s in S.items():
            if src.endswith(f"/{name}.mp4"):
                v["video"] = src[:-4] + "_s.mp4"
                v["ss"] = round(v.get("ss", 0) * s, 3)
                if "len" in v: v["len"] = round(v["len"] * s, 3)
json.dump(t, open(p, "w"), indent=1, ensure_ascii=False)
print("updated", p)
