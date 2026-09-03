#!/usr/bin/env python3
"""ตรวจว่าคำแปลใช้ "ทะเบียนภาษา" ตรงกับที่ล็อกไว้ของตัวละครคนนั้นจริง

ทำไมต้องมี (26 ส.ค. 2026 · sprint 7): ด่านที่มีอยู่ตรวจ "ความสอดคล้องภายในบรรทัด" เท่านั้น —
`check_pronoun_pairs.py` จับเฉพาะการ **ผสมข้ามระดับในประโยคเดียว** (ผม...มึง) ส่วน
`check_speaker_gender.py` จับเฉพาะคำลงท้ายที่ขัดกับ **เพศ** ของผู้พูด
จึงไม่มีด่านไหนจับได้เลยเวลาคำแปล **ใช้ทะเบียนผิดคนอย่างสม่ำเสมอทั้งบรรทัด**
(ยากามิที่ล็อกเป็น T1 พูดว่า "พวกมึงทำให้กูขยะแขยงว่ะ!" — ผ่านทุกด่านมาตั้งแต่ sprint 1)

สิ่งที่ตรวจ (อ่านทะเบียนจาก `translations/characters_*.json` ซึ่งล็อกไว้ใน PRONOUN_MATRIX §2):
  - บรรทัดธง `neutral` : ห้ามมีทั้งคำสุภาพและคำหยาบ (กติกาข้อ 1 ของ SPRINT_TASKS)
  - ตัวละคร **T1**      : ห้าม กู/มึง
  - ตัวละคร **T2**      : ห้าม ครับ/ค่ะ/ผม/ดิฉัน และห้าม กู/มึง
  - ตัวละคร **T3**      : ห้าม ครับ/ค่ะ/ผม/ดิฉัน — **ยกเว้นบทที่ต้นฉบับให้ยอมสยบ**
                          (`Yessir` / `No sir` / `Sorry, boss` — ดู SPRINT_TASKS ข้อ 2b)

⚠ **ข้อจำกัดของด่านคำเรียกคู่สนทนา**: `RE_KAE` จับคำว่า "แก" ที่ไหนก็ได้ในบรรทัด โดย
**แยกไม่ออกว่าเป็นการเรียกคู่สนทนา (บุรุษที่ 2) หรือพูดถึงคนที่ไม่อยู่ในฉาก (บุรุษที่ 3)**
ของจริงที่เจอ (batch_034 · ตัวไล่หนี้รายงาน 26 ส.ค. 2026): นิชิโซโนะ (T1) พูดว่า
"ได้ยินว่า**แก**ป่วยหนัก" ซึ่งหมายถึง *อาจารย์ที่ปรึกษาที่ไม่อยู่ในฉาก* ไม่ใช่คู่สนทนา
ถ้าเผลอแทนเป็น "คุณ/นาย" ความหมายจะกลายเป็น "ได้ยินว่า**คุณ**ป่วย" ซึ่งผิดสนิท
→ บรรทัดแบบนี้ให้เรียบเรียงใหม่ด้วยคำนาม/สรรพนามบุรุษที่ 3 ("อาจารย์" / "เขา") ไม่ใช่แทนคำดิบ ๆ
⚠ **อีกข้อ**: ถ้าเปลี่ยนคำเรียกอีกฝ่ายเป็น "มึง" ให้เช็คคำแทนตัวในบรรทัดเดียวกันด้วย —
T3 ต้องใช้ "กู" ไม่ใช่ "ฉัน" (batch_008 ตก merge_qc 3 บรรทัดเพราะแก้แค่คำเรียกฝ่ายเดียว)

⚠ เป็น **ตัวเตือน ไม่ใช่ด่านตัดสิน**: บางบรรทัดเป็นการ *ยกคำพูดของคนอื่นมาเล่า* ซึ่งต้องใช้
ทะเบียนของ **เจ้าของคำพูด** ไม่ใช่ของผู้เล่า (ดู PRONOUN_MATRIX "กฎคำพูดที่ยกมาอ้าง")
บรรทัดที่ตรวจแล้วว่าถูกต้อง ให้ใส่ไว้ใน `translations/pronoun_exceptions.json`

ใช้:
  python scripts/check_character_register.py --only 057
  python scripts/check_character_register.py --done
  python scripts/check_character_register.py --done --speaker Yagami
"""
import argparse
import collections
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

