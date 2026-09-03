# batch_049 — รีวิว (lead · ไม่ผ่านนักแปล)

ก้อนนี้ **ไม่ได้ส่งให้นักแปล** เพราะทุกคีย์เป็นสตริงชนิดข้อมูล ไม่ใช่ข้อความบนจอ
(`scripts/mark_dnt.py` จัด DNT ได้ 250/250 คีย์)

ต้นทาง: armp:blacksmith_weapon_parameter.detail_path, armp:blacksmith_weapon_parameter.down_id, armp:blacksmith_weapon_parameter.icon_path, armp:blacksmith_weapon_parameter.left_id, armp:blacksmith_weapon_parameter.right_id, armp:blacksmith_weapon_parameter.silhouette_path, armp:blacksmith_weapon_parameter.up_id, armp:minigame_kakashi_base_setting.reward_item, armp:ultimate_settings.item_armor, armp:ultimate_settings.item_hachimaki, armp:ultimate_settings.item_id_left, armp:ultimate_settings.item_kote

คอลัมน์ที่พบ: path ของรูป/โมเดล · id ของอาวุธและไอเทม · ธงเนื้อเรื่อง (`TUTORIAL_*_開始/完了`)
ถ้าแปลของพวกนี้เกมจะหารูป/ธงไม่เจอ → เขียนไฟล์ done โดย **copy คีย์เป็นค่าเดิมทุกตัว**

ด่านตรวจ: `merge_qc.py --only 049` ผ่านทุกคีย์ ตก 0 · merge เข้า master แล้ว
