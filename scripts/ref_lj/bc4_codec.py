#!/usr/bin/env python3
"""BC4_UNORM (ATI1/3Dc single-channel) decoder + encoder — pure numpy, no external
BC4 library. ต้องใช้เพราะ gothic.dds ของ Y6 เป็น BC4U 1-channel (ยืนยันจาก DDS header:
fourCC=b'BC4U', pf_flags=0x4, legacy 128-byte header ไม่มี DX10 extension — ดู
docs/font_y6_slotmap.md หัวข้อ DDS header)

สเปก BC4 block (8 bytes ต่อ 4x4 texel):
  byte0 = red0 (u8), byte1 = red1 (u8)
  byte2..7 = 48 บิต ดัชนี 3-bit x 16 texel (little-endian bit-packed ต่อเนื่อง 6 ไบต์
             เป็นสอง chunk 24-bit: texel 0-7 ใน 3 ไบต์แรก, texel 8-15 ใน 3 ไบต์หลัง —
             มาตรฐาน DirectX BC4/BC3-alpha)
  ถ้า red0 > red1: 8-value interpolation (c0=red0, c1=red1, c2..c7 = lerp 1/7 step)
  ถ้า red0 <= red1: 6-value interpolation + c6=0, c7=255 (4/5 step)

ยืนยันด้วย known-answer test ก่อนใช้งานจริงเสมอ (ดู scripts/test_y6_font_inject.py):
  decode ต้นฉบับ gothic.dds แล้ว render บริเวณ cell ของ glyph ที่รู้จัก (เช่น 'A','H')
  ต้องเห็นรูปตัวอักษรจริง ไม่ใช่ noise — เทียบผลกับ known-shape ก่อน trust decoder
"""
import numpy as np


def _block_palettes(red0, red1):
    """red0,red1: uint16 array (nblocks,) -> palette (nblocks, 8) uint8"""
    n = red0.shape[0]
    pal = np.zeros((n, 8), dtype=np.float32)
    r0 = red0.astype(np.float32)
    r1 = red1.astype(np.float32)
    pal[:, 0] = r0
    pal[:, 1] = r1
    mode8 = red0 > red1
    # 8-value mode: c(i) = ((7-i)*r0 + i*r1) / 7  for i=1..6
    for i in range(1, 7):
        v8 = ((7 - i) * r0 + i * r1) / 7.0
        v6 = ((5 - i) * r0 + i * r1) / 5.0 if i <= 5 else np.zeros(n, dtype=np.float32)
        pal[:, 1 + i] = np.where(mode8, v8, v6)
    pal[:, 6] = np.where(mode8, pal[:, 6], 0.0)
    pal[:, 7] = np.where(mode8, pal[:, 7], 255.0)
    return np.clip(np.rint(pal), 0, 255).astype(np.uint8)


def _unpack_indices(idx_bytes):
    """idx_bytes: (nblocks, 6) uint8 -> (nblocks, 16) uint8 in [0,7]
    48-bit value (LE across 6 bytes) split into 16 x 3-bit fields, LSB-first."""
    n = idx_bytes.shape[0]
    bits = np.zeros(n, dtype=np.uint64)
    for b in range(6):
        bits |= idx_bytes[:, b].astype(np.uint64) << np.uint64(8 * b)
    out = np.zeros((n, 16), dtype=np.uint8)
    for t in range(16):
        out[:, t] = ((bits >> np.uint64(3 * t)) & np.uint64(7)).astype(np.uint8)
    return out


def decode_bc4(data, width, height):
    """data: bytes (payload only, no DDS header). -> np.uint8 array (height, width)"""
    assert width % 4 == 0 and height % 4 == 0, "BC4 ต้องมีขนาดหารด้วย 4 ลงตัว"
    bw, bh = width // 4, height // 4
    nblocks = bw * bh
    assert len(data) == nblocks * 8, f"payload {len(data)}B ไม่ตรง {nblocks} blocks x 8B"
    arr = np.frombuffer(data, dtype=np.uint8).reshape(nblocks, 8)
    red0 = arr[:, 0]
    red1 = arr[:, 1]
    idx = _unpack_indices(arr[:, 2:8])          # (nblocks, 16)
    pal = _block_palettes(red0, red1)            # (nblocks, 8)
    texels = np.take_along_axis(pal, idx, axis=1)  # (nblocks, 16)
    # block order in file: row-major blocks (by_col fastest), each block's 16 texels
    # row-major within block: texel t -> (row=t//4, col=t%4)
    texels = texels.reshape(bh, bw, 4, 4)  # (block_row, block_col, in_row, in_col)
    return texels.transpose(0, 2, 1, 3).reshape(height, width)


