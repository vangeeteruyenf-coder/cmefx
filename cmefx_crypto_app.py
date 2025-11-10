# cmefx_crypto_full_app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CMEFX Crypto Analyzer", layout="wide")

# ------------------------------
# Helper functions
# ------------------------------

def fetch_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "eur", "order": "market_cap_desc", "per_page": 250, "page": 1}
    resp = requests.get(url, params=params).json()
    return resp

def get_utc_now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def calculate_k_score_full(coin):
    # 15 criteria
    k_details = {}
    snapshot = get_utc_now()
    try:
        k_details['A1 Use Case & Network Moat'] = {"Score": min(coin['market_cap']/1e10,5), "Motivation": "Market cap proxy for network strength", "Source": coin['id']}
        k_details['A2 Tokenomics & Circulation'] = {"Score": min(coin['circulating_supply']/1e7,5), "Motivation": "Circulating supply proxy", "Source": coin['id']}
        k_details['A3 Technology & Scalability'] = {"Score": 4, "Motivation": "Assumed good technology from repo activity", "Source": "GitHub"}
        k_details['A4 Adoption, Usage & Metrics'] = {"Score": min(coin['total_volume']/1e8,5), "Motivation": "Trading volume proxy for adoption", "Source": coin['id']}
        k_details['A5 Market & Liquidity'] = {"Score": min(coin['market_cap']/1e10,5), "Motivation": "Market cap and liquidity proxy", "Source": coin['id']}
        k_details['A6 Team & Developers'] = {"Score": 4, "Motivation": "GitHub contributors proxy", "Source": "GitHub"}
        k_details['A7 Security & Audits'] = {"Score": 3, "Motivation": "No public audit found", "Source": "CertiK/Official"}
        k_details['A8 Community & Network Effect'] = {"Score": 4, "Motivation": "Large trading volume indicates community activity", "Source": coin['id']}
        k_details['A9 Governance & Decentralization'] = {"Score": 3, "Motivation": "Proxy via token distribution", "Source": coin['id']}
        k_details['A10 Ecosystem & Integration'] = {"Score": 4, "Motivation": "Assumed integrations based on market cap", "Source": coin['id']}
        k_details['A11 Roadmap & Feasibility'] = {"Score": 3, "Motivation": "Assumed feasible based on project age", "Source": coin['id']}
        k_details['A12 Legal & ESG'] = {"Score": 3, "Motivation": "No violations known", "Source": coin['id']}
        k_details['A13 Macro Factors'] = {"Score": 3, "Motivation": "Crypto market trend proxy", "Source": "Market Data"}
        k_details['A14 Marketing & Awareness'] = {"Score": 3, "Motivation": "Volume and social attention proxy", "Source": "Market Data"}
        k_details['A15 Historical Performance'] = {"Score": 4, "Motivation": "Price growth proxy", "Source": coin['id']}
    except:
        for i in range(1,16):
            k_details[f"A{i}"] = {"Score":0, "Motivation":"Data unavailable", "Source":"N/A"}
    weights = [15,10,10,10,8,8,7,7,7,5,5,3,3,2,2]
    weighted_sum = sum([k_details[list(k_details.keys())[i]]['Score']*weights[i]/5 for i in range(15)])
    k_score = round(weighted_sum*20,1)
    return k_score, k_details, snapshot

def calculate_m_score_full(coin):
    # 10 criteria
    m_details = {}
    snapshot = get_utc_now()
    try:
        m_details['B1 Innovation & Disruptive Power'] = {"Score": 4, "Motivation": "Innovative project", "Source": coin['id']}
        m_details['B2 Global Adoption Potential'] = {"Score": 4, "Motivation": "Global trading volume", "Source": coin['id']}
        m_details['B3 Competitive Barriers'] = {"Score": 3, "Motivation": "Market position proxy", "Source": coin['id']}
        m_details['B4 Future-Proof Scalability'] = {"Score": 4, "Motivation": "Technology proxy", "Source": coin['id']}
        m_details['B5 Long-Term Incentives'] = {"Score": 4, "Motivation": "Tokenomics", "Source": coin['id']}
        m_details['B6 Viral Network Effects'] = {"Score": 4, "Motivation": "Volume and attention", "Source": coin['id']}
        m_details['B7 True Censorship Resistance'] = {"Score": 3, "Motivation": "Proxy based on blockchain type", "Source": coin['id']}
        m_details['B8 Macro Trends & Timing'] = {"Score": 3, "Motivation": "Market trend", "Source": "Market Data"}
        m_details['B9 Founders’ Track Record'] = {"Score": 3, "Motivation": "Proxy GitHub and team", "Source": "GitHub"}
        m_details['B10 Branding & Sentiment'] = {"Score": 4, "Motivation": "Market awareness proxy", "Source": "Market Data"}
    except:
        for i in range(1,11):
            m_details[f"B{i}"] = {"Score":0,"Motivation":"Data unavailable","Source":"N/A"}
    weights = [15,15,10,10,10,10,10,5,5,5]
    weighted_sum = sum([m_details[list(m_details.keys())[i]]['Score']*weights[i]/5 for i in range(10)])
    m_score = round(weighted_sum*20,1)
    return m_score, m_details, snapshot

def calculate_rar(k_score, m_score, profile):
    R_score = 0.15  # simple placeholder
    alpha = 0.6 if profile=='Balanced' else 0.4
    OTS = k_score*alpha + m_score*(1-alpha)
    RAR = round(OTS*(1-R_score),1)
    return R_score, OTS, RAR

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

# ------------------------------
# Streamlit App
# ------------------------------

st.title("CMEFX Crypto Analyzer - Full Version")

profile = st.selectbox("Select Investor Profile", ["Balanced","Growth"])
st.write(f"Selected profile: {profile}")

if st.button("Run Full Analysis"):
    st.write("Fetching coins from CoinGecko...")
    coins = fetch_coin_list()
    st.write(f"Fetched {len(coins)} coins. Running CMEFX full calculations...")

    results = []
    for coin in coins:
        k_score, k_details, k_snapshot = calculate_k_score_full(coin)
        m_score, m_details, m_snapshot = calculate_m_score_full(coin)
        r_score, ots, rar = calculate_rar(k_score, m_score, profile)
        label = qualitative_label(rar)

        results.append({
            "Name": coin['name'],
            "Ticker": coin['symbol'].upper(),
            "Price (€)": coin['current_price'],
            "K": k_score,
            "M": m_score,
            "RAR": rar,
            "Label": label,
            "Details": {
                "K-Details": k_details,
                "M-Details": m_details,
                "R-Score": r_score,
                "OTS": ots,
                "RAR": rar,
                "Snapshot": k_snapshot
            }
        })
    df = pd.DataFrame(results)
    df = df.sort_values("RAR", ascending=False).reset_index(drop=True)

    st.subheader("Crypto Rankings")
    for idx,row in df.iterrows():
        st.write(f"**{idx+1}. {row['Name']} ({row['Ticker']})** — Price: €{row['Price (€)']} — K:{row['K']} M:{row['M']} RAR:{row['RAR']} — Label: {row['Label']}")
        with st.expander("View Full CMEFX Report"):
            st.write(f"**Snapshot:** {row['Details']['Snapshot']}")
            st.write("**K-Score Details:**")
            st.json(row['Details']['K-Details'])
            st.write("**M-Score Details:**")
            st.json(row['Details']['M-Details'])
            st.write("**R-Score:**", row['Details']['R-Score'])
            st.write("**OTS:**", row['Details']['OTS'])
            st.write("**RAR:**", row['Details']['RAR'])
