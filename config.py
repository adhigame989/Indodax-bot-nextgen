"""
config.py
Global configuration for INDODAX AI Trading Bot
Comments are in English.
"""

# =========================
# EXCHANGE
# =========================
EXCHANGE_NAME = "indodax"
TIMEZONE = "Asia/Jakarta"

# =========================
# API
# =========================
API_KEY = ""
API_SECRET = ""

# =========================
# SCANNER
# =========================
SCAN_INTERVAL = 60
SCAN_LIMIT = 200

TIMEFRAME_ENTRY = "15m"
TIMEFRAME_H1 = "1h"
TIMEFRAME_H4 = "4h"

EXCLUDED_COINS = [
    "USDT",
    "USDC",
    "BIDR",
    "IDRT"
]

MIN_VOLUME_IDR = 50_000_000
MAX_SPREAD_PERCENT = 1.5

# =========================
# BUY
# =========================
BASE_TRADE_AMOUNT = 50_000
MAX_ACTIVE_TRADES = 3
MAX_LAYER_PER_COIN = 3
BUY_SLIPPAGE = 0.001

# =========================
# SELL
# =========================
DEFAULT_TAKE_PROFIT = 8.0
DEFAULT_STOP_LOSS = 5.0
TRAILING_GAP = 2.0
SELL_RETRY = 5

# =========================
# TIMEOUT
# =========================
TIMEOUT_WEAK_HOURS = 24
TIMEOUT_STALE_HOURS = 48
TIMEOUT_MAX_HOURS = 72

# =========================
# SMART SL
# =========================
SMART_SL_CONFIRM_SECONDS = 60
EMERGENCY_STOP_LOSS = -9.0

# =========================
# RISK
# =========================
MAX_TRADE_PER_DAY = 20
MAX_DAILY_LOSS_PERCENT = 10
PORTFOLIO_HEAT = 0.30

# =========================
# COOLDOWN
# =========================
COOLDOWN_AFTER_SL = 900
COOLDOWN_AFTER_TIMEOUT = 1800
COOLDOWN_AFTER_TRAILING = 300

# =========================
# LOGGING
# =========================
LOG_LEVEL = "INFO"

# =========================
# FILES
# =========================
ACTIVE_TRADES_FILE = "active_trades.json"
HISTORY_FILE = "history.json"
COOLDOWN_FILE = "cooldown.json"
CONFIG_FILE = "config.json"
