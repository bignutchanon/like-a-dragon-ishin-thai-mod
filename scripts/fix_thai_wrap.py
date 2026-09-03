#!/usr/bin/env python3
r"""แทรกช่องว่างที่ "ขอบคำ" ในข้อความไทยยาว เพื่อให้เอนจิ้นตัดบรรทัดได้

พอร์ตจาก `D:\Projects\y8-infinite-wealth\scripts\fix_thai_wrap.py` เมื่อ 29 ส.ค. 2026
เจออาการจริงในเกม LJ วันเดียวกัน — แผงคำอธิบายทักษะในหน้า Skill Tree (`player_skill.bin`)
กล่องกว้างราว 40 หน่วย แต่เกณฑ์ที่ประมาณจาก p99 ให้ 60 → ดู BIN_CAP และ docs/ISSUES.md LJ-010

ปัญหา (เจอในเกมจริงของ Y8 30 ก.ค. 2026 — หน้าประวัติตัวละคร):
  เอนจิ้น Dragon Engine ตัดบรรทัดที่ **ช่องว่าง** เท่านั้น · ภาษาไทยไม่มีช่องว่างระหว่างคำ
  → ทั้งประโยคนับเป็น "คำเดียว" ยาวเกินกล่อง → เอนจิ้นตัดทีละตัวอักษร **เรียงเป็นแนวตั้ง**
  (ในภาพ: สองบรรทัดแรกที่ผู้แปลใส่ช่องว่างไว้เรียงปกติ ส่วนที่ไม่มีช่องว่างพังทั้งท่อน)
  v1.2 ก็มีปัญหานี้ 4,363 รายการ = ปัญหาเก่าที่ไม่มีใครแก้ ไม่ใช่ของใหม่

วิธีแก้: ตัดคำไทยด้วย pythainlp (newmm) แล้วแทรกช่องว่าง **ที่ขอบคำเท่านั้น**
ให้ทุกช่วงอักษรไทยติดกันไม่เกิน MAX_RUN ตัว → เอนจิ้นมีจุดตัดบรรทัดให้ใช้
- **ไม่แทรกกลางคำ** (ตัดคำผิด = อ่านไม่รู้เรื่อง) · ไม่แตะแท็ก/`${...}`/`\\n` (เป็น ASCII อยู่นอกช่วงไทย)
- จำนวน `\\n` และแท็กไม่เปลี่ยน → ผ่าน QC ข้อ N/T/S/X เหมือนเดิม

MAX_RUN มาจากการวัดกล่องแคบสุดที่เจอ (หน้าประวัติตัวละคร ~45 ตัวอักษรไทย/บรรทัด)
ตั้ง 32 เผื่อไว้ เพราะฟอนต์เป็น proportional ความกว้างต่อตัวไม่เท่ากัน

ใช้:
  python scripts/fix_thai_wrap.py --check          # ดูตัวอย่างผลลัพธ์ ไม่เขียนไฟล์
  python scripts/fix_thai_wrap.py                  # แก้ที่ translations/done/ ต้นทาง
  python scripts/fix_thai_wrap.py --max-run 28     # เข้มขึ้น (กล่องแคบกว่า)
แล้วต่อด้วย merge_qc.py + build_text.py + deploy_title_poc.srmm_and_mods()
"""
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths as PP
from pythainlp.corpus.common import thai_words
from pythainlp.tokenize import Tokenizer
from pythainlp.util import dict_trie

THAI_RUN = re.compile(r"[฀-๿]+")
# วัดจากกล่องแคบสุดที่เจอในเกม (หน้าประวัติตัวละคร): บรรทัด "อดีตหัวหน้าตระกูลชิงากิ
# หลังตระกูลโทโจล่มสลาย" = 44 ตัวอักษร พอดีบรรทัด → ช่วงที่ **ยาวเกิน 44** คือตัวที่พัง
# ตั้ง 44 เพื่อ **ไม่ไปแตะบทพูด/ซับที่กล่องกว้างพออยู่แล้ว** (เกณฑ์ 32 เคยแก้เกิน 9,326 จุด)
MAX_RUN = 60          # ดูเหตุผลที่ FLOOR ด้านล่าง
TARGET = 52          # เวลาต้องแทรก ให้แต่ละช่วงสั้นกว่าเพดานไว้เผื่อฟอนต์ proportional

