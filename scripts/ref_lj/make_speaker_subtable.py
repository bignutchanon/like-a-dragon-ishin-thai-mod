#!/usr/bin/env python3
"""ดึง "ผู้พูด" จากชื่อ subTable ใน `sound_auth.bin.json` — หลักฐานที่แข็งที่สุดที่โปรเจกต์มี

ที่มา: ผู้ตรวจ batch_072 พบว่าตารางบทพูดฉากต่อสู้ตั้งชื่อด้วยชื่อตัวละคร (`speech_btl12_030_yagami`)
แล้วผู้ตรวจ batch_077 พบต่อว่า **บทเนื้อเรื่องหลักก็ตั้งชื่อแบบเดียวกัน** (`speech_m13_00500_morita`)
รวมแล้วมี subTable แบบนี้ 1,295 ตาราง ครอบคลุมบทพูดหลักเกือบทั้งเกม

ไฟล์นี้แปลงข้อมูลนั้นเป็น `extracted/facts/speaker_by_subtable.json` = {"<ตารางแม่>#<id>": "ผู้พูด"}
ให้นักแปล/ผู้ตรวจ **เปิดด้วย speaker-slot id ตรง ๆ แล้วได้ชื่อผู้พูดทันที** ไม่ต้องไล่ anchor เอง
ตรวจสอบแล้ว 10/10 กับ id ที่ทีมยืนยันด้วยมือมาตลอดสปรินต์ (บทที่ 7/11/12/13) — ตรงทั้งหมด

รูปแบบชื่อ subTable: `speech_<scene>_<number>_<speaker>` เช่น
  speech_m01_00100_kaito · speech_btl12_030_sugiura · speech_m13_00500_morita
ตัวที่ลงท้ายด้วยชื่อไม่ใช่ตัวละคร (เช่น `_homeless`, `_enemy003`) ก็เก็บไว้เหมือนกัน —
บอกได้ว่าเป็น NPC ประเภทไหน

ใช้:  python scripts/make_speaker_subtable.py [--write]
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

SRC = paths.DB_EN / "sound_auth.bin.json"
OUT = paths.EXTRACTED / "facts" / "speaker_by_subtable.json"
DOC = paths.DOCS / "reference" / "speaker_by_subtable.md"
# `speech_m13_00500_morita` -> ("m13", "morita") · `speech_btl12_030_sugiura` -> ("btl12", "sugiura")
NAME_RE = re.compile(r"^speech_([a-z0-9]+)_\d+_(.+)$")


def collect(data):
    """หา subTable ที่ชื่อบอกผู้พูด แล้วอ่าน field "0" ของมัน = **speaker-slot id** ของผู้พูดคนนั้น

    โครงจริงในไฟล์: `speech_m13_00100_higashi` -> {"0": 1471, "1": {ตารางบรรทัดเสียง}}
    field "0" คือเลขเดียวกับ field "1" ของแถวบทพูดในตารางแม่ → ได้ map (ตารางแม่, id) -> ผู้พูด
    """
    out = collections.OrderedDict()
    scenes = collections.Counter()
    conflicts = []

    def walk(obj, parent):
        if not isinstance(obj, dict):
            return
        for k, v in obj.items():
            m = NAME_RE.match(k) if isinstance(k, str) else None
            if m and isinstance(v, dict) and isinstance(v.get("0"), int):
                scene, speaker = m.groups()
                scenes[scene] += 1
                key = "%s#%d" % (parent, v["0"])
                if key in out and out[key] != speaker:
                    conflicts.append((key, out[key], speaker))
                out.setdefault(key, speaker)
            walk(v, k if isinstance(k, str) and k.startswith("speech_list") else parent)

    walk(data, "?")
    return out, scenes, conflicts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="เขียนไฟล์จริง")
    a = ap.parse_args()

    data = json.load(io.open(SRC, encoding="utf-8"))
    mapping, scenes, conflicts = collect(data)
    print("จับคู่ (ตาราง, speaker-slot id) -> ผู้พูด ได้ %s รายการ · ชนกันเอง %d"
          % (format(len(mapping), ","), len(conflicts)))
    print("ฉากที่ครอบคลุม %d: %s ..." % (len(scenes), " ".join(sorted(scenes)[:12])))

    if not a.write:
        for t, s in list(mapping.items())[:8]:
            print("   %-58s %s" % (t.replace("\n", " / ")[:58], "/".join(s)))
        print("(ใส่ --write เพื่อเขียนไฟล์)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(mapping, ensure_ascii=False, indent=1) + "\n")

    lines = [
        "# ผู้พูดจากชื่อ subTable — หลักฐานชั้นที่ 1 ของโปรเจกต์",
        "",
        "สร้างด้วย `python scripts/make_speaker_subtable.py --write` →",
        "`extracted/facts/speaker_by_subtable.json` (`{ข้อความ EN: [ผู้พูด]}`)",
        "",
        "**รูปแบบคีย์**: `<ชื่อตารางแม่>#<speaker-slot id>` → ชื่อผู้พูด",
        "เช่น `speech_list_coyote_main_c13#1471` → `higashi`",
        "",
        "**วิธีใช้**: อ่าน field `\"1\"` ของแถวบทพูดใน `sound_auth.bin.json` (= speaker-slot id)",
        "แล้วเปิดไฟล์นี้ด้วยคีย์ `<ตารางแม่>#<id>` → ได้ชื่อผู้พูดทันที **ไม่ต้องไล่ anchor เอง**",
        "",
        "**ที่มาของข้อมูล**: เกมตั้งชื่อ subTable บทพูดเป็น `speech_<ฉาก>_<เลข>_<ผู้พูด>`",
        "เช่น `speech_m13_00500_morita` · `speech_btl12_030_sugiura` — ผู้ตรวจ batch_072 เจอในฉากต่อสู้ก่อน",
        "แล้วผู้ตรวจ batch_077 พบว่าบทเนื้อเรื่องหลักก็ใช้รูปแบบเดียวกัน",
        "",
        "**ข้อควรระวัง**: ไม่ใช่ทุก id ที่มีในไฟล์นี้ (บางฉากไม่มี subTable ตั้งชื่อ) — ถ้าไม่เจอคีย์",
        "ให้ถอยไปใช้ `speaker_exact` แล้วค่อยไปเทคนิค anchor ตามลำดับเดิม",
        "",
        "| ตัวเลข | ค่า |",
        "|---|---|",
        "| คู่ (ตาราง, id) ที่ผูกผู้พูดได้ | %s |" % format(len(mapping), ","),
        "| ผู้พูดไม่ซ้ำ | %s |" % format(len(set(mapping.values())), ","),
        "| ฉากที่ครอบคลุม | %d |" % len(scenes),
        "",
    ]
    io.open(DOC, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("เขียน %s" % OUT)
    print("เขียน %s" % DOC)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
