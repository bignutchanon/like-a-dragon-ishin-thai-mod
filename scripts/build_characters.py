#!/usr/bin/env python3
"""ทะเบียนตัวละครของ Ishin! — รวมทุกแหล่งในไฟล์เกมเข้าเป็นตารางเดียว

แหล่งที่ใช้ (ทั้งหมดอยู่ในไฟล์เกม):
  1. `Game.locres` namespace `correlation_person_*` = **แผนผังความสัมพันธ์ในเกม**
     ให้ชื่อเต็ม (`Sakamoto Ryoma`) · ชื่อสั้นที่ใช้เป็นป้ายผู้พูด (`Ryoma`) · สังกัด (`Tosa Domain`)
     · ประวัติย่อที่ใช้ **he/she ตรง ๆ** → เป็นหลักฐานเพศที่ชี้ขาดที่สุดของภาคนี้
     ฝั่ง `ja` ของคีย์เดียวกันให้ **คันจิชื่อจริง** (坂本龍馬) ซึ่งจำเป็นตอนทับศัพท์ไทย
  2. `translations/speakers.json` = ทะเบียนผู้พูด + เพศจากเครื่องหมายภาษาญี่ปุ่น
     (สร้างโดย `build_speaker_gender.py`)
  3. `scripts/romaji_to_thai.py` = ร่างคำทับศัพท์ไทย — **ร่างเท่านั้น lead ต้องเคาะ**

⚠ กติกาเฉพาะภาคนี้: Ishin เป็นยุคบาคุมัตสึ ตัวละคร **คนละคน** กับซีรีส์หลัก แม้ใช้หน้าตัวละครชุดเดียวกัน
   id ภายในยังเป็นชื่อนักแสดงชุด Yakuza (`kiryu` = เรียวมะ · `majima` = โอกิตะ)
   → **ห้ามยกคำล็อกชื่อจากภาคก่อนมาใช้เด็ดขาด** ทุกชื่อต้องตั้งใหม่ตามชื่อประวัติศาสตร์ญี่ปุ่น

ผลลัพธ์:
  translations/characters.json   ทะเบียนรวม (เครื่องอ่าน)
  docs/characters.md             ตารางให้คนอ่าน
  translations/name_proposals.md ใบเสนอชื่อไทยให้ lead เคาะ

ใช้: python scripts/build_characters.py
ต้องมีมาก่อน: build_parallel.py · build_speaker_gender.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                            # noqa: E402
from romaji_to_thai import convert as translit            # noqa: E402

HE = re.compile(r"\b(he|his|him|himself)\b", re.I)
SHE = re.compile(r"\b(she|her|hers|herself)\b", re.I)
NS_PREFIX = "correlation_person_"


def load_correlation():
    """คืน {id: {name, name_short, group, explanation, name_ja, explanation_ja}}"""
    rows = json.loads((paths.EXTRACTED / "parallel" / "locres.json")
                      .read_text(encoding="utf-8"))
    out = defaultdict(dict)
    for r in rows:
        if not r["ns"].startswith(NS_PREFIX):
            continue
        field = r["ns"][len(NS_PREFIX):]
        pid = r["key"].rsplit("/", 1)[-1]
        out[pid][field] = r["en"]
        out[pid][field + "_ja"] = r["ja"]
    return out


def bio_gender(text):
    """เพศจากคำสรรพนามในประวัติย่อ — หลักฐานตรงจากไฟล์เกม"""
    if not text:
        return None, None
    h, s = len(HE.findall(text)), len(SHE.findall(text))
    if h > s and h >= 1:
        return "male", "ประวัติในแผนผังใช้ he/his %d ครั้ง" % h
    if s > h and s >= 1:
        return "female", "ประวัติในแผนผังใช้ she/her %d ครั้ง" % s
    return None, None


# คำอังกฤษที่โผล่ในชื่อบนจอ — ชื่อพวกนี้ต้อง **แปลความหมาย** ไม่ใช่ทับศัพท์
# (`The Masked Man` = ชายสวมหน้ากาก · `The Impostor Ryoma` = เรียวมะตัวปลอม)
EN_WORDS = re.compile(r"\b(the|real|impostor|masked|man|in|white|of|and|gate|guard|"
                      r"lady|large|mysterious|elderly|young|old)\b", re.I)


def load_locks():
    """คำล็อกชื่อที่ lead เคาะแล้ว — {'full': {...}, 'short': {...}}"""
    p = paths.TRANSLATIONS / "name_locks.json"
    if not p.exists():
        return {}, {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("full") or {}, d.get("short") or {}


def thai_name(name, locks):
    """คำไทยของชื่อ — คำล็อกมาก่อนเสมอ ถ้ายังไม่ล็อกค่อยใช้ร่างอัตโนมัติ

    คืน (คำไทย, ที่มา) โดยที่มาเป็น 'locked' หรือ 'draft' หรือ 'needs_meaning'
    """
    if name in locks:
        return locks[name], "locked"
    if EN_WORDS.search(name):
        return "⚠ วลีอังกฤษ — ต้องแปลความหมาย ไม่ใช่ทับศัพท์", "needs_meaning"
    return " ".join(translit(w)[0] for w in name.split()), "draft"


def find_speaker(speakers, short, full):
    """หาแถวในทะเบียนผู้พูดที่ตรงกับตัวละครนี้

    ป้ายผู้พูดบนจอไม่ได้ตรงกับ `name_short` ของแผนผังเสมอ —
    `Tokugawa Yoshinobu` ย่อเป็น `Tokugawa` ในแผนผัง แต่ป้ายผู้พูดคือ `Yoshinobu`
    จึงต้องลองทีละท่อนของชื่อเต็มด้วย
    """
    keys = [short, full]
    # ชื่อที่เป็นวลีอังกฤษคือ "ตัวปลอม/ตัวจริง" ของคนอื่น (`The Real Nagakura Shinpachi`)
    # ห้ามไล่ทีละท่อน ไม่งั้นจะไปคว้าบทของตัวจริงมาทั้งกอง
    if not EN_WORDS.search(full):
        keys += full.split()
    for k in keys:
        if k and k in speakers:
            return speakers[k]
    return {}


def main():
    lock_full, lock_short = load_locks()
    corr = load_correlation()
    spk_path = paths.TRANSLATIONS / "speakers.json"
    if not spk_path.exists():
        sys.exit("ยังไม่มี %s — รัน scripts/build_speaker_gender.py ก่อน" % spk_path)
    speakers = json.loads(spk_path.read_text(encoding="utf-8"))

    # ---- ยุบ id ที่เป็นคนเดียวกัน (แผนผังมีหลายแถวต่อคน แยกตามช่วงเนื้อเรื่อง) ----
    people = {}
    bios = defaultdict(list)
    for pid, f in sorted(corr.items()):
        name = f.get("name")
        if not name:
            continue
        p = people.setdefault(name, {
            "name": name,
            "name_ja": f.get("name_ja"),
            "short": f.get("name_short"),
            "short_ja": f.get("name_short_ja"),
            "groups": set(), "ids": [],
        })
        p["ids"].append(pid)
        if f.get("diagram_group"):
            p["groups"].add(f["diagram_group"])
        if f.get("explanation"):
            bios[name].append(f["explanation"])

    # ประวัติของ id ที่ไม่มีชื่อ = คนเดิมในช่วงเนื้อเรื่องอื่น — เก็บไว้เป็นหลักฐานเพศเพิ่ม
    # (จับคู่ไม่ได้แน่ชัดจึงไม่ผูกกับใคร แค่รายงานจำนวนไว้)
    orphan_bios = sum(1 for f in corr.values() if f.get("explanation") and not f.get("name"))

    # ---- รวมกับทะเบียนผู้พูด + ตัดสินเพศ ----
    tally = Counter()
    for name, p in people.items():
        joined = "\n".join(bios[name])
        g, why = bio_gender(joined)
        p["bio"] = bios[name][0] if bios[name] else None
        p["bio_count"] = len(bios[name])

        sp = find_speaker(speakers, p["short"], name)
        p["cue_id"] = sp.get("id")
        p["lines"] = sp.get("ja_lines", 0)
        p["gender_ja_markers"] = sp.get("gender", "unknown")

        if g:
            p["gender"], p["gender_from"], p["gender_why"] = g, "bio_pronoun", why
        elif sp.get("gender", "unknown") != "unknown":
            p["gender"] = sp["gender"]
            p["gender_from"] = sp.get("gender_from", "ja_markers")
            p["gender_why"] = " · ".join(sp.get("gender_why") or [])
        else:
            p["gender"], p["gender_from"], p["gender_why"] = "unknown", "none", ""
        tally[p["gender"]] += 1

        # คำไทย — คำล็อกมาก่อน ถ้ายังไม่ล็อกใช้ร่างอัตโนมัติ
        p["th"], p["th_from"] = thai_name(name, lock_full)
        if p["short"]:
            p["th_short"], p["th_short_from"] = thai_name(p["short"], lock_short)
        else:
            p["th_short"], p["th_short_from"] = None, None
        p["groups"] = sorted(p["groups"])

    # ---- ผู้พูดที่ไม่มีในแผนผัง (NPC/ตัวประกอบ) ----
    known_short = {p["short"] for p in people.values() if p["short"]}
    known_full = set(people)
    extra = {n: e for n, e in speakers.items()
             if n not in known_short and n not in known_full}

    out = {"main": people, "other_speakers": extra}
    (paths.TRANSLATIONS / "characters.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    print("ตัวละครในแผนผัง %d คน (จาก %d แถว · ประวัติที่ไม่มีชื่อกำกับอีก %d แถว)"
          % (len(people), len(corr), orphan_bios))
    print("  เพศ — ชาย %d · หญิง %d · พิสูจน์ไม่ได้ %d"
          % (tally["male"], tally["female"], tally["unknown"]))
    print("ผู้พูดที่ไม่อยู่ในแผนผัง (NPC/ตัวประกอบ): %d" % len(extra))

    # ---- ตารางให้คนอ่าน ----
    order = sorted(people.values(), key=lambda p: (-p["lines"], p["name"]))
    md = [
        "# ทะเบียนตัวละคร — Like a Dragon: Ishin!", "",
        "สร้างโดย `scripts/build_characters.py` · ข้อมูลทุกช่องมาจากไฟล์เกม",
        "(ยกเว้นช่อง **ไทย (ร่าง)** ซึ่งเป็นคำทับศัพท์อัตโนมัติ — **lead ต้องเคาะก่อนใช้**)", "",
        "⚠ **ห้ามยกคำล็อกชื่อจากซีรีส์หลักมาใช้** — Ishin เป็นยุคบาคุมัตสึ ตัวละครคนละคน",
        "แม้ใช้หน้านักแสดงชุดเดียวกัน (`kiryu` ในไฟล์เกม = **เรียวมะ** ไม่ใช่คิริว)", "",
        "| ชื่อบนจอ | ชื่อเต็ม | คันจิ | สังกัด | เพศ | ที่มาของเพศ | id คิว | บรรทัด | ไทย (ร่าง) |",
        "|---|---|---|---|---|---|---|---:|---|",
    ]
    for p in order:
        md.append("| %s | %s | %s | %s | **%s** | %s | %s | %d | %s |" % (
            p["short"] or "-", p["name"], p["name_ja"] or "-",
            " / ".join(p["groups"]) or "-", p["gender"], p["gender_from"],
            "`%s`" % p["cue_id"] if p["cue_id"] else "-", p["lines"],
            p["th"]))
    md += ["", "## ประวัติย่อจากแผนผังในเกม (ใช้ตั้งโทนและตรวจความสัมพันธ์)", ""]
    for p in order:
        if p["bio"]:
            md.append("### %s (%s)" % (p["name"], p["short"] or "-"))
            md.append("")
            md.append("> " + p["bio"].replace("\n", "\n> "))
            md.append("")
    md += ["## ผู้พูดที่ไม่อยู่ในแผนผัง", "",
           "ป้ายผู้พูดที่เจอในไฟล์เสียง/บทแต่ไม่มีในแผนผังความสัมพันธ์ —",
           "ส่วนใหญ่เป็น NPC หรือป้ายกลุ่มคน (ดูเพศรายตัวใน `docs/reference/gender_evidence_ishin.md`)",
           "", "| ป้ายผู้พูด | เพศ | ที่มา | บรรทัด |", "|---|---|---|---:|"]
    for n, e in sorted(extra.items(), key=lambda kv: -kv[1].get("ja_lines", 0))[:80]:
        md.append("| %s | %s | %s | %d |"
                  % (n, e.get("gender", "unknown"), e.get("gender_from", "none"),
                     e.get("ja_lines", 0)))
    p = paths.DOCS / "characters.md"
    p.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("เขียนแล้ว: %s" % p)

    # ---- ใบเสนอชื่อไทย ----
    prop = [
        "# ใบเสนอชื่อไทย — Like a Dragon: Ishin!", "",
        "คำที่ขึ้น **LOCKED** = lead เคาะแล้ว อ่านจาก `translations/name_locks.json` — **ใช้ได้ทันที**",
        "คำที่ขึ้น **รอเคาะ** = ร่างอัตโนมัติจาก `scripts/romaji_to_thai.py` ยังห้ามใช้",
        "แก้คำล็อกที่ `name_locks.json` ที่เดียว แล้วรัน `python scripts/build_characters.py` ใหม่", "",
        "หลักที่ใช้กับภาคนี้:",
        "- ชื่อคนญี่ปุ่นเรียง **นามสกุลก่อนชื่อตัว** ตามต้นฉบับ (`Sakamoto Ryoma` = ซากาโมโตะ เรียวมะ)",
        "- ป้ายผู้พูดบนจอใช้ **ชื่อสั้น** — คำไทยของชื่อสั้นต้องตรงกับท่อนเดียวกันของชื่อเต็มเสมอ",
        "- ชื่อในประวัติศาสตร์ที่คนไทยคุ้นอยู่แล้ว (ซากาโมโตะ เรียวมะ · ชินเซ็นกุมิ) ให้ใช้รูปที่คุ้น",
        "  แทนผลของตัวทับศัพท์ ถ้าขัดกัน — จดเหตุผลกำกับ", "",
        "| ชื่อเต็ม (EN) | คันจิ | ชื่อสั้น | ไทย (เต็ม) | ไทย (สั้น) | สถานะ |",
        "|---|---|---|---|---|---|",
    ]
    for p_ in order:
        prop.append("| %s | %s | %s | %s | %s | %s |" % (
            p_["name"], p_["name_ja"] or "-", p_["short"] or "-",
            p_["th"], p_["th_short"] or "-",
            "LOCKED" if p_["th_from"] == "locked" else "รอเคาะ"))
    pp = paths.TRANSLATIONS / "name_proposals.md"
    pp.write_text("\n".join(prop) + "\n", encoding="utf-8")
    print("เขียนแล้ว: %s" % pp)


if __name__ == "__main__":
    main()
