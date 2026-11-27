# world-glyphs

`Noto Sans CJK JP Regular` / `Bold` のグリフに、Noto CJK に含まれない世界の文字を補うスクリプトです。

Noto Sans CJK JP は Adobe-Japan1 由来のラテン文字しか持たないため、トルコ語の `İ ı Ş ş Ğ ğ` やポーランド語の `ą ę ł ś ż`、チェコ語の `č ř`、ルーマニア語の `ș ț` などが地図上で表示されませんでした。

## 方針

- **既存のグリフは一切変更しない**（バイト単位で同一）。日本語・既存のラテン文字の見た目は変わりません
- 既存スタックに無いコードポイントだけを、`stacks.json` の `fill` に書いた順に Noto フォントから追加します
- フォントごとに ascender が違うため、追加するグリフの `top` を既存スタックの ascender（`stacks.json` の `ascender`）に合わせて補正し、ベースラインを揃えます
- 何度実行しても同じ結果になります（冪等）

補うフォント：Noto Sans（ラテン・ギリシャ・キリル）、Arabic、Hebrew、Armenian、Georgian、Thai、Lao、Khmer、Myanmar、Devanagari、Bengali、Gurmukhi、Gujarati、Oriya、Tamil、Telugu、Kannada、Malayalam、Sinhala、Ethiopic、Thaana、Syriac、Mongolian、Tifinagh、Cherokee、Canadian Aboriginal

## 実行

```bash
cargo install build_pbf_glyphs
bash scripts/world-glyphs/build.sh
```

フォントは [notofonts.github.io](https://github.com/notofonts/notofonts.github.io) からダウンロードされ、`scripts/world-glyphs/.work/` に置かれます（git 管理外）。

## 制約

- グリフ（字形）が揃うだけで、文字の整形（シェーピング）は MapLibre 側の機能に依存します
  - アラビア語・ヘブライ語の右から左の表示には MapLibre の RTL テキストプラグインが必要です
  - インド系文字・タイ語などの結合文字は、MapLibre ではシェーピングされないため崩れて表示されることがあります（文字が消えることはなくなります）
- `Noto Sans CJK JP Light` は対象外です
