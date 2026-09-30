# 초등 수학 문제집 비교 도우미

## 무엇을 하나

초등 5학년 아이의 수학 문제집을 고르는 학부모가 예산(원)과 학년-학기(예: 5-2)를 넣으면, 그 조건에 맞는 수학 문제집을 판매가 · 세일즈포인트 · 출판사와 함께 보여 주는 화면입니다.
「이 조건으로 추천받기」를 누르면 조건에 맞는 후보 가운데 한 권을 AI가 골라 이유 두 줄과 함께 보여 줍니다.

## 배포 주소

https://math-pick.vercel.app

## 데이터

- 출처 : 알라딘 초등학교참고서 주간 베스트 1페이지 (https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=50246)
- 수집 시점 : 2026-09-28 11:22 (한국 시간)
- 행 수 : 수집 50행 → 정제 50행 (뺀 행 0) · `data/data.json` 50개
- 정제한 열
  - `price` : `price_raw` 의 「원」과 쉼표를 떼고 정수로 바꿈 (예: 14,400원 → 14400)
  - `sales_point` : `sales_point_raw` 의 쉼표를 떼고 정수로 바꿈 (예: 19,763 → 19763)
  - `publisher` : `publisher_raw` 를 글자 그대로 두고 앞뒤 공백만 정리함 (15곳)
  - 못 바꾼 값은 채우지 않고 그 행을 사유와 함께 빼기로 했고, 이번에는 0건
- `data/data.json` 의 칸 : `name` · `price` · `sales_point` · `publisher` · `detail_url`

출처 : 알라딘 초등학교참고서 주간 베스트 1페이지 · 2026-09-28 11:22 수집(한국 시간) · 50개 · 부트캠프 비영리 과제

## AI 추천

- 모델 : Google Gemini `gemini-3.5-flash-lite` (`api/recommend.mjs`, Vercel Function `POST /api/recommend`)
- 열쇠 : Vercel 환경변수 `GEMINI_API_KEY` 에 넣습니다. 서버에서만 읽고 화면(`index.html`)으로는 보내지 않습니다.
- AI에게 넘기는 것
  - 화면은 조건 두 개(예산 · 학년-학기)만 서버에 보냅니다.
  - 서버는 화면이 보낸 목록을 믿지 않고, 그 조건으로 `data/data.json` 에서 후보를 다시 골라 판매가 낮은 순 최대 5권의 `name` · `price` · `sales_point` · `publisher` 를 조건과 함께 넘깁니다.
- AI에게 받는 것 : 후보 표의 `name` 하나와 이유 두 줄(`reasons`)
- 지키게 한 규칙 (지시문)
  1. `name` 은 후보 표의 이름을 글자 하나 바꾸지 않고 그대로 쓴다.
  2. 이유 첫 줄에는 추천한 책의 `price` 를, 둘째 줄에는 `sales_point` 를 표의 값 그대로 넣는다.
  3. 이유에 쓰는 숫자는 추천한 책의 `price` 와 `sales_point` 두 값뿐이다.
  4. 다른 후보와 견줄 때는 표로 사실인 것만 숫자 없이 말로 쓴다.
  5. 표에 없는 책이나 정보(난이도 · 후기 · 저자 · 학습 효과 등)는 말하지 않는다.
  6. `sales_point` 는 「세일즈포인트」 라고만 부른다(「인기」 · 「판매량」 금지).
  7. 이유 각 줄은 띄어쓰기를 포함해 40자 안쪽으로 쓴다.
  8. 「합리적」 · 「알맞다」 · 「부담이 적다」 · 「많은 선택」 · 「인기」 처럼 표에 없는 판단이나 평가는 쓰지 않는다.
- 화면에서 한 번 더 확인 : 받은 이름이 후보 안에 있고, 이유 속 숫자가 모두 그 책의 판매가 · 세일즈포인트일 때만 추천을 보여 줍니다. 아니면 「추천을 확인하지 못했습니다」, 응답을 받지 못하면 「잠시 뒤 다시 눌러 주세요」 를 띄웁니다.

## 확인한 것

