#!/usr/bin/env python3
"""
OLYMPUS SUPREME AI BRAIN - INTRADAY INSTITUTIONAL SNIPER
Mode: STRICT INTRADAY TRADING (No 1-Minute Micro Noise, No Multi-Day Swings)
Horizon: 15-Minute & 1-Hour Intraday Sweeps, London & New York Session Momentum.
Rules:
1. Target: Clean Intraday Targets ($10 to $25 profit runs on Gold, Forex, Crypto).
2. Noise Shield: Stop-Loss placed strictly outside intraday session wicks.
3. Learn -> Improve -> Repeat active across every single session.
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
    Pulls 15-Minute (M15) and 1-Hour (H1) intraday structure.
    Eliminates 1-minute noise completely.
    """
    tickers = {
        "XAUUSD": "GC=F",
        "BTCUSD": "BTC-USD",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "USTEC": "NQ=F",
        "US30": "YM=F",
        "USOIL": "CL=F",
        "DXY": "DX-Y.NYB",
        "US10Y": "^TNX"
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
    log("OLYMPUS INTRADAY SNIPER BRAIN - 15M/1H INSTITUTIONAL EXECUTION")
    log("==================================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    account_status = {"balance": 97.96, "equity": 97.96, "open_positions": []}
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
YOU ARE THE OLYMPUS INTRADAY QUANTITATIVE HEDGE FUND BRAIN.
YOUR EXCLUSIVE MANDATE: STRICT INTRADAY TRADING (NO MICRO-NOISE SCALPING, NO MULTI-DAY SWINGS).

CORE PHILOSOPHY:
- Timeframe Horizon: 15-Minute & 1-Hour Intraday Sweeps.
- Target: Ride clean intraday momentum runs (London session open, New York overlap) targeting $10 to $25 profit moves.
- Stop-Loss: MUST be structural, placed behind key session swing highs/lows (outside noise).
- Risk-Reward: Target minimum 1:2.5 to 1:4 RR.

LIVE BROKER STATUS:
- Balance: ${account_status.get('balance', 97.96)} USD
- Equity: ${account_status.get('equity', 97.96)} USD
- Open Positions: {json.dumps(account_status.get('open_positions', []))}

RECENT CLOSED DEALS FEEDBACK (LEARN -> IMPROVE):
{json.dumps(deal_feedback.get('deals', [])[-5:], indent=2)}

LIVE 15-MINUTE INTRADAY CANDLESTICK MATRIX ({now_utc.isoformat()}):
{json.dumps(chart_matrix, indent=2)}

DIRECTIONS:
1. Identify the single best INTRADAY trade setup across Gold, Bitcoin, EUR, GBP, JPY, or Nasdaq.
2. If the intraday trend is confirmed with volume displacement -> Output 'BUY' or 'SELL'.
3. If all assets are in tight lunchtime consolidation -> Output 'WAIT'.
4. Provide exact SL and TP prices for intraday execution.

Respond STRICTLY in valid JSON matching this schema:
{{
  "timestamp": "{now_utc.isoformat()}",
  "verdict": "BUY" or "SELL" or "WAIT",
  "symbol": "XAUUSD" or "BTCUSD" or "EURUSD" or "GBPUSD" or "USDJPY" or "USTEC",
  "confidence_score": 0 to 100,
  "trade_style": "INTRADAY",
  "lot_size": 0.01,
  "sl_price": 0.0,
  "tp_price": 0.0,
  "trailing_activation_profit": 5.0,
  "intraday_rationale": "Why this 15m/1h intraday setup offers asymmetric reward",
  "learning_applied": "How past feedback protected capital for this intraday trade"
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
            log(f"Intraday Council convening via model: {m}...")
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.25,
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                log(f"Intraday deliberation successful via {m}!")
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
            
        log(f"🔥 INTRADAY VERDICT: {decision.get('verdict')} on {decision.get('symbol')} | Style: INTRADAY")
        log(f"SL: {decision.get('sl_price')} | TP: {decision.get('tp_price')} | Lots: {decision.get('lot_size')} | Conf: {decision.get('confidence_score')}%")
        log(f"Intraday Rationale: {decision.get('intraday_rationale')}")
    except Exception as e:
        log(f"Error parsing Intraday decision: {e}")

if __name__ == "__main__":
    convene_supreme_council()
