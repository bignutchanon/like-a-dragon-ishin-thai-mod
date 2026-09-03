#!/usr/bin/env python3
"""สร้างไฟล์บริบทคู่กับทุก batch — ใครพูดบรรทัดนี้ · เพศ · ต้องแปลกลางเพศไหม · อยู่บทไหน

ทำไมต้องมี: ภาษาไทยบังคับให้รู้เพศผู้พูดตั้งแต่คำแรก (ขอรับ/เจ้าค่ะ · ข้า/กระผม) แต่ต้นฉบับอังกฤษ
ไม่บอกอะไรเลย ถ้าเดาผิดจะเห็นทันทีบนจอและแก้ทีหลังแพงมาก
กติกาของทุกโปรเจกต์ในสายนี้: **พิสูจน์ไม่ได้ = แปลกลางเพศ ห้ามเดา**

ผู้พูดของแต่ละสตริงมาจากไหน (ทุกทางเป็นการจับคู่ในไฟล์เกม ไม่ใช่การอ่านเนื้อความแล้วเดา):
  locres คัตซีน     namespace `X` คู่กับ `X_speaker` คีย์ต่อคีย์ — ชี้ขาดรายบรรทัด
  ARMP NPC          `sound_speak_data.bin` มีคอลัมน์ `speaker` อยู่ในแถวเดียวกับ `message`
  .msg              คิวเสียง opcode 0x03 — นับเฉพาะแถวที่คิว **ชี้ขาด** (คิวเดียว ใช้แถวเดียว)
                    เหตุผลที่ต้องเข้มขนาดนี้อยู่ใน scripts/build_speaker_gender.py

เพศของผู้พูดอ่านจาก `translations/speakers.json` (สร้างโดย build_speaker_gender.py)

สตริงหนึ่งอาจถูกใช้ซ้ำโดยผู้พูดหลายคน — ถ้าเพศไม่ตรงกันจะบังคับ `neutral: true` เสมอ

ผลลัพธ์: translations/worklist/batch_*.context.json (ไฟล์คู่ ชื่อเดียวกับ batch)

ใช้: python scripts/make_batch_context_ishin.py
ต้องมีมาก่อน: make_worklist_ishin.py · build_speaker_gender.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # console Windows = cp1252 (กติกาข้อ 5)
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                            # noqa: E402

PARALLEL = paths.EXTRACTED / "parallel"
CUE_RE = re.compile(r"^([a-z][a-z0-9]{1,15})_[a-z0-9_]+$")
NOT_SPEAKER = {"kaiwabgm", "bgm", "se", "voice", "sys", "system", "minig", "mini",
               "2d", "3d", "arasuji", "telop", "sub", "common", "cmn", "test", "dummy"}
NAME_RE = re.compile(r"^[A-Z][A-Za-z'’ -]{1,30}$")
NOT_A_NAME = re.compile(r"^(Talk_|TLK_|C\d|P_|M_|F_|Idle|Player|Never|Dummy)", re.I)
# บทของเนื้อเรื่องอยู่ในชื่อ namespace/คิว: `s_c01_010` · `otose_adv_c02_150_001`
CHAPTER_RE = re.compile(r"(?:^|_)c(\d{2})(?:_|$)")


def load_speakers():
    """คืน ({ชื่อผู้พูด: เพศ}, {id คิว: ชื่อผู้พูด})

    เพศเอาจากสองไฟล์ซ้อนกัน — `characters.json` (มีหลักฐานจากประวัติในแผนผัง ซึ่งแข็งกว่า)
    ทับ `speakers.json` (เครื่องหมายภาษาญี่ปุ่น)
    """
    p = paths.TRANSLATIONS / "speakers.json"
    if not p.exists():
        sys.exit("ยังไม่มี %s — รัน scripts/build_speaker_gender.py ก่อน" % p)
    reg = json.loads(p.read_text(encoding="utf-8"))
    gender = {name: e.get("gender", "unknown") for name, e in reg.items()}
    by_id = {e["id"]: name for name, e in reg.items() if e.get("id")}

    cp = paths.TRANSLATIONS / "characters.json"
    if cp.exists():
        chars = json.loads(cp.read_text(encoding="utf-8")).get("main", {})
        for full, c in chars.items():
            if c.get("gender", "unknown") == "unknown":
                continue
            for key in (c.get("short"), full):
                if key:
                    gender[key] = c["gender"]
            if c.get("cue_id"):
                by_id.setdefault(c["cue_id"], c.get("short") or full)
    else:
        print("!! ยังไม่มี characters.json — รัน build_characters.py จะได้เพศแม่นขึ้น")
    return gender, by_id


def chapter_of(s):
    m = CHAPTER_RE.search(s or "")
    return int(m.group(1)) if m else None


def map_locres(acc):
    en = json.loads((paths.EXTRACTED / "locres" / "Game.en.json").read_text(encoding="utf-8"))
    S = en["strings"]
    flat, speakers = {}, {}
    for ns in en["namespaces"]:
        for e in ns["entries"]:
            (speakers if ns["ns"].endswith("_speaker") else flat)[(ns["ns"], e["key"])] = S[e["idx"]]
    for (ns, key), text in flat.items():
        sp = speakers.get((ns + "_speaker", key))
        acc[text].append((sp, chapter_of(ns), "locres:" + ns))


def map_speak_data(acc):
    p = paths.EXTRACTED / "db_en" / "sound_speak_data.bin.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for k in d:
        if not k.isdigit() or not isinstance(d[k], dict):
            continue
        for row in d[k].values():
            if isinstance(row, dict) and row.get("message"):
                acc[row["message"]].append(
                    (row.get("speaker"), None, "armp:sound_speak_data"))


def map_msg(acc, by_id):
    """ผู้พูดของบท .msg — จากคำสั่ง 0x03 ชนิดย่อย 0x35 ("เล่นเสียงบรรทัดนี้") เท่านั้น

    label ที่มันชี้เป็นได้สองรูป: ชื่อคิวเสียงโรมาจิที่ฝัง id ผู้พูดไว้หน้าสุด
    หรือ **ชื่อผู้พูดบนจอตรง ๆ** — เหตุผลที่ใช้ตัวนี้ตัวเดียวอยู่ใน tools/msg.py
    """
    rows = json.loads((PARALLEL / "msg.json").read_text(encoding="utf-8"))
    for r in rows:
        if not r["en"]:
            continue
        voice = r.get("voice")
        name = ch = None
        if voice:
            m = CUE_RE.match(voice)
            if m and m.group(1) not in NOT_SPEAKER:
                name = by_id.get(m.group(1)) or ("id:" + m.group(1))
                ch = chapter_of(voice)
            elif not m and NAME_RE.match(voice) and not NOT_A_NAME.match(voice):
                name = voice
        acc[r["en"]].append((name, ch, "msg:" + r["file"]))


def evidence_gender(en, ja):
    """เพศที่ **พิสูจน์ได้จากไฟล์เกม** นอกเหนือจากป้ายผู้พูด — ใช้เติมข้อมูลให้นักแปลเห็นตั้งแต่แรก

    ชั้น `.msg` รู้ป้ายผู้พูดแค่ส่วนน้อย ไฟล์บริบทจึงตี `neutral: true` เกือบทั้งชั้น
    ทั้งที่ `merge_qc.py` ด่าน G รู้จักหลักฐานอีกสามชั้นอยู่แล้ว ผลคือนักแปลเขียนกลางเพศไว้ก่อน
    แล้วผู้ตรวจต้องมาไล่เติมคำลงท้ายคืนทีหลัง (คลื่น MSG_031 เติมคืน 25 บรรทัด)

    ⚠ ฟังก์ชันนี้ **ไม่แตะช่อง `neutral`** — ด่าน G ยังเป็นคนตัดสินเหมือนเดิม
    ที่เพิ่มคือช่อง `evidence_gender` ที่บอกนักแปลว่า "ถ้าจะใส่คำลงท้าย มีหลักฐานรองรับอยู่ชั้นไหน"
    """
    import merge_qc as M                      # โหลดตอนเรียกเพื่อไม่ให้ import วน

    g = M.line_gender(en)
    if g:
        return {"gender": g, "from": "lead", "why": "translations/gender_lines.json"}
    g = M.ja_gender(ja or "")
    if g:
        return {"gender": g, "from": "ja_line", "why": "เครื่องหมายเพศในต้นฉบับของบรรทัดนี้เอง"}
    g = M.scene_gender(en)
    if g:
        return {"gender": g, "from": "scene",
                "why": ("ทั้งไฟล์ฉากมีเครื่องหมายเพศเดียวล้วน — **ตรวจก่อนใช้** "
                        "ฉากหลายคนพูดอาจยืมเพศจากตัวละครอื่น")}
    return None


def decide(entries, gender_of):
    """สรุปผู้พูด/เพศของสตริงหนึ่ง จากทุกที่ที่สตริงนั้นถูกใช้"""
    names = Counter(n for n, _, _ in entries if n)
    chapters = sorted({c for _, c, _ in entries if c})
    n_no_speaker = sum(1 for n, _, _ in entries if not n)

    if not names:
        return {"speakers": [], "gender": "unknown", "neutral": True,
                "why_neutral": "ไม่มีข้อมูลผู้พูดในไฟล์เกม", "chapters": chapters}

    genders = {gender_of.get(n, "unknown") for n in names}
    sp = [{"name": n, "gender": gender_of.get(n, "unknown"), "uses": c}
          for n, c in names.most_common(6)]

    if n_no_speaker:
        return {"speakers": sp, "gender": "unknown", "neutral": True,
                "why_neutral": "สตริงเดียวกันถูกใช้ในที่ที่ไม่รู้ผู้พูดด้วย (%d จุด)" % n_no_speaker,
                "chapters": chapters}
    if len(names) > 1 and len(genders - {"unknown"}) > 1:
        return {"speakers": sp, "gender": "mixed", "neutral": True,
                "why_neutral": "ผู้พูดหลายคนคนละเพศใช้ข้อความเดียวกัน", "chapters": chapters}
    if genders == {"unknown"}:
        return {"speakers": sp, "gender": "unknown", "neutral": True,
                "why_neutral": "พิสูจน์เพศผู้พูดจากไฟล์เกมไม่ได้", "chapters": chapters}

    g = next(iter(genders - {"unknown"}))
    if "unknown" in genders:
        return {"speakers": sp, "gender": "unknown", "neutral": True,
                "why_neutral": "ผู้พูดบางคนพิสูจน์เพศไม่ได้", "chapters": chapters}
    return {"speakers": sp, "gender": g, "neutral": False,
            "why_neutral": None, "chapters": chapters}


def main():
    gender_of, by_id = load_speakers()

    acc = defaultdict(list)
    map_locres(acc)
    map_speak_data(acc)
    map_msg(acc, by_id)
    print("สตริงที่หาแหล่งใช้งานได้: %s" % f"{len(acc):,}")

    # ⚠ `batch_*.json` จับไฟล์คู่ที่ sprint 9–10 เพิ่มเข้ามาด้วย (.todo · .prior · .dnt)
    # รอบ 3 ก.ย. 2026 เขียนไฟล์บริบทเกินมา 258 ไฟล์เพราะ glob นี้ — ต้องรับเฉพาะ worklist จริง
    SIDECARS = (".context.json", ".todo.json", ".prior.json", ".dnt.json")
    batches = sorted(b for b in paths.WORKLIST.glob("batch_*.json")
                     if not b.name.endswith(SIDECARS))
    if not batches:
        sys.exit("ยังไม่มี batch — รัน scripts/make_worklist_ishin.py ก่อน")

    tally = Counter()
    for bf in batches:
        data = json.loads(bf.read_text(encoding="utf-8"))
        ja = data.get("ref_ja") or {}
        ctx = {}
        for en in data.get("strings", {}):
            info = decide(acc.get(en, []), gender_of)
            info["ja"] = ja.get(en)
            info["occurrences"] = len(acc.get(en, []))
            if info["neutral"]:
                ev = evidence_gender(en, info["ja"])
                if ev:
                    info["evidence_gender"] = ev
                    tally["evidence:" + ev["from"]] += 1
            ctx[en] = info
            tally[info["gender"]] += 1
            tally["neutral" if info["neutral"] else "gendered"] += 1
        out = bf.with_name(bf.stem + ".context.json")
        out.write_text(json.dumps({
            "batch": bf.name,
            "readme": ("ไฟล์คู่ของ batch — เปิดพร้อมกันเสมอ · neutral:true = ไม่มีป้ายผู้พูดที่พิสูจน์เพศได้ "
                       "ให้เขียนแบบกลางเพศตาม PRONOUN_MATRIX §1.3 · "
                       "**ยกเว้นบรรทัดที่มีช่อง evidence_gender** ซึ่งแปลว่ามีหลักฐานจากไฟล์เกมชั้นอื่นรองรับ "
                       "(from=lead > ja_line > scene) — ชั้น scene ต้องอ่านฉากก่อนใช้ เพราะอาจยืมเพศจากตัวละครอื่น"),
            "lines": ctx,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    total = tally["gendered"] + tally["neutral"]
    print("เขียนไฟล์บริบท %d ไฟล์ · สตริงรวม %s" % (len(batches), f"{total:,}"))
    print("  รู้เพศผู้พูด  : %s (%.0f%%) — ชาย %s · หญิง %s"
          % (f"{tally['gendered']:,}", 100 * tally["gendered"] / max(total, 1),
             f"{tally['male']:,}", f"{tally['female']:,}"))
    print("  ต้องกลางเพศ  : %s (%.0f%%)"
          % (f"{tally['neutral']:,}", 100 * tally["neutral"] / max(total, 1)))
    ev_total = sum(v for k, v in tally.items() if k.startswith("evidence:"))
    if ev_total:
        print("  ในนั้นมีหลักฐานเพศชั้นอื่นรองรับ: %s (lead %s · บรรทัดเอง %s · ระดับฉาก %s)"
              % (f"{ev_total:,}", f"{tally['evidence:lead']:,}",
                 f"{tally['evidence:ja_line']:,}", f"{tally['evidence:scene']:,}"))
    print("-> %s" % paths.WORKLIST)


if __name__ == "__main__":
    main()
