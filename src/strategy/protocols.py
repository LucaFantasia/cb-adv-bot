from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from strategy.signals import Signal


class Strategy(Protocol):
    """
    A strategy consumes the latest candle (and optionally internal state) and emits Signals.
    It must be side-effect free except for its own internal state; order placement happens elsewhere.
    """

    name: str

    def on_candle(self, candle: dict[str, Any]) -> list[Signal]:
        """
        Inputs:
           - candle: A dict representing the latest candle, with keys like 'open', 'high', 'low', 'close', 'volume', 'timestamp', etc.

        Returns:
              - A list of Signal objects representing trade actions to take based on the candle data.
        """
        ...

    def reset(self) -> None:
        """
        Clear internal buffers/state.
        """
        ...
