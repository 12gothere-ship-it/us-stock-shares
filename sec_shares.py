"""SEC 공시 데이터에서 미국 상장사 발행주식수를 받아 sec_shares.csv로 저장."""
import csv
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request

UA = os.environ["SEC_USER_AGENT"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def recent_quarters(n=3):
    today = datetime.date.today()
    y, q = today.year, (today.month - 1) // 3 + 1
    out = []
    for _ in range(n):
        out.append(f"CY{y}Q{q}I")
        q -= 1
        if q == 0:
            q, y = 4, y - 1
    return out


# CIK(기업 고유번호) -> 종목코드들 ('BRK-B' -> 'BRK.B')
tickers = get("https://www.sec.gov/files/company_tickers.json")
cik_map = {}
for e in tickers.values():
    cik_map.setdefault(e["cik_str"], []).append(e["ticker"].replace("-", "."))

# 최근 3개 분기 공시 표지의 발행주식수 중 가장 최신 값
best = {}
for q in recent_quarters():
    time.sleep(0.5)
    try:
        data = get("https://data.sec.gov/api/xbrl/frames/dei/"
                   f"EntityCommonStockSharesOutstanding/shares/{q}.json")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            continue
        raise
    for f in data.get("data", []):
        if not f.get("val"):
            continue
        b = best.get(f["cik"])
        if b is None or f["end"] > b[1]:
            best[f["cik"]] = (f["val"], f["end"])

rows = sorted((t, val, end) for cik, (val, end) in best.items() for t in cik_map.get(cik, []))
if len(rows) < 1000:
    sys.exit(f"받은 종목이 너무 적음({len(rows)}개) - 저장하지 않음")

with open("sec_shares.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["ticker", "shares", "end"])
    w.writerows(rows)
print(f"{len(rows)}개 종목 저장")
