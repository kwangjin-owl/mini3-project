# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 없이 파일로만 그리도록 matplotlib을 불러온다
import matplotlib
# 그림 창을 띄우지 않는 Agg 백엔드를 쓴다
matplotlib.use("Agg")
# 그래프를 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# 세로축 눈금 글자 모양을 정하기 위해 FuncFormatter를 불러온다
from matplotlib.ticker import FuncFormatter
# CSV를 읽고 묶어 계산하기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트가 있는 scripts 폴더 위치를 구한다
BASE = Path(__file__).resolve().parent
# 읽을 파일: ../data/clean.csv (읽기만 한다)
IN_PATH = BASE / ".." / "data" / "clean.csv"
# 저장할 그림: ../charts/by_category_median.png (by_category.png는 건드리지 않는다)
OUT_PATH = BASE / ".." / "charts" / "by_category_median.png"
# 가로축 순서 (06_by_category.py와 같음)
ORDER = ["디딤돌", "좋은책신사고", "에듀왕", "천재교육",
         # 뒤쪽 네 곳 (각 1행)
         "비상교육", "슬기로운공부", "씨투엠에듀", "한국교육방송공사(초등)"]
# 그림 안에만 쓰는 영어 막대 이름 (06_by_category.py와 같음, 데이터 값은 바꾸지 않는다)
EN_NAME = {"디딤돌": "Didimdol", "좋은책신사고": "Sinsago", "에듀왕": "Eduwang",
           # 천재교육·비상교육
           "천재교육": "Chunjae Education", "비상교육": "Visang Education",
           # 슬기로운공부·씨투엠에듀·EBS
           "슬기로운공부": "Slgong", "씨투엠에듀": "C2M Edu", "한국교육방송공사(초등)": "EBS"}
# 막대 색 (06_by_category.py와 같은 파란색)
BAR_COLOR = "#2a78d6"
# 글자 색 (막대 색이 아닌 글자용 색)
TEXT_COLOR = "#52514e"

# clean.csv를 읽는다
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
# name에 "수학"이 들어간 행만 고른다
math = df[df["name"].str.contains("수학", regex=False)]
# 고른 행 수를 센다
n = len(math)

# publisher별로 price의 개수·평균·중앙값을 구한다
g = math.groupby("publisher")["price"].agg(["count", "mean", "median"])
# 정해진 순서에 있고 값이 있는 범주만 그 순서대로 남긴다
g = g.reindex([p for p in ORDER if p in g.index and g.at[p, "count"] > 0])
# 평균 순위: 큰 값이 1위, 같은 값은 같은 순위 (소수 둘째 자리로 맞춘 뒤 비교)
g["mean_rank"] = g["mean"].round(2).rank(ascending=False, method="min").astype(int)
# 중앙값 순위: 큰 값이 1위, 같은 값은 같은 순위
g["median_rank"] = g["median"].round(2).rank(ascending=False, method="min").astype(int)

# 정해진 순서 중 자료가 없는 범주를 찾는다
missing = [p for p in ORDER if p not in g.index]
# 표 머리글을 출력한다
print("| 범주 | 개수 | 평균 | 중앙값 | 평균 순위 | 중앙값 순위 |")
# 표 구분선을 출력한다
print("|---|---|---|---|---|---|")
# 범주를 순서대로 돈다
for pub, r in g.iterrows():
    # 범주, 개수, 평균, 중앙값, 두 순위를 한 줄로 출력한다
    print(f"| {pub} | {int(r['count'])} | {r['mean']:.2f} | {r['median']} | {int(r['mean_rank'])} | {int(r['median_rank'])} |")
# 자료가 없는 범주를 하나씩 돈다
for pub in missing:
    # 자료 없음으로 적는다 (막대는 그리지 않는다)
    print(f"| {pub} | 자료 없음 | 자료 없음 | 자료 없음 | - | - |")

# 빈 줄을 출력한다
print()
# 평균 순위와 중앙값 순위가 다른 범주를 고른다
diff = g[g["mean_rank"] != g["median_rank"]]
# 제목을 출력한다
print("평균 순위와 중앙값 순위가 다른 범주:")
# 그런 범주가 없으면
if diff.empty:
    # 없다고 출력한다
    print("  없음")
# 그런 범주를 하나씩 돈다
for pub, r in diff.iterrows():
    # 범주와 두 순위를 출력한다
    print(f"  {pub}: 평균 순위 {int(r['mean_rank'])} → 중앙값 순위 {int(r['median_rank'])}")

# 빈 줄을 출력한다
print()
# 31행 중 price가 가장 큰 행들을 고른다 (같은 값이면 모두)
top = math[math["price"] == math["price"].max()]
# 31행 중 price가 가장 작은 행들을 고른다 (같은 값이면 모두)
low = math[math["price"] == math["price"].min()]
# 가장 큰 행과 가장 작은 행을 차례로 돈다
for label, rows in [("price 가장 큰 행", top), ("price 가장 작은 행", low)]:
    # 해당 행을 하나씩 돈다
    for i, r in rows.iterrows():
        # 구분, 행 번호, name, price, publisher를 출력한다
        print(f"{label}: 행 {i} | {r['name']} | {r['price']} | {r['publisher']}")

# 그림과 축을 만든다
fig, ax = plt.subplots(figsize=(10, 6))
# 막대 위치 번호를 만든다
xs = list(range(len(g)))
# 중앙값 막대를 그린다
bars = ax.bar(xs, g["median"], width=0.6, color=BAR_COLOR)
# 막대 위에 중앙값과 n을 두 줄로 적는다
ax.bar_label(bars, labels=[f"{m:,.1f}\nn = {int(c)}" for m, c in zip(g["median"], g["count"])],
             # 막대와 글자 사이 간격, 글자 색
             padding=4, color=TEXT_COLOR)
# 가로축 눈금 위치를 막대 위치로 정한다
ax.set_xticks(xs)
# 가로축 눈금 글자를 영어 이름으로 적고 겹치지 않게 기울인다
ax.set_xticklabels([EN_NAME[p] for p in g.index], rotation=30, ha="right", color=TEXT_COLOR)
# 세로축 위쪽에 두 줄 글자가 들어갈 여유를 넉넉히 둔다
ax.set_ylim(0, g["median"].max() * 1.25)
# 세로축 눈금 글자를 쉼표 있는 숫자로 적는다
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
# 가로축 이름을 적는다
ax.set_xlabel("Publisher", color=TEXT_COLOR)
# 세로축 이름을 적는다
ax.set_ylabel("Median price (KRW)", color=TEXT_COLOR)
# 제목과 고른 행 수를 적는다
ax.set_title(f"Median price by publisher (math workbooks)\nn = {n}", loc="left")
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