def _encode_block(px4x4):
    """px4x4: (16,) uint8 texel values for one 4x4 block -> 8 bytes BC4 block
    ใช้ 8-value interpolation mode เสมอ (red0=max, red1=min) — ความเรียบง่ายที่ยอมรับได้
    สำหรับ alpha/SDF mask ตามที่ระบุใน ASSIGNMENT (ไม่ต้องหา endpoint ที่เหมาะสุด)"""
    lo = int(px4x4.min())
    hi = int(px4x4.max())
    if hi == lo:
        # บล็อกสีเดียว (เช่น พื้นว่างทั้งหมด) -> red0=red1=hi, index ไม่สำคัญ (ทุก index ให้ค่าเดียวกันไม่ได้
        # จริงจัง เพราะ mode 6-value ทำให้ c6=0,c7=255 ผิดถ้า idx สุ่มไปโดน 6/7 — บังคับ red0>red1
        # เสมอด้วยการหลอกค่า lo ลง 1 ถ้าเป็นไปได้ เพื่อการันตี mode 8-value คงที่)
        red0, red1 = hi, (hi - 1 if hi > 0 else 0)
        idx = np.zeros(16, dtype=np.uint8)  # ทุก texel = red0 (index0)
    else:
        red0, red1 = hi, lo  # red0>red1 -> 8-value interpolation mode
        # ‼ palette ต้องเรียงตาม convention BC4 เป๊ะเหมือน decoder (_block_palettes):
        # idx0=red0, idx1=red1, idx2..7 = ((7-i)*r0 + i*r1)/7 for i=1..6
        # (เดิมใช้ linear ramp idx0=max..idx7=min = ผิด convention → 0 ถูก decode เป็น 36
        #  = กรอบสี่เหลี่ยมรอบ glyph บนซับที่มี shader ขอบ)
        r0, r1 = float(red0), float(red1)
        levels = np.array([r0, r1] + [((7 - i) * r0 + i * r1) / 7.0 for i in range(1, 7)])
        # หา index ที่ใกล้ค่าจริงที่สุดต่อ texel
        diffs = np.abs(px4x4.astype(np.float32)[:, None] - levels[None, :])
        idx = np.argmin(diffs, axis=1).astype(np.uint8)
    # pack 16x3-bit -> 6 bytes (LSB-first ต่อเนื่อง เหมือนตอน decode)
    bits = np.uint64(0)
    for t in range(16):
        bits |= np.uint64(idx[t]) << np.uint64(3 * t)
    idx_bytes = bytes((bits >> np.uint64(8 * b)) & np.uint64(0xFF) for b in range(6))
    return bytes([red0 & 0xFF, red1 & 0xFF]) + idx_bytes


def encode_bc4(img):
    """img: np.uint8 array (height, width) -> bytes payload BC4U
    เข้ารหัสแบบ block-max/min + nearest-index 8-value interpolation (คุณภาพยอมรับได้
    สำหรับ alpha mask ตาม ASSIGNMENT — ไม่ใช่ optimal encoder แต่ deterministic + ตรวจสอบได้)
    หมายเหตุ: เข้ารหัสทั้งภาพ ช้า (loop python ต่อ block) — ใช้ตอน self-test เล็กๆ เท่านั้น
    งานจริง (inject_thai_y6.py) ใช้ encode_bc4_blocks แบบ patch เฉพาะ block ที่เปลี่ยน แทน"""
    h, w = img.shape
    assert h % 4 == 0 and w % 4 == 0
    bh, bw = h // 4, w // 4
    out = bytearray(bh * bw * 8)
    blocks = img.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(bh * bw, 16)
    for i in range(bh * bw):
        off = i * 8
        out[off:off + 8] = _encode_block(blocks[i])
    return bytes(out)


def encode_bc4_blocks(payload, width, atlas, changed_block_coords):
    """แก้ payload (bytes เดิมทั้งก้อน) เฉพาะ block (by,bx) ที่อยู่ใน changed_block_coords
    (set ของ tuple (by,bx)) โดยเข้ารหัสใหม่จาก atlas (pixel เต็ม หลังเขียน glyph ไทยแล้ว)
    คืน bytes ก้อนใหม่ — block อื่นที่ไม่อยู่ใน set นี้จะเป็น byte เดิมทุกประการ (รับประกัน
    "untouched regions bit-identical" ตาม ASSIGNMENT โดยโครงสร้าง ไม่ต้องเทียบทีหลัง)"""
    bw_total = width // 4
    out = bytearray(payload)
    for by, bx in sorted(changed_block_coords):
        block_idx = by * bw_total + bx
        off = block_idx * 8
        px4x4 = atlas[by * 4:by * 4 + 4, bx * 4:bx * 4 + 4].reshape(16)
        out[off:off + 8] = _encode_block(px4x4)
    return bytes(out)


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    # self-test เล็ก: encode->decode round-trip บนภาพสังเคราะห์ (gradient + blocks สีเดียว)
    rng = np.random.default_rng(0)
    test = rng.integers(0, 256, size=(16, 16), dtype=np.uint8)
    test[0:4, 0:4] = 200  # บล็อกสีเดียว (constant) — เคส edge case
    enc = encode_bc4(test)
    dec = decode_bc4(enc, 16, 16)
    err = np.abs(test.astype(int) - dec.astype(int))
    print(f"self-test synth 16x16: max err={err.max()} mean err={err.mean():.2f} "
          f"(BC4 lossy คาดหวัง error ไม่เป็น 0 แต่ควรเล็ก ยกเว้นบล็อกที่ variance สูงมาก)")
