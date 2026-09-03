#!/usr/bin/env python3
"""แนบ "บริบทผู้พูด + เพศ" ให้ทุก batch ในคิวแปล — ตัวช่วยที่ตัดงานเดาของนักแปลออกทั้งหมด

ปัญหาที่แก้: ไฟล์คำแปลเป็น map แบน EN→TH นักแปลเห็นแต่ประโยคลอย ๆ ไม่รู้ว่าใครพูด
เลยต้องเดาว่าจะใช้ ผม/ฉัน/ครับ/ค่ะ หรือไม่ — เดาผิดทีเดียวพังทั้งบรรทัด และ QC จับไม่ได้
เพราะประโยคถูกไวยากรณ์อยู่แล้ว

สคริปต์นี้เขียนไฟล์คู่กับทุก batch: `batch_NNN.context.json`
  {EN: {"speaker", "gender", "gender_confidence", "neutral", "why_neutral",
        "dupes", "chapter", "bins"}}

`neutral: true` = **บังคับแปลกลางเพศ** (ห้าม ผม/ดิฉัน · ห้าม ครับ/ค่ะ) เกิดได้สามกรณี:
  1. ไม่รู้ผู้พูด (string อยู่ใน bin ที่ไม่ผูกผู้พูด เช่น ui/item/help)
  2. รู้ผู้พูดแต่ **เพศยังพิสูจน์ไม่ได้** (`unknown`/`conflict` ใน gender_evidence.json)
  3. ข้อความเดียวถูกใช้ซ้ำโดยผู้พูดหลายคน (`dupes`) — คำแปลเดียวต้องใช้ได้กับทุกคน
  4. ผู้พูดที่พบคนละเพศกัน (`gender: conflict`) — เกมใช้บรรทัดซ้ำข้ามฉาก

ใช้:
  python scripts/make_batch_context.py [--write]
  python scripts/make_batch_context.py --find "Hey, man the fuck up!"
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

FACTS = paths.EXTRACTED / "facts"
TALK = FACTS / "talk_speaker.json"
SPEECH = FACTS / "speech_speaker_map.json"
SPEECH_SPK = FACTS / "speech_speaker.json"     # ผู้พูดรายบรรทัดของคัตซีน (แม่นกว่า ครอบเกือบทุกบรรทัด)
AUTH_SPK = FACTS / "auth_speaker.json"         # ผู้พูดรายบรรทัดของซับทับคัตซีน (auth.bin cinema_telop)
GENDER = FACTS / "gender_evidence.json"
UNIQUE = paths.EXTRACTED / "unique_strings.json"
REPORT = paths.TRANSLATIONS / "batch_context_report.md"


def load(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(io.open(p, encoding="utf-8"))


# ตารางผู้พูดทุกแหล่ง — เก็บ **รวมกันทุกแหล่ง** ห้ามให้แหล่งหลังทับแหล่งก่อน
# (บั๊กเดิม: sound_auth ทับ talk ทำให้ "Sure!" เหลือผู้พูดคนเดียวทั้งที่ Minato กับ Jun พูดคนละฉาก
#  → ธง neutral หาย นักแปลใส่สรรพนามผูกเพศไปแล้วผิดครึ่งหนึ่ง)
# ชื่อผู้พูดสะกดคนละแบบข้ามตาราง: `talk_talker` ให้ชื่อขึ้นต้นตัวใหญ่ ("Kaito")
# ส่วน `speech_speaker_map` ให้ token ของคีย์เสียงตัวเล็กมีคำนำหน้าบท ("dlc_g02_kaito")
# ถ้าไม่ยุบให้เป็นคนเดียวกัน จะกลายเป็น "ผู้พูดสองคน" ปลอม ๆ แล้วบังคับกลางเพศทั้งที่รู้ตัวคนพูดชัด
# (วัดเมื่อ 25 ส.ค. 2026: 1,802 จาก 3,356 บรรทัดที่มี dupes เป็นเคสปลอมแบบนี้)
# คำนำหน้าเชิงกลไกที่เกมใส่ไว้หน้าคีย์เสียง (บท/ฉาก/DLC/เควสเสริม) — ตัดออกทั้งหมด
# ขยาย 26 ส.ค. 2026: ของเดิมครอบแค่ `dlc_`/`g\d+_` ทำให้ `g_m_g01_yagami`, `side_ptc071_yagami`,
# `drama_m24_itokura`, `old_mamiya`, `g_g_yagami` กลายเป็น "คนละคน" กับ `Yagami`/`Itokura`/`Mamiya`
PREFIX_RE = re.compile(
    r"^(?:(?:dlc|old|new|g|m|b|f|p|c|side|drama|dgmb|btl|hact|ptc|sub|kif)_?\d*_)+")

# ชื่อเดียวกันที่ไฟล์เกมสะกดคนละแบบ — **ใส่ได้เฉพาะคู่ที่พิสูจน์แล้วจากบทจริง ห้ามเดาจากชื่อคล้าย**
SPEAKER_ALIASES = {
    "souma": "soma",            # 相馬/そうま — Hepburn สระยาว (ยืนยันแล้วใน make_talk_speaker.ALIASES)
    "kouda": "koda",            # 幸田 — รูปสระยาวของ Koda (ผู้ตรวจ batch_036 ยืนยันจากฉากเดียวกัน)
    "tessou": "tesso",          # รูปสระยาวแบบเดียวกัน
    "wanatabe": "watanabe",     # สลับตัวอักษรในข้อมูลเกม (ชื่อเดียวกัน)
    "sayaka": "nishizono",      # ชื่อต้น vs นามสกุล — ผู้ตรวจ batch_034 ยืนยันจากบท
                                # ("Sayaka Nishizono-san" ในฉากเดียวกัน · gender_evidence ตรงกัน)
    "omonaga_basket": "long_faced_basketball_girl",   # 面長 = หน้ายาว (ผู้ตรวจ batch_036)
    "sobakasu_basket": "freckled_basketball_player",  # そばかす = ฝ้ากระ
    # ลูกชายของมามิยะ (6 ขวบ) ถูกเก็บสองไอดี — ผู้ตรวจ batch_047 ยืนยันว่าเป็นเด็กคนเดียวกัน
    # (กระทบ 7 บรรทัด: batch_034 1 · batch_047 6) · **ยังไม่ได้ regenerate context หลังเพิ่มบรรทัดนี้**
    # ให้ regenerate ตอนคิวว่างระหว่าง sprint เท่านั้น
    "mamiya_jr": "mamiya_s_son_age_6",
}


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")
    prev = None
    while prev != s:
        prev, s = s, PREFIX_RE.sub("", s)
    return s or prev


def load_generated_aliases():
    """ตารางชื่อพ้องที่ **พิสูจน์จากไฟล์เกม** — สร้างโดย scripts/make_speaker_aliases.py

    เนื้อหาคือคู่ "id ของ voicer ↔ ชื่อที่แสดงบนจอ" ที่เป็นคนเดียวกัน
    (`seiren` ↔ `Siren Owner` · `fat_hangure` ↔ `Chubby Thug`) ซึ่งเดิมถูกนับเป็นคนละคน
    แล้วบังคับให้บรรทัดนั้นแปลกลางเพศทั้งที่รู้ตัวผู้พูดชัด
    """
    p = FACTS / "speaker_aliases.json"
    if not p.exists():
        return {}
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for raw, display in d.items():
        a, b = slug(raw), slug(display)
        if a and b and a != b:
            out[a] = b
    return out


GEN_ALIASES = load_generated_aliases()


def canon(name):
    """คีย์ยุบชื่อผู้พูด — ตัวเล็ก + ตัดคำนำหน้าบท/DLC (ซ้อนกันหลายชั้นก็ตัดหมด) + ตารางชื่อพ้อง

    ลำดับ: ตารางที่สร้างจากไฟล์เกมก่อน แล้วค่อยตารางที่คนใส่มือ (คนใส่มือชนะ = แก้เคสที่เครื่องพลาดได้)
    """
    s = slug(name)
    s = GEN_ALIASES.get(s, s)
    return SPEAKER_ALIASES.get(s, s)


LINE_SOURCES = [
    (TALK, "talk.bin", "talk_speaker"),
    (SPEECH_SPK, "sound_auth.bin", "sound_auth(talker)"),
    (AUTH_SPK, "auth.bin", "auth(cinema_telop)"),
]


def build_index():
    """คืน {EN: บริบท} ของทุกข้อความที่รู้ผู้พูด — รวมผู้พูดจากทุกตารางเข้าด้วยกัน"""
    gender = load(GENDER, {}) or {}
    gender.pop("_meta", None)
    speech = load(SPEECH, {}) or {}

    def g_of(name):
        r = gender.get(name) or gender.get(name.lower()) or {}
        return r.get("gender", "unknown"), r.get("gender_confidence") or r.get("confidence", "none")

    # {EN: {ชื่อผู้พูด: (gender, conf)}} + แหล่ง/บทที่พบ
    hits = collections.OrderedDict()

    def add(text, name, g, conf, source, chapter=None):
        if not name:
            return
        ent = hits.setdefault(text, {"who": collections.OrderedDict(),
                                     "sources": [], "chapter": []})
        if g in (None, "", "unknown"):
            g, conf = g_of(name)
        key = canon(name)
        prev = ent["who"].get(key)
        if prev is None:
            ent["who"][key] = [name, g or "unknown", conf]
        else:
            # ชื่อที่เจอก่อน (มาจาก talk_talker) สะกดสวยกว่า token ของคีย์เสียง — คงไว้
            if prev[1] in (None, "", "unknown") and g not in (None, "", "unknown"):
                prev[1], prev[2] = g, conf
        if source not in ent["sources"]:
            ent["sources"].append(source)
        if chapter and chapter not in ent["chapter"]:
            ent["chapter"].append(chapter)

    for path, source, conf in LINE_SOURCES:
        for text, rec in (load(path, {}) or {}).items():
            rows = [rec] + list(rec.get("dupes", []))
            for r in rows:
                add(text, r.get("speaker") or "", r.get("gender"), conf, source,
                    r.get("chapter"))

    # ตารางเก่าจากคีย์เสียง — ใช้เป็นหลักฐานเสริม (ชื่ออาจเป็นโทเคนไม่ใช่ชื่อเต็ม)
    for text, rec in speech.items():
        toks = list(rec.get("speaker_exact") or []) or list(rec.get("speaker") or [])
        for name in toks:
            g, conf = g_of(name)
            add(text, name, g, conf, "sound_auth.bin")
        for ch in rec.get("chapter", []) or []:
            ent = hits.get(text)
            if ent is not None and ch not in ent["chapter"]:
                ent["chapter"].append(ch)

    idx = {}
    for text, ent in hits.items():
        names = [v[0] for v in ent["who"].values()]
        primary = names[0]
        genders = {v[1] for v in ent["who"].values() if v[1] not in (None, "", "unknown")}
        if len(genders) > 1:
            g, conf = "conflict", "หลายผู้พูดคนละเพศ"
        elif genders:
            g = next(iter(genders))
            conf = next(v[2] for v in ent["who"].values() if v[1] == g)
        else:
            g, conf = "unknown", "none"
        idx[text] = {"speaker": primary, "gender": g, "gender_confidence": conf,
                     "dupes": sorted(set(names[1:])), "chapter": sorted(ent["chapter"], key=str),
                     "source": " + ".join(ent["sources"])}
    return idx


def decide_neutral(ent):
    """คืน (neutral, เหตุผลไทย)"""
    if ent is None:
        return True, "ไม่รู้ผู้พูด (ข้อความระบบ/UI หรือไม่ผูกกับตารางบทพูด) — แปลกลางเพศ"
    if ent.get("dupes"):
        return True, ("ผู้พูดหลายคนใช้ข้อความเดียวกัน (%d คน) — คำแปลเดียวต้องใช้ได้กับทุกคน"
                      % (1 + len(ent["dupes"])))
    if ent.get("gender") in (None, "", "unknown"):
        return True, "รู้ผู้พูดแต่เพศยังพิสูจน์ไม่ได้ — ห้ามเดา ให้แปลกลางเพศ"
    if ent.get("gender") == "conflict" or ent.get("gender_confidence") == "conflict":
        return True, "หลักฐานเพศขัดกันเอง — แปลกลางเพศจนกว่าจะมีคนยืนยัน"
    return False, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--find", help="ค้นข้อความ EN ตรง ๆ")
    a = ap.parse_args()

    idx = build_index()
    print("ข้อความที่รู้ผู้พูด: %s" % format(len(idx), ","))

    if a.find:
        ent = idx.get(a.find)
        neutral, why = decide_neutral(ent)
        print(json.dumps({"context": ent, "neutral": neutral, "why": why},
                         ensure_ascii=False, indent=1))
        return 0

    unique = load(UNIQUE, {}) or {}
    batches = sorted(paths.WORKLIST.glob("batch_*.json"))
    batches = [b for b in batches if not b.name.endswith(".context.json")]
    if not batches:
        print("ไม่พบ batch ใน %s — รัน make_worklist.py ก่อน" % paths.WORKLIST)
        return 2

    stat = collections.Counter()
    per_batch = []
    for bf in batches:
        data = json.load(io.open(bf, encoding="utf-8"))
        ctx = collections.OrderedDict()
        n_neutral = 0
        for en in data.get("strings", {}):
            ent = idx.get(en)
            neutral, why = decide_neutral(ent)
            n_neutral += neutral
            rec = collections.OrderedDict()
            rec["speaker"] = (ent or {}).get("speaker", "")
            rec["gender"] = (ent or {}).get("gender", "unknown")
            rec["gender_confidence"] = (ent or {}).get("gender_confidence", "none")
            rec["neutral"] = neutral
            if why:
                rec["why_neutral"] = why
            if (ent or {}).get("dupes"):
                rec["dupes"] = ent["dupes"]
            if (ent or {}).get("chapter"):
                rec["chapter"] = ent["chapter"]
            if (ent or {}).get("source"):
                rec["source"] = ent["source"]
            rec["bins"] = (unique.get(en) or {}).get("bins", [])[:4]
            ctx[en] = rec
            stat["neutral" if neutral else "gendered"] += 1
            stat["speaker_known" if rec["speaker"] else "speaker_unknown"] += 1
        per_batch.append((bf.name, len(ctx), n_neutral))
        if a.write:
            out = bf.with_suffix("")
            out = out.with_name(out.name + ".context.json")
            io.open(out, "w", encoding="utf-8", newline="\n").write(
                json.dumps(ctx, ensure_ascii=False, indent=1) + "\n")

    total = stat["neutral"] + stat["gendered"]
    print("string ในคิว %s · ต้องแปลกลางเพศ %s (%.0f%%) · รู้ตัวผู้พูด %s"
          % (format(total, ","), format(stat["neutral"], ","),
             100.0 * stat["neutral"] / max(total, 1), format(stat["speaker_known"], ",")))
    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์ .context.json ข้าง batch ทุกไฟล์)")
        return 0

    L = ["# บริบทผู้พูด/เพศ ของทุก batch — Lost Judgment", "",
         "> สร้างด้วย `python scripts/make_batch_context.py --write` ·",
         "> ไฟล์คู่: `translations/worklist/batch_NNN.context.json`", "",
         "**วิธีใช้ (นักแปลอ่านตรงนี้ก่อนเริ่ม batch):**", "",
         "1. เปิด `batch_NNN.json` คู่กับ `batch_NNN.context.json` เสมอ",
         "2. บรรทัดที่ `neutral: true` → **ห้าม ผม/ดิฉัน · ห้าม ครับ/ค่ะ** (ดูวิธีเขียนใน PRONOUN_MATRIX §1.3)",
         "3. บรรทัดที่มี `speaker` + `gender` → เปิด `characters_main.json` หาสรรพนามที่ล็อกไว้ของคนนั้น",
         "4. `gender_confidence: medium-conflict` = ใช้ได้แต่ถ้าอ่านบทแล้วขัด ให้ถอยไปกลางเพศแล้วแจ้ง lead",
         "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| string ในคิวทั้งหมด | %s |" % format(total, ","),
         "| ต้องแปลกลางเพศ | %s (%.0f%%) |" % (format(stat["neutral"], ","),
                                               100.0 * stat["neutral"] / max(total, 1)),
         "| ระบุเพศได้ (ใส่ ครับ/ค่ะ ได้) | %s |" % format(stat["gendered"], ","),
         "| รู้ตัวผู้พูด | %s |" % format(stat["speaker_known"], ","),
         "", "## รายละเอียดรายไฟล์", "",
         "| batch | strings | ต้องกลางเพศ |", "|---|---:|---:|"]
    for name, n, nn in per_batch:
        L.append("| `%s` | %d | %d |" % (name, n, nn))
    io.open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน context %d ไฟล์ + %s" % (len(per_batch), REPORT))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
