"""ด่านตรวจ **ผลลัพธ์ที่แปลแล้ว** ของชั้น ARMP — แตกไฟล์ที่บิลด์กลับมาเทียบกับ vanilla ทีละช่อง

ทำไมต้องมี: `check_layout_all.py` เทียบ "ไบต์ในแถว" กับ vanilla ซึ่งจับได้แค่ layout เพี้ยน
แต่จับไม่ได้ว่า **ค่าในช่องที่ไม่ใช่ข้อความ** ถูกเขียนกลับผิด (เช่น คอลัมน์ธง 30/31 กลายเป็นศูนย์)
ซึ่งเป็นอาการที่ทำให้เมนู/เงื่อนไขในเกมพัง ทั้งที่ข้อความขึ้นไทยครบ

เกณฑ์:
  - ช่องชนิดข้อความ (13) ต้องเท่ากับ `master_th[ต้นฉบับ]` (ถ้าไม่มีคำแปลต้องเท่าต้นฉบับ)
  - ช่องชนิดอื่น **ทุกช่อง** ต้องเท่ากับ vanilla เป๊ะ
  - เดินเข้าตารางที่ซ้อนอยู่ในแถว (`row["table"]`) ด้วย

ใช้: python scripts/check_armp_translated.py [--max 12]
"""
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                    # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REARMP = paths.TOOLS / "reARMP_fixed.py"
STAGE_DB = paths.PROJECT / "build" / "text" / "db.macan.en"


def to_json(bin_path):
    """แตก .bin เป็น dict ด้วย reARMP (ทำงานในโฟลเดอร์ชั่วคราวเพราะ reARMP เขียนลง cwd)"""
    with tempfile.TemporaryDirectory(prefix="ishin_armp_chk_") as td:
        td = Path(td)
        src = td / bin_path.name
        src.write_bytes(bin_path.read_bytes())
        subprocess.run([sys.executable, str(REARMP), src.name],
                       cwd=str(td), input=b"\n", capture_output=True, check=False)
        out = td / (src.name + ".json")
        if not out.exists():
            return None
        return json.loads(out.read_text(encoding="utf-8"))


def unstored_cols(bin_path, doc):
    """ชื่อคอลัมน์ที่ **ไม่ได้เก็บไว้ในแถว** (shift = -1)

    คอลัมน์พวกนี้ reARMP ไม่ได้อ่านจากไบต์ในแถว จึงเทียบค่าที่มันคืนมาไม่ได้ —
    เคสจริง: `sound_speak_data` คอลัมน์ `*` (ชนิด 1 · shift -1) อ่านกลับได้ 3840 แทน 512
    ทั้งที่ไบต์ในแถวเท่ากับ vanilla ทุกไบต์ (4,044/4,045 แถว · aux/types ตรงกัน · layout ตรง)
    = เป็นค่าที่ตัวอ่านสังเคราะห์ ไม่ใช่ข้อมูลที่เราเขียนพัง
    """
    try:
        b = Path(bin_path).read_bytes()
        main = struct.unpack_from("<i", b, 0x10)[0]
        cols = struct.unpack_from("<i", b, main + 4)[0]
        p_aux = struct.unpack_from("<i", b, main + 0x48)[0]
        names = list((doc.get("columnTypes") or {}).keys())
        out = set()
        for ci in range(min(cols, len(names))):
            shift = struct.unpack_from("<i", b, p_aux + 16 * ci + 4)[0]
            if shift < 0:
                out.add(names[ci])
        return out
    except Exception:
        return set()


def cells(tbl, path=""):
    """คืน (path, ชนิดคอลัมน์, ค่า) ของทุกช่อง รวมตารางซ้อน"""
    types = tbl.get("columnTypes") or {}
    for k, v in tbl.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        for gk, row in v.items():
            if not isinstance(row, dict):
                continue
            for col, val in row.items():
                if col == "table" and isinstance(val, dict):
                    yield from cells(val, "%s/%s/%s/table" % (path, k, gk))
                    continue
                yield ("%s/%s/%s/%s" % (path, k, gk, col), types.get(col), val)


def main() -> int:
    argv = sys.argv[1:]
    show = int(argv[argv.index("--max") + 1]) if "--max" in argv else 12
    master = json.loads(
        (paths.PROJECT / "translations" / "master_th.json").read_text(encoding="utf-8"))

    built = sorted(STAGE_DB.glob("*.bin"))
    if not built:
        print("!! ไม่พบไฟล์ที่บิลด์ใน build/text/db.macan.en — รัน scripts/build_text.py ก่อน")
        return 1

    bad, checked = [], 0
    for path in built:
        table = path.stem
        van_bin = paths.EXTRACTED / "db_en" / (table + ".bin")
        van = json.loads((paths.EXTRACTED / "db_en" / (table + ".bin.json")).read_text(
            encoding="utf-8")) if (paths.EXTRACTED / "db_en" / (table + ".bin.json")).exists() else None
        if van is None or not van_bin.exists():
            bad.append((table, "-", "ไม่มีต้นฉบับให้เทียบ", "", ""))
            continue
        new = to_json(path)
        if new is None:
            bad.append((table, "-", "แตกไฟล์ที่บิลด์ไม่ได้", "", ""))
            continue
        skip = unstored_cols(van_bin, van)
        v_cells = list(cells(van))
        n_cells = list(cells(new))
        if len(v_cells) != len(n_cells):
            bad.append((table, "-", "จำนวนช่องต่าง", len(v_cells), len(n_cells)))
            continue
        for (vp, vt, vv), (_np, _nt, nv) in zip(v_cells, n_cells):
            if vp.rsplit("/", 1)[-1] in skip:      # คอลัมน์ที่ไม่ได้เก็บในแถว — เทียบไม่ได้
                continue
            checked += 1
            if vt == 13 and isinstance(vv, str):
                want = master.get(vv, vv)
                if nv != want:
                    bad.append((table, vp, "ข้อความไม่ตรงคำแปล", want, nv))
            elif vv != nv:
                bad.append((table, vp, "ค่าที่ไม่ใช่ข้อความเปลี่ยนไป", vv, nv))

    print("ตารางที่บิลด์ %d · ช่องที่ตรวจ %d · **ต่าง %d**" % (len(built), checked, len(bad)))
    for table, cpath, why, want, got in bad[:show]:
        print("  %s %s — %s" % (table, cpath, why))
        print("     vanilla/ควรเป็น : %r" % (str(want)[:70],))
        print("     ในไฟล์ที่บิลด์  : %r" % (str(got)[:70],))
    if len(bad) > show:
        print("  ... อีก %d ช่อง" % (len(bad) - show))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
