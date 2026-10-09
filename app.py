import streamlit as st
import pandas as pd
import unicodedata
import base64

# 1. ページの設定
st.set_page_config(
    page_title="Nagi Archives DB",
    page_icon="icon.png",
    layout="centered"
)

# 背景アイコンを読み込む
with open("icon.png", "rb") as f:
    icon_base64 = base64.b64encode(f.read()).decode()

# 2. CSSの設定
css = """
<style>

    /* フォントをインポート */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Noto+Sans+JP:wght@400;700;900&display=swap');

    /* 上部スペースを詰める */
    header[data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* 画面上部の不要な余白・マージンを完全ゼロ化 */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 3rem !important;
        margin-top: 0rem !important;
    }

    /* 全体のフォントと背景色 */
    html,
    body,
    [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    .stApp {
    background-color: #0B0D12 !important;
    color: #E0E0E0 !important;
    position: relative;
    isolation: isolate;
}

/* ========================================
   背景にアイコンを薄く表示
   ======================================== */
.stApp::after {
    content: "";
    position: fixed;
    right: -40px;
    bottom: -10px;
    width: 420px;
    height: 420px;

    background-image: url("data:image/png;base64,ICON_BASE64");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;

    opacity: 0.6;
    pointer-events: none;

    z-index: 0;
}

/* 本体をアイコンより前にする */
[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
    background: transparent !important;
}

    /* ラベルや通常テキスト */
    p,
    label,
    .stMarkdown {
        color: #E0E0E0 !important;
    }

    /* タイトル */
    .nagi-title {
        font-family: 'Anton', 'Noto Sans JP', sans-serif !important;
        text-align: center;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 5px !important;
        font-size: 56px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    /* 紺色 */
    .nagi {
        color: #2563EB !important;
        text-shadow:
            0 0 12px rgba(37, 99, 235, 0.8),
            0 0 25px rgba(37, 99, 235, 0.4);
    }

    /* 濃いピンク */
    .archives {
        color: #FF1493 !important;
        text-shadow:
            0 0 12px rgba(255, 20, 147, 0.8),
            0 0 25px rgba(255, 20, 147, 0.4);
    }

    .db {
        color: #FFFFFF !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }

    /* 更新日 */
    .update-date {
        text-align: center;
        color: #8892B0 !important;
        font-size: 13px;
        margin-top: -5px;
        margin-bottom: 30px;
        letter-spacing: 1.5px;
    }

    /* セクションタイトル */
    .archive-title {
        font-size: 22px;
        font-weight: 900;
        color: #FFFFFF !important;
        border-bottom: 3px solid;
        border-image: linear-gradient(
            90deg,
            #1E40AF 0%,
            #FF1493 100%
        ) 1;
        padding-bottom: 8px;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    /* ラジオボタンの見た目調整 */
    div[role="radiogroup"] label {
        background-color: #131722 !important;
        padding: 8px 16px !important;
        border-radius: 4px !important;
        border: 1px solid #2A324B !important;
        margin-right: 8px !important;
        transition: all 0.2s ease !important;
    }

    /* 入力フォーム */
    .stTextInput input {
        background-color: #131722 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        border: 1px solid #2A324B !important;
        padding: 12px 15px !important;
    }

    /* 検索プレースホルダーの視認性向上 */
    .stTextInput input::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }

    .stTextInput input::-webkit-input-placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }

    .stTextInput input:focus {
        border-color: #FF1493 !important;
        box-shadow: 0 0 10px rgba(255, 20, 147, 0.5) !important;
    }

    /* 検索ボタン */
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(
            135deg,
            #1E3A8A 0%,
            #FF1493 100%
        ) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 40px !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        letter-spacing: 2px !important;
        transition: all 0.25s ease-in-out !important;
        box-shadow: 0 0 15px rgba(255, 20, 147, 0.3) !important;
        display: block;
        margin: 0 auto;
        text-transform: uppercase;
    }

    button[kind="secondaryFormSubmit"]:hover {
        transform: scale(1.03) !important;
        box-shadow:
            0 0 25px rgba(255, 20, 147, 0.7),
            0 0 12px rgba(37, 99, 235, 0.6) !important;
        cursor: pointer;
    }

    /* ランキング */
    .ranking-item {
        background: #131722;
        border: 1px solid #2A324B;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 7px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .ranking-rank {
        width: 42px;
        min-width: 42px;
        text-align: center;
        font-size: 18px;
        font-weight: 900;
        color: #FFFFFF;
    }

    .ranking-name {
        flex: 1;
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 700;
        word-break: break-word;
    }

    .ranking-count {
        white-space: nowrap;
        color: #FF1493;
        font-size: 15px;
        font-weight: 900;
    }

    /* 区切り線 */
    hr {
        border-color: #2A324B !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    

    /* スマホ表示 */
    @media (max-width: 600px) {

        .stApp::after {
            right: -60px;
            bottom: 10px;
            width: 300px;
            height: 300px;
            opacity: 0.5;
        }

        .main .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 0rem !important;
        }

        .nagi-title {
            font-size: 38px !important;
        }

        .archive-title {
            font-size: 18px !important;
        }

        .ranking-item {
            padding: 9px 10px;
            gap: 8px;
        }

        .ranking-rank {
            width: 34px;
            min-width: 34px;
            font-size: 16px;
        }

        .ranking-name {
            font-size: 14px;
        }

        .ranking-count {
            font-size: 14px;
        }
    }

</style>
"""

