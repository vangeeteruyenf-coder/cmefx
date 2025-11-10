# cmefx_crypto_app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CMEFX scoring helpers ---
def calculate_k_score(coin):
    # voorbeeldberekening gebaseerd op CoinGecko data
    try:
        market_cap_score = min(coin.get('market_cap',0)/1e10,5)
        volume_score = min(coin.get('total_volume',0)/1e9,5)
    except:
        market_cap_score = 0
        volume_score = 0
    team_score = 3  # placeholder
    adoption_score = 3  # placeholder
    weighted_sum = 0.15*market_cap_score + 0.10*volume_score + 0.08*team_score + 0.10*adoption_score
    k_score = weighted_sum*20  # percentage
    return round(k_score,1)

def calculate_m_score(coin):
    # placeholder, hier kan GitHub, social, trends toegevoegd worden
    m_score = 50 + (coin.get('market_cap',0)/1e11)*10
    return round(min(m_score,100),1)

def calculate_r_score(coin):
    # simpele risico inschatting
    return round(0.15,4)

def calculate_rar_score(k,m,r,profile='Balanced'):
    alpha = 0.6 if profile=='Balanced' else 0.4
    ots = k*alpha + m*(1-alpha)
    rar = ots*(1-r)
    return round(rar,1)

def qualitative_label(score):
    if score >=85:
        return "Elite"
    elif score>=70:
        return "Very Strong"
    elif score>=55:
        return "Strong"
    elif score>=40:
        return "Acceptable"
    else:
        return "Weak"

# --- Streamlit App ---
st.title("CMEFX Crypto Analyzer")

# Profiel keuze
profile = st.selectbox("Select Investor Profile", ["Balanced", "Growth"])
st.write(f"Selected profile: {profile}")

# Analyse knop
if st.button("Run Full Analysis"):
    # CoinGecko API ophalen
    st.info("Fetching coins from CoinGecko...")
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency":"eur","order":"market_cap_desc","per_page":250,"page":1}
    response = requests.get(url, params=params)
    coins_data = response.json()
    
    # Berekeningen
    results = []
    for coin in coins_data:
        k = calculate_k_score(coin)
        m = calculate_m_score(coin)
        r = calculate_r_score(coin)
        rar = calculate_rar_score(k,m,r,profile)
        label = qualitative_label(rar)
        results.append({
            "Name": coin.get('name',''),
            "Ticker": coin.get('symbol','').upper(),
            "Price (€)": coin.get('current_price',0),
            "K-Score": k,
            "M-Score": m,
            "R-Score": r,
            "RAR-Score": rar,
            "Label": label,
            "Coin Data": coin  # bewaar voor uitgebreid rapport
        })
    
    # Dataframe en sorteren
    df = pd.DataFrame(results)
    df.sort_values(by="RAR-Score", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Tabelweergave
    st.subheader("Crypto Ranking Table")
    st.dataframe(df[["Name","Ticker","Price (€)","K-Score","M-Score","RAR-Score","Label"]])
    
    # Uitgebreid rapport per coin
    st.subheader("Full CMEFX Report")
    selected_coin_name = st.selectbox("Select Coin for Full Report", df["Name"])
    coin_info = df[df["Name"]==selected_coin_name].iloc[0]
    
    st.write(f"**Name:** {coin_info['Name']}")
    st.write(f"**Ticker:** {coin_info['Ticker']}")
    st.write(f"**Current Price (€):** {coin_info['Price (€)']}")
    st.write(f"**K-Score:** {coin_info['K-Score']}")
    st.write(f"**M-Score:** {coin_info['M-Score']}")
    st.write(f"**R-Score:** {coin_info['R-Score']}")
    st.write(f"**RAR-Score:** {coin_info['RAR-Score']}")
    st.write(f"**Label:** {coin_info['Label']}")
    
    # Hier kan je volledige CMEFX uitleg toevoegen
    st.markdown("### Detailed CMEFX Explanations and Calculations")
    st.markdown(f"- **K-Score:** calculated from market cap, volume, adoption, team metrics (see coin JSON below)")
    st.markdown(f"- **M-Score:** based on long-term potential (innovation, adoption, network)")
    st.markdown(f"- **R-Score:** technical/regulatory/volatility risk factor")
    st.markdown(f"- **RAR-Score:** Risk-adjusted score combining K, M, and R")
    st.markdown("#### Coin raw data snapshot (UTC):")
    st.json(coin_info["Coin Data"])
    
    # Datum en uur van opvraging
    st.write("**Snapshot UTC:**", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
