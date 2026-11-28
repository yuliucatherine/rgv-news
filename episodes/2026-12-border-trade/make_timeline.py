"""Builds timeline.json for Episode 8 (border trade: a bigger bridge, emptier factories).
Episodes 1-3 voice, real imagery first, new Blender angles (Starbase orbit, Pharr bridge orbit, Donna at golden hour,
SH 4 at sunset; owner rule Nov 24: no reused SH 4 flyover), a 3D wage chart, USGS aerials and Wikimedia photos.
Run: python3 episodes/2026-12-border-trade/make_timeline.py"""
import json, os

E8, FLY = "demo/ep8", "demo/flyovers"
P = [0.15, 0.3]
HL, BARS = f"{E8}/headlines.mp4", f"{E8}/v_bars_vacancy_s.mp4"
REY = f"{FLY}/v2/v_reynosa_south_s.mp4"
SB, SH4D = f"{FLY}/v2/v_starbase_orbit_s.mp4", f"{FLY}/v_sh4_dusk_west_s.mp4"
DON, PHR = f"{FLY}/v2/v_donna_dusk_s.mp4", f"{FLY}/v2/v_pharr_bridge_top_s.mp4"
PORT = "demo/ep7/v_port_s.mp4"
USGS = "Imagery: USGS The National Map"
RGVBJ = "Source: RGV Business Journal"
FED = "Source: Federal Reserve Bank of Dallas, Rio Grande Valley Economic Indicators"
PHOTO_DIRS = {"p": "assets/photos/ep4", "q": "assets/photos/ep5", "r": "assets/photos/ep6"}
CRED = {}
for d in PHOTO_DIRS.values():
    f = os.path.join(d, "credits.json")
    if os.path.exists(f): CRED.update(json.load(open(f)))


def V(path, ss=0, ln=None, w=1.0):
    v = {"video": path, "ss": ss, "weight": w}
    if ln: v["len"] = ln
    return v


def IMG(name, w=1.0, zoom=(1.0, 1.12), pan=(0.5, 0.5, 0.5, 0.5), place=None):
    if name.startswith("a_"):
        d = next(f"assets/photos/{e}/aerial" for e in ("ep6", "ep5", "ep4") if os.path.exists(f"assets/photos/{e}/aerial/{name}.jpg"))
        path, credit = f"{d}/{name}.jpg", (f"{place} · {USGS}" if place else USGS)
    else:
        c = CRED[name]; path = f"{PHOTO_DIRS[name[0]]}/{name}.jpg"
        credit = f"Photo: {c['artist']}, {c['license']}" + (f" · {place}" if place else "")
    return {"image": path, "weight": w, "zoom": list(zoom), "pan": list(pan), "credit": credit}


def C(card, w=1.0): return {"card": card, "weight": w}
def stat(label, big, lines, accent="orange", w=1.0): return C({"type": "stat", "label": label, "big": big, "lines": lines, "accent": accent}, w)
def lst(title, items, accent="orange", w=1.0): return C({"type": "list", "title": title, "items": items, "accent": accent}, w)
def N(nid, visuals, **kw): return dict(narr=nid, visuals=visuals, pad=kw.pop("pad", P), **kw)
def K(words, at=0.4, step=0.4, hold=2.8, size=120):
    return {"words": words, "at": at, "step": step, "hold": hold, "size": size, "box": "0x091020@0.55"}


def section(tag, title, chapter, accent="orange"):
    return {"label": tag.lower(), "dur": 1.5, "visuals": [C({"type": "section", "tag": tag, "title": title, "accent": accent})],
            "chapter": chapter, "pad": [0.5, 0.8]}


