#!/bin/sh
# 맥에서 실행: card 폴더를 phase0.shop 서버의 /var/www/html/card 로 업로드
set -e
KEY=/Users/hyein/Desktop/AWS/SSHKEY.pem
cd "$(dirname "$0")"
python3 build.py
rsync -avz -e "ssh -i $KEY" --exclude deploy.sh --exclude '*.pdf' ./ admin@phase0.shop:/var/www/html/card/
echo "완료 → https://phase0.shop/card/"
