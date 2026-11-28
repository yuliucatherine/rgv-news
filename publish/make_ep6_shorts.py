"""Writes Metricool payloads for the five Episode 6 Shorts (s50-s54). Usage: python3 publish/make_ep6_shorts.py"""
import json
LINK = "https://www.youtube.com/watch?v=VAxBJ711ChE"
R2 = "https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev"; DAY = "2026-11-28"
TAIL = "Narration is AI-generated. Not financial advice."
MUS = 'Music: "{}" by Kevin MacLeod (incompetech.com), CC BY 4.0.'
S = [
 ("s50_sh4_10x", "2026-12-02T22:20:00", "10x the traffic on the only road to Starbase",
  "State Highway 4, the only road from Brownsville to Starbase, went from about 645 vehicles a day in 2019 to more than 6,700 in 2024. TxDOT projects about 19,700 a day by 2050. Texas committed $192 million to make it four lanes, with bids scheduled before August 2027.",
  "Sources: TxDOT traffic counts via RGV Business Journal (Dec 16, 2025 and Aug 26, 2026). 3D flyovers over USGS imagery.", "Rising Tide",
  ["Starbase Texas", "State Highway 4", "SpaceX", "TxDOT", "Brownsville", "Texas"], "#Starbase #SpaceX #TxDOT #Brownsville #Texas"),
 ("s51_spi_one_bridge", "2026-12-03T10:20:00", "South Padre Island has one bridge. A second could cost $1B",
  "South Padre Island has one road in and out, the Queen Isabella Causeway. TxDOT has narrowed a second causeway to two routes, about 8 miles across the Laguna Madre, and estimates it could cost up to $1 billion and take 5 to 6 years to build. There's no construction start date yet.",
  "Sources: TxDOT; KRGV (Nov 2025). 3D flyovers over USGS imagery. Photos: G. Lamar, CC BY 2.0; Shannon247, public domain.", "Inspired",
  ["South Padre Island", "second causeway", "Queen Isabella Causeway", "TxDOT", "Port Isabel", "Texas"], "#SouthPadreIsland #TxDOT #RioGrandeValley #RealEstate #Texas"),
 ("s52_donna_100_trucks", "2026-12-03T14:20:00", "100 trucks an hour are coming to the Donna bridge",
  "A $62 million project at the Donna bridge would put U.S. and Mexican inspectors in one facility with six dedicated lanes, handling up to 100 trucks an hour once finished before the end of 2028. But the toll-free, 13-mile International Bridge Trade Corridor behind it has hit a funding snag.",
  "Source: RGV Business Journal (Feb 26, 2026). 3D flyover and aerials over USGS imagery; map: U.S. Census TIGER. Photo: Congressman Ruben Hinojosa, public domain.", "Industrial Cinematic",
  ["Donna bridge", "trade corridor", "trucks", "Hidalgo County", "Pharr", "Texas"], "#Donna #Pharr #Trade #RioGrandeValley #Texas"),
 ("s53_three_corridors", "2026-12-03T18:20:00", "The Valley has 3 truck corridors, and none connect",
  "Thousands of tractor-trailers cross northbound at the Pharr International Bridge every day. The Port of Harlingen's director says the Valley has three heavyweight truck corridors, serving Harlingen, Brownsville and Hidalgo County, and none of them connect to each other.",
  "Source: RGV Business Journal (Feb 26, 2026). 3D flyovers and aerials over USGS imagery.", "Deliberate Thought",
  ["trucking", "Port of Harlingen", "Port of Brownsville", "Pharr", "Rio Grande Valley", "Texas"], "#Trucking #Freight #RioGrandeValley #Pharr #Texas"),
 ("s54_i69_gap", "2026-12-03T22:20:00", "The Valley's interstates still don't connect to the rest of America",
  "The Valley has I-2, I-69 Central and I-69 East, but they still don't connect to the national interstate system. I-69E signs end at Raymondville. TxDOT has about $400 million in contracts on U.S. 77 through Kenedy County, less than half of the miles still needed, and the I-69 Connector's environmental decision is due in 2027.",
  "Sources: TxDOT; The Monitor (Jun 11, 2025); Rio Grande Guardian (Feb 2026). Maps: U.S. Census TIGER. Aerials: USGS. Photo: formulanone, CC BY-SA 2.0.", "Unanswered Questions",
  ["I-69", "interstate", "Rio Grande Valley", "TxDOT", "Harlingen", "Texas"], "#I69 #TxDOT #RioGrandeValley #Harlingen #Texas"),
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
json.dump(out, open("publish/ep6_shorts.json", "w"), indent=1, ensure_ascii=False)
print(len(out), "shorts", max(len(o["social"]["text"]) for o in out), "max chars")
