"""Builds timeline.json for Episode 4 (RGV housing heading into 2027).
Run: python3 episodes/2026-12-rgv-housing/make_timeline.py
3D bar shots use camera focus tours and are rendered 12 s, smoothed to 60 fps (stretch 1.0)."""
import json, os

E4, E2, E1 = "demo/ep4", "demo/ep2", "demo/ep1"
P = [0.15, 0.3]   # tight: no dead air between paragraphs
LST, MOI, PRC = f"{E4}/v_bars_listings_s.mp4", f"{E4}/v_bars_moi_s.mp4", f"{E4}/v_bars_price_s.mp4"
GRW, PAY = f"{E4}/v_bars_growth_s.mp4", f"{E4}/v_bars_payment_s.mp4"
CR, CL, MAP, DOC = f"{E4}/chart_rates.mp4", f"{E4}/chart_listings.mp4", f"{E4}/map_valley.mp4", f"{E4}/doc_afford.mp4"
EDI, SB = f"{E2}/v_edinburg_s.mp4", f"{E1}/v_starbase_s.mp4"
RGVBJ = "Source: RGV Business Journal"
FRED = "Data: Realtor.com via FRED"


def V(path, ss=0, ln=None, w=1.0):
    v = {"video": path, "ss": ss, "weight": w}
    if ln: v["len"] = ln
    return v


def C(card, w=1.0): return {"card": card, "weight": w}
def stat(label, big, lines, accent="orange"): return C({"type": "stat", "label": label, "big": big, "lines": lines, "accent": accent})
def lst(title, items, accent="orange"): return C({"type": "list", "title": title, "items": items, "accent": accent})
def N(nid, visuals, **kw): return dict(narr=nid, visuals=visuals, pad=kw.pop("pad", P), **kw)
def K(words, at=0.4, step=0.4, hold=2.8, size=120): return {"words": words, "at": at, "step": step, "hold": hold, "size": size}


def section(tag, title, chapter, accent="orange"):
    return {"label": tag.lower(), "dur": 1.5, "visuals": [C({"type": "section", "tag": tag, "title": title, "accent": accent})],
            "chapter": chapter, "pad": [0.5, 0.8]}


