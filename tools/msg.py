#!/usr/bin/env python3
"""ตัวอ่าน/ประกอบไฟล์ .msg ของ Like a Dragon: Ishin!

.msg คือฟอร์แมตข้อความของ RGG เอง (สาย Old Engine) ที่ Ishin! รีเมคยกมาใช้ทั้งชุด
แล้วห่อไว้ในไฟล์ pak ของ UE4 อีกที — ไม่ใช่ ARMP ของ Dragon Engine และไม่ใช่ .locres ของ UE

## โครงไฟล์ (แกะครบแล้ว · ตรวจกับคลัง EN 1,678 ไฟล์ / 54,318 บรรทัด ตรง 100%)

ทุกค่าเป็น big-endian

```
0x00  uint32   header[0]  ไบต์แรกเป็น 0x20 เสมอ · ไบต์ที่ 4 เป็นเลขรุ่นย่อย (พบ 01-05)
0x04  uint32   header[1]  พบ 0x18 เสมอ
0x08  uint32   header[2]
0x0c  uint32   header[3]  **16 บิตล่าง = จำนวน label** (16 บิตบนเป็นค่าอื่น)
0x10  uint32   header[4]  ตำแหน่งตารางพอยเตอร์ของ label
0x14  uint32   header[5]  ตำแหน่งท้ายบล็อก label
0x18  uint32   header[6]
0x1c  uint32   header[7]  ตำแหน่งตาราง entry
```

ตาราง entry — แถวละ **12 ไบต์**:
```
uint16  ความยาวสตริงเป็นไบต์ (ไม่นับ NUL)
uint16  จำนวนคำสั่ง << 8   → (ค่า >> 8) * 16 = ขนาดบล็อกคำสั่งพอดีทุกไฟล์
uint32  ตำแหน่งสตริง (UTF-8 ปิดท้าย NUL)
uint32  ตำแหน่งบล็อกคำสั่ง
```
จำนวนแถว = (ตำแหน่งบล็อกคำสั่งของแถวแรก − ตำแหน่งตาราง entry) / 12

บล็อกคำสั่ง — คำสั่งละ 16 ไบต์ ไบต์แรกคือ opcode (พบแค่ 3 ค่า):
```
0x01  หัว/ท้ายบรรทัด   byte[1]=0 คือเริ่ม · 1 คือจบ · byte[7] = ตำแหน่งตัวอักษร
0x02  คำสั่งกลางข้อความ byte[7] = ตำแหน่งตัวอักษรที่คำสั่งมีผล
0x03  อ้างถึง label      byte[1] = ชนิดย่อย · byte[3] = **ดัชนีใน label**
```

ตาราง label เก็บของปนกันสามแบบ: ชื่อตัวละคร (`Otose`) · ชื่อคิวเสียงที่ **ฝังชื่อผู้พูดไว้ข้างหน้า**
(`otose_adv_c02_150_001`) · ชื่อท่าทาง/ฉาก (`Idle`, `Talk_Yes`, `TLK_SCN001`)

### ชนิดย่อยของ 0x03 — `byte[1] == 0x35` คือคำสั่ง "เล่นเสียงของบรรทัดนี้"
(แกะได้ 1 ก.ย. 2026 · ยืนยันกับคลัง EN ทั้ง 1,678 ไฟล์)

คำสั่ง 0x03 หนึ่งบรรทัดมีได้หลายตัว เพราะมันถูกใช้อ้างถึง label ทุกชนิด — รวม
**ตัวเลือกในเมนูสนทนา** (`ไปร้านตีเหล็ก`) ที่ค้างอยู่กับทุกบรรทัดในบล็อกเดียวกัน
ถ้าเอา label ตัวแรกที่หน้าตาเหมือนคิวเสียงมาใช้ จะได้ผู้พูดผิดทันที
(เคสจริง: บรรทัดรำพึงของเรียวมะพก `haruka_door_s02_004` ติดมาด้วย → ตัดสินฮารุกะเป็นชายทั้งที่เป็นหญิง)

ตัวชี้ขาดคือชนิดย่อย `0x35` ซึ่งวัดแล้วมี **อย่างมากหนึ่งตัวต่อบรรทัด** (4,113 บรรทัดมีหนึ่งตัว ·
50,205 บรรทัดไม่มีเลย · ไม่มีบรรทัดไหนมีสองตัว) และ label ที่มันชี้เป็น
ชื่อคิวเสียงโรมาจิ 3,989 ครั้ง หรือ **ชื่อผู้พูดบนจอตรง ๆ** (`Ryoma` · `Otose` · `Gate Guard`) อีก 124 ครั้ง
→ `Line.speaker_label()` คืนค่าตัวนี้ตัวเดียว ใช้เป็นหลักฐานผู้พูดรายบรรทัดได้

ชนิดย่อยอื่นที่พบบ่อย (0x1f 56,304 · 0x29 15,618 · 0x09 11,653 · 0x16 6,217) ส่วนใหญ่ชี้ label
ที่ไม่ใช่คิวเสียง — ยังไม่รู้ความหมายรายตัว และ **ห้ามเอามาใช้เดาผู้พูด**

## เรื่องสำคัญ
สตริงเป็น **UTF-8** อยู่แล้ว → ต่างจาก Dragon Engine ตรงที่ไม่ต้องใช้ donor slot map
(ตัวอักษรไทยเขียนลงไปได้ตรง ๆ) ข้อจำกัดจึงย้ายไปอยู่ที่ฟอนต์ล้วน ๆ
"""
import struct
import sys
from pathlib import Path

