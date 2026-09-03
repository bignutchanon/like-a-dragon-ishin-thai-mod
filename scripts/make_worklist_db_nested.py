"""ดึงข้อความ ARMP ที่ตกคิว — โดยเฉพาะ "ตารางซ้อนในแถว" ที่ตัวดึงเดิมเดินไม่ถึง

ที่มา (3 ก.ย. 2026 · เจอจากการทดสอบในเกม): จอ "ทิปส์และสมุดบันทึก" ขึ้นหัวข้อเป็นไทย
แต่ **เนื้อความเป็นอังกฤษ** เพราะข้อความจริงของ `tips` อยู่ในตาราง ARMP อีกชั้นที่ซ้อนอยู่ในแถว
(`row["table"]`) ซึ่ง `make_worklist_ishin.py` เดินแค่ชั้นบน จึงไม่เคยเข้าคิวแปล

สคริปต์นี้เดินทุกชั้น เก็บช่องชนิด 13 (สตริง) ที่ **ยังไม่มีใน `master_th.json`**
แล้วเขียนเป็น worklist ก้อนใหม่ให้ทีมแปล (ข้ามตารางที่กติกาสั่งคง EN และตารางที่ประกอบกลับไม่ได้)

ใช้: python scripts/make_worklist_db_nested.py [--batch 086] [--write]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                    # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

WORKLIST = paths.PROJECT / "translations" / "worklist"
# ⚠ ใช้ **บัญชีขาว** ไม่ใช่บัญชีดำ — คอลัมน์ชนิด 13 ในภาคนี้ปนของสองแบบอยู่ในชนิดเดียวกัน:
# ข้อความบนจอ กับ **ไอดี/พาธของแอสเซต** (`c_cm_ryoma` · `WEPCT2700` · `item/Accessory`
# · `Wanderer/ACT/` · `T_UI_Tips_glossary01`) การแปลไอดีพวกนี้ = เกมหาแอสเซตไม่เจอ
# (เกิดมาแล้วจริง: บิลด์ทดสอบเขียน `ทดสอบไทย wepct9000` ลง `battle_bomb_info` ทั้งตาราง)
ALLOW = {"tips", "photo_stamp", "option"}
HAS_LATIN = re.compile(r"[A-Za-z]{2}")
# ตัวกรองชั้นสอง: ต้องเป็น "ข้อความ" จริง ๆ — มีช่องว่างอย่างน้อยหนึ่งช่อง
# และไม่ใช่ตัวยึด `<%...%>` ของเอนจิน หรือพาธที่มี /
IDENTIFIER = re.compile(r"^<%|/")


def table_cells(tbl, path=""):
    """คืน (path, ค่า) ของช่องชนิด 13 ทุกชั้น รวมตารางที่ซ้อนในแถว"""
    cols = {c for c, t in (tbl.get("columnTypes") or {}).items() if t == 13}
    for k, v in tbl.items():
        if not k.isdigit() or not isinstance(v, dict):
            continue
        for gk, row in v.items():
            if not isinstance(row, dict):
                continue
            for c in cols:
                s = row.get(c)
                if isinstance(s, str) and s.strip():
                    yield ("%s/%s/%s/%s" % (path, k, gk, c), s)
            inner = row.get("table")
            if isinstance(inner, dict):
                yield from table_cells(inner, "%s/%s/%s/table" % (path, k, gk))


def main() -> int:
    argv = sys.argv[1:]
    batch = argv[argv.index("--batch") + 1] if "--batch" in argv else "086"
    write = "--write" in argv

    master = json.loads(
        (paths.PROJECT / "translations" / "master_th.json").read_text(encoding="utf-8"))
    deny = set()
    deny_path = paths.BUILD / "armp_deny.json"
    if deny_path.exists():
        deny = set(json.loads(deny_path.read_text(encoding="utf-8")).get("tables") or [])

    strings, sources, per_table = {}, [], {}
    for js in sorted((paths.EXTRACTED / "db_en").glob("*.bin.json")):
        table = js.name[: -len(".bin.json")]
        if table not in ALLOW or table in deny:
            continue
        doc = json.loads(js.read_text(encoding="utf-8"))
        found = 0
        for _path, val in table_cells(doc):
            if val in master or val in strings:
                continue
            if not HAS_LATIN.search(val) or len(val) < 4:
                continue
            if " " not in val or IDENTIFIER.search(val):   # ไอดี/พาธ/ตัวยึด — ห้ามแปล
                continue
            strings[val] = ""
            found += 1
        if found:
            per_table[table] = found
            sources.append("db:" + table)

    print("สตริงที่ยังไม่มีคำแปล %d รายการ จาก %d ตาราง" % (len(strings), len(per_table)))
    for t, n in sorted(per_table.items(), key=lambda kv: -kv[1]):
        print("   %-24s %d" % (t, n))

    if not write:
        print("\n(ยังไม่เขียนไฟล์ — ใส่ --write)")
        return 0

    doc = {
        "priority": 10,
        "priority_name": "ข้อความ ARMP ที่ตกคิว (ตารางซ้อนในแถว — tips ฯลฯ)",
        "sources": sources,
        "strings": strings,
    }
    out = WORKLIST / ("batch_%s.json" % batch)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\nเขียน %s (%d สตริง)" % (out.name, len(strings)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
