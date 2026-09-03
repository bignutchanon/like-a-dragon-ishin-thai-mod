# รีวิว batch_018 — 2 ก.ย. 2026

250 คีย์ · priority 3 · คำอธิบายทักษะและปุ่มบังคับ (`ability_control_explanation` · `ability_explanation`)

## แก้ไปกี่จุด

- **นักแปลแก้เอง 4 จุด**: "กิออง" → "กิอง" (คำล็อก) · ด่าน G ตีกลับ "คุณ" 1 บรรทัด → เขียนใหม่ไม่มีสรรพนาม
  · เลี่ยงคำต้องห้าม "แก๊ง" → "กลุ่มศัตรู"
- **lead ก่อนส่งตรวจ 14 จุด**: `Splendid Skill` "ท่าเทพ" → **"ท่าพิสดาร"** (ท่าเทพเป็นสแลงสมัยใหม่)
  · `Komaki X` "สำนักโคมากิ: X" → **"โคมากิ X"** · `Essence of Mighty Strikes` / `Shoving Shot` ตามรูปมาตรฐาน
- **ผู้ตรวจ 68 จุด** — ก้อนที่ถูกแก้หนักที่สุดของทั้งสองคลื่น
  - **21 จุด**: ปรับรูปประโยคมาตรฐานให้ตรงกับ batch_019 (เลือกรูปของ 019 เพราะสั้นกว่า
    โครงประโยค 66 → 52 ตัวอักษร): **"เปิดท่าไม้ตายของ X ได้ กด\<symbol\>เพิ่มเติมเพื่อเพิ่มความเสียหาย"**
  - **47 จุด**: ชื่อท่าที่ตั้งชนกับ 019 — Essence 6 ชื่อ · Heavy Sword · **Swordplay ("ท่าดาบ:" → "ดาบร่าย:")**
    · Mirage of Shimmering Heat · Rain/Squall/Typhoon of Steel and Fire · Dance of Mourning ·
    Luxury and Splendor · Asura Spirit · War Cry Counter · Bellowing Fusillade · Remnant Silhouette ·
    Twister Tussle · Majestic Dispersal · **Texas Two-Step ("ท่ายิงสองจังหวะ" → "ระบำสองจังหวะ")**
    · **Finishing Blow ("ท่าจบ" → "ท่าจบคอมโบ")** 7 จุด

## ที่ตรวจแล้วยืนยัน

- นักแปลไม่ใช้ `ref_tm` ที่ขัดกับ `name_locks.json` (tm ให้ "ไซโก"/"อิโต้"/"คนโดะ")
- tag/placeholder/`\n` ครบ 100% ทั้งไฟล์ · ลำดับคีย์ตรง worklist

## ค้างไว้

`Majestic Dispersal` — JA คือ 群衆散らし (สลาย**หมู่**) รูปเดิมของ 018 ("สลายหมู่สง่างาม") ใกล้ JA กว่า
แต่ผู้ตรวจแก้ให้ตรงกับรูปยืนเดี่ยวของ 019 ("สลายศัตรูอย่างสง่างาม") ตามกติกา
— ความหมายคลาดจาก JA เล็กน้อย จดไว้เผื่อทบทวน

## ผลด่านอัตโนมัติ

merge_qc ผ่าน 250 ตก 0 · glossary_locks เหลือแต่ตัวเตือน · term_consistency 0/0
