# JSON으로 저장하고 다시 읽기 위해 json을 불러온다
import json
# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트가 있는 scripts 폴더 위치를 구한다
BASE = Path(__file__).resolve().parent
# 읽을 파일: ../data/clean.csv (읽기만 한다)
IN_PATH = BASE / ".." / "data" / "clean.csv"
# 저장할 파일: ../data/data.json
OUT_PATH = BASE / ".." / "data" / "data.json"
# 저장할 열과 순서
COLUMNS = ["name", "price", "sales_point", "publisher", "detail_url"]
# 따옴표 없는 숫자로 저장할 열
INT_COLUMNS = ["price", "sales_point"]

# clean.csv를 읽는다
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
# 저장할 다섯 열만 고른다
sub = df[COLUMNS]

# 한 행을 한 묶음(사전)으로 하는 목록을 담을 빈 목록
records = []
# 행을 하나씩 돈다
for _, row in sub.iterrows():
    # 한 행의 값을 담을 빈 사전
    item = {}
    # 열을 하나씩 돈다
    for col in COLUMNS:
        # 그 칸의 값을 꺼낸다
        value = row[col]
        # 값이 비어 있으면 JSON의 null로 둔다 (0이나 평균으로 채우지 않음)
        if pd.isna(value):
            item[col] = None
        # 숫자 열이면 파이썬 정수로 바꿔 따옴표 없는 숫자로 저장되게 한다
        elif col in INT_COLUMNS:
            item[col] = int(value)
        # 글자 열이면 글자 그대로 둔다
        else:
            item[col] = str(value)
    # 완성한 사전을 목록에 더한다
    records.append(item)

# data.json을 utf-8로 연다
with open(OUT_PATH, "w", encoding="utf-8") as f:
    # 한글이 깨지지 않게(ensure_ascii=False) 들여쓰기 2칸으로 저장한다
    json.dump(records, f, ensure_ascii=False, indent=2)
# 저장한 위치를 출력한다
print("저장:", OUT_PATH.resolve())

# 저장한 data.json을 다시 연다
with open(OUT_PATH, encoding="utf-8") as f:
    # JSON을 파이썬 목록으로 다시 읽는다
    loaded = json.load(f)
# 항목 수와 clean.csv 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"data.json 항목 수 {len(loaded)} / clean.csv 행 수 {len(df)} → {'같음' if len(loaded) == len(df) else '다름'}")

# clean.csv 첫 줄을 글자 그대로 다시 읽는다 (비교용)
csv_first = pd.read_csv(IN_PATH, encoding="utf-8-sig", dtype=str, nrows=1).iloc[0]
# data.json의 첫 항목을 꺼낸다
json_first = loaded[0]
# 비교 표 머리글을 출력한다
print("| 열 | data.json 첫 항목 | JSON 형 | clean.csv 첫 줄 | 같나 |")
# 비교 표 구분선을 출력한다
print("|---|---|---|---|---|")
# 다섯 열을 하나씩 돈다
for col in COLUMNS:
    # data.json 값을 꺼낸다
    j = json_first[col]
    # clean.csv 값을 글자로 꺼낸다
    c = csv_first[col]
    # 글자로 바꿨을 때 두 값이 같은지 판정한다
    same = "같음" if str(j) == c else "다름"
    # 열 이름, JSON 값(따옴표 여부가 보이게 repr), JSON 형, CSV 값, 판정을 출력한다
    print(f"| {col} | {j!r} | {type(j).__name__} | {c} | {same} |")
