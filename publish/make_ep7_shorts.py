"""Writes Metricool payloads for the six Episode 7 Shorts (s44-s49): per Short, one YouTube post (no cover) and one
Facebook/Instagram/TikTok post with the cover. Usage: python3 publish/make_ep7_shorts.py <youtube_url>"""
import json, sys
LINK = sys.argv[1]
R2 = "https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev"; DAY = "2026-11-28"
TAIL = "Narration is AI-generated. Not financial advice."
MUS = 'Music: "{}" by Kevin MacLeod (incompetech.com), CC BY 4.0.'
S = [
 ("s44_41b_700_jobs", "2026-11-29T22:20:00", "$41B in projects, 700 jobs lost: is the Rio Grande Valley boom real?",
  "Cameron County counts about $41.1 billion in just four projects; Rio Grande LNG alone is about $31.8 billion by the county's figures. Yet the Dallas Fed says Valley employment fell at an annualized 0.6% in the third quarter, roughly 700 jobs, while Texas and the U.S. still grew.",
  "Sources: Cameron County via RGV Business Journal (Oct 3, 2026); Federal Reserve Bank of Dallas (Q3 2026). 3D flyovers over USGS imagery. Photo: Anthony Acosta, CC BY-SA 4.0.", "Crusade - Heavy Industry",
  ["Rio Grande Valley", "jobs", "Cameron County", "Rio Grande LNG", "Brownsville", "Texas"], "#RioGrandeValley #Jobs #Brownsville #RioGrandeLNG #Texas"),
 ("s47_trucking_bankruptcies", "2026-12-01T18:20:00", "2 Valley trucking companies file bankruptcy as filings double",
  "Xoco Transport of Hidalgo and American Petroleum Carriers of McAllen filed for Chapter 11 protection in recent weeks, and three more carriers filed in Laredo. Court records show steep revenue drops and heavy truck debt. Valley business bankruptcies doubled last year, from 62 to 127.",
  "Sources: RGV Business Journal (Nov 23 and Mar 7, 2026). 3D flyovers over USGS imagery. Photo: formulanone, CC BY-SA 2.0.", "I Can Feel it Coming",
  ["trucking", "bankruptcy", "McAllen", "Hidalgo County", "Rio Grande Valley", "Texas"], "#Trucking #Bankruptcy #McAllen #RioGrandeValley #Texas"),
 ("s45_jobless_rate_catch", "2026-12-01T22:20:00", "Brownsville's jobless rate fell to 6%. Here's the catch",
  "Unemployment fell to 6.0% in Brownsville and 5.8% in McAllen in September, against 4.4% statewide. But the Dallas Fed notes part of that drop comes from a shrinking labor force: Brownsville's is down about 2% from a year ago, and its employment shrank at an annualized 2.8% last quarter.",
  "Source: Federal Reserve Bank of Dallas, Rio Grande Valley Economic Indicators (Q3 2026). Aerials: USGS. Photos: Billy D. Wagner, CC BY-SA 4.0; Mig Esc, CC BY 3.0.", "Unanswered Questions",
  ["Brownsville", "unemployment", "labor force", "Dallas Fed", "Rio Grande Valley", "Texas"], "#Brownsville #Jobs #Unemployment #RioGrandeValley #Texas"),
 ("s46_mcallen_vs_brownsville", "2026-12-02T10:20:00", "McAllen added 4,500 jobs. Brownsville lost 300",
  "Over the year through October, the McAllen metro added about 4,500 jobs, mostly in health care and education, to 311,800. The Brownsville metro, home of the LNG and SpaceX boom, lost about 300. Valley job growth went from +1.4% annualized in the first quarter to -0.6% in the third.",
  "Sources: Texas Workforce Commission via RGV Business Journal (Nov 20, 2026); Federal Reserve Bank of Dallas. 3D flyover and aerials over USGS imagery. Photo: Billy D. Wagner, CC BY-SA 4.0.", "Deliberate Thought",
  ["McAllen", "Brownsville", "jobs", "Texas Workforce Commission", "Rio Grande Valley", "Texas"], "#McAllen #Brownsville #Jobs #RioGrandeValley #Texas"),
 ("s48_output_vs_jobs", "2026-12-02T14:20:00", "Valley economy grew 2.6%, jobs just 0.2%: why the gap?",
  "The Rio Grande Valley's economy grew about 2.6% in 2025, but jobs grew just 0.2%. Dallas Fed economist Luis Torres says weak hiring reflects the supply of workers more than a weak economy: labor force growth is flat or negative, and wage growth is still solid.",
  "Sources: RGV Business Journal (Feb 15 and Nov 18, 2026), citing the Federal Reserve Bank of Dallas. 3D flyover and aerials over USGS imagery. Photo: Alex Garrido, CC BY 3.0.", "Dreamer",
  ["Rio Grande Valley economy", "jobs", "Dallas Fed", "labor force", "McAllen", "Texas"], "#RioGrandeValley #Economy #Jobs #DallasFed #Texas"),
 ("s49_lowest_wages", "2026-12-02T18:20:00", "Lowest pay in Texas: about $36K a year, despite billions",
  "In 2025, the median annual wage in the Hidalgo and Starr counties workforce area was $35,971, the lowest in Texas. Cameron County was second-lowest at $36,942; statewide it was $48,621. Rio Grande LNG expects about 700 permanent jobs, and Saronic says up to 10,000 over a decade.",
  "Sources: Texas Workforce Commission report via RGV Business Journal (Aug 2, 2026); FERC; Defense News and USNI News (Jul 2026). Chart by RGV News. Aerial: USGS. Photo: Goose Green Photography, CC0.", "Industrial Cinematic",
  ["wages", "Hidalgo County", "Cameron County", "Rio Grande Valley", "Saronic", "Texas"], "#Wages #RioGrandeValley #Edinburg #Brownsville #Texas"),
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
json.dump(out, open("publish/ep7_shorts.json", "w"), indent=1, ensure_ascii=False)
print(len(out), "shorts", max(len(o["social"]["text"]) for o in out), "max chars")
