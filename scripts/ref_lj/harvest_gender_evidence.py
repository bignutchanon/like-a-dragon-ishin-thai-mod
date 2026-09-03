#!/usr/bin/env python3
"""เก็บ "หลักฐานเพศ" ของผู้พูดทุกคนจากไฟล์เกมโดยตรง — ไม่เดาจากชื่อ

ทำไมต้องมี: ระบบสรรพนามไทยผูกกับเพศ (ผม/ดิฉัน · ครับ/ค่ะ) เดาผิด = บทพูดผิดทั้งบรรทัด
กติกา PRONOUN_MATRIX §0.1 บังคับว่า "เพศไม่ชัด = แปลกลาง ๆ" ดังนั้นต้องรู้ให้ชัดว่า
ใคร **พิสูจน์ได้** ใคร **ยังไม่ได้** แล้วส่งรายชื่อให้ทีมแปลใช้ตัดสินใจรายบรรทัด

ลำดับความน่าเชื่อของหลักฐาน (สูง -> ต่ำ):
  1. voicer    — `sound_voicer.bin` คอลัมน์ `sex` (1=ชาย 2=หญิง) = ข้อมูลของทีมสร้างเกมเอง
               (เทียบด้วย **ชื่อ** ผู้พูด จึงใช้ได้เฉพาะตัวละครที่ชื่อในเกมตรงกับชื่อแถว voicer)
  1b. voice_cue — ชั้นเดียวกับ voicer แต่ผูก **รายบรรทัด**: ชื่อคิวเสียงใน `sound_auth.bin`
               ลงท้ายด้วย id ของ voicer (ดู `scripts/make_cue_gender.py` · ครอบคลุม 15,619/15,622 บรรทัด)
               ช่องนี้แก้ปัญหา NPC ที่ชื่อเป็นคำบรรยาย ("Rugged Thug"/"Siren Owner") ซึ่งเทียบชื่อตรง ๆ ไม่ได้
  2. pronoun — มี he/him/his หรือ she/her/hers ในบรรทัด EN ที่พูดถึงชื่อนั้น
               (นับเฉพาะบรรทัดที่มีชื่อตัวละครที่รู้จัก **ชื่อเดียว** กันสับสน)
  3. title   — Mr./Ms./Mrs./Miss/sir/ma'am/ma am นำหน้าหรือกำกับชื่อนั้น
  4. role    — คำบอกบทบาทที่ผูกเพศชัด (father/son/brother/boyfriend ↔ mother/daughter/sister ...)

ตัดสิน:
  - หลักฐาน voicer มี = ใช้ voicer ทันที (confidence "high", source "voicer")
  - ไม่มี voicer: นับคะแนนชาย/หญิงจากข้อ 2-4 ถ้าฝั่งหนึ่งชนะขาด (>=2 ชิ้น และอีกฝั่ง 0)
    -> "high"; ชนะ 1-0 -> "medium"; ขัดกันเอง หรือไม่มีเลย -> "unknown" (ทีมแปลต้องเลี่ยงสรรพนาม)

ผลลัพธ์:
  extracted/facts/gender_evidence.json   {speaker: {gender, confidence, source, evidence[]}}
  docs/reference/gender_evidence_lj.md   ตารางอ่านคน + รายชื่อที่ยังพิสูจน์ไม่ได้

ใช้:  python scripts/harvest_gender_evidence.py [--write] [--max-quotes 3]
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

TALK_SPEAKER = paths.EXTRACTED / "facts" / "talk_speaker.json"
VOICER = paths.EXTRACTED / "facts" / "voicer_gender.json"
CUE = paths.EXTRACTED / "facts" / "cue_gender.json"
SPEECH_MAP = paths.EXTRACTED / "facts" / "speech_speaker_map.json"
SPEECH_SPEAKER = paths.EXTRACTED / "facts" / "speech_speaker.json"
AUTH_SPEAKER = paths.EXTRACTED / "facts" / "auth_speaker.json"
UNIQUE = paths.EXTRACTED / "unique_strings.json"
OUT_JSON = paths.EXTRACTED / "facts" / "gender_evidence.json"
OUT_MD = paths.DOCS / "reference" / "gender_evidence_lj.md"

MALE_PRON = re.compile(r"\b(he|him|his|himself)\b", re.I)
FEMALE_PRON = re.compile(r"\b(she|her|hers|herself)\b", re.I)
MALE_TITLE = re.compile(r"\b(mr\.?|sir|mister)\b", re.I)
FEMALE_TITLE = re.compile(r"\b(ms\.?|mrs\.?|miss|ma'am|madam|madame)\b", re.I)
MALE_ROLE = re.compile(r"\b(father|dad|son|brother|boyfriend|husband|uncle|grandfather|"
                       r"boy|guy|man|men|gentleman|nephew|king|businessman|schoolboy)\b", re.I)
FEMALE_ROLE = re.compile(r"\b(mother|mom|daughter|sister|girlfriend|wife|aunt|grandmother|"
                         r"girl|lady|woman|women|hostess|niece|queen|schoolgirl|actress)\b", re.I)

# ⚠ กันบั๊กชั้นที่สอง (แก้ 26 ส.ค. 2026 · ผู้ตรวจ batch_083 จับได้จากเคส `hiyori`)
# บรรทัดที่เอ่ยชื่อคนหนึ่ง **ในบุรุษที่สาม** แต่คำบอกเพศอยู่ในประโยค **บุรุษที่หนึ่ง**
# = คำนั้นบรรยาย "คนพูด" ไม่ใช่ "คนที่ถูกเอ่ยชื่อ" — เอามาตัดสินเพศเจ้าของชื่อไม่ได้
# ของจริง: "I'm no fireworks maker, I'm a homeless **guy** with no education.
#           I don't have what it takes to make **Hiyori-san** happy..."
# ผู้พูดคือแฟนหนุ่มของฮิโยริ แต่สคริปต์เอา "guy" ไปตีตราฮิโยริว่าชาย ทั้งที่บทของเธอเอง
# ("Hehehe. Aw, Junpei-kun.") อ่านเป็นหญิงชัด — บั๊กชั้นเดียวกับเคส Mamiya/Ehara เดิม
FIRST_PERSON_NEAR = re.compile(r"\b(i'?m|i am|i'?ve|my|me)\b[^.?!]{0,60}$", re.I)


def first_person_clause(text, pos):
    """คำบอกเพศที่ตำแหน่ง pos อยู่ในประโยคบุรุษที่หนึ่งหรือไม่"""
    return bool(FIRST_PERSON_NEAR.search(text[:pos]))


# ชื่อผู้พูดที่ไม่ใช่ตัวละคร (แถวระบบ/ทดสอบ) — ข้ามไปเลย
SKIP_NAMES = {"", "test", "player", "switch test"}

# คำในชื่อผู้พูดที่บอกเพศอยู่ในตัวเอง (ชื่อบรรยาย เช่น "Suspicious Man", "Young Woman")
SELF_MALE = re.compile(r"\b(man|boy|guy|male|father|dad|son|brother|husband|uncle|"
                       r"grandpa|grandfather|mister|mr|gentleman|schoolboy|salaryman)\b", re.I)
SELF_FEMALE = re.compile(r"\b(woman|girl|lady|female|mother|mom|daughter|sister|wife|aunt|"
                         r"grandma|grandmother|miss|mrs|ms|hostess|schoolgirl|actress|"
                         r"waitress)\b", re.I)


def load(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(io.open(p, encoding="utf-8"), object_pairs_hook=collections.OrderedDict)


def norm(name):
    return re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")


def collect_speakers():
    """คืน ({ชื่อผู้พูด: จำนวนบรรทัด}, {ชื่อ: ที่มา}) จากสองแหล่ง

    - `talk.bin` (บทเดินเมือง/เควสเสริม) — ชื่อผู้พูดเป็นชื่อคนแบบ EN ("Okitegawa")
    - `sound_auth.bin` (บทคัตซีนมีเสียงพากย์) — ชื่อผู้พูดเป็น token ของคีย์เสียง ("kuwana")
      แหล่งนี้สำคัญเพราะตัวละครเนื้อเรื่องหลักแทบไม่โผล่ใน talk.bin เลย
    """
    counts = collections.Counter()
    where = {}
    ts = load(TALK_SPEAKER, {}) or {}
    for rec in ts.values():
        for r in [rec] + list(rec.get("dupes", [])):
            n = (r.get("speaker") or "").strip()
            if n and n.lower() not in SKIP_NAMES:
                counts[n] += 1
                where.setdefault(n, "talk.bin")

    # ผู้พูดรายบรรทัดของคัตซีน (จากคอลัมน์ "3" ของ sound_auth = id ใน talk_talker)
    ss = load(SPEECH_SPEAKER, {}) or {}
    for rec in ss.values():
        for r in [rec] + list(rec.get("dupes", [])):
            n = (r.get("speaker") or "").strip()
            if n and n.lower() not in SKIP_NAMES:
                counts[n] += 1
                where.setdefault(n, "sound_auth.bin(talker)")

    # ซับทับคัตซีนของ auth.bin (คอลัมน์ "8" = id ใน talk_talker) — 5,136 บรรทัด
    aus = load(AUTH_SPEAKER, {}) or {}
    for rec in aus.values():
        for r in [rec] + list(rec.get("dupes", [])):
            n = (r.get("speaker") or "").strip()
            if n and n.lower() not in SKIP_NAMES:
                counts[n] += 1
                where.setdefault(n, "auth.bin(cinema_telop)")

    sm = load(SPEECH_MAP, {}) or {}
    for rec in sm.values():
        toks = list(rec.get("speaker_exact") or []) or list(rec.get("speaker") or [])
        for t in toks:
            t = (t or "").strip()
            if not t or t.lower() in SKIP_NAMES or len(t) < 3:
                continue
            counts[t] += 1
            where.setdefault(t, "sound_auth.bin")
    return counts, where


def build_name_index(names):
    """regex หา 'ชื่อ' ในข้อความ EN (ขอบเขตคำ + รองรับ -san/-kun/-chan/'s)"""
    idx = {}
    for n in names:
        # token ของ sound_auth ("dlc_g02_kaito") ไม่เคยโผล่ในบทพูด EN — ค้นไปก็เจอแต่ noise
        if len(n) < 3 or "_" in n or any(ch.isdigit() for ch in n):
            continue
        idx[n] = re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", re.I)
    return idx


def harvest(names, texts, max_quotes):
    """เดินทุกข้อความ EN เก็บหลักฐานเข้าแต่ละชื่อ (เฉพาะบรรทัดที่มีชื่อที่รู้จักชื่อเดียว)"""
    idx = build_name_index(names)
    ev = {n: [] for n in names}
    for text in texts:
        if len(text) < 8:
            continue
        hit = [n for n, rx in idx.items() if rx.search(text)]
        if len(hit) != 1:          # 0 = ไม่เกี่ยว · >1 = ชี้ไม่ชัดว่าสรรพนามหมายถึงใคร
            continue
        n = hit[0]
        if len(ev[n]) >= max_quotes * 4:
            continue
        for kind, rxm, rxf in (("pronoun", MALE_PRON, FEMALE_PRON),
                               ("title", MALE_TITLE, FEMALE_TITLE),
                               ("role", MALE_ROLE, FEMALE_ROLE)):
            mm, mf = rxm.search(text), rxf.search(text)
            # คำบอกเพศที่อยู่ในประโยคบุรุษที่หนึ่ง = บรรยายคนพูด ไม่ใช่เจ้าของชื่อ (ดูหมายเหตุด้านบน)
            if mm and first_person_clause(text, mm.start()):
                mm = None
            if mf and first_person_clause(text, mf.start()):
                mf = None
            m, f = bool(mm), bool(mf)
            if m ^ f:              # ชิ้นไหนชี้สองทางพร้อมกันในบรรทัดเดียว = ทิ้ง
                ev[n].append({"type": kind, "gender": "male" if m else "female",
                              "quote": text[:200]})
    return ev


# คำนำหน้าของคีย์เสียงที่ไม่ใช่ชื่อคน (บท/DLC/ฉาก) — ตัดทิ้งก่อนเทียบกับตาราง voicer
PREFIX_RE = re.compile(r"^(dlc(_g)?(_[gm])?_?\d*_?|g\d+_|m\d+_|dgmb\d+_|btl\d*_|hact\d*_)+")


# ชื่อผู้พูดใน talk_talker กับคีย์ใน sound_voicer สะกดคนละแบบ (ทับศัพท์คนละรูป)
# ใส่ได้เฉพาะคู่ที่ **ยืนยันแล้วว่าเป็นคนเดียวกัน** — ห้ามเดาจากชื่อคล้าย
ALIASES = {
    "soma": "souma",     # 相馬/そうま — talk_talker เขียน "Soma" · voicer เขียน "souma"
}


def lookup_voicer(name, voicer_g):
    """เทียบชื่อผู้พูดกับตาราง sound_voicer (ลองตัดคำนำหน้าบท/DLC ออกทีละชั้น)"""
    cands = [norm(name), norm(name).replace("_", "")]
    if norm(name) in ALIASES:
        cands.insert(0, ALIASES[norm(name)])
    stripped = PREFIX_RE.sub("", norm(name))
    if stripped and stripped != norm(name):
        cands += [stripped, stripped.replace("_", "")]
    parts = norm(name).split("_")
    if len(parts) > 1:
        cands.append(parts[-1])          # หางคีย์มักเป็นชื่อคน (dlc_g02_kaito -> kaito)
        cands.append("_".join(parts[-2:]))
    for c in cands:
        if c and len(c) >= 3 and c in voicer_g:
            return voicer_g[c]
    return None


def decide(name, voicer_g, quotes, max_quotes, cue_g=None):
    """ตัดสินเพศ + confidence จากหลักฐานทั้งหมดของชื่อนี้"""
    out = {"gender": "unknown", "confidence": "none", "source": "none", "evidence": []}
    vg = lookup_voicer(name, voicer_g)
    if vg:
        out.update(gender=vg, confidence="high", source="voicer",
                   evidence=[{"type": "voicer", "gender": vg,
                              "quote": "sound_voicer.bin: sex=%s" % ("1" if vg == "male" else "2")}])
        return out

    # หลักฐานชั้นเดียวกับ voicer แต่ผูกรายบรรทัด: คิวเสียงของบทพูดชี้ไปยังแถว voicer ตรง ๆ
    # (ดู scripts/make_cue_gender.py) — ครอบคลุม NPC ที่ชื่อเป็นคำบรรยายซึ่งเทียบชื่อตรง ๆ ไม่ได้
    cue = (cue_g or {}).get(name)
    if cue and cue.get("gender") in ("male", "female"):
        v = cue.get("votes", {})
        m, f = v.get("male", 0), v.get("female", 0)
        hi, lo = max(m, f), min(m, f)
        if lo == 0 or hi >= lo * 3:
            q = "sound_auth.bin: คิวเสียง %s -> sound_voicer sex (ชาย %d : หญิง %d)" % (
                cue.get("example_cue", ""), m, f)
            if cue.get("voice_types"):
                q += " · voice_type=%s" % ", ".join(cue["voice_types"])
            # เสียงล้วนเพศเดียว = เชื่อได้เต็ม (ตรวจสอบแล้ว 70/70 ตรงกับช่อง voicer ที่จับคู่ด้วยชื่อ)
            # เสียงปนแต่ฝั่งหนึ่งชนะขาด = อาจเป็นชื่อที่ใช้ร่วมกันหลายคน -> ลด confidence ให้ทีมแปลรู้ตัว
            out.update(gender=cue["gender"],
                       confidence="high" if lo == 0 else "medium-conflict",
                       source="voice_cue" if lo == 0 else "voice_cue(majority %d:%d)" % (hi, lo),
                       evidence=[{"type": "voice_cue", "gender": cue["gender"], "quote": q}])
            return out
        # เสียงชาย/หญิงปนกันจริง = ชื่อผู้พูดนี้ใช้ร่วมกันหลายคน -> ต้องแปลกลางเพศ
        out.update(confidence="conflict", source="voice_cue(mixed)",
                   evidence=[{"type": "voice_cue", "gender": "unknown",
                              "quote": "คิวเสียงปนสองเพศ (ชาย %d : หญิง %d) = ชื่อนี้ใช้ร่วมกันหลายคน" % (m, f)}])
        return out

    # ชื่อบรรยายที่บอกเพศในตัวเอง (Suspicious Man / Young Woman) = หลักฐานระดับ title
    self_m, self_f = bool(SELF_MALE.search(name)), bool(SELF_FEMALE.search(name))
    if self_m ^ self_f:
        quotes = list(quotes) + [{"type": "name", "gender": "male" if self_m else "female",
                                  "quote": "ชื่อผู้พูดในไฟล์เกมระบุเพศเอง: %s" % name}]

    dossier = [q for q in quotes if q["type"] == "dossier"]
    if dossier and len({q["gender"] for q in dossier}) == 1:
        g = dossier[0]["gender"]
        out.update(gender=g, confidence="high", source="dossier",
                   evidence=dossier[:max_quotes])
        return out

    score = collections.Counter(q["gender"] for q in quotes)
    m, f = score["male"], score["female"]
    if m and f:
        # ขัดกันเอง — เกิดได้ตามปกติเพราะบรรทัดที่เอ่ยชื่อ A อาจพูดถึงคน B ด้วย (he/she ปนกัน)
        # ถ้าฝั่งหนึ่ง **ชนะขาด** (>=3 ชิ้น และมากกว่าอีกฝั่ง 3 เท่า) ให้ตัดสินตามเสียงข้างมาก
        # แต่ลด confidence เป็น "medium-conflict" เพื่อให้ทีมแปลรู้ว่ายังมีหลักฐานสวนอยู่
        hi, lo = max(m, f), min(m, f)
        if hi >= 3 and hi >= lo * 3:
            g = "male" if m > f else "female"
            out.update(gender=g, confidence="medium-conflict",
                       source="majority(%d:%d)" % (hi, lo),
                       evidence=[q for q in quotes if q["gender"] == g][:max_quotes])
            return out
        out["evidence"] = quotes[:max_quotes * 2]
        out["confidence"] = "conflict"
        return out
    if not (m or f):
        return out
    g = "male" if m else "female"
    n = max(m, f)
    kinds = {q["type"] for q in quotes if q["gender"] == g}
    conf = "high" if ("dossier" in kinds or (n >= 2 and ("pronoun" in kinds or "title" in kinds or "name" in kinds))) else "medium"
    out.update(gender=g, confidence=conf,
               source="+".join(sorted(kinds)),
               evidence=[q for q in quotes if q["gender"] == g][:max_quotes])
    return out


def add_dossier_evidence(quotes, names):
    """หลักฐานจาก **แฟ้มคดีในเกม** (`evidence.bin` -> extracted/facts/evidence.json)

    แต่ละรายการคือคำอธิบายตัวบุคคลตรง ๆ ("A second-year student and captain of Seiryo High's
    dance club. ... **she** ...") จึงเป็นหลักฐานเพศที่แรงกว่าบทพูดทั่วไปที่บังเอิญเอ่ยชื่อ
    """
    p = paths.EXTRACTED / "facts" / "evidence.json"
    if not os.path.exists(p):
        return
    data = json.load(io.open(p, encoding="utf-8"))
    by_token = {}
    for n in names:
        by_token.setdefault(n.lower(), []).append(n)
    for rows in data.values():
        for r in rows:
            nm = re.sub(r"\s*\(.*?\)", "", (r.get("name") or "")).strip()
            desc = (r.get("desc") or "").strip()
            if not nm or len(desc) < 20:
                continue
            m, f = bool(MALE_PRON.search(desc)), bool(FEMALE_PRON.search(desc))
            if m == f:                    # ไม่มีสรรพนาม หรือมีทั้งสองแบบ = ใช้ไม่ได้
                continue
            g = "male" if m else "female"
            toks = {nm.lower()}
            parts = nm.split()
            if parts:
                toks.add(parts[-1].lower())
            for t in toks:
                for target in by_token.get(t, []):
                    quotes.setdefault(target, []).append(
                        {"type": "dossier", "gender": g,
                         "quote": "evidence.bin — %s: %s" % (nm, desc[:150])})


def add_dating_evidence(quotes, names):
    """หลักฐานจากตารางเนื้อเรื่อง: แถว `girlfriend_<ชื่อ>` ใน `scenario_summary`

    เควสสายเดตของภาคนี้ผูกกับตัวละครหญิงสี่คน — id ในไฟล์เกมบอกตรง ๆ ว่าใคร
    (เป็นหลักฐานจากไฟล์เกม ไม่ใช่การเดาจากชื่อ)
    """
    p = paths.EXTRACTED / "facts" / "scenario_summary.json"
    if not os.path.exists(p):
        return
    rows = json.load(io.open(p, encoding="utf-8"))
    by_lower = {n.lower(): n for n in names}
    for r in rows if isinstance(rows, list) else []:
        rid = (r.get("id") or "")
        if not rid.startswith("girlfriend_"):
            continue
        cands = [rid[len("girlfriend_"):]] + (r.get("title") or "").split()
        for c in cands:
            n = by_lower.get(c.strip(".,").lower())
            if n:
                quotes.setdefault(n, []).append(
                    {"type": "dating", "gender": "female",
                     "quote": "scenario_summary: %s = \"%s\" (เควสสายเดต)" % (rid, r.get("title"))})


def merge_name_variants(result, counts):
    """ยุบชื่อที่สะกดคนละแบบให้ใช้ผลเพศชุดเดียวกัน (ใช้ตาราง canon เดียวกับ make_batch_context)

    ที่มา (26 ส.ค. 2026): `mamiya` มี 367 บรรทัดแต่เพศเป็น unknown ทั้งที่แฟ้มคดีในเกมเขียน "her"
    ชัดเจน — เพราะหลักฐานไปกองอยู่ที่ `old_mamiya` ซึ่งถูกนับเป็นคนละคน
    วิธีแก้: จัดกลุ่มด้วย `canon()` แล้วให้ทุกตัวแปรในกลุ่มใช้ผลของตัวที่ **พิสูจน์เพศได้และมีบรรทัดมากที่สุด**
    (ยังคงคีย์ของทุกตัวแปรไว้ เพราะที่อื่นค้นด้วยชื่อดิบ)
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from make_batch_context import canon
    except Exception as e:  # noqa: BLE001 — ไม่มี canon ก็ยังทำงานต่อได้
        print("!! โหลด canon ไม่ได้ ข้ามการยุบชื่อ: %s" % e)
        return result

    groups = collections.defaultdict(list)
    for n in result:
        groups[canon(n)].append(n)

    merged = 0
    for key, variants in groups.items():
        if len(variants) < 2:
            continue
        best = None
        for n in variants:
            if result[n]["gender"] == "unknown":
                continue
            if best is None or counts[n] > counts[best]:
                best = n
        if best is None:
            continue
        for n in variants:
            if n == best or result[n]["gender"] != "unknown":
                continue
            src = result[best]
            result[n]["gender"] = src["gender"]
            result[n]["confidence"] = src["confidence"]
            result[n]["source"] = "%s (ยืมจาก \"%s\" — ชื่อเดียวกันสะกดคนละแบบ)" % (src.get("source", "?"), best)
            result[n]["evidence"] = list(src.get("evidence", []))[:2]
            merged += 1
    if merged:
        print("ยุบชื่อสะกดคนละแบบ: เติมเพศให้ %d รายการ" % merged)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--max-quotes", type=int, default=3)
    a = ap.parse_args()

    voicer_g = load(VOICER, {}) or {}
    voicer_g.pop("_meta", None)
    cue_g = load(CUE, {}) or {}
    cue_g.pop("_meta", None)
    counts, where = collect_speakers()
    names = list(counts)
    print("ผู้พูดที่มีชื่อ (talk.bin + sound_auth.bin + auth.bin): %d คน (%s บรรทัด)"
          % (len(names), format(sum(counts.values()), ",")))

    uniq = load(UNIQUE, {}) or {}
    texts = list(uniq.keys())
    print("ข้อความ EN ที่ใช้ค้นหลักฐาน: %s" % format(len(texts), ","))

    quotes = harvest(names, texts, a.max_quotes)
    add_dossier_evidence(quotes, names)
    add_dating_evidence(quotes, names)
    result = collections.OrderedDict()
    for n in sorted(names, key=lambda x: -counts[x]):
        rec = decide(n, voicer_g, quotes.get(n, []), a.max_quotes, cue_g)
        rec["lines"] = counts[n]
        rec["found_in"] = where.get(n, "?")
        result[n] = rec

    result = merge_name_variants(result, counts)

    stat = collections.Counter((r["gender"], r["confidence"]) for r in result.values())
    known = [n for n, r in result.items() if r["gender"] != "unknown"]
    unknown = [n for n, r in result.items() if r["gender"] == "unknown"]
    lines_known = sum(result[n]["lines"] for n in known)
    lines_all = sum(counts.values())
    print("พิสูจน์ได้ %d/%d คน (%.0f%% ของบรรทัด) · ยังไม่ได้ %d คน"
          % (len(known), len(names), 100.0 * lines_known / max(lines_all, 1), len(unknown)))
    for k, v in sorted(stat.items()):
        print("   %-8s %-8s %d" % (k[0], k[1], v))

    if not a.write:
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = collections.OrderedDict()
    payload["_meta"] = {
        "source": "scripts/harvest_gender_evidence.py",
        "inputs": ["extracted/facts/talk_speaker.json", "extracted/facts/speech_speaker.json",
                   "extracted/facts/auth_speaker.json", "extracted/facts/voicer_gender.json",
                   "extracted/facts/cue_gender.json",
                   "extracted/unique_strings.json"],
        "rule": "voicer > voice_cue > dossier > pronoun/title/name > role · ขัดกัน/ไม่มี = unknown = แปลกลางเพศ",
        "speakers": len(names), "known": len(known), "unknown": len(unknown),
    }
    payload.update(result)
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")

    L = ["# หลักฐานเพศผู้พูด — Lost Judgment", "",
         "> สร้างด้วย `python scripts/harvest_gender_evidence.py --write` ·",
         "> ข้อมูลดิบ: `extracted/facts/gender_evidence.json`", "",
         "**กติกาใช้งาน (บังคับ):** `unknown` หรือ `conflict` = **ห้ามใส่ ครับ/ค่ะ และห้ามใช้ ผม/ดิฉัน**",
         "ให้แปลกลางเพศตาม PRONOUN_MATRIX §0 (ใช้ \"ตัวเอง\" แทนคำแทนตัว หรือเลี่ยงสรรพนามทั้งประโยค)", "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| ผู้พูดที่มีชื่อ | %d |" % len(names),
         "| พิสูจน์เพศได้ | %d |" % len(known),
         "| ยังพิสูจน์ไม่ได้ (ต้องแปลกลาง) | %d |" % len(unknown),
         "| บรรทัดที่ผู้พูดรู้เพศแล้ว | %s / %s |" % (format(lines_known, ","), format(lines_all, ",")),
         "",
         "## ผู้พูดที่พิสูจน์เพศได้ (เรียงตามจำนวนบรรทัด)", "",
         "| ผู้พูด | เพศ | ความมั่นใจ | ที่มา | พบใน | บรรทัด | หลักฐาน |",
         "|---|---|---|---|---|---|---|"]
    for n in known:
        r = result[n]
        q = r["evidence"][0]["quote"].replace("|", "\\|").replace("\n", " ") if r["evidence"] else ""
        L.append("| %s | %s | %s | %s | %s | %d | %s |"
                 % (n, r["gender"], r["confidence"], r["source"], r["found_in"],
                    r["lines"], q[:90]))
    L += ["", "## ยังพิสูจน์ไม่ได้ — ต้องแปลกลางเพศ (เรียงตามจำนวนบรรทัด)", "",
          "| ผู้พูด | พบใน | บรรทัด | สถานะ |", "|---|---|---|---|"]
    for n in unknown:
        L.append("| %s | %s | %d | %s |" % (n, result[n]["found_in"],
                                            result[n]["lines"], result[n]["confidence"]))
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_MD, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("เขียน %s\nเขียน %s" % (OUT_JSON, OUT_MD))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
