#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สลับ "ม็อดข้อความ" เข้า/ออกอย่างเดียว โดยไม่แตะฟอนต์ — ใช้ทำ A/B หาสาเหตุบั๊กพฤติกรรม

ทำไมไม่ใช้ `deploy_title_poc.restore()`: ตัวนั้นคืน **ทั้งฟอนต์และข้อความ** พร้อมกัน
ผลที่ได้จึงบอกไม่ได้ว่าอาการหายเพราะข้อความหรือเพราะฟอนต์ สคริปต์นี้ย้ายเฉพาะโฟลเดอร์
`mods/db.coyote.en` ออกไปพักไว้ข้าง ๆ แล้ว regen MLO ใหม่ ฟอนต์ในเกมยังเป็นไทยเหมือนเดิม

ใช้ตอนเจออาการที่ **ไม่ใช่เรื่องตัวอักษร** (ตกแมพ · เมนูค้าง · เควสไม่เดิน) แล้วต้องพิสูจน์ว่า
ม็อดข้อความเกี่ยวหรือไม่ — ดู docs/ISSUES.md LJ-011

    python scripts/ab_text_mod.py --off     # ถอดม็อดข้อความ (ข้อความกลับเป็นอังกฤษ ฟอนต์ยังไทย)
    python scripts/ab_text_mod.py --on      # ใส่กลับ
    python scripts/ab_text_mod.py           # ดูสถานะเฉย ๆ

⚠ ห้ามรันพร้อมกับ deploy ตัวอื่น (กติกาเหล็กข้อ 11)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                                    # noqa: E402

LIVE = paths.MODS_DIR / "db.coyote.en"
# ⚠ ที่พักต้องอยู่ **นอกโฟลเดอร์ mods** — SRMM กวาดทุกโฟลเดอร์ใต้ mods/<ชื่อม็อด>/ แล้วใส่ลง MLO
# ถ้าพักไว้ข้าง ๆ ในนั้น MLO จะมี entry `/db.coyote.en.ab_off/*.bin` 228 บรรทัดติดมาด้วย
# (ไม่ redirect จริงเพราะไม่มี par ชื่อนั้น แต่ทำให้ A/B ไม่สะอาดและอ่านผลยาก)
PARKED = paths.BUILD / "ab_parked" / "db.coyote.en"
MEDIA = paths.GAME / "runtime" / "media"


def regen_mlo():
    srmm = MEDIA / "ShinRyuModManager.exe"
    if not srmm.exists():
        sys.exit("!! ไม่พบ ShinRyuModManager.exe — ยังไม่ได้ติดตั้ง SRMM")
    r = subprocess.run([str(srmm), "-s"], cwd=str(MEDIA), capture_output=True,
                       text=True, timeout=1800)
    mlo = MEDIA / "YakuzaParless.mlo"
    print("regen MLO: rc=%d, %s B" % (r.returncode, "{:,}".format(
        mlo.stat().st_size if mlo.exists() else 0)))
    if r.returncode != 0 or not mlo.exists():
        sys.exit("!! MLO ไม่สำเร็จ — ห้ามเปิดเกมจนกว่าจะแก้")


def status():
    n_live = len(list(LIVE.rglob("*"))) if LIVE.exists() else 0
    n_park = len(list(PARKED.rglob("*"))) if PARKED.exists() else 0
    print("ม็อดข้อความ: %s (%d ไฟล์)" % ("เปิดอยู่" if LIVE.exists() else "ถอดออกแล้ว", n_live))
    if PARKED.exists():
        print("พักไว้ที่: %s (%d ไฟล์)" % (PARKED, n_park))
    par = paths.FONT_PAR
    orig = par.with_suffix(par.suffix + ".orig")
    print("ฟอนต์: %s" % ("ไทย (มี .orig สำรองไว้)" if orig.exists() else "ต้นฉบับ"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--off", action="store_true", help="ถอดม็อดข้อความออก (ฟอนต์คงไว้)")
    g.add_argument("--on", action="store_true", help="ใส่ม็อดข้อความกลับ")
    a = ap.parse_args()

    if a.off:
        if not LIVE.exists():
            print("ถอดออกอยู่แล้ว ไม่ต้องทำอะไร")
            return status()
        if PARKED.exists():
            shutil.rmtree(PARKED)
        PARKED.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(LIVE), str(PARKED))
        print("ย้าย %s -> %s" % (LIVE.name, PARKED.name))
        regen_mlo()
    elif a.on:
        if LIVE.exists():
            print("เปิดอยู่แล้ว ไม่ต้องทำอะไร")
            return status()
        if not PARKED.exists():
            sys.exit("!! ไม่มีของที่พักไว้ — ให้ deploy ใหม่ด้วย deploy_title_poc.srmm_and_mods()")
        shutil.move(str(PARKED), str(LIVE))
        print("ย้ายกลับ %s -> %s" % (PARKED.name, LIVE.name))
        regen_mlo()
    status()


if __name__ == "__main__":
    sys.exit(main())
