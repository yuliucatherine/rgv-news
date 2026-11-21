"""Builds timeline.json for Episode 4 v2 (RGV housing heading into 2027). v1 was scrapped by the owner (Nov 21, 2026).
v2: Episodes 1-3 narration voice, simple one-move 3D shots (10 s, smoothed to 60 fps), and real imagery first:
Wikimedia Commons photos (assets/photos/ep4/credits.json) and USGS aerial photos of real Valley subdivisions.
Run: python3 episodes/2026-12-rgv-housing/make_timeline.py"""
import json, os

E4, E3, E1 = "demo/ep4", "demo/ep3", "demo/ep1"
PH, AE = "assets/photos/ep4", "assets/photos/ep4/aerial"
P = [0.15, 0.3]
MOI, PRC, GRW, PAY = (f"{E4}/v_bars_{n}_s.mp4" for n in ("moi", "price", "growth", "payment"))
CR, CL, MAP, DOC = f"{E4}/chart_rates.mp4", f"{E4}/chart_listings.mp4", f"{E4}/map_valley.mp4", f"{E4}/doc_afford.mp4"
SB, CH = f"{E1}/v_starbase_s.mp4", f"{E3}/v_channel_s.mp4"
RGVBJ, FRED = "Source: RGV Business Journal", "Data: Realtor.com via FRED"
USGS = "Imagery: USGS The National Map"
CRED = json.load(open(os.path.join(PH, "credits.json")))


def V(path, ss=0, ln=None, w=1.0):
    v = {"video": path, "ss": ss, "weight": w}
    if ln: v["len"] = ln
    return v


def IMG(name, w=1.0, zoom=(1.0, 1.12), pan=(0.5, 0.5, 0.5, 0.5), place=None, portrait=False):
    """Real photo with a slow push/pan and its own on-screen credit (author, license; place if not in the Valley)."""
    if name.startswith("a_"):
        path, credit = f"{AE}/{name}.jpg", f"{place} · {USGS}" if place else USGS
    else:
        c = CRED[name]; path = f"{PH}/{name}.jpg"
        credit = f"Photo: {c['artist']}, {c['license']}" + (f" · {place}" if place else "")
    v = {"image": path, "weight": w, "zoom": list(zoom), "pan": list(pan), "credit": credit}
    if portrait: v["portrait_fill"] = True
    return v


def C(card, w=1.0): return {"card": card, "weight": w}
def stat(label, big, lines, accent="orange", w=1.0): return C({"type": "stat", "label": label, "big": big, "lines": lines, "accent": accent}, w)
def lst(title, items, accent="orange", w=1.0): return C({"type": "list", "title": title, "items": items, "accent": accent}, w)
def N(nid, visuals, **kw): return dict(narr=nid, visuals=visuals, pad=kw.pop("pad", P), **kw)
def K(words, at=0.4, step=0.4, hold=2.8, size=120, box=True):
    k = {"words": words, "at": at, "step": step, "hold": hold, "size": size}
    if box: k["box"] = "0x091020@0.55"
    return k


def section(tag, title, chapter, accent="orange"):
    return {"label": tag.lower(), "dur": 1.5, "visuals": [C({"type": "section", "tag": tag, "title": title, "accent": accent})],
            "chapter": chapter, "pad": [0.5, 0.8]}


