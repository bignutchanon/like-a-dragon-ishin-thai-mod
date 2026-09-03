#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""บิลด์ข้อความไทยทั้งเกมจาก `translations/master_th.json` -> `build/text/db.coyote.en/en/*.bin`

สายงาน (ทั้งหมดอิงข้อเท็จจริงที่ยืนยันกับไฟล์เกมจริงแล้ว — ดู docs/research.md):
  1. `extracted/strings_by_bin.json`  บอกว่า bin ไหนมีข้อความแปลได้บ้าง (ผลจาก extract_all_en.py)
  2. `translations/master_th.json`    คำแปลรวม (EN -> ไทย · source of truth ข้อเดียว)
  3. `SlotMap.encode()`               ไทย -> สตริง donor ตาม `translations/slotmap.json`
     (map เดียวกับที่ `inject_thai_title.py --slotmap` ใช้วาดกลิฟ — ห้ามมีสำเนาที่สอง)
  4. `tools/reARMP_fixed.py`          JSON -> .bin (ทำงานบนสำเนาใน temp เท่านั้น)

ไม่แตะไฟล์ต้นฉบับใน `extracted/` และไม่แตะเกม — deploy เป็นหน้าที่ `deploy_spoil.py`

bin ที่ข้าม:
  * DENY_BINS  (identifier/พารามิเตอร์เอนจิ้น — ตัดสินแล้วใน make_worklist.py)
  * KEEP_EN_BINS (license/EULA/credits — กติกาเหล็กข้อ 10)
  * RAW_BINS ที่ reARMP rebuild ไม่ได้ — ทำด้วย `scripts/patch_bin_raw.py` แทน

ใช้:
  python scripts/build_text.py                    # บิลด์ทั้งเกม
  python scripts/build_text.py --bins talk.bin    # เฉพาะบางไฟล์
  python scripts/build_text.py --workers 8 --dry-run
"""
import argparse
import concurrent.futures as cf
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths                                        # noqa: E402
from make_worklist import DENY_BINS, KEEP_EN_BINS, KEEP_EN_COLUMNS   # noqa: E402
from slot_alloc import SlotMap                      # noqa: E402

BY_BIN = paths.EXTRACTED / "strings_by_bin.json"
SRC_DIR = paths.DB_EN
STAGE = paths.BUILD / "text" / "db.coyote.en"
REPORT = paths.BUILD / "text" / "build_report.md"

# bin ที่ reARMP export ไม่ผ่านตั้งแต่ตอน extract -> ต้องแพตช์ระดับไบต์ (patch_bin_raw.py)
RAW_BINS = {"ui_layer_text.bin"}


def rearmp_encode(json_path, work):
    """JSON -> .bin ด้วย reARMP (เขียนผลลง cwd) — คืน (path, None) หรือ (None, สาเหตุ)"""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    res = subprocess.run([sys.executable, str(paths.REARMP), json_path.name],
                         cwd=str(work), env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, timeout=1800)
    out = work / (json_path.name + ".bin")
    if res.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        err = res.stderr.decode("utf-8", "replace").strip().splitlines()
        return None, "exit %d: %s" % (res.returncode, err[-1] if err else "?")
    return out, None


def walk_replace(obj, mapping, counter, skip_cols=frozenset(), done=None):
    """แทนที่เฉพาะ value ที่ตรงเป๊ะกับคีย์ใน mapping (key ของ dict = row/column name — ไม่แตะ)

    `skip_cols` = ชื่อคอลัมน์ที่ต้องคงต้นฉบับอังกฤษไว้ (KEEP_EN_COLUMNS) เพราะค่าในนั้นเป็น
    identifier ที่เอนจิ้นใช้ค้นหา ไม่ใช่ข้อความบนจอ — เทียบที่ **ชื่อคีย์ของ dict** ซึ่งใน JSON
    ของ reARMP คือชื่อคอลัมน์พอดี (คอลัมน์แบบอาร์เรย์จะเป็น `col[0]` จึงตัดวงเล็บก่อนเทียบ)
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if v in mapping and _col_of(k) not in skip_cols:
                    obj[k] = mapping[v]
                    counter[0] += 1
                    if done is not None:
                        done.add(mapping[v])
            else:
                walk_replace(v, mapping, counter, skip_cols, done)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                if v in mapping:
                    obj[i] = mapping[v]
                    counter[0] += 1
                    if done is not None:
                        done.add(mapping[v])
            else:
                walk_replace(v, mapping, counter, skip_cols, done)


