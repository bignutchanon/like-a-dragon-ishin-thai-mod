#!/usr/bin/env python3
"""ฝัง glyph ไทย (Sarabun) ลงฟอนต์ SDF ของ Lost Judgment — generalized ใช้ได้ทุกฟอนต์ L8
พอร์ต/ขยายจาก K2R inject_thai_sdf.py

ใช้กับ: system_main_en_all_sdf (เมนู/ซับหลัก), caption_en_fhd/uhd (หัวข้อ serif
ที่ทำ "อัปเกรดความสามารถ" เพี้ยนเป็น ÂûªíβùçãóîôÚîôîùö ในเมนูสกิล v1.2)

หลักการ generalize:
- อ่านขนาด atlas จาก DDS header · วัด EM_PER_PX / SLOPE / PAD จาก glyph เดิมตอนรัน
- วัด CAP_EM (median yTop ของ A-Z) แล้วสเกลอักษรไทย + ระดับแนวตั้งทั้งหมดตามสัดส่วน
  ที่พิสูจน์ในเกมแล้วของฟอนต์ sdf หลัก (ก ink = 0.773×cap, เพดานวรรณยุกต์ 1.47×cap ฯลฯ)
- donor slot ที่ไม่มีในฟอนต์ (เช่น β ā ō ใน caption) -> insert เพิ่ม (ปลอดภัยเฉพาะ
  ไฟล์ tail เป็น padding เท่านั้น — มี assert กัน)
- ที่ว่างใต้ atlas ไม่พอ -> reclaim สี่เหลี่ยมรูปเก่าของ donor ที่ถูก repoint ทิ้ง

ใช้:
  python scripts/inject_thai_sdf.py                      # ฟอนต์หลัก sdf
  python scripts/inject_thai_sdf.py caption_en_fhd caption_en_uhd
อ่าน  extracted/font/<name>.{bin,dds} (ต้นฉบับเกม — ไม่แตะ)
เขียน build/font/<name>.{bin,dds} + build/font/preview_<name>.png
"""
import io
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as pirate_paths
from font_tool import Font, cp_pack, cp_unpack
MAP = 'cyr' if '--map=cyr' in sys.argv else 'latin1'
if MAP == 'cyr':
    from thai_encode_cyr import ENCODE, DECODE, encode   # donor Cyrillic (tbgm_0p / tbcgr_0p)
else:
    from thai_encode import ENCODE, DECODE, encode       # donor Latin-1 (metaoffcpro-condbook)
ALIAS_THAI = '--alias-thai' in sys.argv

SS = 8

THAI_CHARS = sorted(set(DECODE.values()))
SLOTS_OF = {}
for cp, ch in DECODE.items():
    SLOTS_OF.setdefault(ch, []).append(cp)

UPPER = set('ัิีึื็') & set(THAI_CHARS)
TONE  = set('่้๊๋์') & set(THAI_CHARS)
LOWER = set('ุู') & set(THAI_CHARS)

# ---- สัดส่วน envelope เทียบ cap height (จากฟอนต์ sdf หลัก: cap=687em ค่าที่
#      K2R/Pirate v1.2 พิสูจน์ในเกม: THAI_SCALE 0.90, TONE 0.70, LOWER 0.80,
#      L_TONE 845, LOWER_TOP -60, เพดาน 1010) ----
REF_CAP     = 687.0
R_BASE      = 0.90 / REF_CAP      # scale Sarabun-unit ต่อ 1 cap-em
R_TONE      = 0.70 / REF_CAP
R_LOWER     = 0.80 / REF_CAP
R_LTONE     = 845.0 / REF_CAP
R_LOWERTOP  = -60.0 / REF_CAP
R_CEIL      = 1010.0 / REF_CAP


def measure(f, atlas, aw, ah):
    """วัด (em_per_px, slope, pad_px, cap_em) จาก glyph เดิม"""
    em_ratios, pads, slopes, caps = [], [], [], []
    uppercase = {chr(c) for c in range(65, 91)}
    for i in range(len(f.cps)):
        ch = cp_unpack(f.cps[i])
        u0, v0, u1, v1 = f.uv[i]
        x0, y0 = int(round(u0 * aw)), int(round(v0 * ah))
        x1, y1 = int(round(u1 * aw)), int(round(v1 * ah))
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        tile = atlas[y0:y1, x0:x1].astype(np.float32)
        ink = tile >= 127.5
        if ink.sum() < 30:
            continue
        ys, xs = np.where(ink)
        iw, ih = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        xmin, ybot, xmax, ytop, adv = f.met[i]
        w_em, h_em = xmax - xmin, ytop - ybot
        if iw >= 6 and w_em > 0:
            em_ratios.append(w_em / iw)
        if ih >= 6 and h_em > 0:
            em_ratios.append(h_em / ih)
        pads.extend([xs.min(), ys.min(), tile.shape[1] - 1 - xs.max(),
                     tile.shape[0] - 1 - ys.max()])
        g = np.abs(np.diff(tile, axis=1))
        band = (tile[:, :-1] > 40) & (tile[:, :-1] < 215)
        if band.any():
            slopes.append(np.percentile(g[band], 90))
        if ch in uppercase:
            caps.append(ytop)
    em_per_px = float(np.median(em_ratios))
    pad_px = float(np.median(pads))
    slope = float(np.median(slopes))
    cap_em = float(np.median(caps))
    print(f'  วัด: EM_PER_PX={em_per_px:.2f} SLOPE={slope:.2f} PAD={pad_px:.1f} CAP={cap_em:.0f}em')
    assert 6 <= slope <= 40 and 2 <= pad_px <= 20 and cap_em > 100, 'ค่าที่วัดหลุดช่วง'
    return em_per_px, slope, pad_px, cap_em


class Packer:
    """จองที่ใน atlas: แถบว่างล่าง (shelf) ก่อน แล้วค่อย orphan rects (รูปเก่า donor)"""
    def __init__(s, aw, ah, y_start, orphans):
        s.aw, s.ah = aw, ah
        s.px, s.py, s.rowh, s.GAP = 1, y_start, 0, 1
        s.orphans = sorted(orphans, key=lambda r: r[2] * r[3])   # เล็กก่อน
        s.from_orphan = 0

    def place(s, tw, th):
        # 1) แถบว่างล่าง
        px, py, rowh = s.px, s.py, s.rowh
        if px + tw + s.GAP > s.aw:
            px = 1; py += rowh + s.GAP; rowh = 0
        if py + th < s.ah:
            s.px, s.py, s.rowh = px + tw + s.GAP, py, max(rowh, th)
            return px, py
        # 2) orphan rect ที่พอดีที่สุด + guillotine split เก็บเศษกลับเข้าคลัง
        for k, (ox, oy, ow, oh) in enumerate(s.orphans):
            if tw <= ow and th <= oh:
                s.orphans.pop(k)
                s.from_orphan += 1
                if ow - tw >= 6:
                    s.orphans.append((ox + tw, oy, ow - tw, th))
                if oh - th >= 6:
                    s.orphans.append((ox, oy + th, ow, oh - th))
                s.orphans.sort(key=lambda r: r[2] * r[3])
                return ox, oy
        raise AssertionError(f'atlas เต็ม (tile {tw}x{th})')


