import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 장르 열에 세로막대(|)로 여러 장르가 적힌 경우, 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # 개봉일(여덟 자리 숫자, 예: 20230115)을 날짜 형식으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


df = load_data(DATA_URL)

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ----------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.markdown("---")

# ----------------------------------------------------------------------
# 그래프 2. 장르 안에 영화 - 트리맵 (칸 크기: 총 관객)
# ----------------------------------------------------------------------
st.header("2. 장르별 영화 흥행 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.markdown("---")

# ----------------------------------------------------------------------
# 그래프 3. 총 관객 히스토그램
# ----------------------------------------------------------------------
st.header("3. 총 관객 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=20,
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    bargap=0.05,
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 영화가 많이 몰린 구간 계산
cut_result = pd.cut(df["total_audi"], bins=20)
bin_counts = cut_result.value_counts(sort=False)
top_bin = bin_counts.idxmax()
top_bin_count = bin_counts.max()

# 총 관객이 가장 많은 영화 계산
top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = top_movie_row["total_audi"]

st.markdown(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객 "
    f"**{int(top_bin.left):,}명 ~ {int(top_bin.right):,}명** 구간에 "
    f"**{top_bin_count}편**으로 가장 많이 몰려 있고, "
    f"총 관객이 가장 많은 영화는 **'{top_movie_name}'**"
    f"(총 관객 **{int(top_movie_audi):,}명**)입니다."
)

st.markdown("---")

# ----------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 vs 총 관객 - 산점도 (장르별 색상)
# ----------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.markdown("---")

# ----------------------------------------------------------------------
# 그래프 5. 장르별 총 관객 박스플롯 (영화 10편 이상인 장르만)
# ----------------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (10편 이상 장르만)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major_genres = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major_genres,
    x="genre",
    y="total_audi",
    hover_name="movieNm",
)
fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.markdown("---")

# ----------------------------------------------------------------------
# (다음 그래프를 이어서 추가할 자리)
# ----------------------------------------------------------------------
