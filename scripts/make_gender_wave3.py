#!/usr/bin/env python3
"""คลื่นสามของตารางเพศรายบรรทัด — ไล่ไฟล์ฉากที่ `build_scene_gender.py` ตัดออกเพราะมีสองเพศ (15 ก.ย. 2026)

ไฟล์เหล่านี้เคยถูกตีทั้งฉากเป็นเพศเดียว พอตัดออกแล้ว บรรทัดที่ไม่มีหลักฐานรายบรรทัดจะกลายเป็น "ไม่รู้เพศ"
ซองนี้ให้ผู้ตรวจอ่านทั้งฉากเป็นบริบท แต่ตัดสินเฉพาะบรรทัดที่ติด `decide: true`
(= ยังไม่มีเพศจาก gender_lines · คิวเสียง · เครื่องหมายญี่ปุ่นในบรรทัด · ผลคลื่นก่อน)

บรรทัดที่รู้เพศแล้วติด `known` = เพศ+ชั้น ไว้ให้ผู้ตรวจใช้นับเทิร์น (ชั้น voice/ja/line เชื่อได้ · ชั้น key มาจากคลื่นก่อน)

ใช้: python scripts/make_gender_wave3.py [--lines 700]   -> work/gender_wave3/in/packet_NN.json
รวมผล: python scripts/merge_gender_wave.py --wave gender_wave gender_wave2 gender_wave3
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                    # noqa: E402
import merge_qc as M                            # noqa: E402
from make_gender_packets import load_files      # noqa: E402

WAVE = paths.PROJECT / "work" / "gender_wave3"


def load_keys(name):
    p = paths.TRANSLATIONS / name
    raw = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {k: v["gender"] for k, v in raw.items() if isinstance(v, dict) and v.get("gender") in ("male", "female")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=700)
    args = ap.parse_args()

    dropped = json.loads((paths.TRANSLATIONS / "scene_gender_dropped.json").read_text(encoding="utf-8"))
    voice, dkeys = load_keys("gender_voice_keys.json"), load_keys("gender_dialogue_keys.json")
    by = load_files()

    packets, cur, n = [], [], 0
    for f in sorted(dropped):
        if f not in by:
            continue
        cur.append(f)
        n += len(by[f])
        if n >= args.lines:
            packets.append(cur)
            cur, n = [], 0
    if cur:
        packets.append(cur)

    out = WAVE / "in"
    out.mkdir(parents=True, exist_ok=True)
    total_decide = 0
    for i, files in enumerate(packets, 1):
        scenes = []
        for f in files:
            lines = []
            for r in by[f]:
                item = {"key": r["key"], "en": r["en"], "ja": r.get("ja") or ""}
                if r.get("labels"):
                    item["labels"] = r["labels"]
                if r.get("voice"):
                    item["voice"] = r["voice"]
                for layer, g in (("line", M.line_gender(r["en"])), ("voice", voice.get(r["key"])),
                                 ("ja", M.ja_gender(r.get("ja") or "")), ("key", dkeys.get(r["key"]))):
                    if g:
                        item["known"] = "%s(%s)" % (g, layer)
                        break
                else:
                    item["decide"] = True
                    total_decide += 1
                lines.append(item)
            scenes.append({"file": f, "lines": lines})
        data = {"packet": "packet_%02d" % i, "scenes": scenes}
        p = out / ("packet_%02d.json" % i)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        nd = sum(1 for s in scenes for l in s["lines"] if l.get("decide"))
        print("%s  ฉาก %2d · บรรทัด %4d · ต้องตัดสิน %4d"
              % (p.name, len(files), sum(len(s["lines"]) for s in scenes), nd))
    print("รวม %d ซอง · ต้องตัดสิน %d บรรทัด -> %s" % (len(packets), total_decide, out))


if __name__ == "__main__":
    main()