def inject_font(name):
    ttf = pirate_paths.SARABUN_TTF
    src_bin = pirate_paths.EXTRACTED / 'font' / (name + '.bin')
    src_dds = pirate_paths.EXTRACTED / 'font' / (name + '.dds')
    out_dir = pirate_paths.BUILD / 'font'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f'== {name} ==')

    f = Font(str(src_bin))
    dds = bytearray(open(src_dds, 'rb').read())
    ah, aw = struct.unpack_from('<II', dds, 12)
    assert struct.unpack_from('<I', dds, 88)[0] == 8, 'atlas ต้องเป็น 8-bit luminance'
    atlas = np.frombuffer(dds, np.uint8, aw * ah, 128).reshape(ah, aw).copy()
    slot_index = {cp_unpack(cp): i for i, cp in enumerate(f.cps) if cp_unpack(cp)}

    em_per_px, slope, pad_px, cap_em = measure(f, atlas, aw, ah)
    em_per_hipx = em_per_px / SS

    # สเกล/ระดับแนวตั้ง อิง cap ของฟอนต์นี้
    s_base, s_tone, s_lower = R_BASE * cap_em, R_TONE * cap_em, R_LOWER * cap_em
    l_tone, lower_top, ceil_em = R_LTONE * cap_em, R_LOWERTOP * cap_em, R_CEIL * cap_em
    font_px = 1000 * s_base * SS / em_per_px

    def render_hi(ch, su):
        F = font_px * su / s_base
        font = ImageFont.truetype(str(ttf), int(round(F)))
        W = int(F * 4); H = int(F * 5)
        ox, oy = int(F * 1.5), int(F * 3.2)
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).text((ox, oy), ch, font=font, fill=255, anchor='ls')
        bb = im.getbbox()
        if not bb:
            return None
        l, t, r, b = bb
        mask = np.asarray(im.crop(bb), dtype=np.uint8) >= 128
        return mask, (l - ox) * em_per_hipx, (oy - t) * em_per_hipx, font.getlength(ch) * em_per_hipx

    def sdf_tile(mask):
        pad = int(round(pad_px * SS))
        m = np.pad(mask, pad)
        h, w = m.shape
        H2 = -(-h // SS) * SS
        W2 = -(-w // SS) * SS
        m = np.pad(m, ((0, H2 - h), (0, W2 - w)))
        d_in = distance_transform_edt(m)
        d_out = distance_transform_edt(~m)
        d = np.where(m, d_in - 0.5, -(d_out - 0.5))
        d = d.reshape(H2 // SS, SS, W2 // SS, SS).mean(axis=(1, 3)) / SS
        return np.clip(np.rint(127.5 + slope * d), 0, 255).astype(np.uint8)

    # ---- render ----
    glyphs, natives = {}, {}
    for ch in THAI_CHARS:
        su = s_tone if ch in TONE else s_lower if ch in LOWER else s_base
        r = render_hi(ch, su)
        assert r, f'Sarabun ไม่มี glyph {ch!r}'
        mask, x0, ytop, adv = r
        natives[ch] = (x0, ytop, adv, mask.shape[1] * em_per_hipx, mask.shape[0] * em_per_hipx, su)
        glyphs[ch] = {'tile': sdf_tile(mask)}

    cons = [c for c in THAI_CHARS if 0x0E01 <= ord(c) <= 0x0E2E]
    MADV = float(np.median([natives[c][2] for c in cons]))

    # ---- metrics ----
    for ch in THAI_CHARS:
        x0, ytop, adv, w, h, su = natives[ch]
        if ch in UPPER:
            bx, yt, a = MADV + x0, ytop, 0
        elif ch in TONE:
            cx = MADV + (x0 / (su / s_base) + (x0 / (su / s_base) + w / (su / s_base))) / 2
            bx, yt, a = cx - w / 2, min(l_tone + h, ceil_em), 0
        elif ch in LOWER:
            cx = MADV + (x0 / (su / s_base) + (x0 / (su / s_base) + w / (su / s_base))) / 2
            bx, yt, a = cx - w / 2, lower_top, 0
        else:
            bx, yt, a = x0, ytop, adv
        met = (int(round(bx)), int(round(yt - h)), int(round(bx + w)),
               int(round(yt)), int(round(a)))
        assert all(-32768 <= v <= 32767 for v in met)
        glyphs[ch]['met'] = met

    # ---- โซนว่าง + orphan rects (รูปเก่าของ donor ที่มีอยู่แล้วและจะถูก repoint) ----
    y_used = max(int(np.ceil(uv[3] * ah)) for uv in f.uv)
    y_start = y_used + 2
    orphans = []
    for ch in THAI_CHARS:
        for cp in SLOTS_OF[ch]:
            i = slot_index.get(chr(cp))
            if i is None:
                continue
            u0, v0, u1, v1 = f.uv[i]
            x0, y0 = int(np.ceil(u0 * aw)), int(np.ceil(v0 * ah))
            x1, y1 = int(u1 * aw), int(v1 * ah)
            if x1 - x0 > 4 and y1 - y0 > 4:
                orphans.append((x0, y0, x1 - x0, y1 - y0))
    print(f'  โซนว่าง y={y_start}..{ah} ({ah - y_start} แถว) + orphan {len(orphans)} rects')

    # ---- --grow: atlas เล็กเกิน (เช่น hankaku 512x192 มีแค่ ASCII 95 ตัว ไม่มี donor ให้ reclaim)
    # → ต่อความสูง atlas ลงล่างเป็น 2 เท่า, rescale v ของ glyph เดิม, อัปเดต DDS header
    # (DDS ของฟอนต์เกมเป็น 8-bit luminance ไม่มี mip · UV normalized → เอนจิ้นอ่านขนาดจาก header)
    grown = False
    if GROW:
        # dry-run pack ก่อน เพื่อขยายเท่าที่จำเป็น (ปัดขึ้นทวีคูณ 16) — ไม่ใช่ 2 เท่าเสมอ (ja_all atlas ใหญ่มาก)
        dry = Packer(aw, ah * 4, y_start, list(orphans))
        need = ah
        for ch in sorted(THAI_CHARS, key=lambda c: glyphs[c]['tile'].shape[0], reverse=True):
            th_, tw = glyphs[ch]['tile'].shape
            px, py = dry.place(tw, th_)
            need = max(need, py + th_ + 2)
        new_ah = max(ah, ((need + 15) // 16) * 16)
        big = np.zeros((new_ah, aw), np.uint8)
        big[:ah] = atlas
        f.uv = [(u0, v0 * ah / new_ah, u1, v1 * ah / new_ah) for (u0, v0, u1, v1) in f.uv]
        atlas, ah, grown = big, new_ah, True
        struct.pack_into('<I', dds, 12, ah)
        print(f'  --grow: ขยาย atlas เป็น {aw}x{ah} (โซนว่างใหม่ y={y_start}..{ah})')

    packer = Packer(aw, ah, y_start, orphans)
    order = sorted(THAI_CHARS, key=lambda c: glyphs[c]['tile'].shape[0], reverse=True)
    for ch in order:
        tile = glyphs[ch]['tile']
        th_, tw = tile.shape
        px, py = packer.place(tw, th_)
        atlas[py:py + th_, px:px + tw] = tile
        glyphs[ch]['uv'] = (px / aw, py / ah, (px + tw) / aw, (py + th_) / ah)
    print(f'  วาด {len(order)} glyph (ใช้ orphan {packer.from_orphan})')

    # ---- repoint + insert slot ที่ขาด ----
    # หา index สดจากค่า cp ทุกครั้ง — add_glyph ทำให้ index เดิมเลื่อน (ห้าม cache)
    n_re = n_ins = 0
    for ch in THAI_CHARS:
        for cp in SLOTS_OF[ch]:
            key = cp_pack(chr(cp))
            if key in f.cps:
                i = f.cps.index(key)
                f.uv[i] = glyphs[ch]['uv']
                f.met[i] = glyphs[ch]['met']
                n_re += 1
            else:
                assert not f.tail.strip(b'\x00'), \
                    f'insert ไม่ปลอดภัย: {name} มี tail จริง ({len(f.tail)}B)'
                f.add_glyph(key, glyphs[ch]['uv'], glyphs[ch]['met'])
                n_ins += 1

    # ---- alias codepoint ไทยจริง (U+0E01..) ชี้ tile เดียวกับ donor ----
    # ใช้ทดสอบว่าเอนจิ้น route ตัวอักษรไทยตรง ๆ ได้ไหม โดยไม่กินพื้นที่ atlas เพิ่ม
    n_alias = 0
    if ALIAS_THAI:
        for ch in THAI_CHARS:
            key = cp_pack(ch)
            if key in f.cps:
                continue
            assert not f.tail.strip(b'\x00'),                 f'alias ไม่ปลอดภัย: {name} มี tail จริง ({len(f.tail)}B)'
            f.add_glyph(key, glyphs[ch]['uv'], glyphs[ch]['met'])
            n_alias += 1
        print(f'  alias codepoint ไทยจริง {n_alias} ตัว')

    # ---- เขียน ----
    out_bin = out_dir / (name + '.bin')
    out_dds = out_dir / (name + '.dds')
    if grown:
        # aux[0x28] = ความสูง atlas DDS (ยืนยัน 18 ส.ค. 2026: ตรง DDS height ในฟอนต์ต้นฉบับ IW ทั้ง 69 ไฟล์)
        # --grow เปลี่ยน DDS height แล้วต้องอัปเดตช่องนี้ด้วย ไม่งั้นเอนจิ้นยังคิดว่า atlas สูงเท่าเดิม
        aux = bytearray(f.aux); struct.pack_into('<I', aux, 0x28, ah); f.aux = bytes(aux)
    built = f.build()
    open(out_bin, 'wb').write(built)
    if grown:
        dds = bytearray(bytes(dds[:128]) + atlas.tobytes())
    else:
        dds[128:128 + aw * ah] = atlas.tobytes()
    open(out_dds, 'wb').write(dds)
    print(f'  เขียน {out_bin.name} ({len(built)} B, repoint {n_re} + insert {n_ins} + alias {n_alias}) และ {out_dds.name}')

    # ---- ตรวจกลับ ----
    f2 = Font(str(out_bin))
    n0 = len(Font(str(src_bin)).cps)
    assert len(f2.cps) == n0 + n_ins + n_alias
    if grown:
        hdr_new, hdr_old = open(out_dds, 'rb').read(128), open(src_dds, 'rb').read(128)
        assert hdr_new[:12] == hdr_old[:12] and hdr_new[16:] == hdr_old[16:]   # ต่างแค่ height
        assert len(open(out_dds, 'rb').read()) == 128 + aw * ah
    else:
        assert open(out_dds, 'rb').read(128) == open(src_dds, 'rb').read(128)
    make_preview(f2, atlas, aw, ah, out_dir / f'preview_{name}.png', ttf, em_per_px, slope, pad_px)
    return True


# ================= preview =================
def make_preview(f, atlas, aw, ah, out_png, ttf, em_per_px, slope, pad_px):
    def _alpha(tile):
        return np.clip((tile.astype(np.float32) - 127.5) / slope + 0.5, 0, 1)

    idx = {cp_unpack(cp): i for i, cp in enumerate(f.cps) if cp_unpack(cp)}
    lab = ImageFont.truetype(str(ttf), 20)
    sample = 'อัปเกรดความสามารถ เพิ่มพลังชีวิตสูงสุด น้ำใจที่เกาะริช ปั้นปึ้ก'
    enc = encode(sample)
    P_EM = pad_px * em_per_px
    pen = 0.0; parts = []
    for c in enc:
        if c == ' ':
            pen += 300 * em_per_px / 12.5; continue
        i = idx.get(c)
        if i is None:
            pen += 300; continue
        bx, yb, xmax, yt, adv = f.met[i]
        u0, v0, u1, v1 = f.uv[i]
        x0, y0 = int(round(u0 * aw)), int(round(v0 * ah))
        x1, y1 = int(round(u1 * aw)), int(round(v1 * ah))
        tile = _alpha(atlas[y0:y1, x0:x1])
        parts.append((pen + bx - P_EM, yt + P_EM, tile))
        pen += adv
    top = max(p[1] for p in parts); bot = min(p[1] - p[2].shape[0] * em_per_px for p in parts)
    lw = int((pen + 200) / em_per_px) + 20
    lh = int((top - bot) / em_per_px) + 20
    line = np.zeros((lh, lw), np.float32)
    for x_em, ytop_em, tile in parts:
        px = int(round(x_em / em_per_px)) + 10
        py = int(round((top - ytop_em) / em_per_px)) + 10
        h, w = tile.shape
        if px < 0: tile = tile[:, -px:]; w = tile.shape[1]; px = 0
        sub = line[py:py + h, px:px + w]
        np.maximum(sub, tile[:sub.shape[0], :sub.shape[1]], out=sub)
    scale = max(1, int(round(56 / lh)))
    img = Image.fromarray((line * 255).astype(np.uint8)).resize((lw * scale, lh * scale), Image.LANCZOS)
    W = max(img.width + 20, 900)
    grid = Image.new('L', (W, img.height + 60), 20)
    ImageDraw.Draw(grid).text((10, 8), f'{out_png.stem}: {sample}', font=lab, fill=255)
    grid.paste(img, (10, 44))
    grid.save(out_png)
    print(f'  เขียน {out_png.name}')


GROW = '--grow' in sys.argv

if __name__ == '__main__':
    names = [a for a in sys.argv[1:] if not a.startswith('--')] or ['metaoffcpro-condbook']
    for n in names:
        inject_font(n)
