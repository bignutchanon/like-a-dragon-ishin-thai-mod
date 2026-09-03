#!/usr/bin/env python3
"""Round-trip structure checker สำหรับ build/text/*.bin

เอา bin ที่ build แล้ว decode กลับเป็น JSON ด้วย tools/reARMP_fixed.py แล้ว diff
โครงสร้าง (ไม่ใช่ค่า string) กับต้นฉบับ extracted/db_en/<bin>.json

กติกา diff (recursive):
  - dict key หาย/เกินไปจากต้นฉบับ           -> MISSING
  - list ยาวไม่เท่ากัน                        -> LEN (ไม่ไล่ element ต่อ เพราะ index ไม่ align กันแล้ว)
  - ค่าไม่เท่ากัน และไม่ใช่ทั้งคู่เป็น str      -> VAL
  - str <-> str                              -> ข้าม (ไทยถูก map เป็น donor codepoint ปกติ)
    ยกเว้น: ถ้าต้นฉบับมี placeholder ${...} / <...> / เครื่องหมายขึ้นบรรทัดใหม่ (\n จริง)
    และฝั่ง build มีจำนวนไม่เท่ากัน           -> TAG

ใช้:
  python scripts/check_bin_roundtrip.py                 # รันทั้ง 230 bin
  python scripts/check_bin_roundtrip.py --only a.bin b.bin
  python scripts/check_bin_roundtrip.py --selftest       # ต้องรันผ่านก่อนใช้จริงเสมอ
"""
import sys, os, io, json, re, shutil, argparse, subprocess, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as P

PROJECT = P.PROJECT
BUILD_TEXT = P.BUILD / "text" / "db.coyote.en"   # LJ: bin ที่บิลด์อยู่ในโฟลเดอร์ย่อยตามชื่อ par
DB_EN = P.DB_EN
REARMP = P.REARMP
SCRATCH = PROJECT / "build" / "roundtrip"
RT_DIR = SCRATCH / "rt"
REPORT_JSON = SCRATCH / "roundtrip_report.json"
REPORT_MD = SCRATCH / "roundtrip_report.md"

TIMEOUT_SEC = 120
MAX_WORKERS = 6
MAX_EXAMPLES = 5

TAG_RE = re.compile(r"\$\{[^}]*\}|<[^<>]*>|\n")


# --------------------------------------------------------------------------
# recursive diff
# --------------------------------------------------------------------------
def _tag_count(s):
    return len(TAG_RE.findall(s))