- 조건 필터 (M10) : 정상(5-2 · 예산 16200) 3개 · 후보 1개(5-2 · 예산 15000) 1개 · 후보 없음(5-2 · 예산 14000) 0개로, 화면 개수와 `data.json` 에서 따로 센 개수가 세 경우 모두 같았습니다.
- AI 추천 검증 (M14) : 정상 조건에서 표에 없는 판단(「합리적」)이 숫자 없이 나와 화면 확인을 통과한 1건을 찾았습니다. 지시를 고친 뒤(커밋 c4233ee) 같은 조건으로 세 번 다시 해 보니 세 번 모두 디딤돌 5-2 · 첫 줄 15300(원) · 둘째 줄 세일즈포인트 36685 로 규칙을 지켰습니다.

## 한계

- 알라딘 초등학교참고서 주간 베스트 1페이지 50권을 2026-09-28 한 번 모은 것입니다.
- 이름에 「수학」이 든 책만 보여 줍니다.
- Gemini 무료 한도(하루 요청 수)를 넘으면 추천이 잠시 안 됩니다.
- 추천 이유가 숫자 두 줄이라 「왜 그 책인지」는 잘 드러나지 않습니다.
- 예산 칸에 숫자가 아닌 글자를 넣으면 빈칸처럼 읽힙니다.

## 실행 안내

명령은 모두 `mini3-project` 폴더에서 실행합니다. 윈도우는 `python`, 맥은 `python3` 로 씁니다.

### 1. 다시 모으기

| 순서 | 파일 | 만드는 것 | 명령 | 확인 |
|---|---|---|---|---|
| 0 | `scripts/00_env_check.py` | 파일 없음 (가짜 도서명 3개 표를 출력해 환경만 확인) | `python scripts/00_env_check.py` | 확인 안 함 |
| 1 | `scripts/01_collect_p1.py` | `data/raw_p1.csv` (목록 1페이지) — 사이트에 요청을 보낸다 · 페이지 수를 늘리지 않는다 · 주간 순위라 다시 돌리면 다른 50행이 된다 | `python scripts/01_collect_p1.py` | 확인 안 함 |
| 2 | `scripts/02_collect.py` | `data/raw.csv` — 사이트에 요청을 보낸다 · 페이지 수를 늘리지 않는다 · 주간 순위라 다시 돌리면 다른 50행이 된다 | `python scripts/02_collect.py` | 확인 안 함 |
| 3 | `scripts/03_check_pages.py` (필요할 때만) | 파일 없음 (`data/raw.csv` 를 페이지별 행 수로 출력) | `python scripts/03_check_pages.py` | 확인 안 함 |
| 3 | `scripts/03_clean.py` | `data/clean.csv` (`data/raw.csv` 는 읽기만 함) | `python scripts/03_clean.py` | 확인함 — 오류 없이 끝남 · 정제 50행 (전 50 → 후 50) |
| 4 | `scripts/04_stats.py` | 파일 없음 (`data/clean.csv` 의 기초 통계를 출력) | `python scripts/04_stats.py` | 확인 안 함 |
| 5 | `scripts/05_hist.py` | `charts/hist.png` | `python scripts/05_hist.py` | 확인 안 함 |
| 5 | `scripts/05_hist_half.py` (필요할 때만) | `charts/hist_half.png` | `python scripts/05_hist_half.py` | 확인 안 함 |
| 6 | `scripts/06_by_category.py` | `charts/by_category.png` | `python scripts/06_by_category.py` | 확인 안 함 |
| 6 | `scripts/06_by_category_median.py` (필요할 때만) | `charts/by_category_median.png` | `python scripts/06_by_category_median.py` | 확인 안 함 |
| 7 | `scripts/07_export_json.py` | `data/data.json` (`data/clean.csv` 는 읽기만 함) | `python scripts/07_export_json.py` | 확인 안 함 |

### 2. 화면에 반영하기

화면(`index.html`)은 `data/data.json` 과 `charts/hist.png` · `charts/by_category.png` 를 읽고, 추천(`api/recommend.mjs`)도 후보를 `data/data.json` 에서 다시 고릅니다. 새로 만든 `data/data.json` 과 `charts` 를 커밋 · 푸시하면 Vercel 이 다시 배포합니다. (확인 안 함)

### 3. AI 연결

Vercel 환경변수 이름 `GEMINI_API_KEY` 에 열쇠를 넣고 Redeploy 합니다. 열쇠가 없으면 서버가 `ai_unavailable` 을 돌려주고, 화면에는 「잠시 뒤 다시 눌러 주세요」가 뜹니다. (확인 안 함)
