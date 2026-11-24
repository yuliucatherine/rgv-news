"""Builds timeline.json for Episode 6 (The Rio Grande Valley's road problem).
Episodes 1-3 voice, simple one-move 3D, real imagery first: USGS aerials of SH 4, the Queen Isabella Causeway, the Pharr
and Donna bridges and US 77; the Starbase/SH 4, South Padre Island and Port of Brownsville flyovers over real imagery;
road and bridge photos from Wikimedia Commons.
Run: python3 episodes/2026-12-valley-roads/make_timeline.py"""
import json, os

E6, E1 = "demo/ep6", "demo/ep1"
P = [0.15, 0.3]
BARS, HL = f"{E6}/v_bars_sh4_s.mp4", f"{E6}/headlines.mp4"
M_SPI, M_HID, M_I69, M_CON = f"{E6}/map_spi.mp4", f"{E6}/map_hidalgo.mp4", f"{E6}/map_i69.mp4", f"{E6}/map_connector.mp4"
SBV, SH4 = f"{E1}/v_starbase_s.mp4", f"{E6}/v_sh4_192_s.mp4"
SPI, PORT = f"{E6}/v_spi_cw_s.mp4", f"{E6}/v_port_s.mp4"
USGS = "Imagery: USGS The National Map"
RGVBJ = "Source: RGV Business Journal"
PHOTO_DIRS = {"p": "assets/photos/ep4", "q": "assets/photos/ep5", "r": "assets/photos/ep6"}
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
        d = next(f"assets/photos/{e}/aerial" for e in ("ep6", "ep5", "ep4") if os.path.exists(f"assets/photos/{e}/aerial/{name}.jpg"))
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


def have(name): return name in CRED   # photos still downloading are skipped, never blank


def PH(name, alt, **kw): return IMG(name if have(name) else alt, **kw)


