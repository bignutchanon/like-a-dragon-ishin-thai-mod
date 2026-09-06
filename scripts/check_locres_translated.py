"""ด่านตรวจ **ผลลัพธ์ที่แปลแล้ว** ของชั้น locres — แตก Game.locres ที่บิลด์กลับมาเทียบกับ vanilla ทีละคีย์

ทำไมต้องมี: `check_pak_roundtrip.py` เทียบไบต์ของ pak เท่านั้น ไม่รู้ว่าคีย์ไหนควรเป็นไทย/ควรคง EN
เคสจริง (6 ก.ย. 2026): namespace `enemy_name_template` ต้องคง EN เพราะ HUD วาดไทยเป็น "?"
ด่านนี้บังคับว่า namespace ใน KEEP_EN_NS / SKIP_NS ต้องเท่า vanilla ทุกคีย์ และคีย์อื่นต้องเป็น
`master_th[ต้นฉบับ]` ถ้ามีคำแปล ไม่มีก็ต้องเท่าต้นฉบับ

ใช้: python scripts/check_locres_translated.py [--max 12]
ต้องได้ ต่าง 0
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                    # noqa: E402
import locres                                   # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_worklist_ishin import KEEP_EN_NS, SKIP_NS   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BUILT = paths.PROJECT / "build" / "text" / "locres" / "Game.locres"
VANILLA = paths.EXTRACTED / "locres" / "Game.en.json"


def load_th_map():
    m = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    out = {}
    for en, v in m.items():
        th = v.get("th") if isinstance(v, dict) else v
        if isinstance(th, str) and th and th != en:
            out[en] = th
    return out


def entries(doc):
    s = doc["strings"]
    for n in doc["namespaces"]:
        for e in n["entries"]:
            yield n["ns"], e["key"], s[e["idx"]]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max", type=int, default=12, help="จำนวนตัวอย่างที่พิมพ์")
    a = ap.parse_args()
    if not BUILT.exists():
        print("ไม่มี %s — รัน build_text.py ก่อน" % BUILT)
        return 2
    with tempfile.TemporaryDirectory(prefix="ishin_locres_chk_") as td:
        out = Path(td) / "built.json"
        locres.dump_full(str(BUILT), str(out))
        built = json.loads(out.read_text(encoding="utf-8"))
    van = json.loads(VANILLA.read_text(encoding="utf-8"))
    th_map = load_th_map()

    van_map = {(ns, k): s for ns, k, s in entries(van)}
    built_map = {(ns, k): s for ns, k, s in entries(built)}
    bad = []
    n_keep = n_th = n_en = 0
    if set(van_map) != set(built_map):
        bad.append(("<keys>", "", "ชุดคีย์ไม่เท่ากัน: vanilla %d · built %d" % (len(van_map), len(built_map))))
    for (ns, k), en in van_map.items():
        got = built_map.get((ns, k))
        if got is None:
            continue
        if SKIP_NS.match(ns) or ns in KEEP_EN_NS:
            n_keep += 1
            if got != en:
                bad.append((ns, k, "ต้องคง EN แต่ได้ %r" % got[:40]))
            continue
        want = th_map.get(en, en)
        if got != want:
            bad.append((ns, k, "คาด %r ได้ %r" % (want[:40], got[:40])))
        elif want != en:
            n_th += 1
        else:
            n_en += 1
    print("locres: คีย์ %d · เป็นไทย %d · คง EN (ไม่มีคำแปล) %d · ล็อก EN %d · ต่าง %d"
          % (len(van_map), n_th, n_en, n_keep, len(bad)))
    for ns, k, why in bad[:a.max]:
        print("  ", ns, k, why)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
