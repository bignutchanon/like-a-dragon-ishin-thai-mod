#!/usr/bin/env python3
"""แตกตารางตัวละคร `DataTable/Characters/info/*.uasset` (IoStore · Zen package) เป็นรายการแถว

ทำไมมีสคริปต์นี้: ภาคนี้ไม่มีตารางเพศใน ARMP (research §10) แต่ตาราง DataTable ของ UE ที่กำหนด
หน้าตาตัวละครในเกม **มีช่องบอกเพศสามช่องต่อแถว** (ยืนยันจากไฟล์จริง 13 ก.ย. 2026 · research §10.2)

| ช่อง | ตัวอย่าง |
|---|---|
| id แถว | `c_em_` = ชาย · `c_ew_` = หญิง · `c_ek_` = เด็ก |
| ชนิด | `一般男` · `一般女` · `子供男` |
| ประเภทเสียง | `男性_老人_京都弁` · `女性_若者_普_京都弁` |
| โมเดล หน้า/ตัว/ผม | `c_cm_*` ชาย · `c_cw_*` หญิง · `c_ck_*` เด็ก |

ตัวอย่างที่ใช้ยืนยันวิธี: แถว お咲/お菊/お鈴 (ชื่อรูปหญิง) ใช้โมเดลนักซูโม่ `c_cm_x_sumo`
ตรงกับ EN ที่เรียก "his" · คามาโมโตะ `c_em_SS15_kamatukai` = 一般男 · 男性_老人_京都弁 · c_cm

⚠ ยังไม่รู้ว่าไฟล์บทสนทนา (.msg / pac) ผูกกับแถวไหน — ตัวเลขใน section B ของเรคคอร์ด pac
(`0x47a` `0x484` `0x98e`) ไม่ใช่ id แถวในตารางพวกนี้ (ค้นแล้วไม่พบ) จึงใช้ได้เฉพาะตัวละครที่มีชื่อเป็นแถวของตัวเอง

การอ่าน: parse ส่วนหัว FPackageSummary (UE 4.27) → name map (ชื่อ UTF-16 จัดแนวคู่ไบต์) → ข้อมูล export
แล้วไล่ FName reference (u32 index + u32 number) ตามลำดับ แถวเริ่มที่ชื่อ `c_e[mwk]_*`
เป็น heuristic ที่พิสูจน์กับแถวข้างบนแล้ว ไม่ใช่ตัวถอด unversioned property เต็มรูป

ใช้:  python scripts/dump_chara_info.py            -> work/chara_info.json + สรุปจำนวน
"""
import json
import re
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths  # noqa: E402
from iostore import IoStoreSet  # noqa: E402

INFO_DIR = "LikeaDragonIshin/Content/Projects/Devil2/DataTable/Characters/info/"
OUT = paths.PROJECT / "work" / "chara_info.json"
ROW_RE = re.compile(r"c_e[mwk]_")
MODEL_RE = re.compile(r"c_c[mwk]_|c_a[wm]_")


def load_package(data):
    """คืน (name map, ไบต์ export ก้อนใหญ่สุด)"""
    f = struct.unpack_from("<IIIIIIiiiiiiiiii", data, 0)
    cooked, nmo, nms = f[5], f[6], f[7]
    exo, ebo, gdo, gds = f[11], f[12], f[13], f[14]
    names, o, end = [], nmo, nmo + nms
    while o < end:
        h0, h1 = data[o], data[o + 1]
        wide, ln = h0 & 0x80, ((h0 & 0x7F) << 8) | h1
        o += 2
        if wide:
            o += o % 2                       # ชื่อ UTF-16 จัดแนวคู่ไบต์
            names.append(data[o:o + ln * 2].decode("utf-16-le", "replace"))
            o += ln * 2
        else:
            names.append(data[o:o + ln].decode("latin1"))
            o += ln
    exports = [struct.unpack_from("<QQ", data, exo + 72 * i) for i in range((ebo - exo) // 72)]
    so, ss = max(exports, key=lambda e: e[1])
    start = gdo + gds + (so - cooked)
    return names, data[start:start + ss]


def rows_of(data):
    names, blob = load_package(data)
    n = len(names)
    seq, last = [], -99
    for o in range(len(blob) - 8):
        idx, num = struct.unpack_from("<Ii", blob, o)
        if idx < n and num == 0 and o - last >= 4:
            seq.append(names[idx])
            last = o
    rows, cur = [], None
    for t in seq:
        if ROW_RE.match(t):
            cur = {"id": t, "fields": []}
            rows.append(cur)
        elif cur is not None and len(cur["fields"]) < 10:
            cur["fields"].append(t)
    out = []
    for r in rows:
        f = r["fields"]
        jp = [x for x in f if re.search(r"[぀-鿿]", x)]
        out.append({
            "id": r["id"],
            "name": jp[0] if jp else "",
            "kind": next((x for x in jp if x in ("一般男", "一般女", "子供男", "子供女", "巨漢男")), ""),
            "voice": next((x for x in jp if x.startswith(("男性_", "女性_"))), ""),
            "models": [x for x in f if MODEL_RE.match(x)],
        })
    return out


def gender_of(row):
    """ตัดสินเพศเมื่อทุกช่องที่มีค่าไปทางเดียวกัน · ขัดกัน = None"""
    votes = set()
    votes.add({"c_em_": "male", "c_ew_": "female"}.get(row["id"][:5]))
    votes.add({"一般男": "male", "巨漢男": "male", "一般女": "female"}.get(row["kind"]))
    votes.add("male" if row["voice"].startswith("男性_") else "female" if row["voice"].startswith("女性_") else None)
    for m in row["models"]:
        votes.add("male" if m.startswith(("c_cm_", "c_am_")) else "female" if m.startswith(("c_cw_", "c_aw_")) else None)
    votes.discard(None)
    return votes.pop() if len(votes) == 1 else None


def main():
    s = IoStoreSet(paths.GAME / "LikeaDragonIshin" / "Content" / "Paks")
    tables = sorted(p for p in s.index if p.startswith(INFO_DIR) and p.endswith(".uasset"))
    result = {}
    for p in tables:
        name = p[len(INFO_DIR):-len(".uasset")]
        rows = rows_of(s.read(p))
        for r in rows:
            r["gender"] = gender_of(r)
        result[name] = rows
        g = [r["gender"] for r in rows]
        print("%-16s แถว %4d · ชาย %4d · หญิง %4d · ขัดกัน/ไม่รู้ %4d"
              % (name, len(rows), g.count("male"), g.count("female"), g.count(None)))
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("เขียน %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
