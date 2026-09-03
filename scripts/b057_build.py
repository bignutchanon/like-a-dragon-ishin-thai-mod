#!/usr/bin/env python3
"""รวมไฟล์ย่อยคำแปลของก้อน batch_MSG_057 แล้วเขียน translations/done/batch_MSG_057.done.json

คีย์เรียงตามลำดับใน translations/worklist/batch_MSG_057.json เสมอ (ด่าน A1)
"""
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = (r"C:\Users\BigNut\AppData\Local\Temp\claude"
           r"\d--Projects-like-a-dragon-ishin"
           r"\9340e158-6aa9-4e6e-b6ea-dea8a40498ae\scratchpad")


def load_part(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRATCH, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TH


def main():
    th = {}
    for part in ("b057_p1", "b057_p2", "b057_p3"):
        d = load_part(part)
        dup = set(d) & set(th)
        if dup:
            raise SystemExit("!! ดัชนีซ้ำระหว่างไฟล์ย่อย: %s" % sorted(dup))
        th.update(d)

    wl = json.load(io.open(os.path.join(ROOT, "translations", "worklist",
                                        "batch_MSG_057.json"), encoding="utf-8"))
    keys = list(wl["strings"])
    missing = [i for i in range(len(keys)) if i not in th]
    if missing:
        raise SystemExit("!! ขาดคำแปลที่ดัชนี: %s" % missing)
    extra = [i for i in th if i >= len(keys)]
    if extra:
        raise SystemExit("!! ดัชนีเกินขอบเขต: %s" % extra)

    out = {"batch": "MSG_057", "strings": {}}
    for i, k in enumerate(keys):
        out["strings"][k] = th[i]

    dest = os.path.join(ROOT, "translations", "done", "batch_MSG_057.done.json")
    with io.open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("เขียน %s แล้ว — %d คีย์" % (dest, len(out["strings"])))


if __name__ == "__main__":
    main()