def diff_value(orig, new, path, out):
    """เติม diff ลง out (list of dict: path, type, detail) — recursive"""
    if isinstance(orig, dict) and isinstance(new, dict):
        orig_keys = set(orig.keys())
        new_keys = set(new.keys())
        for k in sorted(orig_keys - new_keys, key=str):
            out.append({"path": f"{path}/{k}", "type": "MISSING",
                        "detail": "key missing in build"})
        for k in sorted(new_keys - orig_keys, key=str):
            out.append({"path": f"{path}/{k}", "type": "MISSING",
                        "detail": "extra key in build"})
        for k in orig_keys & new_keys:
            diff_value(orig[k], new[k], f"{path}/{k}", out)

    elif isinstance(orig, list) and isinstance(new, list):
        if len(orig) != len(new):
            out.append({"path": path, "type": "LEN",
                        "detail": f"{len(orig)} -> {len(new)}"})
            # index ไม่ align กันแล้ว ไม่ไล่ element ต่อ
        else:
            for i in range(len(orig)):
                diff_value(orig[i], new[i], f"{path}[{i}]", out)

    elif isinstance(orig, str) and isinstance(new, str):
        oc = _tag_count(orig)
        if oc:
            nc = _tag_count(new)
            if oc != nc:
                out.append({"path": path, "type": "TAG",
                            "detail": f"tag count {oc} -> {nc}"})
        # str<->str อื่น ๆ = mojibake ปกติ ข้าม

    else:
        if orig != new:
            out.append({"path": path, "type": "VAL",
                        "detail": f"{orig!r} -> {new!r}"})


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def run_selftest():
    ok = True

    # เคส 1: LEN — list ยาวไม่เท่ากัน (จำลอง SPECIAL_FIELD_INDICES เติม 0 ท้าย)
    orig1 = {"SPECIAL_FIELD_INDICES": [0, 0]}
    new1 = {"SPECIAL_FIELD_INDICES": [0, 0, 0, 0]}
    d1 = []
    diff_value(orig1, new1, "", d1)
    pass1 = any(x["type"] == "LEN" for x in d1)
    print(f"[selftest] LEN case: {'PASS' if pass1 else 'FAIL'}  diffs={d1}")
    ok &= pass1

    # เคส 2: VAL — ค่า int ไม่ตรงกัน (ไม่ใช่ str)
    orig2 = {"ROW_COUNT": 10, "nested": {"flag": True}}
    new2 = {"ROW_COUNT": 11, "nested": {"flag": False}}
    d2 = []
    diff_value(orig2, new2, "", d2)
    types2 = [x["type"] for x in d2]
    pass2 = types2.count("VAL") == 2
    print(f"[selftest] VAL case: {'PASS' if pass2 else 'FAIL'}  diffs={d2}")
    ok &= pass2

    # เคส 3: MISSING — key หายไปในฝั่ง build + key เกิน
    orig3 = {"a": 1, "b": 2, "c": {"x": 1}}
    new3 = {"a": 1, "c": {}, "d": 9}
    d3 = []
    diff_value(orig3, new3, "", d3)
    paths3 = {(x["path"], x["type"]) for x in d3}
    pass3 = (("/b", "MISSING") in paths3 and ("/d", "MISSING") in paths3
             and ("/c/x", "MISSING") in paths3)
    print(f"[selftest] MISSING case: {'PASS' if pass3 else 'FAIL'}  diffs={d3}")
    ok &= pass3

    # เคส 4: str -> str ต้องไม่ถูกจับ (mojibake ปกติ) ยกเว้น tag count ไม่ตรง
    orig4 = {"txt": "Hello world", "tag": "Hi ${name}, press <symbol=button_x>\nGo"}
    new4 = {"txt": " mojibake garbage", "tag": " ${name} <symbol=button_x>\nOK"}
    d4 = []
    diff_value(orig4, new4, "", d4)
    pass4a = not any(x["path"] == "/txt" for x in d4)          # plain str->str ข้าม
    pass4b = not any(x["path"] == "/tag" for x in d4)          # tag count เท่ากัน (2 tags + 1 \n ทั้งคู่) -> ข้าม
    print(f"[selftest] str->str skip case: {'PASS' if (pass4a and pass4b) else 'FAIL'}  diffs={d4}")
    ok &= pass4a and pass4b

    # เคส 5: TAG — placeholder หายระหว่าง encode
    orig5 = {"tag": "Hi ${name}, press <symbol=button_x>\nGo"}
    new5 = {"tag": " mojibake ${name}\nGo"}   # หาย <symbol=button_x>
    d5 = []
    diff_value(orig5, new5, "", d5)
    pass5 = any(x["type"] == "TAG" and x["path"] == "/tag" for x in d5)
    print(f"[selftest] TAG case: {'PASS' if pass5 else 'FAIL'}  diffs={d5}")
    ok &= pass5

    print(f"\n[selftest] {'ALL PASS' if ok else 'FAILED'}")
    return ok


