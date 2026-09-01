from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.const import UnitOfDataRate
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


SENSORS = {
    "mnet_operator_name": {
        "name": "Operátor",
        "icon": "mdi:cellphone-wireless",
    },
    "mnet_sysmode": {
        "name": "Sieť",
        "icon": "mdi:signal-4g",
    },
    "cm_display_type": {
        "name": "Typ siete",
        "icon": "mdi:network",
    },
    "mnet_sig_level": {
        "name": "Signál",
        "icon": "mdi:signal",
    },
    "mnet_sim_status": {
        "name": "SIM stav",
        "icon": "mdi:sim",
    },
    "mnet_ca_status": {
        "name": "Carrier Aggregation",
        "icon": "mdi:access-point-network",
    },
    "wifi_work_status": {
        "name": "Wi-Fi stav",
        "icon": "mdi:wifi",
    },
    "sms_unread_count": {
        "name": "Neprečítané SMS",
        "icon": "mdi:message-text",
    },

}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    for key, description in SENSORS.items():
        entities.append(
            FlyboxSensor(
                coordinator,
                entry,
                key,
                description,
            )
        )

    entities.append(
        FlyboxUptimeSensor(
            coordinator,
            entry,
        )
    )

    entities.append(
        FlyboxConnectionTimeSensor(
            coordinator,
            entry,
        )
    )

    entities.append(
        FlyboxConnectedDevicesSensor(
            coordinator,
            entry,
        )
    )

    entities.append(
        FlyboxAllHostsSensor(
            coordinator,
            entry,
        )
    )

    entities.extend(
        [
            FlyboxTotalDataSensor(
                coordinator,
                entry,
            ),
            FlyboxDownloadSensor(
                coordinator,
                entry,
            ),
            FlyboxUploadSensor(
                coordinator,
                entry,
            ),
            FlyboxRoamingDownloadSensor(
                coordinator,
                entry,
            ),
            FlyboxRoamingUploadSensor(
                coordinator,
                entry,
            ),
        ]
    )

    entities.append(
        FlyboxRateSensor(
            coordinator,
            entry,
            "statistics_tx_bytes_rate",
            "Upload rýchlosť",
            "mdi:upload-network",
        )
    )

    entities.append(
        FlyboxRateSensor(
            coordinator,
            entry,
            "statistics_rx_bytes_rate",
            "Download rýchlosť",
            "mdi:download-network",
        )
    )
    async_add_entities(entities)



class FlyboxBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    def __init__(
        self,
        coordinator,
        entry,
        key,
        name,
    ):
        super().__init__(coordinator)

        self._key = key

        self._attr_name = f"Flybox {name}"
        self._attr_unique_id = (
            f"{entry.entry_id}_{key}"
        )

        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, entry.entry_id)
            },
            "name": "Orange Flybox",
            "manufacturer": "MeiG",
            "model": "SRT858M",
        }


class FlyboxSensor(FlyboxBaseSensor):
    def __init__(
        self,
        coordinator,
        entry,
        key,
        description,
    ):
        super().__init__(
            coordinator,
            entry,
            key,
            description["name"],
        )

        self._attr_icon = description.get("icon")

    @property
    def native_value(self):
        return self.coordinator.data.get(
            self._key
        )


class FlyboxUptimeSensor(FlyboxBaseSensor):
    def __init__(
        self,
        coordinator,
        entry,
    ):
        super().__init__(
            coordinator,
            entry,
            "device_uptime",
            "Uptime",
        )

        self._attr_icon = "mdi:timer-outline"
        self._attr_native_unit_of_measurement = "h"

    @property
    def native_value(self):
        value = self.coordinator.data.get(
            "device_uptime"
        )

        if value is None:
            return None

        try:
            return round(
                float(value) / 3600,
                1,
            )
        except (TypeError, ValueError):
            return None


class FlyboxTotalDataSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "statistics_data_used",
            "Dáta celkom",
        )

        self._attr_icon = "mdi:database"
        self._attr_native_unit_of_measurement = "GB"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def native_value(self):
        value = self.coordinator.data.get(
            "statistics_data_used"
        )

        if value is None:
            return None

        try:
            return round(
                float(value) / 1_000_000_000,
                2,
            )
        except (TypeError, ValueError):
            return None


class FlyboxDownloadSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "download_data",
            "Download",
        )

        self._attr_icon = "mdi:download"
        self._attr_native_unit_of_measurement = "GB"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def native_value(self):
        total = self.coordinator.data.get(
            "statistics_data_used"
        )
        upload = self.coordinator.data.get(
            "statistics_used_tx"
        )

        if total is None or upload is None:
            return None

        try:
            download = float(total) - float(upload)

            return round(
                download / 1_000_000_000,
                2,
            )
        except (TypeError, ValueError):
            return None


class FlyboxUploadSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "statistics_used_tx",
            "Upload",
        )

        self._attr_icon = "mdi:upload"
        self._attr_native_unit_of_measurement = "GB"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def native_value(self):
        value = self.coordinator.data.get(
            "statistics_used_tx"
        )

        if value is None:
            return None

        try:
            return round(
                float(value) / 1_000_000_000,
                2,
            )
        except (TypeError, ValueError):
            return None

class FlyboxRoamingDownloadSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "roaming_download_data",
            "Roaming Download",
        )

        self._attr_icon = "mdi:download-network"
        self._attr_native_unit_of_measurement = "GB"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def native_value(self):
        total = self.coordinator.data.get(
            "statistics_data_used_r"
        )
        upload = self.coordinator.data.get(
            "statistics_used_tx_r"
        )

        if total is None or upload is None:
            return None

        try:
            download = float(total) - float(upload)

            return round(
                download / 1_000_000_000,
                2,
            )
        except (TypeError, ValueError):
            return None


class FlyboxRoamingUploadSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "statistics_used_tx_r",
            "Roaming Upload",
        )

        self._attr_icon = "mdi:upload-network"
        self._attr_native_unit_of_measurement = "GB"
        self._attr_device_class = SensorDeviceClass.DATA_SIZE

    @property
    def native_value(self):
        value = self.coordinator.data.get(
            "statistics_used_tx_r"
        )

        if value is None:
            return None

        try:
            return round(
                float(value) / 1_000_000_000,
                2,
            )
        except (TypeError, ValueError):
            return None

class FlyboxConnectionTimeSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "connection_time",
            "Čas pripojenia",
        )

        self._attr_icon = "mdi:timer-sand"

    @property
    def native_value(self):
        uptime = self.coordinator.data.get(
            "device_uptime"
        )
        conn_info = self.coordinator.data.get(
            "rt_wwan_conn_info"
        )

        if uptime is None or not conn_info:
            return None

        try:
            parts = str(conn_info).split(",")

            if len(parts) < 2:
                return None

            if parts[0].lower() != "connected":
                return "00:00:00"

            seconds = int(float(uptime)) - int(float(parts[1]))

            if seconds < 0:
                seconds = 0

            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

        except (TypeError, ValueError, IndexError):
            return None

class FlyboxConnectedDevicesSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "connected_devices",
            "Pripojené zariadenia",
        )

        self._attr_icon = "mdi:devices"

    @property
    def native_value(self):
        try:
            client_0 = int(self.coordinator.data.get("wifi_client_0", 0))
            client_1 = int(self.coordinator.data.get("wifi_client_1", 0))
            client_2 = int(self.coordinator.data.get("wifi_client_2", 0))

            return client_0 + client_1 + client_2

        except (TypeError, ValueError):
            return None


class FlyboxAllHostsSensor(FlyboxBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(
            coordinator,
            entry,
            "all_hosts",
            "Všetky zariadenia",
        )

        self._attr_icon = "mdi:lan-connect"

    @property
    def native_value(self):
        try:
            return int(
                self.coordinator.data.get(
                    "rt_hosts_count",
                    0,
                )
            )
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self):
        hosts = self.coordinator.data.get(
            "rt_hosts_list",
            [],
        )

        devices = []

        for host in hosts:
            devices.append(
                {
                    "nazov": host.get("rt_hosts_hostname"),
                    "ip": host.get("rt_hosts_ip"),
                    "mac": host.get("rt_hosts_mac"),
                    "pripojenie": host.get("rt_hosts_type"),
                    "ssid": host.get("rt_hosts_ssid"),
                    "wifi_ap": host.get("rt_hosts_wifi_ap_index"),
                    "uptime": host.get("rt_hosts_uptime"),
                    "lease_time": host.get("rt_hosts_lease_time"),
                    "online_od": host.get("rt_hosts_online_time"),
                }
            )

        return {
            "zariadenia": devices,
        }

class FlyboxRateSensor(FlyboxBaseSensor):
    def __init__(
        self,
        coordinator,
        entry,
        key,
        name,
        icon,
    ):
        super().__init__(
            coordinator,
            entry,
            key,
            name,
        )

        self._attr_icon = icon
        self._attr_device_class = SensorDeviceClass.DATA_RATE
        self._attr_native_unit_of_measurement = UnitOfDataRate.BYTES_PER_SECOND

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._key)

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
