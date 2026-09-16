#!/usr/bin/env python3
"""
SerpApi(Google Scholar Author API)를 이용해 citation 수 / h-index / i10-index를
가져와 citations.json 파일로 저장하는 스크립트.

필요한 환경변수:
- SERPAPI_KEY : serpapi.com에서 발급받은 API 키
  (GitHub 저장소 Settings > Secrets and variables > Actions 에 등록)
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

SCHOLAR_USER_ID = "8PT4DmgAAAAJ"
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
API_URL = "https://serpapi.com/search.json"


def fetch_author_data() -> dict:
    if not SERPAPI_KEY:
        raise RuntimeError(
            "환경변수 SERPAPI_KEY가 설정되지 않았습니다. "
            "GitHub 저장소 Secrets에 SERPAPI_KEY를 등록했는지 확인하세요."
        )

    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_USER_ID,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    resp = requests.get(API_URL, params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"SerpApi 요청 실패: HTTP {resp.status_code} - {resp.text[:300]}")

    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"SerpApi 오류: {data['error']}")

    return data


def parse_metrics(data: dict) -> dict:
    author = data.get("author", {})
    cited_by = data.get("cited_by", {})
    table = cited_by.get("table", [])

    def get_row(key: str) -> dict:
        for row in table:
            if key in row:
                return row[key]
        return {}

    citations = get_row("citations")
    h_index = get_row("h_index")
    i10_index = get_row("i10_index")

    if not citations and not h_index:
        raise RuntimeError(
            "SerpApi 응답에서 지표를 찾을 수 없습니다. "
            "author_id가 올바른지, 응답 구조가 바뀌지 않았는지 확인하세요."
        )

    return {
        "name": author.get("name"),
        "citations_all": citations.get("all", 0),
        "citations_since_5y": citations.get("since_2020", 0),
        "h_index_all": h_index.get("all", 0),
        "h_index_since_5y": h_index.get("since_2020", 0),
        "i10_index_all": i10_index.get("all", 0),
        "i10_index_since_5y": i10_index.get("since_2020", 0),
        "profile_url": f"https://scholar.google.com/citations?user={SCHOLAR_USER_ID}&hl=en",
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main():
    data = fetch_author_data()
    metrics = parse_metrics(data)

    with open("citations.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
