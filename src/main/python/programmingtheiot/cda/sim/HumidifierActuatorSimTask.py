import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class HumidifierActuatorSimTask(BaseActuatorSimTask):
    """
    This is a simple wrapper for an Actuator abstraction - it provides
    a container for the actuator's state, value, name, and status. A
    command variable is also provided to instruct the actuator to
    perform a specific function (in addition to setting a new value
    via the 'val' parameter).
    """
   
    def __init__(self):
        super(HumidifierActuatorSimTask, self).__init__(
            name=ConfigConst.HUMIDIFIER_ACTUATOR_NAME,
            typeID=ConfigConst.HUMIDIFIER_ACTUATOR_TYPE,
            simpleName="HUMIDIFIER"
        )

    