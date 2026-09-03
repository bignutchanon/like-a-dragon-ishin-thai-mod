"""ผู้ตรวจ: dump ก้อนแบบกระชับ  usage: rev_dump.py BATCH [lo] [hi] [--ja]"""
import sys, json

sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from rev_query import rows

b = sys.argv[1]
args = [a for a in sys.argv[2:] if not a.startswith("--")]
lo = int(args[0]) if args else 0
hi = int(args[1]) if len(args) > 1 else 9999
withja = "--ja" in sys.argv

for r in rows(b):
    if not (lo <= r["i"] <= hi):
        continue
    print(f"{r['i']:03d}| E {r['en'].replace(chr(10),' | ')}")
    if withja:
        print(f"   | J {(r['ja'] or '').replace(chr(13),'').replace(chr(10),' | ')}")
    print(f"   | T {r['th'].replace(chr(10),' | ')}")
