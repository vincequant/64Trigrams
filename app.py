import base64
import json
import random
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="64 Trigrams Zelda", page_icon="🧿", layout="wide")

ROOT = Path(__file__).parent
HEXAGRAMS_PATH = ROOT / "hexagrams.json"
IMAGE_DIR = ROOT / "assets" / "zelda64"

TRIGRAM_TO_BITS = {
    "乾 (天)": "111",
    "兌 (澤)": "011",
    "離 (火)": "101",
    "震 (雷)": "001",
    "巽 (風)": "110",
    "坎 (水)": "010",
    "艮 (山)": "100",
    "坤 (地)": "000",
}
BITS_TO_TRIGRAM = {v: k for k, v in TRIGRAM_TO_BITS.items()}
TRIGRAM_OPTIONS = list(TRIGRAM_TO_BITS.keys())


def normalize_hexagram_filename(name: str) -> str:
    return name.replace("无妄", "無妄")


@st.cache_data
def load_hexagrams() -> dict[str, str]:
    return json.loads(HEXAGRAMS_PATH.read_text(encoding="utf-8"))


def get_hexagram_key(upper: str, lower: str) -> str:
    return TRIGRAM_TO_BITS[upper] + TRIGRAM_TO_BITS[lower]


@st.cache_data
def image_to_data_uri(image_path: str) -> str:
    data = Path(image_path).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def show_hexagram_image(hexagram_name: str, hexagram_key: str):
    image_name = normalize_hexagram_filename(hexagram_name)
    image_path = IMAGE_DIR / f"{image_name}.jpg"
    if not image_path.exists():
        st.error(f"找不到插图：{image_name}.jpg")
        return

    modal_id = f"hex-modal-{hexagram_key}"
    data_uri = image_to_data_uri(str(image_path))
    html = f"""
    <div class="viewer-wrap">
        <a class="viewer-thumb-link" href="#{modal_id}" aria-label="打開全屏圖片">
            <img class="viewer-thumb" src="{data_uri}" alt="{hexagram_name}">
        </a>
        <div id="{modal_id}" class="viewer-modal" aria-hidden="true">
            <a href="#" class="viewer-backdrop" aria-label="關閉"></a>
            <img class="viewer-modal-img" src="{data_uri}" alt="{hexagram_name}">
            <a href="#" class="viewer-close" aria-label="關閉">×</a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.caption("点击图片可全屏；竖屏时会自动横向旋转显示。")


st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 0.45rem;
        padding-bottom: 0.5rem;
        max-width: 100%;
    }
    h1 {
        font-size: 1.2rem !important;
        margin-bottom: 0.15rem !important;
    }
    [data-testid="stCaptionContainer"] {
        margin-bottom: 0.25rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.62rem 0.8rem;
    }
    .portrait-tip {
        display: block;
        margin: 0 0 0.4rem 0;
        padding: 0.45rem 0.65rem;
        border-radius: 10px;
        background: #fff7ed;
        border: 1px solid #fdba74;
        color: #9a3412;
        font-size: 0.86rem;
    }
    .viewer-wrap {
        width: 100%;
    }
    .viewer-thumb-link {
        display: block;
        width: 100%;
    }
    .viewer-thumb {
        width: 100%;
        height: auto;
        border-radius: 12px;
        display: block;
        cursor: zoom-in;
    }
    .viewer-modal {
        display: none;
        position: fixed;
        inset: 0;
        z-index: 99999;
    }
    .viewer-modal:target {
        display: block;
    }
    .viewer-backdrop {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.88);
    }
    .viewer-modal-img {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        max-width: 98vw;
        max-height: 98vh;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 10px;
        box-shadow: 0 16px 50px rgba(0,0,0,0.45);
    }
    .viewer-close {
        position: absolute;
        right: 14px;
        top: 10px;
        width: 40px;
        height: 40px;
        border-radius: 999px;
        text-decoration: none;
        background: rgba(15, 23, 42, 0.85);
        color: #fff;
        font-size: 28px;
        line-height: 36px;
        text-align: center;
    }

    @media (orientation: portrait) {
        .viewer-modal-img {
            transform: translate(-50%, -50%) rotate(90deg);
            max-width: 96vh;
            max-height: 96vw;
            border-radius: 8px;
        }
    }

    @media (orientation: landscape) {
        .portrait-tip {
            display: none;
        }
        .main .block-container {
            padding-top: 0.25rem;
            padding-bottom: 0.3rem;
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("六十四卦·塞尔达插图")
st.caption("横屏优先：iPhone 15 Pro Max 建议旋转到横屏查看。")
st.markdown('<div class="portrait-tip">建议横屏查看：插图会更大更清晰。</div>', unsafe_allow_html=True)

hexagrams = load_hexagrams()

if "upper" not in st.session_state:
    st.session_state.upper = TRIGRAM_OPTIONS[0]
if "lower" not in st.session_state:
    st.session_state.lower = TRIGRAM_OPTIONS[0]

with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1, 0.9])
    with c1:
        upper = st.selectbox("上卦", TRIGRAM_OPTIONS, index=TRIGRAM_OPTIONS.index(st.session_state.upper))
    with c2:
        lower = st.selectbox("下卦", TRIGRAM_OPTIONS, index=TRIGRAM_OPTIONS.index(st.session_state.lower))
    with c3:
        st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
        if st.button("随机一卦", use_container_width=True):
            random_key = random.choice(list(hexagrams.keys()))
            st.session_state.upper = BITS_TO_TRIGRAM[random_key[:3]]
            st.session_state.lower = BITS_TO_TRIGRAM[random_key[3:]]
            st.rerun()

    st.session_state.upper = upper
    st.session_state.lower = lower

key = get_hexagram_key(st.session_state.upper, st.session_state.lower)
hexagram_name = hexagrams.get(key)

if hexagram_name:
    st.subheader(hexagram_name)
    show_hexagram_image(hexagram_name, key)
else:
    st.warning(f"未找到对应卦（key: {key}）")
