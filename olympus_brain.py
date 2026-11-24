#!/usr/bin/env python3
"""
OLYMPUS SUPREME AI BRAIN - GOLD & MULTI-ASSET INTRADAY SNIPER
PRIMARY HUNTING GROUND: Gold (XAUUSD) - The King of Volatility & Asymmetric Swings.
Secondary: Bitcoin (BTCUSD), Nasdaq (USTEC), EURUSD, GBPUSD.
MANDATE: Gold ko top priority par continuously scan aur hunt karega without needing any manual reminder.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai
from google.genai import types

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DECISION_FILE = os.path.join("brain_vault", "active_trade_thesis.json")
BROKER_LIVE_FILE = os.path.join("brain_vault", "broker_account_live.json")
MEMORY_FILE = os.path.join("brain_vault", "olympus_learning_memory.json")
DEAL_FEEDBACK_FILE = os.path.join("brain_vault", "closed_deals_feedback.json")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        print(f"[{ts}] {msg}", flush=True)
    except Exception:
        print(f"[{ts}] {msg.encode('ascii', 'ignore').decode('ascii')}", flush=True)

def fetch_intraday_chart_data():
    """
    Pulls real-time 15m/1h candle geometry, placing GOLD (XAUUSD) at the top of the matrix.
    """
    tickers = {
        "XAUUSD": "GC=F",       # Priority #1: Gold
        "BTCUSD": "BTC-USD",    # Priority #2: Bitcoin
        "USTEC": "NQ=F",        # Priority #3: Nasdaq
        "EURUSD": "EURUSD=X",   # Priority #4: Forex
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "DXY": "DX-Y.NYB",      # Dollar Index Pressure
        "US10Y": "^TNX"         # 10Y Yields Pressure
    }
    
    chart_matrix = {}
    for sym, ticker in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=2d"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                res = data['chart']['result'][0]
                quotes = res['indicators']['quote'][0]
                opens = [o for o in quotes.get('open', []) if o is not None]
                highs = [h for h in quotes.get('high', []) if h is not None]
                lows = [l for l in quotes.get('low', []) if l is not None]
                closes = [c for c in quotes.get('close', []) if c is not None]
                volumes = [v for v in quotes.get('volume', []) if v is not None]
                
                intraday_candles = []
                count = min(16, len(closes))
                for i in range(-count, 0):
                    intraday_candles.append({
                        "O": round(opens[i], 4),
                        "H": round(highs[i], 4),
                        "L": round(lows[i], 4),
                        "C": round(closes[i], 4),
                        "V": volumes[i] if volumes and i < len(volumes) else 0
                    })
                    
                chart_matrix[sym] = {
                    "current_price": round(closes[-1], 4) if closes else 0,
                    "intraday_high": round(max(highs[-20:]), 4) if highs else 0,
                    "intraday_low": round(min(lows[-20:]), 4) if lows else 0,
                    "candles_15m": intraday_candles
                }
        except Exception as e:
            chart_matrix[sym] = {"error": str(e)}
            
    return chart_matrix

def convene_supreme_council():
    log("==================================================================")
    log("OLYMPUS GOLD (XAUUSD) & MULTI-ASSET AUTONOMOUS SNIPER COUNCIL")
    log("==================================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    account_status = {"balance": 100.85, "equity": 102.31, "open_positions": []}
    if os.path.exists(BROKER_LIVE_FILE):
        try:
            with open(BROKER_LIVE_FILE, "r", encoding="utf-8") as f:
                account_status = json.load(f)
        except Exception:
            pass

    deal_feedback = {}
    if os.path.exists(DEAL_FEEDBACK_FILE):
        try:
            with open(DEAL_FEEDBACK_FILE, "r", encoding="utf-8") as f:
                deal_feedback = json.load(f)
        except Exception:
            pass

    chart_matrix = fetch_intraday_chart_data()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    prompt = f"""
YOU ARE THE OLYMPUS SOVEREIGN QUANTITATIVE HEDGE FUND BRAIN.

### CORE OPERATING DOCTRINE:
1. PRIMARY ASSET FOCUS: GOLD (XAUUSD).
   - Gold is the primary alpha generator ($10 to $25 intraday price swings).
   - Prioritize Gold (XAUUSD) opportunities first in every cycle.
   - Secondary hunting grounds: Bitcoin (BTCUSD), Nasdaq (USTEC), EURUSD, GBPUSD.
2. ABSOLUTE AUTONOMY - NO USER PROMPTING NEEDED:
   - You NEVER require human input or reminders.
   - You autonomously detect Gold liquidity sweeps, Fair Value Gaps, and session order blocks.
   - When an asymmetric intraday edge exists on Gold (or secondary assets) -> Execute BUY or SELL immediately.
   - If market is in noisy sideways chop -> Mandate WAIT.

LIVE BROKER STATUS:
- Balance: ${account_status.get('balance', 100.85)} USD
- Equity: ${account_status.get('equity', 102.31)} USD
- Open Positions: {json.dumps(account_status.get('open_positions', []))}

RECENT CLOSED DEALS FEEDBACK (LEARN -> IMPROVE):
{json.dumps(deal_feedback.get('deals', [])[-5:], indent=2)}

LIVE INTRADAY CANDLESTICK MATRIX (GOLD & GLOBAL ASSETS) ({now_utc.isoformat()}):
{json.dumps(chart_matrix, indent=2)}

Respond STRICTLY in valid JSON matching this schema:
{{
  "timestamp": "{now_utc.isoformat()}",
  "verdict": "BUY" or "SELL" or "WAIT",
  "symbol": "XAUUSD" or "BTCUSD" or "USTEC" or "EURUSD" or "GBPUSD",
  "confidence_score": 0 to 100,
  "trade_style": "INTRADAY",
  "lot_size": 0.01,
  "sl_price": 0.0,
  "tp_price": 0.0,
  "trailing_activation_profit": 5.0,
  "gold_liquidity_analysis": "Detailed reading of XAUUSD order flow, wicks, and DXY correlation",
  "trade_thesis": "Full institutional thesis for this trade"
}}
"""

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash"
    ]
    
    res = None
    for m in models_to_try:
        try:
            log(f"Gold Sniper Council convening via model: {m}...")
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.25,
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                log(f"Council deliberation successful via {m}!")
                break
        except Exception as e:
            log(f"Model {m} error: {e}. Trying next...")
            time.sleep(2)
            
    if not res or not res.text:
        log("No response from AI models. Standing by.")
        return
        
    try:
        decision = json.loads(res.text)
        os.makedirs("brain_vault", exist_ok=True)
        with open(DECISION_FILE, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2)
            
        log(f"🔥 SOVEREIGN VERDICT: {decision.get('verdict')} on {decision.get('symbol')} | Style: INTRADAY")
        log(f"SL: {decision.get('sl_price')} | TP: {decision.get('tp_price')} | Lots: {decision.get('lot_size')} | Conf: {decision.get('confidence_score')}%")
        log(f"Gold Reading: {decision.get('gold_liquidity_analysis')}")
        log(f"Thesis: {decision.get('trade_thesis')}")
    except Exception as e:
        log(f"Error parsing decision: {e}")

if __name__ == "__main__":
    convene_supreme_council()
