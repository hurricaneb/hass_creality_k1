"""Constants for the Creality K1 integration."""

from homeassistant.const import Platform

DOMAIN = "creality_k1"  # The domain for your integration
PLATFORMS = (Platform.SENSOR, Platform.SWITCH, Platform.FAN, Platform.BUTTON, Platform.CLIMATE) # The platforms that are used

# WebSocket constants
MSG_TYPE_HEARTBEAT = "heart_beat"  # Heartbeat message
HEARTBEAT_INTERVAL = 5  # Seconds
WS_OPERATION_TIMEOUT = 10 # seconds
HASS_UPDATE_INTERVAL = 30 # seconds

# Fan controls (translation_key: (percentage_key, toggle_key, p_index))
FAN_CONFIG = {
    "model_fan": ("modelFanPct", "fan", 0),  # P0 for Model Fan
    "case_fan": ("caseFanPct", "fanCase", 1), # P1 for Case Fan
    "side_fan": ("auxiliaryFanPct", "fanAuxiliary", 2), # P2 for Aux Fan
}

# Button controls (translation_key, {Params})
BUTTON_CONTROLS = (
    ("pause_print", {"pause": 1}),
    ("resume_print", {"pause": 0}),
    ("stop_print", {"stop": 1}),
    ("home_xy", {"autohome":"X Y"}),
    ("home_z", {"autohome":"Z"}),
)

# Climate controls (heater_id, translation_key, current_temp_key, target_temp_key, max_temp_key)
CLIMATE_CONTROLS = (
    ("bed0", "bed_heater", "bedTemp0", "targetBedTemp0", "maxBedTemp"),
    ("nozzle0", "nozzle_heater", "nozzleTemp", "targetNozzleTemp", "maxNozzleTemp")
)

# Device information
DEVICE_MANUFACTURER = "Creality"
DEVICE_MODEL = "K1"
PRINTER_STATE_MAP = {
    0: "Stopped",        
    1: "Printing",
    2: "Complete",       
    3: "Failed",         
    4: "Aborted",        
    5: "Paused"          
}
DEFAULT_PRINTER_STATE = "Unknown"