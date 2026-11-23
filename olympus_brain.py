#!/usr/bin/env python3
"""
OLYMPUS SUPREME AI BRAIN - 100% UNCONSTRAINED AUTONOMY
Full Freedom: Brain decides Asset, Direction (BUY/SELL/WAIT), Lot Size, SL, TP, Trailing Logic, and Tactical Horizon.
Zero Boxes. Zero Artificial Limits. Total AI Sovereign Power.
"""

import os
import sys
import json
import time
import datetime
import urllib.request
from google import genai
from google.genai import types

DECISION_FILE = os.path.join("brain_vault", "active_trade_thesis.json")
BROKER_LIVE_FILE = os.path.join("brain_vault", "broker_account_live.json")
MEMORY_FILE = os.path.join("brain_vault", "olympus_learning_memory.json")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)

def fetch_comprehensive_market_data():
    """
    Scans entire global liquidity landscape:
    Commodities, Crypto, Major FX, Equity Indices, Rates & Dollar Index.
    """
    tickers = {
        "XAUUSD": "GC=F",
        "XAGUSD": "SI=F",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "USTEC": "NQ=F",
        "US30": "YM=F",
        "USOIL": "CL=F",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "DXY": "DX-Y.NYB",
        "US10Y": "^TNX"
    }
    
    landscape = {}
    for sym, ticker in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=5m&range=1d"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                res = data['chart']['result'][0]
                quotes = res['indicators']['quote'][0]
                closes = [c for c in quotes.get('close', []) if c is not None]
                highs = [h for h in quotes.get('high', []) if h is not None]
                lows = [l for l in quotes.get('low', []) if l is not None]
                
                curr = res['meta'].get('regularMarketPrice') or (closes[-1] if closes else 0)
                landscape[sym] = {
                    "price": round(curr, 4),
                    "day_high": round(max(highs), 4) if highs else curr,
                    "day_low": round(min(lows), 4) if lows else curr,
                    "recent_candles": [round(c, 4) for c in closes[-10:]] if closes else []
                }
        except Exception as e:
            landscape[sym] = {"error": str(e)}
            
    return landscape

def convene_supreme_council():
    log("==================================================================")
    log("TITAN OLYMPUS: UNCONSTRAINED SUPREME AI COUNCIL (ZERO BOXES)")
    log("==================================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log("GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # Live Broker Reality
    account_status = {"balance": 100.0, "equity": 100.0, "open_positions": []}
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

    market_data = fetch_comprehensive_market_data()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    prompt = f"""
YOU ARE THE SUPREME QUANTITATIVE TRADING INTELLIGENCE.
YOU HAVE TOTAL SOVEREIGNTY AND 100% UNCONSTRAINED AUTONOMY.
THERE ARE NO RULES, NO BOXES, NO HUMAN INTERFERENCE, AND NO ARTIFICIAL LIMITS.

YOU AND YOUR 8 INTERNAL SPECIALIST AGENTS DECIDE EVERYTHING:
- What asset to trade (Gold, BTC, Crypto, FX, Indices, Oil).
- Whether to BUY, SELL, or WAIT.
- Exactly how much volume (lot size) to deploy based on your conviction.
- Exact Stop-Loss price level (outside noise, behind swing liquidity).
- Exact Take-Profit target level (unconstrained profit capture).
- Tactical horizon: Scalp, Intraday Momentum, or Swing Liquidity Sweep.

### YOUR 8 ADVERSARIAL AGENTS DEBATING RIGHT NOW:
1. Macro Capital Flow Agent (Global liquidity trends)
2. Statistical Arbitrage & Momentum Agent
3. Liquidity Trap & Retail Stop Hunter Agent
4. Asymmetric Risk/Reward Structuring Agent
5. Volatility Regime & Microstructure Agent
6. Cross-Asset Correlation Agent
7. Red Team Devil's Advocate (Critiques and attempts to veto weaknesses)
8. Supreme Risk Master (Ensures portfolio survival and geometric compounding)

### LIVE BROKER STATUS ({now_utc.isoformat()}):
- Balance: ${account_status.get('balance', 100.0)} USD
- Equity: ${account_status.get('equity', 100.0)} USD
- Open Positions: {json.dumps(account_status.get('open_positions', []))}

### LIVE GLOBAL MARKET MATRIX:
{json.dumps(market_data, indent=2)}

### PAST SESSIONS / MISTAKES TO LEARN FROM:
{json.dumps(past_memory[-5:], indent=2)}

Synthesize the debate of all 8 agents and formulate your sovereign thesis.
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
  "trade_thesis": "In-depth reasoning behind the setup",
  "red_team_objection_handled": "How the Devil's Advocate objection was solved"
}}
"""

    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    res = None
    for m in models:
        try:
            log(f"Supreme Council deliberating via {m}...")
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                break
        except Exception as e:
            log(f"Model {m} busy: {e}. Trying next...")
            time.sleep(2)
            
    if not res or not res.text:
        log("No response from AI models. Standing by.")
        return
        
    try:
        decision = json.loads(res.text)
        os.makedirs("brain_vault", exist_ok=True)
        with open(DECISION_FILE, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2)
            
        # Log to permanent learning memory
        past_memory.append(decision)
        past_memory = past_memory[-100:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"total": len(past_memory), "history": past_memory}, f, indent=2)
            
        log(f"🔥 SUPREME AI VERDICT: {decision.get('verdict')} on {decision.get('symbol')} | Style: {decision.get('trade_style')}")
        log(f"SL: {decision.get('sl_price')} | TP: {decision.get('tp_price')} | Lots: {decision.get('lot_size')} | Conf: {decision.get('confidence_score')}%")
        log(f"Thesis: {decision.get('trade_thesis')}")
    except Exception as e:
        log(f"Error parsing AI decision: {e}")

if __name__ == "__main__":
    convene_supreme_council()
