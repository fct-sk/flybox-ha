from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL


FLYBOX_KEYS = [
    "device_uptime",
    "rt_wwan_conn_info",
    "mnet_sysmode",
    "mnet_sig_level",
    "mnet_sim_status",
    "mnet_ca_status",
    "cm_display_type",
    "mnet_operator_name",

    "statistics_data_used",
    "statistics_used_tx",
    "statistics_data_used_r",
    "statistics_used_tx_r",
    "statistics_current_bytes",
    "statistics_tx_bytes_rate",
    "statistics_rx_bytes_rate",

    "dialup_dial_status",
    "mnet_roam_status",
    "sms_unread_count",
    "wifi_work_status",
    "wifi_client_0",
    "wifi_client_1",
    "wifi_client_2",
    "wifi_state_0",
    "wifi_state_1",
    "wifi_state_2",
]


class FlyboxCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        client,
    ):
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="Orange Flybox",
            update_interval=timedelta(
                seconds=DEFAULT_SCAN_INTERVAL
            ),
        )

        self.client = client

    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(
                self.client.get_params,
                FLYBOX_KEYS,
            )

            hosts = await self.hass.async_add_executor_job(
                self.client.get_hosts,
            )

            data["rt_hosts_count"] = hosts.get(
                "rt_hosts_count",
                0,
            )

            data["rt_hosts_list"] = hosts.get(
                "rt_hosts_list",
                [],
            )

            return data

        except Exception as err:
            raise UpdateFailed(
                f"Nepodarilo sa načítať údaje z Flyboxu: {err}"
            ) from err
