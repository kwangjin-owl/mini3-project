# 페이지 사이에 쉬기 위해 time을 불러온다
import time
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

# 페이지 주소 꼴 ({번호} 자리에 페이지 번호를 넣는다)
URL_TEMPLATE = "https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=50246&page={}&cnt=1000&SortOrder=1"
# 최대 페이지 수
MAX_PAGES = 3
# 이 행 수 이상 모이면 멈춘다
TARGET_ROWS = 50
# 저장 위치: 이 스크립트 파일 위치 기준 ../data/raw.csv
OUT_PATH = Path(__file__).resolve().parent / ".." / "data" / "raw.csv"
# 열 이름과 순서 (01_collect_p1.py와 같음)
COLUMNS = ["name", "price_raw", "sales_point_raw", "publisher_raw", "detail_url", "scraped_at"]
# 일반 브라우저처럼 보이도록 요청 헤더를 정한다 (01_collect_p1.py와 같음)
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


# 한 페이지의 HTML에서 행 목록을 뽑는 함수 (뽑는 방법은 01_collect_p1.py와 같음)
def parse_page(html, page_url, scraped_at):
    # 받은 HTML을 해석한다
    soup = BeautifulSoup(html, "html.parser")
    # 이 페이지의 행들을 담을 빈 목록을 만든다
    rows = []
    # 목록의 한 칸(도서 한 권)을 하나씩 돌며 값을 뽑는다
    for box in soup.select("div.ss_book_box"):
        # 도서명 링크(class가 bo3인 a)를 찾는다
        title_a = box.select_one("a.bo3")
        # 링크의 href를 읽는다 (없으면 빈 문자열)
        href = title_a.get("href", "") if title_a is not None else ""
        # 한 행의 값을 사전으로 만든다
        rows.append({
            # 전체 도서명: bo3 링크의 글자
            "name": text_of(title_a),
            # 판매가: ss_p2 칸 안의 글자 그대로
            "price_raw": text_of(box.select_one("span.ss_p2")),
            # 세일즈포인트: sales_point 칸의 글자, 앞뒤 공백만 정리
            "sales_point_raw": text_of(box.select_one("span.sales_point")),
            # 출판사: 주소에 PublisherSearch가 든 링크의 글자
            "publisher_raw": text_of(box.find("a", href=is_publisher_link)),
            # 상세 주소: 그 페이지 주소 기준 전체 주소 (href가 없으면 빈 값)
            "detail_url": urljoin(page_url, href) if href else "",
            # 수집 시각 (한국 시간)
            "scraped_at": scraped_at,
        })
    # 뽑은 행 목록을 돌려준다
    return rows


# 모든 페이지의 행을 모을 목록
all_rows = []
# 1페이지부터 최대 페이지까지 차례로 돈다
for page in range(1, MAX_PAGES + 1):
    # 2페이지부터는 요청 전에 1초 쉰다
    if page > 1:
        time.sleep(1)
    # 이번 페이지 주소를 만든다
    page_url = URL_TEMPLATE.format(page)
    # 페이지를 요청한다
    resp = requests.get(page_url, headers=HEADERS, timeout=20)
    # 응답 헤더의 Content-Type에 charset이 없으면
    if "charset" not in resp.headers.get("Content-Type", "").lower():
        # utf-8로 정한다 (있으면 requests가 넣어 둔 헤더 인코딩을 그대로 쓴다)
        resp.encoding = "utf-8"
    # 이 페이지의 수집 시각을 한국 시간으로 정한다
    scraped_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    # 200일 때만 행을 뽑고, 아니면 빈 목록으로 둔다
    page_rows = parse_page(resp.text, resp.url, scraped_at) if resp.status_code == 200 else []
    # 실제로 연 주소, 응답 상태, 이 페이지 행 수, 인코딩을 한 줄로 출력한다
    print(f"{page}페이지 | 주소: {resp.url} | 상태: {resp.status_code} | 행 수: {len(page_rows)} | 인코딩: {resp.encoding}")
    # 200이 아니거나 0행이면
    if resp.status_code != 200 or len(page_rows) == 0:
        # 몇 페이지에서 멈췄는지 출력하고 반복을 끝낸다
        print(f"{page}페이지에서 멈춤 (상태 {resp.status_code}, {len(page_rows)}행)")
        break
    # 이 페이지 행을 전체 목록에 더한다
    all_rows.extend(page_rows)
    # 합계가 목표 행 수 이상이면
    if len(all_rows) >= TARGET_ROWS:
        # 멈춘 이유를 출력하고 반복을 끝낸다
        print(f"합계 {len(all_rows)}행으로 {TARGET_ROWS}행 이상이 되어 {page}페이지에서 멈춤")
        break

# 모은 행을 정해진 열 순서의 표로 만든다
df = pd.DataFrame(all_rows, columns=COLUMNS)
# 합계 행 수를 출력한다
print("합계 행 수:", len(df))
# 서로 다른 detail_url 개수를 출력한다
print("서로 다른 detail_url 개수:", df["detail_url"].nunique())

# 모은 행이 없으면
if len(df) == 0:
    # CSV를 만들지 않는다고 출력한다
    print("0행이라 CSV를 만들지 않습니다.")
# 모은 행이 있으면
else:
    # 저장할 폴더가 없으면 만든다
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 표를 CSV로 저장한다 (엑셀에서도 한글이 깨지지 않도록 utf-8-sig)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    # 저장한 위치를 출력한다
    print("저장:", OUT_PATH.resolve())
    # 첫 행, 가운데 행(행 수 // 2), 마지막 행 번호를 정한다
    sample_idx = [0, len(df) // 2, len(df) - 1]
    # 표본 행 번호를 출력한다
    print("표본 3행 (행 번호:", sample_idx, ")")
    # 표본 행을 하나씩 돈다
    for i in sample_idx:
        # 행 번호를 출력한다
        print(f"--- 행 {i} ---")
        # 그 행의 모든 열 이름과 값을 출력한다
        for col in COLUMNS:
            # 열 이름과 값을 한 줄씩 출력한다
            print(f"  {col}: {df.at[i, col]}")
