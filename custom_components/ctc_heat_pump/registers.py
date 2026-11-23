"""Register definitions for the CTC Heat Pump integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RegisterType(StrEnum):
    """Supported register data types."""

    INT16 = "int16"
    UINT16 = "uint16"
    FLOAT32 = "float32"


@dataclass(frozen=True, slots=True)
class SensorRegister:
    """Read-only sensor register definition."""

    key: str
    name: str
    address: int
    data_type: RegisterType
    count: int = 1
    scale: float = 1.0
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    enabled_default: bool = True


@dataclass(frozen=True, slots=True)
class NumberRegister:
    """Read/write number register definition."""

    key: str
    name: str
    address: int
    data_type: RegisterType
    scale: float
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    device_class: str | None = None


SENSOR_REGISTERS: tuple[SensorRegister, ...] = (
    SensorRegister("lower_heater_feedback", "Lower heater feedback", 61590, RegisterType.INT16, scale=0.1, unit="kW", device_class="power", state_class="measurement"),
    SensorRegister("upper_heater_feedback", "Upper heater feedback", 61591, RegisterType.INT16, scale=0.1, unit="kW", device_class="power", state_class="measurement"),
    SensorRegister("outdoor_temperature", "Outdoor temperature", 62000, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("dhw_stop_temperature", "DHW stop temperature", 62001, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("hot_water_temperature", "Hot water temperature", 62003, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("dhw_upper_temperature", "DHW upper temperature", 62276, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("dhw_capacity", "DHW capacity", 62279, RegisterType.UINT16, scale=1.0, unit="%", state_class="measurement"),
    SensorRegister("system_status", "System status", 62005, RegisterType.UINT16),
    SensorRegister("radiator_water_temperature", "Radiator water temperature", 62006, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("hc1_supply_temperature", "HC1 supply temperature", 62011, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("return_temperature", "Return temperature", 62015, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("brine_in_temperature", "Heat pump 1 brine in temperature", 62087, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("brine_out_temperature", "Heat pump 1 brine out temperature", 62097, RegisterType.INT16, scale=0.1, unit="°C", device_class="temperature", state_class="measurement"),
    SensorRegister("heat_pump_status", "Heat pump status", 62100, RegisterType.UINT16),
    SensorRegister("active_cooling_demand", "Active cooling demand", 62322, RegisterType.UINT16),
    SensorRegister("immersion_heater_power", "Immersion heater power", 62361, RegisterType.UINT16, scale=0.1, unit="kW", device_class="power", state_class="measurement"),
    SensorRegister("dhw_bottom_temperature", "DHW bottom temperature", 62362, RegisterType.FLOAT32, count=2, unit="°C", device_class="temperature", state_class="measurement", enabled_default=False),
    SensorRegister("cop_heating", "COP heating", 65004, RegisterType.UINT16, scale=0.01, state_class="measurement"),
    SensorRegister("cop_hot_water", "COP hot water", 65005, RegisterType.UINT16, scale=0.01, state_class="measurement"),
    SensorRegister("cop_total", "COP total", 65006, RegisterType.UINT16, scale=0.01, state_class="measurement"),
    SensorRegister("info_code", "Info code", 65061, RegisterType.UINT16),
    SensorRegister("dhw_charge_active", "DHW charge active", 65068, RegisterType.INT16),
    SensorRegister("dhw_setpoint_float", "DHW setpoint float", 65069, RegisterType.FLOAT32, count=2, unit="°C", device_class="temperature", state_class="measurement", enabled_default=False),
    SensorRegister("dhw_diff", "DHW diff", 65070, RegisterType.FLOAT32, count=2, unit="°C", device_class="temperature", state_class="measurement", enabled_default=False),
    SensorRegister("dhw_extra_charge", "DHW extra charge", 65071, RegisterType.INT16),
    SensorRegister("hp1_power_consumption", "Heat pump 1 power consumption", 62331, RegisterType.UINT16, scale=0.1, unit="kW", device_class="power", state_class="measurement"),
)

NUMBER_REGISTERS: tuple[NumberRegister, ...] = (
    NumberRegister("dhw_manual_stop_temperature", "DHW manual stop temperature", 61501, RegisterType.INT16, 0.1, 40, 65, 0.5, "°C", "temperature"),
    NumberRegister("dhw_setpoint", "DHW setpoint", 61502, RegisterType.INT16, 0.1, 35, 65, 0.5, "°C", "temperature"),
    NumberRegister("dhw_minimum_temperature", "DHW minimum temperature", 61503, RegisterType.INT16, 0.1, 30, 60, 0.5, "°C", "temperature"),
    NumberRegister("dhw_comfort_boost", "DHW comfort boost", 61506, RegisterType.INT16, 0.1, 0, 15, 0.5, "°C", "temperature"),
    NumberRegister("room_temp_setpoint_hc1", "Room temperature setpoint HC1", 61509, RegisterType.INT16, 0.1, 16, 24, 0.5, "°C", "temperature"),
    NumberRegister("heating_curve_slope_hc1", "Heating curve slope HC1", 61513, RegisterType.INT16, 0.1, 0.5, 3.0, 0.1),
    NumberRegister("buffer_min_temperature", "Buffer minimum temperature", 61515, RegisterType.INT16, 0.1, 30, 60, 0.5, "°C", "temperature"),
    NumberRegister("room_temp_night_reduction_hc1", "Room temperature night reduction HC1", 61520, RegisterType.INT16, 0.1, 0, 8, 0.5, "°C", "temperature"),
    NumberRegister("max_lower_heater_power", "Maximum lower heater power", 61590, RegisterType.INT16, 0.1, 0, 9, 0.1, "kW", "power"),
    NumberRegister("max_upper_heater_power", "Maximum upper heater power", 61591, RegisterType.INT16, 0.1, 0, 9, 0.1, "kW", "power"),
    NumberRegister("dhw_stop_temperature_control", "DHW stop temperature", 62001, RegisterType.INT16, 0.1, 40, 65, 0.5, "°C", "temperature"),
    NumberRegister("hc1_curve_point_1_outdoor", "HC1 curve point 1 outdoor temperature", 61675, RegisterType.INT16, 1.0, -40, 30, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_1_supply", "HC1 curve point 1 supply temperature", 61676, RegisterType.INT16, 1.0, 20, 80, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_2_outdoor", "HC1 curve point 2 outdoor temperature", 61677, RegisterType.INT16, 1.0, -40, 30, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_2_supply", "HC1 curve point 2 supply temperature", 61678, RegisterType.INT16, 1.0, 20, 80, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_3_outdoor", "HC1 curve point 3 outdoor temperature", 61679, RegisterType.INT16, 1.0, -40, 30, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_3_supply", "HC1 curve point 3 supply temperature", 61680, RegisterType.INT16, 1.0, 20, 80, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_4_outdoor", "HC1 curve point 4 outdoor temperature", 61681, RegisterType.INT16, 1.0, -40, 30, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_4_supply", "HC1 curve point 4 supply temperature", 61682, RegisterType.INT16, 1.0, 20, 80, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_5_outdoor", "HC1 curve point 5 outdoor temperature", 61683, RegisterType.INT16, 1.0, -40, 30, 1, "°C", "temperature"),
    NumberRegister("hc1_curve_point_5_supply", "HC1 curve point 5 supply temperature", 61684, RegisterType.INT16, 1.0, 20, 80, 1, "°C", "temperature"),
)

SMARTGRID_REGISTER = 1100
SMARTGRID_OPTIONS = {
    "Normal": 0,
    "SmartGrid A / Blocking": 64,
    "SmartGrid B / Forced": 128,
    "SmartGrid A+B / Overcapacity": 192,
}
