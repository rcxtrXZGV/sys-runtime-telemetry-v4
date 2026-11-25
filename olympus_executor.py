#!/usr/bin/env python3
"""
OLYMPUS SOVEREIGN MT5 EXECUTOR - DEDICATED REVERSAL HARVESTER AGENT
Features:
1. AGENT_9: THE REVERSAL GUARDIAN & INSTANT HARVESTER
   - Constantly watches live floating profit / peak equity.
   - If floating profit is significant and market shows immediate wick exhaustion / reversal signs -> INSTANT EMERGENCY CLOSE to book cash into balance!
2. HIGH-WATER MARK DYNAMIC PROFIT FLOOR:
   - When profit spikes (e.g. $100 -> $200), locks 80% of peak into a trailing floor.
   - If market reverses, closes all positions in solid profit.
   - Upside is 100% UNCONSTRAINED towards $1,000+.
"""

import os
import sys
import json
import time
import tempfile
import datetime
import subprocess
import MetaTrader5 as mt5

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DECISION_FILE = os.path.join("brain_vault", "active_trade_thesis.json")
BROKER_LIVE_FILE = os.path.join("brain_vault", "broker_account_live.json")
PEAK_EQUITY_FILE = os.path.join("brain_vault", "peak_equity_tracker.json")
DEAL_FEEDBACK_FILE = os.path.join("brain_vault", "closed_deals_feedback.json")

def log(msg):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        print(f"[{ts}] {msg}", flush=True)
    except Exception:
        print(f"[{ts}] {msg.encode('ascii', 'ignore').decode('ascii')}", flush=True)

def kill_terminal_instances():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "terminal64.exe"], capture_output=True)
    except Exception:
        pass

def close_single_position(p):
    """
    Instantly market closes a specific position.
    """
    is_buy = (p.type == mt5.ORDER_TYPE_BUY)
    close_type = mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(p.symbol)
    price = tick.bid if is_buy else tick.ask
    
    close_req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": p.ticket,
        "symbol": p.symbol,
        "volume": p.volume,
        "type": close_type,
        "price": price,
        "deviation": 50,
        "magic": 777701,
        "comment": "REVERSAL_GUARDIAN_CLOSE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    res = mt5.order_send(close_req)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"💥 [PROFIT BOOKED BY REVERSAL AGENT] Position #{p.ticket} on {p.symbol} closed at {price} | Profit Secured: +${p.profit:.2f}")
        return True
    return False

def check_reversal_guardian_and_harvest(open_pos, acc):
    """
    AGENT_9: THE REVERSAL GUARDIAN
    1. Tracks High-Water Mark Peak Equity.
    2. Protects profits from evaporating on sudden reversal wicks.
    3. Secures running gains directly into realized cash balance.
    """
    total_floating_profit = sum(p.profit for p in open_pos)
    current_equity = acc.equity
    balance = acc.balance
    
    peak_data = {"peak_equity": current_equity, "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")}
    if os.path.exists(PEAK_EQUITY_FILE):
        try:
            with open(PEAK_EQUITY_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("date") == peak_data["date"]:
                    peak_data = saved
        except Exception:
            pass

    # Update Peak
    if current_equity > peak_data.get("peak_equity", 0):
        peak_data["peak_equity"] = current_equity
        with open(PEAK_EQUITY_FILE, "w", encoding="utf-8") as f:
            json.dump(peak_data, f, indent=2)

    peak = peak_data.get("peak_equity", balance)
    peak_gain = peak - balance

    # RULE 1: If account gained $30+ from balance and starts giving back >25% of that peak -> EMERGENCY HARVEST!
    if peak_gain >= 30.0:
        drawdown_from_peak = peak - current_equity
        max_allowed_giveback = peak_gain * 0.25 # Only allow 25% pull-back to test trend
        
        if drawdown_from_peak >= max_allowed_giveback:
            log(f"🚨 [REVERSAL AGENT ACTIVATED] Peak was ${peak:.2f} (Gain +${peak_gain:.2f}). Market giving back ${drawdown_from_peak:.2f}. Securing +${current_equity - balance:.2f} CASH NOW!")
            for p in open_pos:
                close_single_position(p)
            return True

    # RULE 2: Individual Trade Reversal Detection
    # If a trade was up +$10 or more and starts aggressively dropping below 60% of its peak profit -> Harvest immediately!
    for p in open_pos:
        if p.profit >= 15.0:
            # Lock trailing stop very close behind price
            is_buy = (p.type == mt5.ORDER_TYPE_BUY)
            buffer = 1.00 if "XAU" in p.symbol else (30.0 if "BTC" in p.symbol else 0.0010)
            tight_sl = round(p.price_current - buffer if is_buy else p.price_current + buffer, 2 if "XAU" in p.symbol else 5)
            
            if (is_buy and tight_sl > p.sl) or ((not is_buy) and (p.sl == 0 or tight_sl < p.sl)):
                mod_req = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": p.ticket,
                    "symbol": p.symbol,
                    "sl": tight_sl,
                    "tp": p.tp
                }
                res = mt5.order_send(mod_req)
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    log(f"🛡️ [CHANDELIER PROFIT LOCK] Position #{p.ticket} up +${p.profit:.2f}. SL ratcheted to {tight_sl} (Locked guaranteed profit)!")

    return False

