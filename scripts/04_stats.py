# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# CSV를 읽고 통계를 내기 위해 pandas를 불러온다
import pandas as pd

# 읽을 위치: 이 스크립트 파일 위치 기준 ../data/clean.csv (읽기만 한다)
IN_PATH = Path(__file__).resolve().parent / ".." / "data" / "clean.csv"

# clean.csv를 읽는다
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
# 통계를 낼 열을 꺼낸다
sp = df["sales_point"]

# 비어 있지 않은 값의 개수를 센다
count = int(sp.count())
# 최솟값을 구한다
sp_min = sp.min()
# 최댓값을 구한다
sp_max = sp.max()
# 평균을 구한다
sp_mean = sp.mean()
# 중앙값을 구한다
sp_median = sp.median()


# 주어진 값과 같은 행들의 name과 publisher를 글자로 묶어 돌려주는 함수 (같은 값이 여러 행이면 모두)
def who(value):
    # 값이 같은 행을 고른다
    rows = df[sp == value]
    # 행마다 "행 번호 name / publisher" 모양으로 만들어 ; 로 잇는다
    return "; ".join(f"행 {i} {r['name']} / {r['publisher']}" for i, r in rows.iterrows())


# 마크다운 표 머리글을 출력한다
print("| 항목 | 값 |")
# 마크다운 표 구분선을 출력한다
print("|---|---|")
# 개수 줄을 출력한다
print(f"| 개수 | {count} |")
# 최소 줄을 출력하고 옆에 그 행의 name과 publisher를 적는다
print(f"| 최소 | {sp_min} ({who(sp_min)}) |")
# 최대 줄을 출력하고 옆에 그 행의 name과 publisher를 적는다
print(f"| 최대 | {sp_max} ({who(sp_max)}) |")
# 평균 줄을 소수 둘째 자리까지 출력한다
print(f"| 평균 | {sp_mean:.2f} |")
# 중앙값 줄을 계산된 그대로 출력한다
print(f"| 중앙값 | {sp_median} |")

# 빈 줄을 하나 출력한다
print()
# 전체 행 수를 센다
total = len(df)
# 개수와 전체 행 수가 같은지 판정한다
same = "같음" if count == total else "다름"
# 개수와 전체 행 수를 나란히 출력하고 판정을 적는다
print(f"sales_point 개수 {count} / clean.csv 전체 행 수 {total} → {same}")