def _col_of(key):
    """`words[3]` -> `words` · คีย์อื่นคืนตามเดิม"""
    return key.split("[", 1)[0] if isinstance(key, str) else key


def build_one(bin_name, mapping):
    """บิลด์ bin เดียว -> dict สรุปผล (ทำงานใน temp dir ของตัวเอง จึงขนานได้ปลอดภัย)"""
    src_json = SRC_DIR / (bin_name + ".json")
    if not src_json.exists():
        return {"bin": bin_name, "ok": False, "err": "ไม่มี JSON (extract ไม่ผ่าน)", "n": 0}
    work = Path(tempfile.mkdtemp(prefix="jeth_"))
    try:
        tmp_json = work / "t.bin.json"
        shutil.copy2(src_json, tmp_json)
        d = json.load(io.open(tmp_json, encoding="utf-8"))
        c, done = [0], set()
        walk_replace(d, mapping, c, KEEP_EN_COLUMNS.get(bin_name, frozenset()), done)
        if c[0] == 0:
            # ไม่มีอะไรต้องแทนแล้ว (เช่น ทุกคอลัมน์ของ bin นี้อยู่ใน KEEP_EN_COLUMNS)
            # ต้อง **ลบไฟล์ที่เคยบิลด์ไว้** ไม่งั้นของเก่าที่ผิดจะค้างอยู่ใน stage แล้วถูก deploy ต่อ
            stale = STAGE / bin_name
            if stale.exists():
                stale.unlink()
            return {"bin": bin_name, "ok": True, "err": None, "n": 0}
        json.dump(d, io.open(tmp_json, "w", encoding="utf-8"), ensure_ascii=False)
        out, err = rearmp_encode(tmp_json, work)
        if out is None:
            return {"bin": bin_name, "ok": False, "err": err, "n": c[0]}
        # ตรวจกลับระดับไบต์: สตริงที่แทนไปต้องโผล่จริงในไฟล์ผลลัพธ์
        blob = out.read_bytes()
        sample = sorted(done)[:5]        # สุ่มจากสิ่งที่ **แทนจริง** — mapping อาจมีตัวที่ถูก
                                         # KEEP_EN_COLUMNS กันไว้ ซึ่งไม่มีทางโผล่ในผลลัพธ์
        missing = [s for s in sample if s.encode("utf-8") not in blob]
        if missing:
            return {"bin": bin_name, "ok": False, "n": c[0],
                    "err": "สตริงที่แทนไม่อยู่ในผลลัพธ์ (%d/%d ตัวอย่าง)"
                           % (len(missing), len(sample))}
        STAGE.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out), str(STAGE / bin_name))
        return {"bin": bin_name, "ok": True, "err": None, "n": c[0],
                "size": (STAGE / bin_name).stat().st_size}
    except Exception as e:                                   # noqa: BLE001
        return {"bin": bin_name, "ok": False, "err": "%s: %s" % (type(e).__name__, e), "n": 0}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def make_mappings(only=None):
    """{bin: {EN: สตริง donor}} + สถิติการ encode

    ขอบเขตการแทนที่ยึด `strings_by_bin.json` (ตัวคัดกรองเดียวกับที่ใช้ทำ worklist)
    จึงไม่ไปโดน identifier ที่บังเอิญสะกดเหมือนข้อความในไฟล์อื่น
    """
    master = json.load(io.open(paths.MASTER_TH, encoding="utf-8"))
    by_bin = json.load(io.open(BY_BIN, encoding="utf-8"))
    cache, fails = {}, {}
    out = {}
    for bin_name, strings in sorted(by_bin.items()):
        if only and bin_name not in only:
            continue
        if bin_name in DENY_BINS or bin_name in KEEP_EN_BINS or bin_name in RAW_BINS:
            continue
        # LJ มี donor map สองชุด (docs/research.md §3.6) — เลือกตาม bin ปลายทาง ไม่ใช่ map เดียวทั้งเกม
        sm = SlotMap.for_bin(bin_name)
        m = {}
        for en in strings:
            th = master.get(en)
            if not isinstance(th, str) or not th.strip() or th == en:
                continue
            ck = (sm.name, th)
            if ck not in cache:
                try:
                    cache[ck] = sm.encode(th)
                except SystemExit as e:
                    cache[ck] = None
                    fails.setdefault(str(e), []).append(th)
                except Exception as e:                       # noqa: BLE001
                    cache[ck] = None
                    fails.setdefault("%s: %s" % (type(e).__name__, e), []).append(th)
            if cache[ck] is not None:
                m[en] = cache[ck]
        if m:
            out[bin_name] = m
    n_enc = sum(1 for v in cache.values() if v is not None)
    return out, {"encoded": n_enc,
                 "failed": sum(len(v) for v in fails.values()),
                 "fail_kinds": fails}


