"""armp_layout_check.py — ตรวจว่า bin ที่ rebuild มี layout แถว (storage mode 1) ตรง vanilla:
aux table (type/shift/special/extra ต่อคอลัมน์) ต้องเท่ากันทุกไบต์ + เนื้อหาทุกแถวเท่ากันทุกไบต์ ยกเว้นช่อง string (type 13, 8 B) และช่อง table pointer (type 9)
ใช้: python scripts/armp_layout_check.py <vanilla.bin> <built.bin>   → พิมพ์สรุป, exit 1 ถ้าต่าง
import ได้: layout_mismatch(vanilla, built) → list ข้อความปัญหา ([] = ผ่าน)"""
import sys, struct, pathlib
sys.stdout.reconfigure(encoding="utf-8")

def _hdr(b, main):
    f = lambda o: struct.unpack_from('<i', b, main + o)[0]
    return dict(rows=f(0), cols=f(4), texts=f(8), p_types=f(0x18), p_content=f(0x1C), storage=b[main+0x23], p_aux=f(0x48), p_sub=f(0x3C))

def _row_offsets(b, h):
    return [struct.unpack_from('<i', b, h['p_content'] + 4*i)[0] for i in range(h['rows'])]

def layout_mismatch(vanilla, built, _main_v=None, _main_b=None, extra_skip=()):
    # extra_skip = ช่วง (shift, size) ที่เรา **ตั้งใจแก้** จึงต้องข้ามตอนเทียบไบต์
    #   เช่น font2_style.font_face_en (LJ-002 ย้าย 126 สไตล์ไปฟอนต์ SDF)
    #   ผู้เรียกคำนวณ shift/size จาก COLUMN_LAYOUT ของ JSON ต้นฉบับแล้วส่งเข้ามา
    A = pathlib.Path(vanilla).read_bytes(); B = pathlib.Path(built).read_bytes()
    mv = struct.unpack_from('<i', A, 0x10)[0] if _main_v is None else _main_v
    mb = struct.unpack_from('<i', B, 0x10)[0] if _main_b is None else _main_b
    ha, hb = _hdr(A, mv), _hdr(B, mb)
    out = []
    if (ha['rows'], ha['cols'], ha['storage']) != (hb['rows'], hb['cols'], hb['storage']):
        return [f"header rows/cols/storage ต่าง {ha} vs {hb}"]
    if ha['storage'] != 1 or ha['cols'] == 0 or ha['rows'] == 0:
        return out
    aux_a = A[ha['p_aux']: ha['p_aux'] + 16*ha['cols']]; aux_b = B[hb['p_aux']: hb['p_aux'] + 16*hb['cols']]
    if aux_a != aux_b:
        for ci in range(ha['cols']):
            xa = struct.unpack_from('<iiii', aux_a, 16*ci); xb = struct.unpack_from('<iiii', aux_b, 16*ci)
            if xa != xb: out.append(f"aux col{ci}: vanilla {xa} built {xb}")
        return out
    types = [struct.unpack_from('<b', A, ha['p_types'] + ci)[0] for ci in range(ha['cols'])]
    layout = [struct.unpack_from('<iiii', aux_a, 16*ci) for ci in range(ha['cols'])]
    ra, rb = _row_offsets(A, ha), _row_offsets(B, hb)
    da = [ra[i+1]-ra[i] for i in range(len(ra)-1) if ra[i+1]-ra[i] > 0]
    stride = max(set(da), key=da.count) if da else max((l[1] + (16 if l[0]==27 else 8) for l in layout if l[1] >= 0), default=16)
    skip = []
    for ci, t in enumerate(types):
        sh = layout[ci][1]
        if sh >= 0 and t in (13, 9): skip.append((sh, sh+8))
    skip += [(sh, sh + sz) for sh, sz in extra_skip]
    AUX_SIZE = {1: 8, 2: 4, 3: 2, 4: 1, 5: 8, 6: 4, 7: 2, 8: 1, 9: 8, 10: 4, 12: 8, 13: 8, 27: 16}  # aux type id → ไบต์
    used_end = max((l[1] + AUX_SIZE.get(l[0], 0) for l in layout if l[1] >= 0), default=stride)
    used_end = min(used_end, stride)
    for r in range(ha['rows']):
        n = stride if r < ha['rows'] - 1 else used_end  # แถวสุดท้าย: หลัง column สุดท้ายอาจเป็น section อื่นใน vanilla
        rowa = bytearray(A[ra[r]: ra[r]+n]); rowb = bytearray(B[rb[r]: rb[r]+n])
        for s0, s1 in skip:
            rowa[s0:s1] = b'\0'*(s1-s0); rowb[s0:s1] = b'\0'*(s1-s0)
        if rowa != rowb:
            i = next(i for i in range(min(len(rowa),len(rowb))) if rowa[i] != rowb[i])
            out.append(f"row {r} byte@{i} ต่าง (stride {stride})")
            if len(out) > 5: break
    return out

if __name__ == '__main__':
    d = layout_mismatch(sys.argv[1], sys.argv[2])
    print("PASS" if not d else "FAIL"); [print(" ", x) for x in d]
    sys.exit(1 if d else 0)
