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
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Noto+Sans+JP:wght@400;700;900&display=swap');

    /* Streamlit標準のメニューバー・ヘッダー・フッターを非表示化 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* 全体のフォントと背景色 */
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    .stApp {
        background-color: #0B0D12 !important;
        color: #E0E0E0 !important;
    }

    /* ラベルや通常テキスト */
    p, label, .stMarkdown {
        color: #E0E0E0 !important;
    }

    /* タイトル */
    .nagi-title {
        font-family: 'Anton', 'Noto Sans JP', sans-serif !important;
        text-align: center;
        margin-bottom: 0px;
        font-size: 56px;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding-bottom: 5px;
    }

    /* ネイビー */
    .nagi {
        color: #2563EB !important;
        text-shadow: 0 0 12px rgba(37, 99, 235, 0.8), 0 0 25px rgba(37, 99, 235, 0.4);
    }

    /* ディープピンク */
    .archives {
        color: #FF1493 !important;
        text-shadow: 0 0 12px rgba(255, 20, 147, 0.8), 0 0 25px rgba(255, 20, 147, 0.4);
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
        margin-bottom: 35px;
        letter-spacing: 1.5px;
    }

    /* セクションタイトル（下線） */
    .archive-title {
        font-size: 22px;
        font-weight: 900;
        color: #FFFFFF !important;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #1E40AF 0%, #FF1493 100%) 1;
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
        background: linear-gradient(135deg, #1E3A8A 0%, #FF1493 100%) !important;
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
        box-shadow: 0 0 25px rgba(255, 20, 147, 0.7), 0 0 12px rgba(37, 99, 235, 0.6) !important;
        cursor: pointer;
    }

    /* 区切り線 */
    hr {
        border-color: #2A324B !important;
    }

    /* スマホ表示のレスポンシブ調整 */
    @media (max-width: 600px) {
        .nagi-title {
            font-size: 38px !important;
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
        <span class='nagi'>Nagi</span>
        <span class='archives'>Archives</span>
        <span class='db'>DB</span>
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
        
        search_button = st.form_submit_button("🔍 SEARCH")

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
                    
                    # URL・リンクが含まれる列を判定して設定
                    column_config = {}
                    for col in results.columns:
                        col_lower = str(col).lower()
                        if "url" in col_lower or "リンク" in col_lower or "link" in col_lower:
                            column_config[col] = st.column_config.LinkColumn(
                                col,
                                display_text="🔗 視聴する"  # クリック文字（URLそのまま表示したい場合は display_text=None にする）
                            )

                    # テーブル表示
                    st.dataframe(
                        results,
                        column_config=column_config,
                        use_container_width=True,
                        hide_index=True  # 左端の行番号(0, 1, 2...)を非表示
                    )
                else:
                    st.warning("該当する履歴が見つかりませんでした。")
            else:
                st.error(f"Excelファイルの中に以下の列が見つかりません: {missing_cols}")
                st.write("💡 現在のExcelの列名:", list(df.columns))
        else:
            st.warning("検索ワードを入力してください。")