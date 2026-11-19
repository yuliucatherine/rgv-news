# RGV News: daily production runbook

Followed by the automated daily session. One episode per day: a long-form video (3–6 min,
16:9) for YouTube + Facebook, and one Short/Reel (30–60 s, 9:16) cut from its strongest segment.

## Audience and angle
Housing developers, builders and real-estate investors watching the Rio Grande Valley.
Each episode covers **developments in Texas that can affect the RGV**: the exciting side
(projects, employers, infrastructure, funding, population growth) **and** the concerning
side (water, insurance, permitting, tariffs and trade, interest rates, flood risk, policy).
Default shape: 2 opportunities + 1 risk to watch. Every segment ends with "why it matters"
for someone who builds, buys, or lends.

## Editorial rules (non-negotiable)
1. **Every number and claim must come from a source found today**, and every source goes in
   the description. If two sources disagree, say so or leave the number out.
2. Prefer primary sources (city/county releases, TxDOT, TWDB, NADBank, EDA, Census, company
   announcements) and established local outlets (KRGV, ValleyCentral, The Monitor/MyRGV,
   Texas Border Business, Texas Tribune, Rio Grande Guardian).
3. **Say what is proposed vs. approved vs. under construction.** Never present a proposal
   as done.
4. Don't repeat a story already covered in the last 14 days (check `episodes/`) unless
   there is genuinely new information; then say "update:".
5. No AI-generated pictures of real places, people, or buildings. Visuals are text, numbers,
   and charts only.
6. Not financial advice: the outro and description say so. No "buy now" language.
7. Stay neutral on politics: report what officials did and said, with attribution.
8. If fewer than 2 solid, sourced stories can be found, make a shorter episode rather than pad.

## Steps
1. `bash setup.sh` (installs packages, downloads the free voice model).
2. Research: search for news from the last ~7 days (RGV cities: McAllen, Edinburg, Mission,
   Pharr, Harlingen, Brownsville, Weslaco, San Benito, Rio Grande City, plus statewide Texas
   items that affect the RGV). Open questions → leave them out.
3. Write `episodes/YYYY-MM-DD/episode.json`, following the schema of the most recent episode
   (scene types: title, section, stat, split, bullets, outro; `tone` up/down; `short` block
   with hook, scene_indexes, cta; `description`, `tags`, `youtube_title`, `thumb_text`).
   Narration: plain spoken English, numbers written as words, ~150 words per minute.
4. Narration (ElevenLabs connector, voice **James**, voice_id `QhpsGjDKZmM9qRYdMhBD`,
   model `eleven_v4`, `generations_count` 1): create one flow named "RGV News YYYY-MM-DD
   narration", generate one clip per scene plus `short.hook` and `short.cta`, poll until all
   are completed (a "concurrency limit" note just means it retries automatically; never
   re-submit), then download each `content_url` with curl to
   `episodes/YYYY-MM-DD/audio/scene_NN.mp3`, `short_hook.mp3`, `short_cta.mp3`.
   Budget: ~1 credit per character, about 3,000 credits per episode. If ElevenLabs is
   unavailable, skip this step: the renderer falls back to the free local voice.
5. Render: `python3 pipeline/render.py episodes/YYYY-MM-DD --voice-dir models`.
6. **Quality check before publishing**: extract a frame from every scene and look at it
   (text not cut off, nothing overlapping); confirm durations; re-read the narration against
   the sources. Fix and re-render if anything is off.
7. Put the chapter timestamps from `long_meta.json` into the description.
8. Upload the media and schedule posts (see "Publishing" below).
9. Commit the episode folder (without the .mp4 files) to `main` so future runs can see what
   was covered.

## Publishing
Metricool brand: **RGV News** (blogId 8063182, timezone America/Chicago).
Networks: YouTube (channel "RGV Today") and the Facebook Page "RGV News".
**Only ever post to blogId 8063182.** Before scheduling, call getBrandSettings and confirm the
brand label is "RGV News" and the YouTube channel ID is UCAPGqmPbbEfxRUI_TkzxD6g. If either
doesn't match, stop and tell the owner instead of posting. Other channels the owner runs
(e.g. Tiny Corrections) are handled elsewhere and are off-limits here.

Hosting: copy `long.mp4`, `short.mp4`, `thumb.jpg` into `<date>/` on the `media` branch
(orphan branch; use a git worktree), commit and push. Public URLs are
`https://raw.githubusercontent.com/yuliucatherine/rgv-news/media/<date>/<file>`; Metricool
copies the file to its own storage when the post is created. Keep only the last 14 days of
media on that branch (delete older date folders) so it stays small.