B = [
    # ---------------- cold open
    N("n00", [IMG("a_edinburg_sub", 0.6, zoom=(1.0, 1.15), pan=(0.45, 0.55, 0.7, 0.25), place="North Edinburg"),
              IMG("p09b", 0.4, zoom=(1.0, 1.08), place="Oregon (details blurred)", portrait=True)],
      chapter="Cold open: a 36-year high"),
    N("n01", [V(CL, 2.5, 10.5)], kinetic=K(["997", "→", "3,432"], at=6.0, size=140),
      headline=["McALLEN METRO", "More homes for sale than at any point in 36 years"],
      credit="Source: Texas A&M Real Estate Center MLS data via RGV Business Journal, Jul 2026"),
    N("n02", [V(CR, 6.5, 7.5)], credit="Data: Freddie Mac via FRED"),
    N("n03", [IMG("p03", 0.5, zoom=(1.05, 1.15), pan=(0.3, 0.5, 0.6, 0.5), place="Harlingen"),
              IMG("a_weslaco_wide", 0.5, zoom=(1.0, 1.12), place="Weslaco area")],
      kinetic=K(["BUYER'S MARKET", "OR", "WARNING SIGN?"], at=4.6, step=0.4, size=104)),
    {"label": "on the record", "dur": 6.0, "visuals": [V(f"{E4}/headlines.mp4", 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "RGV HOUSING HEADING INTO 2027",
                                                "sub": "Buyer's market or warning sign?"})], "pad": [0.5, 0.8]},
    # ---------------- part 1: the glut
    section("PART 1", "THE GLUT", "Part 1: The glut"),
    N("n04", [V(CL, 0, 8.0, w=0.55), IMG("a_mcallen_wide", 0.45, zoom=(1.0, 1.1), place="North McAllen")],
      kinetic=K(["6 MONTHS", "=", "BALANCED"], at=9.0, step=0.45, hold=3.2)),
    N("n05", [V(MOI, 0, 4.0, w=0.45), stat("McAllen metro · May 2021", "~2 MONTHS",
              ["about 757 active listings", "multiple offers, waived inspections"], "blue", w=0.55)],
      credit=RGVBJ + ", Jul 7, 2026"),
    N("n06", [IMG("a_edinburg_nw", 0.55, zoom=(1.0, 1.15), pan=(0.6, 0.4, 0.4, 0.5), place="Northwest Edinburg"),
              IMG("p11", 0.45, zoom=(1.0, 1.1), place="illustrative")]),
    N("n07", [V(MOI, 4.0, 6.0)], credit=RGVBJ + ", Sep 25, 2026"),
    N("n08", [V(MAP, 4.5, 9.5)], credit="Quote: Emiliano Zapata, Capital Insiders, via RGV Business Journal, Jan 2026"),
    # ---------------- part 2: prices
    section("PART 2", "PRICES ARE SLIPPING", "Part 2: Prices are slipping", "blue"),
    N("n09", [IMG("p01", zoom=(1.0, 1.1), pan=(0.4, 0.5, 0.6, 0.5), place="McAllen")],
      kinetic=K(["CRASH?", "NO.", "SLIPPING."], at=2.4, step=0.6, size=130)),
    N("n10", [V(PRC, 0, 10.0, w=0.65), stat("Median sale price · McAllen metro", "~$245K",
              ["roughly flat since 2023", "through Aug 2026"], "blue", w=0.35)],
      credit=FRED + " · " + RGVBJ + ", Sep 25, 2026"),
    N("n11", [stat("Typical days on market · McAllen", "78 DAYS", ["October 2026", "48 days in October 2021"]),
              IMG("p15", 0.8, zoom=(1.0, 1.1), place="Edinburg"),
              stat("McAllen listings with a price cut", "1 IN 6", ["540 of 3,432 listings", "October 2026"])], credit=FRED),
    N("n12", [lst("WHAT BUILDERS ARE OFFERING", ["Rate buy-downs", "Appliance packages", "Warranties",
                                                 "Some new homes priced below resale"], "teal"),
              IMG("p04", 0.8, zoom=(1.05, 1.15), pan=(0.5, 0.4, 0.5, 0.6), place="Harlingen"),
              stat("Gumwood Ave, McAllen · new 3-bed", "$275K → $259K", ["listed February 2026", "asking price by August"], "blue")],
      credit="Brian Reed via RGV Business Journal, Feb 2026; RGV Business Journal, Sep 25, 2026"),
    # ---------------- part 3: the rate whiplash
    section("PART 3", "THE RATE WHIPLASH", "Part 3: The rate whiplash"),
    N("n13", [V(CR, 1.5, 7.5, w=0.6), stat("McAllen metro closings · January 2026", "+21%",
              ["vs. January 2025", "Texas A&M Real Estate Center data"], "teal", w=0.4)],
      credit="Freddie Mac via FRED · " + RGVBJ + ", Feb 25, 2026"),
    N("n14", [V(CR, 7.0, 7.0)], credit="Sources: Freddie Mac; NAHB Eye on Housing, Nov 2026"),
    N("n15", [V(PAY, 0, 10.0, w=0.55), stat("RGV News calculation", "$1,373 → $1,570",
              ["$255,000 home · 10% down · 30-yr fixed", "principal and interest only"], w=0.45)]),
    N("n16", [stat("McAllen metro sales · September 2026", "-8%", ["333 sales vs. 361 a year earlier",
                                                                  "Texas A&M Real Estate Center data"], "blue"),
              IMG("p13", zoom=(1.0, 1.1), place="McAllen")], credit=RGVBJ + ", Oct 22, 2026"),
    # ---------------- part 4: the affordability gap
    section("PART 4", "THE AFFORDABILITY GAP", "Part 4: The affordability gap", "teal"),
    N("n17", [V(GRW, 0, 10.0, w=0.6), V(DOC, 0, 6.0, w=0.4)]),
    N("n18", [stat("Median household income · Hidalgo County", "$55,829", ["30% for housing ≈ $1,396 a month",
                                                                       "U.S. Census Bureau SAIPE, 2024"], "teal"),
              IMG("p14", zoom=(1.0, 1.1), place="Edinburg")]),
    N("n19", [C({"type": "quote", "quote": "The payment is $2,800 a month for an almost above entry-level house.",
                 "by": "Craig Grove, GRT Realty, Brownsville", "source": "to the RGV Business Journal, February 2026"}),
              V(DOC, 9.5, 6.5)], credit="Myssie Cardenas-Barajas via RGV Business Journal, Jul 7, 2026"),
    N("n20", [lst("THE PRICE GAP", ["Demand: $150K to $250K", "Lots: $50K to $70K each", "A $200K new house: \"nearly impossible\""]),
              IMG("a_mcallen_n", zoom=(1.0, 1.15), pan=(0.5, 0.5, 0.65, 0.4), place="North McAllen")],
      credit="Sources: Myssie Cardenas-Barajas; Emiliano Zapata; via RGV Business Journal"),
    # ---------------- part 5: two markets
    section("PART 5", "TWO DIFFERENT MARKETS", "Part 5: Two different markets", "blue"),
    N("n21", [IMG("p02", 0.5, zoom=(1.05, 1.15), place="Harlingen"), V(MAP, 15, 6.5, w=0.5)],
      credit=RGVBJ + ", Sep 25, 2026 (August data)"),
    N("n22", [IMG("a_harlingen", 0.5, zoom=(1.0, 1.15), place="Downtown Harlingen"),
              stat("Median listing · Brownsville-Harlingen", "$297K", ["October 2026", "peak: $321K in October 2022"], "teal", w=0.5)],
      credit=FRED),
    N("n23", [V(SB, 0, 5.0), V(CH, 0, 5.0), stat("Brownsville-Harlingen home sales", "-17%",
                                                 ["through August 2026", "back to 2019 levels"], "blue")],
      credit=RGVBJ + ", Sep 25, 2026"),
    # ---------------- part 6: what to do
    section("PART 6", "WHAT TO DO BEFORE 2027", "Part 6: What to do before 2027"),
    N("n24", [IMG("p09b", 0.4, zoom=(1.08, 1.0), place="Oregon (details blurred)", portrait=True),
              lst("IF YOU'RE BUYING", ["~9 months of inventory = leverage", "Ask for price cuts", "Ask for closing costs",
                                        "Ask for rate buy-downs"], "teal", w=0.6)]),
    N("n25", [lst("IF YOU'RE BUILDING", ["The gap is the opportunity", "Townhomes and smaller homes", "Build-to-rent",
                                          "Target $150K to $250K"], "blue"),
              IMG("p11", zoom=(1.1, 1.0), place="illustrative")]),
    N("n26", [lst("IF YOU'RE LENDING", ["Banks are tightening construction loans", "Private lenders ~13% vs. banks ~8%",
                                         "A home that sits 9 months gets expensive"]),
              IMG("a_edinburg_nw", zoom=(1.12, 1.0), pan=(0.3, 0.6, 0.5, 0.5), place="Northwest Edinburg")],
      credit="Emiliano Zapata, Capital Insiders, via RGV Business Journal, Jan 2026"),
    N("n27", [lst("OUR WATCH LIST", ["Weekly mortgage rates (Freddie Mac)", "Monthly McAllen inventory",
                                      "Brownsville sales vs. port and SpaceX payrolls"], "teal"), V(CR, 9.5, 4.5)]),
    N("n28", [IMG("p01", zoom=(1.15, 1.0), pan=(0.6, 0.5, 0.4, 0.5), place="McAllen")]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays, charts and maps carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any(any(k in v.get("video", "") for k in ("v_", "map_", "chart_", "doc_")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep4/episode4.mp4", "audio_dir": "episodes/2026-12-rgv-housing/audio",
      "narration_json": "episodes/2026-12-rgv-housing/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Rising_Tide.mp3", "chapter": 0, "offset": 20},
          {"track": "assets/music/I_Can_Feel_it_Coming.mp3", "chapter": 3, "offset": 30},
          {"track": "assets/music/Dreamer.mp3", "chapter": 4, "offset": 20},
          {"track": "assets/music/Inspired.mp3", "chapter": 6, "offset": 40}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
