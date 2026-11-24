#!/usr/bin/env python3
"""
TITAN-1: MULTI-SOURCE INSTITUTIONAL DATA FOUNDRY
Integrates:
1. ForexFactory Real-Time High-Impact Economic Calendar (NFP, CPI, Fed, PMI, Rates).
2. Wikipedia / Encyclopedic Financial & Macro Foundations (Market Microstructure, Monetary Policy, FX Regimes).
3. Live Multi-Timeframe Naked Price Action (OHLCV, Volume Delta, Imbalances).
Forges institutional-grade Supervised Fine-Tuning (SFT) training vectors for TITAN-1.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types

DATASET_FILE = os.path.join("brain_vault", "titan1_quant_dataset.jsonl")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_forex_factory_calendar():
    """
    Fetches real-time High & Medium impact macroeconomic news events from ForexFactory.
    """
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    events = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for event in root.findall('event'):
                impact = event.find('impact').text if event.find('impact') is not None else ''
                if impact in ['High', 'Medium']:
                    title = event.find('title').text if event.find('title') is not None else ''
                    country = event.find('country').text if event.find('country') is not None else ''
                    date = event.find('date').text if event.find('date') is not None else ''
                    time_str = event.find('time').text if event.find('time') is not None else ''
                    forecast = event.find('forecast').text if event.find('forecast') is not None else ''
                    previous = event.find('previous').text if event.find('previous') is not None else ''
                    events.append({
                        "event": title,
                        "currency": country,
                        "impact": impact,
                        "date": date,
                        "time": time_str,
                        "forecast": forecast,
                        "previous": previous
                    })
    except Exception as e:
        log(f"ForexFactory calendar fetch error: {e}")
    return events[:10]

def fetch_macro_encyclopedia_concepts():
    """
    Fetches institutional macro theory extracts from Wikipedia API.
    """
    topics = [
        "Market_microstructure",
        "Order_(exchange)",
        "Monetary_policy",
        "Inflation",
        "Foreign_exchange_market"
    ]
    concepts = {}
    for t in topics:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{t}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                concepts[t.replace('_', ' ')] = data.get('extract', '')[:300]
        except Exception:
            pass
    return concepts

def fetch_historical_candles(ticker, interval="5m", range_period="5d"):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range={range_period}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            res = data['chart']['result'][0]
            quotes = res['indicators']['quote'][0]
            opens = [o for o in quotes.get('open', []) if o is not None]
            highs = [h for h in quotes.get('high', []) if h is not None]
            lows = [l for l in quotes.get('low', []) if l is not None]
            closes = [c for c in quotes.get('close', []) if c is not None]
            volumes = [v for v in quotes.get('volume', []) if v is not None]
            
            candles = []
            for i in range(len(closes)):
                candles.append({
                    "open": round(opens[i], 2),
                    "high": round(highs[i], 2),
                    "low": round(lows[i], 2),
                    "close": round(closes[i], 2),
                    "vol": volumes[i] if i < len(volumes) else 0
                })
            return candles
    except Exception as e:
        log(f"Error fetching candles for {ticker}: {e}")
        return []

def synthesize_multi_source_training_sample(client, symbol, window_candles, outcome_candle, news_context, macro_concepts):
    prompt = f"""
YOU ARE THE CHIEF QUANTITATIVE ARCHITECT TRAINING THE 'TITAN-1' SOVEREIGN TRADING FOUNDATION MODEL.
Synthesize multi-source intelligence into an elite institutional Supervised Fine-Tuning (SFT) training sample.

DATA SOURCES EMBEDDED:
1. FOREXFACTORY MACRO CALENDAR:
{json.dumps(news_context, indent=2)}

2. ENCYCLOPEDIC FINANCIAL KNOWLEDGE BASE:
{json.dumps(macro_concepts, indent=2)}

3. RAW 15-CANDLE NAKED CHART WINDOW ({symbol} 5-Minute):
{json.dumps(window_candles[-15:], indent=2)}

4. ACTUAL SUBSEQUENT OUTCOME:
Next price trajectory: Close={outcome_candle['close']}, High={outcome_candle['high']}, Low={outcome_candle['low']}

GENERATE A PERFECT INSTRUCTION-RESPONSE SFT PAIR:
Respond STRICTLY in valid JSON matching this schema:
{{
  "system": "You are TITAN-1, an institutional quantitative hedge fund foundation model. You synthesize live macroeconomic calendar releases (ForexFactory), encyclopedic market microstructure theories, and raw naked candlestick price action to output asymmetric trading mandates.",
  "user": "Synthesize the macroeconomic news schedule, foundational liquidity mechanics, and the 15-candle naked price action for {symbol}:",
  "thought": "Deep institutional chain-of-thought: 1. ForexFactory macro impact assessment, 2. Microstructure liquidity pool & fair value gap identification, 3. Volume delta absorption, 4. Red Team adversarial stress-test.",
  "response": {{
    "verdict": "BUY" or "SELL" or "WAIT",
    "rationale": "High-conviction synthesis connecting news catalyst, naked wick dynamics, and institutional order blocks",
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0,
    "rr": "1:X"
  }}
}}
"""
    try:
        res = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        if res and res.text:
            return json.loads(res.text)
    except Exception as e:
        log(f"Synthesis error: {e}")
        time.sleep(4)
    return None

def build_dataset_batch():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)
    assets = {"XAUUSD": "GC=F", "BTCUSD": "BTC-USD", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X"}

    os.makedirs("brain_vault", exist_ok=True)
    
    log("Step 1: Fetching ForexFactory high-impact economic calendar events...")
    news_events = fetch_forex_factory_calendar()
    log(f"Harvested {len(news_events)} ForexFactory calendar events.")

    log("Step 2: Fetching Encyclopedic Macro & Market Microstructure Foundations...")
    macro_concepts = fetch_macro_encyclopedia_concepts()
    log(f"Harvested {len(macro_concepts)} core institutional financial definitions.")

    total_generated = 0
    log("Step 3: Mining naked candlestick price action & forging multi-source SFT dataset...")

    for sym, ticker in assets.items():
        log(f"Mining sequences for {sym} ({ticker})...")
        candles = fetch_historical_candles(ticker, interval="5m", range_period="5d")
        if len(candles) < 30:
            continue

        step = max(10, len(candles) // 12)
        for idx in range(15, len(candles) - 10, step):
            window = candles[idx-15:idx]
            outcome = candles[idx+5]
            sample = synthesize_multi_source_training_sample(client, sym, window, outcome, news_events, macro_concepts)
            if sample:
                with open(DATASET_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(sample) + "\n")
                total_generated += 1
                log(f"Forged Multi-Source Training Sample #{total_generated} on {sym}!")
                time.sleep(4)  # Rate limit safe

    log(f"Foundry Batch Complete. Total multi-source SFT samples added: {total_generated}")

if __name__ == "__main__":
    build_dataset_batch()
