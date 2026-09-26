import streamlit as st
import pandas as pd
import unicodedata

# 1. ページの設定（ブラウザのタブ名）
st.set_page_config(page_title="Nagi Archives DB", layout="centered")


# 背景色と文字色を設定するCSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F7FC !important;
    }

    /* 通常の説明文 */
    .stApp p {
        color: #111111 !important;
    }

    /* ラジオボタン */
    .stApp label {
        color: #111111 !important;
    }

    /* 検索ボタン */
    .stApp button[kind="secondaryFormSubmit"] {
        color: #111111 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC !important;
    }

    /* タイトル */
    .nagi-title {
        text-align: center;
        margin-bottom: 0px;
        font-size: 42px;
        white-space: nowrap;
    }

    .nagi {
        color: #0000cd !important;
    }

    .archives {
        color: #ff1493 !important;
    }

    .db {
        color: #000000 !important;
    }

    /* 更新日 */
    .update-date {
        text-align: center;
        color: #666666 !important;
        font-size: 12px;
        margin-top: -8px;
        margin-bottom: 5px;
    }

    /* 全アーカイブ */
    .archive-title {
        font-size: 22px;
        font-weight: bold;
        color: #111111 !important;
    }

    /* スマホ表示 */
    @media (max-width: 600px) {

        /* Nagi Archives DB */
        .nagi-title {
            font-size: 30px !important;
            white-space: normal;
        }

        /* 全アーカイブ */
        .archive-title {
            font-size: 18px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 2. 画面トップのタイトル構成
st.markdown(
    """
    <h1 class='nagi-title'>
        <span class='nagi'>Nagi</span>
        <span class='archives'>Archives</span>
        <span class='db'> DB</span>
    </h1>
    """,
    unsafe_allow_html=True
)


# 更新日
st.markdown(
    "<div class='update-date'>※非公式だよ※ 2026年9月27日更新</div>",
    unsafe_allow_html=True
)


# 「🎸 全アーカイブ(歌枠)から探す」
st.markdown(
    "<div class='archive-title'>🎸 全アーカイブ(歌枠)から探す</div>",
    unsafe_allow_html=True
)

st.write("検索方法を選択して、検索ワードを入力してください。")


# 文字を標準化する関数（検索漏れを防ぐ）
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = unicodedata.normalize('NFKC', str(text)).lower()
    return "".join(text.split())


# Excelデータの読み込み
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

    # 3. 検索方法を選択
    search_type = st.radio(
        "🔍 検索方法",
        ["曲情報から検索", "配信タイトルから検索"],
        horizontal=True
    )


    # 4. 検索対象の列を設定
    if search_type == "曲情報から検索":
        target_columns = ["曲名", "アーティスト名", "年", "ジャンル"]
        placeholder = "例：光、イザナギ、2026、リレー など"
    else:
        target_columns = ["配信タイトル"]
        placeholder = "例：叫びはまだ名を持たない、Rock Mode など"


    # 5. 検索フォーム
    with st.form("search_form"):

        search_word = st.text_input(
            "🎵 検索ワードを入力してください(部分検索可)",
            placeholder=placeholder
        )

        search_button = st.form_submit_button(
            "🔍 検索"
        )


    # 6. 検索ボタンを押したときだけ検索
    if search_button:

        search_clean = normalize_text(search_word)

        if search_clean:

            # Excelに指定の列が存在するかチェック
            missing_cols = [
                col for col in target_columns
                if col not in df.columns
            ]

            if not missing_cols:

                # 指定された列のどこかに検索ワードが含まれているか判定
                mask = pd.Series(False, index=df.index)

                for col in target_columns:

                    col_clean = df[col].astype(str).apply(normalize_text)

                    mask = mask | col_clean.str.contains(
                        search_clean,
                        na=False
                    )

                results = df[mask]


                # 検索結果の表示
                if not results.empty:

                    st.success(
                        f"🔥 {len(results)} 件の履歴が見つかりました！"
                    )

                    st.dataframe(
                        results,
                        use_container_width=True
                    )

                else:

                    st.warning(
                        "該当する履歴が見つかりませんでした。"
                    )


            else:

                st.error(
                    f"Excelファイルの中に以下の列が見つかりません: {missing_cols}"
                )

                st.write(
                    "💡 現在のExcelの列名:",
                    list(df.columns)
                )


        else:

            st.warning("検索ワードを入力してください。")