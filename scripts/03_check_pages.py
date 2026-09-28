# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 읽을 위치: 이 스크립트 파일 위치 기준 ../data/raw.csv
IN_PATH = Path(__file__).resolve().parent / ".." / "data" / "raw.csv"

# CSV를 모두 글자로 읽는다 (값을 바꾸지 않고 읽기만 한다)
df = pd.read_csv(IN_PATH, encoding="utf-8-sig", dtype=str)
# 전체 행 수를 출력한다
print("전체 행 수:", len(df))

# scraped_at이 같은 행끼리 한 페이지로 묶는다 (나온 순서를 유지한다)
groups = df.groupby("scraped_at", sort=False)
# 페이지로 본 묶음 수를 출력한다
print("페이지로 본 묶음 수:", groups.ngroups)

# 묶음을 차례로 돌며 페이지 번호를 1부터 붙인다
for page_no, (scraped_at, part) in enumerate(groups, start=1):
    # 이 묶음의 첫 행 번호를 구한다
    first_idx = part.index[0]
    # 이 묶음의 끝 행 번호를 구한다
    last_idx = part.index[-1]
    # 페이지 번호, scraped_at, 행 수, 첫 행과 끝 행의 번호와 name을 한 줄로 출력한다
    print(f"{page_no}페이지 | scraped_at: {scraped_at} | 행 수: {len(part)} | "
          # 첫 행 번호와 name
          f"첫 행 {first_idx}: {part.at[first_idx, 'name']} | "
          # 끝 행 번호와 name
          f"끝 행 {last_idx}: {part.at[last_idx, 'name']}")
