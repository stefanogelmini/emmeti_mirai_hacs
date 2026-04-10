"""Number platform for Emmeti Mirai (writable setpoints)."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
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
    registers = REGISTERS_BY_ENTITY_TYPE.get("number", [])
    async_add_entities(
        EmmetiMiraiNumber(coordinator, entry, reg) for reg in registers
    )


class EmmetiMiraiNumber(EmmetiMiraiEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, config_entry, register) -> None:
        super().__init__(coordinator, config_entry, register)
        self._attr_native_unit_of_measurement = register.get("unit")
        self._attr_native_min_value = register.get("min_value", 0)
        self._attr_native_max_value = register.get("max_value", 100)
        self._attr_native_step = register.get("step", 1)
        dc = register.get("device_class")
        if dc:
            try:
                self._attr_device_class = NumberDeviceClass(dc)
            except ValueError:
                self._attr_device_class = None

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, self._key, value
        )
        if success:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write %s = %s", self._key, value)
