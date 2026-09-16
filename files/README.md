# Google Scholar Citation / h-index 자동 위젯

Google Scholar 프로필(`user=8PT4DmgAAAAJ`)의 citation 수, h-index, i10-index를
매일 자동으로 가져와 홈페이지에 표시하는 세트입니다.

## 구성 파일
- `scrape_scholar.py` : Google Scholar 페이지를 읽어 `citations.json`을 생성하는 스크립트
- `.github/workflows/update-citations.yml` : 매일 자동 실행하는 GitHub Actions 워크플로우
- `citations.json` : 결과가 저장되는 파일 (Actions가 자동으로 갱신)
- `widget-snippet.html` : 홈페이지에 붙여넣을 HTML/CSS/JS 코드

## 설정 방법 (5분)

### 1. GitHub 저장소 만들기
1. github.com에서 새 저장소(Repository)를 하나 만듭니다. (Public이어야 raw 파일에 접근 가능)
   - 예: `scholar-stats`
2. 이 폴더(`scholar-widget/`) 안의 파일들을 전부 그 저장소에 업로드합니다.
   - `.github/workflows/update-citations.yml` 경로 그대로 유지해야 합니다.

### 2. Actions 권한 확인
저장소의 **Settings → Actions → General → Workflow permissions**에서
"Read and write permissions"를 선택해주세요. (Actions가 citations.json을 커밋하려면 필요합니다)

### 3. 워크플로우 실행 확인
- 저장소의 **Actions** 탭 → `Update Google Scholar citations` → **Run workflow** 버튼으로
  1회 수동 실행해봅니다.
- 성공하면 `citations.json`에 실제 숫자가 채워집니다.
- 이후에는 매일 자동으로 (한국시간 새벽 6시경) 갱신됩니다.

### 4. 홈페이지에 위젯 삽입
1. `widget-snippet.html`을 열어 아래 줄을 본인의 GitHub 정보로 수정:
   ```js
   const DATA_URL =
     "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/citations.json";
   ```
2. `widget-snippet.html` 전체 내용을 홈페이지의 원하는 위치(HTML 소스)에 붙여넣습니다.

이제 홈페이지를 열면 citation 수 / h-index / i10-index가 자동으로 표시되고,
매일 최신 값으로 갱신됩니다.

## 참고 / 주의사항
- Google Scholar는 자동화된 접근(robots.txt)을 제한합니다. 이 스크립트는
  "하루 1회"라는 낮은 빈도로 실행하도록 설계되어 있으며, 이보다 훨씬 자주
  실행하면 일시적으로 차단(CAPTCHA)될 위험이 있습니다. 필요시
  `update-citations.yml`의 cron 주기를 조정할 수 있습니다.
- Google Scholar가 페이지 구조를 바꾸면 스크립트가 실패할 수 있습니다.
  그 경우 Actions 탭에 실패 알림이 뜨니 `scrape_scholar.py`의 파싱 정규식을
  다시 확인해야 합니다.
- 더 안정적인 방식을 원하시면 SerpApi(유료) 등 Google Scholar 전용 API
  서비스를 백엔드에서 호출하는 방법도 있습니다 — 필요하시면 말씀해주세요.
