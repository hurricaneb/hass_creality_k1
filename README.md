# Home Assistant Creality K1 / K1C / K1 Max Integration

This is a custom component for [Home Assistant](https://www.home-assistant.io/) to integrate with Creality K1, K1C, and K1 Max 3D printers. It communicates directly with the printer over your local network using its WebSocket API (port 9999), providing sensors and controls without relying on the Creality Cloud.

This integration uses the [creality-k1-api](https://pypi.org/project/creality-k1-api/) Python package to ensure robust, asynchronous communication.

## Features

* **Multi-Printer Support:** Fully compatible with the Creality K1, K1C, and K1 Max.
* **Real-time Monitoring:**
    * Printer State (Printing, Idle, Paused, Complete, Failed, etc.)
    * Nozzle Temperature (Current & Target)
    * Heated Bed Temperature (Current & Target)
    * Chamber Temperature (if reported by the printer)
    * Print Progress (%)
    * Print Job Time / Remaining Time
    * Current Layer / Total Layers
    * Fan Speeds (%)
    * LED Light Status
    * Built-in Camera stream (MJPEG)
    * And can add other sensors exposed by the WebSocket API.
* **Controls:**
    * Turn LED Light On/Off.
    * Control Fan Speeds (Model Fan, Case/Back Fan, Side/Auxiliary Fan) via percentage. (Uses `M106` GCODE commands).
    * Quick Buttons (Pause Print, Resume Print, Stop Print, Home XY, Home Z).
    * Control Heaters (Nozzle and Bed) via On, Off and Target Temp. (Uses `M104` and `M140` GCODE commands).
* **Local Control:** Communicates directly via the local network WebSocket.
* **Seamless Reconfiguration:** Did your printer's IP address change? No need to reinstall! You can easily update the IP address from the integration settings in Home Assistant.
* **Internationalization (i18n):** Native support for English and Swedish out of the box. All entities automatically adapt to your Home Assistant language preferences.

## Requirements

* Home Assistant instance.
* Creality K1, K1C, or K1 Max printer connected to your local network.
* Network connectivity between your Home Assistant instance and the printer.
* The IP address of your printer.

## Installation

### Method 1: Installation via HACS (Home Assistant Community Store)

1. Navigate to HACS: In your Home Assistant, go to HACS > Integrations.
2. Add Custom Repository: Click on the three dots in the top right corner and select "Custom repositories".
3. Enter Repository URL: In the "Repository" field, paste the following URL:
   https://github.com/hurricaneb/hass_creality_k1
4. Select Category: Choose "Integration" as the category.
5. Add and Install: Click "Add". The repository will now appear in your HACS integrations list. Click on it and then click "Install".
6. Restart Home Assistant: After the installation is complete, you will be prompted to restart Home Assistant. Please do so to apply the changes.
7. Add Integration: Go to Settings > Devices & Services and click the "Add Integration" button. Search for "Creality K1" and add it.
8. Configure: Enter the IP address of your Creality printer to complete the setup.

### Method 2: Manual Installation

1.  **Download the Code:** Download the `custom_components/creality_k1` folder from this repository (e.g., download the ZIP and extract it, or use git clone). Make sure you have the folder containing `__init__.py`, `manifest.json`, `sensor.py`, `switch.py`, `fan.py`, etc.
2.  **Copy to Home Assistant:**
    * Connect to your Home Assistant configuration directory (often via Samba, SSH, or the File editor add-on).
    * Navigate to the `custom_components` folder. If it doesn't exist, create it.
    * Copy the entire `custom_components/creality_k1` folder (the one you downloaded/cloned) into the `custom_components` directory.
    * Your final path should look like `config/custom_component/creality_k1/`.
    * Alternatively, to keep the git repo intact:
        * git clone repo to `config/projects`.
        * From `config/custom_components` directory create a symbolic link to the creality_k1 directory: `ln -s ../projects/hass_creality_k1/custom_component/creality_k1 creality_k1`
3.  **Restart Home Assistant:** Restart your Home Assistant instance. (Settings > System > Restart).

## Configuration

Once installed and after restarting Home Assistant:

1.  Go to **Settings** > **Devices & Services**.
2.  Click the **+ Add Integration** button in the bottom right corner.
3.  Search for "**Creality K1**".
4.  Select the integration.
5.  You will be prompted to enter the **IP Address** of your Creality printer.
6.  Click **Submit**.

The integration will attempt to connect to your printer via WebSocket. If successful, it will add the device and its associated entities to Home Assistant.

### Updating IP Address
If the IP address of your printer changes, simply go to Settings > Devices & Services, locate your Creality K1 integration, click the **Configure** button, and enter the new IP address.

## Entities Provided

This integration creates several entities, typically prefixed with the name you gave the device during setup. Key entities include:

* **Camera (`camera.`):** MJPEG Camera Stream (Automatically added if a camera is connected)
* **Fans (`fan.`):** Model Fan, Case Fan, Side Fan (with percentage control)
* **Switch (`switch.`):** LED Light
* **Sensors (`sensor.`):** Printer Status, Temperatures (Nozzle, Bed, Chamber), Print Progress, Times (Job, Remaining), Layers
* **Buttons (`button.`):** Pause, Resume, Stop, Home XY, Home Z
* **Heaters (`climate.`):** Nozzle Heater, Bed Heater (with target temp control)

## Troubleshooting / Notes

* **Connection Issues:** Ensure your printer is powered on, connected to the network, and that the IP address entered during configuration is correct. Check for firewall rules blocking traffic between Home Assistant and the printer (specifically WebSocket traffic on port 9999).
* **Fan Control:** Fan percentage is controlled by sending `M106 P<index> S<0-255>` GCODE commands via the WebSocket. `Pct` values reported by the printer reflect status but are not used for direct control.
* **Heater Control:** Use a thermostat card in HA to control heaters.
* **Firmware Differences:** Printer behavior and available data might vary slightly depending on the firmware version installed on your printer.

## Disclaimer

This is a custom integration and is not officially supported by Home Assistant or Creality. Use at your own risk.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/hurricaneb/hass_creality_k1).

## License

GPL-3.0 license
