"""Sensors for the CTC Heat Pump integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import CtcDataUpdateCoordinator
from .entity import CtcEntity
from .registers import SENSOR_REGISTERS, SensorRegister


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CTC sensors."""
    coordinator: CtcDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        CtcSensor(coordinator, register) for register in SENSOR_REGISTERS
    )


class CtcSensor(CtcEntity, SensorEntity):
    """CTC sensor."""

    def __init__(
        self,
        coordinator: CtcDataUpdateCoordinator,
        register: SensorRegister,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, register.key)
        self.register = register
        self.entity_description = SensorEntityDescription(
            key=register.key,
            name=register.name,
            native_unit_of_measurement=register.unit,
            device_class=register.device_class,
            state_class=register.state_class,
            entity_registry_enabled_default=register.enabled_default,
        )

    @property
    def native_value(self) -> int | float | None:
        """Return the sensor state."""
        return self.coordinator.data.sensors.get(self.register.key)
