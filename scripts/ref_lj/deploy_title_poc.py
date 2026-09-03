#!/usr/bin/env python3
"""deploy PoC ไตเติลภาษาไทยลงเกม Lost Judgment

ทำสามอย่าง (อยู่ในขอบเขตที่กติกาเหล็กอนุญาต):
1. ฟอนต์ — LJ เก็บฟอนต์ไว้ใน `data/font.coyote.par` (ไม่ใช่โฟลเดอร์ loose แบบ Judgment)
   จึงต้อง repack: สำรอง par เดิมเป็น `.orig` ครั้งแรกเสมอ แล้วสร้าง par ใหม่ด้วย
   `ParTool.exe add <par เดิม> build/font_stage <par ใหม่>` ก่อนเขียนทับไฟล์เกม
   (ฟอนต์ loose ผ่าน Parless โหลดไม่ทัน — กติกาเหล็กข้อ 5)
2. SRMM — วาง `ShinRyuModManager.exe` + `version.dll` + `YakuzaParless.asi` ใน `runtime/media`
   (เพิ่มไฟล์ใหม่ ไม่ทับของเกม)
3. ข้อความ — `mods/LostJudgmentThai/db.coyote.en/*.bin` แล้วรัน `ShinRyuModManager.exe -s`
   เพื่อ regen `YakuzaParless.mlo`

ใช้:  python scripts/deploy_title_poc.py            # deploy
      python scripts/deploy_title_poc.py --restore  # ถอน (คืน par จาก .orig + ลบโฟลเดอร์ม็อด)

ผู้ใช้เป็นคนเปิดเกมทดสอบเสมอ (กติกาเหล็กข้อ 2)
"""
import io
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                        # noqa: E402

MEDIA = paths.GAME / "runtime/media"
SRMM_SRC = paths.TOOLS / "SRMM-4.8.4"
SRMM_FILES = ["ShinRyuModManager.exe", "version.dll", "YakuzaParless.asi"]
BUILD_FONT = paths.BUILD / "font"
FONT_STAGE = paths.BUILD / "font_stage"
BUILD_TEXT = paths.BUILD / "text" / "db.coyote.en"
BUILD_UI = paths.BUILD / "ui"          # <par ที่จะทับ>/<ไฟล์ในนั้น> เช่น ui.coyote.en/font/*.bin


def font_repack():
    """สร้าง font.coyote.par ใหม่จาก .orig + ไฟล์ที่ build ไว้ แล้วเขียนทับไฟล์เกม"""
    par = paths.FONT_PAR
    orig = par.with_suffix(par.suffix + ".orig")
    assert par.exists(), "ไม่พบ %s" % par
    if not orig.exists():
        print("สำรอง %s -> %s (%s MB) ..." % (par.name, orig.name, par.stat().st_size // 1048576))
        shutil.copy2(par, orig)
    else:
        print("มี .orig อยู่แล้ว: %s" % orig.name)

    # staging: ไฟล์ต้องอยู่ระดับรากเหมือนใน par (par ของ LJ แบน ยกเว้นโฟลเดอร์ debug/)
    if FONT_STAGE.exists():
        shutil.rmtree(FONT_STAGE)
    FONT_STAGE.mkdir(parents=True)
    names = []
    for f in sorted(BUILD_FONT.glob("*")):
        if f.suffix.lower() in (".bin", ".dds"):
            shutil.copy2(f, FONT_STAGE / f.name)
            names.append(f.name)
    assert names, "ยังไม่ได้ build ฟอนต์ (scripts/inject_thai_sdf.py)"
    print("ฟอนต์ที่จะใส่กลับเข้า par: %s" % ", ".join(names))

    out_par = paths.BUILD / "font.coyote.par"
    if out_par.exists():
        out_par.unlink()
    t0 = time.time()
    r = subprocess.run([str(paths.PARTOOL), "add", str(orig), str(FONT_STAGE), str(out_par)],
                       capture_output=True, text=True, timeout=3600)
    if r.returncode != 0 or not out_par.exists():
        sys.exit("ParTool add ล้ม: rc=%d\n%s\n%s" % (r.returncode, r.stdout[-800:], r.stderr[-800:]))
    print("repack เสร็จใน %.1f วินาที (%s MB)" % (time.time() - t0, out_par.stat().st_size // 1048576))

    shutil.copy2(out_par, par)
    print("drop-in: %s (%s MB)" % (par.name, par.stat().st_size // 1048576))


def srmm_and_mods():
    for name in SRMM_FILES:
        dst = MEDIA / name
        if dst.exists():
            print("SRMM มีแล้ว: %s" % name)
        else:
            shutil.copy2(SRMM_SRC / name, dst)
            print("ติดตั้ง SRMM: %s" % name)

    assert BUILD_TEXT.exists(), "ยังไม่ได้ build ข้อความ (scripts/make_title_thai.py)"
    dst_root = paths.MODS_DIR / "db.coyote.en"
    if dst_root.exists():
        shutil.rmtree(dst_root)
    dst_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUILD_TEXT, dst_root)
    files = sorted(p.name for p in dst_root.rglob("*") if p.is_file())
    print("mods: %s (%s)" % (dst_root, ", ".join(files)))

    # ตารางฟอนต์สไปรต์ของ UI (LJ-015) — loose file ทับ ui.coyote.en.par ผ่าน Parless
    for src in sorted(BUILD_UI.glob("*")) if BUILD_UI.exists() else []:
        if not src.is_dir():
            continue
        dst = paths.MODS_DIR / src.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        n = sum(1 for p in dst.rglob("*") if p.is_file())
        print("mods: %s (%d ไฟล์)" % (dst, n))

    r = subprocess.run([str(MEDIA / "ShinRyuModManager.exe"), "-s"],
                       cwd=str(MEDIA), capture_output=True, text=True, timeout=1800)
    mlo = MEDIA / "YakuzaParless.mlo"
    size = mlo.stat().st_size if mlo.exists() else 0
    print("regen MLO: rc=%d, %s B" % (r.returncode, "{:,}".format(size)))
    tail = (r.stdout or "").strip().splitlines()[-12:]
    if tail:
        print("\n".join(tail))
    if r.returncode != 0 or not mlo.exists():
        sys.exit("!! MLO ไม่สำเร็จ — ห้ามเปิดเกมจนกว่าจะแก้")


def restore():
    par = paths.FONT_PAR
    orig = par.with_suffix(par.suffix + ".orig")
    if orig.exists():
        shutil.copy2(orig, par)
        print("คืนฟอนต์: %s จาก .orig" % par.name)
    else:
        print("ไม่มี .orig ให้คืน (ฟอนต์อาจยังไม่เคย deploy)")
    for name in ("db.coyote.en", "ui.coyote.en"):
        dst_root = paths.MODS_DIR / name
        if dst_root.exists():
            shutil.rmtree(dst_root)
            print("ลบ %s" % dst_root)
    srmm = MEDIA / "ShinRyuModManager.exe"
    if srmm.exists():
        subprocess.run([str(srmm), "-s"], cwd=str(MEDIA), capture_output=True, timeout=1800)
        print("regen MLO (ว่าง)")


if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        font_repack()
        srmm_and_mods()
        print("\nพร้อมทดสอบ — เปิดเกมแล้วดูหน้าไตเติล (ผู้ใช้เป็นคนเปิดเกม)")