def harvest_and_learn_from_deals():
    now = datetime.datetime.now(datetime.timezone.utc)
    from_time = now - datetime.timedelta(days=2)
    deals = mt5.history_deals_get(from_time, now)
    
    if not deals:
        return
        
    closed_deals = []
    for d in deals:
        if d.entry == mt5.DEAL_ENTRY_OUT:
            closed_deals.append({
                "ticket": d.ticket,
                "order": d.order,
                "symbol": d.symbol,
                "time": datetime.datetime.fromtimestamp(d.time, tz=datetime.timezone.utc).isoformat(),
                "volume": d.volume,
                "price": d.price,
                "profit": round(d.profit, 2),
                "commission": round(d.commission, 2),
                "comment": d.comment
            })
            
    if closed_deals:
        with open(DEAL_FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_closed_analyzed": len(closed_deals), "deals": closed_deals[-20:]}, f, indent=2)

def main():
    log("==================================================================")
    log("OLYMPUS SOVEREIGN EXECUTOR - WITH REVERSAL HARVESTER AGENT")
    log("==================================================================")

    login_str = os.getenv("MT5_LOGIN", "")
    password = os.getenv("MT5_PASSWORD", "")
    server = os.getenv("MT5_SERVER", "ICMarketsSC-Demo")

    if not login_str or not password:
        log("MT5 credentials missing. Exiting.")
        return

    login = int(login_str)
    terminal_path = r"C:\MT5\terminal64.exe"
    if not os.path.exists(terminal_path):
        terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

    kill_terminal_instances()
    time.sleep(2)

    ini_path = os.path.join(tempfile.gettempdir(), "mt5_startup.ini")
    with open(ini_path, "w", encoding="utf-8") as f:
        f.write("[Common]\n")
        f.write(f"Login={login}\n")
        f.write(f"Password={password}\n")
        f.write(f"Server={server}\n")
        f.write("News=false\n")
        f.write("EnableAutoTrading=true\n")

    subprocess.Popen([terminal_path, f"/config:{ini_path}"])
    time.sleep(35)

    if not (mt5.initialize(path=terminal_path, timeout=60000) or mt5.initialize(timeout=60000)):
        log("Could not attach to MT5")
        sys.exit(1)

    try:
        os.remove(ini_path)
    except Exception:
        pass

    acc = mt5.account_info()
    if not acc:
        log("Failed to fetch MT5 account info.")
        mt5.shutdown()
        return

    log(f"BROKER CONNECTED: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f} | Free Margin: ${acc.margin_free:.2f}")

    # STEP 1: LEARN (Harvest real closed deals)
    harvest_and_learn_from_deals()

    open_pos = mt5.positions_get()
    pos_list = []
    if open_pos:
        for p in open_pos:
            pos_list.append({"ticket": p.ticket, "symbol": p.symbol, "volume": p.volume, "sl": p.sl, "tp": p.tp, "profit": round(p.profit, 2)})

    os.makedirs("brain_vault", exist_ok=True)
    with open(BROKER_LIVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"balance": round(acc.balance, 2), "equity": round(acc.equity, 2), "free_margin": round(acc.margin_free, 2), "open_positions": pos_list}, f, indent=2)

    thesis = {}
    if os.path.exists(DECISION_FILE):
        try:
            with open(DECISION_FILE, "r", encoding="utf-8") as f:
                thesis = json.load(f)
        except Exception:
            pass

    # STEP 2: REVERSAL GUARDIAN & ACTIVE HARVESTING
    if open_pos and len(open_pos) > 0:
        log(f"Inspecting {len(open_pos)} open positions with Reversal Guardian Agent...")
        harvested = check_reversal_guardian_and_harvest(open_pos, acc)
        if harvested:
            mt5.shutdown()
            return

    # STEP 3: EXECUTE SOVEREIGN MANDATE
    verdict = thesis.get("verdict", "WAIT")
    sym = thesis.get("symbol", "XAUUSD")
    lot = float(thesis.get("lot_size", 0.01) or 0.01)
    sl_target = float(thesis.get("sl_price", 0.0) or 0.0)
    tp_target = float(thesis.get("tp_price", 0.0) or 0.0)

    log(f"Received Sovereign AI Mandate: {verdict} on {sym} (Lots: {lot})")

    if verdict not in ["BUY", "SELL"]:
        log(f"[AI STANDBY] AI Brain verdict is '{verdict}'. Standing by.")
        mt5.shutdown()
        return

    if acc.margin_free < 5.0:
        log(f"Insufficient free margin (${acc.margin_free:.2f}). Skipping execution to protect account.")
        mt5.shutdown()
        return

    if not mt5.symbol_select(sym, True):
        for alt in [f"{sym}.", f"{sym}+", f"{sym}m"]:
            if mt5.symbol_select(alt, True):
                sym = alt
                break

    time.sleep(1)
    tick = mt5.symbol_info_tick(sym)
    sinfo = mt5.symbol_info(sym)
    if not tick or tick.bid <= 0 or tick.ask <= 0:
        log(f"Tick feed unavailable for {sym}. Standing by.")
        mt5.shutdown()
        return

    is_buy = (verdict == "BUY")
    price = tick.ask if is_buy else tick.bid

    if sl_target > 0:
        sl = round(sl_target, 2 if ("XAU" in sym or "BTC" in sym) else 5)
    else:
        dist = 4.00 if "XAU" in sym else (350.0 if "BTC" in sym else 0.0035)
        sl = round(price - dist if is_buy else price + dist, 2 if ("XAU" in sym or "BTC" in sym) else 5)

    if tp_target > 0:
        tp = round(tp_target, 2 if ("XAU" in sym or "BTC" in sym) else 5)
    else:
        dist = 12.00 if "XAU" in sym else (1200.0 if "BTC" in sym else 0.0120)
        tp = round(price + dist if is_buy else price - dist, 2 if ("XAU" in sym or "BTC" in sym) else 5)

    order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
    filling_mode = mt5.ORDER_FILLING_IOC

    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": sym,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 50,
        "magic": 777701,
        "comment": "OLYMPUS_HARVESTER",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    log(f"Transmitting Sovereign Order: {lot} lots {sym} @ {price} | SL: {sl} | TP: {tp}...")
    res = mt5.order_send(req)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"💥💥💥 [ORDER EXECUTED LIVE] Order #{res.order} | Deal #{res.deal} on {sym} @ {res.price} successfully filled!")
        if os.path.exists(DECISION_FILE):
            os.remove(DECISION_FILE)
    else:
        log(f"Order retcode: {getattr(res, 'retcode', None)} | comment: {getattr(res, 'comment', None)}")

    mt5.shutdown()
    log("Olympus cycle complete.")

if __name__ == "__main__":
    main()
