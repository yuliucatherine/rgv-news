"""Fills description_template.md's {chapters} from demo/ep4/episode4_meta.json -> description.md"""
import json, os
D = os.path.dirname(__file__)
meta = json.load(open("demo/ep4/episode4_meta.json"))
ch = "\n".join(f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in meta["chapters"])
tpl = open(os.path.join(D, "description_template.md")).read()
open(os.path.join(D, "description.md"), "w").write(tpl.replace("{chapters}", ch))
print(ch)
