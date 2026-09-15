#!/usr/bin/env python3
"""เพศผู้พูดรายบรรทัดจาก "คิวเสียงของบรรทัดนั้นเอง" — หลักฐานจากไฟล์เกมที่แม่นที่สุดของชั้น .msg

ที่มา: คำสั่ง 0x03 ชนิดย่อย 0x35 (research §9 · ช่อง `voice` ใน extracted/parallel/msg.json)
= "เล่นเสียงของบรรทัดนี้" มีอย่างมากหนึ่งตัวต่อบรรทัด ชี้คิวเสียงที่ฝังรหัสผู้พูดไว้หน้าสุด
(`haruka_door_s01_003`) หรือชื่อผู้พูดบนจอตรง ๆ (`Otose`)

⚠ research §10.1 เคยตีตกป้ายคิว `haruka_*`/`oryo_*` — แต่ตอนนั้นนับจาก `labels` ทั้งหมด ซึ่งมีป้ายค้าง
จากบรรทัดอื่น (ชนิดย่อย 0x16) · วัดใหม่เฉพาะช่อง `voice` (15 ก.ย. 2026 · `audit_voice_gender.py`):
ทุกคำนำหน้าไม่มีบรรทัดขัดกับเครื่องหมายเพศในบรรทัดเอง ยกเว้นฮารุกะ 4 บรรทัดที่เป็นบวกปลอมของ
regex (なにとぞ) ซึ่งแก้ใน merge_qc แล้ว

รหัสคิว -> เพศ มาจากทะเบียนที่อ้างไฟล์เกมแล้วเท่านั้น:
  1. `translations/characters.json` ช่อง `cue_id` (ประวัติในแผนผังใช้ he/she · EN pronoun · ป้ายสายสัมพันธ์)
  2. `translations/speakers.json` ช่อง `id` ที่เพศมาจากเครื่องหมายญี่ปุ่นผ่านเกณฑ์
  ถ้าสองทะเบียนขัดกัน = ไม่ใช้รหัสนั้น · รหัสที่ไม่มีในทะเบียน (`haha` · `okami` · `chonin1`) = ไม่เดาจากความหมายโรมาจิ

เขียนออก:
  translations/gender_voice_keys.json  คีย์บรรทัด -> {gender, why}          (make_polish_packets อ่าน)
  translations/gender_voice.json       สตริงอังกฤษ -> {gender, why}          (merge_qc อ่าน)
     ยุบเป็นสตริงอังกฤษได้เฉพาะเมื่อ **ทุกที่** ที่สตริงนั้นโผล่มีคิวเสียงเพศเดียวกัน
     หรือทุกที่มีต้นฉบับญี่ปุ่นเหมือนกันเป๊ะ (สำเนาฉาก — เกณฑ์เดียวกับ check_gender_lines.py)

ใช้: python scripts/build_voice_gender.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                   # noqa: E402
from merge_qc import ja_gender                 # noqa: E402
from make_gender_packets import DEAD_FILES     # noqa: E402

CUE_RE = re.compile(r"^([a-z][a-z0-9]{1,15})_[a-z0-9_]+$")
KEYS_OUT = paths.TRANSLATIONS / "gender_voice_keys.json"
EN_OUT = paths.TRANSLATIONS / "gender_voice.json"


def load_registry():
    """คืน (รหัสคิว -> (เพศ, คำอธิบาย), ชื่อบนจอ -> (เพศ, คำอธิบาย), รายการขัดกัน)"""
    by_id, by_name, conflicts = {}, {}, []
    chars = json.loads((paths.TRANSLATIONS / "characters.json").read_text(encoding="utf-8"))
    for group in chars.values():
        for name, c in group.items():
            g = c.get("gender")
            if g not in ("male", "female"):
                continue
            why = "%s = %s (characters.json %s: %s)" % (c.get("cue_id") or c.get("short"), name,
                                                        c.get("gender_from"), c.get("gender_why"))
            if c.get("cue_id"):
                by_id[c["cue_id"]] = (g, why)
            if c.get("short"):
                by_name[c["short"]] = (g, why)
    spk = json.loads((paths.TRANSLATIONS / "speakers.json").read_text(encoding="utf-8"))
    for name, s in spk.items():
        g, sid = s.get("gender"), s.get("id")
        if g not in ("male", "female"):
            continue
        why = "%s = %s (speakers.json %s: %s)" % (sid or name, name, s.get("gender_from"),
                                                  " · ".join(s.get("gender_why") or []))
        for table, k in ((by_id, sid), (by_name, name if not name.startswith("id:") else None)):
            if not k:
                continue
            if k in table and table[k][0] != g:
                conflicts.append((k, table[k], (g, why)))
            elif k not in table:
                table[k] = (g, why)
    for k, _a, _b in conflicts:
        by_id.pop(k, None)
        by_name.pop(k, None)
    return by_id, by_name, conflicts


def voice_gender(voice, by_id, by_name):
    m = CUE_RE.match(voice)
    if m:
        return by_id.get(m.group(1)) or (None, None)
    return by_name.get(voice) or (None, None)


def main():
    by_id, by_name, conflicts = load_registry()
    for k, a, b in conflicts:
        print("!! ทะเบียนขัดกัน ไม่ใช้ %s: %s | %s" % (k, a[1], b[1]))

    rows = [r for r in json.loads((paths.EXTRACTED / "parallel" / "msg.json").read_text(encoding="utf-8"))
            if r["file"] not in DEAD_FILES]
    keys, check = {}, Counter()
    contra = []
    unmapped = Counter()
    for r in rows:
        v = r.get("voice")
        if not v or not (r.get("en") or "").strip():
            continue
        g, why = voice_gender(v, by_id, by_name)
        if not g:
            unmapped[CUE_RE.match(v).group(1) if CUE_RE.match(v) else v] += 1
            continue
        keys[r["key"]] = {"gender": g, "why": "คิวเสียงของบรรทัด %s = %s · %s" % (r["key"], v, why)}
        jg = ja_gender(r.get("ja") or "")
        if jg:
            check["ตรง" if jg == g else "ขัด"] += 1
            if jg != g:
                contra.append((r["key"], v, r.get("ja"), r.get("en")))

    # ยุบเป็นสตริงอังกฤษ
    occ = defaultdict(list)
    for r in rows:
        if (r.get("en") or "").strip():
            occ[r["en"]].append(r)
    by_en = {}
    dropped = 0
    for en, rs in occ.items():
        gs = {(keys.get(r["key"]) or {}).get("gender") for r in rs}
        if gs == {None}:
            continue
        same_ja = len({r.get("ja") or "" for r in rs}) == 1
        if len(gs) == 1 or (same_ja and len(gs - {None}) == 1):
            g = next(iter(gs - {None}))
            src = next(r["key"] for r in rs if r["key"] in keys)
            by_en[en] = {"gender": g, "why": keys[src]["why"] + (" · สำเนาฉาก ja ตรงกันทุกที่" if len(gs) > 1 else "")}
        else:
            dropped += 1

    KEYS_OUT.write_text(json.dumps(keys, ensure_ascii=False, indent=1), encoding="utf-8")
    EN_OUT.write_text(json.dumps(by_en, ensure_ascii=False, indent=1), encoding="utf-8")
    g_count = Counter(v["gender"] for v in keys.values())
    print("บรรทัดที่มีคิวเสียงและรู้เพศ %d (ชาย %d · หญิง %d)" % (len(keys), g_count["male"], g_count["female"]))
    print("เทียบเครื่องหมายเพศในบรรทัดเอง: ตรง %d · ขัด %d" % (check["ตรง"], check["ขัด"]))
    for k, v, ja, en in contra[:30]:
        print("  ขัด %s voice=%s\n    JA: %s\n    EN: %s" % (k, v, (ja or "").replace("\r\n", " / "), en))
    print("สตริงอังกฤษ %d (ตัดทิ้งเพราะสตริงใช้ร่วมกับผู้พูดอื่น %d)" % (len(by_en), dropped))
    print("รหัสคิวที่ไม่มีในทะเบียน (ไม่เดา): %s" % ", ".join("%s:%d" % kv for kv in unmapped.most_common(25)))
    print("-> %s · %s" % (KEYS_OUT.name, EN_OUT.name))


if __name__ == "__main__":
    main()
