# 64Trigrams (Zelda Images)

Core features:
- Select upper and lower trigrams.
- Show corresponding Zelda-style hexagram image.
- Random button to get a random hexagram image.

## Run locally

```bash
cd /Users/vk/Documents/Coding/64Trigrams
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` on your iPhone 15 Pro Max browser.

## Deploy later (GitHub + Streamlit)

- Push this folder to GitHub.
- In Streamlit Community Cloud, set:
  - Main file path: `app.py`
  - Python dependencies: `requirements.txt`
