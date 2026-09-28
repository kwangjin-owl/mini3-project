# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 없이 파일로만 그리도록 matplotlib 백엔드를 Agg로 정한다
import matplotlib
# 그림 창을 띄우지 않는 Agg 백엔드를 쓴다
matplotlib.use("Agg")
# 그래프를 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# 구간별 개수를 세기 위해 numpy를 불러온다
import numpy as np
# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트가 있는 scripts 폴더 위치를 구한다
BASE = Path(__file__).resolve().parent
# 읽을 파일: ../data/clean.csv (읽기만 한다)
IN_PATH = BASE / ".." / "data" / "clean.csv"
# 저장할 그림: ../charts/hist_half.png (hist.png는 건드리지 않는다)
OUT_PATH = BASE / ".." / "charts" / "hist_half.png"
# 고정 구간 경계: 0부터 40000까지 2500 간격 (16구간)
BINS = list(range(0, 40000 + 1, 2500))
# 가로축 눈금: 글자가 겹치지 않게 5000 간격
XTICKS = list(range(0, 40000 + 1, 5000))
# 막대 색 (05_hist.py와 같은 파란색 한 가지)
BAR_COLOR = "#2a78d6"
# 글자 색 (막대 색이 아닌 글자용 색)
TEXT_COLOR = "#52514e"

# clean.csv를 읽는다
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
# name에 "수학"이 들어간 행만 고른다
math = df[df["name"].str.contains("수학", regex=False)]
# 고른 행 수를 센다
n = len(math)
# 고른 행의 sales_point 값을 꺼낸다
sp = math["sales_point"]

# 구간별 개수를 센다 (왼쪽 끝 포함·오른쪽 끝 미포함, 마지막 구간만 오른쪽 끝 포함)
counts, edges = np.histogram(sp, bins=BINS)
# 구간 밖(0 미만 또는 40000 초과) 값의 개수를 센다
outside = int(((sp < BINS[0]) | (sp > BINS[-1])).sum())


# i번째 구간을 [왼쪽, 오른쪽) 또는 마지막만 [왼쪽, 오른쪽] 글자로 만드는 함수
def bin_label(i):
    # 마지막 구간은 오른쪽 끝을 포함하므로 ] 로, 나머지는 ) 로 적는다
    right = "]" if i == len(counts) - 1 else ")"
    # 구간 글자를 돌려준다
    return f"[{BINS[i]}, {BINS[i + 1]}{right}"


# 빈도 표 머리글을 출력한다
print("| 구간 | 개수 |")
# 빈도 표 구분선을 출력한다
print("|---|---|")
# 구간을 하나씩 돈다
for i, c in enumerate(counts):
    # 구간과 개수를 한 줄로 출력한다
    print(f"| {bin_label(i)} | {c} |")
# 빈도 합을 구한다
total = int(counts.sum())
# 합계 줄을 출력한다
print(f"| 합계 | {total} |")
# 빈 줄을 출력한다
print()
# 빈도 합과 고른 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"빈도 합 {total} / 고른 행 수 {n} → {'같음' if total == n else '다름'}")
# 구간 밖 값의 개수를 출력한다
print(f"구간 밖 값: {outside}개")
# 가장 높은 막대의 개수를 구한다
top = int(counts.max())
# 그 개수와 같은 높이의 구간을 모두 모은다
top_bins = [bin_label(i) for i, c in enumerate(counts) if c == top]
# 가장 높은 막대의 구간과 개수를 한 줄로 출력한다
print(f"가장 높은 막대: {', '.join(top_bins)} → {top}개")

# 그림과 축을 만든다
fig, ax = plt.subplots(figsize=(9, 5.5))
# 구간 폭만큼 막대를 그린다 (막대 사이 틈을 위해 흰 테두리)
bars = ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge",
              # 막대 색, 흰 테두리, 테두리 두께
              color=BAR_COLOR, edgecolor="white", linewidth=2)
# 막대 위에 개수를 적는다
ax.bar_label(bars, labels=[str(c) for c in counts], padding=3, color=TEXT_COLOR)
# 가로축 눈금을 5000 간격으로 정한다
ax.set_xticks(XTICKS)
# 가로축 눈금 글자를 쉼표 있는 숫자로 적는다
ax.set_xticklabels([f"{b:,}" for b in XTICKS], color=TEXT_COLOR)
# 가로축 범위를 구간 경계에 맞춘다
ax.set_xlim(BINS[0], BINS[-1])
# 세로축 위쪽에 막대 위 글자가 들어갈 여유를 둔다
ax.set_ylim(0, counts.max() * 1.15 + 0.5)
# 세로축 눈금을 정수로만 표시한다
ax.yaxis.get_major_locator().set_params(integer=True)
# 가로축 이름을 적는다
ax.set_xlabel("Sales Point", color=TEXT_COLOR)
# 세로축 이름을 적는다
ax.set_ylabel("Number of books", color=TEXT_COLOR)
# 제목과 고른 행 수를 적는다
ax.set_title(f"Aladin elementary math workbooks, half bin width (2,500)\nn = {n}", loc="left")
# 가로 눈금선만 옅게 그린다
ax.grid(axis="y", color="#e5e4e0", linewidth=0.8)
# 눈금선을 막대 뒤로 보낸다
ax.set_axisbelow(True)
# 위쪽과 오른쪽 테두리를 없앤다
ax.spines[["top", "right"]].set_visible(False)
# 여백을 알맞게 정리한다
fig.tight_layout()
# charts 폴더가 없으면 만든다
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
# 그림을 파일로 저장한다 (plt.show는 쓰지 않는다)
fig.savefig(OUT_PATH, dpi=150)
# 저장한 위치를 출력한다
print("저장:", OUT_PATH.resolve())
