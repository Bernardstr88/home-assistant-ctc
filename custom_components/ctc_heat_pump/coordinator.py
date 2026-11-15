"""Data coordinator for the CTC Heat Pump integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    DEFAULT_SENSOR_READ_TIMEOUT,
)
from .modbus import (
    CtcConnectionError,
    CtcModbusClient,
    CtcModbusError,
    decode_float32,
    decode_int16,
    decode_uint16,
)
from .registers import (
    NUMBER_REGISTERS,
    SENSOR_REGISTERS,
    SMARTGRID_REGISTER,
    NumberRegister,
    RegisterType,
    SensorRegister,
)

_LOGGER = logging.getLogger(__name__)

@dataclass(slots=True)
class CtcData:
    """Current CTC data."""
    sensors: dict[str, int | float | None]
    numbers: dict[str, float | None]
    smartgrid_raw: int | None

class CtcDataUpdateCoordinator(DataUpdateCoordinator[CtcData]):
    """Class to manage fetching CTC data."""
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.client = CtcModbusClient(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, 502),
            slave_id=entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
        )
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> CtcData:
        """Fetch data from the heat pump."""
        try:
            return await self.hass.async_add_executor_job(self._read_all)
        except (CtcConnectionError, CtcModbusError) as err:
            raise UpdateFailed(str(err)) from err

    def close(self) -> None:
        """Close the underlying client."""
        self.client.close()

    def _read_all(self) -> CtcData:
        # 1. Sensor query with timeout
        sensors = {}
        for register in SENSOR_REGISTERS:
            try:
                sensors[register.key] = self._read_sensor(register)
            except Exception as err:
                # If a sensor fails, we logg it, but we don't block the whole system
                _LOGGER.error("Error reading sensor %s", register.key, err)
                continue
            finally:
                time.sleep(DEFAULT_SENSOR_READ_TIMEOUT) # Pause after each sensor read, default 150ms

        # 2. Numbers (settings value) with timeout query
        numbers = {}
        for register in NUMBER_REGISTERS:
            try:
                numbers[register.key] = self._read_number(register)
            except Exception as err:
                _LOGGER.error("Error reading numbers %s: %s", register.key, err)
                continue
            finally:
                time.sleep(DEFAULT_SENSOR_READ_TIMEOUT) # Pause after each sensor read, default 150ms
        # 3. SmartGrid-Register query
        try:
            smartgrid_raw = self.client.read_registers(SMARTGRID_REGISTER, 1)[0]
        except CtcModbusError:
            smartgrid_raw = None
        finally:
            time.sleep(DEFAULT_SENSOR_READ_TIMEOUT)

        return CtcData(
            sensors=sensors,
            numbers=numbers,
            smartgrid_raw=smartgrid_raw,
        )

    def _read_sensor(self, register: SensorRegister) -> int | float | None:
        """Read a sensor register."""
        try:
            words = self.client.read_registers(register.address, register.count)
        except CtcModbusError:
            return None
        value = _decode_value(register.data_type, words)
        return round(value * register.scale, 3)

    def _read_number(self, register: NumberRegister) -> float | None:
        """Read a number register."""
        try:
            words = self.client.read_registers(register.address, 1)
        except CtcModbusError:
            return None
        value = _decode_value(register.data_type, words)
        return round(value * register.scale, 3)

    def write_scaled_number(self, register: NumberRegister, value: float) -> None:
        """Write a scaled number register via FC6."""
        raw = round(value / register.scale)
        self.client.write_register(register.address, raw)

    def write_smartgrid(self, value: int) -> None:
        """Write SmartGrid mode register via FC6."""
        self.client.write_register(SMARTGRID_REGISTER, value)

def _decode_value(data_type: RegisterType, words: list[int]) -> int | float:
    """Decode register words."""
    if data_type == RegisterType.INT16:
        return decode_int16(words[0])
    if data_type == RegisterType.UINT16:
        return decode_uint16(words[0])
    if data_type == RegisterType.FLOAT32:
        return decode_float32(words)
    raise ValueError(f"Unsupported data type: {data_type}")