# CSS内のICON_BASE64を実際の画像データに置き換える
css = css.replace("ICON_BASE64", icon_base64)

st.markdown(
    css,
    unsafe_allow_html=True
)


# 3. 画面トップのタイトル
st.markdown(
    """
    <div class='nagi-title'>
        <span class='nagi'>Nagi</span>
        <span class='archives'>Archives</span>
        <span class='db'>DB</span>
    </div>
    """,
    unsafe_allow_html=True
)


# 更新日
st.markdown(
    "<div class='update-date'>✨公認アプリ✨<br>2026年10月09日更新</div>",
    unsafe_allow_html=True
)


# 文字を標準化する関数（検索漏れを防ぐ）
def normalize_text(text):
    if pd.isna(text):
        return ""

    text = unicodedata.normalize(
        'NFKC',
        str(text)
    ).lower()

    return "".join(text.split())


# データの読み込み
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("songs_data.xlsx")
        df.columns = df.columns.str.strip()
        return df

    except Exception as e:
        st.error(f"Excelの読み込み失敗: {e}")
        return None


df = load_data()


if df is not None:

    # ========================================
    # 🫀 ランキング
    # ========================================

    # 歌った曲 TOP10
    with st.expander("🫀 歌った曲 TOP10"):

        # オリ曲を含めないチェックボックス
        exclude_original = st.checkbox(
            "オリ曲を含めない"
        )

        if "曲名" in df.columns:

            # ランキング用データ
            ranking_df = df.copy()

            # 「オリ曲を含めない」にチェックが入っている場合、
            # イザナギ・エルヴァの曲を除外
            if exclude_original and "アーティスト名" in ranking_df.columns:
                ranking_df = ranking_df[
                    ranking_df["アーティスト名"]
                    .astype(str)
                    .str.strip()
                    != "イザナギ・エルヴァ"
                ]

            # 曲名＋アーティスト名の組み合わせでランキング
            if "アーティスト名" in ranking_df.columns:

                song_ranking = (
                    ranking_df[
                        ["曲名", "アーティスト名"]
                    ]
                    .dropna(subset=["曲名"])
                    .assign(
                        曲名=lambda x: x["曲名"].astype(str).str.strip(),
                        アーティスト名=lambda x: x["アーティスト名"]
                        .astype(str)
                        .str.strip()
                    )
                    .value_counts()
                    .head(10)
                )

                if not song_ranking.empty:

                    medals = ["🥇", "🥈", "🥉"]

                    for rank, ((song, artist), count) in enumerate(
                        song_ranking.items(),
                        start=1
                    ):

                        if rank <= 3:
                            rank_display = medals[rank - 1]
                        else:
                            rank_display = f"{rank}位"

                        st.markdown(
                            f'<div class="ranking-item">'
                            f'<div class="ranking-rank">{rank_display}</div>'
                            f'<div class="ranking-name">'
                            f'{song}'
                            f'<div style="font-size:13px; font-weight:500; margin-top:3px; color:#B8C0D9;">'
                            f'{artist}'
                            f'</div>'
                            f'</div>'
                            f'<div class="ranking-count">{count}回</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                else:
                    st.write("ランキングデータがありません。")

            else:
                st.error("Excelに「アーティスト名」列がありません。")

        else:
            st.error("Excelに「曲名」列がありません。")

    # 歌ったアーティスト TOP10
    with st.expander("🎤 歌ったアーティスト TOP10"):

        if "アーティスト名" in df.columns:

            artist_ranking = (
                df["アーティスト名"]
                .dropna()
                .astype(str)
                .str.strip()
                .value_counts()
                .head(10)
            )

            if not artist_ranking.empty:

                medals = ["🥇", "🥈", "🥉"]

                for rank, (artist, count) in enumerate(
                    artist_ranking.items(),
                    start=1
                ):

                    if rank <= 3:
                        rank_display = medals[rank - 1]
                    else:
                        rank_display = f"{rank}位"

                    st.markdown(
                        f"""
                        <div class="ranking-item">
                            <div class="ranking-rank">
                                {rank_display}
                            </div>
                            <div class="ranking-name">
                                {artist}
                            </div>
                            <div class="ranking-count">
                                {count}回
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:
                st.write("ランキングデータがありません。")

        else:
            st.error(
                "「アーティスト名」列がありません。"
            )


    # ========================================
    # 🎸 全アーカイブ(歌枠)から探す
    # ========================================

    st.markdown(
        "<div class='archive-title'>🎸 全アーカイブ(歌枠)から探す</div>",
        unsafe_allow_html=True
    )

    st.write(
        "検索方法を選択して、検索ワードを入力してください。"
    )


    # ========================================
    # 🔍 検索
    # ========================================

    # 検索方法を選択
    search_type = st.radio(
        "🔍 検索方法",
        ["曲情報から検索", "配信タイトルから検索"],
        horizontal=True
    )


    # 検索対象の列を設定
    if search_type == "曲情報から検索":

        target_columns = [
            "曲名",
            "アーティスト名",
            "年",
            "ジャンル"
        ]

        placeholder = (
            "例：光、イザナギ、2026、リレー など"
        )

    else:

        target_columns = [
            "配信タイトル"
        ]

        placeholder = (
            "例：叫びは、Rock Mode など"
        )


    st.write("")


    # ========================================
    # 🔍 検索フォーム
    # ========================================

    with st.form(
        "search_form",
        clear_on_submit=False
    ):

        search_word = st.text_input(
            "🎵 検索ワードを入力してください(部分検索可)",
            placeholder=placeholder
        )

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        search_button = st.form_submit_button(
            "🔍 SEARCH 👇"
        )


    # ========================================
    # 🔍 検索実行
    # ========================================

    if search_button:

        search_clean = normalize_text(search_word)

        if search_clean:

            # 指定の列が存在するかチェック
            missing_cols = [
                col
                for col in target_columns
                if col not in df.columns
            ]

            if not missing_cols:

                # 指定された列のどこかに
                # 検索ワードが含まれているか判定
                mask = pd.Series(
                    False,
                    index=df.index
                )

                for col in target_columns:

                    col_clean = (
                        df[col]
                        .astype(str)
                        .apply(normalize_text)
                    )

                    mask = mask | col_clean.str.contains(
                        search_clean,
                        na=False
                    )

                results = df[mask]

                # 検索結果の表示
                st.markdown("---")

                if not results.empty:

                    st.success(
                        f"🔥 {len(results)} 件の履歴が見つかりました！"
                    )

                    # URL列の自動判定＆クレンジング
                    column_config = {}
                    results = results.copy()

                    for col in results.columns:

                        if (
                            "url" in col.lower()
                            or "リンク" in col
                            or "link" in col.lower()
                        ):

                            results[col] = results[col].apply(
                                lambda x:
                                    str(x).strip()
                                    if pd.notna(x)
                                    and str(x).strip().startswith(
                                        ("http://", "https://")
                                    )
                                    else None
                            )

                            column_config[col] = (
                                st.column_config.LinkColumn(
                                    col,
                                    display_text="視聴する 🔗"
                                )
                            )

                    # インデックスを非表示化
                    st.dataframe(
                        results,
                        use_container_width=True,
                        column_config=column_config,
                        hide_index=True
                    )

                else:

                    st.warning(
                        "該当する履歴が見つかりませんでした。"
                    )

            else:

                st.error(
                    f"データの中に以下の列が見つかりません: "
                    f"{missing_cols}"
                )

                st.write(
                    "💡 現在の列名:",
                    list(df.columns)
                )

        else:

            st.warning(
                "検索ワードを入力してください。"
            )