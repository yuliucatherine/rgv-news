"""Builds timeline.json for Episode 5 ($42B in Valley data centers vs Texas' new freeze).
Episodes 1-3 voice, simple one-move 3D, real imagery first: USGS aerials of the actual sites, the Episode 1 Starbase
flyover, Harlingen photos (Wikimedia Commons), the Texas Capitol (Library of Congress, public domain).
Run: python3 episodes/2026-12-data-centers/make_timeline.py"""
import json, os

E5, E1 = "demo/ep5", "demo/ep1"
P = [0.15, 0.3]
BARS, MAP, HL = f"{E5}/v_bars_42b_s.mp4", f"{E5}/map_cameron.mp4", f"{E5}/headlines.mp4"
SBV, FALCON = f"{E1}/v_starbase_s.mp4", f"{E1}/v_falcon_s.mp4"
USGS = "Imagery: USGS The National Map"
RGVBJ = "Source: RGV Business Journal"
PHOTO_DIRS = {"p": "assets/photos/ep4", "q": "assets/photos/ep5"}
CRED = {}
for d in PHOTO_DIRS.values():
    f = os.path.join(d, "credits.json")
    if os.path.exists(f): CRED.update(json.load(open(f)))


def V(path, ss=0, ln=None, w=1.0):
    v = {"video": path, "ss": ss, "weight": w}
    if ln: v["len"] = ln
    return v


def IMG(name, w=1.0, zoom=(1.0, 1.12), pan=(0.5, 0.5, 0.5, 0.5), place=None, portrait=False):
    if name.startswith("a_"):
        d = "assets/photos/ep5/aerial" if os.path.exists(f"assets/photos/ep5/aerial/{name}.jpg") else "assets/photos/ep4/aerial"
        path, credit = f"{d}/{name}.jpg", (f"{place} · {USGS}" if place else USGS)
    else:
        c = CRED[name]; path = f"{PHOTO_DIRS[name[0]]}/{name}.jpg"
        credit = f"Photo: {c['artist']}, {c['license']}" + (f" · {place}" if place else "")
    v = {"image": path, "weight": w, "zoom": list(zoom), "pan": list(pan), "credit": credit}
    if portrait: v["portrait_fill"] = True
    return v


def C(card, w=1.0): return {"card": card, "weight": w}
def stat(label, big, lines, accent="orange", w=1.0): return C({"type": "stat", "label": label, "big": big, "lines": lines, "accent": accent}, w)
def lst(title, items, accent="orange", w=1.0): return C({"type": "list", "title": title, "items": items, "accent": accent}, w)
def quote(q, by, src, w=1.0): return C({"type": "quote", "quote": q, "by": by, "source": src}, w)
def N(nid, visuals, **kw): return dict(narr=nid, visuals=visuals, pad=kw.pop("pad", P), **kw)
def K(words, at=0.4, step=0.4, hold=2.8, size=120):
    return {"words": words, "at": at, "step": step, "hold": hold, "size": size, "box": "0x091020@0.55"}


def section(tag, title, chapter, accent="orange"):
    return {"label": tag.lower(), "dur": 1.5, "visuals": [C({"type": "section", "tag": tag, "title": title, "accent": accent})],
            "chapter": chapter, "pad": [0.5, 0.8]}