_TK = None
_WORDS = set()


def crosses(a, b):
    """จริงถ้ามีคำในพจนานุกรม **คร่อมรอยต่อ** a|b (เช่น 'ทุ'+'กร้าน' → 'ทุก') = newmm ตัดคลุมเครือ
    ห้ามแทรกช่องว่างตรงนี้ (บั๊ก 19 ส.ค. 2026: 'ทุ กร้าน', 'หา ยาก')"""
    for i in range(max(0, len(a) - 3), len(a)):
        for j in range(1, min(3, len(b)) + 1):
            w = a[i:] + b[:j]
            if len(w) >= 3 and w in _WORDS:
                return True
    return False


def thai_units(run):
    """ตัดคำไทยด้วย newmm แล้ว **เชื่อมเศษที่ไม่ใช่คำในพจนานุกรม** เข้ากับคำก่อนหน้า
    (บั๊ก 19 ส.ค. 2026: 'เพนแนนต์' ไม่อยู่ใน dict → newmm ผ่าเป็น 'เพ'+'นแนนต์' แล้วเราแทรกช่องว่างกลางคำ)
    เศษที่ไม่รู้จัก = ส่วนหนึ่งของคำทับศัพท์/คำประสม → ห้ามเป็นจุดตัดทั้งหน้าและหลัง"""
    words = tokenizer().word_tokenize(run)
    out = []
    glue_next = False
    for w in words:
        known = w in _WORDS
        if out and (not known or glue_next):
            out[-1] += w
        else:
            out.append(w)
        glue_next = not known          # คำถัดจากเศษก็ติดกับเศษด้วย (เศษอาจเป็นต้นคำ)
    return out


def tokenizer():
    """newmm + **พจนานุกรมชื่อเฉพาะของโปรเจกต์** — กันตัวแบ่งคำผ่าชื่อทับศัพท์
    (เจอจริง: 'มอร์ติเมอร์' ถูกตัดเป็น 'มอร์ติ เมอร์')"""
    global _TK
    if _TK:
        return _TK
    protected = set()
    for f in ("glossary.md", "characters_main.json", "characters_side.json",
              "PRONOUN_MATRIX.md", "glossary_wave5_names.md"):
        p = PP.PROJECT / "translations" / f
        if p.exists():
            # เก็บทุกคำไทยยาว >=4 ตัวที่ปรากฏในเอกสารชื่อเฉพาะ = ถือเป็นคำเดียวห้ามผ่า
            protected.update(w for w in THAI_RUN.findall(p.read_text(encoding="utf-8"))
                             if 4 <= len(w) <= 30)
    global _WORDS
    _WORDS = set(thai_words()) | protected
    _TK = Tokenizer(custom_dict=dict_trie(_WORDS), engine="newmm")
    print(f"พจนานุกรม: คำไทยมาตรฐาน + ชื่อเฉพาะโปรเจกต์ {len(protected):,} คำ (ห้ามผ่า)")
    return _TK


COMBINING = set("ิีึืั็่้๊๋์ุู")
# หน่วยที่ตัดไม่ได้: แท็ก / placeholder / ช่วงไทย / ช่วงอื่น (Latin, ตัวเลข, เครื่องหมาย)
UNIT = re.compile(r"<[^>]*>|\$\{[^}]*\}|[฀-๿]+|[^฀-๿<$]+|.")
# ตัวแบ่ง "segment" = จุดที่เอนจิ้นตัดบรรทัดได้อยู่แล้ว: ช่องว่างจริง / newline จริง / literal 

