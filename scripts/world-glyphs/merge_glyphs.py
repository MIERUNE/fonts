#!/usr/bin/env python3
"""既存のフォントスタックに、不足しているグリフだけを別フォントから補う。

- 既存のグリフはそのまま残す（バイト単位で変更しない）
- 既存スタックに無いコードポイントだけを、stacks.json に書いた順にフォントから追加する
- 何度実行しても同じ結果になる（冪等）

使い方:
    python3 merge_glyphs.py stacks.json <フォント(.ttf)のディレクトリ> <build_pbf_glyphs の出力ディレクトリ> <リポジトリのルート>
"""
import json
import os
import sys


def _varint(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if not x & 0x80:
            return r, i


def _enc_varint(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n:
            out.append(x | 0x80)
        else:
            out.append(x)
            return bytes(out)


def _fields(b):
    i = 0
    while i < len(b):
        k, i = _varint(b, i)
        f, t = k >> 3, k & 7
        if t == 0:
            v, i = _varint(b, i)
        elif t == 2:
            n, i = _varint(b, i)
            v = bytes(b[i:i + n])
            i += n
        elif t == 5:
            v = bytes(b[i:i + 4])
            i += 4
        elif t == 1:
            v = bytes(b[i:i + 8])
            i += 8
        else:
            raise ValueError(f"unsupported wire type {t}")
        yield f, t, v


def read_glyphs(path):
    """PBF を読み、{コードポイント: Glyph メッセージの生バイト} を返す。"""
    glyphs = {}
    if not os.path.exists(path):
        return glyphs
    with open(path, "rb") as fp:
        data = fp.read()
    for f, _, stack in _fields(data):
        if f != 1:
            continue
        for f2, _, raw in _fields(stack):
            if f2 != 3:
                continue
            for f3, _, v in _fields(raw):
                if f3 == 1:
                    glyphs.setdefault(v, raw)
                    break
    return glyphs


def _len_field(num, payload):
    return _enc_varint((num << 3) | 2) + _enc_varint(len(payload)) + payload


def font_ascender_px(path, size=24):
    """build_pbf_glyphs（FreeType）と同じく、size px での ascender（hhea, 切り上げ）を返す。"""
    with open(path, "rb") as fp:
        data = fp.read()
    num_tables = int.from_bytes(data[4:6], "big")
    tables = {}
    for i in range(num_tables):
        rec = data[12 + 16 * i: 28 + 16 * i]
        tables[rec[:4].decode("latin-1")] = int.from_bytes(rec[8:12], "big")
    upem = int.from_bytes(data[tables["head"] + 18: tables["head"] + 20], "big")
    ascent = int.from_bytes(data[tables["hhea"] + 4: tables["hhea"] + 6], "big", signed=True)
    return -(-ascent * size // upem)


def shift_top(raw, delta):
    """Glyph メッセージの top を delta だけずらす（フォント間でベースラインを揃えるため）。"""
    if delta == 0:
        return raw
    out = b""
    for f, t, v in _fields(raw):
        if f == 6:
            top = ((v >> 1) ^ -(v & 1)) + delta
            v = (top << 1) ^ (top >> 31)
        if t == 0:
            out += _enc_varint(f << 3) + _enc_varint(v & 0xFFFFFFFF)
        else:
            out += _len_field(f, v)
    return out


def write_glyphs(path, name, rng, glyphs):
    stack = _len_field(1, name.encode()) + _len_field(2, rng.encode())
    for cp in sorted(glyphs):
        stack += _len_field(3, glyphs[cp])
    with open(path, "wb") as fp:
        fp.write(_len_field(1, stack))


def main():
    spec_path, src_dir, pbf_dir, repo_root = sys.argv[1:5]
    with open(spec_path) as fp:
        spec = json.load(fp)

    for target, conf in spec.items():
        target_dir = os.path.join(repo_root, target)
        if not os.path.isdir(target_dir):
            sys.exit(f"stack not found: {target_dir}")
        fills = conf["fill"]
        # top はフォントごとの ascender 基準なので、既存スタックの ascender に合わせて補正する
        delta = {f: font_ascender_px(os.path.join(src_dir, f + ".ttf")) - conf["ascender"] for f in fills}
        added = 0
        for start in range(0, 65536, 256):
            rng = f"{start}-{start + 255}"
            path = os.path.join(target_dir, f"{rng}.pbf")
            glyphs = read_glyphs(path)
            before = len(glyphs)
            for fill in fills:
                fill_path = os.path.join(pbf_dir, fill, f"{rng}.pbf")
                if not os.path.exists(fill_path):
                    sys.exit(f"missing generated glyphs: {fill_path}")
                for cp, raw in read_glyphs(fill_path).items():
                    if cp not in glyphs:
                        glyphs[cp] = shift_top(raw, delta[fill])
            if len(glyphs) != before:
                write_glyphs(path, target, rng, glyphs)
                added += len(glyphs) - before
        print(f"{target}: added {added} glyphs")


if __name__ == "__main__":
    main()
