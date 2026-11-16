# CTC Heat Pump

Home Assistant custom integration for CTC heat pumps over Modbus TCP.

This integration is built around CTC EcoZenith / Eco-series style BMS registers
and uses local polling over Modbus TCP. It does not depend on Home Assistant's
YAML Modbus integration and does not require external Python packages.

## Features

- UI setup flow
- Local Modbus TCP polling using FC3 read holding registers
- FC6 single-register writes for writable CTC parameters
- Temperature, COP, status and DHW sensors
- Number controls for DHW, heating curve and heater limits
- SmartGrid mode select on register `1100`
- User-selected CTC product family recorded in the Home Assistant device info

## Default Connection

| Field | Default |
| --- | --- |
| Host | `192.168.0.222` |
| Port | `502` |
| Slave ID | `1` |
| Scan interval | `30` seconds |

During setup, select the product family from the model list in the CTC BMS code
table. The table labels the GSi family as **GSi / CTC GS**, which is the choice
for a GSi 612. Choose **Other / not listed** if you are unsure. The selection
is saved on the integration and shown as the device model in Home Assistant;
it can be changed later from the integration's options.

The BMS documentation does not expose a reliable model-identification register,
so the integration cannot automatically determine the model. The current
register/entity definitions are still shared across selected families; the
model selection records the user's identification and does not yet filter
entities by model-specific register availability. Validate registers against
your heat pump before relying on them, especially writable controls.

The config flow checks whether the TCP port is reachable. The first real Modbus
register read happens when Home Assistant sets up the integration.

## Register Notes

The CTC BMS map uses holding registers with offset `0`.

- Read: FC3
- Write: FC6
- Byte order: big-endian
- Word order for `float32`: big-endian, AB CD

SmartGrid register:

| Value | Meaning |
| ---: | --- |
| `0` | Normal |
| `64` | SmartGrid A / Blocking |
| `128` | SmartGrid B / Forced |
| `192` | SmartGrid A+B / Overcapacity |

Some high register addresses are known to differ between CTC models. The
float32 DHW sensors around `62361` and `65069` are disabled by default until
validated on a live installation.

## Installation With HACS

Add this repository as a custom repository:

```text
https://github.com/William-Wolke/home-assistant-ctc
