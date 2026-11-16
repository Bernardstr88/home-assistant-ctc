"""Model compatibility for curated CTC BMS register definitions.

The BMS PDF contains many more codes than the integration should expose. Keep
compatibility here limited to codes that the integration actually defines in
``registers.py``. Keys omitted from the compatibility table retain the legacy
shared-register behavior until their model support has been checked against the
manual or a real device. This avoids silently hiding existing entities while
allowing confirmed model-specific entries to be declared explicitly.
"""

from __future__ import annotations

from collections.abc import Iterable

from homeassistant.config_entries import ConfigEntry

from .const import CONF_MODEL, DEFAULT_MODEL

# Register key -> model identifiers verified to implement that code.
# Use a frozenset so the compatibility data is immutable at runtime. Add keys
# only for curated integration registers; do not import the entire PDF table.
REGISTER_COMPATIBILITY: dict[str, frozenset[str]] = {}


def selected_model(entry: ConfigEntry) -> str:
    """Return the model selected in options, falling back to setup data."""
    return entry.options.get(
        CONF_MODEL,
        entry.data.get(CONF_MODEL, DEFAULT_MODEL),
    )


def is_compatible(register_key: str, model: str) -> bool:
    """Return whether a curated code is known to apply to the selected model.

    An omitted key is treated as a legacy shared definition. Once a key has
    verified compatibility metadata, it is only exposed for the listed models.
    """
    compatible_models = REGISTER_COMPATIBILITY.get(register_key)
    return compatible_models is None or model in compatible_models


def compatible_registers(registers: Iterable, model: str) -> tuple:
    """Filter register definitions to those available for one model."""
    return tuple(
        register
        for register in registers
        if is_compatible(register.key, model)
    )

