#!/usr/bin/env bash
# One-time setup: Python deps, offline Whisper model, HyperFrames CLI + headless Chrome.
set -euo pipefail
cd "$(dirname "$0")"

pip install -q sherpa-onnx numpy scipy

# Whisper "medium" (int8) packaged by sherpa-onnx on GitHub releases (works where HuggingFace is blocked)
if [ ! -f models/sherpa-onnx-whisper-medium/medium-encoder.int8.onnx ]; then
  mkdir -p models && cd models
  curl -sSL -o w.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-medium.tar.bz2
  tar xjf w.tar.bz2 && rm w.tar.bz2
  rm -f sherpa-onnx-whisper-medium/medium-encoder.onnx sherpa-onnx-whisper-medium/medium-decoder.onnx
  cd ..
fi

# RNNoise model for speech denoising (ffmpeg arnndn)
[ -f models/rnnoise.rnnn ] || curl -sSL -o models/rnnoise.rnnn \
  https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn

npm install --no-audit --no-fund
npx hyperframes browser ensure
echo "setup done"
