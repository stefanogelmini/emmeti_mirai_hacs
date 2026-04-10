"""DataUpdateCoordinator for Emmeti Mirai."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .modbus_client import EmmetiModbusClient

_LOGGER = logging.getLogger(__name__)


class EmmetiMiraiCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the Modbus device and distributes data to all entities."""

    config_entry: ConfigEntry  # type: ignore[assignment]

    def __init__(
        self,
        hass: HomeAssistant,
        client: EmmetiModbusClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch fresh data from the Modbus device (runs in executor)."""
        try:
            return await self.hass.async_add_executor_job(self.client.read_all)
        except ConnectionError as exc:
            raise UpdateFailed(f"Modbus connection error: {exc}") from exc
        except Exception as exc:  # pylint: disable=broad-except
            raise UpdateFailed(f"Unexpected error: {exc}") from exc
