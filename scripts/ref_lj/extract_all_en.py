#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สกัด string อังกฤษทั้งหมดจาก db.coyote.en.par (Lost Judgment — port จาก K3 20 ส.ค. 2026)

ขั้นตอน:
  1) แปลงทุก extracted/db_en/*.bin (ARMP v2) -> .bin.json คู่กัน ด้วย tools/reARMP_fixed.py
     (subprocess ขนาน, ไฟล์ที่พังเก็บ error ไว้ ไม่หยุดทั้งงาน; ข้ามไฟล์ที่มี .json แล้ว เว้นแต่ --force)
  2) เดินเก็บ string "ที่น่าจะแปลได้" จาก JSON ทุกไฟล์ (เดินเฉพาะ value ไม่เอา key
     เพราะ row/column name เป็น identifier — แนวเดียวกับ PIRATE/scripts/extract_strings.py)
  3) เขียนผลลัพธ์:
     - extracted/strings_by_bin.json   {bin: [string, ...]}  (unique ภายใน bin, เรียงตามที่พบ)
     - extracted/unique_strings.json   {string: {"count": n, "bins": [...]}}
       (count = จำนวนครั้งที่พบทั้งหมดใน JSON ทุกไฟล์ นับซ้ำใน bin เดียวกันด้วย)
     - extracted/extract_report.md     สถิติ + รายชื่อไฟล์ที่แปลงไม่ผ่าน

เกณฑ์คัด string (ดู is_translatable):
  - เป็น str และมีตัวอักษร A-Za-z >= 2 ตัว
  - ไม่ใช่ตัวเลข/hex ล้วน (ไม่มีตัวอักษรก็ตกเกณฑ์แรกอยู่แล้ว, hex เช่น DEADBEEF โดน SCREAMING rule)
  - token เดี่ยวรูป identifier/path ([A-Za-z0-9_./\\:-]+ ไม่มีช่องว่าง) ที่มี _ / . / ตัวเลข ฯลฯ -> ทิ้ง
    ยกเว้น token ที่เป็นตัวอักษรล้วน (เช่น "Continue", "Yes") เก็บไว้ ตาม logic ของ
    PIRATE extract_strings.py — แต่คำ ALLCAPS ยาว >3 (SCREAMING_ENUM) ทิ้ง
  - string ที่มี placeholder/tag (%s, <...>) หรือช่องว่าง/ขึ้นบรรทัด -> เก็บ
  - ที่เป็นภาษาไทยอยู่แล้ว -> ข้าม

ใช้:
  python scripts/extract_all_en.py [--workers 8] [--force] [--convert-only|--collect-only]
"""
import argparse
import concurrent.futures as cf
import io
import json
import os
import re
import subprocess
import sys
import time
from collections import OrderedDict

# console Windows เป็น cp1252 — wrap stdout/stderr เป็น utf-8 กันพังเวลา print ไทย
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- filter ----
IDENT_RE = re.compile(r"^[A-Za-z0-9_./\\:\-]+$")  # รูป identifier/path (ไม่มีช่องว่าง)
PURE_ALPHA_RE = re.compile(r"^[A-Za-z]+$")
LETTER_RE = re.compile(r"[A-Za-z]")
# token ตัวอักษร + เครื่องหมายประโยคเท่านั้น (จุด/ขีด/apostrophe/ellipsis) ไม่มี _ / \ : หรือเลข
# = คำพูดสั้นในบทสนทนา เช่น 'Yeah.' 'O-Oh.' 'Aniki...' "it's" (แก้บั๊กที่เคยตกหล่น 277 บทพูด)
DIALOG_TOKEN_RE = re.compile(r"^[A-Za-z.\-'’…]+$")


def is_translatable(s):
    """string นี้ควรเข้าคิวแปลไหม"""
    if not isinstance(s, str):
        return False
    if len(LETTER_RE.findall(s)) < 2:      # ต้องมีอักษรละติน >= 2 (ตัด %s, ตัวเลข/สัญลักษณ์ล้วน)
        return False
    if any("฀" <= c <= "๿" for c in s):   # ไทยอยู่แล้ว
        return False
    t = s.strip()
    if not t:
        return False
    if IDENT_RE.fullmatch(t):
        # token เดี่ยวไม่มีช่องว่าง รูป identifier/path/hex/เลข
        if PURE_ALPHA_RE.fullmatch(t):
            # คำเดี่ยวตัวอักษรล้วน เช่น Continue / Yes — เก็บ
            # ⚠ เดิมตัด ALLCAPS ยาว >3 ทิ้ง (กัน SCREAMING_ENUM) แต่ 22 ส.ค. 2026 พบว่ากติกานี้
            # ทิ้ง **ป้าย UI จริง** ไปด้วย: CONTINUE / SETTINGS / REPLAY / EASY / NORMAL / HARD /
            # LEGEND / CUSTOMIZE / DRONE ... (เห็นบนจอเป็นภาษาอังกฤษกลางเมนูไทย)
            # enum จริง ๆ ที่เป็น ALLCAPS อยู่รวมกันใน bin เดียว (chat_commands) ซึ่งย้ายไป
            # KEEP_EN_BINS แล้ว จึงเลิกตัดด้วยรูปคำ
            if t.isupper() and len(t) > 16:
                return False
            return True
        # token ตัวอักษร+จุด/ขีด/apostrophe (ไม่มี _ / \ : เลข) = คำพูดสั้น เช่น 'Yeah.' 'Aniki...' → เก็บ
        if DIALOG_TOKEN_RE.fullmatch(t) and not (t.isupper() and len(t) > 3):
            return True
        return False  # มี _ / \ : หรือตัวเลขปน = identifier/path/ID
    return True  # มีช่องว่าง/บรรทัดใหม่/เครื่องหมายอื่น/tag <...> = ข้อความแสดงผล


def walk_strings(obj, sink):
    """เดินเก็บ str ทุกตัวจาก JSON (เฉพาะ value — key คือ row/column name)"""
    if isinstance(obj, dict):
        for v in obj.values():
            walk_strings(v, sink)
    elif isinstance(obj, list):
        for v in obj:
            walk_strings(v, sink)
    elif isinstance(obj, str):
        sink.append(obj)


# --------------------------------------------------------------- convert ----
def convert_one(bins_dir, rearmp, bin_name, timeout, force):
    """แปลง bin เดียว -> (bin_name, ok, error_msg, cached)"""
    bin_path = os.path.join(bins_dir, bin_name)
    json_path = bin_path + ".json"
    if not force and os.path.isfile(json_path) and os.path.getsize(json_path) > 0:
        return bin_name, True, None, True
    try:
        with open(bin_path, "rb") as f:
            magic = f.read(4)
        if magic != b"armp":
            return bin_name, False, "not ARMP (magic=%r)" % magic, False
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        # reARMP_fixed.py เขียน <basename>.json ลง cwd เมื่อส่ง path ไม่มี backslash
        res = subprocess.run(
            [sys.executable, rearmp, bin_name],
            cwd=bins_dir, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if res.returncode != 0:
            err = res.stderr.decode("utf-8", "replace").strip().splitlines()
            return bin_name, False, "exit %d: %s" % (res.returncode, err[-1] if err else "?"), False
        if not os.path.isfile(json_path) or os.path.getsize(json_path) == 0:
            return bin_name, False, "no json produced", False
        return bin_name, True, None, False
    except subprocess.TimeoutExpired:
        return bin_name, False, "timeout after %ds" % timeout, False
    except Exception as e:  # noqa: BLE001 — เก็บ error รายไฟล์ ไม่ให้ล้มทั้งงาน
        return bin_name, False, "%s: %s" % (type(e).__name__, e), False


def convert_all(bins_dir, rearmp, workers, timeout, force):
    bins = sorted(f for f in os.listdir(bins_dir) if f.lower().endswith(".bin"))
    errors = OrderedDict()
    done = cached = 0
    t0 = time.time()
    print("[convert] %d bins, %d workers" % (len(bins), workers), flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(convert_one, bins_dir, rearmp, b, timeout, force) for b in bins]
        for fut in cf.as_completed(futs):
            name, ok, err, was_cached = fut.result()
            done += 1
            cached += was_cached
            if not ok:
                errors[name] = err
                print("[convert] FAIL %s : %s" % (name, err), flush=True)
            if done % 50 == 0 or done == len(bins):
                print("[convert] %d/%d (%.0fs elapsed, %d failed)"
                      % (done, len(bins), time.time() - t0, len(errors)), flush=True)
    return bins, errors, cached


# --------------------------------------------------------------- collect ----
def collect_all(bins_dir, bins, errors):
    strings_by_bin = OrderedDict()
    unique = OrderedDict()   # s -> {"count": n, "bins": set()}
    raw_total = 0            # จำนวน string ดิบทั้งหมดที่ผ่านเกณฑ์ (นับซ้ำ)
    for bin_name in bins:
        if bin_name in errors:
            continue
        json_path = os.path.join(bins_dir, bin_name) + ".json"
        try:
            with io.open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001
            errors[bin_name] = "json load: %s: %s" % (type(e).__name__, e)
            continue
        sink = []
        walk_strings(data, sink)
        seen = OrderedDict()  # unique ภายใน bin ตามลำดับที่พบ
        for s in sink:
            if not is_translatable(s):
                continue
            raw_total += 1
            seen.setdefault(s, 0)
            seen[s] += 1
        strings_by_bin[bin_name] = list(seen.keys())
        for s, n in seen.items():
            ent = unique.get(s)
            if ent is None:
                ent = unique[s] = {"count": 0, "bins": []}
            ent["count"] += n
            ent["bins"].append(bin_name)
    return strings_by_bin, unique, raw_total


# ---------------------------------------------------------------- report ----
KEY_BINS = ["talk.bin", "auth.bin", "sound_auth.bin", "item.bin", "msg.bin",
            "ui_text.bin", "title_root.bin", "caption.bin", "pause_message.bin",
            "manual.bin", "ui_preview_text.bin"]


def write_outputs(out_dir, bins, errors, cached, strings_by_bin, unique, raw_total, elapsed):
    os.makedirs(out_dir, exist_ok=True)
    p_by_bin = os.path.join(out_dir, "strings_by_bin.json")
    p_unique = os.path.join(out_dir, "unique_strings.json")
    p_report = os.path.join(out_dir, "extract_report.md")

    with io.open(p_by_bin, "w", encoding="utf-8") as f:
        json.dump(strings_by_bin, f, ensure_ascii=False, indent=1)
    with io.open(p_unique, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=1)

    total_bins = len(bins)
    ok_bins = total_bins - len(errors)
    total_strings = sum(len(v) for v in strings_by_bin.values())
    n_unique = len(unique)
    top = sorted(strings_by_bin.items(), key=lambda kv: len(kv[1]), reverse=True)[:20]
    nonempty = sum(1 for v in strings_by_bin.values() if v)

    stats = {
        "total_bins": total_bins,
        "ok_bins": ok_bins,
        "failed_bins": len(errors),
        "cached_json_reused": cached,
        "bins_with_strings": nonempty,
        "total_strings": total_strings,
        "raw_string_occurrences": raw_total,
        "unique_strings": n_unique,
    }
    for kb in KEY_BINS:
        stats[kb.replace(".bin", "") + "_strings"] = len(strings_by_bin.get(kb, []))

    lines = []
    lines.append("# Extract Report — db.coyote.en.par (Lost Judgment)")
    lines.append("")
    lines.append("- สร้างโดย: `scripts/extract_all_en.py` (A3-Extractor)")
    lines.append("- วันที่: %s · ใช้เวลา %.0f วินาที" % (time.strftime("%Y-%m-%d %H:%M:%S"), elapsed))
    lines.append("- แหล่ง bin: `extracted/db_en/*.bin` (base สำหรับ apply ภายหลัง)")
    lines.append("- ตัวแปลง: `tools/reARMP_fixed.py` (ARMP v2 -> JSON คู่กันเป็น `*.bin.json`)")
    lines.append("")
    lines.append("## สรุปตัวเลข")
    lines.append("")
    lines.append("| ตัวชี้วัด | ค่า |")
    lines.append("|---|---|")
    lines.append("| bin ทั้งหมด | %d |" % total_bins)
    lines.append("| แปลงสำเร็จ (มี JSON ใช้ได้) | %d |" % ok_bins)
    lines.append("| แปลงล้มเหลว | %d |" % len(errors))
    lines.append("| ใช้ JSON เดิม (cache) | %d |" % cached)
    lines.append("| bin ที่มี string แปลได้ >= 1 | %d |" % nonempty)
    lines.append("| strings รวม (unique ต่อ bin, รวมทุก bin) | %d |" % total_strings)
    lines.append("| string occurrences ดิบ (นับซ้ำ) | %d |" % raw_total)
    lines.append("| unique strings ทั้งโปรเจกต์ | %d |" % n_unique)
    lines.append("")
    lines.append("## ไฟล์สำคัญ")
    lines.append("")
    lines.append("| bin | strings (unique ใน bin) |")
    lines.append("|---|---|")
    for kb in KEY_BINS:
        mark = "" if kb in strings_by_bin else " (ไม่พบ/ล้มเหลว)"
        lines.append("| %s | %d%s |" % (kb, len(strings_by_bin.get(kb, [])), mark))
    lines.append("")
    lines.append("## Top-20 bin ตามจำนวน string")
    lines.append("")
    lines.append("| # | bin | strings |")
    lines.append("|---|---|---|")
    for i, (name, arr) in enumerate(top, 1):
        lines.append("| %d | %s | %d |" % (i, name, len(arr)))
    lines.append("")
    lines.append("## ไฟล์ที่แปลงไม่ผ่าน (%d)" % len(errors))
    lines.append("")
    if errors:
        lines.append("| bin | error |")
        lines.append("|---|---|")
        for name, err in errors.items():
            lines.append("| %s | %s |" % (name, str(err).replace("|", "\\|")))
    else:
        lines.append("ไม่มี — แปลงผ่านทุกไฟล์")
    lines.append("")
    lines.append("## เกณฑ์คัด string")
    lines.append("")
    lines.append("- เดินเฉพาะ **value** ใน JSON (key = row/column name ซึ่งเป็น identifier)")
    lines.append("- ต้องมีอักษร A-Za-z อย่างน้อย 2 ตัว (ตัดตัวเลข/hex/สัญลักษณ์ล้วน เช่น `%s`, `123`, `0xFF`)")
    lines.append("- token เดี่ยวรูป identifier/path (`[A-Za-z0-9_./\\\\:-]+` ไม่มีช่องว่าง) ที่มีตัวเลข/`_`/`.`/`/` ปน → ทิ้ง")
    lines.append("- **ข้อยกเว้น** (ตาม logic PIRATE extract_strings.py): token ตัวอักษรล้วน เช่น `Continue`, `Yes` → เก็บ; แต่ ALLCAPS ยาว >3 (`SCREAMING`) → ทิ้ง")
    lines.append("- string มีช่องว่าง/ขึ้นบรรทัด/เครื่องหมาย/tag (`%s`, `<...>`) → เก็บ (ต้องแปลรอบข้าง tag)")
    lines.append("- ภาษาไทยอยู่แล้ว → ข้าม")
    lines.append("- `unique_strings.json`: `count` = จำนวนครั้งที่พบรวมทุกไฟล์ (นับซ้ำใน bin เดียวกัน), `bins` = รายชื่อ bin ที่พบ")
    lines.append("")
    lines.append("## STATS_JSON")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(stats, ensure_ascii=False, indent=2))
    lines.append("```")
    with io.open(p_report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return stats, (p_by_bin, p_unique, p_report)


# ------------------------------------------------------------------ main ----
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bins-dir", default=os.path.join(PROJECT, "extracted", "db_en"))
    ap.add_argument("--rearmp", default=os.path.join(PROJECT, "tools", "reARMP_fixed.py"))
    ap.add_argument("--out-dir", default=os.path.join(PROJECT, "extracted"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=1500, help="วินาทีต่อไฟล์")
    ap.add_argument("--force", action="store_true", help="แปลงใหม่แม้มี .json แล้ว")
    ap.add_argument("--convert-only", action="store_true")
    ap.add_argument("--collect-only", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    if not os.path.isdir(args.bins_dir):
        print("bins dir not found: %s" % args.bins_dir)
        return 2
    if not os.path.isfile(args.rearmp):
        print("reARMP not found: %s" % args.rearmp)
        return 2

    if args.collect_only:
        bins = sorted(f for f in os.listdir(args.bins_dir) if f.lower().endswith(".bin"))
        errors, cached = OrderedDict(), 0
        for b in bins:  # ไฟล์ไม่มี json = ถือว่าแปลงไม่ผ่าน
            if not os.path.isfile(os.path.join(args.bins_dir, b) + ".json"):
                errors[b] = "no json (convert step not run)"
    else:
        bins, errors, cached = convert_all(args.bins_dir, args.rearmp,
                                           args.workers, args.timeout, args.force)
    if args.convert_only:
        print("[convert] done: %d ok / %d fail" % (len(bins) - len(errors), len(errors)))
        return 0

    print("[collect] walking JSONs ...", flush=True)
    strings_by_bin, unique, raw_total = collect_all(args.bins_dir, bins, errors)
    stats, paths = write_outputs(args.out_dir, bins, errors, cached,
                                 strings_by_bin, unique, raw_total, time.time() - t0)
    print("[done] outputs:")
    for p in paths:
        print("  " + p)
    print("STATS " + json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
