#!/usr/bin/env python3
"""
TITAN-1: PROPRIETARY QUANT DATASET GENERATION FOUNDRY
Converts raw multi-timeframe candles into institutional Supervised Fine-Tuning (SFT)
training samples with deep 12-Desk Chain-of-Thought (CoT) reasoning.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai
from google.genai import types

DATASET_FILE = os.path.join("brain_vault", "titan1_quant_dataset.jsonl")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

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
        log(f"Error fetching {ticker}: {e}")
        return []

def synthesize_training_sample(client, symbol, window_candles, outcome_candle):
    prompt = f"""
YOU ARE THE CHIEF QUANTITATIVE ARCHITECT TRAINING THE 'TITAN-1' SOVEREIGN TRADING FOUNDATION MODEL.
Create a high-quality, institutional-grade Supervised Fine-Tuning (SFT) training sample.

INPUT CANDLESTICK CONTEXT ({symbol} 5-Minute Window):
{json.dumps(window_candles[-15:], indent=2)}

ACTUAL SUBSEQUENT OUTCOME:
Next 5-10 candles moved to: Close={outcome_candle['close']}, High={outcome_candle['high']}, Low={outcome_candle['low']}

GENERATE A PERFECT INSTRUCTION-RESPONSE SFT PAIR:
Format your response as a valid JSON object matching the Hugging Face / ShareGPT fine-tuning format:
{{
  "system": "You are TITAN-1, an institutional quantitative hedge fund foundation model. You analyze raw naked candlestick price action, order flow liquidity, and structural fair value gaps to output asymmetric trading mandates.",
  "user": "Analyze this 15-candle sequence for {symbol} and formulate the execution thesis:",
  "thought": "Step-by-step deep chain-of-thought analysis covering: 1. Liquidity sweeps, 2. Fair Value Gaps, 3. Volume delta absorption, 4. Red Team objection.",
  "response": {{
    "verdict": "BUY" or "SELL" or "WAIT",
    "rationale": "High-conviction institutional thesis",
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
    return None

def build_dataset_batch():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY missing.")
        return

    client = genai.Client(api_key=api_key)
    assets = {"XAUUSD": "GC=F", "BTCUSD": "BTC-USD", "EURUSD": "EURUSD=X"}

    os.makedirs("brain_vault", exist_ok=True)
    total_generated = 0

    log("Starting TITAN-1 Dataset Synthesis Foundry...")
    for sym, ticker in assets.items():
        log(f"Mining historical price sequences for {sym} ({ticker})...")
        candles = fetch_historical_candles(ticker, interval="5m", range_period="5d")
        if len(candles) < 30:
            continue

        # Slide through candle windows to build diverse market regimes
        step = max(10, len(candles) // 15)
        for idx in range(15, len(candles) - 10, step):
            window = candles[idx-15:idx]
            outcome = candles[idx+5]
            sample = synthesize_training_sample(client, sym, window, outcome)
            if sample:
                with open(DATASET_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(sample) + "\n")
                total_generated += 1
                log(f"Generated Training Sample #{total_generated} on {sym}!")
                time.sleep(1)

    log(f"Foundry Batch Complete. Total SFT samples ready: {total_generated}")

if __name__ == "__main__":
    build_dataset_batch()
