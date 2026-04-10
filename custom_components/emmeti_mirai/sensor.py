"""Sensor platform for Emmeti Mirai."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, REGISTERS_BY_ENTITY_TYPE
from .coordinator import EmmetiMiraiCoordinator
from .entity_base import EmmetiMiraiEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: EmmetiMiraiCoordinator = hass.data[DOMAIN][entry.entry_id]
    registers = REGISTERS_BY_ENTITY_TYPE.get("sensor", [])
    async_add_entities(
        EmmetiMiraiSensor(coordinator, entry, reg) for reg in registers
    )


class EmmetiMiraiSensor(EmmetiMiraiEntity, SensorEntity):
    def __init__(self, coordinator, config_entry, register) -> None:
        super().__init__(coordinator, config_entry, register)
        self._attr_native_unit_of_measurement = register.get("unit")
        dc = register.get("device_class")
        if dc:
            try:
                self._attr_device_class = SensorDeviceClass(dc)
            except ValueError:
                self._attr_device_class = None
        sc = register.get("state_class")
        if sc:
            try:
                self._attr_state_class = SensorStateClass(sc)
            except ValueError:
                self._attr_state_class = None

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key) if self.coordinator.data else None