# --------------------------------------------------------------------------
# round-trip 1 bin: copy -> reARMP decode -> load -> diff
# --------------------------------------------------------------------------
def process_bin(bin_path: Path):
    name = bin_path.name
    dest = RT_DIR / name
    result = {"name": name, "status": "ok", "n_diff": 0,
              "types": {}, "examples": []}
    try:
        shutil.copy2(bin_path, dest)
    except Exception as e:
        result["status"] = "copy_fail"
        result["error"] = str(e)
        return result

    dest_arg = str(dest.resolve()).replace("\\", "/")
    rearmp_arg = str(REARMP.resolve()).replace("\\", "/")
    try:
        proc = subprocess.run(
            [sys.executable, rearmp_arg, dest_arg],
            cwd=str(PROJECT), timeout=TIMEOUT_SEC,
            capture_output=True, text=True,
        )
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        return result
    except Exception as e:
        result["status"] = "decode_fail"
        result["error"] = str(e)
        return result

    dest_json = Path(str(dest) + ".json")
    if proc.returncode != 0 or not dest_json.exists():
        result["status"] = "decode_fail"
        result["error"] = (proc.stderr or proc.stdout or "")[-800:]
        return result

    orig_json = DB_EN / (name + ".json")
    if not orig_json.exists():
        result["status"] = "orig_missing"
        return result

    try:
        with io.open(dest_json, encoding="utf-8") as f:
            new_data = json.load(f)
        with io.open(orig_json, encoding="utf-8") as f:
            orig_data = json.load(f)
    except Exception as e:
        result["status"] = "json_load_fail"
        result["error"] = str(e)
        return result

    diffs = []
    diff_value(orig_data, new_data, "", diffs)

    types = {}
    for d in diffs:
        types[d["type"]] = types.get(d["type"], 0) + 1

    result["n_diff"] = len(diffs)
    result["types"] = types
    result["examples"] = diffs[:MAX_EXAMPLES]
    return result


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--only", nargs="+", default=None,
                    help="รันเฉพาะบาง bin (ชื่อไฟล์ พร้อมหรือไม่พร้อม .bin ก็ได้)")
    args = ap.parse_args()

    if args.selftest:
        ok = run_selftest()
        sys.exit(0 if ok else 1)

    RT_DIR.mkdir(parents=True, exist_ok=True)

    all_bins = sorted(BUILD_TEXT.glob("*.bin"))
    if args.only:
        want = {n if n.endswith(".bin") else n + ".bin" for n in args.only}
        all_bins = [b for b in all_bins if b.name in want]

    print(f"[check_bin_roundtrip] target bins: {len(all_bins)}  workers={MAX_WORKERS}  timeout={TIMEOUT_SEC}s")

    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(process_bin, b): b for b in all_bins}
        done_n = 0
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            done_n += 1
            if done_n % 40 == 0:
                print(f"  ... {done_n}/{len(all_bins)}")

    elapsed = time.time() - t0

    results.sort(key=lambda r: r["name"])
    n_total = len(results)
    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_diff_bins = sum(1 for r in results if r["status"] == "ok" and r["n_diff"] > 0)
    n_clean_bins = sum(1 for r in results if r["status"] == "ok" and r["n_diff"] == 0)
    fail_statuses = ["timeout", "decode_fail", "copy_fail", "orig_missing", "json_load_fail"]
    fails = {s: [r["name"] for r in results if r["status"] == s] for s in fail_statuses}
    n_fail = sum(len(v) for v in fails.values())

    type_totals = {}
    for r in results:
        for t, c in r.get("types", {}).items():
            type_totals[t] = type_totals.get(t, 0) + c

    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(elapsed, 1),
        "n_total_bins": n_total,
        "n_ok": n_ok,
        "n_clean_bins": n_clean_bins,
        "n_diff_bins": n_diff_bins,
        "n_decode_fail_total": n_fail,
        "fail_by_status": {k: len(v) for k, v in fails.items()},
        "fail_bin_names": fails,
        "type_totals": type_totals,
        "bins": results,
    }
    with io.open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # ---- markdown report ----
    diff_bins = sorted(
        (r for r in results if r["status"] == "ok" and r["n_diff"] > 0),
        key=lambda r: r["n_diff"], reverse=True,
    )
    lines = []
    lines.append("# Round-trip structure report — build/text/*.bin vs extracted/db_en\n")
    lines.append(f"generated: {report['generated_at']}  |  elapsed: {report['elapsed_sec']}s\n")
    lines.append("## สรุปรวม\n")
    lines.append(f"- bin ทั้งหมด: {n_total}")
    lines.append(f"- decode สำเร็จ: {n_ok}")
    lines.append(f"- decode ไม่ได้ / timeout รวม: {n_fail}")
    for s, names in fails.items():
        if names:
            lines.append(f"  - {s}: {len(names)} ({', '.join(names[:10])}{' ...' if len(names) > 10 else ''})")
    lines.append(f"- bin ที่โครงสร้างตรง (n_diff=0): {n_clean_bins}")
    lines.append(f"- bin ที่โครงสร้างเพี้ยน (n_diff>0): {n_diff_bins}")
    lines.append(f"- diff รวมตามชนิด: {type_totals}\n")

    lines.append("## bin ที่มี diff (เรียง n_diff มาก -> น้อย)\n")
    lines.append("| bin | n_diff | types | ตัวอย่าง diff (path : type : detail) |")
    lines.append("|---|---:|---|---|")
    for r in diff_bins:
        ex = "; ".join(f"`{e['path']}`:{e['type']}:{e['detail']}" for e in r["examples"])
        lines.append(f"| {r['name']} | {r['n_diff']} | {r['types']} | {ex} |")

    with io.open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[check_bin_roundtrip] done in {elapsed:.1f}s")
    print(f"  total={n_total} ok={n_ok} fail={n_fail} clean={n_clean_bins} diff_bins={n_diff_bins}")
    print(f"  type_totals={type_totals}")
    print(f"  report: {REPORT_JSON}")
    print(f"  report: {REPORT_MD}")


if __name__ == "__main__":
    main()