SH4P = "State Highway 4 near Boca Chica"
B = [
    # ---------------- cold open
    N("n00", [IMG("a_sh4_flats", 0.45, zoom=(1.0, 1.15), pan=(0.35, 0.6, 0.55, 0.5), place=SH4P), V(SBV, 0, 8.0, w=0.55)],
      chapter="Cold open: one road, ten times the traffic", credit="Source: TxDOT counts via RGV Business Journal",
      kinetic=K(["645", "→ 6,743", "A DAY"], at=7.0, step=0.5, size=120)),
    N("n01", [V(SH4, 4.0, 8.0, w=0.6),
              stat("TxDOT · 2027 Unified Transportation Program", "$192M", ["SH 4: two lanes to a divided four-lane highway",
                                                                             "bids scheduled before August 2027"], w=0.4)],
      credit=RGVBJ + ", Aug 26, 2026"),
    N("n02", [PH("r09", "a_mcallen_n", w=0.5, zoom=(1.0, 1.1), place="McAllen"),
              IMG("a_pharr_bridge", 0.5, zoom=(1.0, 1.12), pan=(0.5, 0.6, 0.5, 0.45), place="Pharr International Bridge")]),
    N("n03", [PH("r07", "a_brownsville_n", w=0.5, zoom=(1.05, 1.15), place="Brownsville"),
              IMG("a_causeway", 0.5, zoom=(1.0, 1.12), place="Queen Isabella Causeway")]),
    {"label": "on the record", "dur": 6.0, "visuals": [V(HL, 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "THE VALLEY'S ROAD PROBLEM",
                                                "sub": "Where the next boom can (and can't) go"})], "pad": [0.5, 0.8]},
    # ---------------- part 1: the one road to Starbase
    section("PART 1", "THE ONE ROAD TO STARBASE", "Part 1: The one road to Starbase"),
    N("n04", [V(SBV, 8.5, 12.0)], credit=RGVBJ + ", Dec 16, 2025"),
    N("n05", [lst("TXDOT'S PLAN FOR SH 4", ["Two lanes to a divided four-lane highway", "Brownsville to Starbase",
                                            "Inside the state's existing right-of-way", "No new land to buy"], "teal", w=0.5),
              IMG("a_sh4_flats", 0.5, zoom=(1.12, 1.0), pan=(0.6, 0.5, 0.4, 0.55), place=SH4P)],
      credit=RGVBJ + ", Dec 16, 2025 and Aug 26, 2026"),
    N("n06", [V(BARS, 0, 12.0)]),
    N("n07", [IMG("a_starbase_wide", 0.35, zoom=(1.0, 1.12), place="Starbase"),
              lst("ALONG THE CORRIDOR", ["Starbase has approved commercial projects", "Rio West: housing, retail, restaurants",
                                         "County wants four lanes west to FM 511"], w=0.35),
              IMG("a_sh4_west", 0.3, zoom=(1.0, 1.1), pan=(0.4, 0.5, 0.6, 0.5), place="West end of SH 4, toward Brownsville")],
      credit=RGVBJ + ", Dec 16, 2025"),
    # ---------------- part 2: one bridge to the island
    section("PART 2", "ONE BRIDGE TO THE ISLAND", "Part 2: One bridge to the island", "blue"),
    N("n08", [V(SPI, 0, 9.0, w=0.65), PH("r02", "a_causeway", w=0.35, zoom=(1.0, 1.1), place="Queen Isabella Causeway")],
      credit="Source: TxDOT, South Padre Island Second Access Project"),
    N("n09", [V(M_SPI, 0, 12.0, w=0.75), PH("r01", "a_spi_north", w=0.25, zoom=(1.0, 1.1), place="South Padre Island")],
      credit="Sources: KRGV; TxDOT; Texas Transportation Commission, Dec 2023"),
    N("n10", [stat("Second causeway · State Highway 104", "UP TO $1B", ["two routes, about 8 miles across the Laguna Madre",
                                                                         "four lanes · 5 to 6 years to build"], "blue", w=0.45),
              V(M_SPI, 12.5, 11.0, w=0.55)], credit="Source: TxDOT public meeting via KRGV, Nov 2025"),
    N("n11", [IMG("a_spi_north", 0.5, zoom=(1.0, 1.12), pan=(0.5, 0.55, 0.5, 0.45), place="North end of South Padre Island"),
              PH("r03", "a_laguna", w=0.5, zoom=(1.0, 1.1), place="Port Isabel and the Queen Isabella Causeway")],
      kinetic=K(["NO START", "DATE YET"], at=4.5, step=0.5, size=120)),
    # ---------------- part 3: the trucks and the bridges
    section("PART 3", "THE TRUCKS AND THE BRIDGES", "Part 3: The trucks and the bridges"),
    N("n12", [IMG("a_pharr_bridge", zoom=(1.0, 1.15), pan=(0.5, 0.45, 0.5, 0.6), place="Pharr International Bridge")],
      credit=RGVBJ + ", Feb 26, 2026"),
    N("n13", [PH("r06", "a_donna_bridge", w=0.35, zoom=(1.0, 1.1), place="Donna port of entry"),
              stat("Donna International Bridge", "$62M", ["U.S. and Mexican inspectors in one facility", "six dedicated lanes",
                                                         "up to 100 trucks an hour · done by end of 2028"], "teal", w=0.35),
              IMG("a_donna_bridge", 0.3, zoom=(1.0, 1.12), pan=(0.4, 0.4, 0.5, 0.5), place="Donna International Bridge")],
      credit=RGVBJ + ", Feb 26, 2026"),
    N("n14", [V(M_HID, 0, 15.0, w=0.65),
              stat("International Bridge Trade Corridor", "$150M", ["requested by Gov. Abbott in 2023",
                                                                     "toll-free, about 13 miles · funding stuck"], w=0.35)],
      credit=RGVBJ + ", Feb 26, 2026; Donna interim city manager Jesus Reyna"),
    N("n15", [IMG("a_pharr_n", zoom=(1.12, 1.0), place="Pharr")],
      kinetic=K(["100 TRUCKS", "AN HOUR"], at=1.6, step=0.5, size=120)),
    N("n16", [V(PORT, 2.0, 8.0, w=0.6),
              lst("THREE HEAVYWEIGHT CORRIDORS", ["Port of Harlingen", "Port of Brownsville", "Hidalgo County", "None connect to each other"],
                  "teal", w=0.4)], credit="Source: Walker Smith, Port of Harlingen, via RGV Business Journal, Feb 26, 2026"),
    # ---------------- part 4: the interstate gap
    section("PART 4", "THE INTERSTATE GAP", "Part 4: The interstate gap", "blue"),
    N("n17", [V(M_I69, 0, 19.5, w=0.76), IMG("a_us77_kenedy", 0.24, zoom=(1.0, 1.12), place="U.S. 77, Kenedy County")],
      credit="Sources: TxDOT via The Monitor, Jun 11, 2025; Cameron County RMA"),
    N("n18", [V(M_CON, 0, 12.0, w=0.65), PH("r08", "a_harlingen", w=0.35, zoom=(1.05, 1.15), place="Harlingen")],
      credit="Sources: TxDOT I-69 Connector fact sheet; Rio Grande Guardian, Feb 2026"),
    # ---------------- part 5: what it means
    section("PART 5", "WHAT IT MEANS FOR BUILDERS, BUYERS AND LENDERS", "Part 5: What it means for builders, buyers and lenders", "teal"),
    N("n19", [lst("FUNDED: PLAN AROUND IT", ["SH 4 widening: $192M, bids before Aug 2027", "Donna bridge lanes: done by end of 2028"], "teal", w=0.5),
              V(SBV, 21.0, 6.0, w=0.5)]),
    N("n20", [lst("NOT FUNDED YET: TREAT AS OPTIONS", ["Second causeway: environmental study", "Trade corridor: funding stuck",
                                                      "I-69 Connector: decision in 2027"], w=0.5),
              IMG("a_laguna", 0.5, zoom=(1.0, 1.1), place="Laguna Madre")]),
    N("n21", [lst("FOR BUILDERS", ["Industrial and logistics near the Pharr and Donna bridges",
                                   "Housing and services on the Brownsville-Starbase corridor"], "teal", w=0.5),
              IMG("a_sh4_west", 0.5, zoom=(1.12, 1.0), pan=(0.6, 0.5, 0.4, 0.5), place="SH 4, east of Brownsville")]),
    N("n22", [quote("Is it in the state's ten-year plan with real money behind it, or is it still in a study?",
                    "The lender's question", "RGV News", w=0.6),
              PH("r05", "a_causeway", w=0.4, zoom=(1.0, 1.1), place="South Padre Island")]),
    N("n23", [lst("OUR WATCH LIST", ["SH 4 bids: by August 2027", "Donna bridge: done by end of 2028",
                                     "Second causeway: environmental decision", "Legislature opens Jan 12"], "teal")]),
    N("n24", [V(SPI, 12.0, 6.0, w=0.5), IMG("a_sh4_flats", 0.5, zoom=(1.15, 1.0), place=SH4P)]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays, charts and maps carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any(any(k in v.get("video", "") for k in ("v_", "map_", "chart_", "doc_")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep6/episode6.mp4", "audio_dir": "episodes/2026-12-valley-roads/audio",
      "narration_json": "episodes/2026-12-valley-roads/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Rising_Tide.mp3", "chapter": 0, "offset": 10},
          {"track": "assets/music/Deliberate_Thought.mp3", "chapter": 2, "offset": 45},
          {"track": "assets/music/Industrial_Cinematic.mp3", "chapter": 3, "offset": 10},
          {"track": "assets/music/Unanswered_Questions.mp3", "chapter": 4, "offset": 50},
          {"track": "assets/music/Inspired.mp3", "chapter": 5, "offset": 20}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
