# Explainer-UI style (test, Nov 24, 2026)

Vertical Shorts built from code instead of footage: mock app cards (counters, dot grids, status steppers),
a mascot (our own map pin in a hard hat, not anyone else's character), a status chip that changes each beat,
and karaoke captions that light up the spoken word. Each scene is plain HTML/SVG whose state is a function
of time, `window.render(t)`, so headless Chromium can step it exactly at 60 fps.

    node pipeline/ui_explainer/render.js pipeline/ui_explainer/sh4_test.html <frames_dir> 22.3 60
    # then mux frames + voice (see the ffmpeg line in the session log / make step)

Caption timing comes from pauses detected in the voice clips (ffmpeg silencedetect), split per word by length.
