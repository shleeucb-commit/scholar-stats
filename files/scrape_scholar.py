#!/usr/bin/env python3
"""
Google Scholar 프로필에서 citation 수 / h-index / i10-index를 가져와
citations.json 파일로 저장하는 스크립트.

주의:
- Google Scholar는 robots.txt로 자동화된 접근을 제한하고 있습니다.
  이 스크립트는 GitHub Actions에서 "하루 1회" 정도의 낮은 빈도로
  실행하는 것을 전제로 만들어졌습니다. 너무 자주 실행하면 일시적으로
  차단(429 / CAPTCHA)될 수 있습니다.
- 개인 연구 성과를 본인 홈페이지에 표시하는 용도로만 사용하세요.
"""

import json
import re
import sys
import time
from datetime import datetime, timezone

import requests

SCHOLAR_USER_ID = "8PT4DmgAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_USER_ID}&hl=en"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_html(url: str, retries: int = 3, backoff: float = 5.0) -> str:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                return resp.text
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            last_err = str(e)
        print(f"[warn] attempt {attempt}/{retries} failed: {last_err}", file=sys.stderr)
        time.sleep(backoff * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def parse_metrics(html: str) -> dict:
    """
    Google Scholar 프로필 페이지의 지표 테이블(id="gsc_rsb_st")을 파싱합니다.
    테이블 구조: [Citations(All, Since5y), h-index(All, Since5y), i10-index(All, Since5y)]
    각 값은 <td class="gsc_rsb_std">숫자</td> 형태로 나열되어 있습니다.
    """
    values = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    if len(values) < 6:
        raise RuntimeError(
            "지표 파싱 실패 - Google Scholar가 페이지 구조를 바꿨거나 "
            "요청이 차단(CAPTCHA)되었을 수 있습니다."
        )

    name_match = re.search(r'id="gsc_prf_in">([^<]+)</div>', html)
    name = name_match.group(1) if name_match else None

    return {
        "name": name,
        "citations_all": int(values[0]),
        "citations_since_5y": int(values[1]),
        "h_index_all": int(values[2]),
        "h_index_since_5y": int(values[3]),
        "i10_index_all": int(values[4]),
        "i10_index_since_5y": int(values[5]),
        "profile_url": URL,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main():
    html = fetch_html(URL)
    metrics = parse_metrics(html)

    with open("citations.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