Posts per episode:
| Post | YouTube | Facebook |
|---|---|---|
| Long video | type `video`, category NEWS_POLITICS, madeForKids false, title, tags | type `POST`, title |
| Short / Reel | type `short` | type `REEL` |

- Long video publishes at the best evening slot (Metricool `getBestTimeToPostByNetwork`,
  default 6:00 PM Central); the Short publishes the next morning (default 8:00 AM).
- Narration is synthetic but the content isn't a realistic depiction of real people or
  events, so `isAiGeneratedContent` stays false; the description notes the narration is
  computer-generated.
- **Review window:** videos are made in the morning and scheduled for the evening; the owner
  gets a summary with the title, the sources, and a link to the post in Metricool so it can be
  edited or deleted before it goes live.

## Style guide (owner's notes)
- **Narration is always ElevenLabs "James"** (voice_id `QhpsGjDKZmM9qRYdMhBD`). The free local
  voice is only for internal drafts and demos, never for anything published.
- **Burned-in captions** on every long video and Short: short phrases (3–5 words), bold, high
  contrast, kept clear of on-screen credits.
- **Kinetic emphasis words** for key lines: big words that fade/pop in one at a time on the left
  third of the frame, timed to the narration. Example: narration "For builders and investors, the
  question is simple: where will the water be?" → on screen, word by word: WHERE · WILL · THE ·
  WATER · BE? Use 2–4 of these moments per episode, on the most important questions and numbers.
- Every real photo/video carries an on-screen credit; maps and 3D carry a data-source line;
  anything illustrative is labeled "illustrative".
- Episode format: 8–12 minutes on one development (or closely related ones), plus 2–3 Shorts
  cut from it. Budget ≈ 50,000 ElevenLabs credits for 3–4 episodes.
- **Vertical safe zone (Shorts/Reels):** all text must fit inside x 60–940 and y 220–1340 on a
  1080×1920 frame (clear of the right-side buttons and the bottom title/caption overlay). Text
  auto-shrinks to fit (see `fit()` in pipeline/short_flight15.py). Before posting, render sample
  frames with the red danger zones drawn on and check nothing overlaps them.

## Credibility and copyright rules (added Nov 16, 2026)
- Every long episode includes an **"On the record" montage** right after the cold open: 4–6 real headlines
  from the outlets/officials the episode cites (outlet, exact headline, date), built with
  `pipeline/headlines.py` from `episodes/<ep>/headlines.json`. Copy headlines exactly from the saved
  source page (`og:title`); never paraphrase inside quote marks.
- **Never use TV/news broadcast clips or outlet logos.** Stations use Content ID; one clip can mean a
  claim or a copyright strike. Quote headlines as text with credit; link sources in the description.
- Generative-AI video only for clearly generic illustrative b-roll, labeled "Illustrative", and never
  to depict a real place, person or event. Mark YouTube's altered/synthetic flag when realistic.
- Episodes render at 60 fps (`"fps": 60` in the timeline); 3D shots held longer than rendered must be
  smoothed with `pipeline/smooth.py` (the assembler warns when a clip would look choppy).
- Music: quiet ducked bed via the timeline `"music"` key (`pipeline/music_bed.py`); CC BY tracks only,
  credited in the description. Library (`assets/music/`, Kevin MacLeod, incompetech.com, CC BY 4.0;
  catalog: incompetech.com/music/royalty-free/pieces.json):
  - Deliberate Thought, Unanswered Questions: calm explainer
  - Industrial Cinematic, Crusade - Heavy Industry: construction, ports, industry
  - Rising Tide: energetic middle sections · I Can Feel it Coming: risks and tension
  - Inspired: opportunities and closings · Dreamer: soft piano for reflective beats
  Vary the tracks between episodes; list every track used in the description's MUSIC line.
- Thumbnail: `pipeline/thumbnail.py` + `episodes/<ep>/thumbnail.json` (own footage, one sourced number,
  short headline, brand chip).

## Platforms and hosting (updated Nov 17, 2026)
- Brand 8063182 now has YouTube (UCAPGqmPbbEfxRUI_TkzxD6g), Facebook (1468277193033622), Instagram (@rgv.news)
  and TikTok (RGV News). Long episodes: YouTube + Facebook. Shorts/teasers: YouTube Shorts, Instagram Reels,
  TikTok, Facebook Reels.
