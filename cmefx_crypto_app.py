# cmefx_crypto_app_safe.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CMEFX Crypto Analyzer", layout="wide")

# -----------------------------
# Helper Functions
# -----------------------------

def safe_get(coin, key, default=0):
    """Veilige manier om waarden op te halen uit coin dict"""
    value = coin.get(key, default)
    if value is None:
        return default
    return value

def fetch_coins():
    """Haal lijst van alle coins van CoinGecko als voorbeeld (Bitvavo kan ook via scrape/public endpoint)"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "eur", "order": "market_cap_desc", "per_page": 250, "page": 1}
    try:
        response = requests.get(url, params=params)
        coins = response.json()
        return coins
    except Exception as e:
        st.error(f"Error fetching coins: {e}")
        return []

def calculate_k_score(coin):
    """K-Score calculation (safely)"""
    # Safely get values
    price = safe_get(coin, 'current_price')
    market_cap = safe_get(coin, 'market_cap')
    total_volume = safe_get(coin, 'total_volume')

    adoption_score = min(total_volume / 1e8, 5)
    liquidity_score = min(market_cap / 1e9, 5)
    team_score = 3  # placeholder
    security_score = 3 # placeholder

    # Weights (%)
    weights = [15,10,10,10,8,8,7,7,7,5,5,3,3,2,2]
    # Simplified scores for demo
    scores = [adoption_score, liquidity_score, 4, adoption_score, liquidity_score,
              team_score, security_score, 3,3,3,3,2,2,1,1]
    weighted = [w/100*s for w,s in zip(weights,scores)]
    k_score = sum(weighted)*20
    return round(k_score,1)

def calculate_m_score(coin):
    """M-Score calculation (safely)"""
    innovation = 4
    adoption = 3
    network_effect = 3
    weights = [15,15,10,10,10,10,10,5,5,5]
    scores = [innovation, adoption, network_effect, 3,3,3,3,2,2,1]
    weighted = [w/100*s for w,s in zip(weights,scores)]
    m_score = sum(weighted)*20
    return round(m_score,1)

def calculate_r_score(coin):
    """R-Score calculation (safely)"""
    tech_risk = 0.2
    legal_risk = 0.1
    financial_risk = 0.15
    r_score = tech_risk*0.4 + legal_risk*0.35 + financial_risk*0.25
    return round(r_score,4)

def calculate_rar_score(k,m,r,profile):
    """RAR-Score calculation"""
    if profile == "Balanced":
        alpha = 0.6
    else:
        alpha = 0.4
    ots = k*alpha + m*(1-alpha)
    rar = ots*(1-r)
    return round(rar,1)

def qualitative_label(score):
    if score >= 85:
        return "Elite"
    elif score >= 70:
        return "Very Strong"
    elif score >= 55:
        return "Strong"
    elif score >= 40:
        return "Acceptable"
    else:
        return "Weak"

# -----------------------------
# Streamlit UI
# -----------------------------

st.title("CMEFX Crypto Analyzer - Safe Version")

profile = st.selectbox("Select Investor Profile", ["Balanced", "Growth"])
st.write(f"Selected profile: {profile}")

if st.button("Run Full Analysis"):
    coins = fetch_coins()
    if not coins:
        st.warning("No coins fetched.")
    else:
        st.info(f"Fetched {len(coins)} coins. Running CMEFX calculations...")
        data = []
        for coin in coins:
            k = calculate_k_score(coin)
            m = calculate_m_score(coin)
            r = calculate_r_score(coin)
            rar = calculate_rar_score(k,m,r,profile)
            label = qualitative_label(rar)
            data.append({
                "Name": safe_get(coin,'name'),
                "Ticker": safe_get(coin,'symbol').upper(),
                "Current Price (€)": safe_get(coin,'current_price'),
                "K-Score": k,
                "M-Score": m,
                "R-Score": r,
                "RAR-Score": rar,
                "Label": label
            })
        df = pd.DataFrame(data)
        df = df.sort_values(by="RAR-Score", ascending=False).reset_index(drop=True)
        df.index +=1
        st.dataframe(df)

        # Detailed report per coin
        st.write("Click a coin to see detailed CMEFX report:")
        selected_coin = st.selectbox("Select Coin for Full Report", df["Name"])
        coin_info = df[df["Name"]==selected_coin].iloc[0]
        st.write("## CMEFX Full Report")
        st.write(f"Name: {coin_info['Name']}")
        st.write(f"Ticker: {coin_info['Ticker']}")
        st.write(f"Current Price: €{coin_info['Current Price (€)']}")
        st.write(f"K-Score: {coin_info['K-Score']}")
        st.write(f"M-Score: {coin_info['M-Score']}")
        st.write(f"R-Score: {coin_info['R-Score']}")
        st.write(f"RAR-Score: {coin_info['RAR-Score']}")
        st.write(f"Label: {coin_info['Label']}")
        st.write("Detailed CMEFX explanations and calculations would appear here (placeholder).")
