#!/usr/bin/env python3
"""แตกบทพูดทั้งหมดจาก .msg พร้อมเดาผู้พูดรายบรรทัด

ที่มาของผู้พูด — ไม่ได้เดาจากเนื้อความ แต่มาจากข้อมูลในไฟล์เกม:
  แต่ละบรรทัดมีคำสั่ง opcode 0x03 (คิวเสียง) ที่ชี้ดัชนีเข้าตาราง label ของไฟล์
  label คิวเสียงตั้งชื่อแบบ `<ผู้พูด>_<ฉาก>_<เลข>` เช่น `otose_adv_c02_150_001`
  → ตัดคำหน้าสุดได้ id ผู้พูด (`otose`) ซึ่งตรงกับชื่อตัวละครใน label เดียวกัน (`Otose`)
  วิธีเดียวกับที่โปรเจกต์ Lost Judgment ใช้กับ `sound_auth.bin` (ดู docs/reference/CUE_GENDER_METHOD.md)

ระดับความเชื่อมั่นที่ติดมากับทุกบรรทัด:
  cue      = บรรทัดนั้นมีคิวเสียงของตัวเอง — เชื่อถือได้สูงสุด
  file     = ทั้งไฟล์มี id ผู้พูดเดียว จึงยกมาใช้กับบรรทัดที่ไม่มีคิว
  unknown  = พิสูจน์ไม่ได้ → **ต้องแปลกลางเพศ ห้ามเดา** (กติกาเดียวกับทุกภาค)

ใช้:
  python scripts/extract_lines.py            # เขียน extracted/lines_en.json + docs/speakers.md
  python scripts/extract_lines.py --summary  # ดูสรุปอย่างเดียว ไม่เขียนไฟล์
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                        # noqa: E402
from msg import MsgFile                             # noqa: E402

# label ที่เป็นคิวเสียง: ตัวพิมพ์เล็ก/ตัวเลข คั่นด้วย _ อย่างน้อยสองท่อน
CUE_RE = re.compile(r"^([a-z][a-z0-9]{1,15})_[a-z0-9_]+$")
# id ที่ไม่ใช่ชื่อคน (เสียงประกอบ/ระบบ) — ตัดออกจากการเดาผู้พูด
NOT_SPEAKER = {
    "kaiwabgm", "bgm", "se", "voice", "sys", "system", "minig", "mini",
    "2d", "3d", "arasuji", "telop", "sub", "common", "cmn", "test", "dummy",
}


def speaker_of(label):
    m = CUE_RE.match(label)
    if not m:
        return None
    sid = m.group(1)
    return None if sid in NOT_SPEAKER else sid


def run(write=True):
    src = paths.EXTRACTED / "msg_en"
    files = sorted(src.glob("*.msg"))
    if not files:
        print("ยังไม่มี %s — รัน scripts/extract_msg.py ก่อน" % src)
        return 2

    records = []
    conf = Counter()
    per_speaker = Counter()
    speaker_files = defaultdict(set)
    n_lines = n_empty = 0

    for f in files:
        try:
            m = MsgFile(f.read_bytes(), f.name)
        except Exception as e:                       # ห้ามเงียบ
            print("!! อ่านไม่ได้ %s: %s" % (f.name, e), file=sys.stderr)
            continue

        # id ผู้พูดทั้งหมดที่โผล่ในตาราง label ของไฟล์นี้
        file_ids = {s for s in (speaker_of(x) for x in m.labels) if s}
        file_default = next(iter(file_ids)) if len(file_ids) == 1 else None

        for rec in m.to_records():
            n_lines += 1
            if not rec["en"]:
                n_empty += 1
            ids = [s for s in (speaker_of(x) for x in rec["labels"]) if s]
            if ids:
                sid, how = ids[0], "cue"
            elif file_default:
                sid, how = file_default, "file"
            else:
                sid, how = None, "unknown"
            conf[how] += 1
            if sid:
                per_speaker[sid] += 1
                speaker_files[sid].add(f.stem)
            rec["speaker"] = sid
            rec["speaker_from"] = how
            records.append(rec)

    known = conf["cue"] + conf["file"]
    print("ไฟล์ %d · บรรทัด %d (ว่าง %d)" % (len(files), n_lines, n_empty))
    print("ระบุผู้พูดได้ %d (%.0f%%) — จากคิวเสียง %d · จากไฟล์ %d · ไม่รู้ %d (%.0f%%)"
          % (known, 100 * known / max(n_lines, 1), conf["cue"], conf["file"],
             conf["unknown"], 100 * conf["unknown"] / max(n_lines, 1)))
    print("ผู้พูดไม่ซ้ำ %d คน" % len(per_speaker))
    print("\n25 อันดับแรก (id · บรรทัด · จำนวนไฟล์ที่โผล่):")
    for sid, c in per_speaker.most_common(25):
        print("   %-16s %6d   %4d ไฟล์" % (sid, c, len(speaker_files[sid])))

    if write:
        out = paths.EXTRACTED / "lines_en.json"
        out.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nเขียนแล้ว: %s (%d บรรทัด)" % (out, len(records)))

        md = ["# ตารางผู้พูดจากคิวเสียง — Like a Dragon: Ishin!", "",
              "สร้างโดย `scripts/extract_lines.py` จากคำสั่งคิวเสียง (opcode 0x03) ในไฟล์ `.msg`",
              "", "| id ผู้พูด | บรรทัด | ไฟล์ที่โผล่ |", "|---|---:|---:|"]
        for sid, c in per_speaker.most_common():
            md.append("| `%s` | %d | %d |" % (sid, c, len(speaker_files[sid])))
        md += ["", "## ความครอบคลุม", "",
               "- บรรทัดทั้งหมด: %d" % n_lines,
               "- ระบุผู้พูดได้: %d (%.0f%%)" % (known, 100 * known / max(n_lines, 1)),
               "- จากคิวเสียงของบรรทัดเอง: %d" % conf["cue"],
               "- ยกมาจากไฟล์ที่มีผู้พูดคนเดียว: %d" % conf["file"],
               "- พิสูจน์ไม่ได้: %d — **ต้องแปลกลางเพศ ห้ามเดา**" % conf["unknown"]]
        p = paths.DOCS / "speakers.md"
        p.write_text("\n".join(md) + "\n", encoding="utf-8")
        print("เขียนแล้ว: %s" % p)
    return 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true", help="ไม่เขียนไฟล์")
    a = ap.parse_args()
    raise SystemExit(run(write=not a.summary))


if __name__ == "__main__":
    main()
