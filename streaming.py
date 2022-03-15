from ipaddress import summarize_address_range
import olympe
import gmplot
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


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

long = []
lat = []

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
        long.append(event.args['longitude'])
        lat.append(event.args['latitude'])
        

    @olympe.listen_event(SpeedChanged(_policy="wait"))
    def onSpeedChanged(self, event, scheduler):
        x = 1
        # print("speedXYZ = ({speedX}, {speedY}, {speedZ})".format(**event.args))


drone = olympe.Drone("192.168.53.1")
gmap3 = gmplot.GoogleMapPlotter(36.00169533334618, -78.94490416666508, 13)
gmap3.apikey = "AIzaSyDa_CY2kSKvOT7P3UTFBJHzuiAS7d19f7M"
#latitude_list = [ 30.3358376, 30.307977, 30.3216419 ]
#longitude_list = [ 77.8701919, 78.048457, 78.0413095 ]
#gmap3.scatter( latitude_list, longitude_list, '# FF0000',size = 40, marker = False )
#gmap3.plot(latitude_list, longitude_list, 'cornflowerblue', edge_width = 2.5)
#gmap3.draw( "/home/drone/Desktop//map13.html" )

with FlightListener(drone):
    
    drone.connect()
    drone(setPilotingSource(source=0))

    while True:
        if len(long) % 10 == 0:

            gmap3.scatter(lat, long, '#FF0000',size = 40, marker = False )
            gmap3.plot(lat, long, 'cornflowerblue', edge_width = 2.5)
            gmap3.draw( "/home/drone/Desktop//map13.html" )

    #size = len(long)

    #fig = plt.figure()
    #while True:
    #    x=1
    #    if len(long) != size:
    #        plt.clf()
    #        ax = fig.add_subplot(111)

#            line = Line2D(long, lat)
 #           ax.add_line(line)
  #          ax.set_xlim(min(long), max(long))
   #         ax.set_ylim(min(lat), max(lat))
    #        plt.show()
     #       size = len(long)
            # print(coordinates)
    # drone.disconnect()