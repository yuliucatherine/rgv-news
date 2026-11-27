"""Writes Metricool payloads for the six Episode 5 Shorts (s38-s43): per Short, one YouTube post (no cover) and one
Facebook/Instagram/TikTok post with the cover. Usage: python3 publish/make_ep5_shorts.py <youtube_url>"""
import json, sys
LINK = sys.argv[1]
R2 = "https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev"; DAY = "2026-11-27"
TAIL = "Narration is AI-generated. Not financial advice."
MUS = 'Music: "{}" by Kevin MacLeod (incompetech.com), CC BY 4.0.'
S = [
 ("s38_spacex_24b", "2026-11-28T10:20:00", "SpaceX's $24B Starbase data center: tax break denied",
  "SpaceX wants a $24 billion computing complex at Starbase, with its own natural gas power plant of about 748 MW, on 444 acres. On November 17, Cameron County commissioners voted 3-2 not to even schedule a public hearing on its tax break.",
  "Sources: RGV Business Journal; MyRGV; ValleyCentral; S&P Global (Nov 2026). 3D flyover over USGS imagery.", "Crusade - Heavy Industry",
  ["SpaceX", "Starbase Texas", "data center", "Cameron County", "tax abatement", "Texas"], "#SpaceX #Starbase #DataCenter #CameronCounty #Texas"),
 ("s40_texas_freeze", "2026-11-28T14:20:00", "Texas froze data center permits. $42B in Cameron County plans in limbo?",
  "In September, Governor Abbott told the state environmental agency to stop issuing data center permits until ERCOT finishes its audit, expected mid-December. Governor-elect Gina Hinojosa, who takes office January 19, has promised a moratorium on new approvals. About $42 billion in Cameron County plans are on the table.",
  "Sources: Office of the Texas Governor; Texas Tribune; Houston Chronicle; Gibson Dunn. Photos: Carol M. Highsmith, Public domain; Carl Lender, CC BY 2.0; Victorgrigas, CC BY-SA 3.0.", "Unanswered Questions",
  ["data centers", "Texas", "ERCOT", "Greg Abbott", "Gina Hinojosa", "Cameron County"], "#DataCenters #Texas #ERCOT #CameronCounty #RioGrandeValley"),
 ("s39_rio_hondo_4b", "2026-11-28T18:20:00", "A $4B AI campus near Rio Hondo with no local tax breaks",
  "Fluidstack broke ground in September on a $4 billion AI computing campus between Valley International Airport and the Port of Harlingen, near Rio Hondo. It isn't asking for local property tax breaks, plans 2,500+ construction jobs, and targets completion in mid-2028.",
  "Sources: KRGV; Construction Review Online (Sep 2026). Aerial: USGS. Photos: Derrick Coetzee, CC0; Carl Lender, CC BY 2.0.", "Deliberate Thought",
  ["Fluidstack", "AI data center", "Rio Hondo", "Harlingen", "Rio Grande Valley", "Texas"], "#AI #DataCenter #RioHondo #Harlingen #RioGrandeValley"),
 ("s42_harlingen_20m", "2026-11-28T22:20:00", "Harlingen tabled a data center deal. The county gets $20M",
  "Harlingen's commissioners tabled a deal to send a data center site's stormwater into a city canal after residents pushed back. The county issued the permit instead, and the mayor says $20 million in proposed infrastructure money will now go to the county.",
  "Source: KRGV (Sep 2026), statement by Mayor Norma Sepulveda. Aerial: USGS. Photos: RobertKixmiller, CC BY-SA 4.0.", "Deliberate Thought",
  ["Harlingen", "data center", "Cameron County", "infrastructure", "Rio Grande Valley", "Texas"], "#Harlingen #DataCenter #CameronCounty #RioGrandeValley #Texas"),
 ("s41_dec9_starbase", "2026-11-29T10:20:00", "SpaceX warns it could leave Cameron County. Next date: Dec 9",
  "After the county vote, SpaceX said fast-depreciating computer equipment could swing local tax rates year to year, and warned it could send future investment outside Cameron County. The city of Starbase holds its own hearing on a separate tax deal on December 9.",
  "Sources: RGV Business Journal; MyRGV (Nov 2026). 3D flyovers over USGS imagery.", "Industrial Cinematic",
  ["SpaceX", "Starbase Texas", "Cameron County", "data center", "tax abatement", "Texas"], "#SpaceX #Starbase #CameronCounty #DataCenter #Texas"),
 ("s43_water_proof", "2026-11-29T14:20:00", "Data centers vs. Valley water: Texas wants proof",
  "Three data centers planned in Cameron County all say they'll use closed-loop cooling or reclaimed water. After two years of worry about the Rio Grande, the state now requires them to report how much water they use.",
  "Sources: company statements; Office of the Texas Governor (Sep 2026). 3D flyovers over USGS imagery.", "Unanswered Questions",
  ["data centers", "water", "Rio Grande", "Cameron County", "Rio Grande Valley", "Texas"], "#Water #DataCenters #RioGrande #RioGrandeValley #Texas"),
]
out = []
for n, when, title, body, src, track, tags, hashtags in S:
    assert len(title) <= 100, title
    text = f"{body}\n\nWatch the full breakdown on YouTube: {LINK}\n\n{src} {MUS.format(track)} {TAIL}\n\n{hashtags}"
    base = {"autoPublish": True, "descendants": [], "draft": False, "firstCommentText": "", "hasNotReadNotes": False,
            "media": [f"{R2}/shorts/{DAY}/{n}.mp4"], "mediaAltText": [],
            "publicationDate": {"dateTime": when, "timezone": "America/Chicago"}, "shortener": False,
            "smartLinkData": {"ids": []}, "text": text}
    yt = dict(base, providers=[{"network": "youtube"}],
              youtubeData={"title": title, "type": "short", "privacy": "public", "tags": tags, "category": "NEWS_POLITICS",
                           "madeForKids": False, "isAiGeneratedContent": False})
    soc = dict(base, providers=[{"network": "facebook"}, {"network": "instagram"}, {"network": "tiktok"}],
               videoThumbnailUrl=f"{R2}/covers/{DAY}/{n}.jpg",
               facebookData={"type": "REEL", "title": title},
               instagramData={"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True},
               tiktokData={"privacyOption": "PUBLIC_TO_EVERYONE", "title": title, "isAigc": True})
    out.append({"name": n, "date": when + "-06:00", "youtube": yt, "social": soc})
json.dump(out, open("publish/ep5_shorts.json", "w"), indent=1, ensure_ascii=False)
print(len(out), "shorts", max(len(o["social"]["text"]) for o in out), "max chars")
