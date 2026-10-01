#!/usr/bin/env python3
"""profile.json -> contact.vcf + QR 코드(qr/*.svg, *.png) 생성.

    pip install segno
    python3 build.py
"""
import json
import pathlib

import segno

HERE = pathlib.Path(__file__).resolve().parent
P = json.loads((HERE / "profile.json").read_text(encoding="utf-8"))


def real(v):
    """TODO 가 남아 있는 값은 비어 있는 것으로 취급."""
    return v if v and "TODO" not in v else ""


def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def vcard():
    L = P["links"]
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{esc(P['familyName'])};{esc(P['givenName'])};;;",
        f"FN:{esc(P['name'])}",
        f"ORG:{esc(P['org'])}",
        f"TITLE:{esc(P['title'])}",
    ]
    if real(P["phone"]):
        lines.append(f"TEL;TYPE=CELL:{P['phone']}")
    if real(P["email"]):
        lines.append(f"EMAIL;TYPE=WORK:{P['email']}")
    lines.append(f"URL:{P['cardUrl']}")
    lines.append(f"item1.URL:{P['website']}")
    lines.append("item1.X-ABLabel:홈페이지")
    for i, (key, label) in enumerate(
        [("kakao", "카카오톡"), ("remember", "리멤버"), ("naverBlog", "네이버 블로그"),
         ("tistory", "티스토리"), ("threads", "스레드")], start=2):
        if real(L.get(key, "")):
            lines += [f"item{i}.URL:{L[key]}", f"item{i}.X-ABLabel:{label}"]
    lines.append(f"NOTE:{esc(P['greeting'] + chr(10) + P['intro'])}")
    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def qr(name, data):
    q = segno.make(data, error="q", micro=False)
    q.save(HERE / "qr" / f"{name}.svg", scale=10, border=2, dark="#1f1a17")
    q.save(HERE / "qr" / f"{name}.png", scale=20, border=2, dark="#1f1a17")
    print(f"  qr/{name}.svg  ->  {data[:70]}")


def main():
    (HERE / "qr").mkdir(exist_ok=True)
    (HERE / "contact.vcf").write_text(vcard(), encoding="utf-8", newline="")
    print("contact.vcf 생성")
    url = P["cardUrl"]
    qr("card", url)                       # 명함 인쇄용 (자동 판별: 아이폰/안드로이드)
    qr("card-ios", url + "?os=ios")       # 아이폰 전용
    qr("card-android", url + "?os=android")  # 안드로이드 전용
    # 인터넷 없이도 바로 연락처 추가되는 QR (이름·전화·이메일·명함주소만)
    offline = ["BEGIN:VCARD", "VERSION:3.0", f"N:{P['familyName']};{P['givenName']}",
               f"FN:{P['name']}", f"TITLE:{P['title']}"]
    if real(P["phone"]):
        offline.append(f"TEL:{P['phone']}")
    if real(P["email"]):
        offline.append(f"EMAIL:{P['email']}")
    offline += [f"URL:{url}", "END:VCARD"]
    qr("contact-offline", "\n".join(offline))


if __name__ == "__main__":
    main()
