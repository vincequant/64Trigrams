import base64
import json
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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
    file_name = f"{image_name}.jpg"
    html = f"""
    <div class="viewer-wrap">
        <a class="viewer-thumb-link" href="#{modal_id}" aria-label="打開全屏圖片">
            <img class="viewer-thumb" src="{data_uri}" alt="{hexagram_name}">
        </a>
        <div id="{modal_id}" class="viewer-modal" aria-hidden="true">
            <a href="#" class="viewer-backdrop" aria-label="關閉"></a>
            <div class="viewer-modal-stage" id="{modal_id}-stage">
                <div class="viewer-zoom-layer" id="{modal_id}-zoom">
                    <img class="viewer-modal-img" src="{data_uri}" alt="{hexagram_name}">
                </div>
            </div>
            <div class="viewer-actions">
                <a class="viewer-action-btn viewer-action-download" href="{data_uri}" download="{file_name}">下载到相册</a>
            </div>
            <a href="#" class="viewer-close" aria-label="關閉">×</a>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    components.html(
        f"""
        <script>
        (function () {{
          const modal = parent.document.getElementById("{modal_id}");
          if (!modal || modal.dataset.zoomReady === "1") return;
          const stage = parent.document.getElementById("{modal_id}-stage");
          const zoomLayer = parent.document.getElementById("{modal_id}-zoom");
          if (!stage || !zoomLayer) return;
          modal.dataset.zoomReady = "1";

          let scale = 1;
          let tx = 0;
          let ty = 0;
          let mode = "";
          let startX = 0;
          let startY = 0;
          let startTx = 0;
          let startTy = 0;
          let startScale = 1;
          let startDist = 0;
          let startMidX = 0;
          let startMidY = 0;
          const minScale = 1;
          const maxScale = 4;

          function clamp(v, min, max) {{
            return Math.min(max, Math.max(min, v));
          }}

          function touchDist(t1, t2) {{
            return Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
          }}

          function apply() {{
            zoomLayer.style.transform = `translate(${{tx}}px, ${{ty}}px) scale(${{scale}})`;
          }}

          function reset() {{
            scale = 1;
            tx = 0;
            ty = 0;
            mode = "";
            apply();
          }}

          stage.addEventListener("touchstart", function (e) {{
            if (e.touches.length === 2) {{
              mode = "pinch";
              startScale = scale;
              startDist = touchDist(e.touches[0], e.touches[1]);
              startMidX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
              startMidY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
              startTx = tx;
              startTy = ty;
            }} else if (e.touches.length === 1 && scale > 1) {{
              mode = "pan";
              startX = e.touches[0].clientX;
              startY = e.touches[0].clientY;
              startTx = tx;
              startTy = ty;
            }}
          }}, {{ passive: false }});

          stage.addEventListener("touchmove", function (e) {{
            if (mode === "pinch" && e.touches.length === 2) {{
              e.preventDefault();
              const currentDist = touchDist(e.touches[0], e.touches[1]);
              const nextScale = clamp(startScale * (currentDist / Math.max(startDist, 1)), minScale, maxScale);
              const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
              const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
              tx = startTx + (midX - startMidX);
              ty = startTy + (midY - startMidY);
              scale = nextScale;
              apply();
            }} else if (mode === "pan" && e.touches.length === 1) {{
              e.preventDefault();
              tx = startTx + (e.touches[0].clientX - startX);
              ty = startTy + (e.touches[0].clientY - startY);
              apply();
            }}
          }}, {{ passive: false }});

          stage.addEventListener("touchend", function (e) {{
            if (e.touches.length === 0) {{
              mode = "";
            }} else if (e.touches.length === 1 && scale > 1) {{
              mode = "pan";
              startX = e.touches[0].clientX;
              startY = e.touches[0].clientY;
              startTx = tx;
              startTy = ty;
            }}
            if (scale <= 1) {{
              tx = 0;
              ty = 0;
              scale = 1;
              apply();
            }}
          }});

          parent.window.addEventListener("hashchange", function () {{
            if (parent.window.location.hash !== "#{modal_id}") {{
              reset();
            }}
          }});
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
    st.caption("点击图片可全屏；可直接双指拉伸缩放，单指拖动查看，支持“下载到相册”。")


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
        overflow: auto;
        -webkit-overflow-scrolling: touch;
        touch-action: pinch-zoom;
    }
    .viewer-modal:target {
        display: block;
    }
    .viewer-backdrop {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.88);
    }
    .viewer-modal-stage {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: auto;
        padding: 56px 10px 82px;
        -webkit-overflow-scrolling: touch;
        touch-action: none;
    }
    .viewer-zoom-layer {
        transform: translate(0, 0) scale(1);
        transform-origin: center center;
        will-change: transform;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .viewer-modal-img {
        width: min(92vw, 1800px);
        max-width: min(92vw, 1800px);
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
        z-index: 2;
    }
    .viewer-actions {
        position: absolute;
        left: 12px;
        right: 12px;
        bottom: 12px;
        z-index: 2;
        display: block;
    }
    .viewer-action-btn {
        display: inline-block;
        text-align: center;
        text-decoration: none;
        background: rgba(15, 23, 42, 0.9);
        color: #fff;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 9px 10px;
        font-weight: 600;
        font-size: 0.92rem;
        width: 100%;
        box-sizing: border-box;
    }
    .viewer-action-download {
        background: #0369a1;
        border-color: #0ea5e9;
    }

    @media (orientation: portrait) {
        .viewer-modal-img {
            transform: rotate(90deg);
            width: min(140vh, 1400px);
            max-width: min(140vh, 1400px);
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
    @media (orientation: landscape) and (max-width: 900px) {
        .viewer-modal-img {
            width: min(160vw, 1800px);
            max-width: min(160vw, 1800px);
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
