# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 없이 파일로만 그리도록 matplotlib을 불러온다
import matplotlib
# 그림 창을 띄우지 않는 Agg 백엔드를 쓴다
matplotlib.use("Agg")
# 그래프를 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# 세로축 눈금 글자 모양을 정하기 위해 ticker를 불러온다
from matplotlib.ticker import FuncFormatter
# CSV를 읽고 묶어 계산하기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트가 있는 scripts 폴더 위치를 구한다
BASE = Path(__file__).resolve().parent
# 읽을 파일: ../data/clean.csv (읽기만 한다)
IN_PATH = BASE / ".." / "data" / "clean.csv"
# 저장할 그림: ../charts/by_category.png
OUT_PATH = BASE / ".." / "charts" / "by_category.png"
# 가로축 순서 (행 수 많은 순, 같으면 이름순)
ORDER = ["디딤돌", "좋은책신사고", "에듀왕", "천재교육",
         # 뒤쪽 네 곳 (각 1행)
         "비상교육", "슬기로운공부", "씨투엠에듀", "한국교육방송공사(초등)"]
# 그림 안에만 쓰는 영어 막대 이름 (데이터 값은 바꾸지 않는다)
EN_NAME = {"디딤돌": "Didimdol", "좋은책신사고": "Sinsago", "에듀왕": "Eduwang",
           # 천재교육·비상교육
           "천재교육": "Chunjae Education", "비상교육": "Visang Education",
           # 슬기로운공부·씨투엠에듀·EBS
           "슬기로운공부": "Slgong", "씨투엠에듀": "C2M Edu", "한국교육방송공사(초등)": "EBS"}
# 막대 색 (한 계열이므로 파란색 한 가지)
BAR_COLOR = "#2a78d6"
# 글자 색 (막대 색이 아닌 글자용 색)
TEXT_COLOR = "#52514e"

# clean.csv를 읽는다
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
# name에 "수학"이 들어간 행만 고른다
math = df[df["name"].str.contains("수학", regex=False)]
# 고른 행 수를 센다
n = len(math)
# 나머지 행 수를 센다
rest = len(df) - n

# publisher별로 price의 개수·합·평균을 구한다 (개수는 비어 있지 않은 price 수)
g = math.groupby("publisher")["price"].agg(["count", "sum", "mean"])

# 그룹별 표 머리글을 출력한다
print("| 범주 | 개수 | 합 | 평균 |")
# 표 구분선을 출력한다
print("|---|---|---|---|")
# 막대로 그릴 범주, 평균, 개수를 담을 목록
plot_names, plot_means, plot_counts = [], [], []
# 정해진 순서대로 범주를 돈다
for pub in ORDER:
    # 그 범주에 price 값이 하나도 없으면
    if pub not in g.index or g.at[pub, "count"] == 0:
        # 자료 없음으로 적고 막대는 그리지 않는다
        print(f"| {pub} | 자료 없음 | 자료 없음 | 자료 없음 |")
        # 다음 범주로 넘어간다
        continue
    # 그 범주의 개수를 꺼낸다
    cnt = int(g.at[pub, "count"])
    # 그 범주의 합을 꺼낸다
    total = int(g.at[pub, "sum"])
    # 그 범주의 평균을 꺼낸다
    mean = float(g.at[pub, "mean"])
    # 범주, 개수, 합, 평균(소수 둘째 자리)을 한 줄로 출력한다
    print(f"| {pub} | {cnt} | {total} | {mean:.2f} |")
    # 막대로 그릴 범주 이름을 더한다
    plot_names.append(pub)
    # 막대로 그릴 평균을 더한다
    plot_means.append(mean)
    # 막대로 그릴 개수를 더한다
    plot_counts.append(cnt)

# 정해진 순서에 없는 publisher가 있는지 찾는다
extra = [p for p in g.index if p not in ORDER]
# 순서에 없는 publisher가 있으면 알린다 (그림에는 넣지 않음)
if extra:
    # 순서 목록에 없는 publisher를 출력한다
    print("순서 목록에 없는 publisher:", extra)

# 개수 합을 구한다
count_sum = int(g["count"].sum())
# 빈 줄을 출력한다
print()
# 개수 합과 고른 행 수를 나란히 출력하고 같음/다름을 적는다
print(f"개수 합 {count_sum} / 고른 행 수 {n} → {'같음' if count_sum == n else '다름'}")
# 고른 행 수 + 나머지 행 수 = 전체 행 수를 출력한다
print(f"고른 행 수 {n} + 나머지 행 수 {rest} = {n + rest} (clean.csv 전체 행 수 {len(df)})")

# 그림과 축을 만든다
fig, ax = plt.subplots(figsize=(10, 6))
# 막대 위치 번호를 만든다
xs = list(range(len(plot_names)))
# 막대를 그린다
bars = ax.bar(xs, plot_means, width=0.6, color=BAR_COLOR)
# 막대 위에 평균(소수 둘째 자리)과 n을 두 줄로 적는다
ax.bar_label(bars, labels=[f"{m:,.2f}\nn = {c}" for m, c in zip(plot_means, plot_counts)],
             # 막대와 글자 사이 간격, 글자 색
             padding=4, color=TEXT_COLOR)
# 가로축 눈금 위치를 막대 위치로 정한다
ax.set_xticks(xs)
# 가로축 눈금 글자를 영어 이름으로 적고 겹치지 않게 기울인다
ax.set_xticklabels([EN_NAME[p] for p in plot_names], rotation=30, ha="right", color=TEXT_COLOR)
# 세로축 위쪽에 두 줄 글자가 들어갈 여유를 넉넉히 둔다
ax.set_ylim(0, max(plot_means) * 1.25)
# 세로축 눈금 글자를 쉼표 있는 숫자로 적는다
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
# 가로축 이름을 적는다
ax.set_xlabel("Publisher", color=TEXT_COLOR)
# 세로축 이름을 적는다
ax.set_ylabel("Average price (KRW)", color=TEXT_COLOR)
# 제목과 고른 행 수를 적는다
ax.set_title(f"Average price by publisher (math workbooks)\nn = {n}", loc="left")
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
