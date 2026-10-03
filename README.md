# Earnings Call Prep Room (Streamlit)
Synthetic data (Meridian Industrial Ltd, INR crore). Optional AI coach via ANTHROPIC_API_KEY.

## Run locally
pip install -r requirements.txt
streamlit run app.py

## Deploy (Streamlit Community Cloud)
1. Push app.py and requirements.txt to a GitHub repo.
2. share.streamlit.io -> New app -> pick repo, branch, app.py.
3. (Optional) Settings -> Secrets: ANTHROPIC_API_KEY = "sk-ant-..."
