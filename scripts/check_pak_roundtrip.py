#!/usr/bin/env python3
"""ด่านตรวจ: pak ที่เราเขียนเอง ต้องอ่านกลับด้วย tools/pakfile.py ได้ครบทุกไบต์

เขียน pak ทดสอบจากข้อมูลสมมติ แล้วอ่านกลับมาเทียบ — จับบั๊กฝั่งตัวเขียนก่อนเอาไปใส่เกม
(ตัวเกมจะบอกแค่ว่า "ไม่โหลด" เฉย ๆ ดีบักยากกว่ามาก)

ใช้: python scripts/check_pak_roundtrip.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from pakfile import PakFile          # noqa: E402
from pakwrite import write_pak       # noqa: E402

BASE = "LikeaDragonIshin/Content/Projects/Devil2/data/"


def run():
    tmp = Path(__file__).resolve().parent.parent / "work" / "roundtrip_test.pak"
    samples = {
        BASE + "wdr_en/msg/uid00xxxxxx/uid00000001.msg": b"\x20\xf7\x08\x01" + os.urandom(500),
        BASE + "wdr_en/msg/uid01xxxxxx/uid01000002.msg": os.urandom(3000),
        BASE + "db.macan/en/tips.bin": b"armp" + os.urandom(12345),
        "LikeaDragonIshin/Content/Localization/Game/en/Game.locres": os.urandom(70000),
        "LikeaDragonIshin/Content/Projects/Devil2/UI/Font/FontFace/EFIGS/Kuro-Medium.ufont":
            os.urandom(54528),
        BASE + "empty.bin": b"",
    }
    write_pak(tmp, samples)

    pak = PakFile(tmp)
    ok = bad = missing = 0
    for gpath, data in samples.items():
        if gpath not in pak.files:
            missing += 1
            print("   หาย: %s" % gpath)
            continue
        got = pak.read(gpath)
        if got == data:
            ok += 1
        else:
            bad += 1
            print("   ต่าง: %s (%d -> %d ไบต์)" % (gpath, len(data), len(got)))
    extra = set(pak.files) - set(samples)
    print("pak ทดสอบ %d ไบต์ · ไฟล์ %d" % (tmp.stat().st_size, len(pak.files)))
    print("ตรงกัน %d · ต่าง %d · หาย %d · เกินมา %d" % (ok, bad, missing, len(extra)))
    for e in sorted(extra)[:5]:
        print("   เกิน: %s" % e)
    return 0 if (bad == 0 and missing == 0 and not extra) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(run())
