#!/usr/bin/env python3
"""ตัวอ่าน/ประกอบ `pac_STID_*.bin` ของ Like a Dragon: Ishin! (data/wdr_<lang>/pac/ · 168 ไฟล์ต่อภาษา)

ไฟล์วางวัตถุ/NPC ประจำฉาก — บทพูดลอยของ NPC เดินถนน ("You really saved me last time!") ·
ข้อความตรวจสอบ ("(It's not budging. ...)") · ป้ายชื่อร้าน/ปุ่มพิเศษ ("Pray" · "Recipient")
ฝังอยู่ในนี้ ไม่ได้อยู่ใน .msg/locres

## โครงไฟล์ (พิสูจน์ 13 ก.ย. 2026 · big-endian ทั้งหมด)

ด่านตรวจ `scripts/check_pac_roundtrip.py`: 9 ภาษา × 168 ไฟล์ rebuild ตรงไบต์ 100% และ
แปลง EN -> ภาษาอื่นด้วยการแทนสตริง+บล็อกคำสั่ง ได้ไฟล์ภาษานั้นตรงไบต์ 168/168 ทั้ง 8 ภาษา

```
ไฟล์
0x00  u16  จำนวนเรคคอร์ด N
0x02  u16  0
0x04  u32  8  (ตำแหน่งตาราง)
0x08  N × 16 ไบต์: u32 record id · u32 offA · u32 offB · u16 lenA · u16 lenB
      + ศูนย์ 8 ไบต์
      แล้วต่อด้วย A,B ของแต่ละเรคคอร์ดตามลำดับ (แต่ละส่วน pad ถึง 4 · len=0 -> off=0)
      B = ทุ่น/พิกัด เหมือนกันทุกภาษาเสมอ · A = คอนเทนเนอร์ข้อความ (ข้างล่าง) หรือว่าง
```

ส่วน A = คอนเทนเนอร์ตระกูลเดียวกับ .msg (ออฟเซ็ตทั้งหมดนับจากต้น A):
```
0x00 u8  magic 0x20 หรือ 0x40 · u8 u8 ธง (คัดลอกดิบ) · u8 จำนวนกลุ่ม G
0x04 u32 0x18               ตำแหน่งตารางกลุ่ม
0x08 u32 ตำแหน่งตาราง extra (0 = ไม่มี)
0x0c u16 จำนวน extra · u16 จำนวน label
0x10 u32 ตำแหน่งตารางพอยเตอร์ label (0 = ไม่มี)
0x14 u32 0
0x18 G × 16: u32 data_off (0 = ไม่มี · ชี้เข้าก้อนข้อมูลกลุ่ม) · u32 entry_off · u8[8] ธง
            ธง[1] = จำนวน entry ของกลุ่ม · entry ของกลุ่มเรียงต่อกัน
     entry × 12: u16 ความยาวสตริง (ไบต์) · u16 จำนวนคำสั่ง<<8 · u32 str_off · u32 cmd_off
     บล็อกคำสั่ง  16 ไบต์/คำสั่ง ต่อกันตามลำดับ entry (opcode เดียวกับ .msg · [6:8] = ตำแหน่งตัวอักษร)
     ข้อมูลกลุ่ม  ก้อนดิบ · ข้างในมี **ดัชนี label** (ไม่มีออฟเซ็ต)
     สตริง       UTF-8 ปิด NUL ต่อกันตามลำดับ entry (สตริงว่าง = NUL ตัวเดียว)
     [pad4] ตาราง extra (จำนวน × 16 · float พิกัด)   ┐ เรียงตามออฟเซ็ต
     [pad4] พอยเตอร์ label (u32 ×n) + สตริง label     ┘
     จบด้วยสตริง entry -> lenA รวม pad ถึง 4 · จบด้วย extra/label -> lenA ไม่รวม pad
```
ส่วนหัว + ตารางกลุ่ม + ตาราง entry ขนาดคงที่ → แปลแล้วสิ่งที่ต้องคำนวณใหม่คือ
ความยาว/ออฟเซ็ตสตริง · cmd_off · data_off · ตำแหน่ง extra/label · พอยเตอร์ label · lenA/offA/offB
(ตัวประกอบนี้คำนวณใหม่ทั้งหมดจากเลย์เอาต์ ไม่ได้ปะทีละฟิลด์)

## สตริงสองชนิด
- `line`  สตริงของ entry — มีบล็อกคำสั่ง (ต้อง retime ตำแหน่งตัวอักษรตามคำแปล เหมือน .msg)
- `label` ตาราง label — ปนกันระหว่างไอดี (`Talk_Kamae` · `M_BUS_TLK_...` · `7e008100`) กับ
  ข้อความบนจอ (`Pray` · `Recipient` · `Up for a palanquin ride?`) · แยกด้วยการเทียบภาษา
  (ไอดีเหมือนกันทุกภาษา) — ดู scripts/extract_pac_text.py
- ⚠ ข้อมูลกลุ่มอ้าง label ด้วยดัชนี → **ห้ามเปลี่ยนจำนวน label** (บางภาษารวม label ซ้ำเป็นตัวเดียว
  เช่น KYOTO 006e030f EN มี 2 ตัว JA มี 1 — ผลของการแปลภาษานั้น ไม่ใช่สิ่งที่คำแปลไทยต้องทำ)

## ตำแหน่งตัวอักษรในบล็อกคำสั่ง
หน่วยเดียวกับ .msg (`msg.disp_chars` — ตัวอักษรบนจอ ไม่นับไบต์ · JA 15 ตัว/45 ไบต์ -> 0x0f)
เทียบ 8 ภาษา: จุดจบบรรทัดหลัง `retime_cmds` ตรง **ทุกบรรทัด** · จุดกลางบรรทัดเป็นค่าประมาณ
แต่ละภาษาใส่คำสั่งจังหวะ (`02 09` · `02 0e`) เองไม่เท่ากัน จึงแทนสตริงอย่างเดียวได้ไฟล์ที่ต่างจาก
ต้นฉบับภาษานั้นในบล็อกคำสั่ง — เป็นเรื่องปกติ (ไฟล์ .msg ก็เป็นแบบเดียวกัน)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from msg import retime_cmds, disp_chars          # noqa: E402  ใช้กติกาตำแหน่งตัวอักษรชุดเดียวกับ .msg

MSG_MAGICS = (0x20, 0x40)
FILE_HDR = 8
REC_SIZE = 16
TABLE_GAP = 8          # ศูนย์ 8 ไบต์คั่นระหว่างตารางกับข้อมูลก้อนแรก
MSG_HDR = 0x18
GROUP_SIZE = 16
ENTRY_SIZE = 12
CMD_SIZE = 16
EXTRA_SIZE = 16


def _p4(x):
    return (x + 3) & ~3


class PacFormatError(ValueError):
    pass


def _need(cond, what):
    if not cond:
        raise PacFormatError(what)


def _cstr_end(raw, off, limit):
    e = raw.find(b"\0", off, limit)
    _need(e >= 0, "สตริงไม่มี NUL ปิดท้าย @0x%x" % off)
    return e


class MsgBlock:
    """ส่วน A ของเรคคอร์ด = คอนเทนเนอร์แบบ .msg (อ่านทุกส่วนเป็นชิ้น แล้วประกอบใหม่แบบ canonical)"""

    def __init__(self, raw):
        raw = bytes(raw)
        _need(len(raw) >= MSG_HDR and raw[0] in MSG_MAGICS, "หัว msg ไม่รู้จัก")
        h0, h1, h2, h3, h4, h5 = struct.unpack_from(">6I", raw, 0)
        _need(h1 == MSG_HDR, "h1 != 0x18")
        _need(h5 == 0, "h5 != 0 (0x%x)" % h5)
        self.head3 = raw[0:3]                         # magic + ธงสองไบต์ (คัดลอกดิบ)
        ng = raw[3]
        self.extra_count = h3 >> 16
        self.label_count = h3 & 0xFFFF
        _need((self.extra_count == 0) == (h2 == 0), "h2/extra count ไม่สอดคล้อง")
        _need((self.label_count == 0) == (h4 == 0), "h4/label count ไม่สอดคล้อง")

        et = MSG_HDR + ng * GROUP_SIZE
        groups = [struct.unpack_from(">II8s", raw, MSG_HDR + g * GROUP_SIZE) for g in range(ng)]
        ne = sum(fl[1] for _, _, fl in groups)
        cmd_start = et + ne * ENTRY_SIZE
        _need(cmd_start <= len(raw), "ตาราง entry เกินขอบ")

        # ---- entry: ต้องเรียงต่อกันตามกลุ่ม ----
        acc = 0
        for _, eo, fl in groups:
            _need(eo == et + acc * ENTRY_SIZE, "entry_off ของกลุ่มไม่เรียงต่อกัน")
            acc += fl[1]
        ents = [struct.unpack_from(">HHII", raw, et + k * ENTRY_SIZE) for k in range(ne)]

        # ---- บล็อกคำสั่ง: ต่อกันตามลำดับ entry ----
        pos = cmd_start
        self.cmds = []
        for blen, pk, so, co in ents:
            _need(pk & 0xFF == 0, "ไบต์ล่างของจำนวนคำสั่งไม่เป็น 0")
            n = pk >> 8
            _need(co == pos, "บล็อกคำสั่งไม่ต่อกัน @0x%x (คาด 0x%x)" % (co, pos))
            self.cmds.append([raw[co + j * CMD_SIZE: co + (j + 1) * CMD_SIZE] for j in range(n)])
            pos = co + n * CMD_SIZE
        cmd_end = pos

        # ---- สตริงของ entry: NUL ปิดท้าย ต่อกันตามลำดับ entry ----
        self.lines = []
        if ne:
            s_start = ents[0][2]
            p = s_start
            for blen, pk, so, co in ents:
                _need(so == p, "สตริงไม่ต่อกัน @0x%x (คาด 0x%x)" % (so, p))
                e = _cstr_end(raw, so, len(raw))
                _need(e - so == blen, "ความยาวสตริงในตาราง != ตำแหน่ง NUL")
                self.lines.append(raw[so:e])
                p = e + 1
            s_end = p
        else:
            s_start = s_end = None

        # ---- ข้อมูลกลุ่ม: ช่วงระหว่างท้ายคำสั่งกับสตริงแรก ----
        tail_marks = [x for x in (h2, h4) if x]
        g_end = s_start if ne else (min(tail_marks) if tail_marks else len(raw))
        _need(cmd_end <= g_end, "ข้อมูลกลุ่มติดลบ")
        self.gdata = raw[cmd_end:g_end]
        self.group_flags = []
        self.group_data = []                         # ออฟเซ็ตในก้อน gdata หรือ None
        for do, _, fl in groups:
            self.group_flags.append(fl)
            if do == 0:
                self.group_data.append(None)
            else:
                _need(cmd_end <= do <= g_end, "data_off ของกลุ่มอยู่นอกช่วงข้อมูลกลุ่ม")
                self.group_data.append(do - cmd_end)
        if not ne:
            s_end = g_end

        # ---- ท้ายก้อน: [pad4] [ตาราง extra] [ตารางพอยเตอร์ label + สตริง label] ----
        cur = s_end
        self.extra = b""
        self.order = []
        for off, kind in sorted((o, k) for k, o in (("extra", h2), ("label", h4)) if o):
            _need(off == _p4(cur), "%s ไม่ได้อยู่ที่ pad4 ต่อจากส่วนก่อนหน้า (0x%x vs 0x%x)"
                  % (kind, off, _p4(cur)))
            _need(not any(raw[cur:off]), "padding ก่อน %s ไม่เป็นศูนย์" % kind)
            self.order.append(kind)
            if kind == "extra":
                self.extra = raw[off:off + self.extra_count * EXTRA_SIZE]
                cur = off + self.extra_count * EXTRA_SIZE
            else:
                n = self.label_count
                ptrs = struct.unpack_from(">%dI" % n, raw, off)
                p = off + n * 4
                self.labels = []
                for lp in ptrs:
                    _need(lp == p, "สตริง label ไม่ต่อกัน")
                    e = _cstr_end(raw, lp, len(raw))
                    self.labels.append(raw[lp:e])
                    p = e + 1
                cur = p
        if "label" not in self.order:
            self.labels = []
        # ความยาวรวม: ถ้าจบด้วยสตริง entry จะรวม padding ถึง 4 เสมอ · ถ้าจบด้วย extra/label จะไม่รวม
        # (เป็นกฎตายตัว ไม่ใช่ธงรายเรคคอร์ด — ห้ามจำจากต้นฉบับ เพราะความยาวที่หารสี่ลงตัว
        #  โดยบังเอิญแยกไม่ออกจาก "ไม่ pad" แล้วพอสตริงเปลี่ยนจะได้ขนาดผิด · พิสูจน์ด้วย oracle ข้ามภาษา)
        end = cur if self.order else _p4(cur)
        _need(end == len(raw), "ท้ายก้อนไม่ตรง (0x%x vs 0x%x)" % (end, len(raw)))
        _need(not any(raw[cur:]), "padding ท้ายไม่เป็นศูนย์")
        self.ng = ng

    # ---- ประกอบกลับ ----
    def build(self, lines=None, cmds=None, labels=None, gdata=None):
        """คืนไบต์ของส่วน A จากชิ้นส่วน (list ของ bytes) — ไม่ส่ง = ใช้ของเดิม

        ทุกออฟเซ็ตคำนวณใหม่จากเลย์เอาต์: ส่วนหัว/กลุ่ม/ตาราง entry ขนาดคงที่ (ไม่เลื่อน)
        ส่วนที่เลื่อนได้ = บล็อกคำสั่ง → ข้อมูลกลุ่ม → สตริง → extra → label

        `gdata` (ก้อนข้อมูลกลุ่มทั้งก้อน) มีไว้ให้ด่านตรวจข้ามภาษาเท่านั้น: ข้อมูลกลุ่มเก็บ
        **ดัชนี label** อยู่ข้างใน ภาษาที่รวม label ซ้ำเป็นตัวเดียวจึงมีจำนวน label ต่างจาก EN
        — เปลี่ยนจำนวน label ได้ก็ต่อเมื่อส่ง gdata ที่อ้างดัชนีชุดใหม่มาด้วย (งานแปลห้ามใช้)
        """
        lines = self.lines if lines is None else lines
        cmds = self.cmds if cmds is None else cmds
        labels = self.labels if labels is None else labels
        _need(len(lines) == len(self.lines) and len(cmds) == len(self.cmds),
              "จำนวนบรรทัด/บล็อกคำสั่งไม่ตรงของเดิม")
        _need(gdata is not None or len(labels) == len(self.labels),
              "จำนวน label เปลี่ยนไม่ได้ (ข้อมูลกลุ่มอ้างดัชนี label)")
        _need(bool(labels) == bool(self.labels), "เพิ่ม/ลบตาราง label ทั้งตารางไม่รองรับ")
        gdata = self.gdata if gdata is None else gdata
        _need(len(gdata) == len(self.gdata), "ขนาดข้อมูลกลุ่มต้องเท่าเดิม (ออฟเซ็ตกลุ่มอ้างถึงข้างใน)")
        ng, ne = self.ng, len(self.lines)
        et = MSG_HDR + ng * GROUP_SIZE
        pos = et + ne * ENTRY_SIZE
        cmd_offs = []
        for c in cmds:
            cmd_offs.append(pos)
            pos += len(c) * CMD_SIZE
        cmd_end = pos
        pos += len(gdata)
        str_offs = []
        for s in lines:
            _need(b"\0" not in s, "สตริงมี NUL ข้างใน")
            str_offs.append(pos)
            pos += len(s) + 1
        cur = pos
        h2 = h4 = 0
        tail = bytearray()
        for kind in self.order:
            off = _p4(cur)
            tail += b"\0" * (off - cur)
            if kind == "extra":
                h2 = off
                tail += self.extra
                cur = off + len(self.extra)
            else:
                h4 = off
                p = off + len(labels) * 4
                ptrs = []
                for s in labels:
                    _need(b"\0" not in s, "label มี NUL ข้างใน")
                    ptrs.append(p)
                    p += len(s) + 1
                tail += struct.pack(">%dI" % len(ptrs), *ptrs)
                for s in labels:
                    tail += s + b"\0"
                cur = p
        if not self.order:
            tail += b"\0" * (_p4(cur) - cur)

        out = bytearray()
        out += self.head3 + bytes((ng,))
        out += struct.pack(">5I", MSG_HDR, h2, (self.extra_count << 16) | len(labels), h4, 0)
        acc = 0
        for g in range(ng):
            rel = self.group_data[g]
            fl = self.group_flags[g]
            out += struct.pack(">II8s", 0 if rel is None else cmd_end + rel,
                               et + acc * ENTRY_SIZE, fl)
            acc += fl[1]
        for k in range(ne):
            out += struct.pack(">HHII", len(lines[k]), len(cmds[k]) << 8, str_offs[k], cmd_offs[k])
        for c in cmds:
            for one in c:
                _need(len(one) == CMD_SIZE, "คำสั่งต้องยาว 16 ไบต์")
                out += one
        out += gdata
        for s in lines:
            out += s + b"\0"
        out += tail
        return bytes(out)


def _dec(b):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("utf-8", "replace")


class Record:
    __slots__ = ("rid", "a", "b", "msg", "error")

    def __init__(self, rid, a, b):
        self.rid, self.a, self.b = rid, a, b
        self.msg, self.error = None, None
        if a:
            try:
                self.msg = MsgBlock(a)
            except PacFormatError as e:
                self.error = str(e)


class PacFile:
    """ไฟล์ pac_STID_*.bin ทั้งไฟล์: ตารางเรคคอร์ด + (A, B) ต่อเรคคอร์ด"""

    def __init__(self, data, name=""):
        d = bytes(data)
        self.raw = d
        self.name = name
        self.stem = Path(name).stem if name else "pac"
        _need(len(d) >= FILE_HDR, "ไฟล์สั้นเกิน")
        cnt, zero, tstart = struct.unpack_from(">HHI", d, 0)
        _need(zero == 0 and tstart == FILE_HDR, "ส่วนหัวไฟล์ไม่รู้จัก (%s)" % d[:8].hex())
        tend = FILE_HDR + cnt * REC_SIZE
        _need(not any(d[tend:tend + TABLE_GAP]), "ช่องว่างหลังตารางไม่เป็นศูนย์")
        pos = tend + TABLE_GAP
        self.records = []
        for i in range(cnt):
            rid, oa, ob, la, lb = struct.unpack_from(">IIIHH", d, FILE_HDR + i * REC_SIZE)
            for off, ln, tag in ((oa, la, "A"), (ob, lb, "B")):
                if ln == 0:
                    _need(off == 0, "เรคคอร์ด %d ส่วน %s ยาว 0 แต่ออฟเซ็ตไม่เป็น 0" % (i, tag))
                    continue
                _need(off == pos, "เรคคอร์ด %d ส่วน %s ไม่ต่อกัน (0x%x vs 0x%x)" % (i, tag, off, pos))
                end = off + ln
                _need(not any(d[end:_p4(end)]), "padding หลังส่วน %s ไม่เป็นศูนย์" % tag)
                pos = _p4(end)
            self.records.append(Record(rid, d[oa:oa + la], d[ob:ob + lb]))
        _need(pos == len(d), "ขนาดไฟล์ไม่ตรงผลรวมเรคคอร์ด (0x%x vs 0x%x)" % (pos, len(d)))
        ids = [r.rid for r in self.records]
        _need(len(set(ids)) == len(ids), "record id ซ้ำในไฟล์")
        self.by_rid = {r.rid: r for r in self.records}

    @property
    def errors(self):
        return [(r.rid, r.error) for r in self.records if r.error]

    # ---- รายการสตริง ----
    def key(self, rid, kind, index):
        return "%s#%08x#%s%d" % (self.stem, rid, "L" if kind == "label" else "", index)

    def strings(self):
        """ทุกสตริงในไฟล์: บรรทัด (entry) และ label — dict ที่มี key/record/kind/index/raw/text"""
        out = []
        for r in self.records:
            if not r.msg:
                continue
            for kind, seq in (("line", r.msg.lines), ("label", r.msg.labels)):
                for i, s in enumerate(seq):
                    out.append({"key": self.key(r.rid, kind, i), "record": r.rid, "kind": kind,
                                "index": i, "raw": s, "text": _dec(s),
                                "ncmds": len(r.msg.cmds[i]) if kind == "line" else 0})
        return out

    # ---- ประกอบกลับ ----
    def rebuild(self, replacements=None, cmd_replacements=None, retime=True):
        """คืนไบต์ไฟล์ใหม่

        replacements      {key: str} — ข้อความใหม่ (บรรทัดหรือ label)
        cmd_replacements  {key: [bytes16, ...]} — แทนบล็อกคำสั่งของบรรทัดทั้งชุด (ใช้ในด่านตรวจ)
        retime            ปรับตำแหน่งตัวอักษรในบล็อกคำสั่งตาม msg.retime_cmds (ข้ามถ้าส่ง cmd แทนแล้ว)
        """
        replacements = replacements or {}
        cmd_replacements = cmd_replacements or {}
        known = set()
        body = []
        for r in self.records:
            a = r.a
            if r.msg:
                m = r.msg
                lines, cmds, labels = list(m.lines), list(m.cmds), list(m.labels)
                touched = False
                for i in range(len(lines)):
                    k = self.key(r.rid, "line", i)
                    known.add(k)
                    if k in cmd_replacements:
                        cmds[i] = list(cmd_replacements[k])
                        touched = True
                    if k in replacements:
                        new = replacements[k].encode("utf-8")
                        if new != lines[i]:
                            if retime and k not in cmd_replacements:
                                cmds[i] = retime_cmds(cmds[i], _dec(lines[i]), replacements[k])
                            lines[i] = new
                            touched = True
                for i in range(len(labels)):
                    k = self.key(r.rid, "label", i)
                    known.add(k)
                    if k in replacements:
                        new = replacements[k].encode("utf-8")
                        if new != labels[i]:
                            labels[i] = new
                            touched = True
                a = m.build(lines, cmds, labels) if touched else m.build()
            body.append((r.rid, a, r.b))
        unknown = (set(replacements) | set(cmd_replacements)) - known
        _need(not unknown, "คีย์ไม่มีในไฟล์: %s" % sorted(unknown)[:5])
        return self.assemble(body)

    @staticmethod
    def assemble(body):
        """ประกอบไฟล์จาก [(record id, ไบต์ A, ไบต์ B)] ตามลำดับ — เขียนตารางและออฟเซ็ตใหม่ทั้งหมด"""
        cnt = len(body)
        table = bytearray(struct.pack(">HHI", cnt, 0, FILE_HDR))
        data = bytearray()
        base = FILE_HDR + cnt * REC_SIZE + TABLE_GAP
        for rid, a, b in body:
            _need(len(a) <= 0xFFFF and len(b) <= 0xFFFF, "ส่วนยาวเกิน u16 (record %08x)" % rid)
            oa = base + len(data) if a else 0
            data += a + b"\0" * (_p4(len(a)) - len(a))
            ob = base + len(data) if b else 0
            data += b + b"\0" * (_p4(len(b)) - len(b))
            table += struct.pack(">IIIHH", rid, oa, ob, len(a), len(b))
        return bytes(table) + b"\0" * TABLE_GAP + bytes(data)

    def __repr__(self):
        return "<PacFile %s records=%d strings=%d errors=%d>" % (
            self.name or "?", len(self.records), len(self.strings()), len(self.errors))


def load(path):
    p = Path(path)
    return PacFile(p.read_bytes(), p.name)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    pf = load(sys.argv[1])
    print(pf)
    for s in pf.strings():
        if s["raw"]:
            print("  %-40s %-5s %s" % (s["key"], s["kind"], s["text"][:70]))
