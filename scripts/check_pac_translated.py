"""ด่านตรวจ **ผลลัพธ์ที่แปลแล้ว** ของชั้น pac_STID — อ่านไฟล์ที่บิลด์จริงแล้วเทียบกับ vanilla ทีละส่วน

`check_pac_roundtrip.py` พิสูจน์ตัวประกอบ (ไม่แทนอะไร = ไบต์เท่าเดิม · สลับเป็นภาษาอื่น = ไบต์เท่าไฟล์ภาษานั้น)
ด่านนี้ตรวจไฟล์ที่ **บิลด์ออกมาจริง** ใน build/text/pac ว่า:
  1. อ่านได้ทุกเรคคอร์ด · ลำดับ record id เท่า vanilla
  2. ส่วน B (ตำแหน่ง/ค่าตัวละคร) เท่า vanilla ทุกไบต์ · เรคคอร์ดที่ไม่ใช่ข้อความ ส่วน A เท่า vanilla ทุกไบต์
  3. ทุกบรรทัด/label = คำแปลตาม `build_text.pac_replacements` (ไม่มีคำแปล = เท่าต้นฉบับ)
  4. บล็อกคำสั่ง = vanilla ถ้าไม่ได้แปล · = `msg.retime_cmds(vanilla, EN, ไทย)` ถ้าแปล
  5. ไฟล์ที่ควรถูกบิลด์ (มีคำแปลอย่างน้อยหนึ่งสตริง) ต้องอยู่ใน stage ครบ

ใช้: python scripts/check_pac_translated.py [--max 20]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                          # noqa: E402
import pac                                            # noqa: E402
from msg import retime_cmds                           # noqa: E402
from pakfile import PakFile                           # noqa: E402
from build_text import STAGE_PAC, load_master, pac_replacements, pac_rows_by_file  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def main():
    argv = sys.argv[1:]
    show = int(argv[argv.index("--max") + 1]) if "--max" in argv else 12
    th_map = load_master()
    by_file = pac_rows_by_file()
    if not by_file:
        print("!! ไม่พบ extracted/pac_en.json — รัน scripts/extract_pac_text.py ก่อน")
        return 1
    expected = {stem for stem, rows in by_file.items() if pac_replacements(rows, th_map)}
    built = {p.stem: p for p in STAGE_PAC.glob("*.bin")} if STAGE_PAC.exists() else {}

    pak = PakFile(paths.PAK_MAIN)
    bad, n_strings, n_translated = [], 0, 0
    for stem in sorted(expected | set(built)):
        if stem not in built:
            bad.append((stem, "-", "ควรถูกบิลด์แต่ไม่มีใน stage", "", ""))
            continue
        if stem not in expected:
            bad.append((stem, "-", "มีใน stage แต่ไม่มีคำแปล (ไฟล์ค้างจากบิลด์เก่า?)", "", ""))
            continue
        name = stem + ".bin"
        van = pac.PacFile(pak.read((paths.PAC_DIR % "en") + name), name)
        new = pac.PacFile(built[stem].read_bytes(), name)
        if new.errors:
            bad.append((stem, "-", "อ่านเรคคอร์ดไม่ได้", str(new.errors[:2]), ""))
            continue
        if [r.rid for r in van.records] != [r.rid for r in new.records]:
            bad.append((stem, "-", "ลำดับ record id ไม่ตรง vanilla", "", ""))
            continue
        repl = pac_replacements(by_file[stem], th_map)
        for rv, rn in zip(van.records, new.records):
            rid = "%08x" % rv.rid
            if rv.b != rn.b:
                bad.append((stem, rid, "ส่วน B ไม่ตรง vanilla", "", ""))
            if not rv.msg:
                if rv.a != rn.a:
                    bad.append((stem, rid, "ส่วน A (ไม่ใช่ข้อความ) ไม่ตรง vanilla", "", ""))
                continue
            mv, mn = rv.msg, rn.msg
            if len(mv.lines) != len(mn.lines) or len(mv.labels) != len(mn.labels):
                bad.append((stem, rid, "จำนวนบรรทัด/label ไม่ตรง", "", ""))
                continue
            for kind, sv, sn in (("line", mv.lines, mn.lines), ("label", mv.labels, mn.labels)):
                for i, (x, y) in enumerate(zip(sv, sn)):
                    key = van.key(rv.rid, kind, i)
                    src = pac._dec(x)
                    want = repl.get(key, src)
                    got = pac._dec(y)
                    n_strings += 1
                    if key in repl:
                        n_translated += 1
                    if got != want:
                        bad.append((stem, key, src, want, got))
                    if kind == "line":
                        want_cmds = retime_cmds(mv.cmds[i], src, want) if key in repl else mv.cmds[i]
                        if list(want_cmds) != list(mn.cmds[i]):
                            bad.append((stem, key, "บล็อกคำสั่งไม่ตรง (vanilla+retime)", "", ""))

    print("ไฟล์ที่ควรบิลด์ %d · ในstage %d · สตริงที่ตรวจ %d · แปลแล้ว %d · **ต่าง %d**"
          % (len(expected), len(built), n_strings, n_translated, len(bad)))
    for stem, key, a, b, c in bad[:show]:
        print("  %s %s" % (stem, key))
        print("     ต้นฉบับ/เหตุ : %r" % a[:70])
        if b or c:
            print("     ควรเป็น     : %r" % b[:70])
            print("     ในไฟล์      : %r" % c[:70])
    if len(bad) > show:
        print("  ... อีก %d รายการ" % (len(bad) - show))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
