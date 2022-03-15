import olympe

from olympe.messages.skyctrl.CoPiloting import setPilotingSource

import time

from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy
from olympe.messages.ardrone3.PilotingState import (
    PositionChanged,
    AlertStateChanged,
    FlyingStateChanged,
    NavigateHomeStateChanged,
    SpeedChanged
)

class FlightListener(olympe.EventListener):

    @olympe.listen_event(FlyingStateChanged() | AlertStateChanged() |
        NavigateHomeStateChanged())
    def onStateChanged(self, event, scheduler):
        print("{} = {}".format(event.message.name, event.args["state"]))
        print(time.time())

    @olympe.listen_event(PositionChanged(_policy="wait"))
    def onPositionChanged(self, event, scheduler):
        print(
            "latitude = {latitude} longitude = {longitude} altitude = {altitude}".format(
                **event.args
            )
        )
        print(time.time())

    @olympe.listen_event(SpeedChanged(_policy="wait"))
    def onSpeedChanged(self, event, scheduler):
        print("speedXYZ = ({speedX}, {speedY}, {speedZ})".format(**event.args))


drone = olympe.Drone("192.168.53.1")
with FlightListener(drone):
    
    drone.connect()
    drone(setPilotingSource(source=0))
    while True:
        x=1
    # drone.disconnect()