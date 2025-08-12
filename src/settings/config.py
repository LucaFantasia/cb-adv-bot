"""
config.py — Central config entry point

Combines strategy, candle, and backtest settings into a single import.
Use this file to access all global settings throughout the bot.
"""

from settings.backtest_config import backtest_config
from settings.candle_config import candle_config
from settings.strategy_config import strategy_config


class Config:
    strategy = strategy_config
    candle = candle_config
    backtest = backtest_config


config = Config()
