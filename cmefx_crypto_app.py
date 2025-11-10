import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CMEFX Crypto Analyzer", layout="wide")

st.title("CMEFX Crypto Analyzer - Snapshot Version")

# --- Select Profile ---
profile = st.radio("Select Investor Profile:", ["Balanced", "Growth"])
st.write(f"Selected profile: {profile}")

# --- Run Analysis Button ---
if st.button("Run Full Analysis"):
    st.info("Fetching coins and running CMEFX calculations...")

    # Fetch CoinGecko coin list
    cg_coins = requests.get("https://api.coingecko.com/api/v3/coins/markets",
                            params={"vs_currency": "eur", "order": "market_cap_desc", "per_page": 250, "page": 1}).json()
    
    results = []
    for coin in cg_coins:
        # --- K-Score Placeholder Calculation ---
        try:
            k_score = min((coin['market_cap'] / 1e10 + coin['total_volume'] / 1e9 + 3), 5) * 20
        except:
            k_score = 0
        # --- M-Score Placeholder Calculation ---
        m_score = min((coin['circulating_supply'] / 1e8 + 2), 5) * 20
        # --- R-Score Placeholder ---
        r_score = 0.15  # fixed for snapshot
        # --- OTS and RAR ---
        alpha = 0.6 if profile == "Balanced" else 0.4
        ots = k_score * alpha + m_score * (1 - alpha)
        rar_score = ots * (1 - r_score)

        # --- Label ---
        if rar_score >= 85:
            label = "Elite"
        elif rar_score >= 70:
            label = "Very Strong"
        elif rar_score >= 55:
            label = "Strong"
        elif rar_score >= 40:
            label = "Acceptable"
        else:
            label = "Weak"

        results.append({
            "Name": coin['name'],
            "Ticker": coin['symbol'].upper(),
            "Current Price (€)": coin.get('current_price', 0),
            "K-Score": round(k_score,1),
            "M-Score": round(m_score,1),
            "R-Score": round(r_score,4),
            "RAR-Score": round(rar_score,1),
            "Label": label,
            "Snapshot UTC": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(results).sort_values(by="RAR-Score", ascending=False).reset_index(drop=True)
    
    # --- Display Table ---
    st.subheader("CMEFX Crypto Ranking")
    st.dataframe(df[["Name","Ticker","Current Price (€)","K-Score","M-Score","RAR-Score","Label","Snapshot UTC"]])

    # --- Select Coin for Full Report ---
    st.subheader("Select Coin for Full CMEFX Report")
    coin_selection = st.selectbox("Select Coin", df["Name"])
    selected = df[df["Name"] == coin_selection].iloc[0]

    st.markdown(f"""
    ### CMEFX Full Report
    **Name:** {selected['Name']}  
    **Ticker:** {selected['Ticker']}  
    **Current Price:** €{selected['Current Price (€)']}  
    **K-Score:** {selected['K-Score']}  
    **M-Score:** {selected['M-Score']}  
    **R-Score:** {selected['R-Score']}  
    **RAR-Score:** {selected['RAR-Score']}  
    **Label:** {selected['Label']}  
    **Snapshot UTC:** {selected['Snapshot UTC']}  
    """)
    st.markdown("""
    **Detailed CMEFX explanations and calculations:**  
    (This is a momentary snapshot. Placeholder explanations can later be replaced with full per-criterion CMEFX analysis.)  
    - K-Score calculated from Market Cap, Volume, and placeholder network usage  
    - M-Score calculated from Circulating Supply and placeholder adoption metrics  
    - R-Score fixed placeholder 0.15 for snapshot  
    - OTS and RAR calculated per CMEFX formula with profile weightings  
    - Full per-criterion data, GitHub activity, audits, sentiment, on-chain metrics can later be integrated
    """)

