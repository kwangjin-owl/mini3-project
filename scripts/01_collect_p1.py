# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 상대 주소를 전체 주소로 바꾸기 위해 urljoin을 불러온다
from urllib.parse import urljoin
# 수집 시각을 기록하기 위해 datetime을 불러온다
from datetime import datetime
# 한국 시간대를 쓰기 위해 ZoneInfo를 불러온다
from zoneinfo import ZoneInfo

# 웹 페이지 요청을 위해 requests를 불러온다
import requests
# HTML 해석을 위해 BeautifulSoup을 불러온다
from bs4 import BeautifulSoup
# 표를 만들고 CSV로 저장하기 위해 pandas를 불러온다
import pandas as pd

# 수집할 목록 페이지 주소 (이 페이지 하나만 요청한다)
URL = "https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=50246"
# 화면에서 직접 센 항목 수 (비교용)
EXPECTED_COUNT = 50
# 저장 위치: 이 스크립트 파일 위치 기준 ../data/raw_p1.csv
OUT_PATH = Path(__file__).resolve().parent / ".." / "data" / "raw_p1.csv"
# 열 이름과 순서
COLUMNS = ["name", "price_raw", "sales_point_raw", "publisher_raw", "detail_url", "scraped_at"]
# 일반 브라우저처럼 보이도록 요청 헤더를 정한다
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# 요소가 있으면 앞뒤 공백을 정리한 글자를, 없으면 빈 문자열을 돌려주는 함수
def text_of(tag):
    # 요소가 없으면 빈 문자열을 돌려준다
    if tag is None:
        return ""
    # 요소의 글자에서 앞뒤 공백만 정리해 돌려준다
    return tag.get_text().strip()


# 링크 주소에 PublisherSearch가 들어 있는지 확인하는 함수 (대소문자 무시)
def is_publisher_link(href):
    # href가 있고 그 안에 publishersearch가 들어 있으면 참
    return href is not None and "publishersearch" in href.lower()


# 목록 페이지를 한 번 요청한다
resp = requests.get(URL, headers=HEADERS, timeout=20)
# 응답 상태 코드를 출력한다
print("상태 코드:", resp.status_code)

# 응답 헤더의 Content-Type에 charset이 적혀 있는지 확인한다
if "charset" in resp.headers.get("Content-Type", "").lower():
    # 헤더에 적힌 인코딩을 그대로 쓴다 (requests가 이미 resp.encoding에 넣어 둠)
    pass
else:
    # 헤더에 없으면 utf-8로 정한다
    resp.encoding = "utf-8"
# 실제로 사용한 인코딩을 출력한다
print("사용 인코딩:", resp.encoding)

# 수집 시각을 한국 시간으로 한 번 정해 모든 행에 같이 쓴다
scraped_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

# 받은 HTML을 해석한다
soup = BeautifulSoup(resp.text, "html.parser")
# 목록의 한 칸(도서 한 권)을 모두 찾는다
boxes = soup.select("div.ss_book_box")

# 행들을 담을 빈 목록을 만든다
rows = []
# 전체 이름이 들어 있을 수 있는 링크 속성 이름들
FULL_NAME_ATTRS = ["title", "data-title", "aria-label"]
# 칸마다 (화면 글자, 전체 이름 속성 값) 짝을 담을 목록 (속성이 없으면 None)
name_checks = []
# 칸을 하나씩 돌며 값을 뽑는다
for box in boxes:
    # 도서명 링크(class가 bo3인 a)를 찾는다
    title_a = box.select_one("a.bo3")
    # 링크의 href를 읽는다 (없으면 빈 문자열)
    href = title_a.get("href", "") if title_a is not None else ""
    # 전체 이름 속성 중 처음 발견되는 값을 찾는다 (없으면 None)
    full_name = next((title_a.get(a) for a in FULL_NAME_ATTRS if title_a is not None and title_a.get(a) is not None), None)
    # 화면 글자와 전체 이름 속성 값을 짝으로 기록한다
    name_checks.append((text_of(title_a), full_name.strip() if full_name is not None else None))
    # 한 행의 값을 사전으로 만든다
    rows.append({
        # 전체 도서명: bo3 링크의 글자
        "name": text_of(title_a),
        # 판매가: ss_p2 칸 안의 글자 그대로 (예: 14,400원)
        "price_raw": text_of(box.select_one("span.ss_p2")),
        # 세일즈포인트: sales_point 칸의 글자, 앞뒤 공백만 정리
        "sales_point_raw": text_of(box.select_one("span.sales_point")),
        # 출판사: 주소에 PublisherSearch가 든 링크의 글자
        "publisher_raw": text_of(box.find("a", href=is_publisher_link)),
        # 상세 주소: href를 페이지 주소 기준 전체 주소로 바꾼다 (href가 없으면 빈 값)
        "detail_url": urljoin(URL, href) if href else "",
        # 수집 시각 (한국 시간)
        "scraped_at": scraped_at,
    })

