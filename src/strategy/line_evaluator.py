"""
line_evaluator.py
"""


def is_near_line(price: float, proj_price: float, deviation_pct: float) -> bool:
    return proj_price * (1 - 2 * deviation_pct) <= price <= proj_price * (1 + 2 * deviation_pct)


def intersects_support_line(
    candle_high: float, candle_low: float, proj_price: float, deviation_pct: float
) -> bool:
    return candle_high >= (proj_price * (1 - 2 * deviation_pct)) and candle_low <= (
        proj_price * (1 + 2 * deviation_pct)
    )


def calc_sell_price(support_price: float, resistance_price: float) -> float:
    return (resistance_price - support_price) * 0.7 + support_price


def default_exit_price(entry_price: float, stop_loss_pct: float) -> float:
    max_price = entry_price * (1 + 2 * stop_loss_pct)
    return (max_price - entry_price) * 0.7 + entry_price
