# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 표를 읽고 정제하고 저장하기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트가 있는 scripts 폴더 위치를 구한다
BASE = Path(__file__).resolve().parent
# 읽을 파일: ../data/raw.csv (읽기만 하고 고치지 않는다)
IN_PATH = BASE / ".." / "data" / "raw.csv"
# 저장할 파일: ../data/clean.csv
OUT_PATH = BASE / ".." / "data" / "clean.csv"
# 빈칸이면 행을 빼는 기준 열
REQUIRED = ["name", "price", "sales_point", "detail_url"]
# 저장할 열 순서: _raw 열 바로 옆에 새 열을 붙인다
OUT_COLUMNS = ["name", "price_raw", "price", "sales_point_raw", "sales_point",
               # 출판사 원문과 정리한 출판사, 그 뒤에 주소와 수집 시각
               "publisher_raw", "publisher", "detail_url", "scraped_at"]


# 칸이 비었는지(값이 없거나 공백뿐인지) 참/거짓으로 돌려주는 함수
def blank_mask(s):
    # 값이 없는 칸은 빈칸이다
    mask = s.isna()
    # 글자 열이면 공백만 있는 칸도 빈칸으로 본다
    if not pd.api.types.is_numeric_dtype(s):
        # 값이 있는 칸 중 앞뒤 공백을 지우면 빈 글자가 되는 칸을 더한다
        mask = mask | (s.astype("string").str.strip() == "")
    # 빈칸 여부를 돌려준다
    return mask.fillna(False).astype(bool)


# 표의 행 수, 열별 데이터형, 열별 빈칸 수, detail_url 중복 수를 모아 돌려주는 함수
def summary(df):
    # 열 이름별 데이터형을 글자로 모은다
    dtypes = {c: str(df[c].dtype) for c in df.columns}
    # 열 이름별 빈칸 수를 모은다
    blanks = {c: int(blank_mask(df[c]).sum()) for c in df.columns}
    # detail_url이 두 번째 이후로 다시 나온 횟수를 센다
    dups = int(df["detail_url"].duplicated().sum())
    # 네 가지를 묶어 돌려준다
    return len(df), dtypes, blanks, dups


# 글자에서 지울 문자를 떼고, 숫자로만 남으면 정수로 바꾸는 함수 (못 바꾸면 NaN)
def to_int(s, remove):
    # 원문을 글자형으로 바꾼다 (빈칸은 그대로 비어 있음)
    t = s.astype("string")
    # 지울 문자를 하나씩 뗀다
    for ch in remove:
        # 해당 문자를 빈 글자로 바꾼다
        t = t.str.replace(ch, "", regex=False)
    # 앞뒤 공백을 정리한다
    t = t.str.strip()
    # 숫자만으로 이루어진 칸만 남기고 나머지는 비운다 (0이나 평균으로 채우지 않음)
    t = t.where(t.str.fullmatch(r"[0-9]+").fillna(False))
    # 정수형(빈칸 허용 Int64)으로 바꿔 돌려준다
    return pd.to_numeric(t).astype("Int64")


# raw.csv를 모두 글자로 읽는다
raw = pd.read_csv(IN_PATH, encoding="utf-8-sig", dtype=str)
# 원본을 건드리지 않도록 복사본으로 작업한다
df = raw.copy()

# 1. 판매가: 「원」과 쉼표를 떼고 정수로 바꿔 price에 넣는다
df["price"] = to_int(df["price_raw"], ["원", ","])
# 2. 세일즈포인트: 쉼표를 떼고 정수로 바꿔 sales_point에 넣는다
df["sales_point"] = to_int(df["sales_point_raw"], [","])
# 3. 출판사: 글자 그대로 앞뒤 공백만 정리해 publisher에 넣는다
df["publisher"] = df["publisher_raw"].astype("string").str.strip()
# 정해진 열 순서로 다시 놓는다
df = df[OUT_COLUMNS]

