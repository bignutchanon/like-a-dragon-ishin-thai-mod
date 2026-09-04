"""ด่านตรวจ **ผลลัพธ์ที่แปลแล้ว** ของชั้น `.msg` — อ่านไฟล์ที่บิลด์จริงแล้วเทียบทีละบรรทัด

ทำไมต้องมีทั้งที่มี `check_msg_roundtrip.py` อยู่แล้ว:
`check_msg_roundtrip` ประกอบไฟล์กลับแบบ **ไม่แทนที่อะไรเลย** แล้วเทียบไบต์ — จับได้แค่บั๊ก
ที่เกิดตอนความยาวไม่เปลี่ยน ด่านนั้นจึงมองไม่เห็นบั๊กที่โผล่เฉพาะตอนสตริงยาวขึ้น

บั๊กจริงที่ด่านนี้ถูกเขียนขึ้นมาเพราะมัน (3 ก.ย. 2026 · เจอจากการทดสอบในเกม):
`MsgFile.rebuild()` เขียนตารางพอยเตอร์ label ที่ตำแหน่ง **เดิม** ทั้งที่ตารางนั้นอยู่หลัง
บล็อกสตริงซึ่งขยายตัวเมื่อไทยยาวกว่าอังกฤษ → พอยเตอร์ 4 ไบต์ไปทับกลางข้อความไทย
ผลคือข้อความขาดกลางประโยค **1,418 บรรทัดใน 1,017 ไฟล์** โดยด่านเดิมรายงานว่าผ่านหมด

เกณฑ์: ทุกบรรทัดในไฟล์ที่บิลด์ ต้องเท่ากับ `master_th[ต้นฉบับ]` เป๊ะ
(ถ้าไม่มีคำแปล ต้องเท่ากับต้นฉบับ) · ต่าง 1 บรรทัด = ตก

ใช้: python scripts/check_msg_translated.py [--max 20]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                    # noqa: E402
import msg as msgmod                            # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_text import label_replacements_for   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STAGE_MSG = paths.PROJECT / "build" / "text" / "msg"


def main() -> int:
    argv = sys.argv[1:]
    show = int(argv[argv.index("--max") + 1]) if "--max" in argv else 12
    master = json.loads(
        (paths.PROJECT / "translations" / "master_th.json").read_text(encoding="utf-8"))

    built = sorted(STAGE_MSG.glob("*.msg"))
    if not built:
        print("!! ไม่พบไฟล์ที่บิลด์ใน build/text/msg — รัน scripts/build_text.py ก่อน")
        return 1

    bad, checked, missing = [], 0, []
    for path in built:
        uid = path.stem
        src = paths.MSG_EN / (uid + ".msg")
        if not src.exists():
            missing.append(uid)
            continue
        van = msgmod.load(src)
        new = msgmod.load(path)
        if len(van.lines) != len(new.lines):
            bad.append((uid, -1, "จำนวนบรรทัดต่าง", len(van.lines), len(new.lines)))
            continue
        # label กับบล็อกคำสั่งต้องเหมือน vanilla เป๊ะ — ถ้าเพี้ยน ป้ายฉาก/ท่าทาง/คิวเสียงจะพัง
        # (บั๊กจริง 3 ก.ย. 2026: พอยเตอร์ label ถูกเขียนทับกลางสตริง ทำให้กล้องคัตซีนค้างในเกม)
        # label ชั้นแสดงผล (ชื่อผู้พูด/ตัวเลือก) ถูกแปลได้ตาม build_text.label_replacements_for
        lab_repl = label_replacements_for(van.labels, master)
        want_labels = [lab_repl.get(L, L) for L in van.labels]
        if want_labels != new.labels or van.label_count != new.label_count:
            bad.append((uid, -1, "ตาราง label ไม่ตรง vanilla",
                        "%d labels" % len(van.labels), "%d labels" % len(new.labels)))
            continue
        # บล็อกคำสั่งต้องเท่า vanilla **หลังปรับตำแหน่งตัวอักษร** ให้เข้ากับคำแปลแล้ว (msg.retime_cmds)
        # — บรรทัดที่ไม่ได้แปลต้องเท่า vanilla เป๊ะ · บรรทัดที่แปลต้องมีจุดจบ = จำนวนตัวอักษรไทย
        # (บั๊กจริง 3 ก.ย. 2026: ไม่ปรับแล้ว "ไม่ได้เจอกันนานเลยนะ ซากาโมโตะซัง" โชว์แค่ 28 ตัวเท่า EN)
        for i, (x, y) in enumerate(zip(van.lines, new.lines)):
            want = master.get(x.text or "", x.text) or ""
            want_cmds = msgmod.retime_cmds(x.cmds, x.text, want) if want != x.text else x.cmds
            if want_cmds != y.cmds:
                bad.append((uid, i, "บล็อกคำสั่งไม่ตรง (vanilla+retime)", "%d cmds" % len(x.cmds),
                            "%d cmds" % len(y.cmds)))
                break
        for i, (x, y) in enumerate(zip(van.lines, new.lines)):
            checked += 1
            want = master.get(x.text or "", x.text) or ""
            if (y.text or "") != want:
                bad.append((uid, i, x.text or "", want, y.text or ""))

    print("ไฟล์ที่บิลด์ %d · บรรทัดที่ตรวจ %d · **ต่าง %d**" % (len(built), checked, len(bad)))
    if missing:
        print("!! ไม่พบต้นฉบับของ %d ไฟล์ (ไฟล์ค้างจากบิลด์เก่า?): %s"
              % (len(missing), " ".join(missing[:5])))
    for uid, i, src_text, want, got in bad[:show]:
        print("  %s #%s" % (uid, i))
        print("     ต้นฉบับ : %r" % src_text[:70])
        print("     ควรเป็น : %r" % want[:70])
        print("     ในไฟล์  : %r" % got[:70])
    if len(bad) > show:
        print("  ... อีก %d บรรทัด" % (len(bad) - show))
    return 1 if (bad or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
