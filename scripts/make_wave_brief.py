"""สร้างบรีฟรายก้อนของคลื่นหนึ่ง ๆ

เขียนคำล็อก/คำที่เคาะแล้วลงบรีฟตรง ๆ โดย **copy จากไฟล์** (name_locks.json ·
place_locks.json · batch_NNN.prior.json) ไม่ให้ lead พิมพ์จากความจำ — cheatsheet §4.6

ใช้: python scripts/make_wave_brief.py MSG_043 MSG_044 ...
ผลลัพธ์: work/brief/batch_<ก้อน>.brief.md
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WORKLIST = ROOT / "translations" / "worklist"
OUTDIR = ROOT / "work" / "brief"
# ประกาศที่ต้องแปะลงบรีฟทุกก้อนของคลื่น (คำตัดสินใหม่ · คำที่เพิ่งกวาดทั้งคลัง)
# เขียนที่ไฟล์เดียว แล้วสคริปต์ copy ลงทุกก้อน — lead ไม่ต้องพิมพ์ซ้ำหกรอบ
ANNOUNCE = OUTDIR / "ANNOUNCE.md"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def overlap_lines(batches):
    """เรียก batch_overlap.py ครั้งเดียว แล้วแยกบรรทัดตามก้อน"""
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "batch_overlap.py"), *batches],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
    ).stdout
    result = {}
    for line in out.splitlines():
        head = line.split(None, 1)
        if len(head) == 2 and head[0] in batches:
            result[head[0]] = head[1].strip()
    return result


def table(pairs):
    rows = ["| EN | ไทย |", "|---|---|"]
    for en, th in pairs:
        rows.append(f"| {en} | {th} |")
    return "\n".join(rows)


def main(batches):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    overlaps = overlap_lines(batches)
    wave = set(batches)
    announce = ANNOUNCE.read_text(encoding="utf-8").strip() if ANNOUNCE.exists() else ""
    if not announce:
        print(f"[เตือน] ไม่มี {ANNOUNCE.relative_to(ROOT)} — บรีฟจะไม่มีหัวข้อประกาศคลื่นนี้")

    for b in batches:
        todo = load(WORKLIST / f"batch_{b}.todo.json")
        prior = load(WORKLIST / f"batch_{b}.prior.json")
        ov = overlaps.get(b, "")
        # ก้อนในคลื่นเดียวกันที่ใช้ไฟล์ฉากร่วมกัน — เลขน้อยกว่าเป็นเจ้าของรูป
        same_wave = sorted(x for x in wave if x != b and x in ov)

        parts = [
            f"# บรีฟก้อน batch_{b} — คลื่น {batches[0]}–{batches[-1]}",
            "",
            f"สตริง **{len(todo['strings'])}** · priority **{todo['priority']}** "
            f"· ไฟล์ฉาก {len(todo['sources'])} ไฟล์",
            "",
            "## 0. อ่านก่อน",
            "`docs/reference/BATCH_CHEATSHEET_ishin.md` ทั้งไฟล์ (กติกาครบ) "
            "· ฉบับเต็ม `TRANSLATOR_BRIEF_ishin.md` เปิดเมื่อต้องค้นจริง",
            "",
            announce,
            "",
            "## 1. ไฟล์ของก้อนนี้",
            "",
            "| ไฟล์ | ใช้ทำอะไร |",
            "|---|---|",
            f"| `translations/worklist/batch_{b}.todo.json` | **สตริงที่ต้องแปล** (`strings`) "
            "+ `ref_ja` + `ref_tm` |",
            f"| `translations/worklist/batch_{b}.context.json` | ผู้พูด · เพศ · `neutral` "
            "· `evidence_gender` · บท (query ด้วย python เท่านั้น ห้าม cat) |",
            f"| `translations/worklist/batch_{b}.prior.json` | คำที่ก้อนก่อนเคาะแล้วและโผล่ในก้อนนี้ |",
            f"| `translations/done/batch_{b}.done.json` | **ที่เขียนผลงาน** |",
            "",
            "## 2. คำล็อกของก้อนนี้ — สะกดตามนี้เป๊ะ",
            "",
            f"### 2.1 ชื่อคน/สถานที่ (`locked_names_places` · {len(prior['locked_names_places'])} รายการ)",
            "",
            table(prior["locked_names_places"].items()),
            "",
            f"### 2.2 ชื่อเฉพาะที่ขุดจาก master (`names_from_master` · "
            f"{len(prior.get('names_from_master') or {})} รายการ)",
            "",
            "⚠ ชื่อที่ **เคยเคาะรูปไทยไว้แล้ว** แต่ไม่เคยเป็นคีย์สั้นใน master จึงไม่เข้า lexicon "
            "— ใช้รูปนี้ ห้ามตั้งใหม่",
            "",
            table((prior.get("names_from_master") or {}).items())
            if prior.get("names_from_master") else "(ไม่มี)",
            "",
            f"### 2.3 ชื่อเฉพาะ/วลีที่เคาะแล้ว (`terms` · {len(prior['terms'])} รายการ)",
            "",
            table(prior["terms"].items()) if prior["terms"] else "(ไม่มี)",
            "",
            f"### 2.4 คำเดี่ยวจากบริบทอื่น (`single_words` · {len(prior['single_words'])} รายการ)",
            "",
            "⚠ เป็นคำแปลของ**บริบทอื่น** ใช้เมื่อบริบทตรงกันเท่านั้น",
            "",
            table(prior["single_words"].items()) if prior["single_words"] else "(ไม่มี)",
            "",
            "## 3. ฉากที่ใช้ร่วมกับก้อนอื่น",
            "",
            f"`{ov}`" if ov else "(ไม่มี)",
            "",
            "- ก้อนที่ทำเสร็จแล้ว (✓) → **ค้น `translations/master_th.json` ก่อนตั้งรูปใหม่ทุกครั้ง**",
        ]
        if same_wave:
            owner = min(same_wave + [b])
            parts.append(
                f"- ก้อนในคลื่นเดียวกัน: **{' · '.join(same_wave)}** — "
                f"เจ้าของรูปคือก้อนเลขน้อยกว่า = **{owner}** "
                + ("(ก้อนนี้เป็นเจ้าของ)" if owner == b else f"(ก้อนนี้ตามรูปของ {owner})")
            )
        parts += [
            "",
            "## 4. ด่านที่ต้องรันให้สะอาดก่อนรายงาน",
            "",
            "```",
            f"python scripts/merge_qc.py --dry-run --only {b}      # ต้อง \"ตก 0\"",
            f"python scripts/check_glossary_locks.py --only {b}    # ตัวเตือน — อธิบายทุกจุดที่เหลือ",
            "```",
            "",
            "⚠ **ห้ามดัดคำแปลเพื่อหลบตัวตรวจ** — ถ้ามั่นใจว่าคำแปลถูกให้รายงาน lead "
            "พร้อมบรรทัดตัวอย่าง (cheatsheet §7.5)",
            "",
        ]
        path = OUTDIR / f"batch_{b}.brief.md"
        path.write_text("\n".join(parts), encoding="utf-8")
        print(f"{b}: ล็อก {len(prior['locked_names_places'])} · terms {len(prior['terms'])}"
              f" · single {len(prior['single_words'])} -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("ใช้: python scripts/make_wave_brief.py MSG_043 MSG_044 ...")
    main(sys.argv[1:])
