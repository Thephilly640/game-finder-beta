#!/usr/bin/env python3
"""One-off look at what ESPN gives for finishing gaps in NASCAR and F1. Writes probe.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update as u
from datetime import datetime, timedelta
out = {}
today = datetime.now(u.ET).date()
rng = f"{today - timedelta(days=5):%Y%m%d}-{today:%Y%m%d}"
for slug in ("nascar-premier", "f1"):
    lst = u.get(u.RC + f"{slug}/events?dates={rng}&limit=20")
    for it in (lst or {}).get("items", [])[:2]:
        ev = u.get(u.ref(it)) or {}
        comps = ev.get("competitions") or []
        comp = next((c for c in comps if (c.get("type") or {}).get("abbreviation") == "Race"), None) or (comps[0] if comps else {})
        cc = comp.get("competitors")
        items = cc if isinstance(cc, list) and cc else ((u.get(u.ref(cc)) or {}).get("items", []) if u.ref(cc) else [])
        items = sorted([c for c in items if c.get("order")], key=lambda c: c["order"])[:3]
        rec = {"name": ev.get("name"), "comp_keys": sorted(comp.keys()), "competitors_inline": isinstance(cc, list), "rows": []}
        for c in items:
            row = {"keys": sorted(c.keys()), "raw": {k: v for k, v in c.items() if not isinstance(v, dict) or "$ref" not in v}}
            for k in ("statistics", "linescores", "status", "score"):
                if u.ref(c.get(k)):
                    row[k] = u.get(u.ref(c[k]))
            rec["rows"].append(row)
        out[slug + ":" + str(ev.get("id"))] = rec
out["errors"] = u.ERRORS[:10]
s = json.dumps(out, ensure_ascii=False, indent=1)
open(os.path.join(u.ROOT, "probe.json"), "w").write(s[:150000])
print(len(s))
