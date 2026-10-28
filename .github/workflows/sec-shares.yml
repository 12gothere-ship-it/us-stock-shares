name: SEC shares

on:
  schedule:
    - cron: "17 21 * * 5"   # 매주 토요일 오전 6시 17분(한국시간)
  workflow_dispatch:         # Actions 탭에서 수동 실행 가능

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SEC 주식수 받기
        run: python3 sec_shares.py
        env:
          SEC_USER_AGENT: ${{ secrets.SEC_USER_AGENT }}
      - name: 변경 내용 저장
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add sec_shares.csv
          git diff --cached --quiet || git commit -m "Update SEC shares"
          git push
