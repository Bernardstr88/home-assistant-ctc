"""Base entities for the CTC Heat Pump integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import CtcDataUpdateCoordinator


class CtcEntity(CoordinatorEntity[CtcDataUpdateCoordinator]):
    """Base CTC entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CtcDataUpdateCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )
