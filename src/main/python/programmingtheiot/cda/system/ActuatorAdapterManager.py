import logging
from importlib import import_module
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.HvacActuatorSimTask import HvacActuatorSimTask
from programmingtheiot.cda.sim.HumidifierActuatorSimTask import HumidifierActuatorSimTask

class ActuatorAdapterManager(object):
    """
    Shell representation of class for student implementation.
    """
    
    def __init__(self, dataMsgListener: IDataMessageListener = None):
        self.dataMsgListener = dataMsgListener
        self.configUtil = ConfigUtil()
        
        self.useSimulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.ENABLE_SIMULATOR_KEY
        )
        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.deviceID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.DEVICE_LOCATION_ID_KEY, 
            defaultVal=ConfigConst.NOT_SET
        )
        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.DEVICE_LOCATION_ID_KEY, 
            defaultVal=ConfigConst.NOT_SET
        )

        self.humidifierActuator = None
        self.hvacActuator = None
        self.ledDisplayActuator = None
        
        # Initialize environmental actuation tasks
        self._initEnvironmentalActuationTasks()

    def _initEnvironmentalActuationTasks(self):
        if not self.useEmulator:
            # load the environmental tasks for simulated actuation
            self.humidifierActuator = HumidifierActuatorSimTask()
            
            # create the HVAC actuator
            self.hvacActuator = HvacActuatorSimTask()
        else:
            hueModule = import_module('programmingtheiot.cda.emulated.HumidifierEmulatorTask', 'HumidiferEmulatorTask')
            hueClazz = getattr(hueModule, 'HumidifierEmulatorTask')
            self.humidifierActuator = hueClazz()
            
            # create the HVAC actuator emulator
            hveModule = import_module('programmingtheiot.cda.emulated.HvacEmulatorTask', 'HvacEmulatorTask')
            hveClazz = getattr(hveModule, 'HvacEmulatorTask')
            self.hvacActuator = hveClazz()
            
            # create the LED display actuator emulator
            leDisplayModule = import_module('programmingtheiot.cda.emulated.LedDisplayEmulatorTask', 'LedDisplayEmulatorTask')
            leClazz = getattr(leDisplayModule, 'LedDisplayEmulatorTask')
            self.ledDisplayActuator = leClazz()


    def sendActuatorCommand(self, data: ActuatorData) -> ActuatorData:
        if data and not data.isResponseFlagEnabled():
            # First check if the actuation event is destined for this device
            if data.getLocationID() == self.locationID:
                logging.info("Actuator command received for location ID %s. Processing...", str(data.getLocationID()))
                
                aType = data.getTypeID()
                responseData = None
                
                # Implement appropriate logging and error handling
                if aType == ConfigConst.HUMIDIFIER_ACTUATOR_TYPE and self.humidifierActuator:
                    responseData = self.humidifierActuator.updateActuator(data)
                elif aType == ConfigConst.HVAC_ACTUATOR_TYPE and self.hvacActuator:
                    responseData = self.hvacActuator.updateActuator(data)
                elif aType == ConfigConst.LED_DISPLAY_ACTUATOR_TYPE and self.ledDisplayActuator:
                    responseData = self.ledDisplayActuator.updateActuator(data)
                else:
                    logging.warning("No valid actuator type. Ignoring actuation for type: %s", data.getTypeID())
                
                # Later, the responseData instance will be passed to a callback function
                return responseData
            else:
                logging.warning("Location ID doesn't match. Ignoring actuation: (me) %s != (you) %s", 
                                str(self.locationID), str(data.getLocationID()))
        else:
            logging.warning("Actuator request received. Message is empty or response. Ignoring.")
        
        return None

    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        if listener:
            self.dataMsgListener = listener
