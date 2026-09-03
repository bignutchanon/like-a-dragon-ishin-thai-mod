#!/usr/bin/env python3
"""POC: แปล "label" ในตาราง .msg (ชื่อผู้พูด/ป้ายปุ่มโต้ตอบ) เฉพาะไฟล์ทดสอบ แล้ววางลง build/stage_pak/

ทำไมต้องมี: "Young Woman" (ชื่อผู้พูดฉากเปิด) และ "Pray" (ปุ่มไหว้ศาลเจ้า) ไม่ได้อยู่ในบรรทัดบทพูด
แต่อยู่ใน **ตาราง label** ของ .msg ซึ่ง pipeline ไม่เคยแตะ (ยืนยัน 3 ก.ย. 2026)
ยังไม่รู้ว่าเกมใช้ label เป็นแค่ข้อความบนจอ หรือใช้เป็นคีย์ค้นหาด้วย → ต้องทดสอบในเกมก่อนขยายผล

คำแปลในนี้เป็นของชั่วคราวสำหรับทดสอบเท่านั้น ไม่ใช่คำแปลจริง (คำแปลจริงต้องผ่าน merge_qc.py)
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paths                                        # noqa: E402
import msg as msgmod                                # noqa: E402
from build_text import msg_game_paths, load_master  # noqa: E402

POC_LABELS = {
    "Young Woman": "หญิงสาว",
    # "Pray" ถอดออกแล้ว (3 ก.ย. 2026 ค่ำ): ป้ายปุ่มไหว้ศาลเจ้าบนจอมาจาก wdr_en/pac/pac_STID_ST_*.bin
    # (สตริงฝังในไฟล์วางวัตถุประจำฉาก · JA เป็น 参拝) ไม่ใช่ label ใน .msg — แปล label แล้วจอไม่เปลี่ยน
}
STAGE_PAK = paths.BUILD / "stage_pak"


def main():
    th_map = load_master()
    game_paths = msg_game_paths()
    done = 0
    for js in sorted(paths.TEXT_EN.glob("*.json")):
        uid = js.stem
        src = paths.MSG_EN / (uid + ".msg")
        if not src.exists():
            continue
        # ⚠ ต้องดูจากตาราง label ของไฟล์จริง — records["labels"] มีแค่ label ที่คำสั่ง 0x03 อ้างถึง
        #   "Young Woman" (ชื่อผู้พูด) ไม่มีคำสั่งไหนอ้าง เลยไม่โผล่ใน records
        m = msgmod.load(src)
        hit = {L for L in m.labels if L in POC_LABELS}
        if not hit:
            continue
        gp = game_paths.get(uid)
        if gp is None:
            print("!! ข้าม %s (ไม่รู้ path ในเกม)" % uid)
            continue
        records = json.loads(js.read_text(encoding="utf-8"))
        repl = {r["line"]: th_map[r["en"]] for r in records if r["en"] in th_map}
        data = m.rebuild(repl, {k: v for k, v in POC_LABELS.items() if k in hit})
        back = msgmod.MsgFile(data, uid)
        got = {L for L in back.labels if L in POC_LABELS.values()}
        assert got == {POC_LABELS[k] for k in hit}, (uid, got)
        assert [ln.text for ln in back.lines] == [repl.get(i, ln.text) for i, ln in enumerate(m.lines)], uid
        out = STAGE_PAK / gp
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        done += 1
        print("%s  labels %s  บรรทัดแปล %d/%d" % (uid, sorted(hit), len(repl), len(m.lines)))
    print("POC label: เขียน %d ไฟล์ลง %s" % (done, STAGE_PAK))


if __name__ == "__main__":
    main()
