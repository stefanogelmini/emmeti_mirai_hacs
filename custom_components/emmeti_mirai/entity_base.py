"""Base entity for Emmeti Mirai."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import EmmetiMiraiCoordinator


class EmmetiMiraiEntity(CoordinatorEntity[EmmetiMiraiCoordinator]):
    """Base class shared by all Emmeti Mirai entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EmmetiMiraiCoordinator,
        config_entry: ConfigEntry,
        register: dict,
    ) -> None:
        super().__init__(coordinator)
        self._register = register
        self._key = register["key"]
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{self._key}"
        self._attr_name = register["name"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info shared across all entities."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Emmeti",
            model="Mirai",
            configuration_url=f"http://{self._config_entry.data['host']}",
        )