def write_report(results, stats, elapsed, path=REPORT):
    ok = [r for r in results if r["ok"] and r["n"]]
    skipped = [r for r in results if r["ok"] and not r["n"]]
    bad = [r for r in results if not r["ok"]]
    L = ["# Build report — ข้อความไทยทั้งเกม", "",
         "> สร้างด้วย `python scripts/build_text.py` — ห้ามแก้ด้วยมือ", "",
         "| ตัวชี้วัด | ค่า |", "|---|---|",
         "| bin ที่บิลด์สำเร็จ | %d |" % len(ok),
         "| สตริงที่แทนที่รวม | %s |" % "{:,}".format(sum(r["n"] for r in ok)),
         "| ประโยคไทย unique ที่ encode ผ่าน | %s |" % "{:,}".format(stats["encoded"]),
         "| encode ไม่ผ่าน | %d |" % stats["failed"],
         "| bin ที่บิลด์ไม่ผ่าน | %d |" % len(bad),
         "| bin ที่ไม่มีคู่แปล (ข้าม) | %d |" % len(skipped),
         "| เวลา | %.1f วินาที |" % elapsed, "",
         "## bin ที่บิลด์สำเร็จ (เรียงตามจำนวนสตริง)", "",
         "| bin | สตริงที่แทน | ขนาด (B) |", "|---|---|---|"]
    for r in sorted(ok, key=lambda r: -r["n"]):
        L.append("| %s | %s | %s |" % (r["bin"], "{:,}".format(r["n"]),
                                       "{:,}".format(r.get("size", 0))))
    L += ["", "## bin ที่บิลด์ไม่ผ่าน", ""]
    if bad:
        L += ["| bin | สตริงที่จะแทน | สาเหตุ |", "|---|---|---|"]
        L += ["| %s | %d | %s |" % (r["bin"], r["n"], r["err"]) for r in bad]
    else:
        L.append("ไม่มี")
    if stats["fail_kinds"]:
        L += ["", "## ประโยคที่ encode ไม่ผ่าน", ""]
        for kind, items in stats["fail_kinds"].items():
            L.append("- **%s** (%d ประโยค) เช่น `%s`" % (kind, len(items), items[0][:60]))
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    return path


