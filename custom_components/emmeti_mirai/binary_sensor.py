"""Binary sensor platform for Emmeti Mirai."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
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
    registers = REGISTERS_BY_ENTITY_TYPE.get("binary_sensor", [])
    async_add_entities(
        EmmetiMiraiBinarySensor(coordinator, entry, reg) for reg in registers
    )


class EmmetiMiraiBinarySensor(EmmetiMiraiEntity, BinarySensorEntity):
    def __init__(self, coordinator, config_entry, register) -> None:
        super().__init__(coordinator, config_entry, register)
        dc = register.get("device_class")
        if dc:
            try:
                self._attr_device_class = BinarySensorDeviceClass(dc)
            except ValueError:
                self._attr_device_class = None

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get(self._key)
        return bool(val) if val is not None else None
