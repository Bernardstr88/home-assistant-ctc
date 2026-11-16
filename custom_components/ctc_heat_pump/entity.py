"""Base entities for the CTC Heat Pump integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MODEL,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    MODEL_OPTIONS,
)
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
        entry = self.coordinator.config_entry
        model = entry.options.get(
            CONF_MODEL,
            entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        )
        return DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL_OPTIONS.get(model, MODEL_OPTIONS[DEFAULT_MODEL]),
            name=DEFAULT_NAME,
        )
