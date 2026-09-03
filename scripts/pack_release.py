"""แพ็ก pak ม็อดด้วย repak แล้วประกอบชุดปล่อย (zip) — ขั้นตอน §0.6 ของ HANDOFF ทำเป็นสคริปต์

ทำไมต้อง repak: pak ที่ `tools/pakwrite.py` เขียนเอง เกมไม่โหลด (HANDOFF §0.2) จึงต้อง
  1) แตก build/LikeADragonIshinThai_P.pak (ผลจาก build_text.py) ลง build/stage_pak/ ตาม path ในเกม
  2) tools/repak/repak.exe pack --mount-point ../../../ --version V11 build/stage_pak build/IshinThai_P.pak
  3) เปิด pak ที่ repak เขียน เทียบไบต์ทุกไฟล์กับ stage_pak — ต้อง ต่าง 0 · หาย 0 · เกิน 0
  4) ประกอบ release/LikeADragonIshinThai-<ver>/ (files/IshinThai_P.pak + install/uninstall + README + patch.md)
     แล้ว zip เป็น release/LikeADragonIshinThai-<ver>.zip

ใช้:  python scripts/pack_release.py --version v1.0 [--install]
  --install  คัดลอก pak เข้า ~mods ของเกมด้วย (ลบ IshinThai*_P.pak เวอร์ชันเก่าออกก่อน)
ไม่แตะไฟล์ต้นฉบับของเกม · ไม่เปิดเกม
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths  # noqa: E402
from pakfile import PakFile  # noqa: E402

REPAK = paths.PROJECT / "tools" / "repak" / "repak.exe"
STAGE = paths.BUILD / "stage_pak"
OUT_PAK = paths.BUILD / "IshinThai_P.pak"
PACKAGING = paths.PROJECT / "packaging"
RELEASE = paths.PROJECT / "release"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_from_pak(src):
    if STAGE.exists():
        shutil.rmtree(STAGE)
    pk = PakFile(src)
    n = 0
    for gp in sorted(pk.files):
        pk.extract(gp, STAGE)
        n += 1
    print("แตก %s → %s · %d ไฟล์" % (src.name, STAGE, n))
    return n


def repak_pack():
    if OUT_PAK.exists():
        OUT_PAK.unlink()
    cmd = [str(REPAK), "pack", "--mount-point", "../../../", "--version", "V11", str(STAGE), str(OUT_PAK)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not OUT_PAK.exists():
        print(r.stdout, r.stderr)
        raise SystemExit("repak ล้มเหลว")
    print("repak: %s · %.1f MB" % (OUT_PAK, OUT_PAK.stat().st_size / 1e6))


def verify_pak():
    """เทียบไบต์ทุกไฟล์ใน pak ที่ repak เขียน กับ stage_pak (ไม่ใช่ decode ซ้ำด้วยเครื่องมือเดียวกัน)"""
    pk = PakFile(OUT_PAK)
    stage_files = {p.relative_to(STAGE).as_posix(): p for p in STAGE.rglob("*") if p.is_file()}
    same = diff = 0
    seen = set()
    for gp in pk.files:
        rel = gp
        while rel.startswith("../"):
            rel = rel[3:]
        rel = rel.lstrip("/")
        sp = stage_files.get(rel)
        if sp is None:
            print("  เกินมาใน pak: %s" % gp)
            diff += 1
            continue
        seen.add(rel)
        if pk.read(gp) == sp.read_bytes():
            same += 1
        else:
            print("  ไบต์ต่าง: %s" % gp)
            diff += 1
    missing = set(stage_files) - seen
    for m in sorted(missing)[:10]:
        print("  หายจาก pak: %s" % m)
    print("ตรวจ pak: ตรงกัน %d · ต่าง %d · หาย %d" % (same, diff, len(missing)))
    if diff or missing:
        raise SystemExit("pak ไม่ตรง stage_pak — ห้ามปล่อย")
    return same


def assemble(version, n_translated):
    name = "LikeADragonIshinThai-%s" % version
    out = RELEASE / name
    if out.exists():
        shutil.rmtree(out)
    (out / "files").mkdir(parents=True)
    shutil.copy2(OUT_PAK, out / "files" / "IshinThai_P.pak")
    for f in ("install.bat", "install.ps1", "uninstall.bat", "uninstall.ps1"):
        shutil.copy2(PACKAGING / f, out / f)
    readme = (PACKAGING / "README.txt").read_text(encoding="utf-8")
    readme = readme.replace("{VERSION}", version).replace("{N_TRANSLATED}", "{:,}".format(n_translated))
    (out / "README.txt").write_text("﻿" + readme, encoding="utf-8")
    patch = paths.PROJECT / "patch.md"
    if patch.exists():
        shutil.copy2(patch, out / "patch.md")
    zpath = RELEASE / (name + ".zip")
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, (Path(name) / p.relative_to(out)).as_posix())
    print("ชุดปล่อย: %s · %.1f MB · sha256 %s" % (zpath, zpath.stat().st_size / 1e6, sha256(zpath)))
    return zpath


def count_translated():
    m = json.loads(paths.MASTER_TH.read_text(encoding="utf-8"))
    n = 0
    for k, v in m.items():
        th = v if isinstance(v, str) else (v or {}).get("th")
        if th and th != k:
            n += 1
    return n


def install():
    dst = paths.MODS_DIR
    dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("*.pak"):
        if old.name.startswith("IshinThai") or old.name == paths.MOD_PAK:
            old.unlink()
            print("  ลบเวอร์ชันเก่า: %s" % old.name)
    shutil.copy2(OUT_PAK, dst / "IshinThai_P.pak")
    print("ติดตั้งแล้ว: %s (การทดสอบในเกมเป็นหน้าที่ผู้ใช้)" % (dst / "IshinThai_P.pak"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True, help="เช่น v1.0")
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    src = paths.BUILD / paths.MOD_PAK
    if not src.exists():
        raise SystemExit("ไม่พบ %s — รัน scripts/build_text.py ก่อน" % src)
    if not REPAK.exists():
        raise SystemExit("ไม่พบ %s" % REPAK)
    stage_from_pak(src)
    repak_pack()
    verify_pak()
    n = count_translated()
    print("ประโยคที่แปล (ต่างจากต้นฉบับ): {:,}".format(n))
    assemble(a.version, n)
    if a.install:
        install()
    return 0


if __name__ == "__main__":
    sys.exit(main())
