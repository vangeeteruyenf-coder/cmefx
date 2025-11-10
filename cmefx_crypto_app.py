# cmefx_crypto_app.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="CMEFX Crypto Analyzer", layout="wide")

st.title("CMEFX Crypto Analyzer - Momentopname")

# -------------------------------
# 1️⃣ Profiel keuze
# -------------------------------
profile = st.selectbox("Select Investor Profile", ["Balanced", "Growth"])
st.write(f"Selected profile: {profile}")

# -------------------------------
# 2️⃣ Haal lijst van coins op
# -------------------------------
@st.cache_data(show_spinner=False)
def fetch_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "eur", "order": "market_cap_desc", "per_page": 250, "page": 1, "sparkline": False}
    response = requests.get(url, params=params)
    return response.json()

coins_raw = fetch_coin_list()
st.write(f"Fetched {len(coins_raw)} coins. Running CMEFX calculations...")

# -------------------------------
# 3️⃣ Bereken scores (safe version)
# -------------------------------
def calculate_k_score(coin):
    try:
        adoption_score = min(coin['total_volume']/1e8,5)
        market_score = min(coin['market_cap']/1e10,5)
        k = round((adoption_score + market_score + 5)/3,1)  # simplified safe K
        return min(k, 100)
    except:
        return 0

def calculate_m_score(coin):
    try:
        m = round((coin['price_change_percentage_30d_in_currency'] if coin.get('price_change_percentage_30d_in_currency') else 0)/5 + 2.5,1)
        return min(max(m,0),5)*20
    except:
        return 0

def calculate_r_score(coin):
    # Simplified placeholder risk
    return round(0.15,4)

def calculate_rar_score(k,m,r,profile):
    alpha = 0.6 if profile=="Balanced" else 0.4
    ots = (k*alpha) + (m*(1-alpha))
    rar = ots*(1-r)
    return round(rar,1)

# -------------------------------
# 4️⃣ Verwerk alle coins
# -------------------------------
coins_data = []
utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

for i, coin in enumerate(coins_raw):
    k = calculate_k_score(coin)
    m = calculate_m_score(coin)
    r = calculate_r_score(coin)
    rar = calculate_rar_score(k,m,r,profile)
    if rar >=85:
        label="Elite"
    elif rar>=70:
        label="Very Strong"
    elif rar>=55:
        label="Strong"
    elif rar>=40:
        label="Acceptable"
    else:
        label="Weak"
    coins_data.append({
        "NR": i+1,
        "Name": coin['name'],
        "Ticker": coin['symbol'].upper(),
        "Price": round(coin['current_price'],2),
        "Timestamp": utc_now,
        "K": k,
        "M": m,
        "R": r,
        "RAR": rar,
        "Label": label
    })

df = pd.DataFrame(coins_data)
df = df.sort_values(by="RAR", ascending=False).reset_index(drop=True)
df["NR"] = df.index +1

# -------------------------------
# 5️⃣ Toon tabel
# -------------------------------
st.subheader("All Coins Ranked by RAR-Score")
st.dataframe(df[["NR","Name","Ticker","Price","Timestamp","K","M","RAR","Label"]])

# -------------------------------
# 6️⃣ Volledig rapport per coin
# -------------------------------
selected_coin = st.selectbox("Select Coin for Full Report", df["Name"])
coin_report = df[df["Name"]==selected_coin].iloc[0]

st.subheader(f"CMEFX Full Report - {coin_report['Name']}")
st.write(f"Name: {coin_report['Name']}")
st.write(f"Ticker: {coin_report['Ticker']}")
st.write(f"Current Price: €{coin_report['Price']}")
st.write(f"Data retrieved: {coin_report['Timestamp']}")
st.write(f"K-Score: {coin_report['K']}")
st.write(f"M-Score: {coin_report['M']}")
st.write(f"R-Score: {coin_report['R']}")
st.write(f"RAR-Score: {coin_report['RAR']}")
st.write(f"Label: {coin_report['Label']}")

st.markdown("### Detailed CMEFX explanations and calculations")
st.markdown("*(This is a momentary snapshot. Placeholder explanations can later be replaced with full per-criterion CMEFX analysis.)*")