# 못 바꾼 값 목록 제목을 출력한다
print("[못 바꾼 값 (NaN으로 둠)]")
# 못 바꾼 값이 있었는지 기록할 변수
any_fail = False
# 바꾼 열과 그 원문 열을 짝지어 돈다
for new_col, raw_col in [("price", "price_raw"), ("sales_point", "sales_point_raw")]:
    # 바꾼 결과가 NaN인 행을 고른다
    failed = df[df[new_col].isna()]
    # 그런 행을 하나씩 돈다
    for idx, row in failed.iterrows():
        # 행 번호, 열 이름, 원문 값을 출력한다
        print(f"  행 {idx} | {new_col} | 원문 {row[raw_col]!r}")
        # 못 바꾼 값이 있었다고 기록한다
        any_fail = True
# 못 바꾼 값이 하나도 없었다면
if not any_fail:
    # 없다고 출력한다
    print("  없음")

# 뺄 행 목록 제목을 출력한다
print("[빼는 행]")
# 기준 열 중 빈칸인 열 이름을 행마다 모은다
blank_cols = {c: blank_mask(df[c]) for c in REQUIRED}
# 기준 열 중 하나라도 빈칸인 행을 고른다
blank_rows = pd.concat(blank_cols, axis=1).any(axis=1)
# 빈칸 때문에 빼는 행을 하나씩 돈다
for idx in df.index[blank_rows]:
    # 그 행에서 빈칸인 열 이름을 모은다
    cols = [c for c in REQUIRED if blank_cols[c][idx]]
    # 행 번호, 사유, name을 출력한다
    print(f"  행 {idx} | 사유: 빈칸 {cols} | name {df.at[idx, 'name']!r}")
# 빈칸 행을 뺀 나머지를 남긴다
kept = df[~blank_rows]
# 남은 행 중 detail_url이 앞에서 이미 나온 행을 고른다 (처음 한 행은 남김)
dup_rows = kept["detail_url"].duplicated(keep="first")
# 중복 때문에 빼는 행을 하나씩 돈다
for idx in kept.index[dup_rows]:
    # 같은 주소가 처음 나온 행 번호를 찾는다
    first_idx = kept.index[kept["detail_url"] == kept.at[idx, "detail_url"]][0]
    # 행 번호, 사유, 주소를 출력한다
    print(f"  행 {idx} | 사유: detail_url 중복 (처음 나온 행 {first_idx}) | {kept.at[idx, 'detail_url']}")
# 뺄 행이 하나도 없었다면
if not blank_rows.any() and not dup_rows.any():
    # 없다고 출력한다
    print("  없음")
# 중복 행까지 뺀 최종 표를 만든다
clean = kept[~dup_rows]

# 처리 전(raw.csv) 요약을 구한다
b_n, b_types, b_blanks, b_dups = summary(raw)
# 처리 후(clean) 요약을 구한다
a_n, a_types, a_blanks, a_dups = summary(clean)
# 처리 전후 비교 제목을 출력한다
print("[처리 전후 비교]")
# 행 수를 나란히 출력한다
print(f"  행 수: 전 {b_n} → 후 {a_n}")
# detail_url 중복 수를 나란히 출력한다
print(f"  detail_url 중복 수: 전 {b_dups} → 후 {a_dups}")
# 열별 비교 표의 머리글을 출력한다
print(f"  {'열':<16}{'전 데이터형':<12}{'후 데이터형':<12}{'전 빈칸':>8}{'후 빈칸':>8}")
# 처리 후 열 순서대로 돈다 (처리 전에 없던 열은 '-'로 표시)
for c in OUT_COLUMNS:
    # 열 이름, 전후 데이터형, 전후 빈칸 수를 한 줄로 출력한다
    print(f"  {c:<16}{b_types.get(c, '-'):<12}{a_types[c]:<12}{str(b_blanks.get(c, '-')):>8}{a_blanks[c]:>8}")

# 최종 표를 clean.csv로 저장한다 (엑셀에서 한글이 깨지지 않도록 utf-8-sig)
clean.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
# 저장한 위치를 출력한다
print("저장:", OUT_PATH.resolve())