# regex สรรพนาม/คำลงท้ายทั้งหมดมาจาก `thai_pronouns.py` แหล่งเดียว (แยกออกมา 26 ส.ค. 2026)
# ห้ามเขียน pattern เองในไฟล์นี้ — เคยคัดลอกไว้สามไฟล์แล้วแก้บั๊กไม่ครบมาแล้ว
from thai_pronouns import RUDE, POLITE, RE_KAE, RE_ROUGH_END     # noqa: E402

MONO = re.compile(r"<color=monologue>", re.I)

# ต้นฉบับที่แปลว่า "ยอมสยบ" — T3 ใช้คำสุภาพในบรรทัดพวกนี้ได้ (ดู SPRINT_TASKS ข้อ 2b)
DEFER_EN = re.compile(r"\b(yes\s*sir|yessir|no\s*sir|nosir|sorry,?\s*boss|yes,?\s*boss|"
                      r"right away|as you wish|forgive me)\b"
                      # เพิ่ม 26 ส.ค. 2026 (ผู้ตรวจ batch_064 ยกกรณีมา): ในจักรวาล RGG การเรียก
                      # คู่สนทนาว่า "<ชื่อ>-aniki" คือการยอมเป็นลูกน้องอย่างชัดเจน เทียบเท่า "Yessir"
                      # (ลูกน้องเท็ตโซรับยากามิเข้าบ้านตามคำสั่งนาย — สุภาพทั้งสี่บรรทัด)
                      r"|[A-Za-z]+-aniki\b", re.I)


def load(p, default=None):
    if not os.path.exists(p):
        return default if default is not None else {}
    return json.load(io.open(p, encoding="utf-8"))


def tier_table():
    """คืน {ชื่อผู้พูด: (ระดับ T, ล็อกแล้วหรือยัง)}

    ช่อง `pronoun_source` แยก "คำตัดสินที่ล็อกแล้ว" ออกจาก "ค่าตั้งต้นตามเพศ/บทบาท" —
    สำคัญมากสำหรับด่านคำเรียกคู่สนทนา เพราะตัวละครที่ยังเป็นค่าตั้งต้นแปลว่า **ยังไม่มีใครเคาะ**
    ว่าเขาพูดระดับไหน การเอากติกา T1 ไปบังคับเขาจะสร้างหนี้เท็จนับร้อยบรรทัด (วัดได้จริง 111 บรรทัด)
    """
    out = {}
    for name in ("characters_main.json", "characters_side.json"):
        for k, v in load(paths.TRANSLATIONS / name).items():
            t = str(v.get("tier") or "").strip()
            locked = "ล็อกแล้ว" in str(v.get("pronoun_source") or "")
            # ถ้าคำล็อกของตัวละครระบุ "แก" ไว้เองในช่องคำเรียกคู่สนทนา แปลว่า lead เคาะแล้วว่าใช้ได้
            # → ด่านคำเรียกต้องไม่จับคนนั้น (ของจริง: soma เป็นหัวหน้าที่เรียกลูกน้องรวมว่า "พวกแก")
            allows_kae = "แก" in str(v.get("pronoun_to_others") or "")
            out[k.lower()] = (t, locked and not allows_kae)
            for n in v.get("names_in_game", []) or []:
                out[str(n).lower()] = (t, locked and not allows_kae)
    return out


def exceptions():
    return set(load(paths.TRANSLATIONS / "pronoun_exceptions.json").keys())


def batches(a):
    if a.only:
        return [a.only]
    return [p.name[len("batch_"):-len(".done.json")]
            for p in sorted((paths.TRANSLATIONS / "done").glob("batch_*.done.json"))]


SPLIT_TIER = re.compile("T[123][^T]*T[123]")


