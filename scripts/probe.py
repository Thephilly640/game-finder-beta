#!/usr/bin/env python3
"""One-off look at NASCAR's own feeds for finishing gaps. Writes probe.json."""
import json, os, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)[:200]}
out = {}
for series in (1, 2, 3):
    rl = get(f"https://cf.nascar.com/cacher/2026/{series}/race_list_basic.json")
    out[f"race_list_{series}"] = (rl if isinstance(rl, dict) else {"n": len(rl)})
    races = rl if isinstance(rl, list) else []
    done = [r for r in races if (r.get("winner_driver_id") or r.get("winner_driver_name"))]
    out[f"race_list_{series}_sample"] = races[:1]
    out[f"race_list_{series}_count"] = len(races)
    if not done:
        continue
    r = done[-1]
    rid = r.get("race_id")
    out[f"last_{series}"] = r
    wf = get(f"https://cf.nascar.com/cacher/2026/{series}/{rid}/weekend-feed.json")
    s = json.dumps(wf)
    out[f"weekend_{series}_len"] = len(s)
    wr = (wf.get("weekend_race") or [{}])[0] if isinstance(wf, dict) else {}
    out[f"weekend_{series}_keys"] = sorted(wr.keys()) if isinstance(wr, dict) else str(type(wr))
    res = wr.get("results") if isinstance(wr, dict) else None
    out[f"weekend_{series}_results_first3"] = (res or [])[:3]
    lf = get(f"https://cf.nascar.com/live/feeds/series_{series}/{rid}/live_feed.json")
    out[f"live_{series}_keys"] = sorted(lf.keys()) if isinstance(lf, dict) else str(type(lf))
    out[f"live_{series}_vehicles_first3"] = (lf.get("vehicles") or [])[:3] if isinstance(lf, dict) else None
    out[f"live_{series}_error"] = lf.get("_error") if isinstance(lf, dict) else None
open(os.path.join(ROOT, "probe.json"), "w").write(json.dumps(out, ensure_ascii=False, indent=1)[:200000])
