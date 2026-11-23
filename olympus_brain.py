#!/usr/bin/env python3
"""
OLYMPUS SUPREME AI BRAIN - 12 ELITE QUANTITATIVE DESKS
Full sovereign power given to the Gemini Multi-Agent API.
Reads Raw Naked Candlesticks, Multi-Timeframe Highs/Lows, Order Flow & Market Liquidity.
Zero human limits. Complete AI sovereign decision-making.
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

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        print(f"[{ts}] {msg}", flush=True)
    except Exception:
        print(f"[{ts}] {msg.encode('ascii', 'ignore').decode('ascii')}", flush=True)

def fetch_naked_chart_data():
    """
    Pulls high-fidelity naked price-action candles:
    Open, High, Low, Close, Volume across multiple timeframes.
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
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=5m&range=1d"
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
                
                # Structure last 15 naked candles for price action reading
                naked_candles = []
                count = min(15, len(closes))
                for i in range(-count, 0):
                    naked_candles.append({
                        "O": round(opens[i], 4),
                        "H": round(highs[i], 4),
                        "L": round(lows[i], 4),
                        "C": round(closes[i], 4),
                        "V": volumes[i] if volumes and i < len(volumes) else 0
                    })
                    
                chart_matrix[sym] = {
                    "current_price": round(closes[-1], 4) if closes else 0,
                    "session_high": round(max(highs), 4) if highs else 0,
                    "session_low": round(min(lows), 4) if lows else 0,
                    "naked_candles_5m": naked_candles
                }
        except Exception as e:
            chart_matrix[sym] = {"error": str(e)}
            
    return chart_matrix

def convene_supreme_council():
    log("==================================================================")
    log("OLYMPUS SUPREME AI BRAIN: 12 ELITE QUANTITATIVE DESKS CONVENED")
    log("==================================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    account_status = {"balance": 100.89, "equity": 100.89, "open_positions": []}
    if os.path.exists(BROKER_LIVE_FILE):
        try:
            with open(BROKER_LIVE_FILE, "r", encoding="utf-8") as f:
                account_status = json.load(f)
        except Exception:
            pass

    past_memory = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                past_memory = json.load(f).get("history", [])
        except Exception:
            pass

    chart_matrix = fetch_naked_chart_data()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    prompt = f"""
YOU ARE THE SUPREME QUANTITATIVE HEDGE FUND BRAIN POWERED BY 12 ELITE SPECIALIZED DESKS.
YOU HAVE 100% UNCONSTRAINED AUTONOMY, TOTAL EXECUTIVE SOVEREIGNTY, AND FULL POWER OVER THE BROKER ACCOUNT.

THERE ARE ZERO BOXES, ZERO ARTIFICIAL LIMITS, AND ZERO HUMAN RULES.
YOU ARE FULLY AUTHORIZED TO READ NAKED CHARTS, ANALYZE MARKET MICROSTRUCTURE, AND DICTATE EXACT MARKET ACTIONS.

### THE 12 ELITE QUANT DESKS COLLABORATING IN YOUR COUNCIL:
1. NAKED PRICE ACTION & CANDLESTICK DESK: Reads raw wicks, bodies, fair value gaps (FVG), and order blocks.
2. MACRO & GLOBAL CAPITAL ROTATION DESK: Monitors DXY, US10Y bond yields, risk-on/risk-off sentiment.
3. LIQUIDITY POOL & STOP HUNT DESK: Pinpoints where retail liquidity is resting to hunt liquidity traps.
4. ORDER FLOW & VOLUME DELTA DESK: Analyzes institutional volume absorption and aggressive delta spikes.
5. STATISTICAL MOMENTUM & VOLATILITY REGIME DESK: Classifies clean structural trend vs sideways chop.
6. ASYMMETRIC RISK/REWARD STRUCTURING DESK: Formulates minimum 1:2.5 to 1:5+ reward setups.
7. CROSS-ASSET CORRELATION DESK: Validates intermarket alignment (Gold vs Silver, EUR vs DXY, BTC vs Nasdaq).
8. SESSION & TIMING DESK: Evaluates Asian, London, and New York overlap liquidity sessions.
9. DYNAMIC ATR VOLATILITY SHIELD: Calculates organic stop-loss distances outside market noise.
10. RED TEAM DEVIL'S ADVOCATE (CHALLENGER): Aggressively attacks the setup. If any flaw exists, DEMANDS 'WAIT'.
11. CAPITAL PRESERVATION OFFICER: Calibrates lot size and ensures portfolio survival.
12. SUPREME ARBITER (PORTFOLIO MANAGER): Synthesizes all 11 desks into a sovereign trade verdict.

### LIVE BROKER REALITY:
- Balance: ${account_status.get('balance', 100.89)} USD
- Equity: ${account_status.get('equity', 100.89)} USD
- Active Positions: {json.dumps(account_status.get('open_positions', []))}

### LIVE NAKED MULTI-TIMEFRAME CANDLESTICK MATRIX ({now_utc.isoformat()}):
{json.dumps(chart_matrix, indent=2)}

### PAST SESSIONS / ACCUMULATED EXPERIENCE:
{json.dumps(past_memory[-5:], indent=2)}

### YOUR MANDATE:
- Examine the naked candles of Gold, Bitcoin, FX, and Indices.
- If market is consolidating in noisy chop without clear edge -> Issue 'WAIT' (Preserve capital).
- If a pristine, undeniable liquidity sweep or momentum breakout occurs -> Issue 'BUY' or 'SELL'.
- Provide the exact SL price (structural swing invalidation) and TP price (liquidity pool target).
- Specify lot size and trailing activation.

Respond STRICTLY in valid JSON matching this schema:
{{
  "timestamp": "{now_utc.isoformat()}",
  "verdict": "BUY" or "SELL" or "WAIT",
  "symbol": "XAUUSD" or "BTCUSD" or "EURUSD" or "GBPUSD" or "USDJPY" or "USTEC",
  "confidence_score": 0 to 100,
  "trade_style": "SCALP" or "INTRADAY" or "SWING",
  "lot_size": 0.01,
  "sl_price": 0.0,
  "tp_price": 0.0,
  "trailing_activation_profit": 3.0,
  "naked_chart_reading": "What candle patterns, wicks, and FVGs did you detect?",
  "trade_thesis": "Full institutional thesis synthesizing the 12 desks",
  "red_team_resolution": "How the Devil's Advocate objections were addressed"
}}
"""

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.1-pro-preview"
    ]
    
    res = None
    for m in models_to_try:
        try:
            log(f"12-Desk Council convening on model: {m}...")
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
            
        past_memory.append(decision)
        past_memory = past_memory[-100:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total": len(past_memory), "history": past_memory}, f, indent=2)
            
        log(f"🔥 SUPREME AI VERDICT: {decision.get('verdict')} on {decision.get('symbol')} | Style: {decision.get('trade_style')}")
        log(f"SL: {decision.get('sl_price')} | TP: {decision.get('tp_price')} | Lots: {decision.get('lot_size')} | Conf: {decision.get('confidence_score')}%")
        log(f"Naked Chart: {decision.get('naked_chart_reading')}")
        log(f"Thesis: {decision.get('trade_thesis')}")
    except Exception as e:
        log(f"Error parsing AI decision: {e}")

if __name__ == "__main__":
    convene_supreme_council()