MAGIC_BYTE0 = 0x20
HEADER_FIELDS = 8
ENTRY_SIZE = 12
CMD_SIZE = 16

OP_MARKER = 0x01
OP_INLINE = 0x02
OP_VOICE = 0x03
# ชนิดย่อยของ 0x03 ที่แปลว่า "เล่นเสียงของบรรทัดนี้" — ตัวเดียวที่ใช้หาผู้พูดได้
SUB_VOICE_PLAY = 0x35


class Line:
    __slots__ = ("index", "text", "byte_len", "str_off", "meta_off", "cmds")

    def __init__(self, index, text, byte_len, str_off, meta_off, cmds):
        self.index = index
        self.text = text
        self.byte_len = byte_len
        self.str_off = str_off
        self.meta_off = meta_off
        self.cmds = cmds                       # list of bytes ยาว 16

    def label_refs(self, label_count):
        """ดัชนี label ทั้งหมดที่บรรทัดนี้อ้างถึง (คำสั่ง 0x03 ทุกชนิดย่อย)

        ⚠ อย่าใช้หาผู้พูด — ในบล็อกสนทนา label ของ *ตัวเลือกในเมนู* ติดมากับทุกบรรทัด
        ให้ใช้ `speaker_label_ref()` แทน (ดูเหตุผลใน docstring หัวไฟล์)
        """
        out = []
        for c in self.cmds:
            if c[0] == OP_VOICE and c[3] < label_count and c[3] not in out:
                out.append(c[3])
        return out

    def speaker_label_ref(self, label_count):
        """ดัชนี label ของคำสั่ง "เล่นเสียงบรรทัดนี้" (0x03 ชนิดย่อย 0x35) หรือ None

        มีอย่างมากหนึ่งตัวต่อบรรทัดเสมอ — ใช้เป็นหลักฐานผู้พูดรายบรรทัดได้
        """
        for c in self.cmds:
            if c[0] == OP_VOICE and c[1] == SUB_VOICE_PLAY and c[3] < label_count:
                return c[3]
        return None

    def __repr__(self):
        return "<Line %d len=%d cmds=%d>" % (self.index, self.byte_len, len(self.cmds))


