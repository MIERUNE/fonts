#!/usr/bin/env bash
# Noto Sans CJK JP のグリフに、世界の文字（ラテン拡張・ギリシャ・キリル・アラビア・インド系など）を補う。
#
# 必要なもの: curl, python3, build_pbf_glyphs（cargo install build_pbf_glyphs）
# 使い方:    bash scripts/world-glyphs/build.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
WORK="${WORK:-$HERE/.work}"
NOTO_BASE="https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts"

command -v build_pbf_glyphs >/dev/null || { echo "build_pbf_glyphs が必要です: cargo install build_pbf_glyphs" >&2; exit 1; }

mkdir -p "$WORK/src" "$WORK/pbf"

# stacks.json に書かれたフォント（例: NotoSansArabic-Bold）を notofonts からダウンロードする
python3 -c 'import json,sys; print("\n".join(sorted({f for v in json.load(open(sys.argv[1])).values() for f in v["fill"]})))' "$HERE/stacks.json" |
while read -r font; do
  family="${font%-*}"
  dest="$WORK/src/$font.ttf"
  [ -f "$dest" ] && continue
  echo "download: $font"
  curl -sSfL -o "$dest" "$NOTO_BASE/$family/hinted/ttf/$font.ttf"
done

# SDF グリフを生成（出力は $WORK/pbf/<ファイル名>/<range>.pbf）
build_pbf_glyphs "$WORK/src" "$WORK/pbf"

# 既存スタックに無いグリフだけを追加
python3 "$HERE/merge_glyphs.py" "$HERE/stacks.json" "$WORK/src" "$WORK/pbf" "$ROOT"
