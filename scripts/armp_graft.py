"""armp_graft.py — คืนไบต์ของคอลัมน์ชนิดที่ reARMP ไม่รู้จัก กลับเข้าไฟล์ที่ประกอบใหม่

ที่มา: Ishin! มีชนิดคอลัมน์ที่ reARMP (เขียนไว้สำหรับ Judgment/LAD) ไม่รู้จัก — ที่พบคือ
**ชนิด 30 (บล็อกธง 32 ไบต์) และ 31 (4 ไบต์)** ตัวอ่านข้ามคอลัมน์พวกนี้ไปเฉย ๆ
ตอนประกอบกลับจึงเขียนเป็นศูนย์ทั้งก้อน → 11 ตารางประกอบกลับไม่ได้ รวม `tips` ที่มีข้อความให้แปล 172 ช่อง

วิธีแก้: เราไม่เคยแก้คอลัมน์พวกนี้เลย (แก้แต่คอลัมน์สตริงชนิด 13) จึง **ก๊อปไบต์ของมัน
จากไฟล์ vanilla กลับเข้าแถวเดียวกันที่ตำแหน่งเดิม** หลัง reARMP ประกอบเสร็จ
เงื่อนไขที่ต้องจริงก่อนจะก๊อป: จำนวนแถว/คอลัมน์/โหมดเก็บ/ตาราง aux ต้องตรงกันทุกไบต์
(ถ้าไม่ตรง แปลว่าโครงเปลี่ยน — ห้ามก๊อป ให้รายงานแทน)

ใช้: python scripts/armp_graft.py <vanilla.bin> <built.bin> [<out.bin>]
import: graft(vanilla_path, built_bytes) -> (bytes, notes)
"""
import struct
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ชนิดคอลัมน์ที่ reARMP อ่าน/เขียนได้จริง (ตรงกับ exportTable/importTable version 2)
KNOWN = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13]) | set(range(14, 30))


def _hdr(b, main):
    f = lambda o: struct.unpack_from("<i", b, main + o)[0]      # noqa: E731
    return dict(rows=f(0), cols=f(4), p_types=f(0x18), p_content=f(0x1C),
                storage=b[main + 0x23], p_aux=f(0x48))


def _rows(b, h):
    return [struct.unpack_from("<i", b, h["p_content"] + 4 * i)[0] for i in range(h["rows"])]


def graft(vanilla_path, built):
    """คืน (ไบต์ที่ปะแล้ว, บันทึกสิ่งที่ทำ) — ถ้าปะไม่ได้จะคืนไบต์เดิมพร้อมเหตุผล"""
    A = Path(vanilla_path).read_bytes()
    B = bytearray(built)
    notes = []
    mv = struct.unpack_from("<i", A, 0x10)[0]
    mb = struct.unpack_from("<i", B, 0x10)[0]
    ha, hb = _hdr(A, mv), _hdr(B, mb)
    if (ha["rows"], ha["cols"], ha["storage"]) != (hb["rows"], hb["cols"], hb["storage"]):
        return bytes(B), ["โครงตารางต่างกัน (rows/cols/storage) — ไม่ปะ"]
    if ha["storage"] != 1 or ha["rows"] == 0 or ha["cols"] == 0:
        return bytes(B), []
    aux_a = A[ha["p_aux"]: ha["p_aux"] + 16 * ha["cols"]]
    aux_b = B[hb["p_aux"]: hb["p_aux"] + 16 * hb["cols"]]
    if aux_a != aux_b:
        return bytes(B), ["ตาราง aux ต่างกัน — ไม่ปะ (โครงแถวเปลี่ยน)"]

    types = [struct.unpack_from("<b", A, ha["p_types"] + ci)[0] for ci in range(ha["cols"])]
    shifts = [struct.unpack_from("<i", aux_a, 16 * ci + 4)[0] for ci in range(ha["cols"])]
    ra, rb = _rows(A, ha), _rows(B, hb)
    deltas = [ra[i + 1] - ra[i] for i in range(len(ra) - 1) if ra[i + 1] - ra[i] > 0]
    stride = max(set(deltas), key=deltas.count) if deltas else 0
    if not stride:
        return bytes(B), ["หา stride ของแถวไม่ได้ — ไม่ปะ"]

    # ขนาดของคอลัมน์ = ระยะถึง shift ตัวถัดไป (คอลัมน์สุดท้าย = ถึงท้ายแถว)
    order = sorted([(sh, ci) for ci, sh in enumerate(shifts) if sh >= 0])
    size = {}
    for i, (sh, ci) in enumerate(order):
        end = order[i + 1][0] if i + 1 < len(order) else stride
        size[ci] = max(0, end - sh)

    unknown = [ci for ci in range(ha["cols"]) if types[ci] not in KNOWN and shifts[ci] >= 0]
    if not unknown:
        return bytes(B), []

    patched = 0
    for r in range(ha["rows"]):
        for ci in unknown:
            sh, sz = shifts[ci], size.get(ci, 0)
            if sz <= 0:
                continue
            src = A[ra[r] + sh: ra[r] + sh + sz]
            dst0 = rb[r] + sh
            if len(src) != sz or dst0 + sz > len(B):
                continue
            if B[dst0: dst0 + sz] != src:
                B[dst0: dst0 + sz] = src
                patched += 1
    notes.append("ปะคอลัมน์ชนิดที่ไม่รู้จัก %s · %d ช่อง"
                 % (", ".join("col%d(type %d)" % (ci, types[ci]) for ci in unknown), patched))
    return bytes(B), notes


def main():
    van, built = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else built
    data, notes = graft(van, Path(built).read_bytes())
    Path(out).write_bytes(data)
    for n in notes:
        print(n)
    if not notes:
        print("ไม่มีคอลัมน์ชนิดที่ไม่รู้จัก — ไม่ต้องปะ")


if __name__ == "__main__":
    main()