def nchars(text):
    """จำนวน "ตัวอักษร" แบบที่เกมนับในบล็อกคำสั่ง — code point ละหนึ่ง · `\\r\\n` นับเป็นหนึ่ง

    พิสูจน์จากไฟล์จริง (3 ก.ย. 2026): คำสั่งปิดบรรทัด `01 01` และ `02 09` เก็บค่าที่ไบต์ [6:8]
    EN 28 ตัว/28 ไบต์ -> 28 · JA 12 ตัว/36 ไบต์ -> 12 · บรรทัดที่มี CRLF หนึ่งคู่ -> len-1
    (2,008/2,130 บรรทัดหลายบรรทัดตรงกับกติกานี้ · ไม่มีชนิดคำสั่งไหนมีค่าเกินจำนวนตัวอักษร)
    """
    return len(text.replace("\r\n", "\n"))


def retime_cmds(cmds, old_text, new_text):
    """คืนบล็อกคำสั่งที่ปรับตำแหน่งตัวอักษรให้เข้ากับข้อความใหม่แล้ว (list ของ bytes 16 ไบต์)

    ทุกคำสั่งเก็บ "ตำแหน่งตัวอักษรในบรรทัด" ที่ไบต์ [6:8] (0 = ไม่ใช้) — ค่าที่เท่ากับความยาวเดิม
    คือจุดจบบรรทัด (เกมแสดง/เล่นเสียงถึงตรงนั้นแล้วหยุด) ค่าที่น้อยกว่าคือจุดกลางบรรทัด
    (จังหวะพิมพ์ · จุดหยุด · ช่วงเน้น) → จุดจบ = ความยาวใหม่ · จุดกลาง = สเกลตามสัดส่วน
    ถ้าไม่ปรับ ข้อความไทยที่ยาวกว่าอังกฤษ (นับเป็นตัวอักษร) จะถูกตัดท้ายบนจอ
    (บั๊กจริง: "ไม่ได้เจอกันนานเลยนะ ซากาโมโตะซัง" 33 ตัว โชว์แค่ 28 ตัวเท่าประโยคอังกฤษ)
    """
    oc, nc = nchars(old_text), nchars(new_text)
    if oc == 0 or nc == oc:
        return list(cmds)
    out = []
    for c in cmds:
        v = (c[6] << 8) | c[7]
        if v == 0:
            out.append(c)
            continue
        nv = nc if v >= oc else max(1, round(v * nc / oc))
        nv = min(nv, 0xFFFF)
        out.append(c[:6] + bytes((nv >> 8, nv & 0xFF)) + c[8:])
    return out


