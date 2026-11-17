"""Upload a file to the channel's Cloudflare R2 bucket and print its public URL (for Metricool).
The API token is injected by the session's network proxy for api.cloudflare.com (saved as an
environment network secret); no key is stored in this repo or read from a variable.
Usage: python3 pipeline/r2_upload.py <local_file> <key, e.g. episodes/2026-11-17/ep1.mp4>
       python3 pipeline/r2_upload.py --delete <key>
Limit: single-request uploads via the Cloudflare API are fine up to ~300 MB.
"""
import sys, os, subprocess, json, mimetypes

ACCOUNT = "9b8e14eb1d62974718628534959b3e0b"
BUCKET = "rgv-news-media"
PUBLIC = "https://pub-d5fcbef93b824664bb534c8643fb48b4.r2.dev"
API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}/objects/"


def upload(path, key):
    size = os.path.getsize(path)
    if size > 300 * 1024 * 1024: raise SystemExit(f"{path} is {size/1e6:.0f} MB; over the ~300 MB API limit")
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    r = subprocess.run(["curl", "-sS", "-m", "1800", "-X", "PUT", "-H", f"Content-Type: {ctype}",
                        "--data-binary", f"@{path}", API + key], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    if not d.get("success"): raise SystemExit(f"upload failed: {d.get('errors')}")
    url = f"{PUBLIC}/{key}"; print(url); return url


def delete(key):
    r = subprocess.run(["curl", "-sS", "-m", "60", "-X", "DELETE", API + key], capture_output=True, text=True, check=True)
    print(json.loads(r.stdout).get("success"))


if __name__ == "__main__":
    if sys.argv[1] == "--delete": delete(sys.argv[2])
    else: upload(sys.argv[1], sys.argv[2])
