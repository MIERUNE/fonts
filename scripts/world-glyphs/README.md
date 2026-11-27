# world-glyphs

`Noto Sans CJK JP Regular` / `Bold` のグリフに、Noto CJK に含まれない世界の文字を補うスクリプトです。

Noto Sans CJK JP は Adobe-Japan1 由来のラテン文字しか持たないため、トルコ語の `İ ı Ş ş Ğ ğ` やポーランド語の `ą ę ł ś ż`、チェコ語の `č ř`、ルーマニア語の `ș ț` などが地図上で表示されませんでした。

## 方針

- **既存のグリフは一切変更しない**（バイト単位で同一）。日本語・既存のラテン文字の見た目は変わりません
- 既存スタックに無いコードポイントだけを、`stacks.json` の `fill` に書いた順に Noto フォントから追加します
- フォントごとに ascender が違うため、追加するグリフの `top` を既存スタックの ascender（`stacks.json` の `ascender`）に合わせて補正し、ベースラインを揃えます
- 何度実行しても同じ結果になります（冪等）

補うフォント：Noto Sans（ラテン・ギリシャ・キリル）、Arabic、Hebrew、Armenian、Georgian、Thai、Lao、Ethiopic、Thaana、Tifinagh、Cherokee、Canadian Aboriginal

### 対象外にした文字

MapLibre は文字の整形（シェーピング）をしないため、字形があっても正しく表示できない文字は追加していません。

- インド系文字（Devanagari、Bengali、Gurmukhi、Gujarati、Oriya、Tamil、Telugu、Kannada、Malayalam、Sinhala）：結合・並べ替えが必要
- Khmer、Myanmar：下付き文字・並べ替えが必要
- Syriac：文字の連結が必要（RTL プラグインはアラビア文字しか整形しない）
- Mongolian：縦書きと文字の連結が必要

これらの地域でも、スタイルが `name:latin` を併記していればラテン文字の名前は表示されます。

## 実行

```bash
cargo install build_pbf_glyphs
bash scripts/world-glyphs/build.sh
```

フォントは [notofonts.github.io](https://github.com/notofonts/notofonts.github.io) からダウンロードされ、`scripts/world-glyphs/.work/` に置かれます（git 管理外）。

## 制約

- アラビア語・ヘブライ語・ディベヒ語（Thaana）の右から左の表示には、MapLibre GL JS では RTL テキストプラグインが必要です（maplibre-native / chiitiler は標準で対応）
- タイ語・ラオ語は、声調記号が重なる場合にわずかにずれることがあります
- `Noto Sans CJK JP Light` は対象外です