B = [
    # ---------------- cold open
    N("n00", [V(PHR, 0, 6.0, w=0.6),
              stat("Pharr International Bridge", "4 → 8 LANES", ["second structure open this fall", "about $50B in trade a year"], w=0.4)],
      chapter="Cold open: a bigger bridge, emptier factories", credit=RGVBJ + ", Oct 8, 2026; Texas Comptroller"),
    N("n01", [V(REY, 0, 12.0)], credit="Source: DATOZ via RGV Business Journal, Jun 22, 2026",
      kinetic=K(["10-YEAR HIGH", "IN VACANCY"], at=6.0, step=0.5, size=110)),
    N("n02", [IMG("a_pharr_n", 0.5, zoom=(1.0, 1.12), place="Pharr"), IMG("r09", 0.5, zoom=(1.0, 1.1), place="McAllen")]),
    N("n03", [V(DON, 0, 9.9)]),
    {"label": "on the record", "dur": 6.0, "visuals": [V(HL, 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "THE BORDER TRADE BET",
                                                "sub": "A bigger bridge, emptier factories"})], "pad": [0.5, 0.8]},
    # ---------------- part 1
    section("PART 1", "THE BIGGER BRIDGE", "Part 1: The bigger bridge"),
    N("n04", [V(PHR, 6.5, 8.0, w=0.55),
              stat("Bridge director Luis Bazán", "~5,000", ["trucks a day, both directions", "new structure: 4 more lanes, 100% more capacity"], "teal", w=0.45)],
      credit=RGVBJ + ", Oct 8, 2026 and Dec 30, 2025"),
    N("n05", [lst("PHARR BRIDGE UPGRADES", ["FAST lanes for pre-cleared cargo: since March", "20-acre truck park, about 300 spaces: early 2027"], "teal", w=0.5),
              IMG("a_pharr_bridge", 0.5, zoom=(1.0, 1.12), place="Pharr International Bridge")], credit="Source: Texas Border Business (2026)"),
    N("n06", [stat("Texas Comptroller", "$50B", ["trade a year through the Pharr bridge", "about 92,000 jobs supported"], w=0.45),
              IMG("a_mcallen_wide", 0.55, zoom=(1.0, 1.12), place="McAllen")], credit=RGVBJ + ", Oct 8, 2026"),
    N("n07", [IMG("a_donna_bridge", 0.5, zoom=(1.0, 1.12), place="Donna International Bridge"),
              lst("THE GATEWAY FORUM QUESTION", ["Can the roads keep up?", "Truck corridor behind Pharr and Donna: funding stuck"], w=0.5)],
      credit=RGVBJ + ", Oct 8, 2026; Episode 6"),
    N("n08", [IMG("r08", zoom=(1.0, 1.12), place="U.S. 77/83")]),
    # ---------------- part 2
    section("PART 2", "THE EMPTY FACTORIES", "Part 2: The empty factories", "blue"),
    N("n09", [V(REY, 12.5, 5.5, w=0.38), V(BARS, 0, 9.0, w=0.62)], credit="Source: DATOZ via RGV Business Journal, Jun 22, 2026"),
    N("n10", [lst("WHY THE SPACE IS EMPTY", ["Move-outs and corporate adjustments", "Expansions on hold over trade rules",
                                             "Not a wave of speculative building"], "blue", w=0.5), V(BARS, 9.5, 7.0, w=0.5)],
      credit="Sources: DATOZ via RGV Business Journal; Newmark; Solili"),
    N("n11", [stat("Reynosa · early 2026", "-2,500", ["maquila jobs", "a large logistics facility closed in March"], w=0.5),
              V(DON, 10.0, 6.0, w=0.5)], credit=RGVBJ + ", Mar 4 and Mar 24, 2026"),
    N("n12", [stat("Leased in Reynosa and Matamoros, past year", "553,000+ SQ FT", ["up 59%", "led by electronics"], "teal", w=0.5),
              stat("Vertiv · power equipment for AI data centers", "$150M", ["expansion in Reynosa", "about 1,000 jobs"], "teal", w=0.5)],
      credit=RGVBJ + ", Jun 22 and Jul 5, 2026"),
    N("n13", [IMG("a_brownsville_n", zoom=(1.0, 1.12), place="Brownsville, across from Matamoros")],
      credit="Source: DATOZ via RGV Business Journal", kinetic=K(["MATAMOROS", "ABOUT 3%"], at=1.0, step=0.5, size=120)),
    N("n14", [IMG("a_weslaco_wide", zoom=(1.12, 1.0), place="Weslaco")], kinetic=K(["A PAUSE,", "NOT A COLLAPSE"], at=1.5, step=0.5, size=120)),
    # ---------------- part 3
    section("PART 3", "A TRADE DEAL ON A ONE-YEAR CLOCK", "Part 3: A trade deal on a one-year clock"),
    N("n15", [stat("U.S.-Mexico-Canada Agreement · July 1, 2026", "NOT RENEWED", ["stays in force", "reviewed every year"], w=0.5),
              IMG("r06", 0.5, zoom=(1.0, 1.1), place="Donna port of entry")], credit=RGVBJ + ", Jul 1, 2026"),
    N("n16", [lst("SINCE THE DECISION", ["Officials: no immediate tariff or customs changes",
                                         "Rep. Henry Cuellar: cross-border investment 'freezing'"], w=0.5),
              IMG("a_mcallen_n", 0.5, zoom=(1.0, 1.12), place="McAllen")], credit="Sources: RGV Business Journal, Jul 1, 2026; Rio Grande Guardian"),
    N("n17", [stat("Two readings of the same deal", "10 YEARS vs. 1 YEAR", ["Mexico: ten-year deal with an annual review",
                                                                          "U.S.: yearly reviews until all agree to extend"], "blue", w=0.5),
              IMG("a_edinburg_new", 0.5, zoom=(1.0, 1.12), place="Edinburg")], credit="Sources: Rio Times, Oct 2026; RGV Business Journal"),
    N("n18", [IMG("r07", 0.5, zoom=(1.0, 1.1), place="U.S. 77/83 at TX 48"),
              stat("Valley business bankruptcies", "62 → 127", ["2024 to 2025: doubled"], w=0.5)],
      credit="Sources: RGV Business Journal, Mar 7 and Nov 23, 2026"),
    # ---------------- part 4
    section("PART 4", "WHAT'S STILL MOVING", "Part 4: What's still moving", "teal"),
    N("n19", [IMG("a_pharr_n", 0.5, zoom=(1.12, 1.0), pan=(0.6, 0.5, 0.4, 0.5), place="Pharr"),
              stat("Pharr tax increment zone", "+384 ACRES", ["near the international bridge", "vote slated by end of December"], "teal", w=0.5)],
      credit=RGVBJ + ", Nov 23, 2026"),
    N("n20", [stat("Mission · Bettcher", "$3M", ["about 50 new jobs"], "teal", w=0.33),
              IMG("a_harlingen", 0.34, zoom=(1.0, 1.12), place="Harlingen"),
              stat("Port of Harlingen", "$12.5M", ["infrastructure push for trade"], "teal", w=0.33)],
      credit=RGVBJ + ", Apr 30 and Jun 28, 2026"),
    N("n21", [IMG("a_airport_east", zoom=(1.0, 1.15), place="Cameron County")], credit=RGVBJ + ", May 26 and Jun 12, 2026"),
    # ---------------- part 5
    section("PART 5", "WHAT IT MEANS FOR BUILDERS, BUYERS AND LENDERS", "Part 5: What it means for builders, buyers and lenders", "teal"),
    N("n22", [lst("FOR BUILDERS", ["Industrial near new bridge capacity", "Truck routes that are actually funded",
                                   "Careful with speculative space"], "teal", w=0.5),
              IMG("a_pharr_bridge", 0.5, zoom=(1.12, 1.0), pan=(0.4, 0.6, 0.5, 0.5), place="Pharr International Bridge")]),
    N("n23", [lst("FOR BUYERS AND INVESTORS", ["Watch leases, not ribbon cuttings", "Leasing: electronics, data-center suppliers",
                                               "Pulled back: e-commerce, auto parts"], w=0.5),
              IMG("a_mcallen_wide", 0.5, zoom=(1.15, 1.0), place="McAllen")]),
    N("n24", [lst("FOR LENDERS", ["Trucking, warehousing, customs brokers", "Stress-test tariff changes at each review"], w=0.5),
              IMG("r08", 0.5, zoom=(1.1, 1.0), place="U.S. 77/83")]),
    N("n25", [lst("OUR WATCH LIST", ["Pharr zone expansion vote: by end of December", "Pharr truck park: early 2027",
                                     "The trade deal's next annual review"], "teal", w=0.5),
              IMG("a_donna_bridge", 0.5, zoom=(1.15, 1.0), place="Donna International Bridge")],
      credit="Sources: RGV Business Journal, Nov 23 and Jul 1, 2026; Texas Border Business"),
    N("n26", [V(PHR, 0, 7.0, w=0.5), IMG("a_mcallen_n", 0.5, zoom=(1.15, 1.0), place="McAllen")]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:
    if b.get("credit") and any(any(k in v.get("video", "") for k in ("v_", "map_", "chart_", "doc_")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep8/episode8.mp4", "audio_dir": "episodes/2026-12-border-trade/audio",
      "narration_json": "episodes/2026-12-border-trade/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Rising_Tide.mp3", "chapter": 0, "offset": 25},
          {"track": "assets/music/Industrial_Cinematic.mp3", "chapter": 2, "offset": 25},
          {"track": "assets/music/I_Can_Feel_it_Coming.mp3", "chapter": 3, "offset": 30},
          {"track": "assets/music/Unanswered_Questions.mp3", "chapter": 4, "offset": 40},
          {"track": "assets/music/Inspired.mp3", "chapter": 5, "offset": 30}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
