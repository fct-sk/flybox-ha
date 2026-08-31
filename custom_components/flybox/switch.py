from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    async_add_entities(
        [
            FlyboxWifiSwitch(
                coordinator,
                client,
                entry,
                "wifi_state_0",
                "Wi-Fi 2,4 GHz",
            ),
            FlyboxWifiSwitch(
                coordinator,
                client,
                entry,
                "wifi_state_1",
                "Guest Wi-Fi 2,4 GHz",
            ),
            FlyboxWifiSwitch(
                coordinator,
                client,
                entry,
                "wifi_state_2",
                "Wi-Fi 5 GHz",
            ),
        ]
    )


class FlyboxWifiSwitch(
    CoordinatorEntity,
    SwitchEntity,
):
    def __init__(
        self,
        coordinator,
        client,
        entry,
        key,
        name,
    ):
        super().__init__(coordinator)

        self.client = client
        self._key = key

        self._attr_name = f"Flybox {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}_switch"
        self._attr_icon = "mdi:wifi"

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
        return (
            self.coordinator.data.get(self._key)
            == "ap_enable"
        )

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.client.set_wifi_state,
            self._key,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.client.set_wifi_state,
            self._key,
            False,
        )
        await self.coordinator.async_request_refresh()
