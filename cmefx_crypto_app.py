import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="CMEFX Crypto Analyzer", layout="wide")
st.title("CMEFX Crypto Analyzer - Full Table & Detailed Reports")

# --- CMEFX Functies ---

def fetch_bitvavo_coins():
    url = "https://api.bitvavo.com/v2/markets"
    response = requests.get(url)
    markets = response.json()
    coins = []
    seen = set()
    for m in markets:
        symbol = m['market'].split('-')[0]
        if symbol not in seen:
            coins.append(symbol)
            seen.add(symbol)
    return coins

def fetch_coingecko_data(ticker):
    gecko_list = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
    coin_id = next((c['id'] for c in gecko_list if c['symbol'].upper()==ticker.upper()), None)
    if not coin_id:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=true&developer_data=true&sparkline=false"
    data = requests.get(url).json()
    return data

def qualitative_label(score):
    if score>=85:
        return "Elite"
    elif score>=70:
        return "Very Strong"
    elif score>=55:
        return "Strong"
    elif score>=40:
        return "Acceptable"
    else:
        return "Weak"

# --- K-Score (15 criteria) ---
def calculate_k_score(data):
    k_table = []
    total_weighted = 0
    criteria = [
        ("Use Case & Network Moat", 15),
        ("Tokenomics & Circulation", 10),
        ("Technology & Scalability", 10),
        ("Adoption, Usage & Metrics", 10),
        ("Market & Liquidity", 8),
        ("Team & Developers", 8),
        ("Security & Audits", 7),
        ("Community & Network Effect", 7),
        ("Governance & Decentralization", 7),
        ("Ecosystem & Integration", 5),
        ("Roadmap & Feasibility", 5),
        ("Legal & ESG", 3),
        ("Macro Factors",3),
        ("Marketing & Awareness",2),
        ("Historical Performance",2)
    ]
    
    for name, weight in criteria:
        # Score = placeholder op basis van data (max 5)
        score = min((hash(name+data['id'])%6),5)  # 0-5
        weighted = round(score * (weight/100),4)
        total_weighted += weighted
        k_table.append({
            "Criterion": name,
            "Weight": weight,
            "Score": score,
            "Weighted": weighted,
            "Motivation": f"Auto-calculated placeholder for {name}",
            "Source": "CoinGecko"
        })
    k_percent = round(total_weighted*20,1)
    return k_percent, k_table

# --- M-Score (10 criteria) ---
def calculate_m_score(data):
    m_table = []
    total_weighted = 0
    criteria = [
        ("Innovation & Disruptive Power",15),
        ("Global Adoption Potential",15),
        ("Competitive Barriers",10),
        ("Future-Proof Scalability",10),
        ("Long-Term Incentives",10),
        ("Viral Network Effects",10),
        ("True Censorship Resistance",10),
        ("Macro Trends & Timing",5),
        ("Founders' Track Record",5),
        ("Branding & Sentiment",5)
    ]
    for name, weight in criteria:
        score = min((hash(name+data['id'])%6),5)
        weighted = round(score * (weight/100),4)
        total_weighted += weighted
        m_table.append({
            "Criterion": name,
            "Weight": weight,
            "Score": score,
            "Weighted": weighted,
            "Motivation": f"Auto-calculated placeholder for {name}",
            "Source": "CoinGecko"
        })
    m_percent = round(total_weighted*20,1)
    return m_percent, m_table

# --- R-Score & RAR ---
def calculate_r_score(data):
    # Placeholder 0-1
    return round(0.15,4)

def calculate_ots_rar(k,m,r,profile):
    alpha = 0.6 if profile=='Balanced' else 0.4
    ots = k*alpha + m*(1-alpha)
    rar = ots*(1-r)
    return round(ots,1), round(rar,1)

# --- UI ---
profile = st.selectbox("Select Investor Profile", ["Balanced","Growth"])
st.write(f"Selected profile: {profile}")

if st.button("Run Full Analysis"):
    st.info("Fetching coins and running CMEFX calculations...")
    coins = fetch_bitvavo_coins()
    st.write(f"Fetched {len(coins)} coins.")
    
    results = []
    snapshot_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    for coin in coins:
        data = fetch_coingecko_data(coin)
        if not data:
            continue
        price = data['market_data']['current_price'].get('eur',0)
        k, k_table = calculate_k_score(data)
        m, m_table = calculate_m_score(data)
        r = calculate_r_score(data)
        ots, rar = calculate_ots_rar(k,m,r,profile)
        label = qualitative_label(rar)
        
        details = {
            "K-Score Table": k_table,
            "M-Score Table": m_table,
            "R-Score": r,
            "OTS": ots,
            "RAR": rar,
            "Snapshot": snapshot_time
        }
        results.append({
            "Name": coin,
            "Ticker": coin,
            "Price": price,
            "K": k,
            "M": m,
            "RAR": rar,
            "Label": label,
            "Details": details
        })
    
    df = pd.DataFrame(results)
    df = df.sort_values(by='RAR',ascending=False).reset_index(drop=True)
    df.index += 1  # NR
    
    st.subheader("Crypto Rankings")
    st.dataframe(df[['Name','Ticker','Price','K','M','RAR','Label']],height=400)
    
    selected_coin = st.selectbox("Select Coin for Full CMEFX Report", df["Name"])
    coin_row = df[df["Name"]==selected_coin].iloc[0]
    
    st.subheader(f"Full CMEFX Report - {selected_coin}")
    st.write(f"Price: €{coin_row['Price']}")
    st.write(f"K: {coin_row['K']}, M: {coin_row['M']}, RAR: {coin_row['RAR']}, Label: {coin_row['Label']}")
    st.write("**Detailed CMEFX Explanations & Calculations**")
    st.json(coin_row["Details"])
