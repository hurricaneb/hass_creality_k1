"""Constants for the Creality K1 integration."""

from homeassistant.const import Platform

DOMAIN = "creality_k1"  # The domain for your integration
PLATFORMS = (Platform.SENSOR, Platform.SWITCH, Platform.FAN, Platform.BUTTON, Platform.CLIMATE) # The platforms that are used

# WebSocket-relaterade konstanter
MSG_TYPE_HEARTBEAT = "heart_beat"  # Heartbeat message
HEARTBEAT_INTERVAL = 5  # Seconds
WS_OPERATION_TIMEOUT = 10 # seconds
HASS_UPDATE_INTERVAL = 30 # seconds

# Sensor-relaterade konstanter
SENSOR_NAME_BED_TEMP = "Bed Temperature"
SENSOR_NAME_BOX_TEMP = "Box Temperature"
SENSOR_NAME_NOZZLE_TEMP = "Nozzle Temperature"
SENSOR_NAME_PRINT_PROGRESS = "Print Progress"
SENSOR_NAME_TOTAL_LAYER = "Total Layer Count"
SENSOR_NAME_WORKING_LAYER = "Working Layer"
SENSOR_NAME_USED_MATERIAL = "Used Material Length"
SENSOR_NAME_TOTAL_PRINT_TIME = "Total Print Time"
SENSOR_NAME_PRINT_JOB_LEFT  = "Print Job Left"
SENSOR_NAME_PRINT_STATE = "Print State"

# Switch controls
SWITCH_NAME_LIGHT = "Printer Light"

# Fan controls
FAN_NAME_MODEL_FAN = "Model Fan"
FAN_NAME_CASE_FAN = "Case Fan"
FAN_NAME_AUXILIARY_FAN = "Side Fan"
FAN_CONFIG = {
    FAN_NAME_MODEL_FAN: ("modelFanPct", "fan", 0),  # P0 for Model Fan
    FAN_NAME_CASE_FAN: ("caseFanPct", "fanCase", 1), # P1 for Case Fan
    FAN_NAME_AUXILIARY_FAN: ("auxiliaryFanPct", "fanAuxiliary", 2), # P2 for Aux Fan
}

# Button controls ("Name", {Params})
BUTTON_CONTROLS = (
    ("Pause Print", {"pause": 1}),
    ("Resume Print", {"pause": 0}),
    ("Stop Print", {"stop": 1}),
    ("Home XY", {"autohome":"X Y"}),
    ("Home Z", {"autohome":"Z"}),
    #("Move X Left", {"setPosition":"X-0.1 F3000"}),
    #("Move X Right", {"setPosition":"X0.1 F3000"}),
    #("Move Y Forwards", {"setPosition":"Y-0.1 F3000"}),
    #("Move Y Backwards", {"setPosition":"Y0.1 F3000"}),
    #("Move Z Up", {"setPosition":"Z-0.1 F600"}),
    #("Move Z Down", {"setPosition":"Z0.1 F600"}),
    #("Bed Temp 90", {"bedTempControl":{"num":0,"val":90}}),
    #("Bed Temp 1", {"bedTempControl":{"num":0,"val":1}}),
    #("Nozzle Temp 240", {"nozzleTempControl":240}),
    #("Nozzle Temp 1", {"nozzleTempControl":1}),
)

# Climate controls (heater_id, name, current_temp_key, target_temp_key, max_temp_key)
CLIMATE_CONTROLS = (
    ("bed0", "Bed Heater", "bedTemp0", "targetBedTemp0", "maxBedTemp"),
    ("nozzle0", "Nozzle Heater", "nozzleTemp", "targetNozzleTemp", "maxNozzleTemp")
)

# Enhetsinformation
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