def check_line(en, th, tier, neutral, locked=True):
    """คืนข้อความอธิบายปัญหา หรือ None ถ้าไม่มี"""
    rude, polite = RUDE.search(th), POLITE.search(th)
    # ตัวละครที่ล็อกแบบ "แยกตามฉาก" (akane = T3/T2 · matsui = T1/T3) ตัดสินด้วยเครื่องไม่ได้
    # ต้องดูว่าฉากนั้นคุยกับใคร — ปล่อยให้ผู้ตรวจอ่าน ยกเว้นกติกา neutral ที่ยังบังคับได้
    if SPLIT_TIER.search(tier or "") and not neutral:
        return None
    if neutral:
        if rude:
            return "บรรทัด neutral แต่มีคำหยาบ (%s)" % rude.group(0)
        if polite:
            return "บรรทัด neutral แต่มีคำสุภาพ (%s)" % polite.group(0)
        return None
    # คำเรียกคู่สนทนา — เพิ่ม 26 ส.ค. 2026 (sprint 9) หลังผู้ตรวจ batch_070 เจอบรรทัดที่ทุกด่านปล่อยผ่าน:
    # อากุตสึ (T3) เรียกคู่สนทนาว่า "แก" ซึ่งเป็นคำระดับ T2 · `check_pronoun_pairs.py` มองไม่เห็น
    # เพราะบรรทัดนั้น **ไม่มีคำแทนตัว** จึงไม่มีอะไรให้ "ผสมข้ามระดับ" ส่วนตัวนี้เดิมดูแค่
    # คำแทนตัวกับคำลงท้าย ไม่เคยดูคำเรียกอีกฝ่ายเลย
    # ตรวจคำเรียกอีกฝ่ายเฉพาะตัวละครที่ **ล็อกทะเบียนแล้ว** เท่านั้น (ดู tier_table)
    kae = RE_KAE.search(th) if locked else None
    if tier.startswith("T1") and rude:
        return "T1 แต่ใช้ %s" % rude.group(0)
    if tier.startswith("T1") and kae:
        return "T1 แต่เรียกคู่สนทนาว่า แก (ระดับ T2 — T1 ใช้ คุณ/นาย)"
    # คำลงท้ายหยาบ — เพิ่ม 26 ส.ค. 2026 (ผู้ตรวจ batch_068 ทักเรื่องเก็นดะพูด "นับถือเลยว่ะ")
    # ทั้งโปรเจกต์มีแค่ 6 บรรทัด และ 3 ใน 6 เป็นของ matsui ซึ่งล็อกแบบแยกตามฉาก (ข้ามไปแล้วข้างบน)
    if tier.startswith("T1") and locked and RE_ROUGH_END.search(th):
        return "T1 แต่ใช้คำลงท้ายหยาบ %s" % RE_ROUGH_END.search(th).group(0)
    if tier.startswith("T2"):
        if polite:
            return "T2 แต่ใช้ %s" % polite.group(0)
        if rude:
            return "T2 แต่ใช้ %s" % rude.group(0)
    if tier.startswith("T3"):
        if polite and not DEFER_EN.search(en):
            return "T3 แต่ใช้ %s (ต้นฉบับไม่ใช่บทยอมสยบ)" % polite.group(0)
        if kae:
            return "T3 แต่เรียกคู่สนทนาว่า แก (ระดับ T2 — T3 ใช้ มึง)"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="เลข batch เช่น 057")
    ap.add_argument("--done", action="store_true", help="ทุกไฟล์ใน translations/done/")
    ap.add_argument("--speaker", help="ดูเฉพาะผู้พูดคนนี้")
    ap.add_argument("--max", type=int, default=40)
    a = ap.parse_args()

    tiers = tier_table()
    skip = exceptions()
    hits = collections.Counter()
    shown = 0

    for b in batches(a):
        done_p = paths.TRANSLATIONS / "done" / ("batch_%s.done.json" % b)
        ctx_p = paths.WORKLIST / ("batch_%s.context.json" % b)
        if not (done_p.exists() and ctx_p.exists()):
            continue
        done = load(done_p).get("strings", {})
        ctx = load(ctx_p)
        for en, th in done.items():
            if en in skip:
                continue
            rec = ctx.get(en) or {}
            spk = (rec.get("speaker") or "").strip()
            if not spk or (a.speaker and spk.lower() != a.speaker.lower()):
                continue
            if MONO.search(en):
                continue
            tier, locked = tiers.get(spk.lower(), ("", False))
            problem = check_line(en, th, tier, bool(rec.get("neutral")), locked)
            if not problem:
                continue
            hits[(spk, problem.split(" แต่")[0])] += 1
            if shown < a.max:
                shown += 1
                print("\nbatch_%s  %s — %s" % (b, spk, problem))
                print("   EN: %s" % en.replace("\n", " / ")[:100])
                print("   TH: %s" % th.replace("\n", " / ")[:100])

    print()
    if not hits:
        print("ไม่พบบรรทัดที่ผิดทะเบียน")
        return 0
    print("สรุป (ผู้พูด · ชนิดปัญหา · จำนวนบรรทัด):")
    for (spk, kind), n in hits.most_common():
        print("   %-28s %-12s %d" % (spk, kind, n))
    print("\nรวม %d บรรทัด" % sum(hits.values()))
    print("⚠ ตัวเตือน ไม่ใช่คำตัดสิน — บรรทัดที่ยกคำพูดคนอื่นมาเล่าให้ใส่ pronoun_exceptions.json")
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