# 행 목록을 정해진 열 순서의 표로 만든다
df = pd.DataFrame(rows, columns=COLUMNS)
# 행 수와 화면에서 센 수를 함께 출력한다
print(f"행 수: {len(df)} (화면에서 센 수: {EXPECTED_COUNT})")

# 출력할 때 열이 잘리지 않도록 표시 폭을 넓힌다
pd.set_option("display.width", 250)
# 출력할 때 모든 열을 보여 주도록 설정한다
pd.set_option("display.max_columns", None)
# 앞 3행을 출력한다
print("앞 3행:")
# 앞 3행을 표 형태로 출력한다
print(df.head(3).to_string())

# 빈 값이 있는 행을 찾기 위한 안내를 출력한다
print("빈 값 점검:")
# 빈 값이 있는 행이 있었는지 기록할 변수
found_empty = False
# 행 번호와 행 내용을 하나씩 돌며 확인한다
for idx, row in df.iterrows():
    # 이 행에서 값이 빈 문자열인 열 이름을 모은다
    empty_cols = [c for c in COLUMNS if row[c] == ""]
    # 빈 열이 하나라도 있으면
    if empty_cols:
        # 행 번호와 빈 열 이름을 출력한다
        print(f"  행 {idx}: 빈 열 {empty_cols}")
        # 빈 값이 있었다고 기록한다
        found_empty = True
# 빈 값이 있는 행이 하나도 없었다면
if not found_empty:
    # 없다고 출력한다
    print("  빈 값이 있는 행 없음")

# 상태 코드가 200이 아니거나 행이 0개면
if resp.status_code != 200 or len(df) == 0:
    # CSV를 만들지 않는다고 출력한다
    print("상태 코드가 200이 아니거나 0행이라 CSV를 만들지 않습니다.")
# 조건을 만족하면
else:
    # 저장할 폴더가 없으면 만든다
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 표를 CSV로 저장한다 (엑셀에서도 한글이 깨지지 않도록 utf-8-sig)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    # 저장한 위치를 출력한다
    print("저장:", OUT_PATH.resolve())

# 1. 전체 이름 속성이 있는 항목만 고른다
with_attr = [(shown, full) for shown, full in name_checks if full is not None]
# 속성이 있는 항목이 하나도 없으면
if not with_attr:
    # 속성이 없다고 출력한다
    print("전체 이름 속성 없음")
# 속성이 있는 항목이 있으면
else:
    # 속성 값과 화면 글자가 다른 항목 수를 센다
    diff_count = sum(1 for shown, full in with_attr if shown != full)
    # 속성 있는 항목 수와 다른 항목 수를 출력한다
    print(f"전체 이름 속성 있는 항목: {len(with_attr)}개, 그중 화면 글자와 다른 항목: {diff_count}개")
# 2. 화면 글자가 "..." 또는 "…"로 끝나는 항목 수를 센다
ellipsis_count = sum(1 for shown, _ in name_checks if shown.endswith(("...", "…")))
# 말줄임표로 끝나는 항목 수를 출력한다
print(f'"..." 또는 "…"로 끝나는 항목: {ellipsis_count}개')
# 두 조건 중 하나라도 해당하는 항목 수를 센다 (겹치는 항목은 한 번만)
cut_count = sum(1 for shown, full in name_checks
                # 속성 값과 다르거나 말줄임표로 끝나면 잘려 보이는 이름으로 본다
                if (full is not None and shown != full) or shown.endswith(("...", "…")))
# 잘려 보이는 이름 개수를 출력한다
print(f"잘려 보이는 이름: {cut_count}개")