# แพตช์ตารางฟอนต์ที่ต้องรัน **หลัง** บิลด์เสมอ (เขียนทับไฟล์ที่ build_text สร้างจาก vanilla)
#   * patch_font_faces.py  = อัปเดต texture_width/height ให้ตรง atlas ที่ขยายแล้ว
#     ไม่รัน -> เอนจิ้นคำนวณ UV ผิด -> กลิฟเพี้ยนทั้งฟอนต์
#   * patch_font_styles.py = ย้าย font_face_en ของ 126 สไตล์จากฟอนต์ vector ไปฟอนต์ SDF ที่มีไทย
#     ไม่รัน -> เทลอป/ป้ายต่อสู้ขึ้นเป็นตัวละติน donor ดิบ (LJ-002)
# เคยพลาดมาแล้ว 29 ส.ค. 2026: `build_text.py --clean` ล้าง stage แล้วบิลด์ทับด้วยของ vanilla
# ทำให้แพตช์ทั้งสองหายเงียบ ๆ และหลุดเข้าไฟล์แจก v1.0.1 (LJ-013)
POST_BUILD = ["patch_font_faces.py", "patch_font_styles.py"]


def run_post_build():
    ok = True
    for name in POST_BUILD:
        r = subprocess.run([sys.executable, str(paths.PROJECT / "scripts" / name), "--write"],
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                           capture_output=True, text=True)
        tail = (r.stdout or "").strip().splitlines()
        print("post-build %-24s rc=%d  %s" % (name, r.returncode, tail[-1] if tail else ""))
        ok = ok and r.returncode == 0
    if not ok:
        sys.exit("!! แพตช์ตารางฟอนต์ไม่สำเร็จ — ห้าม deploy จนกว่าจะแก้")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bins", default="", help="จำกัดเฉพาะ bin (คั่นด้วย ,)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true", help="คำนวณอย่างเดียว ไม่เขียนไฟล์")
    ap.add_argument("--clean", action="store_true", help="ล้าง stage ก่อนบิลด์")
    a = ap.parse_args()

    only = {b.strip() for b in a.bins.split(",") if b.strip()} or None
    t0 = time.time()
    mappings, stats = make_mappings(only)
    print("bin ที่ต้องบิลด์ %d · ประโยคไทย unique %s · encode ไม่ผ่าน %d"
          % (len(mappings), "{:,}".format(stats["encoded"]), stats["failed"]))
    for kind, items in stats["fail_kinds"].items():
        print("  !! %s (%d ประโยค)" % (kind, len(items)))
    if a.dry_run:
        return 0

    if a.clean and STAGE.exists():
        for f in STAGE.glob("*.bin"):
            if f.name not in RAW_BINS:
                f.unlink()
    # RAW_BINS ไม่ได้บิลด์ที่นี่ (reARMP rebuild ไม่ได้) — เตือนถ้าไฟล์เก่ากว่า slotmap
    # เพราะมันเก็บ "ไบต์ donor" ที่ผูกกับการจัดสรรรอบนั้น พอ slotmap เปลี่ยนจะกลายเป็นตัวมั่วทันที
    for name in RAW_BINS:
        f = STAGE / name
        if f.exists() and f.stat().st_mtime < paths.TRANSLATIONS.joinpath("slotmap.json").stat().st_mtime:
            print("  !! %s เก่ากว่า slotmap.json — รัน `python scripts/patch_bin_raw.py` ใหม่" % name)
    STAGE.mkdir(parents=True, exist_ok=True)

    results = []
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(build_one, b, m): b for b, m in mappings.items()}
        for i, fut in enumerate(cf.as_completed(futs), 1):
            r = fut.result()
            results.append(r)
            print("[%3d/%3d] %s%-44s %5d สตริง%s"
                  % (i, len(futs), "ok " if r["ok"] else "!! ", r["bin"], r["n"],
                     "" if r["ok"] else "  <- " + str(r["err"])))
    bad = [r for r in results if not r["ok"]]
    if not bad and only is None:
        run_post_build()          # ต้องรันหลังบิลด์เสมอ — ดูคอมเมนต์ที่ POST_BUILD
    el = time.time() - t0
    print("เขียน", write_report(results, stats, el))
    print("สำเร็จ %d bin · ล้มเหลว %d · %.1f วินาที"
          % (len([r for r in results if r["ok"] and r["n"]]), len(bad), el))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