SEG_SPLIT = re.compile(r"\s+|\n")
PLACEHOLDER_LEN = 8          # ${...} ขยายเป็นอะไรไม่รู้ ประมาณไว้
OPEN_TAG = re.compile(r"<(color|i|b)(=[^>]*)?>$")
CLOSE_TAG = re.compile(r"</(color|i|b)>$")
OPEN_PUNCT = set("([{\"'“‘«「『")


def vis_len(unit):
    """ความยาวที่ตาเห็นของหน่วย: แท็ก = 0, placeholder = ค่าประมาณ, อื่นๆ = จำนวนตัวไม่นับ combining"""
    if unit.startswith("<") and unit.endswith(">"):
        return 0
    if unit.startswith("${"):
        return PLACEHOLDER_LEN
    return sum(1 for c in unit if c not in COMBINING)


def seg_len(seg):
    return sum(vis_len(u) for u in UNIT.findall(seg))


def split_segment(seg, max_run):
    """แทรกช่องว่างที่ขอบคำไทยใน segment ที่ไม่มีจุดตัดบรรทัดเลย (ยาวเกิน max_run)
    นับความยาวรวม **ทุกอย่างในช่วงเดียวกัน** (Latin/ตัวเลข/... ระหว่างคำไทยด้วย) เพราะเอนจิ้น
    วัดทั้งก้อน — บั๊กจริง 18 ส.ค. 2026: '...เรียกว่า<color>Murderous Heat</color>ได้เมื่อตื่นรู้'
    ช่วงไทยแต่ละข้างไม่เกิน 44 แต่รวมกัน 66 → เอนจิ้นตัดกลางคำ 'เมื่อ' → กล่องสี่เหลี่ยม"""
    if seg_len(seg) <= max_run:
        return seg
    # ชิ้นที่ตัดออกมาต้องสั้นกว่าเพดานเสมอ (ฟอนต์ proportional — 40 หน่วยที่เป็นตัวกว้างล้วน
    # ยังล้นกล่อง 40 ได้) · 0.87 คือสัดส่วนเดิมของค่าคู่ TARGET 52 / FLOOR 60 ที่ใช้มาแล้ว
    target = min(TARGET, int(max_run * 0.87))
    # แตกเป็นหน่วย: ช่วงไทย → คำ (ตัดด้วย pythainlp) · อย่างอื่น → ก้อนเดียวตัดไม่ได้
    units = []
    for u in UNIT.findall(seg):
        if THAI_RUN.fullmatch(u):
            units.extend((w, True) for w in thai_units(u))
        else:
            units.append((u, False))
    # ช่องว่างข้างในสแปน <color>/<i>/<b> เอนจิ้นอาจไม่ใช้ตัด (ดู COLOR_SPAN) → เลี่ยงแทรกในสแปน
    # ให้ตัด "หน้าแท็กเปิด" หรือ "หลังแท็กปิด" แทน · ยกเว้นสแปนยาวเกิน TARGET เอง (ตัดในสแปนเป็นทางสุดท้าย)
    in_span, depth, span_len, j = [], 0, 0, 0
    while j < len(units):
        u = units[j][0]
        if OPEN_TAG.match(u):
            k, L2 = j + 1, 0
            while k < len(units) and not CLOSE_TAG.match(units[k][0]):
                L2 += vis_len(units[k][0]); k += 1
            in_span.append(False)                        # ตัวแท็กเปิดเอง = ตัดหน้ามันได้
            for _ in range(j + 1, min(k, len(units))):
                in_span.append(L2 <= target)              # สแปนสั้น → ห้ามตัดข้างใน
            j = k
            continue
        in_span.append(False); j += 1
    out, cur, cur_len = [], "", 0
    for i, (u, is_thai) in enumerate(units):
        L = vis_len(u)
        prev = units[i - 1][0] if i else ""
        opens = bool(OPEN_TAG.match(u))
        can_break = ((is_thai or opens) and cur and prev and prev[-1] not in OPEN_PUNCT
                     and not in_span[i] and not OPEN_TAG.match(prev)
                     and not (is_thai and units[i - 1][1] and crosses(prev, u)))
        look = L
        if opens:                                        # ตัดหน้าแท็กเปิดถ้าทั้งสแปน (สั้น) จะล้น
            k, L2 = i + 1, 0
            while k < len(units) and not CLOSE_TAG.match(units[k][0]):
                L2 += vis_len(units[k][0]); k += 1
            look = L + L2 if L2 <= target else L
        # ห้ามแทรกติดกับช่องว่างเดิมในสแปน (_NBSP) → กลายเป็นเว้นวรรคซ้ำ
        if can_break and cur_len + look > target and not cur.endswith(_NBSP) and not u.startswith(_NBSP):
            out.append(cur)
            cur, cur_len = u, L
        else:
            cur += u
            cur_len += L
    if cur:
        out.append(cur)
    return " ".join(out)


