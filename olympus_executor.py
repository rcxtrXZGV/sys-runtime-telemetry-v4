#!/usr/bin/env python3
"""
OLYMPUS SOVEREIGN MT5 EXECUTOR - RECURSIVE LEARNING ENGINE
Rule: LEARN -> IMPROVE -> REPEAT
1. Executes AI Sovereign Mandates on MT5.
2. Extracts Recent Closed Deals Outcome (Profit, Loss, Slippage, Holding Time).
3. Evaluates Mistakes & Successes -> Saves into Recursive Learning Memory.
4. Feeds ground-truth feedback into the AI Council for the next cycle.
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
LEARNING_MEMORY_FILE = os.path.join("brain_vault", "olympus_learning_memory.json")
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

def harvest_and_learn_from_deals():
    """
    LEARN -> IMPROVE -> REPEAT
    Analyzes all deals closed in the last 48 hours.
    Identifies what worked and what failed to feed back into the brain.
    """
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
        # Save exact deal feedback
        with open(DEAL_FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump({"total_closed_analyzed": len(closed_deals), "deals": closed_deals[-20:]}, f, indent=2)
            
        recent_net = sum(d["profit"] for d in closed_deals[-10:])
        wins = [d for d in closed_deals[-10:] if d["profit"] > 0]
        losses = [d for d in closed_deals[-10:] if d["profit"] < 0]
        log(f"🧠 [LEARN -> IMPROVE -> REPEAT] Analyzed last {len(closed_deals[-10:])} deals: Wins={len(wins)}, Losses={len(losses)}, Net=${recent_net:.2f}")

def manage_open_positions(open_positions, thesis):
    trailing_activation = float(thesis.get("trailing_activation_profit", 3.0) or 3.0)
    for p in open_positions:
        is_buy = (p.type == mt5.ORDER_TYPE_BUY)
        log(f"Position #{p.ticket} ({p.symbol}): Entry={p.price_open}, Cur={p.price_current}, SL={p.sl}, TP={p.tp}, Profit=${p.profit:.2f}")
        
        if p.profit >= trailing_activation and (p.sl < p.price_open if is_buy else (p.sl == 0 or p.sl > p.price_open)):
            buffer = 0.50 if "XAU" in p.symbol else (15.0 if "BTC" in p.symbol else 0.0005)
            new_sl = round(p.price_open + (buffer if is_buy else -buffer), 2 if "XAU" in p.symbol else 5)
            mod_req = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": p.ticket,
                "symbol": p.symbol,
                "sl": new_sl,
                "tp": p.tp
            }
            res = mt5.order_send(mod_req)
            if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                log(f"🎯 [AUTONOMOUS PROFIT LOCK] Position #{p.ticket} SL moved to {new_sl} to lock in green run!")

def main():
    log("==================================================================")
    log("OLYMPUS RECURSIVE SOVEREIGN EXECUTOR (LEARN -> IMPROVE -> REPEAT)")
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

    log(f"BROKER CONNECTED: {acc.name} | Balance: ${acc.balance:.2f} | Equity: ${acc.equity:.2f}")

    # STEP 1: LEARN (Harvest real closed deals and extract lessons)
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

    # STEP 2: MANAGE ACTIVE POSITIONS
    if open_pos and len(open_pos) > 0:
        log(f"Active trade detected ({len(open_pos)} open). Managing position according to AI thesis.")
        manage_open_positions(open_pos, thesis)
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
        log(f"[AI STANDBY] AI Brain verdict is '{verdict}'. Keeping capital 100% idle.")
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
        dist = 3.50 if "XAU" in sym else (250.0 if "BTC" in sym else 0.0030)
        sl = round(price - dist if is_buy else price + dist, 2 if ("XAU" in sym or "BTC" in sym) else 5)

    if tp_target > 0:
        tp = round(tp_target, 2 if ("XAU" in sym or "BTC" in sym) else 5)
    else:
        dist = 10.00 if "XAU" in sym else (800.0 if "BTC" in sym else 0.0090)
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
        "comment": "OLYMPUS_SOVEREIGN",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }

    log(f"Transmitting Sovereign AI Order: {lot} lots {sym} @ {price} | SL: {sl} | TP: {tp}...")
    res = mt5.order_send(req)
    if res and res.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"💥💥💥 [AI ORDER EXECUTED LIVE] Order #{res.order} | Deal #{res.deal} on {sym} @ {res.price} successfully filled!")
        if os.path.exists(DECISION_FILE):
            os.remove(DECISION_FILE)
    else:
        log(f"Order retcode: {getattr(res, 'retcode', None)} | comment: {getattr(res, 'comment', None)}")

    mt5.shutdown()
    log("Olympus cycle complete.")

if __name__ == "__main__":
    main()
