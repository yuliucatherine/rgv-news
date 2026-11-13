#!/usr/bin/env bash
# One-time setup on a fresh machine: Python packages + free voice model (~350 MB).
set -euo pipefail
cd "$(dirname "$0")"
pip install -q kokoro-onnx soundfile numpy pillow geopandas shapely pyproj pyogrio scipy bpy
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s models/kokoro-v1.0.onnx ] || curl -sSL -o models/kokoro-v1.0.onnx $base/kokoro-v1.0.onnx
[ -s models/voices-v1.0.bin ]  || curl -sSL -o models/voices-v1.0.bin  $base/voices-v1.0.bin
echo "setup ok"
