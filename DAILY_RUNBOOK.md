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
