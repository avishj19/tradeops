"""Trade-log instrument universe spanning equities, commodities, options, and crypto."""
import re

# (asset_class, symbol, price_low, price_high) used by synthetic log generation.
INSTRUMENTS = [
    ('equity', 'AAPL', 170, 230),
    ('equity', 'MSFT', 380, 450),
    ('equity', 'NVDA', 100, 140),
    ('equity', 'SPY', 500, 560),
    ('equity', 'JPM', 180, 220),
    ('commodity', 'GC', 1900, 2500),   # gold futures root
    ('commodity', 'CL', 65, 95),       # WTI crude
    ('commodity', 'NG', 2.0, 6.0),     # natural gas
    ('commodity', 'SI', 20, 35),       # silver
    ('commodity', 'ZC', 400, 600),     # corn
    ('option', 'AAPL250919C00200000', 0.5, 25),
    ('option', 'MSFT250919P00400000', 0.5, 20),
    ('option', 'SPY250919C00550000', 0.5, 15),
    ('option', 'NVDA250919C00120000', 1.0, 30),
    ('crypto', 'BTCUSDT', 25000, 75000),
    ('crypto', 'ETHUSDT', 1500, 4500),
    ('crypto', 'SOLUSDT', 20, 250),
    ('crypto', 'XRPUSDT', 0.3, 2.5),
]

ASSET_CLASSES = ('equity', 'commodity', 'option', 'crypto')
SYMBOL_TO_CLASS = {symbol: asset_class for asset_class, symbol, *_ in INSTRUMENTS}
_COMMODITY_ROOTS = {symbol for asset_class, symbol, *_ in INSTRUMENTS if asset_class == 'commodity'}
_OCC_OPTION = re.compile(r'^[A-Z]{1,6}\d{6}[CP]\d{8}$')
_FUTURES_ROOT = re.compile(r'^(GC|CL|NG|SI|ZC|ZS|ZW|HG|PL|PA)[FGHJKMNQUVXZ]\d{1,2}$')
_CRYPTO_QUOTE = re.compile(r'^(BTC|ETH|SOL|XRP|BNB|ADA|DOGE|AVAX|DOT|LINK)(USDT|USD|USDC)$')


def normalize_asset_class(value):
    name = str(value).strip().lower()
    if name in {'equities', 'stock', 'stocks'}:
        return 'equity'
    if name in {'commodities', 'future', 'futures'}:
        return 'commodity'
    if name in {'options', 'opt'}:
        return 'option'
    if name in {'cryptocurrency', 'cryptocurrencies', 'digital_asset', 'digital_assets'}:
        return 'crypto'
    if name not in ASSET_CLASSES:
        raise ValueError('asset_class must be one of: ' + ', '.join(ASSET_CLASSES))
    return name


def infer_asset_class(symbol):
    """Best-effort classification for uploaded logs that omit asset_class."""
    s = str(symbol).strip().upper()
    if s in SYMBOL_TO_CLASS:
        return SYMBOL_TO_CLASS[s]
    if _OCC_OPTION.match(s) or s.startswith('OPT:'):
        return 'option'
    if s in _COMMODITY_ROOTS or _FUTURES_ROOT.match(s):
        return 'commodity'
    if _CRYPTO_QUOTE.match(s) or s.endswith('USDT') or s.endswith('USDC'):
        return 'crypto'
    return 'equity'
