import streamlit as st
import pandas as pd
import unicodedata
import base64
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from urllib.parse import urlparse, parse_qs

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
    position: absolute;
    right: -40px;
    bottom: 0;
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
        font-size: 10px !important;
        line-height: 1.3 !important;
        margin-top: -5px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
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

    /* ページ切替ボタン：通常・ホバー・クリック時で色を変えて操作を分かりやすくする */
    [data-testid="stButton"] > button {
        background: #151923 !important;
        color: #F8FAFC !important;
        border: 1px solid #303746 !important;
        box-shadow: none !important;
        opacity: 1 !important;
        transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.08s ease !important;
    }

    [data-testid="stButton"] > button p {
        color: #F8FAFC !important;
    }

    /* マウスを乗せたとき：青に変化 */
    [data-testid="stButton"] > button:hover:not(:disabled) {
        background: #2563EB !important;
        border-color: #60A5FA !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.25) !important;
    }

    [data-testid="stButton"] > button:hover:not(:disabled) p {
        color: #FFFFFF !important;
    }

    /* クリック中：ピンクに変化 */
    [data-testid="stButton"] > button:active:not(:disabled) {
        background: #C02678 !important;
        border-color: #FF1493 !important;
        color: #FFFFFF !important;
        transform: translateY(1px) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.25) !important;
    }

    [data-testid="stButton"] > button:active:not(:disabled) p {
        color: #FFFFFF !important;
    }

    /* キーボード操作などでフォーカスされたとき：青い枠で表示 */
    [data-testid="stButton"] > button:focus-visible {
        outline: 2px solid #60A5FA !important;
        outline-offset: 2px !important;
    }

    /* 無効なページ切替ボタン可視性考慮 */
    [data-testid="stButton"] > button:disabled,
    [data-testid="stButton"] > button:disabled p {
        background: #10141C !important;
        color: #778092 !important;
        border-color: #202631 !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }

    [data-testid="stButton"] > button:disabled p {
        color: #778092 !important;
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
        padding: 7px 14px !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        width: fit-content !important;
        min-width: 0 !important;
        transition: all 0.25s ease-in-out !important;
        box-shadow: 0 0 15px rgba(255, 20, 147, 0.3) !important;
        display: inline-flex !important;
        margin: 0 !important;
        text-transform: uppercase;
    }

    button[kind="secondaryFormSubmit"]:hover {
        transform: scale(1.03) !important;
        box-shadow:
            0 0 25px rgba(255, 20, 147, 0.7),
            0 0 12px rgba(37, 99, 235, 0.6) !important;
        cursor: pointer;
    }

    /* 検索フォームのボタンを左寄せ・コンパクトに配置 */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        width: fit-content !important;
        max-width: 100% !important;
        gap: 8px !important;
        justify-content: flex-start !important;
        align-items: center !important;
    }

    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: fit-content !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
    }

    [data-testid="stForm"] button[kind="secondaryFormSubmit"] {
        width: fit-content !important;
        min-width: 0 !important;
        padding: 7px 14px !important;
        margin: 0 !important;
    }

    /* Clearボタン色 */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button[kind="secondaryFormSubmit"],
    [data-testid="stForm"] [data-testid="stColumn"]:nth-child(2) button[kind="secondaryFormSubmit"] {
        background: linear-gradient(135deg, #1E40AF 0%, #38BDF8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.22) !important;
        letter-spacing: 0 !important;
    }

    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) button[kind="secondaryFormSubmit"]:hover,
    [data-testid="stForm"] [data-testid="stColumn"]:nth-child(2) button[kind="secondaryFormSubmit"]:hover {
        background: linear-gradient(135deg, #2563EB 0%, #7DD3FC 100%) !important;
        border: none !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.38) !important;
    }

    /* 視聴リンクボタン */
    a[data-testid="stLinkButton"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #FF1493 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
    }

    a[data-testid="stLinkButton"] p {
        color: #FFFFFF !important;
    }

    /* 検索結果の視聴ボタン */
    [data-testid="stLinkButton"] a {
        padding: 0.35rem 0.45rem !important;
        min-height: 0 !important;
        font-size: 0.78rem !important;
        white-space: nowrap !important;
        border-radius: 6px !important;
        background: #25204A !important;
        color: #FF4DA6 !important;
        border: 1px solid #45356D !important;
    }

    /* 検索結果の表示に関する控えめな案内 */
    .layout-note {
        color: #8892B0 !important;
        font-size: 0.72rem !important;
        line-height: 1.4 !important;
        margin: 0.2rem 0 0.6rem !important;
    }

    /* 検索結果カード：背景アイコンと区別できる背景色・枠線 */
    [class*="st-key-result_card_"] {
        background: #11151F !important;
        border: 1px solid #2A324B !important;
        border-radius: 6px !important;
        padding: 8px 8px 12px !important;
        margin-bottom: 10px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        min-width: 0 !important;
    }

    [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        width: 100% !important;
        min-width: 0 !important;
        align-items: flex-start !important;
    }

    /* 検索結果内の補助情報は詰めて表示 */
    [data-testid="stVerticalBlock"] [data-testid="stCaptionContainer"] p {
        font-size: 0.78rem !important;
        line-height: 1.35 !important;
        margin-bottom: 0.15rem !important;
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
    

    /* PC表示：ページ番号と検索結果の文字欄を垂直中央に配置 */
    @media (min-width: 601px) {
        .st-key-pagination_top [data-testid="stColumn"]:nth-child(2),
        .st-key-pagination_bottom [data-testid="stColumn"]:nth-child(2) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .st-key-pagination_top [data-testid="stCaptionContainer"],
        .st-key-pagination_bottom [data-testid="stCaptionContainer"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            min-height: 42px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-pagination_top [data-testid="stCaptionContainer"] p,
        .st-key-pagination_bottom [data-testid="stCaptionContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
        }

        /* 画像＋視聴ボタン列と、文字情報列の高さをそろえ、文字を中央寄せ */
        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
            display: block !important;
            align-self: start !important;
            min-width: 0 !important;
        }

        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) > [data-testid="stVerticalBlock"] {
            width: 100% !important;
            justify-content: flex-start !important;
        }
    }

    /* スマホ表示 */
    @media (max-width: 600px) {

        /* スマホでは画面幅を超えないよう、全体の横並び設定は変更しない */
        /* ページ送りボタンだけ文字と余白を少し小さくする */
        [data-testid="stButton"] > button {
            padding: 0.3rem 0.1rem !important;
            font-size: 10px !important;
            min-width: 0 !important;
            width: 100% !important;
        }

        [data-testid="stButton"] > button p {
            font-size: 10px !important;
            white-space: nowrap !important;
            line-height: 1.15 !important;
            margin: 0 !important;
        }

        /* ページ送りは3列を均等にし、必ず1行に収める */
        .st-key-pagination_top [data-testid="stHorizontalBlock"],
        .st-key-pagination_bottom [data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) minmax(0, 0.65fr) minmax(0, 1fr) !important;
            gap: 4px !important;
            width: 100% !important;
            min-width: 0 !important;
        }

        .st-key-pagination_top [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
        .st-key-pagination_bottom [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: auto !important;
            min-width: 0 !important;
            flex: none !important;
            padding: 0 !important;
        }

        .st-key-pagination_top button,
        .st-key-pagination_bottom button {
            min-width: 0 !important;
            padding: 0.25rem 0.05rem !important;
            white-space: nowrap !important;
        }

        .st-key-pagination_top [data-testid="stCaptionContainer"],
        .st-key-pagination_bottom [data-testid="stCaptionContainer"] {
            white-space: nowrap !important;
            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100% !important;
            min-height: 42px !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .st-key-pagination_top [data-testid="stCaptionContainer"] p,
        .st-key-pagination_bottom [data-testid="stCaptionContainer"] p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
        }

        .st-key-pagination_top [data-testid="stColumn"]:nth-child(2),
        .st-key-pagination_bottom [data-testid="stColumn"]:nth-child(2) {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* 検索結果は画面幅内に収め、サムネイルと情報の2列にする */
        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: minmax(0, 26%) minmax(0, 1fr) !important;
            align-items: start !important;
            gap: 8px !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box !important;
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: 0 !important;
            width: auto !important;
            max-width: 100% !important;
            flex: none !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        /* サムネイル列だけ間隔を詰める（文字情報の行間には影響させない） */
        [data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stVerticalBlock"] {
            gap: 0.25rem !important;
            row-gap: 0.25rem !important;
        }

        /* 視聴ボタンはサムネイル下に配置 */
        [data-testid="stLinkButton"],
        a[data-testid="stLinkButton"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
            min-width: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: 32px !important;
            padding: 4px 3px !important;
            font-size: 11px !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        [data-testid="stLinkButton"] p,
        a[data-testid="stLinkButton"] p {
            width: auto !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            font-size: 11px !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] [data-testid="stImage"],
        [class*="st-key-result_card_"] [data-testid="stHorizontalBlock"] [data-testid="stImage"] img {
            display: block !important;
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }

        /* スマホで本文全体が横にはみ出さないようにする */
        [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: 100vw !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            box-sizing: border-box !important;
        }

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


    /* TOP10の開閉エリア：フォーカス・ホバー青系で強調 */
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {
        background-color: #0B0D12 !important;
        color: #F8FAFC !important;
        border-color: #252B38 !important;
    }

    [data-testid="stExpander"] summary:hover {
        background-color: #17213A !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }

    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:focus-visible,
    [data-testid="stExpander"] details:focus,
    [data-testid="stExpander"] details:focus-visible {
        background-color: #17213A !important;
        color: #FFFFFF !important;
        outline: 2px solid #2563EB !important;
        outline-offset: 2px !important;
        box-shadow: none !important;
    }

    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #F8FAFC !important;
        fill: currentColor !important;
    }

    [data-testid="stExpander"] summary:hover p,
    [data-testid="stExpander"] summary:hover span,
    [data-testid="stExpander"] summary:hover svg,
    [data-testid="stExpander"] summary:focus p,
    [data-testid="stExpander"] summary:focus span,
    [data-testid="stExpander"] summary:focus svg,
    [data-testid="stExpander"] summary:focus-visible p,
    [data-testid="stExpander"] summary:focus-visible span,
    [data-testid="stExpander"] summary:focus-visible svg {
        color: #FFFFFF !important;
        fill: currentColor !important;
    }


    /* 全体の文字 */
    html {
        font-size: 90% !important;
    }
    [data-testid="stAppViewContainer"] {
        font-size: 0.9rem !important;
    }
    [data-testid="stAppViewContainer"] h1 {
        font-size: 1.8rem !important;
    }
    [data-testid="stAppViewContainer"] h2 {
        font-size: 1.45rem !important;
    }
    [data-testid="stAppViewContainer"] h3 {
        font-size: 1.2rem !important;
    }
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] .stMarkdown,
    [data-testid="stAppViewContainer"] .stCaption {
        font-size: 0.9rem;
    }

    /* TOP10の結果・アーカイブ検索タイトル */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.85rem !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        font-size: 0.95rem !important;
    }
    /* 「🎸 全アーカイブ（歌枠）から探す」の見出し */
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3 {
        line-height: 1.25 !important;
    }


    /* サイズ指定を明示的に上書き：アーカイブ見出し */
    [data-testid="stAppViewContainer"] .archive-title {
        font-size: 19px !important;
        line-height: 1.25 !important;
        letter-spacing: 1px !important;
    }

    /* TOP10内のランキング名・回数 */
    [data-testid="stAppViewContainer"] .ranking-name {
        font-size: 13px !important;
        line-height: 1.25 !important;
    }
    [data-testid="stAppViewContainer"] .ranking-count {
        font-size: 13px !important;
        line-height: 1.25 !important;
    }

    /* TOP10の開閉見出し */
    [data-testid="stAppViewContainer"] [data-testid="stExpander"] summary,
    [data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
        font-size: 14px !important;
        line-height: 1.25 !important;
    }


    /* 歌った曲TOP：アーティスト名 */
    [data-testid="stExpander"] .ranking-item .ranking-name .ranking-artist,
    [data-testid="stExpander"] .ranking-item .ranking-name div.ranking-artist {
        display: block !important;
        font-size: 11px !important;
        line-height: 1.2 !important;
        font-weight: 400 !important;
        opacity: 0.82 !important;
    }


    /* 配信日並び替え */
    .st-key-date_sort_control,
    .st-key-date_sort_control [data-testid="stButton"],
    .st-key-date_sort_control [data-testid="stButton"] > div {
        width: fit-content !important;
        min-width: 0 !important;
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    .st-key-date_sort_control [data-testid="stButton"] button,
    .st-key-date_sort_control [data-testid="stButton"] button[kind],
    .st-key-date_sort_control [data-testid="stButton"] button:focus,
    .st-key-date_sort_control [data-testid="stButton"] button:focus:not(:active),
    .st-key-date_sort_control [data-testid="stButton"] button:not(:hover):not(:active) {
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 2.1rem !important;
        min-height: 2.1rem !important;
        padding: 0.25rem 0.55rem !important;
        font-size: 0.75rem !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        border: 1px solid transparent !important;
        outline: none !important;
        box-shadow: none !important;
        color: #F8FAFC !important;
        transform: scale(1) !important;
        transition: background-color 0.12s ease, border-color 0.12s ease, transform 0.08s ease !important;
    }

    .st-key-date_sort_control [data-testid="stButton"] button p,
    .st-key-date_sort_control [data-testid="stButton"] button span {
        color: #F8FAFC !important;
        opacity: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ホバー時のみ薄い背景、押下時は青みのある背景と縮小で反応 */
    .st-key-date_sort_control [data-testid="stButton"] button:hover {
        background: rgba(148, 163, 184, 0.14) !important;
        background-color: rgba(148, 163, 184, 0.14) !important;
        background-image: none !important;
        border-color: rgba(148, 163, 184, 0.22) !important;
        box-shadow: none !important;
    }

    .st-key-date_sort_control [data-testid="stButton"] button:active {
        background: rgba(37, 99, 235, 0.28) !important;
        background-color: rgba(37, 99, 235, 0.28) !important;
        background-image: none !important;
        border-color: rgba(96, 165, 250, 0.5) !important;
        transform: scale(0.92) !important;
        box-shadow: none !important;
    }

    /* ツールチップ「並び替え」を暗い背景＋白文字にして視認性を確保 */
    [data-testid="stTooltipContent"],
    [data-baseweb="tooltip"] > div,
    [role="tooltip"] {
        background-color: #202633 !important;
        background: #202633 !important;
        color: #FFFFFF !important;
        border: 1px solid #3B465C !important;
        opacity: 1 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
    }

    [data-testid="stTooltipContent"] *,
    [data-baseweb="tooltip"] > div *,
    [role="tooltip"] * {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }

    .st-key-date_sort_control [data-testid="stButton"] > button:focus-visible {
        outline: 2px solid rgba(96, 165, 250, 0.75) !important;
        outline-offset: 2px !important;
    }

    .st-key-date_sort_control [data-testid="stButton"] > button p {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 1rem !important;
        line-height: 1.2 !important;
        color: #F8FAFC !important;
    }


    /* ランキング行のレイアウトを安定化 */
    .ranking-item {
        display: grid !important;
        grid-template-columns: 42px minmax(0, 1fr) auto !important;
        align-items: center !important;
        column-gap: 12px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        min-width: 0 !important;
        line-height: 1.4 !important;
        overflow: visible !important;
    }

    .ranking-item .ranking-rank {
        display: block !important;
        box-sizing: border-box !important;
        width: auto !important;
        min-width: 0 !important;
        margin: 0 !important;
        line-height: 1.35 !important;
        align-self: center !important;
    }

    .ranking-item .ranking-name {
        display: block !important;
        box-sizing: border-box !important;
        min-width: 0 !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }

    .ranking-item .ranking-name .ranking-artist {
        display: block !important;
        margin-top: 3px !important;
        line-height: 1.3 !important;
        overflow-wrap: anywhere !important;
    }

    .ranking-item .ranking-count {
        display: block !important;
        box-sizing: border-box !important;
        min-width: max-content !important;
        margin: 0 !important;
        line-height: 1.35 !important;
        white-space: nowrap !important;
        align-self: center !important;
    }

    @media (max-width: 600px) {
        .ranking-item {
            grid-template-columns: 34px minmax(0, 1fr) auto !important;
            column-gap: 8px !important;
            padding: 9px 10px !important;
        }

        .ranking-item .ranking-rank {
            font-size: 16px !important;
        }

        .ranking-item .ranking-name,
        .ranking-item .ranking-count {
            font-size: 14px !important;
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
    "<div class='update-date'>✨公認アプリ✨<br>2026年10月18日更新<br>(TOTAL TRACKS:758)</div>",
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
    
def get_youtube_video_id(url):
    """YouTubeのURLから動画IDを取得する"""
    if pd.isna(url):
        return None

    try:
        parsed = urlparse(str(url).strip())
        host = parsed.netloc.lower().split(":")[0]

        if host.startswith("www."):
            host = host[4:]

        video_id = None

        if host == "youtu.be":
            video_id = parsed.path.strip("/").split("/")[0]

        elif host in {
            "youtube.com",
            "m.youtube.com",
            "music.youtube.com"
        }:
            if parsed.path == "/watch":
                video_id = parse_qs(
                    parsed.query
                ).get("v", [None])[0]

            else:
                parts = parsed.path.strip("/").split("/")

                if (
                    len(parts) >= 2
                    and parts[0] in {"shorts", "live", "embed"}
                ):
                    video_id = parts[1]

        if (
            video_id
            and len(video_id) == 11
            and all(c.isalnum() or c in "_-" for c in video_id)
        ):
            return video_id

    except Exception:
        pass

    return None


# YouTubeサムネイルを取得する関数
@st.cache_data(ttl=86400, max_entries=60)
def get_thumbnail(video_id):
    if not video_id:
        return None

    thumbnail_url = (
        "https://img.youtube.com/vi/"
        f"{video_id}/hqdefault.jpg"
    )

    try:
        response = requests.get(thumbnail_url, timeout=5)
        response.raise_for_status()

        # スマホでの小さな表示に合わせて縮小・圧縮し、
        # Streamlitから配信する画像データ量を抑える
        from PIL import Image
        with Image.open(BytesIO(response.content)) as image:
            image = image.convert("RGB")
            image.thumbnail((300, 169), Image.Resampling.LANCZOS)

            compressed = BytesIO()
            image.save(
                compressed,
                format="JPEG",
                quality=72,
                optimize=True,
                progressive=True
            )
            return compressed.getvalue()

    except Exception:
        return None


# データの読み込み
@st.cache_data(ttl=3600, max_entries=1)
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
                            f'<div class="ranking-artist" style="font-size:11px !important; line-height:1.2 !important; font-weight:400 !important; margin-top:3px; color:#B8C0D9;">'
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
                st.error("DBに「アーティスト名」列がありません。")

        else:
            st.error("DBに「曲名」列がありません。")

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
            "例：光、2026、オリ曲、リレー など"
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

    # Clearボタンのコールバック：検索ワードを空にする
    def clear_search_word():
        st.session_state["search_word"] = ""

    with st.form(
        "search_form",
        clear_on_submit=False
    ):

        search_word = st.text_input(
            "🎵 検索ワードを入力してください(部分検索可)",
            placeholder=placeholder,
            key="search_word"
        )

        search_col, clear_col = st.columns([0.01, 0.01], gap="small")
        with search_col:
            search_button = st.form_submit_button(
                "🔍 SEARCH 👇",
                width="content"
            )
        with clear_col:
            clear_button = st.form_submit_button(
                "Clear",
                on_click=clear_search_word,
                width="content"
            )


    # ========================================
    # 🔍 検索実行
    # ========================================

    # ページ切り替え時も、入力済みの検索ワードで結果を再表示する
    if search_button or search_word.strip():

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

                    st.markdown(
                        '<div class="layout-note">※ 表示が乱れた場合は、ページをリロードすると改善することがあります。</div>',
                        unsafe_allow_html=True
                    )

                    # URL列を判定
                    results = results.copy()
                    url_cols = [
                        col for col in results.columns
                        if (
                            "url" in col.lower()
                            or "link" in col.lower()
                            or "リンク" in col
                        )
                    ]

                    # URLをクレンジング
                    for col in url_cols:
                        results[col] = results[col].apply(
                            lambda x: str(x).strip()
                            if pd.notna(x)
                            and str(x).strip().startswith(("http://", "https://"))
                            else None
                        )

                    # URL列から有効なURLを整理
                    def get_row_urls(row):
                        valid_urls = [
                            str(row[col]).strip()
                            for col in url_cols
                            if pd.notna(row[col])
                            and str(row[col]).strip().startswith(("http://", "https://"))
                        ]
                        video_url = next(
                            (url for url in valid_urls if get_youtube_video_id(url)),
                            None
                        )
                        video_id = get_youtube_video_id(video_url) if video_url else None
                        link_url = video_url or (valid_urls[0] if valid_urls else None)
                        return video_id, link_url

                    # 配信日の並び順切替（検索条件ごとに状態を保持）
                    page_key = f"search_page_{search_type}_{search_clean}"
                    sort_key = f"{page_key}_date_ascending"
                    if sort_key not in st.session_state:
                        # 初期表示は新しい順
                        st.session_state[sort_key] = False

                    def toggle_date_sort():
                        st.session_state[sort_key] = not st.session_state[sort_key]
                        # 並び順を変えたら先頭ページへ戻す
                        st.session_state[page_key] = 1

                    sort_label = "新しい順" if not st.session_state[sort_key] else "古い順"
                    # 並び替えボタンと再表示ボタン
                    with st.container(key="date_sort_control"):
                        sort_col, reload_col = st.columns([1, 1], gap="small")
                        with sort_col:
                            st.button(
                                "🔃 SORT",
                                key=f"{page_key}_sort_date_button",
                                width="content",
                                help="新しい順／古い順を切り替え",
                                on_click=toggle_date_sort
                            )
                        with reload_col:
                            if st.button(
                                "↻ RELOAD",
                                key=f"{page_key}_reload_button",
                                width="content",
                                help="画面を再表示します"
                            ):
                                st.rerun()

                    # 年・月・日から日付を作成して並び替え（画像取得・描画処理は変更しない）
                    if all(col in results.columns for col in ["年", "月", "日"]):
                        date_parts = pd.DataFrame({
                            "year": pd.to_numeric(results["年"], errors="coerce"),
                            "month": pd.to_numeric(results["月"], errors="coerce"),
                            "day": pd.to_numeric(results["日"], errors="coerce"),
                        }, index=results.index)
                        sort_dates = pd.to_datetime(date_parts, errors="coerce")
                        results = results.assign(_sort_date=sort_dates).sort_values(
                            by="_sort_date",
                            ascending=st.session_state[sort_key],
                            na_position="last",
                            kind="mergesort"
                        ).drop(columns=["_sort_date"])

                    # 件数が多い場合に一度に描画しない（1ページ20件）
                    page_size = 20
                    total_pages = (len(results) + page_size - 1) // page_size
                    if page_key not in st.session_state:
                        st.session_state[page_key] = 1

                    # 上下共通のページ切替処理
                    def set_search_page(next_page):
                        st.session_state[page_key] = max(1, min(total_pages, int(next_page)))
                        # ページ切り替えでは進捗メッセージを表示しない
                        st.session_state["search_is_paging"] = True

                    page_num = max(1, min(total_pages, int(st.session_state[page_key])))
                    st.session_state[page_key] = page_num

                    # 上部ページ切替（スマホでも1行に固定）
                    with st.container(key="pagination_top"):
                        top_prev_col, top_page_col, top_next_col = st.columns([1, 0.72, 1], gap="small")
                        with top_prev_col:
                            st.button(
                                "← 前へ",
                                key=f"{page_key}_prev_top",
                                disabled=page_num <= 1,
                                width="stretch",
                                on_click=set_search_page,
                                args=(page_num - 1,)
                            )
                        with top_page_col:
                            st.caption(
                                f"ページ {page_num} / {total_pages}",
                                text_alignment="center"
                            )
                        with top_next_col:
                            st.button(
                                "次へ →",
                                key=f"{page_key}_next_top",
                                disabled=page_num >= total_pages,
                                width="stretch",
                                on_click=set_search_page,
                                args=(page_num + 1,)
                            )

                    
                    start_idx = (int(page_num) - 1) * page_size
                    page_results = results.iloc[start_idx:start_idx + page_size]

                    # サムネイルを先に並列取得し、結果カードを一度に描画する。
                    # 代替画像から本画像への差し替えや進捗更新によるレイアウト変動を避ける。
                    row_items = []
                    thumbnail_jobs = {}

                    for row_index, (_, row) in enumerate(page_results.iterrows()):
                        video_id, link_url = get_row_urls(row)
                        item = {
                            "row": row,
                            "video_id": video_id,
                            "link_url": link_url,
                            "thumbnail_data": None,
                        }
                        row_items.append(item)
                        if video_id:
                            thumbnail_jobs[video_id] = None

                    # 【原因切り分け用】サムネイル取得を並列ではなく順番に実行する。
                    # Streamlitのキャッシュ関数をワーカースレッドから呼ぶ処理を避け、
                    # レイアウト崩れが並列取得に関係するか確認する。
                    # 同じ動画IDは一度だけ取得する。
                    for video_id in thumbnail_jobs:
                        try:
                            thumbnail_jobs[video_id] = get_thumbnail(video_id)
                        except Exception:
                            thumbnail_jobs[video_id] = None

                    # 画像取得後にカードを描画し、描画中の差し替えをなくす
                    for card_index, item in enumerate(row_items):
                        row = item["row"]
                        video_id = item["video_id"]
                        link_url = item["link_url"]
                        thumbnail_data = thumbnail_jobs.get(video_id) if video_id else None

                        with st.container(key=f"result_card_{card_index}"):
                            image_col, info_col = st.columns(
                                [1.5, 5.5],
                                vertical_alignment="top"
                            )

                            with image_col:
                                if thumbnail_data is not None:
                                    st.image(BytesIO(thumbnail_data), width="stretch")
                                else:
                                    st.image("thumbnail_default.jpg", width="stretch")
                                if link_url:
                                    st.link_button(
                                        "▶ 視聴",
                                        link_url,
                                        width="stretch"
                                    )

                            with info_col:
                                title_col = None
                                for candidate in ["曲名", "配信タイトル"]:
                                    if candidate in results.columns:
                                        value = row[candidate]
                                        if pd.notna(value) and str(value).strip():
                                            title_col = candidate
                                            break

                                if title_col:
                                    st.markdown(f"**🎵 {row[title_col]}**")

                                if "アーティスト名" in results.columns:
                                    value = row["アーティスト名"]
                                    if pd.notna(value) and str(value).strip():
                                        st.caption(f"🎤 {value}")

                                date_text = ""
                                date_cols = ["年", "月", "日"]
                                if all(col in results.columns for col in date_cols):
                                    year, month, day = row["年"], row["月"], row["日"]
                                    if all(pd.notna(v) for v in [year, month, day]):
                                        date_text = f"📅 {int(year)}/{int(month):02d}/{int(day):02d}"

                                genre_text = ""
                                if "ジャンル" in results.columns:
                                    value = row["ジャンル"]
                                    if pd.notna(value) and str(value).strip():
                                        genre_text = f"🏷️ {value}"

                                if date_text or genre_text:
                                    st.caption("　　".join(part for part in [date_text, genre_text] if part))

                                if "配信タイトル" in results.columns and title_col != "配信タイトル":
                                    value = row["配信タイトル"]
                                    if pd.notna(value) and str(value).strip():
                                        st.caption(f"📺 配信タイトル：{value}")

                                timestamp_col = next(
                                    (col for col in results.columns if "タイムスタンプ" in col or col.lower() in {"timestamp", "time_stamp"}),
                                    None
                                )
                                if timestamp_col:
                                    value = row[timestamp_col]
                                    if pd.notna(value) and str(value).strip() and str(value).strip() not in {"-", "－"}:
                                        st.caption(f"⏱ タイムスタンプ：{value}")

                    # 件数表示中央揃え
                    st.markdown(
                        f'<div style="text-align:center;color:#9CA3AF;font-size:0.85rem;">'
                        f'{start_idx + 1}〜{start_idx + len(page_results)}件目 / 全{len(results)}件'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # 件数表示と下部ページ切替の間には区切り線を表示
                    st.markdown(
                        '<hr style="border:none;border-top:1px solid #303746;margin:10px 0 14px 0;">',
                        unsafe_allow_html=True
                    )

                    # 下部ページ切替（スマホでも1行に固定）
                    with st.container(key="pagination_bottom"):
                        bottom_prev_col, bottom_page_col, bottom_next_col = st.columns([1, 0.72, 1], gap="small")
                        with bottom_prev_col:
                            st.button(
                                "← 前へ",
                                key=f"{page_key}_prev_bottom",
                                disabled=page_num <= 1,
                                width="stretch",
                                on_click=set_search_page,
                                args=(page_num - 1,)
                            )
                        with bottom_page_col:
                            st.caption(
                                f"ページ {page_num} / {total_pages}",
                                text_alignment="center"
                            )
                        with bottom_next_col:
                            st.button(
                                "次へ →",
                                key=f"{page_key}_next_bottom",
                                disabled=page_num >= total_pages,
                                width="stretch",
                                on_click=set_search_page,
                                args=(page_num + 1,)
                            )

                else:
                    st.warning("該当する履歴が見つかりませんでした。")

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