"""Builds timeline.json for Episode 2 (Valley water). Run: python3 episodes/2026-12-valley-water/make_timeline.py"""
import json, os

E2, E1 = "demo/ep2", "demo/ep1"
P = [0.15, 0.3]   # tight: no dead air between paragraphs (owner rule, Nov 18)


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
    N("n00", [V(f"{E1}/v_falcon_s.mp4", 0, 9)], chapter="Cold open: the reservoir",
      texts=[{"text": "FALCON RESERVOIR · OCT 2010: 100% FULL", "x": "(w-tw)/2", "y": 930, "size": 38, "font": "Bold",
              "box": "0x091020@0.6", "at": 0.6, "until": 8.0}]),
    N("n01", [V(f"{E2}/chart_falcon.mp4", 0, 13)]),
    N("n02", [V(f"{E2}/v_edinburg_s.mp4", 0, 8), V(f"{E1}/v_starbase_s.mp4", 8, 8)]),
    N("n03", [V(f"{E2}/map_canals.mp4", 12, 10)],
      kinetic={"words": ["WILL", "THERE", "BE", "ENOUGH?"], "at": 3.0, "step": 0.4, "hold": 3.0}),
    {"label": "on the record", "dur": 6.0, "visuals": [V(f"{E2}/headlines.mp4", 0, 6.0)], "pad": [0, 0]},
    {"label": "title", "dur": 2.5, "visuals": [C({"type": "title", "title": "WILL THE VALLEY HAVE ENOUGH WATER?",
                                                "sub": "What the Rio Grande means for builders and investors"})], "pad": [0.5, 0.8]},
    section("PART 1", "WHERE THE WATER COMES FROM", "Part 1: Where the water comes from", "blue"),
    N("n04", [V(f"{E2}/map_basin.mp4", 0, 13)]),
    N("n05", [V(f"{E1}/v_port_s.mp4", 2, 6), C({"type": "stat", "label": "Brownsville's water supply", "big": "~70%",
              "lines": ["comes from the Rio Grande", "about 21 million gallons a day"], "accent": "blue"})],
      credit="Source: Texas Tribune via KRGV, Aug 31, 2026"),
    N("n06", [V(f"{E2}/map_basin.mp4", 7, 6), C({"type": "timeline", "title": "THE 1944 WATER TREATY",
              "points": [["1944", "U.S.-Mexico treaty signed"], ["EVERY 5 YEARS", "Mexico owes 1.75M acre-feet"],
                         ["OCT 2025", "last cycle closes in deficit"]]})],
      credit="Sources: Office of the Texas Governor / TCEQ; Congressional Research Service"),
    N("n07", [C({"type": "stat", "label": "Mexico's commitment, early 2026", "big": "350,000",
                 "lines": ["acre-feet a year, minimum", "plus a plan to repay past-cycle debt"], "accent": "teal"}),
              {"image": "data/imagery/PIA25446.jpg", "weight": 1.0}],
      credit="Sources: U.S. State Dept. / USDA joint statement, Feb 2026 · Image: NASA/METI/AIST/Japan Space Systems, U.S./Japan ASTER Science Team"),
    N("n08", [C({"type": "stat", "label": "Year 1 of the new cycle (Oct 2026)", "big": "MINIMUM MET",
                 "lines": ["Still owed from the last cycle:", "about 830,000 to 860,000 acre-feet"], "accent": "teal"}),
              V(f"{E1}/v_falcon_s.mp4", 5, 7)],
      credit="Sources: Mexican government via Rio Times; Texas Politics; Sen. Cruz's office; Freshplaza"),
    N("n09", [V(f"{E2}/v_acrefoot_s.mp4", 0, 12.8)]),
    section("PART 2", "THE RESERVOIRS", "Part 2: The reservoirs", "teal"),
    N("n10", [V(f"{E2}/chart_both.mp4", 0, 9.8)]),
    N("n11", [V(f"{E2}/chart_both.mp4", 9.8, 11.2)]),
    N("n12", [V(f"{E2}/v_bars_reservoirs_s.mp4", 0, 13)]),
    section("PART 3", "WHO GETS CUT FIRST", "Part 3: Who gets cut first"),
    N("n13", [V(f"{E2}/doc_unmet.mp4", 0, 8.9)]),
    N("n14", [V(f"{E2}/doc_unmet.mp4", 8.9, 10.1)]),
    N("n15", [V(f"{E2}/v_bars_shortfall_s.mp4", 0, 18.4)]),
    N("n16", [C({"type": "stat", "label": "Santa Rosa, Texas · 2024", "big": "MILL CLOSED",
                 "lines": ["Texas' last sugar mill, after 50 years", "cited heat and a shortage of irrigation water"]}),
              V(f"{E2}/v_edinburg_s.mp4", 12, 8)],
      credit="Sources: KSAT, Mar 2024; Texas Workforce Commission; KRGV"),
    N("n17", [V(f"{E2}/map_canals.mp4", 0, 12)]),
    N("n18", [V(f"{E2}/map_canals.mp4", 12, 10)], credit="Source: KRGV, 2026"),
    N("n19", [V(f"{E2}/doc_push.mp4", 0, 20)]),
    section("PART 4", "WHAT IT MEANS FOR BUILDERS", "Part 4: What it means for builders"),
    N("n20", [V(f"{E2}/v_edinburg_s.mp4", 0, 8.4)],
      kinetic={"words": ["FARM", "WATER", "BECOMES", "CITY WATER"], "at": 0.6, "step": 0.4, "hold": 3.0, "size": 110}),
    N("n21", [V(f"{E2}/doc_convert.mp4", 0, 16.9)]),
    N("n22", [V(f"{E2}/chart_urban.mp4", 0, 11)]),
    N("n23", [V(f"{E2}/v_edinburg_s.mp4", 8, 7), C({"type": "list", "title": "WATER AND NEW PROJECTS",
              "items": ["Some cities: prove your own water supply first", "Others are rethinking their rules",
                        "Converted farm rights: about 2 for 1"]})]),
    N("n24", [C({"type": "timeline", "title": "MISSION, TEXAS",
                 "points": [["2024", "weighed a building pause"], ["MAR 2026", "paused new car washes"],
                            ["SPRING 2026", "repealed after lawsuit"]]}),
              V(f"{E2}/map_canals.mp4", 3, 8)],
      credit="Sources: MyRGV, Mar 2024; KRGV, Mar-Apr 2026"),
    N("n25", [V(f"{E2}/v_edinburg_s.mp4", 4, 13)],
      headline=["EDINBURG", "127+ subdivisions under construction · water supply goal: 2030"],
      credit="Source: RGV Business Journal, Apr 2026"),
    N("n26", [C({"type": "quote", "quote": "Water security is a top priority... we need to think ahead.",
                 "by": "Edinburg Mayor Omar Ochoa", "source": "to the RGV Business Journal, April 2026"}),
              C({"type": "list", "title": "EDINBURG'S WATER PLAN",
                 "items": ["Study: desalinating brackish groundwater", "Capture stormwater before it reaches the river",
                           "$33M wastewater plant expansion: 12.3 to 13.5 MGD"]})],
      credit="Source: RGV Business Journal, Apr 2026"),
    N("n27", [V(f"{E1}/v_port_s.mp4", 4, 12)],
      headline=["BROWNSVILLE", "SpaceX land deal funds a water reuse plant + treatment-plant expansion"],
      credit="Source: Texas Tribune via KRGV, Aug 31, 2026"),
    section("PART 5", "NEW WATER", "Part 5: New water", "blue"),
    N("n28", [V(f"{E2}/map_canals.mp4", 6, 5.8)],
      kinetic={"words": ["WHERE", "NEW", "WATER", "COMES FROM"], "at": 0.3, "step": 0.35, "hold": 2.2, "size": 110}),
    N("n29", [C({"type": "stat", "label": "Texas Proposition 4, Nov 2025 · about 70% yes", "big": "$20 BILLION",
                 "lines": ["up to $1 billion a year in sales tax", "for water projects, starting 2027"], "accent": "blue"}),
              V(f"{E2}/map_basin.mp4", 0, 7)],
      credit="Sources: Texas Secretary of State; The Texas Tribune; Texas 2036"),
    N("n30", [C({"type": "stat", "label": "Canal modernization, 12 irrigation districts", "big": "UP TO $164M",
                 "lines": ["open canals into pipelines", "saves up to 44,000 acre-feet a year"], "accent": "teal"}),
              V(f"{E2}/map_canals.mp4", 0, 9)],
      credit="Sources: NADBank, Aug 2026; TWDB, Sep 2026; KRGV"),
    N("n31", [V(f"{E2}/v_spi_s.mp4", 0, 22.7)],
      credit="Sources: KRGV; Texas Border Business; MyRGV, Aug 2026", credit_y=1000),
    section("PART 6", "WHAT TO WATCH", "Part 6: What to watch"),
    N("n32", [V(f"{E2}/chart_falcon.mp4", 7, 6)]),
    N("n33", [C({"type": "list", "title": "RISKS TO WATCH", "items": ["Reservoir levels and Mexico's deliveries",
                 "City water-rights rules for new projects", "The price of new water (desalination, reuse)",
                 "Moratorium talk during droughts"]}), V(f"{E2}/v_bars_reservoirs_s.mp4", 4, 8)]),
    N("n34", [C({"type": "list", "title": "ASK BEFORE YOU BUILD", "items": ["Who supplies water to this site?",
                 "Must the project bring its own water rights? At what cost?", "What's the supplier's drought plan?"],
                 "accent": "teal"}), V(f"{E2}/v_edinburg_s.mp4", 14, 8)]),
    N("n35", [V(f"{E2}/v_edinburg_s.mp4", 6, 9), C({"type": "list", "title": "THE OPPORTUNITY SIDE",
              "items": ["Projects with their own water may move faster", "Know the rules: spot overlooked land",
                        "Avoid deals that look cheap until the water bill"], "accent": "blue"})]),
    N("n36", [V(f"{E2}/map_canals.mp4", 10, 12)]),
    N("n37", [V(f"{E1}/v_falcon_s.mp4", 0, 12.6)]),
    {"label": "end", "dur": 3, "visuals": [C({"type": "title", "title": "RGV NEWS",
                                              "sub": "Not financial advice · Sources in the description"})], "pad": [0.5, 0.8]},
]

for b in B:   # 3D overlays already carry their own credit line at the bottom: stack block credits above them
    if b.get("credit") and any("v_" in v.get("video", "") for v in b["visuals"]): b.setdefault("credit_y", 1000)

tl = {"fps": 60, "trim_narration": True, "out": "demo/ep2/episode2.mp4", "audio_dir": "episodes/2026-12-valley-water/audio",
      "narration_json": "episodes/2026-12-valley-water/narration.json",
      "music": {"level_lufs": -27, "segments": [
          {"track": "assets/music/Deliberate_Thought.mp3", "chapter": 0, "offset": 20},
          {"track": "assets/music/Unanswered_Questions.mp3", "chapter": 3, "offset": 10},
          {"track": "assets/music/Deliberate_Thought.mp3", "chapter": 5, "offset": 80}]},
      "blocks": B}
json.dump(tl, open(os.path.join(os.path.dirname(__file__), "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(len(B), "blocks")
