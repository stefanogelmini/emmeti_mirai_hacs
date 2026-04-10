"""Switch platform for Emmeti Mirai (unit on/off)."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
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
    registers = REGISTERS_BY_ENTITY_TYPE.get("switch", [])
    async_add_entities(
        EmmetiMiraiSwitch(coordinator, entry, reg) for reg in registers
    )


class EmmetiMiraiSwitch(EmmetiMiraiEntity, SwitchEntity):
    def __init__(self, coordinator, config_entry, register) -> None:
        super().__init__(coordinator, config_entry, register)

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get(self._key)
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs) -> None:
        await self._write(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._write(False)

    async def _write(self, value: bool) -> None:
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, self._key, value
        )
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write %s = %s", self._key, value)
