# batch_055 — รีวิว (lead · ไม่ผ่านนักแปล)

ก้อนนี้ **ไม่ได้ส่งให้นักแปล** เพราะทุกคีย์เป็นสตริงชนิดข้อมูล ไม่ใช่ข้อความบนจอ
(`scripts/mark_dnt.py` จัด DNT ได้ 116/116 คีย์)

ต้นทาง: armp:tutorial.finish_flag, armp:tutorial.start_condition[0], armp:tutorial.start_condition[1], armp:tutorial.success_flag

คอลัมน์ที่พบ: path ของรูป/โมเดล · id ของอาวุธและไอเทม · ธงเนื้อเรื่อง (`TUTORIAL_*_開始/完了`)
ถ้าแปลของพวกนี้เกมจะหารูป/ธงไม่เจอ → เขียนไฟล์ done โดย **copy คีย์เป็นค่าเดิมทุกตัว**

ด่านตรวจ: `merge_qc.py --only 055` ผ่านทุกคีย์ ตก 0 · merge เข้า master แล้ว