- GitHub releases and Git LFS are blocked from cloud sessions; the media branch takes files under 100 MB.
  For long episodes, encode a 2-pass HEVC copy under ~97 MB (`libx265 -preset medium -b:v 1100k`, `-tag:v hvc1`,
  AAC 128k) and check SSIM against the master (target >= 0.99 on most samples). Episode 1: Metricool post
  431544038, scheduled Nov 17, 2026 08:55 Central, thumbnail via `videoThumbnailUrl`.

## Video hosting: Cloudflare R2 (set up Nov 17, 2026)
- Bucket `rgv-news-media` (account 9b8e14eb...), public base `https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev`.
- Upload with `python3 pipeline/r2_upload.py <file> <key>`; it prints the public URL to give Metricool.
  The Cloudflare API token is a network secret on the rgv-news environment (host api.cloudflare.com,
  R2 Edit only, expires Nov 2027). Never put it in the repo.
- Upload full-quality masters (no HEVC squeeze needed). Keys: `episodes/<date>/<slug>.mp4`, `shorts/<date>/<slug>.mp4`.
- Metricool copies media into its own storage when a post is scheduled, so old files can be deleted
  after the post publishes to stay far below the 10 GB free tier.

## Always moving (owner rule, Nov 17, 2026)
- Never hold a static frame with only voice-over. Something must move on screen at all times.
- Change the main visual at least every 4-8 seconds in Shorts (8-12 s in long episodes); a single card,
  chart or quote may hold the screen for 6 s at most in a Short, then cut, zoom or animate.
- Charts build (bars grow, lines draw, numbers count); cards get a push-in plus elements animating in;
  quotes reveal line by line with a cutaway to footage or a map; maps pan/zoom while labels pop.
- QC step: scan each Short/episode for any 5 s window with near-zero frame difference and fix it before review.

## Length and pacing (owner rule, Nov 18, 2026)
- Long-form episodes: 6-7 minutes total (about 5,000-5,500 narration characters, roughly 28-32 paragraphs).
- No dead air: narration pads about [0.15, 0.3] s, `"trim_narration": true` in the timeline, section cards 1.5 s,
  title card 2.5 s, end card 3 s, headline montage about 6 s. The music bed carries transitions; the voice should
  never stop while an animation plays on its own.

## Shorts always point to the full video (owner rule, Nov 18, 2026)
- Every Short ends with an on-screen "Watch the full video on YouTube" line (default in shorts_from_episode.py).
- Every Short caption includes "Watch the full breakdown on YouTube: <direct link to the episode>".
  Episode 1: https://www.youtube.com/watch?v=Fp4NCLi_k-I
  Episode 3: https://www.youtube.com/watch?v=EHK9LqRBihU
- Instagram and TikTok captions don't make links clickable: keep the YouTube channel link in both profile bios.
- Schedule Metricool posts that pull from R2 one at a time: parallel downloads from the r2.dev URL can time out
  (Nov 18, 2026). A failed create makes no post, so retrying it alone is safe.

## Scripts feel a little urgent (owner rule, Nov 19, 2026; applies from Episode 4)
The goal is "watch this now, it affects your next decision", not panic. Urgency must come from real,
sourced dates, deadlines and stakes. Never invent a deadline, inflate a number or use clickbait words
("shocking", "you won't believe").
- **First 10 seconds:** say what is happening right now and why it matters to the viewer's money, with a real
  date or number. Present tense: "Right now...", "This year...", "Before the end of 2027...".
- **The question:** make it about the viewer's decision ("before you buy, build or lend here..."), not an
  abstract trend.
- **Put the clock on screen:** name the next dated milestone (a vote, a filing, a start date, a lease-up)
  and how far away it is ("that's months away, not years").
- **End every section with a forward hook** into the next one ("But that's not the part that should
  worry builders.").
- **Close with an action and a time frame:** what to check or do now, and the next date to watch.
- Keep the calm, credible tone: urgent wording, measured claims. If the sources don't support urgency
  for a point, state it plainly.
- Titles and Short hooks follow the same rule: a real number plus a time element
  (e.g. "7,500 jobs now. About 700 after 2027.").

## Shorts cadence (owner rule, Nov 19, 2026)
- Space Shorts 4 hours apart (e.g. 10:20 AM, 2:20 PM, 6:20 PM, 10:20 PM Central), not one per day.
  Keep times on :20 to avoid the top-of-hour rush. Avoid the overnight slots (after 10:20 PM, before 10:20 AM).
- Schedule each Metricool post one at a time (R2 fetches can time out in parallel).