# ช่องว่างข้างในสแปน <color=..>...</color> เอนจิ้นดูจะไม่ใช้เป็นจุดตัด (บั๊ก 18 ส.ค.: 'Murderous Heat'
# ในแท็กสี ไม่ถูกตัดที่ช่องว่าง แต่ไปตัดกลางคำไทยหลังแท็ก) → ถือเป็นก้อนเดียวตอนวัดความยาว
COLOR_SPAN = re.compile(r"(<color=[^>]*>)(.*?)(</color>)", re.S)
_NBSP = chr(0)


def _protect(th):
    return COLOR_SPAN.sub(lambda m: m.group(1) + m.group(2).replace(" ", _NBSP) + m.group(3), th)


def fix(th, max_run):
    if not th or not THAI_RUN.search(th):
        return th
    th = _protect(th)
    # เดินทีละ segment (คั่นด้วยตัวแบ่งที่เอนจิ้นตัดได้อยู่แล้ว) — คงตัวแบ่งเดิมไว้เป๊ะ
    parts = SEG_SPLIT.split(th)
    seps = SEG_SPLIT.findall(th)
    out = []
    for i, seg in enumerate(parts):
        out.append(split_segment(seg, max_run) if THAI_RUN.search(seg) else seg)
        if i < len(seps):
            out.append(seps[i])
    return "".join(out).replace(_NBSP, " ")


def worst(th):
    """segment ที่ยาวสุด (นับความยาวที่ตาเห็น รวม Latin/ตัวเลขที่ติดกับคำไทย)"""
    return max((seg_len(seg) for seg in SEG_SPLIT.split(_protect(th)) if THAI_RUN.search(seg)),
               default=0)


def _selftest():
    s = "เรียกว่า<color=striking>Murderous Heat</color>ได้เมื่อตื่นรู้ซูจิมอนเหล่านี้หาได้ยากมากแต่เทรนเนอร์ที่ฉลาด"
    r = fix(s, 44)
    assert r != s and r.count("<color=striking>") == 1 and "Murderous Heat" in r, r
    assert worst(r) <= 44 and worst(s) > 44, (worst(r), r)
    s2 = "สั้นๆ ไม่ต้องแตะ\nบรรทัดสอง"
    assert fix(s2, 44) == s2
    s3 = "(สัตว์ประหลาดในทะเลสาบเหรอ...พูดตามตรงก็อดสงสัยไม่ได้เหมือนกันนะและอีกยาวมากๆเลยนะครับ)"
    r3 = fix(s3, 44)
    assert not r3.startswith("( ") and worst(r3) <= 44 and r3.replace(" ", "") == s3, r3
    s4 = "ยาวมากก่อนแท็กสีตรงนี้เลยครับผมนะ<color=striking>ของแต่งบ้านเฉพาะของมาตาโยชิ</color>และต่อท้ายอีกยาวมากเลยนะครับ"
    r4 = fix(s4, 44)
    import re as _re
    assert not _re.search(r"<color[^>]*>[^<]* [^<]*</color>", r4), r4   # ห้ามมีช่องว่างในสแปนสั้น
    assert worst(r4) <= 44 and r4.replace(" ", "") == s4, (worst(r4), r4)
    s5 = "สะสมธงเพนแนนต์"
    assert fix(s5, 12) == "สะสมธง เพนแนนต์", fix(s5, 12)
    s6 = "เขารู้ว่าร้านเบเกอรี่ทุกร้านอยู่ที่ไหน"
    assert "ทุ ก" not in fix(s6, 12) and fix(s6, 12).replace(" ", "") == s6, fix(s6, 12)
    s7 = "<b><color=x>ปล่อยให้ความมุ่งร้ายจอมปลอมท่วมท้น โซเชียลมีเดีย ของพวกเจ้า...</color></b>"
    assert worst(fix(s7, 44)) >= worst(s7)   # แก้ไม่ได้ → main ต้องข้าม (idempotent)
    print("selftest ok:", r, "|", r4)


