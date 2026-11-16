"""Background music bed for a finished episode: one or more looping tracks, switched at chapter
starts with crossfades, kept quiet and ducked under the voice / natural sound (sidechain), then peak-limited
(the episode itself is already loudness-normalized). Video is copied untouched.

Timeline config ("music" key, read by longform.py after assembly, or run directly):
  "music": {"level_lufs": -27, "segments": [{"track": "data/music/Deliberate_Thought.mp3", "chapter": 0, "offset": 0},
                                           {"track": "data/music/Unanswered_Questions.mp3", "chapter": 4}, ...]}
Usage: python3 pipeline/music_bed.py <episode.mp4> <episode_meta.json> <timeline.json> <out.mp4>
"""
import sys, json, subprocess

XF = 3.0   # crossfade between tracks, seconds


def build(ep, meta, cfg, out):
    dur = meta["duration"]; ch = [c[0] for c in meta["chapters"]]
    segs = cfg["segments"]; level = cfg.get("level_lufs", -28)
    starts = [ch[s["chapter"]] if "chapter" in s else s.get("at", 0) for s in segs]
    args, fl, labels = ["-i", ep], [], []
    for i, (s, st) in enumerate(zip(segs, starts)):
        end = starts[i + 1] + XF if i + 1 < len(segs) else dur
        ln = end - st
        args += ["-stream_loop", "-1", "-ss", str(s.get("offset", 0)), "-i", s["track"]]
        fin = 2.5 if i == 0 else XF
        fl.append(f"[{i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={ln:.3f},"
                  f"loudnorm=I={level}:TP=-8:LRA=11,aresample=48000,"
                  f"afade=t=in:d={fin},afade=t=out:st={max(0, ln - XF):.3f}:d={XF},"
                  f"adelay={int(st * 1000)}|{int(st * 1000)}[m{i}]")
        labels.append(f"[m{i}]")
    fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad,atrim=duration={dur:.3f}[bed]")
    # duck the bed under the episode's own audio (narration + natural sound)
    fl.append("[0:a]asplit=2[key][prog]")
    fl.append("[bed][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=600:makeup=1[duck]")
    # episode audio is already at -14 LUFS: add the bed at a fixed level and only limit peaks
    # (single-pass loudnorm here would pump the music up in every pause)
    fl.append("[prog][duck]amix=inputs=2:normalize=0,alimiter=limit=0.85:level=false,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-filter_complex", ";".join(fl),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", out], check=True)
    print("music ok", out)


if __name__ == "__main__":
    ep, meta, tl, out = sys.argv[1:5]
    build(ep, json.load(open(meta)), json.load(open(tl))["music"], out)
