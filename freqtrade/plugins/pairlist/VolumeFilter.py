"""
Price pair list filter
"""
import logging
from typing import Any, Dict

from freqtrade.exceptions import OperationalException
from freqtrade.plugins.pairlist.IPairList import IPairList


logger = logging.getLogger(__name__)


class VolumeFilter(IPairList):

    def __init__(self, exchange, pairlistmanager,
                 config: Dict[str, Any], pairlistconfig: Dict[str, Any],
                 pairlist_pos: int) -> None:
        super().__init__(exchange, pairlistmanager, config, pairlistconfig, pairlist_pos)

        self.min_volume = pairlistconfig.get('min_volume', 0)
        self.max_volume = pairlistconfig.get('max_volume', 0)
        if self.min_volume < 0:
            raise OperationalException("VolumeFilter requires min_volume to be >= 0")
        if self.max_volume < 0:
            raise OperationalException("VolumeFilter requires max_volume to be >= 0")
        self._enabled = (self.min_volume > 0 or self.max_volume > 0)

    @property
    def needstickers(self) -> bool:
        """
        Boolean property defining if tickers are necessary.
        If no Pairlist requires tickers, an empty Dict is passed
        as tickers argument to filter_pairlist
        """
        return True

    def short_desc(self) -> str:
        """
        Short whitelist method description - used for startup-messages
        """
        return f"{self.name} - Filtering pairs below {self.min_volume:.8f} and above {self.max_volume:.8f} volume."

    def _validate_pair(self, pair: str, ticker: Dict[str, Any]) -> bool:
        """
        Check if if one price-step (pip) is > than a certain barrier.
        :param pair: Pair that's currently validated
        :param ticker: ticker dict as returned from ccxt.load_markets()
        :return: True if the pair can stay, false if it should be removed
        """
        if ticker['last'] is None or ticker['last'] == 0:
            self.log_once(f"Removed {pair} from whitelist, because "
                          "ticker['last'] is empty (Usually no trade in the last 24h).",
                          logger.info)
            return False

        # Perform min_volume check.
        if self.min_volume != 0:
            if ticker['quoteVolume'] < self.min_volume:
                self.log_once(f"Removed {pair} from whitelist, "
                              f"because 24h volume < {self.min_volume:.8f}", logger.info)
                return False

        # Perform max_volume check.
        if self.max_volume != 0:
            if ticker['quoteVolume'] > self.max_volume:
                self.log_once(f"Removed {pair} from whitelist, "
                              f"because 24h volume < {self.max_volume:.8f}", logger.info)
                return False

        return True
