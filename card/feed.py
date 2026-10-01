#!/usr/bin/env python3
"""네이버 블로그·티스토리 RSS + 스레드(API) 최신 글을 모아 feed.json 으로 저장.

표준 라이브러리만 사용합니다. 서버(EC2) crontab 에 등록하면 1시간마다 자동 갱신:
    0 * * * * THREADS_TOKEN=xxx /usr/bin/python3 /var/www/html/card/feed.py
"""
import datetime as dt
import email.utils
import html
import json
import os
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
P = json.loads((HERE / "profile.json").read_text(encoding="utf-8"))
UA = {"User-Agent": "Mozilla/5.0 (phase0 card feed)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
        return r.read()


def clean(s, n=120):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s[:n] + ("…" if len(s) > n else "")


def first_img(s):
    m = re.search(r'<img[^>]+src="([^"]+)"', html.unescape(s or ""))
    return m.group(1) if m else ""


def iso(rfc822):
    try:
        return email.utils.parsedate_to_datetime(rfc822).isoformat()
    except Exception:
        return ""


def rss(url, source):
    root = ET.fromstring(get(url))
    out = []
    for it in root.iter("item"):
        desc = it.findtext("description") or ""
        out.append({
            "source": source,
            "title": clean(it.findtext("title"), 80),
            "summary": clean(desc),
            "image": first_img(desc),
            "link": (it.findtext("link") or "").strip(),
            "date": iso(it.findtext("pubDate") or ""),
        })
    return out


def threads(token):
    url = ("https://graph.threads.net/v1.0/me/threads"
           "?fields=id,text,permalink,timestamp,media_url,media_type&limit=20&access_token=" + token)
    data = json.loads(get(url))
    return [{
        "source": "threads",
        "title": clean(d.get("text"), 60) or "스레드 게시물",
        "summary": clean(d.get("text"), 140),
        "image": d.get("media_url", "") if d.get("media_type") == "IMAGE" else "",
        "link": d.get("permalink", ""),
        "date": d.get("timestamp", ""),
    } for d in data.get("data", [])]


def main():
    f = P.get("feeds", {})
    items, errors = [], []
    jobs = []
    if f.get("naverBlogId"):
        jobs.append(("naver", lambda: rss(f"https://rss.blog.naver.com/{f['naverBlogId']}.xml", "naver")))
    if f.get("tistoryId"):
        jobs.append(("tistory", lambda: rss(f"https://{f['tistoryId']}.tistory.com/rss", "tistory")))
    if os.environ.get("THREADS_TOKEN"):
        jobs.append(("threads", lambda: threads(os.environ["THREADS_TOKEN"])))
    for name, job in jobs:
        try:
            items += job()
        except Exception as e:  # 한 곳이 실패해도 나머지는 갱신
            errors.append(f"{name}: {e}")
    items.sort(key=lambda x: x["date"], reverse=True)
    out = {"updated": dt.datetime.now(dt.timezone.utc).isoformat(), "items": items[:30]}
    if errors:
        out["errors"] = errors
    (HERE / "feed.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"feed.json: {len(out['items'])}개" + (f" / 오류 {errors}" if errors else ""))


if __name__ == "__main__":
    main()
