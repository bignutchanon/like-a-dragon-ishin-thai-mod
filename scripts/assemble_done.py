"""assemble_done.py — ประกอบไฟล์ done จากงานนักแปล + คีย์ DNT ที่ copy ตรง

นักแปลได้รับเฉพาะคีย์ที่ต้องแปลจริง (ตัด DNT ออกแล้ว) จึงต้องมีตัวประกอบกลับ
ให้ครบทุกคีย์ **ตามลำดับใน worklist** (ด่าน A1 ของ merge_qc ตรวจลำดับ)

ใช้: python scripts/assemble_done.py NNN <ไฟล์งานนักแปล.json>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import paths

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def main():
    n = sys.argv[1]
    if n.isdigit():
        n = n.zfill(3)   # รับได้ทั้ง 042 และ MSG_007
    part_path = Path(sys.argv[2])
    wl = json.loads((paths.WORKLIST / ("batch_%s.json" % n)).read_text(encoding="utf-8"))
    dnt_path = paths.WORKLIST / ("batch_%s.dnt.json" % n)
    dnt = json.loads(dnt_path.read_text(encoding="utf-8")) if dnt_path.exists() else {}
    part = json.loads(part_path.read_text(encoding="utf-8"))
    part = part.get("strings", part)

    out, missing, extra = {}, [], []
    for k in wl["strings"]:
        if k in dnt:
            out[k] = k
        elif k in part and isinstance(part[k], str) and part[k].strip():
            out[k] = part[k]
        else:
            out[k] = ""
            missing.append(k)
    for k in part:
        if k not in wl["strings"]:
            extra.append(k)

    dest = paths.DONE / ("batch_%s.done.json" % n)
    dest.write_text(json.dumps({"batch": "batch_%s.json" % n, "strings": out},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print("batch_%s: คีย์ทั้งหมด %d · DNT %d · จากนักแปล %d · ขาด %d · เกิน %d"
          % (n, len(out), len(dnt), len(out) - len(dnt) - len(missing), len(missing), len(extra)))
    for k in missing[:10]:
        print("   ขาด:", repr(k)[:70])
    for k in extra[:10]:
        print("   เกิน (ไม่มีใน worklist):", repr(k)[:70])
    if missing or extra:
        sys.exit(1)


if __name__ == "__main__":
    main()
