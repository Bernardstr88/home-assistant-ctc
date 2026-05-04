"""Number entities for the CTC Heat Pump integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import CtcDataUpdateCoordinator
from .entity import CtcEntity
from .registers import NUMBER_REGISTERS, NumberRegister


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CTC numbers."""
    coordinator: CtcDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        CtcNumber(coordinator, register) for register in NUMBER_REGISTERS
    )


class CtcNumber(CtcEntity, NumberEntity):
    """CTC number."""

    def __init__(
        self,
        coordinator: CtcDataUpdateCoordinator,
        register: NumberRegister,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, register.key)
        self.register = register
        self.entity_description = NumberEntityDescription(
            key=register.key,
            name=register.name,
            native_unit_of_measurement=register.unit,
            device_class=register.device_class,
        )
        self._attr_native_min_value = register.min_value
        self._attr_native_max_value = register.max_value
        self._attr_native_step = register.step
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.numbers.get(self.register.key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        await self.hass.async_add_executor_job(
            self.coordinator.write_scaled_number,
            self.register,
            value,
        )
        await self.coordinator.async_request_refresh()
