from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [
            FlyboxInternetBinarySensor(
                coordinator,
                entry,
            )
        ]
    )


class FlyboxInternetBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):
    def __init__(
        self,
        coordinator,
        entry,
    ):
        super().__init__(coordinator)

        self._attr_name = "Flybox Internet"
        self._attr_unique_id = (
            f"{entry.entry_id}_internet"
        )
        self._attr_device_class = (
            BinarySensorDeviceClass.CONNECTIVITY
        )

        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, entry.entry_id)
            },
            "name": "Orange Flybox",
            "manufacturer": "MeiG",
            "model": "SRT858M",
        }

    @property
    def is_on(self):
        status = self.coordinator.data.get(
            "dialup_dial_status"
        )

        if status is None:
            return None

        return str(status).lower() == "connected"