# ---- ประมาณความกว้างกล่องต่อบิน (เพื่อไม่แทรกช่องว่างเกินจำเป็น) ----
# หลักการ: บินที่ **SEGA ตัดบรรทัด EN มาให้เองแล้ว** (บรรทัดสั้นสม่ำเสมอ) แปลว่าบรรทัดที่ยาวสุด
# ที่มันปล่อยไว้ยังพอดีกล่อง → ใช้ p99 ของความยาวบรรทัด EN เป็น "ขอบล่างของความกว้างกล่อง"
#   sound_auth.bin p99=76 · auth.bin p99=66  → กล่องซับกว้างกว่ากล่องบรรยายมาก
# บินที่ p99 สูงลิ่ว (talk.bin 153 · pause_profile 348) = SEGA ปล่อยให้เอนจิ้นตัดเอง
# → วัดจากข้อมูลไม่ได้ ใช้ค่าปลอดภัย MAX_RUN (44 = วัดจากกล่องบรรยายในเกมจริง)
PREBROKEN_MAX = 90     # p99 เกินนี้ = ไม่ใช่บินที่ตัดบรรทัดมาให้ → ใช้ค่าปลอดภัย
# LJ ปรับจาก 44 (ค่าของ Y8) เป็น 60 เมื่อ 29 ส.ค. 2026 — เหตุผล:
#   * 44 ของ Y8 วัดจาก "หน้าประวัติตัวละคร" ซึ่งเป็นกล่องแคบพิเศษของภาคนั้น
#   * ผู้ใช้ยืนยันบนจอ LJ แล้วว่าซับและกล่องบทพูดที่ยาว ~34-40 ตัวอักษรไทยแสดงถูกต้องสวยงาม
#   * ใช้ 44 จะไปแทรกช่องว่าง 2,354 จุด (บทพูด/ซับ 1,643) ในข้อความที่รู้อยู่แล้วว่าไม่มีปัญหา
#     ช่องว่างที่แทรกจะ **เห็นเป็นช่องว่างจริงกลางประโยค** เมื่อบรรทัดนั้นไม่ได้ถูกตัด = ทำของดีให้แย่ลง
#   * ใช้ 60 แก้ 268 จุด (บทพูด/ซับ 160) เฉพาะช่วงที่ยาวจนเสี่ยงจริง
#     ไทยที่ ship อยู่มีบรรทัดยาวถึง 150 ตัว (sound_auth) และ 186 ตัว (talk) ซึ่งอันตรายแน่นอน
#   * ถ้าเทสแล้วยังเจอจอที่ตัวอักษรเรียงเป็นแนวตั้ง ให้ลดเกณฑ์ลงทีละขั้น: 55 (530 จุด) -> 44 (2,354 จุด)
FLOOR = 60


