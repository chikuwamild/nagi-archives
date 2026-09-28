import streamlit as st
import pandas as pd
import unicodedata

# 1. ページの設定（ブラウザのタブ名とアイコン）
st.set_page_config(page_title="Nagi Archives DB", page_icon="🎸", layout="centered")

# 2. CSSの設定
st.markdown(
    """
    <style>
    /* Google Fontsからフォントをインポート */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');

    /* Streamlit標準のメニューバー・ヘッダー・フッターを非表示化 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* 全体のフォントを適用 */
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    /* 背景色をクリーンな薄いグレーに */
    .stApp {
        background-color: #FAFAFA !important;
    }

    p, label {
        color: #333333 !important;
    }

    /* タイトル（グラデーションテキスト） */
    .nagi-title {
        text-align: center;
        margin-bottom: 0px;
        font-size: 48px;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #2193b0 0%, #6dd5ed 40%, #ff758c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 5px;
    }

    /* 更新日 */
    .update-date {
        text-align: center;
        color: #888888 !important;
        font-size: 13px;
        margin-top: -5px;
        margin-bottom: 40px;
        letter-spacing: 1px;
    }

    /* セクションタイトル */
    .archive-title {
        font-size: 22px;
        font-weight: 700;
        color: #2C3E50 !important;
        border-bottom: 2px solid #EAEAEA;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* 入力フォームのスタイル */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #D1D5DB !important;
        padding: 10px 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    .stTextInput input:focus {
        border-color: #2193b0 !important;
        box-shadow: 0 0 0 2px rgba(33, 147, 176, 0.2) !important;
    }

    /* 検索ボタンのカスタマイズ（グラデーション＋ホバーアニメーション） */
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(90deg, #2193b0 0%, #ff758c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 8px 30px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
        display: block;
        margin: 0 auto;
    }

    button[kind="secondaryFormSubmit"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2) !important;
        opacity: 0.95;
    }

    /* スマホ表示のレスポンシブ調整 */
    @media (max-width: 600px) {
        .nagi-title {
            font-size: 32px !important;
        }
        .archive-title {
            font-size: 18px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. 画面トップのタイトル構成
st.markdown(
    """
    <div class='nagi-title'>
        Nagi Archives DB
    </div>
    """,
    unsafe_allow_html=True
)

# 更新日
st.markdown(
    "<div class='update-date'>※非公式だよ※<br>2026年9月27日更新</div>",
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
    # 4. 検索方法を選択
    search_type = st.radio(
        "🔍 検索方法",
        ["曲情報から検索", "配信タイトルから検索"],
        horizontal=True
    )

    # 5. 検索対象の列を設定
    if search_type == "曲情報から検索":
        target_columns = ["曲名", "アーティスト名", "年", "ジャンル"]
        placeholder = "例：光、イザナギ、2026、リレー など"
    else:
        target_columns = ["配信タイトル"]
        placeholder = "例：叫びはまだ名を持たない、Rock Mode など"

    st.write("")

    # 6. 検索フォーム
    with st.form("search_form", clear_on_submit=False):
        search_word = st.text_input(
            "🎵 検索ワードを入力してください(部分検索可)",
            placeholder=placeholder
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        search_button = st.form_submit_button("🔍 検索")

    # 7. 検索ボタンを押したときだけ検索
    if search_button:
        search_clean = normalize_text(search_word)

        if search_clean:
            # Excelに指定の列が存在するかチェック
            missing_cols = [col for col in target_columns if col not in df.columns]

            if not missing_cols:
                # 指定された列のどこかに検索ワードが含まれているか判定
                mask = pd.Series(False, index=df.index)

                for col in target_columns:
                    col_clean = df[col].astype(str).apply(normalize_text)
                    mask = mask | col_clean.str.contains(search_clean, na=False)

                results = df[mask]

                # 検索結果の表示
                st.markdown("---")
                
                if not results.empty:
                    st.success(f"🔥 {len(results)} 件の履歴が見つかりました！")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("該当する履歴が見つかりませんでした。")
            else:
                st.error(f"Excelファイルの中に以下の列が見つかりません: {missing_cols}")
                st.write("💡 現在のExcelの列名:", list(df.columns))
        else:
            st.warning("検索ワードを入力してください。")