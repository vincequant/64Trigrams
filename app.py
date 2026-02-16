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


def show_hexagram_image(hexagram_name: str):
    image_name = normalize_hexagram_filename(hexagram_name)
    image_path = IMAGE_DIR / f"{image_name}.jpg"
    if image_path.exists():
        st.image(str(image_path), caption=hexagram_name, use_container_width=True)
    else:
        st.error(f"找不到插图：{image_name}.jpg")


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
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="element-container"]:has(img) img {
            max-height: 84vh;
            width: auto;
            margin: 0 auto;
            object-fit: contain;
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
    show_hexagram_image(hexagram_name)
else:
    st.warning(f"未找到对应卦（key: {key}）")
