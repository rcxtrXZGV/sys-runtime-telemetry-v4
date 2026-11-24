import os, sys, time, tempfile, subprocess
import MetaTrader5 as mt5

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

login = int(os.getenv('MT5_LOGIN'))
password = os.getenv('MT5_PASSWORD')
server = os.getenv('MT5_SERVER', 'ICMarketsSC-Demo')
sym = os.getenv('TARGET_SYMBOL', 'XAUUSD')
direction = os.getenv('TARGET_DIRECTION', 'BUY')

terminal_path = r'C:\MT5\terminal64.exe'
if not os.path.exists(terminal_path):
    terminal_path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

ini_path = os.path.join(tempfile.gettempdir(), 'mt5_startup.ini')
with open(ini_path, 'w') as f:
    f.write(f'[Common]\nLogin={login}\nPassword={password}\nServer={server}\nNews=false\nEnableAutoTrading=true\n')

subprocess.Popen([terminal_path, f'/config:{ini_path}'])
time.sleep(35)
mt5.initialize(path=terminal_path)

acc = mt5.account_info()
print(f'BROKER CONNECTED: {acc.name} | Balance:  | Equity: ')

if not mt5.symbol_select(sym, True):
    for alt in [f'{sym}.', f'{sym}+', f'{sym}m']:
        if mt5.symbol_select(alt, True):
            sym = alt
            break

time.sleep(1)
tick = mt5.symbol_info_tick(sym)

is_buy = (direction == 'BUY')
price = tick.ask if is_buy else tick.bid
order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

dist = 3.50 if 'XAU' in sym else 0.0030
sl = round(price - dist if is_buy else price + dist, 2 if 'XAU' in sym else 5)
tp = round(price + dist if is_buy else price - dist, 2 if 'XAU' in sym else 5)

req = {
    'action': mt5.TRADE_ACTION_DEAL,
    'symbol': sym,
    'volume': 0.01,
    'type': order_type,
    'price': price,
    'sl': sl,
    'tp': tp,
    'deviation': 50,
    'magic': 777701,
    'comment': 'LIVE_XAUUSD_ORDER',
    'type_time': mt5.ORDER_TIME_GTC,
    'type_filling': mt5.ORDER_FILLING_IOC,
}

print(f'Transmitting Instant Live {direction} Order on {sym} @ {price}...')
res = mt5.order_send(req)
if res and res.retcode == mt5.TRADE_RETCODE_DONE:
    print(f'[LIVE ORDER EXECUTED] Order #{res.order} | Deal #{res.deal} on {sym} @ {res.price} FILLED!')
else:
    print('Order failed retcode:', getattr(res, 'retcode', None), 'comment:', getattr(res, 'comment', None))

mt5.shutdown()
