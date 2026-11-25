#!/usr/bin/env python3
"""
OLYMPUS SUPREME AI BRAIN - 12 ELITE QUANTITATIVE DESKS
Enhanced with: AUTONOMOUS REVERSAL SENTINEL (HARVEST GUARDIAN)
MANDATE:
1. Complete unconstrained freedom: No rigid caps, no pressure, full horizon freedom ($100 -> $1,000+).
2. Priority Asset: Gold (XAUUSD) + Multi-asset opportunities.
3. Sentinel Role: When positions are in solid green profit and an exhaustion / reversal wick occurs,
   sovereignly issue an 'EMERGENCY_PROFIT_HARVEST' to pocket peak gains before market reverses.
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
    tickers = {
        "XAUUSD": "GC=F",       # Priority #1: Gold
        "BTCUSD": "BTC-USD",    # Priority #2: Bitcoin
        "USTEC": "NQ=F",        # Priority #3: Nasdaq
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
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
    log("OLYMPUS SUPREME COUNCIL & AUTONOMOUS REVERSAL SENTINEL")
    log("==================================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    account_status = {"balance": 62.23, "equity": 62.23, "open_positions": []}
    if os.path.exists(BROKER_LIVE_FILE):
        try:
            with open(BROKER_LIVE_FILE, "r", encoding="utf-8") as f:
                account_status = json.load(f)
        except Exception:
            pass

    open_positions = account_status.get("open_positions", [])

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
YOU ARE THE OLYMPUS SOVEREIGN QUANTITATIVE HEDGE FUND BRAIN WITH FULL UNCONSTRAINED AUTONOMY.
THERE ARE ZERO RIGID CAPS, ZERO BOXES, AND ZERO PRESSURE.

YOU OPERATE WITH 12 SPECIALIZED DESKS + A DEDICATED AUTONOMOUS REVERSAL SENTINEL.

### DUAL MANDATE:
1. NEW OPPORTUNITY HUNTING:
   - Primary hunting asset: Gold (XAUUSD). Secondary: Bitcoin, Nasdaq, Forex.
   - Look for high-asymmetric momentum breakouts & liquidity sweeps toward $1,000+ compounding.
   - If clean setup: Output 'BUY' or 'SELL'. If choppy consolidation: Output 'WAIT'.

2. REVERSAL SENTINEL (HARVEST GUARDIAN) FOR ACTIVE OPEN TRADES:
   - Current Open Positions on Broker: {json.dumps(open_positions, indent=2)}
   - If open positions are in profit and you detect an imminent momentum exhaustion, top wick rejection, or reversal trap:
     YOU HAVE FULL SOVEREIGN AUTHORITY TO OUTPUT "CLOSE_PROFIT" to instantly harvest peak cash before the market takes it back!
   - If the trend remains strong, let it run freely without interference.

LIVE BROKER STATUS ({now_utc.isoformat()}):
- Balance: ${account_status.get('balance', 62.23)} USD
- Equity: ${account_status.get('equity', 62.23)} USD
- Active Positions: {len(open_positions)}

RECENT CLOSED DEALS FEEDBACK (LEARN -> IMPROVE):
{json.dumps(deal_feedback.get('deals', [])[-5:], indent=2)}

LIVE 15-MINUTE CANDLE MATRIX (GOLD & GLOBAL ASSETS):
{json.dumps(chart_matrix, indent=2)}

Respond STRICTLY in valid JSON matching this schema:
{{
  "timestamp": "{now_utc.isoformat()}",
  "verdict": "BUY" or "SELL" or "WAIT" or "CLOSE_PROFIT",
  "symbol": "XAUUSD" or "BTCUSD" or "USTEC" or "EURUSD" or "GBPUSD",
  "confidence_score": 0 to 100,
  "trade_style": "INTRADAY",
  "lot_size": 0.01,
  "sl_price": 0.0,
  "tp_price": 0.0,
  "trailing_activation_profit": 5.0,
  "reversal_sentinel_assessment": "Analysis of open positions: is trend continuing or is reversal imminent?",
  "trade_thesis": "Full sovereign reasoning"
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
            log(f"Council & Sentinel deliberating via {m}...")
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.25,
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                log(f"Deliberation successful via {m}!")
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
            
        log(f"🔥 SOVEREIGN VERDICT: {decision.get('verdict')} on {decision.get('symbol')}")
        log(f"Sentinel Assessment: {decision.get('reversal_sentinel_assessment')}")
        log(f"SL: {decision.get('sl_price')} | TP: {decision.get('tp_price')} | Conf: {decision.get('confidence_score')}%")
        log(f"Thesis: {decision.get('trade_thesis')}")
    except Exception as e:
        log(f"Error parsing decision: {e}")

if __name__ == "__main__":
    convene_supreme_council()
