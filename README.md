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

HACS installation instructions will be added after the repository is published.

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
