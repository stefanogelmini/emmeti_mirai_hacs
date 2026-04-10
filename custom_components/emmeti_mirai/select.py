"""Select platform for Emmeti Mirai (operating mode)."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REGISTERS_BY_ENTITY_TYPE
from .coordinator import EmmetiMiraiCoordinator
from .entity_base import EmmetiMiraiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: EmmetiMiraiCoordinator = hass.data[DOMAIN][entry.entry_id]
    registers = REGISTERS_BY_ENTITY_TYPE.get("select", [])
    async_add_entities(
        EmmetiMiraiSelect(coordinator, entry, reg) for reg in registers
    )


class EmmetiMiraiSelect(EmmetiMiraiEntity, SelectEntity):
    def __init__(self, coordinator, config_entry, register) -> None:
        super().__init__(coordinator, config_entry, register)
        self._options_map: dict[int, str] = register.get("options", {})
        self._reverse_map: dict[str, int] = {v: k for k, v in self._options_map.items()}
        self._attr_options = list(self._options_map.values())

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        return self._options_map.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        raw = self._reverse_map.get(option)
        if raw is None:
            _LOGGER.error("Unknown option '%s' for %s", option, self._key)
            return
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, self._key, raw
        )
        if success:
            await self.coordinator.async_request_refresh()
