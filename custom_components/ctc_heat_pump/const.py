"""Constants for the CTC Heat Pump integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "ctc_heat_pump"

DEFAULT_NAME = "CTC Heat Pump"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_TIMEOUT = 10
DEFAULT_SENSOR_READ_TIMEOUT = 0.150
MIN_SCAN_INTERVAL = 5

CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

MANUFACTURER = "CTC"

MIN_RAW_INT16 = -32768
MAX_RAW_INT16 = 32767
