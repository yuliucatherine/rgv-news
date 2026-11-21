"""Writes Metricool payloads for the nine Episode 4 Shorts (s29-s37): per Short, one YouTube post (no cover, avoids
YouTube's thumbnail warning) and one Facebook/Instagram/TikTok post with the cover. Usage: python3 make_ep4_shorts.py <youtube_url>"""
import json, sys
LINK = sys.argv[1]
R2 = "https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev"
TAIL = "Narration is AI-generated. Not financial advice."
S = [
 ("s29_36_year_high", "2026-11-25T18:20:00", "McAllen has the most homes for sale in 36 years",
  "There are more homes for sale in the McAllen metro than at any point in 36 years: about 3,432 listings in October, up from 997 in the fall of 2021. And mortgage rates climbed back above 7% this fall.",
  "Sources: Texas A&M Real Estate Center via RGV Business Journal; Realtor.com via FRED; Freddie Mac. Photo: Rick Obst, CC BY 4.0. Aerial: USGS.",
  ["McAllen housing market", "homes for sale", "Rio Grande Valley", "real estate", "mortgage rates", "Texas"], "#McAllen #RealEstate #HousingMarket #RioGrandeValley #Texas"),
 ("s30_nine_months", "2026-11-25T22:20:00", "McAllen went from 2 to 9 months of housing inventory",
  "Months of inventory is how long it would take to sell every listed home at today's pace. Six is balanced. In May 2021 the McAllen metro had about 2 months. By August 2026 it had nearly 9, firmly a buyer's market.",
  "Sources: RGV Business Journal (Jul 7 and Sep 25, 2026). Aerial: USGS. Photo: Goose Green Photography, CC0.",
  ["months of inventory", "buyer's market", "McAllen", "Rio Grande Valley", "real estate", "Texas"], "#BuyersMarket #McAllen #RealEstate #RioGrandeValley #Texas"),
 ("s31_prices_slipping", "2026-11-26T10:20:00", "Are RGV home prices crashing? Not quite",
  "Prices aren't crashing; they're slipping. McAllen's median listing price peaked at $280K in October 2023 and was $255K this October, about 9% lower. Homes now sit about 78 days, and 1 in 6 listings had a price cut.",
  "Sources: Realtor.com via FRED; RGV Business Journal. Photos: Anthony Acosta, CC BY-SA 4.0; Mig Esc, CC BY 3.0.",
  ["home prices", "McAllen", "price cuts", "Rio Grande Valley", "real estate", "Texas"], "#HomePrices #McAllen #RealEstate #RioGrandeValley #Texas"),
 ("s32_builder_deals", "2026-11-26T14:20:00", "Some new McAllen homes now cost less than resales",
  "Builders are adding rate buy-downs, appliance packages and warranties, and some new homes are priced below comparable resales. One new 3-bed on Gumwood Ave in McAllen went from $275K in February to $259K by August.",
  "Sources: RGV Business Journal (Feb 25 and Sep 25, 2026). Photo: RobertKixmiller, CC BY-SA 4.0.",
  ["new construction", "homebuilders", "rate buy-down", "McAllen", "real estate", "Texas"], "#NewConstruction #Homebuilders #McAllen #RealEstate #Texas"),
 ("s33_rate_whiplash", "2026-11-26T18:20:00", "Mortgage rates added $197 a month since February",
  "On a $255,000 home with 10% down, principal and interest at February's 5.98% rate is about $1,373 a month. At today's rate it's about $1,570: roughly $197 more every month, before taxes and insurance.",
  "Sources: Freddie Mac via FRED; RGV Business Journal; RGV News calculation (principal and interest only).",
  ["mortgage rates", "monthly payment", "homebuyers", "McAllen", "real estate", "Texas"], "#MortgageRates #Homebuying #McAllen #RealEstate #Texas"),
 ("s34_income_gap", "2026-11-26T22:20:00", "McAllen home prices +75%, incomes +63%",
  "Over the past decade, median home prices in the McAllen metro rose 75% while median household income rose 63%. Hidalgo County's median household earns about $55,800 a year; 30% of that is about $1,400 a month.",
  "Sources: RGV Business Journal (Jul 7, 2026); U.S. Census Bureau SAIPE. Photo: Mig Esc, CC BY 3.0.",
  ["affordability", "home prices", "incomes", "Hidalgo County", "real estate", "Texas"], "#Affordability #HousingMarket #McAllen #RioGrandeValley #Texas"),
 ("s35_price_gap", "2026-11-27T10:20:00", "The Valley's $150K-$250K housing gap",
  "Realtors say real demand in the Valley is between $150K and $250K. With lots now $50K to $70K each, builders say a new $200K house is nearly impossible to pencil out. And some owners are selling because of property taxes.",
  "Sources: RGV Business Journal interviews (Jan, Feb and Jul 2026). Aerial: USGS.",
  ["affordable housing", "build-to-rent", "homebuilders", "Rio Grande Valley", "real estate", "Texas"], "#AffordableHousing #Homebuilders #RioGrandeValley #RealEstate #Texas"),
 ("s36_two_markets", "2026-11-27T14:20:00", "Brownsville home sales down 17% despite new jobs",
  "Brownsville-Harlingen has about 1,500 listings and roughly 6.7 months of inventory, close to balanced. The median listing was $297K in October. But home sales fell 17% through August, back to 2019 levels, despite SpaceX and LNG hiring nearby.",
  "Sources: RGV Business Journal (Sep 25, 2026); Realtor.com via FRED. Photo: RobertKixmiller, CC BY-SA 4.0. Aerial: USGS.",
  ["Brownsville", "Harlingen", "home sales", "SpaceX", "real estate", "Texas"], "#Brownsville #Harlingen #RealEstate #RioGrandeValley #Texas"),
 ("s37_before_2027", "2026-11-27T18:20:00", "Buying, building or lending in the Valley before 2027?",
  "Buying: 9 months of inventory means leverage on price cuts, closing costs and rate buy-downs. Building: townhomes, smaller homes and build-to-rent can reach $150K-$250K. Lending: watch carry costs; some builders pay private lenders about 13% vs about 8% at banks.",
  "Source: RGV Business Journal (lender interview, Jan 2026). Photos: Rick Obst, CC BY 4.0; Goose Green Photography, CC0. Aerial: USGS.",
  ["real estate investing", "homebuilders", "construction loans", "Rio Grande Valley", "McAllen", "Texas"], "#RealEstateInvesting #Homebuilders #RioGrandeValley #McAllen #Texas"),
]
out = []
for n, when, title, body, src, tags, hashtags in S:
    text = f"{body}\n\nWatch the full breakdown on YouTube: {LINK}\n\n{src} {TAIL}\n\n{hashtags}"
    base = {"autoPublish": True, "descendants": [], "draft": False, "firstCommentText": "", "hasNotReadNotes": False,
            "media": [f"{R2}/shorts/2026-11-21/{n}.mp4"], "mediaAltText": [],
            "publicationDate": {"dateTime": when, "timezone": "America/Chicago"}, "shortener": False,
            "smartLinkData": {"ids": []}, "text": text}
    yt = dict(base, providers=[{"network": "youtube"}],
              youtubeData={"title": title, "type": "short", "privacy": "public", "tags": tags, "category": "NEWS_POLITICS",
                           "madeForKids": False, "isAiGeneratedContent": False})
    soc = dict(base, providers=[{"network": "facebook"}, {"network": "instagram"}, {"network": "tiktok"}],
               videoThumbnailUrl=f"{R2}/covers/2026-11-21/{n}.jpg",
               facebookData={"type": "REEL", "title": title},
               instagramData={"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True},
               tiktokData={"privacyOption": "PUBLIC_TO_EVERYONE", "title": title, "isAigc": True})
    out.append({"name": n, "date": when + "-06:00", "youtube": yt, "social": soc})
json.dump(out, open("publish/ep4_shorts.json", "w"), indent=1, ensure_ascii=False)
print(len(out), "shorts", max(len(o["social"]["text"]) for o in out), "max chars")
