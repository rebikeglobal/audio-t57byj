#!/usr/bin/env python3
"""Add an episode and regenerate feed.xml.

Usage: python3 add_episode.py [--show research|study] path/to/file.mp3 "標題" "描述" [--date YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS+08:00; default now]
Default show is research. The mp3 is copied into <show dir>/episodes/ (ASCII filename),
metadata appended to <show dir>/episodes.json. Run with no positional args to rebuild all feeds.
"""
import json, os, re, shutil, subprocess, sys, uuid, datetime as dt
from email.utils import format_datetime
from xml.sax.saxutils import escape
TPE = dt.timezone(dt.timedelta(hours=8))
BASE = "https://rebikeglobal.github.io/audio-t57byj"
ROOT = os.path.dirname(os.path.abspath(__file__))
SHOWS = {
    "research": {"dir": "research", "title": "LJ 研究", "cover": "research/cover-v2.png",
                 "desc": "研究相關論文與筆記的語音版，僅供自己收聽。"},
    "study": {"dir": "study", "title": "LJ 個人學習", "cover": "study/cover-v3.png",
                   "desc": "個人學習筆記的語音版，僅供自己收聽。"},
}

def duration(p):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p])
    return int(float(out))

def build(show, eps):
    cfg = SHOWS[show]; sub = cfg["dir"]; d0 = os.path.join(ROOT, sub)
    url = BASE + ("/" + sub if sub else "")
    items = []
    for e in sorted(eps, key=lambda e: e["date"], reverse=True):
        p = os.path.join(d0, "episodes", e["file"])
        d = dt.datetime.fromisoformat(e["date"])
        if len(e["date"]) == 10:  # legacy date-only entries: noon Taipei
            d = d.replace(hour=12)
        if d.tzinfo is None:
            d = d.replace(tzinfo=TPE)
        s = duration(p)
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(e['description'])}</description>
      <itunes:summary>{escape(e['description'])}</itunes:summary>
      <enclosure url="{url}/episodes/{e['file']}" length="{os.path.getsize(p)}" type="audio/mpeg"/>
      <guid isPermaLink="false">{e['guid']}</guid>
      <pubDate>{format_datetime(d)}</pubDate>
      <itunes:duration>{s//3600:d}:{s%3600//60:02d}:{s%60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:episodeType>full</itunes:episodeType>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{escape(cfg["title"])}</title>
    <link>{url}/</link>
    <atom:link href="{url}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>{escape(cfg["desc"])}</description>
    <language>zh-tw</language>
    <itunes:author>LJ</itunes:author>
    <itunes:owner><itunes:name>LJ</itunes:name></itunes:owner>
    <itunes:image href="{BASE}/{cfg['cover']}"/>
    <itunes:category text="Education"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
    open(os.path.join(d0, "feed.xml"), "w").write(feed)

def db_path(show):
    return os.path.join(ROOT, SHOWS[show]["dir"], "episodes.json")

def load(show):
    p = db_path(show)
    return json.load(open(p)) if os.path.exists(p) else []

def main():
    a = sys.argv[1:]
    show = "research"
    if "--show" in a:
        i = a.index("--show"); show = a[i+1]; del a[i:i+2]
        if show not in SHOWS: sys.exit(f"unknown show {show}; choose from {list(SHOWS)}")
    if a:
        eps = load(show)
        date = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
        if "--date" in a:
            i = a.index("--date"); date = a[i+1]; del a[i:i+2]
        src, title, desc = a
        name = re.sub(r"[^A-Za-z0-9.-]", "-", f"{date[:10]}-{os.path.basename(src)}")
        if any(e["file"] == name for e in eps): sys.exit(f"exists: {name}")
        if os.path.getsize(src) > 95_000_000: sys.exit("file >95MB: GitHub rejects files over 100MB; split it first")
        os.makedirs(os.path.join(ROOT, SHOWS[show]["dir"], "episodes"), exist_ok=True)
        shutil.copy(src, os.path.join(ROOT, SHOWS[show]["dir"], "episodes", name))
        eps.append({"file": name, "title": title, "description": desc, "date": date, "guid": str(uuid.uuid4())})
        json.dump(eps, open(db_path(show), "w"), ensure_ascii=False, indent=2)
    for s in SHOWS:
        eps = load(s)
        if eps:
            build(s, eps); print(f"{s}: feed rebuilt with {len(eps)} episode(s)")

if __name__ == "__main__":
    main()