def box_width_per_bin():
    sbb = json.loads((PP.EXTRACTED / "strings_by_bin.json").read_text(encoding="utf-8"))
    box = {}
    for b, ss in sbb.items():
        lines = sorted(len(l) for s in ss for l in s.split("\n") if l.strip())
        if not lines:
            continue
        p99 = lines[max(0, int(len(lines) * 0.99) - 1)]
        # ⚠ p99 เป็นได้แค่ **ขอบล่าง** ของความกว้างกล่อง ไม่ใช่ค่าจริง —
        # บินที่เนื้อหาสั้นตามธรรมชาติ (ชื่อไอเทม/ป้ายปุ่ม) จะได้ p99 ต่ำ เช่น 38 ทั้งที่กล่องอาจกว้างกว่านั้น
        # ถ้าเอา p99 มาใช้ตรงๆ จะไปแทรกช่องว่างในข้อความที่ไม่มีปัญหา → ต้อง clamp ด้วย FLOOR เสมอ
        box[b] = max(FLOOR, p99) if p99 <= PREBROKEN_MAX else FLOOR
    box.update(BIN_CAP)          # ค่าที่วัดจากจอจริงทับผลประมาณจาก p99 เสมอ (ทั้งกว้างขึ้นและแคบลง)
    return box, sbb


# กล่องแคบพิเศษ **รายคอลัมน์** (วัดจากเกมจริง 19 ส.ค. 2026): ช่องตาราง Bonds Bingo 5x5 กว้างราว
# 12-14 ตัวอักษร — header/title ของ pause_kizuna_profile_bingo โดนตัดทีละตัวเป็นแนวตั้ง
# (explanation_* โชว์ในแผงรายละเอียดด้านล่างซึ่งกว้าง → ใช้เกณฑ์ปกติ)
# LJ ยังไม่พบกล่องแคบพิเศษแบบนั้น (ของ Y8 คือช่องตาราง Bonds Bingo 5x5 กว้าง 12-14 ตัว
# ซึ่งเป็นมินิเกมที่ภาคนี้ไม่มี) — ถ้าเทสแล้วเจอจอที่ข้อความถูกตัดทีละตัวเป็นแนวตั้ง
# ให้เติม {"<ชื่อ bin>": {"<ชื่อคอลัมน์>": <จำนวนตัวอักษร>}} ที่นี่พร้อมบันทึกว่าวัดจากจอไหน
COLUMN_CAP = {}

# กล่องแคบพิเศษ **รายบิน** (วัดจากภาพจอจริง) — ทับค่าที่ประมาณจาก p99 ของ EN เสมอ
# ใส่ที่นี่เมื่อเจอจอที่ข้อความไทยถูกตัดทีละตัวเรียงเป็นแนวตั้ง พร้อมบันทึกว่าวัดจากจอไหน
#
# ⚠ พฤติกรรมเอนจิ้นที่ยืนยันจากจอแล้ว 29 ส.ค. 2026: ถ้า "คำ" (ช่วงที่ไม่มีช่องว่างเลย)
#   กว้างเกินกล่อง เอนจิ้นจะไม่เติมให้เต็มบรรทัดแรกก่อน แต่โยนทั้งช่วงลงมาทีละตัวอักษร
#   ต่อบรรทัดทันที → ช่วงยาว 56 หน่วยในกล่อง 40 หน่วย = แนวตั้ง 56 บรรทัด ไม่ใช่แค่ล้น 16
BIN_CAP = {
    # แผงคำอธิบายทักษะในหน้า Skill Tree (ภาพจอผู้ใช้ 29 ส.ค. 2026 · ทักษะ "นักทำลายเงียบกริบ"):
    #   segment "ขณะสะกดรอยหรือซุ่มตัว" = 17 หน่วย กว้างราว 229 px ในกล่องกว้างราว 536 px
    #   → กล่องรับได้ราว 40 หน่วย · segment ถัดมา 56 หน่วยถูกตัดทีละตัวเป็นแนวตั้ง
    "player_skill.bin": 40,
}



