"""Select entities for the CTC Heat Pump integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import CtcDataUpdateCoordinator
from .entity import CtcEntity
from .registers import SMARTGRID_OPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CTC selects."""
    coordinator: CtcDataUpdateCoordinator = entry.runtime_data
    async_add_entities([CtcSmartGridSelect(coordinator)])


class CtcSmartGridSelect(CtcEntity, SelectEntity):
    """SmartGrid mode select."""

    _attr_name = "SmartGrid mode"
    _attr_translation_key = "smartgrid_mode"

    def __init__(self, coordinator: CtcDataUpdateCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "smartgrid_mode")
        self._attr_options = list(SMARTGRID_OPTIONS)

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        raw = self.coordinator.data.smartgrid_raw
        if raw is None:
            return None
        for option, value in SMARTGRID_OPTIONS.items():
            if value == raw:
                return option
        return None

    async def async_select_option(self, option: str) -> None:
        """Change selected option."""
        await self.hass.async_add_executor_job(
            self.coordinator.write_smartgrid,
            SMARTGRID_OPTIONS[option],
        )
        await self.coordinator.async_request_refresh()