B = [
    # ---------------- cold open
    N("n00", [V(LST, 0, 6.6)], chapter="Cold open: a 36-year high",
      headline=["McALLEN METRO", "More homes for sale than at any point in 36 years"],
      credit="Source: Texas A&M Real Estate Center MLS data via RGV Business Journal, Jul 2026"),
    N("n01", [V(LST, 6.0, 6.0)], kinetic=K(["997", "→", "3,432"], at=1.2, size=140)),
    N("n02", [V(CR, 6.5, 7.5)], credit="Data: Freddie Mac via FRED"),
    N("n03", [V(EDI, 0, 10.8)], kinetic=K(["BUYER'S", "MARKET", "OR", "WARNING SIGN?"], at=4.2, step=0.35, size=110)),
    {"label": "on the record", "dur": 6.0, "visuals": [V(f"{E4}/headlines.mp4", 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "RGV HOUSING HEADING INTO 2027",
                                                "sub": "Buyer's market or warning sign?"})], "pad": [0.5, 0.8]},
    # ---------------- part 1: the glut
    section("PART 1", "THE GLUT", "Part 1: The glut"),
    N("n04", [V(CL, 0, 8.4)]),
    N("n05", [V(MOI, 2.0, 6.0)], kinetic=dict(K(["6 MONTHS", "=", "BALANCED"], at=0.3, step=0.45, size=120), x=1180)),
    N("n06", [stat("McAllen metro · May 2021", "~2 MONTHS", ["about 757 active listings", "multiple offers, waived inspections"], "blue"), V(CL, 4.5, 3.9)],
      credit=RGVBJ + ", Jul 7, 2026"),
    N("n07", [V(EDI, 10, 6.0)]),
    N("n08", [V(MOI, 7.0, 5.0)], credit=RGVBJ + ", Sep 25, 2026"),
    N("n09", [V(MAP, 4.5, 9.5)], credit="Quote: Emiliano Zapata, Capital Insiders, via RGV Business Journal, Jan 2026"),
    # ---------------- part 2: prices
    section("PART 2", "PRICES ARE SLIPPING", "Part 2: Prices are slipping", "blue"),
    N("n10", [V(EDI, 16, 4.7)], kinetic=K(["CRASH?", "NO.", "SLIPPING."], at=0.2, step=0.5, size=130)),
    N("n11", [V(PRC, 0, 12.0)]),
    N("n12", [stat("Median sale price · McAllen metro", "~$245K", ["roughly flat since 2023", "through Aug 2026"], "blue"), V(MAP, 0, 4)],
      credit=RGVBJ + ", Sep 25, 2026"),
    N("n13", [stat("Typical days on market · McAllen", "78 DAYS", ["October 2026", "48 days in October 2021"]), V(CL, 3, 6)], credit="Days on market: Realtor.com via FRED"),
    N("n14", [stat("McAllen listings with a price cut", "1 IN 6", ["540 of 3,432 listings", "October 2026"]), V(LST, 8, 4)], credit="Price cuts: Realtor.com via FRED"),
    N("n15", [lst("WHAT BUILDERS ARE OFFERING", ["Rate buy-downs", "Appliance packages", "Extended warranties",
                                                 "Some new homes priced below resale"], "teal"), V(EDI, 4, 5)],
      credit="Brian Reed, Ryan & Brian Real Estate Team, via RGV Business Journal, Feb 2026"),
    N("n16", [stat("Gumwood Ave, McAllen · new 3-bed", "$275K → $259K", ["listed February 2026", "asking price by August"], "blue"),
              V(MAP, 0, 6)], credit=RGVBJ + ", Sep 25, 2026"),
    # ---------------- part 3: the rate whiplash
    section("PART 3", "THE RATE WHIPLASH", "Part 3: The rate whiplash"),
    N("n17", [V(CR, 1.5, 8.2)]),
    N("n18", [stat("McAllen metro closings · January 2026", "+21%", ["vs. January 2025", "rates had dipped near 6%"], "teal"), V(EDI, 0, 5)],
      credit=RGVBJ + ", Feb 25, 2026"),
    N("n19", [V(CR, 7.0, 7.0)], credit="Sources: Freddie Mac; NAHB Eye on Housing, Nov 2026"),
    N("n20", [V(PAY, 0, 6.5), stat("RGV News calculation", "$1,373 → $1,570", ["$255,000 home · 10% down · 30-yr fixed",
                                                                            "principal and interest only"])]),
    N("n21", [V(CR, 9.5, 4.5)], kinetic=K(["+$197", "A MONTH"], at=0.2, step=0.4, hold=3.2, size=140)),
    N("n22", [stat("McAllen metro sales · September 2026", "-8%", ["333 sales vs. 361 a year earlier", "Texas A&M Real Estate Center data"], "blue"),
              V(MAP, 14, 5)], credit=RGVBJ + ", Oct 22, 2026"),
    # ---------------- part 4: the affordability gap
    section("PART 4", "THE AFFORDABILITY GAP", "Part 4: The affordability gap", "teal"),
    N("n23", [V(GRW, 0, 5.5), V(DOC, 0, 6)]),
    N("n24", [V(GRW, 5.5, 6.5)]),
    N("n25", [stat("Median household income · Hidalgo County", "$55,829", ["30% for housing ≈ $1,396 a month",
                                                                       "U.S. Census Bureau SAIPE, 2024"], "teal"), V(PAY, 6.0, 6.0)]),
    N("n26", [C({"type": "quote", "quote": "The payment is $2,800 a month for an almost above entry-level house.",
                 "by": "Craig Grove, GRT Realty, Brownsville", "source": "to the RGV Business Journal, February 2026"}), V(EDI, 6, 5)]),
    N("n27", [V(DOC, 9.5, 6.5), V(EDI, 18, 4)], credit="Myssie Cardenas-Barajas via RGV Business Journal, Jul 7, 2026"),
    N("n28", [lst("THE PRICE GAP", ["Demand: $150K to $250K", "Lots: $50K to $70K each", "A $200K new house: \"nearly impossible\""]),
              V(MAP, 2, 6)], credit="Sources: Myssie Cardenas-Barajas; Emiliano Zapata; via RGV Business Journal"),
    # ---------------- part 5: two markets
    section("PART 5", "TWO DIFFERENT MARKETS", "Part 5: Two different markets", "blue"),
    N("n29", [V(MAP, 15, 6.5), V(MOI, 8, 4)], credit=RGVBJ + ", Sep 25, 2026 (August data)"),
    N("n30", [V(PRC, 8.6, 3.4, w=0.4), stat("Median listing · Brownsville-Harlingen", "$297K", ["October 2026", "peak: $321K in October 2022"], "teal", ) | {"weight": 0.6}],
      credit="Brownsville-Harlingen listings: Realtor.com via FRED"),
    N("n31", [stat("Brownsville-Harlingen home sales", "-17%", ["through August 2026", "back to 2019 levels"], "blue"), V(SB, 0, 5)],
      credit=RGVBJ + ", Sep 25, 2026"),
    # ---------------- part 6: what to do
    section("PART 6", "WHAT TO DO BEFORE 2027", "Part 6: What to do before 2027"),
    N("n32", [V(LST, 0, 3.4)], kinetic=K(["BEFORE", "2027"], at=0.2, step=0.35, hold=2.4, size=150)),
    N("n33", [lst("IF YOU'RE BUYING", ["~9 months of inventory = leverage", "Ask for price cuts", "Ask for closing costs",
                                        "Ask for rate buy-downs"], "teal"), V(LST, 8, 4)]),
    N("n34", [lst("IF YOU'RE BUILDING", ["Target $150K to $250K", "Townhomes and smaller homes", "Build-to-rent"], "blue"), V(EDI, 14, 5)]),
    N("n35", [lst("IF YOU'RE LENDING", ["Banks are tightening construction loans", "Private lenders ~13% vs. banks ~8%",
                                         "A home that sits 9 months gets expensive"]), V(MAP, 6, 7)],
      credit="Emiliano Zapata, Capital Insiders, via RGV Business Journal, Jan 2026"),
    N("n36", [lst("OUR WATCH LIST", ["Weekly mortgage rates (Freddie Mac)", "Monthly McAllen inventory",
                                      "Brownsville sales vs. port and SpaceX payrolls"], "teal"), V(CR, 9.5, 4.5)]),
    N("n37", [V(LST, 4, 8.0)]),
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