AIR = "Farmland east of Valley International Airport (imagery predates construction)"
B = [
    # ---------------- cold open
    N("n00", [IMG("a_airport_east", 0.6, zoom=(1.0, 1.15), pan=(0.35, 0.5, 0.6, 0.45), place=AIR), V(SBV, 0, 6.0, w=0.4)],
      chapter="Cold open: $42 billion on the table"),
    N("n01", [V(BARS, 0, 10.0)]),
    N("n02", [IMG("q01", 0.5, zoom=(1.0, 1.1), place="Austin"), IMG("a_starbase", 0.5, zoom=(1.0, 1.12), place="Starbase")],
      kinetic=K(["$42 BILLION", "ON HOLD?"], at=4.5, step=0.5, size=120)),
    N("n03", [V(MAP, 0, 11.0)]),
    {"label": "on the record", "dur": 6.0, "visuals": [V(HL, 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "$42 BILLION IN VALLEY DATA CENTERS",
                                                "sub": "Meets Texas' new freeze"})], "pad": [0.5, 0.8]},
    # ---------------- part 1: what's being built
    section("PART 1", "WHAT'S BEING BUILT", "Part 1: What's being built"),
    N("n04", [IMG("a_rio_hondo_fields", 0.55, zoom=(1.0, 1.12), place="Near Rio Hondo (imagery predates construction)"),
              V(MAP, 6.0, 6.0, w=0.45)], credit="Source: KRGV, Sep 2026"),
    N("n05", [IMG("q03", 0.5, zoom=(1.0, 1.1), place="illustrative"),
              stat("Fluidstack · first phase", "2,500+", ["construction jobs, several hundred permanent", "completion targeted mid-2028"], "teal", w=0.5)],
      credit="Sources: KRGV; Construction Review Online, Sep 2026"),
    N("n06", [lst("FLUIDSTACK SAYS IT PAYS ITS OWN WAY", ["No local property tax breaks", "Own power line and substation (AEP Texas)",
                                                          "Closed-loop cooling from East Rio Hondo WSC", "Water filled once, then recycled"], "teal"),
              IMG("q02", 0.8, zoom=(1.0, 1.1), place="illustrative")], credit="Source: Fluidstack statement via KRGV, Sep 2026"),
    N("n07", [IMG("p03", 0.4, zoom=(1.05, 1.15), place="Harlingen"),
              quote("It was not located in Harlingen. It was not asking Harlingen for permission to build. We did not have the authority to stop it.",
                    "Norma Sepulveda, Mayor of Harlingen", "statement reported by KRGV, September 2026", w=0.6)]),
    N("n08", [IMG("p05", 0.4, zoom=(1.05, 1.15), place="Harlingen"),
              stat("Eneus Energy · PROPOSED", "UP TO $14B", ["about 1,785 acres near Harlingen, up to 2 GW", "land option runs through July 2027"],
                   "blue", w=0.6)], credit="Sources: Baxtel; BeBeez; data center trackers (company-commissioned estimate)"),
    # ---------------- part 2: the SpaceX plan
    section("PART 2", "THE SPACEX PLAN", "Part 2: The SpaceX plan", "blue"),
    N("n09", [V(SBV, 6, 8.0, w=0.55), stat("SpaceX · Starbase", "$24B", ["AI computing complex", "own gas power plant, about 748 MW"], w=0.45)],
      credit="Sources: RGV Business Journal, Nov 11, 2026; S&P Global"),
    N("n10", [IMG("a_starbase_wide", 0.5, zoom=(1.0, 1.12), pan=(0.4, 0.6, 0.5, 0.5), place="Starbase"),
              stat("The site", "444 ACRES", ["land Brownsville disannexed", "for a $220M regional water investment"], "blue", w=0.5)],
      credit=RGVBJ + ", Nov 11, 2026"),
    N("n11", [stat("SpaceX's request to the county", "10 YEARS · 100%", ["property tax abatement", "$13.8B taxable value in its application"]),
              IMG("a_starbase", zoom=(1.1, 1.0), place="Starbase")], credit=RGVBJ + "; MyRGV, Nov 17, 2026"),
    N("n12", [lst("CAMERON COUNTY VOTE · NOV 17", ["Yes: Judge Eddie Treviño Jr., Comm. Joey Lopez",
                                                   "No: Comm. Sofia Benavidez, David Garza, Gus Ruiz",
                                                   "Result: no public hearing on the tax break (3-2)"], "blue"),
              V(MAP, 15.5, 5.5, w=0.7)], credit="Sources: MyRGV; ValleyCentral; RGV Business Journal, Nov 17, 2026"),
    N("n13", [lst("SPACEX'S RESPONSE · NOV 18", ["Computing equipment depreciates fast", "That could swing local tax rates year to year",
                                                 "Could redirect investment outside Cameron County"]),
              V(SBV, 14, 6.0)], credit=RGVBJ + ", Nov 18, 2026; MyRGV, Nov 19, 2026"),
    N("n14", [IMG("a_starbase_wide", zoom=(1.12, 1.0), pan=(0.5, 0.5, 0.4, 0.6), place="Starbase")],
      kinetic=K(["DEC 9", "STARBASE", "HEARING"], at=5.0, step=0.4, size=120)),
    # ---------------- part 3: Texas hits the brakes
    section("PART 3", "TEXAS HITS THE BRAKES", "Part 3: Texas hits the brakes"),
    N("n15", [IMG("q01", 0.45, zoom=(1.08, 1.0), place="Austin"),
              lst("WHAT THE STATE HAS DONE", ["Aug 3: ERCOT audit of data centers in the queue", "Sep 14: water-use reporting (TWDB)",
                                              "Sep 21: TCEQ halts data center permits"], w=0.55)],
      credit="Source: Office of the Texas Governor; Gibson Dunn"),
    N("n16", [lst("THE GOVERNOR'S CONDITIONS", ["Pay for their own electrical infrastructure", "Don't use water communities need",
                                                "Report power and water use", "ERCOT audit expected mid-December"], "teal"),
              IMG("q04", 0.8, zoom=(1.0, 1.1), place="illustrative")], credit="Source: Office of the Texas Governor, Sep 21, 2026"),
    N("n17", [stat("Governor-elect Gina Hinojosa", "MORATORIUM", ["on new data center approvals", "takes office Jan 19, 2027"], "blue"),
              IMG("q01", zoom=(1.0, 1.1), pan=(0.4, 0.5, 0.6, 0.5), place="Austin")], credit="Sources: Texas Tribune; Houston Chronicle, Nov 2026"),
    N("n18", [stat("Announced Texas projects at risk", "~13 GW", ["Jefferies estimate", "Legislature convenes Jan 12, 2027"]),
              IMG("q02", zoom=(1.1, 1.0), place="illustrative")], credit="Source: Gas Turbine World, citing Jefferies"),
    N("n19", [lst("WHAT LIKELY HAPPENS", ["Still needs a state permit: on hold", "Permitted, grid-connected, under construction: likely continues"], "teal"),
              IMG("a_rio_hondo_fields", zoom=(1.12, 1.0), place="Near Rio Hondo")], credit="Sources: Houston Chronicle; Texas Tribune, Nov 2026"),
    # ---------------- part 4: what it means for the Valley
    section("PART 4", "WHAT IT MEANS FOR THE VALLEY", "Part 4: What it means for the Valley", "teal"),
    N("n20", [IMG("p04", 0.5, zoom=(1.05, 1.15), place="Harlingen"), IMG("a_airport_east", 0.5, zoom=(1.1, 1.2), pan=(0.3, 0.4, 0.5, 0.5), place=AIR)]),
    N("n21", [stat("Property taxes", "FULL vs. ABATED", ["full taxes: millions a year locally", "full abatement: very little for a decade"], "teal"),
              IMG("a_harlingen", zoom=(1.0, 1.12), place="Downtown Harlingen")]),
    N("n22", [V(FALCON, 0, 7.0), lst("WATER CLAIMS TO CHECK", ["Closed-loop cooling", "Reclaimed wastewater", "State now requires usage reporting"], "teal")],
      credit="Sources: company statements; Office of the Texas Governor"),
    # ---------------- part 5: what to watch
    section("PART 5", "WHAT TO WATCH", "Part 5: What to watch"),
    N("n23", [lst("BUYING OR BUILDING NEAR RIO HONDO", ["Plan around Fluidstack: permitted, under construction", "Watch its hiring",
                                                       "Watch its community benefits deal with the county"], "teal"),
              IMG("a_airport_east", zoom=(1.0, 1.1), pan=(0.6, 0.5, 0.4, 0.5), place=AIR)]),
    N("n24", [lst("BETTING ON STARBASE", ["Wait for the Dec 9 city hearing", "Then the new governor's first order", "State permits could take months"], "blue"),
              V(SBV, 20, 6.0)]),
    N("n25", [lst("IF YOU'RE LENDING", ["Treat proposals as proposals", "Eneus hasn't bought its land", "SpaceX says it could build elsewhere"]),
              IMG("p02", zoom=(1.05, 1.15), place="Harlingen")]),
    N("n26", [lst("OUR WATCH LIST", ["Dec 9: Starbase hearing on SpaceX incentives", "Mid-December: ERCOT data center audit",
                                     "Jan 12: Legislature convenes", "Jan 19: Hinojosa takes office"], "teal")]),
    N("n27", [V(BARS, 6.0, 4.0, w=0.5), IMG("a_starbase_wide", 0.5, zoom=(1.0, 1.15), place="Starbase")]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays, charts and maps carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any(any(k in v.get("video", "") for k in ("v_", "map_", "chart_", "doc_")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep5/episode5.mp4", "audio_dir": "episodes/2026-12-data-centers/audio",
      "narration_json": "episodes/2026-12-data-centers/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Crusade_Heavy_Industry.mp3", "chapter": 0, "offset": 15},
          {"track": "assets/music/Deliberate_Thought.mp3", "chapter": 2, "offset": 20},
          {"track": "assets/music/Unanswered_Questions.mp3", "chapter": 3, "offset": 20},
          {"track": "assets/music/Industrial_Cinematic.mp3", "chapter": 5, "offset": 40}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
