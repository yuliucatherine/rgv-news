"""Builds timeline.json for Episode 7 (the Valley's boom vs. its paychecks).
Episodes 1-3 voice, real imagery first, new Blender angles (Starbase orbit, Pharr bridge orbit, Donna at golden hour,
SH 4 at sunset; owner rule Nov 24: no reused SH 4 flyover), a 3D wage chart, USGS aerials and Wikimedia photos.
Run: python3 episodes/2026-12-valley-jobs/make_timeline.py"""
import json, os

E7, FLY = "demo/ep7", "demo/flyovers"
P = [0.15, 0.3]
HL, BARS = f"{E7}/headlines.mp4", f"{E7}/v_bars_wages_s.mp4"
SB, SH4D = f"{FLY}/v2/v_starbase_orbit_s.mp4", f"{FLY}/v_sh4_dusk_west_s.mp4"
DON, PHR = f"{FLY}/v2/v_donna_dusk_s.mp4", f"{FLY}/v2/v_pharr_bridge_top_s.mp4"
PORT = "demo/ep6/v_port_s.mp4"
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
    N("n00", [V(SB, 0, 8.0, w=0.55),
              stat("Cameron County · its four biggest projects", "$41.1B", ["Rio Grande LNG · Texas LNG",
                                                                            "Starbase · Saronic's Port Alpha shipyard"], w=0.45)],
      chapter="Cold open: $41 billion in projects, 700 jobs lost", credit=RGVBJ + ", Oct 3, 2026, citing Cameron County"),
    N("n01", [IMG("a_brownsville_n", 0.5, zoom=(1.0, 1.12), pan=(0.4, 0.5, 0.55, 0.5), place="Brownsville"),
              stat("Rio Grande Valley employment · Q3 2026", "-0.6%", ["annualized, three months through September",
                                                                       "about 700 jobs · Texas and U.S. still grew"], "blue", w=0.5)],
      credit=FED + ", Q3 2026", kinetic=K(["ABOUT 700", "JOBS LOST"], at=8.5, step=0.5, size=120)),
    N("n02", [IMG("p01", 0.5, zoom=(1.0, 1.1), place="McAllen"),
              IMG("a_edinburg_sub", 0.5, zoom=(1.12, 1.0), pan=(0.5, 0.5, 0.45, 0.55), place="Edinburg")]),
    N("n03", [V(SH4D, 0, 10.5)]),
    {"label": "on the record", "dur": 6.0, "visuals": [V(HL, 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "THE BOOM VS. THE PAYCHECKS",
                                                "sub": "Where the Valley's money and jobs actually are"})], "pad": [0.5, 0.8]},
    # ---------------- part 1: the money on paper
    section("PART 1", "THE MONEY ON PAPER", "Part 1: The money on paper"),
    N("n04", [V(PORT, 0, 11.0, w=0.55),
              stat("Cameron County estimates", "$31.8B", ["Rio Grande LNG alone",
                                                          "of about $41.1B across the four projects"], w=0.45)],
      credit=RGVBJ + ", Oct 3, 2026, citing Cameron County"),
    N("n05", [stat("Rio Grande LNG · NextDecade", "~80%", ["Trains 1 and 2 complete, September 2026",
                                                           "first LNG expected Q2 2027"], "teal", w=0.45),
              V(PORT, 12.0, 10.0, w=0.55)], credit="Source: NextDecade third quarter 2026 business update, Oct 29, 2026"),
    N("n06", [lst("THE OTHER BIG PROJECTS", ["Texas LNG: investment decision delayed two years",
                                             "Saronic Port Alpha: 95% county tax abatement, June",
                                             "Abatement phases start in 2029"], w=0.5),
              IMG("a_brownsville_n", 0.5, zoom=(1.12, 1.0), pan=(0.6, 0.45, 0.45, 0.55), place="Brownsville")],
      credit="Sources: RGV Business Journal, Oct 3, 2026; KSAT; USNI News, Jul 16, 2026"),
    N("n07", [IMG("a_mcallen_wide", 0.5, zoom=(1.0, 1.12), place="McAllen"),
              stat("Regional project tallies", "$110B+", ["underway, approved or just announced",
                                                          "not money spent · not paychecks written"], "blue", w=0.5)],
      credit="Sources: Strategic Partnerships Inc.; San Antonio Express-News (Nov 2026)"),
    # ---------------- part 2: the jobs on the ground
    section("PART 2", "THE JOBS ON THE GROUND", "Part 2: The jobs on the ground", "blue"),
    N("n08", [lst("VALLEY JOB GROWTH IN 2026 (ANNUALIZED)", ["First quarter: +1.4%", "Second quarter: +1.3%",
                                                            "Third quarter: -0.6%"], "blue", w=0.5),
              IMG("a_weslaco_wide", 0.5, zoom=(1.0, 1.12), place="Weslaco")], credit=FED + ", Q1-Q3 2026"),
    N("n09", [IMG("a_mcallen_n", 0.5, zoom=(1.12, 1.0), place="McAllen"),
              stat("McAllen metro · year through October", "+4,500", ["jobs, to 311,800 · mostly health care and education",
                                                                      "Brownsville metro: about -300"], "teal", w=0.5)],
      credit=RGVBJ + ", Nov 20, 2026, citing Texas Workforce Commission data"),
    N("n10", [IMG("p17", zoom=(1.0, 1.12), place="Harlingen, in the Brownsville metro")],
      credit=FED + ", Q3 2026", kinetic=K(["BROWNSVILLE", "-2.8%"], at=1.0, step=0.5, size=120)),
    N("n11", [stat("Unemployment rate · September 2026", "6.0%", ["Brownsville 6.0% · McAllen 5.8%", "Texas 4.4%"], "blue", w=0.35),
              IMG("p14", 0.3, zoom=(1.0, 1.1), place="Edinburg"),
              stat("Brownsville labor force", "-2.1%", ["year over year", "part of why unemployment fell"], w=0.35)],
      credit=FED + ", Q3 2026"),
    N("n12", [IMG("a_harlingen", zoom=(1.12, 1.0), place="Harlingen")],
      kinetic=K(["FEWER PEOPLE", "WORKING OR LOOKING"], at=3.2, step=0.5, size=110)),
    # ---------------- part 3: why the paychecks lag
    section("PART 3", "WHY THE PAYCHECKS LAG", "Part 3: Why the paychecks lag"),
    N("n13", [V(PHR, 0, 9.0, w=0.6),
              lst("DALLAS FED · LUIS TORRES, NOV 2026", ["Weak hiring reflects the supply of workers",
                                                         "Not a weak economy"], "teal", w=0.4)],
      credit=RGVBJ + ", Nov 18, 2026"),
    N("n14", [lst("WHAT'S HOLDING HIRING BACK", ["Labor force growth flat or negative",
                                                 "Immigration policies keep some workers out of some industries",
                                                 "Wage growth still solid"], "teal", w=0.5),
              IMG("p16", 0.5, zoom=(1.0, 1.1), place="Edinburg")], credit=RGVBJ + ", Nov 18, 2026"),
    N("n15", [stat("Rio Grande Valley · 2025", "2.6% vs. 0.2%", ["economic output grew 2.6%", "jobs grew 0.2%"], "blue", w=0.45),
              V(PHR, 9.5, 8.0, w=0.55)],
      credit=RGVBJ + ", Feb 15, 2026, citing the Dallas Fed", kinetic=K(["LOW HIRE", "LOW FIRE"], at=10.0, step=0.5, size=120)),
    N("n16", [V(BARS, 0, 20.0)]),
    N("n17", [stat("Rio Grande LNG", "7,500 → 700", ["peak construction workers approved by FERC",
                                                     "permanent jobs once the plant runs"], w=0.35),
              IMG("p11", 0.3, zoom=(1.0, 1.1), place="illustrative"),
              stat("Saronic Port Alpha", "UP TO 10,000", ["direct jobs over a decade (company estimate)",
                                                          "abatement phases start in 2029"], "teal", w=0.35)],
      credit="Sources: FERC (Apr 2026); NextDecade; Defense News and USNI News (Jul 2026)"),
    # ---------------- part 4: the cracks to watch
    section("PART 4", "THE CRACKS TO WATCH", "Part 4: The cracks to watch", "blue"),
    N("n18", [V(DON, 0, 9.0, w=0.6),
              lst("TRUCKING BANKRUPTCIES", ["Xoco Transport, Hidalgo: Chapter 11", "American Petroleum Carriers, McAllen: Chapter 11",
                                            "Three more carriers in Laredo"], w=0.4)],
      credit=RGVBJ + ", Nov 23, 2026"),
    N("n19", [stat("Valley business bankruptcies", "62 → 127", ["2024 to 2025: doubled",
                                                               "trucking: revenue drops, truck debt, diesel prices"], w=0.5),
              IMG("r07", 0.5, zoom=(1.0, 1.1), place="U.S. 77/83 at TX 48")],
      credit="Sources: RGV Business Journal, Mar 7, 2026 and Nov 23, 2026"),
    N("n20", [IMG("a_airport_east", 0.5, zoom=(1.0, 1.12), place="Farmland in Cameron County"),
              stat("New World screwworm", "3 COUNTIES", ["first Hidalgo County detection, Nov 21",
                                                         "parts of Cameron, Hidalgo and Willacy restricted"], w=0.5)],
      credit="Sources: Texas Animal Health Commission order, Nov 23, 2026; RGV Business Journal, Nov 24 and 26, 2026"),
    N("n21", [IMG("a_rio_hondo_fields", zoom=(1.12, 1.0), place="Farmland near Rio Hondo")]),
    # ---------------- part 5: what it means
    section("PART 5", "WHAT IT MEANS FOR BUILDERS, BUYERS AND LENDERS", "Part 5: What it means for builders, buyers and lenders", "teal"),
    N("n22", [stat("Valley city sales tax · year through October", "+6.2%", ["Texas Comptroller data",
                                                                            "lags actual sales by about two months"], "teal", w=0.45),
              IMG("p13", 0.55, zoom=(1.0, 1.1), place="La Plaza Mall, McAllen")],
      credit=RGVBJ + ", Nov 25, 2026, citing the Texas Comptroller"),
    N("n23", [lst("FOR BUILDERS", ["Price for when workers arrive", "McAllen: health care and education jobs now",
                                   "Brownsville: first LNG Q2 2027, Saronic from 2029"], "teal", w=0.5),
              V(SH4D, 11.0, 5.0, w=0.5)]),
    N("n24", [lst("FOR LENDERS", ["Freight and trucking borrowers", "Ranch exposure in the screwworm zone",
                                  "Rental demand tied to construction crews"], w=0.5),
              IMG("a_edinburg_new", 0.5, zoom=(1.0, 1.12), place="Edinburg")]),
    N("n25", [lst("OUR WATCH LIST", ["Dallas Fed Texas jobs forecast: monthly", "Rio Grande LNG first gas: by year end",
                                     "Pharr: 384-acre zone expansion, by end of December", "First LNG: Q2 2027"], "teal", w=0.5),
              V(SB, 9.0, 8.5, w=0.5)],
      credit="Sources: Federal Reserve Bank of Dallas; NextDecade, Oct 29, 2026; RGV Business Journal, Nov 23, 2026"),
    N("n26", [V(DON, 9.5, 6.5, w=0.5), IMG("a_mcallen_wide", 0.5, zoom=(1.15, 1.0), pan=(0.55, 0.5, 0.45, 0.5), place="McAllen")]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays, charts and maps carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any(any(k in v.get("video", "") for k in ("v_", "map_", "chart_", "doc_")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep7/episode7.mp4", "audio_dir": "episodes/2026-12-valley-jobs/audio",
      "narration_json": "episodes/2026-12-valley-jobs/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Crusade_Heavy_Industry.mp3", "chapter": 0, "offset": 30},
          {"track": "assets/music/Deliberate_Thought.mp3", "chapter": 2, "offset": 10},
          {"track": "assets/music/Unanswered_Questions.mp3", "chapter": 3, "offset": 20},
          {"track": "assets/music/Dreamer.mp3", "chapter": 4, "offset": 15},
          {"track": "assets/music/I_Can_Feel_it_Coming.mp3", "chapter": 5, "offset": 10}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
