#!/usr/bin/env python3
"""deploy ชุดสปอย/ทดสอบ A-B ลงเกม Lost Judgment

ทำ 3 อย่าง (ทั้งหมดอยู่ในขอบเขตที่กติกาเหล็กอนุญาต):
1. ฟอนต์: drop-in ทับทุกไฟล์ที่อยู่ใน build/font และมีคู่จริงในเกม — backup .orig ก่อนเสมอ
   (ครั้งแรกเท่านั้น .orig มีแล้วไม่ทับ) — copy จาก .orig ไม่ได้เพราะแทนทั้งไฟล์ ไม่มี layering
2. SRMM: วาง ShinRyuModManager.exe + version.dll + YakuzaParless.asi ใน runtime/media
   (เพิ่มไฟล์ใหม่ ไม่ทับของเกม)
3. mods/LostJudgmentThai/db.coyote.en/en/title_root.bin + รัน `ShinRyuModManager.exe -s`
   regen YakuzaParless.mlo

ใช้:  python scripts/deploy_spoil.py             # deploy จริง (ฟอนต์ drop-in ทับไฟล์เกม)
      python scripts/deploy_spoil.py --as-release # ติดตั้งแบบเดียวกับไฟล์แจก: ฟอนต์อยู่ใน
                                                  # โฟลเดอร์ม็อด และคืนฟอนต์เกมจาก .orig
                                                  # (ใช้ทดสอบว่าไฟล์แจกใช้ได้จริงก่อนปล่อย)
      python scripts/deploy_spoil.py --restore    # ถอดทุกอย่างกลับ (ฟอนต์คืนจาก .orig)
"""
import io
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths

MEDIA = paths.GAME / "runtime/media"
SRMM_SRC = paths.TOOLS / "SRMM-4.8.4"
SRMM_FILES = ["ShinRyuModManager.exe", "version.dll", "YakuzaParless.asi"]
BUILD_FONT = paths.BUILD / "font"
BUILD_TEXT = paths.BUILD / "text"


def font_files():
    """ไฟล์ฟอนต์ที่ build ไว้และมีคู่จริงในเกม — รองรับทั้ง tbgm_0p_ja (ข้อความหลัก)
    และ meta_ot_cond_book (ไตเติล/เมนู) โดยไม่ต้องแก้สคริปต์เวลาเพิ่มไฟล์ใหม่"""
    out = []
    for f in sorted(BUILD_FONT.glob("*")):
        if f.suffix.lower() in (".bin", ".dds") and (paths.FONT_GAME_DIR / f.name).exists():
            out.append(f.name)
    assert out, f"ไม่มีไฟล์ฟอนต์ที่ build ไว้ใน {BUILD_FONT}"
    return out


def deploy(as_release=False):
    assert paths.GAME.exists(), f"ไม่พบเกม: {paths.GAME}"
    # ---- 1) ฟอนต์ ----
    if as_release:
        # โหมดไฟล์แจก: ฟอนต์ต้องมาจากโฟลเดอร์ม็อด ไม่ใช่ drop-in → คืนไฟล์เกมให้เป็นต้นฉบับก่อน
        for orig in sorted(paths.FONT_GAME_DIR.glob("*.orig")):
            shutil.copy2(orig, orig.with_suffix(""))
            print(f"คืนฟอนต์เกมเป็นต้นฉบับ: {orig.with_suffix('').name}")
    else:
        _font_dropin()

    _srmm_and_mods(as_release)


def _font_dropin():
    for name in font_files():
        game_f = paths.FONT_GAME_DIR / name
        orig = game_f.with_suffix(game_f.suffix + ".orig")
        built = BUILD_FONT / name
        assert built.exists(), f"ยังไม่ได้ build ฟอนต์: {built}"
        assert game_f.exists(), f"ไม่พบไฟล์เกม: {game_f}"
        if not orig.exists():
            shutil.copy2(game_f, orig)
            print(f"backup {orig.name}")
        shutil.copy2(built, game_f)
        print(f"font drop-in: {name} ({built.stat().st_size} B)")


def _srmm_and_mods(as_release=False):
    # ---- 2) SRMM ----
    for name in SRMM_FILES:
        dst = MEDIA / name
        if not dst.exists():
            shutil.copy2(SRMM_SRC / name, dst)
            print(f"ติดตั้ง SRMM: {name}")
        else:
            print(f"SRMM มีแล้ว: {name}")

    # ---- 3) mods + MLO ----
    mod_src = BUILD_TEXT / "db.coyote.en"
    assert mod_src.exists(), "ยังไม่ได้ build db (scripts/build_text.py)"
    dst_root = paths.MODS_DIR / "db.coyote.en"
    if dst_root.exists():
        shutil.rmtree(dst_root)
    shutil.copytree(mod_src, dst_root)
    n = sum(1 for _ in dst_root.rglob("*") if _.is_file())
    print(f"mods: {dst_root} ({n} ไฟล์)")

    font_mod = paths.MODS_DIR / "font.coyote" / "en"
    if font_mod.exists():
        shutil.rmtree(font_mod)
    if as_release:
        font_mod.mkdir(parents=True)
        for name in ("meta_ot_cond_book.dds", "meta_ot_cond_book_italic.dds"):
            shutil.copy2(BUILD_FONT / name, font_mod / name)
        print(f"mods (ฟอนต์): {font_mod} (2 ไฟล์)")

    r = subprocess.run([str(MEDIA / "ShinRyuModManager.exe"), "-s"],
                       cwd=str(MEDIA), capture_output=True, text=True)
    mlo = MEDIA / "YakuzaParless.mlo"
    print(f"regen MLO: rc={r.returncode}, {mlo.stat().st_size if mlo.exists() else 0} B")
    tail = (r.stdout or "").strip().splitlines()[-12:]
    print("\n".join(tail))
    if r.returncode != 0 or not mlo.exists():
        sys.exit("!! MLO ไม่สำเร็จ — ห้ามเปิดเกมจนกว่าจะแก้")


def restore():
    # คืนทุกไฟล์ที่มี .orig อยู่จริง (ไม่ผูกกับรายชื่อ hardcode)
    for orig in sorted(paths.FONT_GAME_DIR.glob("*.orig")):
        game_f = orig.with_suffix("")
        shutil.copy2(orig, game_f)
        print(f"คืนฟอนต์: {game_f.name}")
    for sub in ("db.coyote.en", "font.coyote"):
        dst_root = paths.MODS_DIR / sub
        if dst_root.exists():
            shutil.rmtree(dst_root)
            print("ลบ mods/%s" % sub)
    srmm = MEDIA / "ShinRyuModManager.exe"
    if srmm.exists():
        subprocess.run([str(srmm), "-s"], cwd=str(MEDIA), capture_output=True)
        print("regen MLO (ว่าง)")


if __name__ == "__main__":
    if "--restore" in sys.argv:
        restore()
    else:
        deploy(as_release="--as-release" in sys.argv)
