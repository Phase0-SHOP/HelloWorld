# 황혜인 강사 디지털 명함 (phase0.shop/card)

명함의 QR 하나로 연락처 저장, 카카오톡, 리멤버 명함, 포트폴리오, 블로그·스레드 최신 글까지 한 화면에서 볼 수 있습니다.

## 파일

| 파일 | 역할 |
|---|---|
| `profile.json` | **내 정보는 여기서만 고칩니다** (전화, 이메일, 카톡·리멤버·블로그 링크) |
| `portfolio.json` | 포트폴리오입니다. 맨 위에 항목을 추가하면 최신순으로 쌓입니다 |
| `index.html` | QR을 찍으면 열리는 모바일 명함 페이지입니다 |
| `contact.vcf` | 연락처 파일입니다. 아이폰과 안드로이드에서 모두 저장됩니다 (`build.py`가 자동 생성) |
| `qr/card.svg` | **인쇄용 QR**입니다. 아이폰인지 안드로이드인지 자동으로 판별합니다 |
| `qr/card-ios.svg`, `qr/card-android.svg` | 기종별 전용 QR입니다 |
| `qr/contact-offline.svg` | 인터넷 없이도 바로 연락처가 추가되는 QR입니다 |
| `print.html`, `명함_인쇄용.pdf` | 90×50mm 앞면과 뒷면 명함입니다 |
| `feed.py` | 네이버 블로그, 티스토리, 스레드 글을 모아 `feed.json`을 만듭니다 |
| `assets/profile.jpg` | 프로필 사진입니다 (넣으면 자동으로 표시됩니다) |
| `assets/remember-card.jpg` | 리멤버 명함 이미지입니다 (넣으면 자동으로 표시됩니다) |

## 정보 수정 순서
1. `profile.json`에서 `TODO` 값을 바꿉니다. `feeds.naverBlogId`와 `feeds.tistoryId`에는 아이디만 넣습니다.
2. `python3 build.py`를 실행합니다 (`pip install segno` 필요). vcf와 QR이 다시 만들어집니다.
3. `./deploy.sh`를 실행하면 서버에 업로드됩니다.

## 블로그·스레드 자동 연동 (서버에서 한 번만 설정)
```
crontab -e
0 * * * * THREADS_TOKEN=발급받은토큰 /usr/bin/python3 /var/www/html/card/feed.py
```
- 네이버 블로그와 티스토리는 RSS로 가져오므로 아이디만 있으면 됩니다.
- 스레드는 Meta 개발자 센터에서 Threads API 장기 토큰(60일)을 발급받아야 합니다. 토큰이 없으면 스레드는 버튼 링크로만 연결됩니다.
