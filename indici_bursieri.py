import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ────────────────────────────────────────────────
# Lista indicilor (simboluri Yahoo Finance)
# Poți adăuga/șterge după preferințe
# ────────────────────────────────────────────────
INDICI = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT",
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",
    "CAC 40": "^FCHI",
    "IBEX 35": "^IBEX",
    "Euro Stoxx 50": "^STOXX50E",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "Shanghai Comp.": "000001.SS",
    "BSE Sensex": "^BSESN",
    "Nifty 50": "^NSEI",
    "IBOVESPA": "^BVSP",
    "MERVAL": "^MERV",
    "S&P/TSX": "^GSPTSE",
    "ASX 200": "^AXJO",
    "BET (BVB)": "^BET",
    "BET-FI": "^BETFI",
    "WIG20": "^WIG20",
    "MOEX": "IMOEX.ME",          # Rusia (atenție la lichiditate/sancțiuni)
    "TAIEX": "^TWII",
}

# ────────────────────────────────────────────────
st.title("Top Indici Bursieri – Creșteri & Evoluție")
st.markdown("Date via Yahoo Finance • ultimele valori disponibile")

# ────────────────────────────────────────────────
# Partea A: Top creșteri 24h și 3 zile
# ────────────────────────────────────────────────
if st.button("Actualizează Top Creșteri (poate dura 10–20 secunde)"):
    with st.spinner("Se descarcă datele..."):
        results = []
        for nume, simbol in INDICI.items():
            try:
                ticker = yf.Ticker(simbol)
                hist = ticker.history(period="5d")   # luăm 5 zile ca să avem marjă
                
                if len(hist) < 3:
                    continue
                
                # Ultima zi închisă
                ultima = hist.iloc[-1]
                penultima = hist.iloc[-2]
                
                change_24h = (ultima['Close'] / penultima['Close'] - 1) * 100
                
                # Ultimele 3 zile
                change_3d = (ultima['Close'] / hist.iloc[-3]['Close'] - 1) * 100
                
                results.append({
                    "Indice": nume,
                    "Simbol": simbol,
                    "Preț actual": round(ultima['Close'], 2),
                    "Schimb. 24h (%)": round(change_24h, 2),
                    "Schimb. 3 zile (%)": round(change_3d, 2),
                    "Volum": int(ultima['Volume']) if 'Volume' in ultima else 0
                })
            except Exception:
                pass  # sărim peste indicii cu eroare temporară
        
        if results:
            df = pd.DataFrame(results)
            
            st.subheader("Top 15 Creșteri în ultimele 24 ore")
            top24 = df.sort_values("Schimb. 24h (%)", ascending=False).head(15)
            st.dataframe(top24.style.format({
                "Preț actual": "{:,.2f}",
                "Schimb. 24h (%)": "{:+.2f}%",
                "Schimb. 3 zile (%)": "{:+.2f}%"
            }).background_gradient(subset=["Schimb. 24h (%)"], cmap="RdYlGn"))
            
            st.subheader("Top 15 Creșteri în ultimele 3 zile")
            top3d = df.sort_values("Schimb. 3 zile (%)", ascending=False).head(15)
            st.dataframe(top3d.style.format({
                "Preț actual": "{:,.2f}",
                "Schimb. 24h (%)": "{:+.2f}%",
                "Schimb. 3 zile (%)": "{:+.2f}%"
            }).background_gradient(subset=["Schimb. 3 zile (%)"], cmap="RdYlGn"))
        else:
            st.error("Nu s-au putut descărca datele. Verifică conexiunea.")

# ────────────────────────────────────────────────
# Partea B: Evoluție detaliată pentru un indice ales
# ────────────────────────────────────────────────
st.subheader("Evoluție detaliată")
selected_name = st.selectbox("Alege indicele", list(INDICI.keys()))
selected_symbol = INDICI.get(selected_name)

if selected_symbol:
    perioade = {
        "Ultima săptămână": "7d",
        "Ultima lună": "1mo",
        "Ultimul an": "1y",
        "Ultimii 5 ani": "5y",
        "De la început (max)": "max"
    }
    
    perioada = st.radio("Perioadă", list(perioade.keys()), horizontal=True)
    interval = "1d" if perioada in ["Ultimul an", "Ultimii 5 ani", "De la început (max)"] else "1h"
    
    if st.button(f"Afișează grafic {perioada} pentru {selected_name}"):
        with st.spinner(f"Se încarcă {perioada}..."):
            try:
                data = yf.download(selected_symbol, period=perioade[perioada], interval=interval, progress=False)
                
                if data.empty:
                    st.warning("Nu există date pentru perioada aceasta.")
                else:
                    fig = px.line(data, x=data.index, y="Close",
                                  title=f"{selected_name} ({selected_symbol}) – {perioada}",
                                  labels={"Close": "Valoare închidere", "index": "Dată"})
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mic tabel cu statistici
                    st.markdown("**Statistici rapide**")
                    col1, col2, col3 = st.columns(3)
                    min_val = data["Close"].min()
                    max_val = data["Close"].max()
                    change_total = (data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100
                    
                    col1.metric("Minim", f"{min_val:,.2f}")
                    col2.metric("Maxim", f"{max_val:,.2f}")
                    col3.metric("Creștere totală", f"{change_total:+.2f}%")
                    
            except Exception as e:
                st.error(f"Eroare: {e}")
