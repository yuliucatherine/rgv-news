"""Builds timeline.json for Episode 3 (Port of Brownsville boom).
Run: python3 episodes/2026-12-port-boom/make_timeline.py
3D shots are referenced as their 60 fps smoothed versions (_s): channel x2.5 (25 s), bars_jobs x2.5 (20 s),
bars_depth x1.6 (12.8 s), bars_cargo x1.35 (9.45 s; 7 s render)."""
import json, os

E3, E2, E1 = "demo/ep3", "demo/ep2", "demo/ep1"
P = [0.15, 0.3]   # tight: no dead air between paragraphs (owner rule, Nov 18)
CH, PORT, MAP = f"{E3}/v_channel_s.mp4", f"{E1}/v_port_s.mp4", f"{E3}/map_port.mp4"
EDI, SB, DOC = f"{E2}/v_edinburg_s.mp4", f"{E1}/v_starbase_s.mp4", f"{E3}/doc_ercot.mp4"
RGVBJ_JUN = "Source: RGV Business Journal, Jun 26, 2026"
NXT = "Sources: NextDecade Q3 2026 business update; SEC 10-Q"


def V(path, ss=0, ln=None, w=1.0):
    v = {"video": path, "ss": ss, "weight": w}
    if ln: v["len"] = ln
    return v


def C(card, w=1.0): return {"card": card, "weight": w}


def N(nid, visuals, **kw): return dict(narr=nid, visuals=visuals, pad=kw.pop("pad", P), **kw)


def section(tag, title, chapter, accent="orange"):
    return {"label": tag.lower(), "dur": 1.5, "visuals": [C({"type": "section", "tag": tag, "title": title, "accent": accent})],
            "chapter": chapter, "pad": [0.5, 0.8]}


