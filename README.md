# Orange Flybox for Home Assistant

Custom integration for Home Assistant providing local monitoring and control of Orange Flybox routers.

## Tested hardware

- Orange Flybox
- MeiG SRT858M
- Firmware tested: SRT858M-EA_8.363.18_EQ100

Other firmware versions or related Flybox models may work, but are not yet verified.

## Features

- Local connection to the router
- Internet connection status
- Mobile network type
- Operator
- Signal level
- SIM status
- Carrier Aggregation status
- Router uptime
- Internet connection duration
- Total transferred data
- Downloaded data
- Uploaded data
- Current download rate
- Current upload rate
- Wi-Fi status
- Connected Wi-Fi clients
- List of connected LAN/Wi-Fi devices

## Wi-Fi control

The integration currently provides switches for:

- Main 2.4 GHz Wi-Fi
- Guest 2.4 GHz Wi-Fi
- Main 5 GHz Wi-Fi

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Open **Custom repositories**.
3. Add:

   `https://github.com/fct-sk/flybox-ha`

4. Select **Integration** as the repository type.
5. Search for **Orange Flybox** in HACS.
6. Download the latest release.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration**.
9. Search for **Orange Flybox**.
10. Enter the router address, username and password.

### Manual installation

Copy the `custom_components/flybox` directory to:

`/config/custom_components/flybox`

Restart Home Assistant and add **Orange Flybox** from:

**Settings → Devices & services → Add integration**

Enter the router address, username and password.

The default router address is:

`192.168.1.1`

## Notes

The integration communicates locally with the Flybox WebUI API. No cloud service is required.

The polling interval is currently 5 seconds.

## Status

This project is currently experimental and has primarily been tested with the MeiG SRT858M Orange Flybox.
