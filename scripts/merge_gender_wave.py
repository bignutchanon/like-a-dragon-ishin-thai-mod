#!/usr/bin/env python3
"""ตรวจผลเพศผู้พูดที่ผู้ตรวจ (subagent) ส่งกลับ แล้วรวมเป็น translations/gender_dialogue.json

**ไม่เชื่อคำตัดสินใด ๆ ที่ตรวจซ้ำด้วยเครื่องไม่ได้** (กติกา CLAUDE.md "ห้ามเดา")
ทุกรายการต้องมี `evidence` = {"src": คีย์บรรทัด, "quote": ข้อความที่ยกมา} และด่านนี้เช็กว่า
  1. คีย์บรรทัดที่ตัดสิน และคีย์ที่อ้างเป็นหลักฐาน อยู่ใน "ไฟล์ฉากเดียวกัน" จริง
  2. `quote` เป็นสตริงย่อยของช่อง ja / en / labels ของบรรทัดที่อ้างจริง (เทียบตรงตัว)
  3. gender เป็น male/female เท่านั้น · quote ยาว 1 ตัวได้ถ้าเป็นคันจิ/คานะ (俺 · 僕 · 儂)
รายการที่ตกข้อใดข้อหนึ่ง = ทิ้ง พร้อมรายงานเหตุผล

**สองมาตรวัดที่พิมพ์ออกมา**
- `ja_gender` = เครื่องหมายเพศในบรรทัดนั้นเอง (ตรรกะเดียวกับ merge_qc) — บรรทัดที่มีเครื่องหมาย
  อยู่แล้วเป็น "ข้อสอบที่รู้คำตอบ" ใช้วัดผู้ตรวจได้ทุกซอง ไม่ใช่เฉพาะซองควบคุม
- `scene_gender` = เพศระดับไฟล์ฉาก (build_scene_gender.py) — ตีทั้งฉากเป็นเพศเดียว
  บรรทัดของตัวละครอีกเพศในฉากเดียวกันจึงขัดกันได้ **โดยที่ผู้ตรวจเป็นฝ่ายถูก**
  ต้องอ่านรายการที่ขัดกันทีละอันก่อนสรุป ห้ามดูแต่เปอร์เซ็นต์

ยุบจาก "รายบรรทัด" เป็น "ต่อสตริงอังกฤษ" (คีย์ที่ merge_qc ใช้) ตอนเขียนไฟล์:
สตริงเดียวกันที่ถูกตัดสินคนละเพศในคนละฉาก = ทิ้งทั้งคู่ (กำกวม แปลกลางเพศปลอดภัยกว่า)

นอกจากนั้นเขียน **ตารางรายบรรทัด** `translations/gender_dialogue_keys.json` (คีย์บรรทัด -> เพศ + หลักฐาน)
ไว้ด้วย เพราะตารางต่อสตริงอังกฤษล็อกบทสั้นที่ใครก็พูดได้ไม่ได้ (HANDOFF §0.59 ข้อจำกัดเชิงโครงสร้าง)
คีย์เดียวที่ถูกตัดสินสองเพศ (คลื่นแรกกับคลื่นสองขัดกัน) = ทิ้ง

ใช้:
  python scripts/merge_gender_wave.py --check     # ตรวจอย่างเดียว
  python scripts/merge_gender_wave.py             # ตรวจ + เขียน translations/gender_dialogue.json
  python scripts/merge_gender_wave.py --wave gender_wave gender_wave2 --check   # รวมหลายคลื่น
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from merge_qc import ja_gender  # noqa: E402
from make_gender_packets import DEAD_FILES  # noqa: E402

OUT_FILE = paths.TRANSLATIONS / "gender_dialogue.json"
KEYS_FILE = paths.TRANSLATIONS / "gender_dialogue_keys.json"
CJK_RE = re.compile("[぀-ヿ㐀-鿿]")

# รูปที่โปรเจกต์วัดแล้วว่า **ไม่บอกเพศ** ในเกมนี้ (merge_qc.py บรรทัด 136-137 · วัดกับผู้พูดที่รู้เพศ 6,382 บรรทัด)
#   ですわ / ますわ = สำเนียงคันไซ ชาย 25 : หญิง 6 (เรียวมะพูดเอง) · わ ท้ายประโยคเดี่ยว ๆ ชาย 83 : หญิง 41
# ผู้ตรวจที่ยกรูปพวกนี้ "เดี่ยว ๆ" มาเป็นหลักฐาน = หลักฐานใช้ไม่ได้ ต้องไปหาคำอื่นในฉากมาอ้างแทน
WEAK_QUOTES = {"ですわ", "ますわ", "わ", "ぜよ", "おます", "でおます", "どす", "やねん", "ですやろ"}
# ป้าย `Player` ไม่ใช่ "ผู้พูดคือเรียวมะ" — วัดทั้งคลัง (13 ก.ย. 2026): 6,597 บรรทัดที่มีป้ายนี้
# มีเครื่องหมายชาย 410 · หญิง 9 (โอมัตสึ `uid01160831#038` · หญิงในฉากหมาจร `uid000c1386`)
WEAK_QUOTES |= {"Player"}


# ป้ายที่ถูกยกมาเป็นหลักฐาน "เดี่ยว ๆ" (ไม่มีข้อความในบรรทัดช่วย) ต้องผ่านสถิติทั้งคลังก่อน:
# บรรทัดที่มีป้ายนี้และมีเครื่องหมายเพศในตัว ต้องเป็นเพศที่อ้าง >= LABEL_MIN และเพศตรงข้าม = 0
# เหตุผล: ป้ายเลอะข้ามบรรทัดเป็นเรื่องปกติของไฟล์ .msg — วัดแล้ว `Player` หญิง 9 · `Ryoma` หญิง 2 ·
# `Shikokuya Okami` มีเครื่องหมายชาย 4 (ป้ายไปเกาะบทของไซโต) ป้ายที่ไม่มีสถิติพอ = พิสูจน์ไม่ได้
LABEL_MIN = 5

# คิวเสียงของบรรทัดนั้นเอง (ช่อง voice = คำสั่ง 0x03/0x35) — ป้ายคิวแต่ละตัวไม่ซ้ำกันจึงไม่มีสถิติให้ผ่านเกณฑ์ข้างบน
# แต่วัดแล้วแม่นกว่าป้ายทั่วไป (build_voice_gender.py 15 ก.ย. 2026: ขัดกับเครื่องหมายในบรรทัด 0/475)
# รับ quote ที่เป็นคิวได้เฉพาะเมื่อ quote == voice ของบรรทัด src จริง และเพศของคิวตรงกับที่อ้าง
VOICE_OF = {}
_VG = paths.TRANSLATIONS / "gender_voice_keys.json"
VOICE_GENDER = ({k: v.get("gender") for k, v in json.loads(_VG.read_text(encoding="utf-8")).items()}
                if _VG.exists() else {})


def load_index():
    """คืน (คีย์บรรทัด -> (ไฟล์ฉาก, en, ja, labels), ป้าย -> {male: n, female: n})"""
    par = json.loads((paths.PROJECT / "extracted" / "parallel" / "msg.json").read_text(encoding="utf-8"))
    # ข้อมูลตายของภาคปัจจุบัน (make_gender_packets.DEAD_FILES) — คลื่นแรกหลุดเข้าซองควบคุมไป
    # ตัดทิ้งที่นี่ คำตัดสินที่อ้างคีย์ในไฟล์พวกนี้จะตกด่าน "คีย์บรรทัดไม่มีจริง"
    par = [r for r in par if r["file"] not in DEAD_FILES]
    idx = {r["key"]: (r["file"], r.get("en") or "", r.get("ja") or "", r.get("labels") or [])
           for r in par}
    VOICE_OF.update({r["key"]: r["voice"] for r in par if r.get("voice")})
    label_stats = defaultdict(lambda: defaultdict(int))
    for r in par:
        g = ja_gender(r.get("ja") or "")
        if g:
            for lab in set(r.get("labels") or []):
                label_stats[lab][g] += 1
    return idx, label_stats


# ด่านเข้ม (คลื่นสาม · 15 ก.ย. 2026) — ผู้ตรวจซอง 03 ตัดสิน 375 บรรทัดด้วย "ตรรกะคัดออก" (ฉากมีหญิงคนเดียว
# ที่เหลือจึงเป็นชาย) แล้วอ้าง quote ที่ไม่บอกเพศเลย: 「……！　そうか……」 48 บรรทัด · 「うむ。」 20 บรรทัด ·
# ห่างจากบรรทัดที่ตัดสินเกิน 10 บรรทัด 77 รายการ — ด่านเดิมผ่านหมดเพราะเช็กแค่ว่า quote มีอยู่จริง
# ด่านเข้มบังคับว่า quote ต้อง "บอกเพศในตัวเอง" และอยู่ใกล้บรรทัดที่ตัดสิน
REFER_WORD = re.compile(r"\b(he|him|his|himself|she|her|hers|herself|man|men|woman|women|girl|boy|lady|ladies|"
                        r"sir|miss|ma'am|madam|brother|sister|mother|father|mom|dad|son|daughter|husband|wife|"
                        r"grandma|grandpa|granny|gramps|old man|old woman|guy|gal|lass|lad)\b"
                        r"|姉|兄|嬢|娘|息子|母|父|婆|爺|旦那|女将|おかみ|女|男|坊|奥さん|嫁|亭主|お袋|親父", re.I)
STRICT_NEAR = 2        # อ้างบรรทัดอื่นที่มีเครื่องหมายเพศ/คิวเสียง ได้ไม่เกินกี่บรรทัด (ต่อเทิร์นเดียวกัน)
STRICT_NEAR_REFER = 3  # อ้างคำเรียก/คำสรรพนามบุรุษที่สามได้ไม่เกินกี่บรรทัด
_RA = paths.PROJECT / "work" / "gender_wave3" / "lead_accept.json"   # {คีย์บรรทัด: เหตุผลที่ lead อ่านแล้วรับ}
REFER_ACCEPT = json.loads(_RA.read_text(encoding="utf-8")) if _RA.exists() else {}


def strict_ok(key, gender, src, quote):
    """คืน (ผ่านไหม, เหตุผลที่ตก)"""
    try:
        dist = abs(int(key.split("#")[1]) - int(src.split("#")[1]))
    except (IndexError, ValueError):
        return False, "คีย์บรรทัดอ่านเลขไม่ได้"
    # หลักฐาน "ยืม" จากบรรทัดอื่น — lead สุ่มอ่าน 30 รายการ (15 ก.ย. 2026): ห่าง 2 บรรทัด (A/B/A) ถูกผู้พูด 11/12
    # แต่ห่าง 1 บรรทัดเป็นคนละคนราว 12/18 (เช่น เด็กตอบ そうだったんですか ถัดจากบรรทัด ワシ ของครู = ถูกตีเป็นชาย)
    # เครื่องนับเทิร์นไม่ได้ → ยืมได้เฉพาะคีย์ที่ lead อ่านบริบทแล้วรับใน lead_accept.json
    if src != key and key not in REFER_ACCEPT:
        return False, "ด่านเข้ม: หลักฐานยืมจากบรรทัดอื่น ยังไม่มีใน lead_accept.json"
    if VOICE_OF.get(src) == quote:
        return (dist <= STRICT_NEAR, "ด่านเข้ม: อ้างคิวเสียงห่างเกิน %d บรรทัด" % STRICT_NEAR)
    jg = ja_gender(quote)
    if jg:
        if jg != gender:
            return False, "ด่านเข้ม: quote มีเครื่องหมายเพศตรงข้าม"
        return (dist <= STRICT_NEAR, "ด่านเข้ม: อ้างเครื่องหมายเพศห่างเกิน %d บรรทัด" % STRICT_NEAR)
    if REFER_WORD.search(quote):
        # คำเรียก/สรรพนามบอก "เพศของคนที่ถูกพูดถึง" ซึ่งอาจไม่ใช่ผู้พูด — lead อ่าน 44 รายการของคลื่นสามแล้ว
        # ถูกแค่ 5: ที่เหลือเป็นคำเรียกคู่สนทนา (お嬢さん · Priestess) · พูดถึงคนที่สาม (彼女 · He's so dreamy · 母)
        # · บทรำพึงของเรียวมะที่พูดถึงผู้หญิง → เครื่องตัดสินทิศทางไม่ได้ ต้องให้ lead รับรายคีย์ใน refer_accept.json
        if key not in REFER_ACCEPT:
            return False, "ด่านเข้ม: หลักฐานเป็นคำเรียก/สรรพนาม ยังไม่มีใน lead_accept.json"
        return (dist <= STRICT_NEAR_REFER, "ด่านเข้ม: อ้างคำเรียก/สรรพนามห่างเกิน %d บรรทัด" % STRICT_NEAR_REFER)
    return False, "ด่านเข้ม: quote ไม่บอกเพศในตัวเอง"


def verify(rows, idx, report, label_stats, hold, strict=False):
    """คืนรายการที่ผ่านด่าน — rows = [{"key","gender","evidence":{"src","quote"}}]
    `strict` = ใช้ด่านเข้ม (quote ต้องบอกเพศในตัว + อยู่ใกล้) — เปิดด้วย --strict-wave"""
    ok = []
    for row in rows:
        key = row.get("key")
        gender = row.get("gender")
        ev = row.get("evidence") or {}
        src = ev.get("src")
        quote = (ev.get("quote") or "").strip()
        if gender not in ("male", "female"):
            report["เพศไม่ถูกรูปแบบ"] += 1
            continue
        if key not in idx or src not in idx:
            report["คีย์บรรทัดไม่มีจริง"] += 1
            continue
        if idx[key][0] != idx[src][0]:
            report["หลักฐานอยู่คนละไฟล์ฉาก"] += 1
            continue
        if not quote or (len(quote) == 1 and not CJK_RE.match(quote)):
            report["quote สั้นเกินไป"] += 1
            continue
        if quote == "Player":
            report["quote เป็นป้าย Player (ไม่ใช่หลักฐานว่าเป็นเรียวมะ)"] += 1
            continue
        if quote in WEAK_QUOTES:
            report["quote เป็นรูปที่วัดแล้วว่าไม่บอกเพศ (สำเนียงคันไซ)"] += 1
            continue
        own = ja_gender(idx[key][2])
        if own and own != gender:
            # เครื่องหมายในบรรทัดเองชนะผู้ตรวจเสมอ (ลำดับเดียวกับ merge_qc) — เคสจริง: ผู้ตรวจอ้างชื่อ 遥
            # จากบรรทัดก่อน แต่บรรทัดนั้นเป็นบทของฮาจิเมะที่มีเครื่องหมายชาย (uid016c00c1#100)
            report["ขัดกับเครื่องหมายเพศในบรรทัดเอง"] += 1
            continue
        if key in hold:
            report["พักไว้ให้ผู้ใช้เคาะ (hold_keys.json)"] += 1
            continue
        _, en, ja, labels = idx[src]
        if quote not in ja and quote not in en and not any(quote in lab for lab in labels):
            report["quote ไม่มีอยู่จริงในบรรทัดที่อ้าง"] += 1
            continue
        if quote not in ja and quote not in en and VOICE_OF.get(src) == quote:
            if VOICE_GENDER.get(src) != gender:
                report["quote เป็นคิวเสียงที่ทะเบียนไม่รู้เพศ/ขัดกับที่อ้าง"] += 1
                continue
        elif quote not in ja and quote not in en:
            st = label_stats.get(quote) or {}
            other = "female" if gender == "male" else "male"
            if st.get(gender, 0) < LABEL_MIN or st.get(other, 0):
                report["หลักฐานเป็นป้ายเดี่ยว ๆ ที่สถิติทั้งคลังไม่พอ/ขัดกัน"] += 1
                continue
        if strict:
            passed, why = strict_ok(key, gender, src, quote)
            if not passed:
                report[why] += 1
                continue
        ok.append((key, gender, src, quote))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--wave", nargs="+", default=["gender_wave"], help="โฟลเดอร์คลื่นใต้ work/")
    ap.add_argument("--strict-wave", nargs="*", default=["gender_wave3"],
                    help="คลื่นที่ใช้ด่านเข้ม (quote ต้องบอกเพศในตัว + อยู่ใกล้) — ค่าตั้งต้น gender_wave3")
    args = ap.parse_args()

    idx, label_stats = load_index()
    scene = json.loads((paths.TRANSLATIONS / "scene_gender.json").read_text(encoding="utf-8"))
    files = []
    hold = {}  # คีย์ที่พักไว้ให้ผู้ใช้เคาะ — work/<คลื่น>/hold_keys.json (คีย์ -> เหตุผล)
    for w in args.wave:
        hp = paths.PROJECT / "work" / w / "hold_keys.json"
        if hp.exists():
            hold.update(json.loads(hp.read_text(encoding="utf-8")))
        out_dir = paths.PROJECT / "work" / w / "out"
        files += sorted(p for p in out_dir.glob("*.json") if ".part" not in p.name) if out_dir.exists() else []
    if not files:
        print("ไม่พบผลลัพธ์ใน %s" % ", ".join(args.wave))
        return 1

    report = defaultdict(int)
    passed, control_rows = [], []
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        rows = data["lines"] if isinstance(data, dict) and "lines" in data else data
        good = verify(rows, idx, report, label_stats, hold, strict=p.parent.parent.name in args.strict_wave)
        print("%-14s %-18s ส่งมา %5d · ผ่านด่าน %5d" % (p.parent.parent.name, p.name, len(rows), len(good)))
        (control_rows if p.name.startswith("control") else passed).extend(good)

    if report:
        print("\nที่ทิ้ง:")
        for k, v in sorted(report.items(), key=lambda x: -x[1]):
            print("  %-36s %d" % (k, v))

    # --- มาตรวัดที่ 1: เครื่องหมายในบรรทัดนั้นเอง (รู้คำตอบแน่) ---
    gsame = gdiff = 0
    gbad = []
    for key, gender, src, quote in passed + control_rows:
        want = ja_gender(idx[key][2])
        if want is None:
            continue
        if want == gender:
            gsame += 1
        else:
            gdiff += 1
            gbad.append((key, gender, want, src, quote))
    if gsame + gdiff:
        tot = gsame + gdiff
        print("\nเทียบเครื่องหมายในบรรทัดเอง (ja_gender): ตรง %d/%d = %.1f%%"
              % (gsame, tot, gsame / tot * 100))
        for key, got, want, src, quote in gbad[:12]:
            print("   ขัดกัน %s: ผู้ตรวจว่า %s · บรรทัดเองบอก %s (อ้าง %s: %s)"
                  % (key, got, want, src, quote))

    # --- มาตรวัดที่ 2: เพศระดับไฟล์ฉาก (หยาบกว่า ดูประกอบเท่านั้น) ---
    if control_rows:
        same = diff = 0
        bad = []
        for key, gender, src, quote in control_rows:
            want = scene.get(idx[key][1])
            if want is None:
                continue
            if want == gender:
                same += 1
            else:
                diff += 1
                bad.append((key, gender, want, src, quote))
        tot = same + diff
        if tot:
            print("\nซองควบคุม เทียบ scene_gender: ตรง %d/%d = %.1f%%" % (same, tot, same / tot * 100))
            print("  (scene_gender ตีทั้งไฟล์เป็นเพศเดียว — บรรทัดของตัวละครอีกเพศในฉากเดียวกัน")
            print("   ขัดกันได้โดยผู้ตรวจถูก ต้องอ่านทีละอัน)")
            for key, got, want, src, quote in bad[:12]:
                print("   ขัดกัน %s: ผู้ตรวจว่า %s · scene_gender ว่า %s (อ้าง %s: %s)"
                      % (key, got, want, src, quote))

    # --- ขัดกับ scene_gender (ทุกซอง) — คลื่นสองตั้งใจหาเคสนี้ ต้องอ่านทีละอัน ---
    conflicts = [(key, g, scene[idx[key][1]], src, quote) for key, g, src, quote in passed
                 if scene.get(idx[key][1]) not in (None, g)]
    if conflicts:
        by_file = defaultdict(int)
        for key, *_ in conflicts:
            by_file[idx[key][0]] += 1
        print("\nขัดกับ scene_gender %d บรรทัด · %d ไฟล์ฉาก (มากสุด: %s)"
              % (len(conflicts), len(by_file),
                 " ".join("%s:%d" % kv for kv in sorted(by_file.items(), key=lambda x: -x[1])[:8])))
        for key, got, want, src, quote in conflicts[:12]:
            print("   %s: ผู้ตรวจว่า %s · scene_gender ว่า %s (อ้าง %s: %s)" % (key, got, want, src, quote))

    # --- ตารางรายบรรทัด ---
    by_key = defaultdict(set)
    key_why = {}
    for key, gender, src, quote in passed:
        by_key[key].add(gender)
        key_why.setdefault(key, (gender, src, quote))
    keys_final = {k: {"gender": key_why[k][0], "why": "หลักฐาน %s: %s" % key_why[k][1:]}
                  for k, gs in sorted(by_key.items()) if len(gs) == 1}
    print("\nตารางรายบรรทัด: %d คีย์ · ทิ้งเพราะคลื่นขัดกันเอง %d"
          % (len(keys_final), len(by_key) - len(keys_final)))

    # --- ยุบเป็นต่อสตริงอังกฤษ ---
    by_en = defaultdict(set)
    why = {}
    for key, gender, src, quote in passed:
        en = idx[key][1]
        by_en[en].add(gender)
        why.setdefault(en, (gender, src, quote))
    final, dropped = {}, 0
    for en, genders in by_en.items():
        if len(genders) != 1:
            dropped += 1
            continue
        g, src, quote = why[en]
        final[en] = {"gender": g, "why": "ผู้ตรวจอ่าน EN คู่ JA · หลักฐาน %s: %s" % (src, quote)}
    print("\nคำตัดสินรายบรรทัดที่ผ่าน %d · สตริงอังกฤษที่ได้ %d · ทิ้งเพราะขัดกันเอง %d"
          % (len(passed), len(final), dropped))
    already = sum(1 for en in final if en in scene)
    print("ในนั้นซ้ำกับ scene_gender เดิม %d · เพิ่มของใหม่ %d" % (already, len(final) - already))

    if not args.check:
        OUT_FILE.write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
        KEYS_FILE.write_text(json.dumps(keys_final, ensure_ascii=False, indent=1), encoding="utf-8")
        print("เขียน %s · %s" % (OUT_FILE, KEYS_FILE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
