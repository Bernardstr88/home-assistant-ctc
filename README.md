# CTC Heat Pump

Home Assistant custom integration for CTC heat pumps over Modbus TCP.

This integration is built around CTC EcoZenith / Eco-series style BMS registers
and uses local polling over Modbus TCP. It does not depend on Home Assistant's
YAML Modbus integration and does not require external Python packages.

## Features

- UI setup flow
- Local Modbus TCP polling using FC3 read holding registers
- FC6 single-register writes for writable CTC parameters
- Temperature, COP, status, DHW, brine, return/supply and power sensors
- GSi/CTC GS DHW controls and five-point HC1 heating-curve controls
- Number controls for heating curve and heater limits
- SmartGrid mode select on register `1100`
- User-selected CTC product family recorded in the Home Assistant device info

## Default Connection

| Field | Default |
| --- | --- |
| Host | `192.168.0.222` |
| Port | `502` |
| Slave ID | `1` |
| Scan interval | `30` seconds |

Select **CTC GSi 612** (or the broader **GSi / CTC GS** family) during setup
for a GSi 612. The selection is stored in the integration and shown in Home
Assistant's device info; it can be changed later in the integration options.

## Curated model-specific registers

The full CTC BMS guide contains far more codes than the integration should
create as Home Assistant entities. `registers.py` remains the curated source of
entity definitions: each sensor or control there is a deliberate choice of
address, data type, scaling, units, and (for controls) write range. Do not
turn the full extracted PDF table into entities automatically.

`model_support.py` provides the compatibility allowlist. Add a register key to
`REGISTER_COMPATIBILITY` only after confirming the code's model range in the
manual or on a device. For example:

```python
REGISTER_COMPATIBILITY = {
    "some_curated_sensor": frozenset({"gsi_ctc_gs"}),
}
