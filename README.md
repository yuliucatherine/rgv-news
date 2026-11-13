# RGV News

Automated daily video pipeline for the RGV News YouTube channel and Facebook Page:
Texas and Rio Grande Valley development news for housing developers and investors.

- `pipeline/render.py`: turns an `episode.json` script into a 16:9 long video, a 9:16 Short with captions, and a thumbnail
- `setup.sh`: installs dependencies and the free fallback voice model
- `DAILY_RUNBOOK.md`: editorial rules and the daily production + publishing steps
- `episodes/YYYY-MM-DD/`: one folder per episode (script, metadata; videos are not stored on `main`)