class MsgFile:
    """อ่าน .msg ตามโครงจริง (ไม่ใช่การสแกนสตริงแบบเดา)"""

    def __init__(self, data, name=""):
        self.raw = bytes(data)
        self.name = name
        if not self.raw or self.raw[0] != MAGIC_BYTE0:
            raise ValueError("ไม่ใช่ .msg ที่รู้จัก (head=%s) %s" % (self.raw[:4].hex(), name))
        self.header = list(struct.unpack_from(">%dI" % HEADER_FIELDS, self.raw, 0))
        self.label_count = self.header[3] & 0xFFFF
        self.label_ptr_table = self.header[4]
        self.label_block_end = self.header[5]
        self.entry_table = self.header[7]
        self._read_labels()
        self._read_lines()

    # ---- อ่าน ----
    def _cstr(self, off):
        end = self.raw.find(b"\0", off)
        if end < 0:
            end = len(self.raw)
        return self.raw[off:end].decode("utf-8", "replace"), end

    def _read_labels(self):
        self.labels = []
        self.label_offsets = []
        n, base = self.label_count, self.label_ptr_table
        if n == 0 or base + n * 4 > len(self.raw):
            self.label_count = 0
            return
        for i in range(n):
            off, = struct.unpack_from(">I", self.raw, base + i * 4)
            if off >= len(self.raw):
                self.labels.append("")
                self.label_offsets.append(off)
                continue
            s, _ = self._cstr(off)
            self.labels.append(s)
            self.label_offsets.append(off)

    def _read_lines(self):
        self.lines = []
        et = self.entry_table
        if et + ENTRY_SIZE > len(self.raw):
            return
        _, _, _, first_meta = struct.unpack_from(">HHII", self.raw, et)
        n = (first_meta - et) // ENTRY_SIZE
        if n <= 0 or et + n * ENTRY_SIZE > len(self.raw):
            return
        for k in range(n):
            blen, packed, str_off, meta_off = struct.unpack_from(
                ">HHII", self.raw, et + k * ENTRY_SIZE)
            cmds = []
            for j in range(packed >> 8):
                c = self.raw[meta_off + j * CMD_SIZE: meta_off + (j + 1) * CMD_SIZE]
                if len(c) < CMD_SIZE:
                    break
                cmds.append(c)
            text, _ = self._cstr(str_off)
            self.lines.append(Line(k, text, blen, str_off, meta_off, cmds))

    # ---- ออกเป็นข้อมูลให้ pipeline แปล ----
    def to_records(self):
        stem = Path(self.name).stem or "msg"
        out = []
        for ln in self.lines:
            refs = ln.label_refs(self.label_count)
            sref = ln.speaker_label_ref(self.label_count)
            out.append({
                "key": "%s#%03d" % (stem, ln.index),
                "file": stem,
                "line": ln.index,
                "en": ln.text,
                "labels": [self.labels[i] for i in refs],
                # label ของคำสั่ง "เล่นเสียงบรรทัดนี้" — หลักฐานผู้พูดรายบรรทัด (None ถ้าไม่มีเสียง)
                "voice": self.labels[sref] if sref is not None else None,
            })
        return out

    # ---- ประกอบกลับ ----
    def rebuild(self, replacements, label_replacements=None):
        """สร้าง .msg ใหม่จาก {ดัชนีบรรทัด: สตริงใหม่}

        `label_replacements` = {ข้อความ label เดิม: ข้อความใหม่} (ไม่ส่ง = ไม่แตะ label เลย)
        ตาราง label เก็บชื่อผู้พูด ("Young Woman") และป้ายปุ่มโต้ตอบ ("Pray") ปนกับ
        ไอดีคิวเสียง/ท่าทาง ("P_MOV_stand_ogamu" · "Talk_Yes") — ผู้เรียกต้องกรองเองว่า
        ตัวไหนเป็นข้อความบนจอ ห้ามส่งไอดีเข้ามา (ยังไม่พิสูจน์ว่าเกมไม่ได้ใช้ label เป็นคีย์ค้นหา)

        เขียนบล็อกสตริงใหม่ทั้งก้อนแล้วอัปเดตพอยเตอร์ให้ครบ: `str_off` ของทุกแถว ·
        ตารางพอยเตอร์ของ label · ค่าในส่วนหัวที่เป็นออฟเซ็ตหลังบล็อก
        ทุกอย่างก่อนบล็อกสตริงถูกคัดลอกดิบ ๆ ไม่แตะ

        ด่านตรวจ: `scripts/check_msg_roundtrip.py` — แปลงเปล่า ๆ แล้วต้องได้ไบต์เท่าเดิมทุกไฟล์
        """
        if not self.lines:
            return self.raw

        # ขอบเขตบล็อกสตริง = ตั้งแต่สตริงแรก ไปจนจบ label ตัวสุดท้าย
        str_offs = [ln.str_off for ln in self.lines]
        blob_start = min(str_offs)
        # ⚠ วัดขอบท้ายจากตำแหน่ง NUL จริงในไฟล์ ห้ามใช้ความยาวของสตริงที่ decode แล้ว
        # (ไฟล์ที่มีไบต์ไม่ใช่ UTF-8 จะถูกแทนด้วย U+FFFD ทำให้ความยาวไม่ตรงกับของจริง)
        def _raw_end(off):
            e = self.raw.find(b"\0", off)
            return len(self.raw) if e < 0 else e + 1

        ends = [_raw_end(o) for o in str_offs]
        if self.label_count:
            ends += [_raw_end(o) for o in self.label_offsets if o < len(self.raw)]
        blob_end = max(ends)

        # ⚠ ช่วงนี้ **ไม่ได้มีแต่สตริง** — ตารางพอยเตอร์ของ label (label_count * 4 ไบต์)
        # นอนอยู่กลางช่วงนี้ด้วย (สตริงบรรทัด -> ตารางพอยเตอร์ -> สตริง label)
        # ถ้าเอาไปตัดด้วย NUL ปนกับสตริง ตารางจะเพี้ยน และถ้าเขียนพอยเตอร์กลับที่ตำแหน่งเดิม
        # มันจะไปทับกลางข้อความไทยที่เพิ่งเขียน — บั๊กจริงที่เจอตอนทดสอบในเกม 3 ก.ย. 2026
        # (ข้อความขาดกลางประโยค 1,418 บรรทัดใน 1,017 ไฟล์ · label ฉาก/ท่าทางพังตามไปด้วย)
        lpt_start = self.label_ptr_table
        lpt_size = self.label_count * 4
        lpt_inside = self.label_count > 0 and blob_start <= lpt_start < blob_end

        # เขียนบล็อกใหม่ทีละ "ท่อนคั่นด้วย NUL" ตามลำดับเดิม — ต้องเก็บท่อนที่ไม่มีใครชี้
        # และท่อนว่าง (padding) ไว้ด้วย ไม่งั้นของหายและไฟล์หด (บทเรียนรอบก่อน)
        line_at = {ln.str_off: i for i, ln in enumerate(self.lines)}
        label_at = {}                            # ออฟเซ็ต -> ข้อความ label (หลายดัชนีชี้ที่เดียวกันได้)
        if label_replacements:
            for idx, off in enumerate(self.label_offsets):
                if off < len(self.raw):
                    label_at.setdefault(off, self.labels[idx])
        blob = bytearray()
        remap = {}                               # ออฟเซ็ตเดิม -> ออฟเซ็ตใหม่
        new_lpt = lpt_start
        pos = blob_start
        while pos < blob_end:
            if lpt_inside and pos == lpt_start:      # ยกตารางพอยเตอร์มาทั้งก้อน
                new_lpt = blob_start + len(blob)
                blob += self.raw[lpt_start:lpt_start + lpt_size]
                pos += lpt_size
                continue
            nul = self.raw.find(b"\0", pos)
            if nul < 0 or nul >= blob_end:
                blob += self.raw[pos:blob_end]
                break
            if lpt_inside and pos < lpt_start <= nul:  # ท่อนนี้ชนขอบตาราง -> ตัดแค่ถึงขอบ
                blob += self.raw[pos:lpt_start]
                pos = lpt_start
                continue
            remap[pos] = blob_start + len(blob)
            i = line_at.get(pos)
            lab = label_at.get(pos)
            if i is not None and i in replacements:
                blob += replacements[i].encode("utf-8") + b"\0"
            elif lab is not None and lab in label_replacements:
                blob += label_replacements[lab].encode("utf-8") + b"\0"
            else:
                blob += self.raw[pos:nul] + b"\0"
            pos = nul + 1

        shift = (blob_start + len(blob)) - blob_end
        out = bytearray(self.raw[:blob_start]) + blob + bytearray(self.raw[blob_end:])

        # ⚠ ตารางที่อยู่ **หลัง** บล็อกสตริงจะเลื่อนไปตาม shift ด้วย — ต้องเขียนที่ตำแหน่งใหม่
        # ถ้าเขียนที่ตำแหน่งเดิมจะไปทับกลางบล็อกสตริงที่เพิ่งเขียน ทำให้ข้อความขาดกลางคัน
        # (บั๊กจริงที่เจอในเกม 3 ก.ย. 2026: label_ptr_table อยู่หลังบล็อกสตริงในทุกไฟล์
        #  พอไทยยาวกว่า EN บล็อกก็ขยาย พอยเตอร์ label 4 ไบต์เลยไปทับข้อความไทย 1,418 บรรทัด)
        def _moved(off):
            return off + shift if off >= blob_end else off

        entry_table = _moved(self.entry_table)
        label_ptr_table = new_lpt if lpt_inside else _moved(self.label_ptr_table)

        for i, ln in enumerate(self.lines):
            if ln.str_off not in remap:
                continue
            text = replacements.get(i, ln.text)
            struct.pack_into(">H", out, entry_table + i * ENTRY_SIZE,
                             len(text.encode("utf-8")))
            struct.pack_into(">I", out, entry_table + i * ENTRY_SIZE + 4,
                             remap[ln.str_off])
            # บล็อกคำสั่งที่อยู่หลังบล็อกสตริงก็เลื่อนเหมือนกัน
            if ln.meta_off >= blob_end:
                struct.pack_into(">I", out, entry_table + i * ENTRY_SIZE + 8,
                                 ln.meta_off + shift)

        for i in range(self.label_count):
            o = self.label_offsets[i]
            if o in remap:
                struct.pack_into(">I", out, label_ptr_table + i * 4, remap[o])

        # ---- แผนที่ออฟเซ็ตเดิม -> ใหม่ สำหรับทุกตำแหน่งในไฟล์ ----
        # ของที่อยู่ **ในบล็อก** ต้องเลื่อนตามระยะที่สตริงก่อนหน้ามันขยายไป ไม่ใช่ shift รวม
        points = sorted(remap.items())
        if lpt_inside:
            points = sorted(points + [(lpt_start, new_lpt)])

        def _map(off):
            if off < blob_start:
                return off
            if off >= blob_end:
                return off + shift
            lo, hi = 0, len(points)
            while lo < hi:                       # หาจุดตั้งต้นที่ใกล้สุดซึ่งไม่เกิน off
                mid = (lo + hi) // 2
                if points[mid][0] <= off:
                    lo = mid + 1
                else:
                    hi = mid
            if lo == 0:
                return off
            old, new = points[lo - 1]
            return new + (off - old)

        hdr = list(self.header)
        for i in range(1, HEADER_FIELDS):
            # ⚠ header[3] ไม่ใช่ออฟเซ็ต — 16 บิตล่างคือจำนวน label ห้ามเลื่อนเด็ดขาด
            # (พลาดมาแล้ว: ค่า 0x400fa บังเอิญตกในช่วงไฟล์ เลยโดนบวก shift จนจำนวน label เพี้ยน)
            if i == 3 or hdr[i] == 0:
                continue
            hdr[i] = _map(hdr[i])
        struct.pack_into(">%dI" % HEADER_FIELDS, out, 0, *hdr)

        # ---- ปรับตำแหน่งตัวอักษรในบล็อกคำสั่งของบรรทัดที่แทนที่ (ดู retime_cmds) ----
        # บล็อกคำสั่งไม่ได้อยู่ในบล็อกสตริง จึงถูกคัดลอกดิบ ๆ มา — เขียนทับที่ตำแหน่งใหม่ของมัน
        for i, ln in enumerate(self.lines):
            if i not in replacements or not ln.cmds:
                continue
            new_cmds = retime_cmds(ln.cmds, ln.text, replacements[i])
            if new_cmds == ln.cmds:
                continue
            meta = _map(ln.meta_off)
            for j, c in enumerate(new_cmds):
                out[meta + j * CMD_SIZE: meta + (j + 1) * CMD_SIZE] = c
        return bytes(out)

    def __repr__(self):
        return "<MsgFile %s lines=%d labels=%d>" % (
            self.name or "?", len(self.lines), self.label_count)


def load(path):
    p = Path(path)
    return MsgFile(p.read_bytes(), p.name)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    m = load(sys.argv[1])
    print(m)
    print("header:", [hex(h) for h in m.header])
    print("labels:", m.labels[:12])
    for r in m.to_records()[:10]:
        print("  %s %-28s %s" % (r["key"], r["labels"], r["en"][:50]))