B = [
    # ---------------- cold open
    N("n00", [V(PORT, 0, 10.3)], chapter="Cold open: Highway 48",
      headline=["HIGHWAY 48", "6,000+ workers building Rio Grande LNG, around the clock"], credit=RGVBJ_JUN),
    N("n01", [V(MAP, 6, 10.7)], credit="Source: RGV Business Journal, Aug 5, 2026 ($30B developer valuation)"),
    N("n02", [V(CH, 0, 7.2), C({"type": "stat", "label": "Why the work never stops", "big": "LNG DEMAND",
              "lines": ["natural gas, chilled into a liquid to ship overseas", "Middle East fighting cut world supply in 2026"],
              "accent": "blue"})],
      credit="Source: RGV Business Journal, Apr 7, 2026"),
    N("n03", [C({"type": "timeline", "title": "RIO GRANDE LNG",
                 "points": [["Q2 2027", "first LNG from Train 1 expected"], ["SEP 2026", "Army Corps OK for Train 6"],
                            ["NEXT", "Trains 7-8: FERC filing planned"]]}), V(MAP, 12, 6)], credit=NXT),
    N("n04", [V(MAP, 0, 6), V(PORT, 10, 6)],
      kinetic={"words": ["HOW", "MANY", "JOBS", "STAY?"], "at": 4.6, "step": 0.35, "hold": 3.0, "size": 120}),
    {"label": "on the record", "dur": 6.0, "visuals": [V(f"{E3}/headlines.mp4", 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "THE PORT OF BROWNSVILLE BOOM",
                                                "sub": "What stays after 2027?"})], "pad": [0.5, 0.8]},
    # ---------------- part 1
    section("PART 1", "WHAT'S BEING BUILT", "Part 1: What's being built", "blue"),
    N("n05", [V(CH, 7, 10.9)], credit=RGVBJ_JUN),
    N("n06", [C({"type": "stat", "label": "Ship channel deepening, 2026", "big": "$539M",
                 "lines": ["about $400M paid by NextDecade", "the company building Rio Grande LNG"]}), V(MAP, 2, 6)],
      credit=RGVBJ_JUN),
    N("n07", [V(MAP, 13, 4.5), C({"type": "stat", "label": "Rio Grande LNG lease from the port", "big": "984 ACRES",
                                  "lines": ["30-year term", "one project, one tenant"], "accent": "teal"})],
      credit=RGVBJ_JUN),
    N("n08", [V(f"{E3}/v_bars_cargo_s.mp4", 0, 9.4)]),
    N("n09", [V(f"{E3}/v_bars_depth_s.mp4", 0, 12.6)]),
    N("n09b", [C({"type": "stat", "label": "Saronic Technologies shipyard", "big": "$3.2 BILLION",
                  "lines": ["autonomous ships, Port of Brownsville", "Gov. Abbott: about 10,000 jobs, eventually"]}),
               V(PORT, 8, 7)], credit="Sources: KRGV; Office of the Texas Governor"),
    N("n10", [V(PORT, 0, 6.5), V(MAP, 18, 6)],
      kinetic={"words": ["$30B+", "IN", "POTENTIAL", "PROJECTS"], "at": 0.6, "step": 0.35, "hold": 3.0, "size": 110},
      credit="Source: Port of Brownsville, State of the Port address, Jun 2026"),
    # ---------------- part 2
    section("PART 2", "THE CONSTRUCTION WAVE", "Part 2: The construction wave"),
    N("n11", [V(MAP, 8, 7), C({"type": "timeline", "title": "RIO GRANDE LNG: SPEED IT UP",
                                "points": [["APR 7, 2026", "asks FERC: more workers, 24/7"], ["APR 10, 2026", "FERC approves"],
                                           ["PEAK", "about 7,500 workers"]]})],
      kinetic={"words": ["7,500", "WORKERS", "AT PEAK"], "at": 1.0, "step": 0.4, "hold": 3.0, "size": 120},
      credit="Sources: RGV Business Journal, Apr 7, 2026; FERC via LNG Prime"),
    N("n12", [V(EDI, 0, 9.5)],
      kinetic={"words": ["SLEEP", "EAT", "PARK"], "at": 0.8, "step": 0.45, "hold": 2.6, "size": 120}),
    N("n13", [C({"type": "stat", "label": "Rio Grande LNG onsite workforce", "big": "~75% LOCAL",
                 "lines": ["Jul 2023 to Jun 2026", "people who already live in the Valley"], "accent": "teal"}),
              V(EDI, 9, 6)], credit="Source: NextDecade"),
    N("n14", [V(f"{E3}/v_bars_jobs_s.mp4", 0, 7.7)]),
    N("n15", [V(f"{E3}/v_bars_jobs_s.mp4", 7.7, 12.3)]),
    N("n16", [C({"type": "timeline", "title": "EXPANSION: THE WILD CARD",
                 "points": [["TRAIN 1", "first LNG expected Q2 2027"], ["TRAIN 6", "Army Corps OK, Sep 2026"],
                            ["TRAINS 7-8", "FERC filing planned"]], "accent": "teal"}), V(MAP, 12, 6)], credit=NXT),
    # ---------------- part 3
    section("PART 3", "WHAT LASTS", "Part 3: What lasts", "teal"),
    N("n17", [V(CH, 13.5, 11.6)]),
    N("n18", [V(PORT, 4, 11.2)],
      kinetic={"words": ["A PROJECTION,", "NOT A", "PAYROLL"], "at": 5.4, "step": 0.45, "hold": 3.5, "size": 110},
      credit="Source: KRGV; Office of the Texas Governor"),
    N("n19", [V(SB, 0, 10.6)], headline=["STARBASE", "3,400+ workers · about 4,000 more signaled for 2026"],
      credit="Source: RGV Business Journal, Aug 5, 2026, citing Cameron County"),
    N("n20", [C({"type": "stat", "label": "Cameron County estimate", "big": "21,400",
                 "lines": ["indirect jobs tied to SpaceX", "an estimate, worth checking"], "accent": "blue"}),
              V(SB, 12, 7)], credit="Source: RGV Business Journal, Aug 5, 2026, citing Cameron County"),
    # ---------------- part 4
    section("PART 4", "THE CONSTRAINTS", "Part 4: The constraints"),
    N("n21", [V(DOC, 0, 12.2)]),
    N("n22", [V(DOC, 12.2, 11.4)]),
    N("n23", [V(f"{E1}/map_rgv_clean_s.mp4", 0, 9.9)],
      kinetic={"words": ["POWER", "ROADS", "WATER"], "at": 0.4, "step": 0.45, "hold": 3.0, "size": 120}),
    # ---------------- part 5
    section("PART 5", "WHAT IT MEANS FOR BUILDERS", "Part 5: What it means for builders", "blue"),
    N("n24", [V(EDI, 12, 4.7)],
      kinetic={"words": ["BUILD", "BUY", "LEND"], "at": 0.2, "step": 0.35, "hold": 2.6, "size": 120}),
    N("n25", [V(EDI, 0, 4.5), C({"type": "list", "title": "TWO KINDS OF DEMAND",
              "items": ["Temporary: construction crews, short-term rentals, RV parks, hotels",
                        "Permanent: workers who buy homes and enroll kids in school"]})]),
    N("n26", [C({"type": "list", "title": "ASK BEFORE YOU BUILD NEAR THE PORT",
                 "items": ["Is demand tied to a construction schedule or a payroll?", "When does that schedule end?",
                           "Which permanent employers are hiring today?"], "accent": "teal"}), V(MAP, 14, 5.5)]),
    N("n27", [V(CH, 3, 7), C({"type": "list", "title": "THE OPPORTUNITY SIDE",
              "items": ["Workforce housing near Highway 48", "Industrial and logistics space on the deeper channel",
                        "Services every new payroll needs"], "accent": "blue"})]),
    N("n28", [C({"type": "list", "title": "OUR WATCH LIST",
                 "items": ["Federal decisions on more LNG trains", "Saronic's actual hiring",
                           "ERCOT grid upgrades for the Valley"]}), V(MAP, 6, 6)]),
    N("n29", [V(PORT, 4, 9.4)]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays and maps carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any(("v_" in v.get("video", "") or "map_" in v.get("video", "")) for v in b["visuals"]):
        b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep3/episode3.mp4", "audio_dir": "episodes/2026-12-port-boom/audio",
      "narration_json": "episodes/2026-12-port-boom/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Industrial_Cinematic.mp3", "chapter": 0, "offset": 20},
          {"track": "assets/music/Rising_Tide.mp3", "chapter": 2, "offset": 30},
          {"track": "assets/music/I_Can_Feel_it_Coming.mp3", "chapter": 4, "offset": 20},
          {"track": "assets/music/Inspired.mp3", "chapter": 5, "offset": 60}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