def column_overrides():
    """string → cap สำหรับคอลัมน์ใน COLUMN_CAP (อ่านจาก extracted/db_en/<bin>.json ของ reARMP)"""
    out = {}
    for b, cols in COLUMN_CAP.items():
        p = PP.EXTRACTED / "db_en" / (b + ".json")
        if not p.exists():
            print(f"⚠ COLUMN_CAP: ไม่พบ {p}"); continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for k, rows in d.items():
            if not k.isdigit():
                continue
            for row in rows.values():
                for c, cap in cols.items():
                    s = row.get(c)
                    if isinstance(s, str) and s:
                        out[s] = min(out.get(s, cap), cap)
    return out


def threshold_per_string(box, sbb):
    """เกณฑ์ของแต่ละข้อความ = ค่าที่ **แคบสุด** ของบินที่มันโผล่
    (ข้อความเดียวใช้ได้หลายที่ ต้องรอดในกล่องที่แคบสุด)"""
    th = {}
    for b, ss in sbb.items():
        w = box.get(b, FLOOR)
        for s in ss:
            if s not in th or w < th[s]:
                th[s] = w
    for s, cap in column_overrides().items():
        th[s] = min(th.get(s, cap), cap)
    return th


def main():
    if "--selftest" in sys.argv:
        _selftest(); return 0
    check = "--check" in sys.argv
    force = int(sys.argv[sys.argv.index("--max-run") + 1]) if "--max-run" in sys.argv else None

    box, sbb = box_width_per_bin()
    limit = threshold_per_string(box, sbb)
    wide = {b: w for b, w in box.items() if w > FLOOR}
    print(f"กล่องกว้างกว่าค่าปลอดภัย {len(wide)} บิน (วัดจากบรรทัดที่ SEGA ตัดไว้เอง): "
          + " · ".join(f"{b.replace('.bin','')}={w}" for b, w in sorted(wide.items(),
                                                                        key=lambda x: -x[1])[:8]))

    files = changed = 0
    samples = []
    hist = {}
    for dp in sorted(PP.DONE.glob("batch_*.done.json")):
        d = json.loads(dp.read_text(encoding="utf-8"))
        strings = d.get("strings", {})
        n = 0
        for en, th in strings.items():
            if not isinstance(th, str):
                continue
            cap = force or limit.get(en, FLOOR)
            if worst(th) <= cap:
                continue
            new = fix(th, cap)
            if new == th or worst(new) >= worst(th):
                # ไม่ดีขึ้น (เช่น ทั้งประโยคอยู่ในสแปนสี ช่องว่างข้างในถูกนับเป็นก้อนเดียวอยู่แล้ว)
                # → ไม่เขียน กันแทรกช่องว่างเพิ่มทุกรอบที่รัน (บั๊ก 19 ส.ค. 2026: TALK_023)
                continue
            strings[en] = new
            n += 1
            hist[cap] = hist.get(cap, 0) + 1
            if len(samples) < 5:
                samples.append((worst(th), cap, th, new))
        if n:
            files += 1
            changed += n
            if not check:
                dp.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                              encoding="utf-8", newline="\n")

    print(f"แก้ {changed:,} ข้อความ ใน {files} batch"
          + ("  (--check: ไม่ได้เขียนไฟล์)" if check else ""))
    print("แยกตามเกณฑ์ที่ใช้:",
          " · ".join(f"เกณฑ์ {k} ตัว: {v:,}" for k, v in sorted(hist.items())))
    for w, cap, was, now in samples:
        print(f"\n[ช่วงเดิม {w} ตัว · เกณฑ์ {cap}]")
        print(f"  เดิม: {was[:150]}")
        print(f"  ใหม่: {now[:170]}")
    if changed and not check:
        print("\nขั้นถัดไป: python scripts/merge_qc.py  แล้ว  python scripts/deploy.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
